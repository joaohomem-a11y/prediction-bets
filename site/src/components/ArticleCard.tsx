import { Link } from "@/i18n/navigation";
import CategoryBadge from "./CategoryBadge";
import type { Article } from "@/types/article";

interface ArticleCardProps {
  article: Article;
  featured?: boolean;
}

export default function ArticleCard({ article, featured = false }: ArticleCardProps) {
  return (
    <Link href={`/article/${article.slug}`} className="group block">
      <article className={`card overflow-hidden ${featured ? "lg:flex" : ""}`}>
        {/* Image */}
        <div
          className={`relative overflow-hidden ${
            featured ? "lg:w-1/2 aspect-[16/9] lg:aspect-auto lg:min-h-[320px]" : "aspect-[16/9]"
          }`}
        >
          <img
            src={article.image}
            alt={article.title}
            className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
            loading="lazy"
          />
          <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent" />
          <div className="absolute top-3 left-3">
            <CategoryBadge category={article.category} />
          </div>
        </div>

        {/* Content */}
        <div className={`p-5 ${featured ? "lg:w-1/2 lg:p-8 lg:flex lg:flex-col lg:justify-center" : ""}`}>
          <h3
            className={`font-bold text-pb-text-primary group-hover:text-pb-accent-blue transition-colors line-clamp-2 ${
              featured ? "text-2xl lg:text-3xl" : "text-lg"
            }`}
          >
            {article.title}
          </h3>

          {article.subtitle && featured && (
            <p className="mt-2 text-pb-text-secondary text-sm lg:text-base line-clamp-2">
              {article.subtitle}
            </p>
          )}

          <p className={`mt-2 text-pb-text-muted text-sm line-clamp-2 ${featured ? "lg:line-clamp-3" : ""}`}>
            {article.excerpt}
          </p>

          {/* Meta */}
          <div className="mt-4 flex items-center gap-3 text-xs text-pb-text-muted">
            <span className="font-medium text-pb-text-secondary">
              {article.author}
            </span>
            <span>&middot;</span>
            <span>{article.date}</span>
            <span>&middot;</span>
            <span className="font-mono text-pb-accent-blue">
              {article.readingTime}m
            </span>
          </div>
        </div>
      </article>
    </Link>
  );
}
