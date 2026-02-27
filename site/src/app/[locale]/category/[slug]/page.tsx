import { notFound } from "next/navigation";
import { getTranslations } from "next-intl/server";
import type { Metadata } from "next";
import { getArticlesByCategory } from "@/lib/articles";
import ArticleCard from "@/components/ArticleCard";
import type { Category } from "@/types/article";

type Props = {
  params: Promise<{ locale: string; slug: string }>;
};

const CATEGORIES: Category[] = [
  "politics",
  "crypto",
  "ai-tech",
  "sports",
  "markets",
  "culture",
  "geopolitics",
];

const categoryNavKeys: Record<Category, string> = {
  politics: "politics",
  crypto: "crypto",
  "ai-tech": "aiTech",
  sports: "sports",
  markets: "markets",
  culture: "culture",
  geopolitics: "geopolitics",
};

const categoryColors: Record<Category, string> = {
  politics: "text-purple-400",
  crypto: "text-orange-400",
  "ai-tech": "text-cyan-400",
  sports: "text-green-400",
  markets: "text-blue-400",
  culture: "text-pink-400",
  geopolitics: "text-red-400",
};

export async function generateStaticParams() {
  const locales = ["en", "pt", "es"];
  return locales.flatMap((locale) =>
    CATEGORIES.map((slug) => ({ locale, slug }))
  );
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { locale, slug } = await params;

  if (!CATEGORIES.includes(slug as Category)) {
    return { title: "Not Found | Prediction Bets" };
  }

  const category = slug as Category;
  const navKey = categoryNavKeys[category];
  const tNav = await getTranslations({ locale, namespace: "nav" });
  const categoryLabel = tNav(navKey);

  return {
    title: `${categoryLabel} | Prediction Bets`,
    description: `Latest prediction market insights and analysis in ${categoryLabel}.`,
  };
}

export default async function CategoryPage({ params }: Props) {
  const { locale, slug } = await params;

  if (!CATEGORIES.includes(slug as Category)) {
    notFound();
  }

  const category = slug as Category;
  const navKey = categoryNavKeys[category];
  const tNav = await getTranslations({ locale, namespace: "nav" });
  const t = await getTranslations({ locale, namespace: "home" });

  const categoryLabel = tNav(navKey);
  const colorClass = categoryColors[category];

  const articles = await getArticlesByCategory(category, locale);

  return (
    <div className="min-h-screen">
      {/* Page Header */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-10 pb-8">
        <h1 className={`text-3xl sm:text-4xl font-bold ${colorClass}`}>
          {categoryLabel}
        </h1>
      </section>

      {/* Article Grid */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-16">
        {articles.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {articles.map((article) => (
              <ArticleCard key={article.slug} article={article} />
            ))}
          </div>
        ) : (
          <div className="text-center py-20">
            <p className="text-pb-text-muted text-lg">
              {t("emptyState")}
            </p>
          </div>
        )}
      </section>
    </div>
  );
}
