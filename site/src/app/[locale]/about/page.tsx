import { getTranslations } from "next-intl/server";
import type { Metadata } from "next";
import { Link } from "@/i18n/navigation";

type Props = {
  params: Promise<{ locale: string }>;
};

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { locale } = await params;
  const t = await getTranslations({ locale, namespace: "about" });

  return {
    title: `${t("title")} | Prediction Bets`,
    description: t("subtitle"),
  };
}

const SACRED_WORDS = [
  "signal",
  "edge",
  "consensus",
  "realityCheck",
  "marketTruth",
  "predictionMindset",
] as const;

export default async function AboutPage({ params }: Props) {
  const { locale } = await params;
  const t = await getTranslations({ locale, namespace: "about" });

  return (
    <main className="min-h-screen">
      {/* ── Hero Section ── */}
      <section className="relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-b from-pb-accent-blue/5 via-transparent to-transparent" />
        <div className="relative max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 pt-20 pb-16 text-center">
          <h1 className="text-5xl sm:text-6xl lg:text-7xl font-bold text-pb-text-primary tracking-tight">
            {t("title")}
          </h1>
          <p className="mt-6 text-xl sm:text-2xl font-mono text-pb-accent-blue">
            {t("subtitle")}
          </p>
        </div>
      </section>

      {/* ── Creation Story ── */}
      <section className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <h2 className="text-sm font-mono uppercase tracking-widest text-pb-accent-amber mb-8">
          {t("story")}
        </h2>
        <blockquote className="border-l-4 border-pb-accent-blue pl-6 sm:pl-8">
          <p className="text-2xl sm:text-3xl lg:text-4xl font-bold leading-relaxed text-pb-text-primary">
            {t("storyText")}
          </p>
        </blockquote>
      </section>

      {/* ── The Creed ── */}
      <section className="border-y border-white/5 bg-pb-bg-secondary/50">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
          <h2 className="text-sm font-mono uppercase tracking-widest text-pb-accent-amber mb-12 text-center">
            {t("creed")}
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {([1, 2, 3, 4] as const).map((num) => (
              <div key={num} className="card p-8 flex items-start gap-5">
                <span className="text-4xl sm:text-5xl font-bold font-mono text-pb-accent-amber leading-none flex-shrink-0">
                  {num}
                </span>
                <p className="text-lg sm:text-xl font-semibold text-pb-text-primary leading-snug pt-1">
                  {t(`creed${num}`)}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── Sacred Words ── */}
      <section className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <h2 className="text-sm font-mono uppercase tracking-widest text-pb-accent-amber mb-12 text-center">
          {t("words")}
        </h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {SACRED_WORDS.map((word) => (
            <div key={word} className="card p-6">
              <dt className="font-mono text-pb-accent-blue text-lg font-semibold mb-2">
                {t(`word_${word}`)}
              </dt>
              <dd className="text-pb-text-secondary leading-relaxed">
                {t(`word_${word}_def`)}
              </dd>
            </div>
          ))}
        </div>
      </section>

      {/* ── Pagans (We Stand Against) ── */}
      <section className="border-y border-white/5 bg-pb-bg-secondary/50">
        <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-20 text-center">
          <h2 className="text-sm font-mono uppercase tracking-widest text-red-400 mb-12">
            {t("pagans")}
          </h2>
          <ul className="space-y-4">
            {([1, 2, 3, 4] as const).map((num) => (
              <li
                key={num}
                className="text-xl sm:text-2xl font-semibold text-pb-text-secondary"
              >
                <span className="text-red-400/60 mr-3">&times;</span>
                {t(`pagan${num}`)}
              </li>
            ))}
          </ul>
        </div>
      </section>

      {/* ── Core Belief CTA ── */}
      <section className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-24 text-center">
        <p className="text-3xl sm:text-4xl lg:text-5xl font-bold text-pb-text-primary leading-tight mb-10">
          {t("coreBeliefHeading")}
        </p>
        <Link href="/auth/signup" className="btn-primary text-lg px-8 py-4">
          {t("joinTribe")}
        </Link>
      </section>
    </main>
  );
}
