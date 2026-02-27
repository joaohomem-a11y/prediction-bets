import { getTranslations } from "next-intl/server";
import type { Metadata } from "next";

type Props = {
  params: Promise<{ locale: string }>;
};

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { locale } = await params;
  const t = await getTranslations({ locale, namespace: "newsletter" });

  return {
    title: `${t("title")} | Prediction Bets`,
    description: t("subtitle"),
  };
}

export default async function NewsletterPage({ params }: Props) {
  const { locale } = await params;
  const t = await getTranslations({ locale, namespace: "newsletter" });

  return (
    <main className="min-h-screen flex items-center justify-center">
      <div className="max-w-lg mx-auto px-4 sm:px-6 lg:px-8 py-24 text-center">
        <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-pb-text-primary tracking-tight mb-4">
          {t("title")}
        </h1>
        <p className="text-lg sm:text-xl text-pb-text-secondary mb-10">
          {t("subtitle")}
        </p>

        <form
          method="POST"
          action="/api/newsletter"
          className="flex flex-col sm:flex-row items-center justify-center gap-3"
        >
          <input
            type="email"
            name="email"
            required
            placeholder={t("placeholder")}
            className="w-full sm:flex-1 px-4 py-3 rounded-lg bg-pb-bg-primary border border-white/10 text-pb-text-primary placeholder:text-pb-text-muted focus:outline-none focus:border-pb-accent-blue transition-colors"
            aria-label="Email address"
          />
          <button type="submit" className="btn-primary whitespace-nowrap">
            {t("submit")}
          </button>
        </form>

        <p className="mt-8 text-sm font-mono text-pb-text-muted">
          {t("socialProof")}
        </p>
      </div>
    </main>
  );
}
