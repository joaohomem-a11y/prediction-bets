import { getTranslations } from "next-intl/server";
import { Link } from "@/i18n/navigation";
import { FORUM_SECTIONS } from "@/lib/forum";

/** Fake preview threads to tease the community vibe */
const PREVIEW_THREADS = [
  {
    section: "signal-drop",
    emoji: "📡",
    author: "The Oracle of Odds",
    title: "Polymarket just flipped on the Fed — 62% now pricing cuts before July",
    replies: 47,
    signals: 182,
    time: "2h",
  },
  {
    section: "contrarian-takes",
    emoji: "🔥",
    author: "Consensus Crusher",
    title: "Unpopular opinion: Bitcoin prediction markets are more accurate than crypto Twitter",
    replies: 93,
    signals: 341,
    time: "5h",
  },
  {
    section: "prediction-battles",
    emoji: "⚔️",
    author: "Base Rate Betty",
    title: "BATTLE: Will AI pass the Turing test by 2027? I'm taking the No side at 34¢",
    replies: 128,
    signals: 567,
    time: "8h",
  },
  {
    section: "reality-check",
    emoji: "✅",
    author: "Market Truth Marta",
    title: "Reality Check: Remember when pundits said the housing market would crash? Markets said no. Markets were right.",
    replies: 61,
    signals: 290,
    time: "1d",
  },
  {
    section: "edge-lab",
    emoji: "🧪",
    author: "Signal Samurai",
    title: "My framework for finding mispriced markets: volume divergence + sentiment analysis",
    replies: 84,
    signals: 412,
    time: "1d",
  },
  {
    section: "off-market",
    emoji: "🎲",
    author: "Edge Lord Eddie",
    title: "If prediction markets existed in 1999, the dot-com crash would've been priced in by August",
    replies: 156,
    signals: 723,
    time: "2d",
  },
];

const STATS = [
  { value: "12.4K", labelKey: "statMembers" },
  { value: "847", labelKey: "statThreads" },
  { value: "23.1K", labelKey: "statSignals" },
  { value: "98%", labelKey: "statAccuracy" },
];

export default async function CommunityPage({
  params,
}: {
  params: Promise<{ locale: string }>;
}) {
  const { locale } = await params;
  const t = await getTranslations({ locale, namespace: "community" });

  return (
    <main className="min-h-screen">
      {/* Hero */}
      <section className="relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-pb-accent-blue/10 via-transparent to-purple-600/10" />
        <div className="relative max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-16 sm:py-24 text-center">
          <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-pb-text-primary mb-4">
            {t("title")}
          </h1>
          <p className="text-lg sm:text-xl text-pb-text-secondary max-w-2xl mx-auto mb-8">
            {t("landingSubtitle")}
          </p>

          {/* Stats */}
          <div className="flex flex-wrap items-center justify-center gap-6 sm:gap-10 mb-10">
            {STATS.map((stat) => (
              <div key={stat.labelKey} className="text-center">
                <div className="text-2xl sm:text-3xl font-bold text-pb-accent-blue font-mono">
                  {stat.value}
                </div>
                <div className="text-xs text-pb-text-muted uppercase tracking-wider mt-1">
                  {t(stat.labelKey as Parameters<typeof t>[0])}
                </div>
              </div>
            ))}
          </div>

          <Link
            href="/auth/signin"
            className="btn-primary text-base px-8 py-3.5"
          >
            {t("joinCta")}
          </Link>
        </div>
      </section>

      {/* Section cards */}
      <section className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <h2 className="text-sm font-semibold text-pb-text-secondary uppercase tracking-wider mb-6">
          {t("sectionsTitle")}
        </h2>
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {FORUM_SECTIONS.map((section) => (
            <div
              key={section.slug}
              className="card p-5 flex items-start gap-3 opacity-90"
            >
              <span className="text-2xl">{section.emoji}</span>
              <div>
                <h3 className="font-semibold text-pb-text-primary">
                  {t(`sections.${section.key}` as Parameters<typeof t>[0])}
                </h3>
                <p className="text-sm text-pb-text-muted mt-0.5">
                  {section.description}
                </p>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Preview threads — the teaser */}
      <section className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <h2 className="text-sm font-semibold text-pb-text-secondary uppercase tracking-wider mb-6">
          {t("previewTitle")}
        </h2>
        <div className="flex flex-col gap-2">
          {PREVIEW_THREADS.map((thread, i) => (
            <div
              key={i}
              className="card p-4 sm:p-5 flex items-start gap-3 sm:gap-4 group"
            >
              <span className="text-xl mt-0.5">{thread.emoji}</span>
              <div className="flex-1 min-w-0">
                <p className="text-sm sm:text-base font-medium text-pb-text-primary line-clamp-2 group-hover:text-pb-accent-blue transition-colors">
                  {thread.title}
                </p>
                <div className="flex items-center gap-3 mt-2 text-xs text-pb-text-muted">
                  <span className="font-medium text-pb-text-secondary">
                    {thread.author}
                  </span>
                  <span>&middot;</span>
                  <span>{thread.time}</span>
                  <span>&middot;</span>
                  <span className="font-mono text-pb-accent-blue">
                    {thread.signals} signals
                  </span>
                  <span>&middot;</span>
                  <span>{thread.replies} replies</span>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Blur overlay + CTA */}
        <div className="relative mt-[-60px] pt-16 pb-8 bg-gradient-to-t from-pb-bg-primary via-pb-bg-primary/95 to-transparent text-center">
          <p className="text-pb-text-secondary mb-4">
            {t("previewCta")}
          </p>
          <Link
            href="/auth/signin"
            className="btn-primary text-base px-8 py-3"
          >
            {t("joinCta")}
          </Link>
        </div>
      </section>
    </main>
  );
}
