import { useTranslations } from "next-intl";
import { Link } from "@/i18n/navigation";
import { FORUM_SECTIONS } from "@/lib/forum";

export default function CommunityPage() {
  const t = useTranslations("community");

  return (
    <section className="max-w-4xl mx-auto px-4 py-12">
      <div className="text-center mb-10">
        <h1 className="text-4xl font-bold text-pb-text-primary mb-3">
          {t("title")}
        </h1>
        <p className="text-pb-text-secondary text-lg">{t("subtitle")}</p>
      </div>

      <div className="grid gap-4 sm:grid-cols-2">
        {FORUM_SECTIONS.map((section) => (
          <Link
            key={section.slug}
            href={`/community/${section.slug}`}
            className="card p-6 block group"
          >
            <div className="flex items-start gap-3">
              <span className="text-2xl">{section.emoji}</span>
              <div>
                <h2 className="font-semibold text-pb-text-primary text-lg group-hover:text-pb-accent-blue transition-colors">
                  {t(`sections.${section.key}` as Parameters<typeof t>[0])}
                </h2>
                <p className="text-sm text-pb-text-muted mt-1">
                  {section.description}
                </p>
              </div>
            </div>
          </Link>
        ))}
      </div>
    </section>
  );
}
