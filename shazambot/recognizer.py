"""Extraction audio (ffmpeg) + reconnaissance musicale.

Moteur principal : Shazam (via shazamio) — gratuit, aucune clé API requise.
Moteur de secours : AudD, utilisé uniquement si AUDD_API_TOKEN est défini.
"""

import asyncio
import logging
import os
import tempfile

import httpx

import config

logger = logging.getLogger(__name__)

AUDD_URL = 'https://api.audd.io/'


class RecognizeError(Exception):
    pass


async def extract_audio(source_path: str) -> str:
    """Extrait un extrait mp3 mono 44.1kHz depuis n'importe quel média."""
    out_path = os.path.join(tempfile.gettempdir(), f'sample_{os.getpid()}_{os.urandom(4).hex()}.mp3')
    process = await asyncio.create_subprocess_exec(
        'ffmpeg', '-hide_banner', '-loglevel', 'error', '-y',
        '-i', source_path,
        '-vn',
        '-t', str(config.SAMPLE_SECONDS),
        '-ac', '1',
        '-ar', '44100',
        '-b:a', '128k',
        out_path,
        stdout=asyncio.subprocess.DEVNULL,
        stderr=asyncio.subprocess.PIPE,
    )
    _, stderr = await process.communicate()
    if process.returncode != 0 or not os.path.exists(out_path) or os.path.getsize(out_path) == 0:
        raise RecognizeError(f'ffmpeg: {stderr.decode("utf-8", "ignore")[:300]}')
    return out_path


def _first(*values):
    for value in values:
        if value:
            return value
    return None


# ---------------------------------------------------------------- Shazam ----

def _shazam_meta(track: dict) -> dict:
    meta = {}
    for section in track.get('sections') or []:
        for item in section.get('metadata') or []:
            key = (item.get('title') or '').strip().lower()
            if key and item.get('text'):
                meta[key] = item['text']
    return meta


def _parse_shazam(track: dict) -> dict:
    meta = _shazam_meta(track)
    images = track.get('images') or {}
    share = track.get('share') or {}
    hub = track.get('hub') or {}

    links = {}
    for provider in hub.get('providers') or []:
        name = (provider.get('type') or '').title()
        uri = None
        for action in provider.get('actions') or []:
            if (action.get('uri') or '').startswith('http'):
                uri = action['uri']
                break
        if name and uri:
            emoji = {'Spotify': '🎧', 'Deezer': '🎶'}.get(name, '🔗')
            links[f'{emoji} {name}'] = uri

    for option in hub.get('options') or []:
        for action in option.get('actions') or []:
            uri = action.get('uri') or ''
            if 'music.apple.com' in uri:
                links.setdefault('🍏 Apple Music', uri)

    shazam_url = _first(track.get('url'), share.get('href'))
    if shazam_url:
        links['🎵 Shazam'] = shazam_url

    preview = None
    for action in hub.get('actions') or []:
        if action.get('type') == 'uri' and (action.get('uri') or '').startswith('http'):
            preview = action['uri']
            break

    return {
        'title': track.get('title') or '—',
        'artist': track.get('subtitle') or '—',
        'album': meta.get('album') or '—',
        'release': meta.get('released') or '—',
        'label': meta.get('label') or '—',
        'cover': _first(images.get('coverarthq'), images.get('coverart'), share.get('image')),
        'links': links,
        'preview': preview,
    }


async def _recognize_shazam(sample_path: str) -> dict | None:
    try:
        from shazamio import Shazam
    except ImportError as exc:  # pragma: no cover
        raise RecognizeError(f'shazamio indisponible: {exc}')

    try:
        payload = await asyncio.wait_for(
            Shazam().recognize(sample_path),
            timeout=config.RECOGNIZE_TIMEOUT,
        )
    except asyncio.TimeoutError:
        raise RecognizeError('Shazam: délai dépassé')
    except Exception as exc:
        raise RecognizeError(f'Shazam: {exc}')

    track = (payload or {}).get('track')
    if not track:
        return None
    return _parse_shazam(track)


# ------------------------------------------------------------------ AudD ----

def _parse_audd(result: dict) -> dict:
    spotify = result.get('spotify') or {}
    deezer = result.get('deezer') or {}
    apple = result.get('apple_music') or {}
    album = spotify.get('album') or {}
    images = album.get('images') or []

    return {
        'title': _first(result.get('title'), apple.get('name'), deezer.get('title')) or '—',
        'artist': _first(result.get('artist'), apple.get('artistName')) or '—',
        'album': _first(result.get('album'), album.get('name'), (deezer.get('album') or {}).get('title')) or '—',
        'release': _first(result.get('release_date'), album.get('release_date')) or '—',
        'label': _first(result.get('label'), apple.get('recordLabel')) or '—',
        'cover': _first(
            images[0].get('url') if images else None,
            (deezer.get('album') or {}).get('cover_big'),
            (apple.get('artwork') or {}).get('url', '').replace('{w}', '600').replace('{h}', '600') or None,
        ),
        'links': {
            key: value for key, value in {
                '🎧 Spotify': (spotify.get('external_urls') or {}).get('spotify'),
                '🍏 Apple Music': apple.get('url'),
                '🎶 Deezer': deezer.get('link'),
            }.items() if value
        },
        'preview': _first(deezer.get('preview'), spotify.get('preview_url')),
    }


async def _recognize_audd(sample_path: str) -> dict | None:
    with open(sample_path, 'rb') as fh:
        files = {'file': ('sample.mp3', fh, 'audio/mpeg')}
        data = {
            'api_token': config.AUDD_API_TOKEN,
            'return': 'apple_music,spotify,deezer',
        }
        async with httpx.AsyncClient(timeout=config.RECOGNIZE_TIMEOUT) as client:
            response = await client.post(AUDD_URL, data=data, files=files)

    if response.status_code != 200:
        raise RecognizeError(f'AudD HTTP {response.status_code}')

    payload = response.json()
    if payload.get('status') != 'success':
        error = (payload.get('error') or {}).get('error_message', 'erreur inconnue')
        raise RecognizeError(f'AudD: {error}')

    result = payload.get('result')
    if not result:
        return None
    return _parse_audd(result)


# ----------------------------------------------------------------- public ---

async def recognize(media_path: str) -> dict | None:
    """Renvoie les infos du son, ou None si rien n'a été reconnu."""
    sample_path = await extract_audio(media_path)
    try:
        try:
            info = await _recognize_shazam(sample_path)
        except RecognizeError as exc:
            logger.warning('Shazam indisponible (%s)', exc)
            info = None
            if not config.AUDD_API_TOKEN:
                raise

        if info:
            return info

        if config.AUDD_API_TOKEN:
            return await _recognize_audd(sample_path)
        return None
    finally:
        try:
            os.remove(sample_path)
        except OSError:
            pass
