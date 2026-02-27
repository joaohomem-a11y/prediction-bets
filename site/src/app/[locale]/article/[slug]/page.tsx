import { notFound } from "next/navigation";
import { getTranslations } from "next-intl/server";
import type { Metadata } from "next";
import { getAllArticles, getAllSlugs } from "@/lib/articles";
import CategoryBadge from "@/components/CategoryBadge";
import ArticleCard from "@/components/ArticleCard";

type Props = {
  params: Promise<{ locale: string; slug: string }>;
};

export async function generateStaticParams() {
  const slugs = getAllSlugs("en");
  const locales = ["en", "pt", "es"];
  return locales.flatMap((locale) =>
    slugs.map((slug) => ({ locale, slug }))
  );
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { locale, slug } = await params;
  const allArticles = await getAllArticles(locale);
  const article = allArticles.find((a) => a.slug === slug);

  if (!article) return { title: "Not Found | Prediction Bets" };

  return {
    title: `${article.title} | Prediction Bets`,
    description: article.excerpt,
    openGraph: {
      title: article.title,
      description: article.excerpt,
      images: [article.image],
      type: "article",
    },
    twitter: {
      card: "summary_large_image",
      title: article.title,
      description: article.excerpt,
      images: [article.image],
    },
  };
}

export default async function ArticlePage({ params }: Props) {
  const { locale, slug } = await params;
  const t = await getTranslations({ locale, namespace: "article" });

  const allArticles = await getAllArticles(locale);
  const article = allArticles.find((a) => a.slug === slug);

  if (!article) notFound();

  const relatedArticles = allArticles
    .filter((a) => a.category === article.category && a.slug !== article.slug)
    .slice(0, 3);

  return (
    <div className="min-h-screen">
      <article className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
        {/* Header */}
        <header className="mb-8">
          <div className="mb-4">
            <CategoryBadge category={article.category} />
          </div>

          <h1 className="text-3xl sm:text-4xl font-bold text-pb-text-primary mb-3">
            {article.title}
          </h1>

          {article.subtitle && (
            <p className="text-lg text-pb-text-secondary mb-4">
              {article.subtitle}
            </p>
          )}

          <div className="flex items-center gap-3 text-sm text-pb-text-muted">
            <span className="text-pb-text-secondary font-medium">
              {t("by")} {article.author}
            </span>
            <span>&middot;</span>
            <time dateTime={article.date}>{article.date}</time>
            <span>&middot;</span>
            <span className="font-mono text-pb-accent-blue">
              {t("readTime", { minutes: article.readingTime })}
            </span>
          </div>
        </header>

        {/* Hero Image */}
        <div className="relative aspect-[2/1] rounded-xl overflow-hidden mb-10">
          <img
            src={article.image}
            alt={article.title}
            className="w-full h-full object-cover"
          />
          <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent" />
          {article.imageCaption && (
            <p className="absolute bottom-0 left-0 right-0 px-4 py-3 text-xs text-pb-text-muted bg-black/40 backdrop-blur-sm">
              {article.imageCaption}
            </p>
          )}
        </div>

        {/* Article Body */}
        <div
          className="prose prose-invert prose-lg max-w-none prose-headings:text-pb-text-primary prose-headings:font-bold prose-p:text-pb-text-secondary prose-p:leading-relaxed prose-a:text-pb-accent-blue prose-a:no-underline hover:prose-a:underline prose-strong:text-pb-text-primary prose-blockquote:border-pb-accent-blue prose-blockquote:text-pb-text-secondary prose-code:text-pb-accent-amber prose-code:bg-pb-bg-surface prose-code:px-1.5 prose-code:py-0.5 prose-code:rounded prose-hr:border-white/10"
          dangerouslySetInnerHTML={{ __html: article.content }}
        />

        {/* Tags */}
        {article.tags.length > 0 && (
          <div className="mt-10 pt-8 border-t border-white/10">
            <div className="flex flex-wrap gap-2">
              {article.tags.map((tag) => (
                <span
                  key={tag}
                  className="font-mono text-sm bg-pb-bg-surface text-pb-text-secondary px-3 py-1 rounded-full"
                >
                  #{tag}
                </span>
              ))}
            </div>
          </div>
        )}
      </article>

      {/* Related Articles */}
      {relatedArticles.length > 0 && (
        <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-16">
          <h2 className="text-xl font-bold text-pb-text-primary mb-6">
            {t("related")}
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {relatedArticles.map((related) => (
              <ArticleCard key={related.slug} article={related} />
            ))}
          </div>
        </section>
      )}
    </div>
  );
}
