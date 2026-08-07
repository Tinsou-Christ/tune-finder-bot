"""Extraction audio (ffmpeg) + reconnaissance musicale via l'API AudD."""

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


def _parse(result: dict) -> dict:
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
            '🎧 Spotify': (spotify.get('external_urls') or {}).get('spotify'),
            '🍏 Apple Music': apple.get('url'),
            '🎶 Deezer': deezer.get('link'),
            '▶️ YouTube': _first(
                (result.get('song_link') or None),
            ),
        },
        'preview': _first(deezer.get('preview'), spotify.get('preview_url')),
    }


async def recognize(media_path: str) -> dict | None:
    """Renvoie les infos du son, ou None si rien n'a été reconnu."""
    if not config.AUDD_API_TOKEN:
        raise RecognizeError('AUDD_API_TOKEN manquant')

    sample_path = await extract_audio(media_path)
    try:
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
        return _parse(result)
    finally:
        try:
            os.remove(sample_path)
        except OSError:
            pass
