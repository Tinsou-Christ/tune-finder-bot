import { createFileRoute } from "@tanstack/react-router";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "Shazam Bot Telegram — Trouve le titre de n'importe quel son" },
      {
        name: "description",
        content:
          "Bot Telegram qui identifie la musique d'un vocal, d'un audio ou d'une vidéo : titre, artiste, album et liens d'écoute.",
      },
      { property: "og:title", content: "Shazam Bot Telegram" },
      {
        property: "og:description",
        content:
          "Envoie un audio ou une vidéo, le bot te donne le titre du son en quelques secondes.",
      },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary_large_image" },
    ],
  }),
  component: Index,
});

const features = [
  { emoji: "🎙", title: "Vocaux & audios", text: "Un simple message vocal suffit pour lancer l'analyse." },
  { emoji: "🎬", title: "Vidéos & GIF", text: "Le son est extrait automatiquement avec ffmpeg." },
  { emoji: "🎯", title: "Résultat complet", text: "Titre, artiste, album, label, pochette et liens d'écoute." },
  { emoji: "🔒", title: "Accès membres", text: "Chaîne et groupe obligatoires avant d'utiliser le bot." },
];

function Index() {
  return (
    <main className="min-h-screen bg-background text-foreground">
      <section className="mx-auto flex max-w-3xl flex-col items-center px-6 py-20 text-center">
        <span className="rounded-full border border-border px-4 py-1 text-xs uppercase tracking-widest text-muted-foreground">
          Bot Telegram
        </span>
        <h1 className="mt-6 text-4xl font-bold tracking-tight sm:text-6xl">
          Trouve le titre de n'importe quel son 🎧
        </h1>
        <p className="mt-5 max-w-xl text-base text-muted-foreground">
          Envoie un vocal, un audio ou une vidéo au bot : il écoute, reconnaît la musique et te renvoie
          toutes les infos en quelques secondes.
        </p>
      </section>

      <section className="mx-auto grid max-w-4xl gap-4 px-6 pb-24 sm:grid-cols-2">
        {features.map((f) => (
          <article key={f.title} className="rounded-2xl border border-border bg-card p-6 text-card-foreground">
            <div className="text-3xl">{f.emoji}</div>
            <h2 className="mt-3 text-lg font-semibold">{f.title}</h2>
            <p className="mt-1 text-sm text-muted-foreground">{f.text}</p>
          </article>
        ))}
      </section>
    </main>
  );
}
