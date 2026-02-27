import { getTranslations } from "next-intl/server";
import ArticleCard from "@/components/ArticleCard";
import { getAllArticles } from "@/lib/articles";
import { Link } from "@/i18n/navigation";

const CATEGORIES = [
  { key: "politics", href: "/category/politics" },
  { key: "crypto", href: "/category/crypto" },
  { key: "aiTech", href: "/category/ai-tech" },
  { key: "sports", href: "/category/sports" },
  { key: "markets", href: "/category/markets" },
  { key: "culture", href: "/category/culture" },
  { key: "geopolitics", href: "/category/geopolitics" },
] as const;

export default async function HomePage({
  params,
}: {
  params: Promise<{ locale: string }>;
}) {
  const { locale } = await params;
  const t = await getTranslations({ locale, namespace: "home" });
  const tNav = await getTranslations({ locale, namespace: "nav" });

  const allArticles = await getAllArticles(locale);
  const heroArticle =
    allArticles.find((a) => a.featured) ?? allArticles[0] ?? null;
  const gridArticles = allArticles.filter(
    (a) => a.slug !== heroArticle?.slug
  );

  // Empty state
  if (!heroArticle) {
    return (
      <main className="min-h-screen">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24">
          <div className="flex flex-col items-center justify-center text-center">
            <h1 className="text-3xl font-bold text-pb-text-primary mb-3">
              PREDICTION<span className="text-pb-accent-blue">BETS</span>
            </h1>
            <p className="text-pb-text-secondary text-lg">
              {t("subtitle")}
            </p>
            <p className="mt-4 text-pb-text-muted">
              {t("emptyState")}
            </p>
          </div>
        </div>
      </main>
    );
  }

  return (
    <main className="min-h-screen">
      {/* -- Compact Tagline Bar -- */}
      <section className="border-b border-white/5">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <p className="text-sm sm:text-base font-mono text-pb-accent-blue tracking-wide">
            {t("hero")}
          </p>
        </div>
      </section>

      {/* -- Featured Article (Hero Card) -- */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-6 pb-8">
        <ArticleCard article={heroArticle} featured />
      </section>

      {/* -- Category Filter Tabs -- */}
      <nav className="border-y border-white/5" aria-label="Category filters">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center gap-2 py-3 overflow-x-auto scrollbar-none" role="tablist">
            {/* Trending tab -- active by default */}
            <Link
              href="/"
              role="tab"
              aria-selected="true"
              className="flex-shrink-0 px-4 py-1.5 rounded-full text-sm font-medium bg-pb-accent-blue/10 text-pb-accent-blue"
            >
              {tNav("trending")}
            </Link>

            {/* Category tabs */}
            {CATEGORIES.map(({ key, href }) => (
              <Link
                key={key}
                href={href}
                role="tab"
                aria-selected="false"
                className="flex-shrink-0 px-4 py-1.5 rounded-full text-sm font-medium bg-pb-bg-surface text-pb-text-secondary hover:bg-pb-bg-surface-hover hover:text-pb-text-primary transition-colors"
              >
                {tNav(key)}
              </Link>
            ))}
          </div>
        </div>
      </nav>

      {/* -- Article Grid -- */}
      {gridArticles.length > 0 && (
        <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
          <h2 className="text-lg font-semibold text-pb-text-primary mb-6">
            {t("latest")}
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {gridArticles.map((article) => (
              <ArticleCard key={article.slug} article={article} />
            ))}
          </div>
        </section>
      )}

      {/* -- Newsletter CTA -- */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-16 pt-6">
        <div className="card p-8 sm:p-12 text-center">
          <h2 className="text-2xl sm:text-3xl font-bold text-pb-text-primary mb-2">
            {t("joinCta")}
          </h2>
          <p className="text-pb-text-secondary mb-8">
            {t("newsletterCta")}
          </p>
          <form
            method="POST"
            action="/api/newsletter"
            className="flex flex-col sm:flex-row items-center justify-center gap-3 max-w-md mx-auto"
          >
            <input
              type="email"
              name="email"
              required
              placeholder="you@example.com"
              className="w-full sm:flex-1 px-4 py-3 rounded-lg bg-pb-bg-primary border border-white/10 text-pb-text-primary placeholder:text-pb-text-muted focus:outline-none focus:border-pb-accent-blue transition-colors"
              aria-label="Email address"
            />
            <button type="submit" className="btn-primary whitespace-nowrap">
              {t("getSignal")}
            </button>
          </form>
        </div>
      </section>
    </main>
  );
}
