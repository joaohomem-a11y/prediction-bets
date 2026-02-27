"use client";

import { useState, useEffect, useCallback } from "react";
import { useParams } from "next/navigation";
import { useSession } from "next-auth/react";
import { useTranslations } from "next-intl";
import { Link } from "@/i18n/navigation";
import { getSectionBySlug } from "@/lib/forum";
import ThreadCard from "@/components/forum/ThreadCard";

type ThreadData = {
  id: string;
  title: string;
  section: string;
  upvotes: number;
  downvotes: number;
  createdAt: string;
  author: { id: string; name: string | null; image: string | null };
  _count: { replies: number };
};

type SortOption = "new" | "hot" | "top";

export default function SectionPage() {
  const params = useParams();
  const sectionSlug = params.section as string;
  const section = getSectionBySlug(sectionSlug);
  const { data: session } = useSession();
  const t = useTranslations("community");

  const [threads, setThreads] = useState<ThreadData[]>([]);
  const [sort, setSort] = useState<SortOption>("new");
  const [loading, setLoading] = useState(true);

  const fetchThreads = useCallback(async () => {
    setLoading(true);
    try {
      const res = await fetch(
        `/api/forum/threads?section=${sectionSlug}&sort=${sort}`,
      );
      if (res.ok) {
        const data = await res.json();
        setThreads(data);
      }
    } catch {
      // silently fail
    } finally {
      setLoading(false);
    }
  }, [sectionSlug, sort]);

  useEffect(() => {
    fetchThreads();
  }, [fetchThreads]);

  if (!section) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-12 text-center">
        <h1 className="text-2xl font-bold text-pb-text-primary">
          Section not found
        </h1>
      </div>
    );
  }

  const sortTabs: { key: SortOption; label: string }[] = [
    { key: "new", label: "New" },
    { key: "hot", label: "Hot" },
    { key: "top", label: "Top" },
  ];

  return (
    <section className="max-w-4xl mx-auto px-4 py-12">
      <div className="mb-8">
        <Link
          href="/community"
          className="text-sm text-pb-text-muted hover:text-pb-accent-blue transition-colors mb-3 inline-block"
        >
          &larr; {t("title")}
        </Link>
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-pb-text-primary flex items-center gap-3">
              <span>{section.emoji}</span>
              {t(`sections.${section.key}` as Parameters<typeof t>[0])}
            </h1>
            <p className="text-pb-text-muted mt-1">{section.description}</p>
          </div>
          {session ? (
            <Link
              href={`/community/new?section=${sectionSlug}`}
              className="btn-primary text-sm"
            >
              {t("newThread")}
            </Link>
          ) : null}
        </div>
      </div>

      {/* Sort tabs */}
      <div className="flex gap-1 mb-6 bg-pb-bg-secondary rounded-lg p-1 w-fit">
        {sortTabs.map((tab) => (
          <button
            key={tab.key}
            onClick={() => setSort(tab.key)}
            className={`px-4 py-1.5 rounded-md text-sm font-medium transition-colors ${
              sort === tab.key
                ? "bg-pb-bg-surface text-pb-text-primary"
                : "text-pb-text-muted hover:text-pb-text-secondary"
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Thread list */}
      {loading ? (
        <div className="space-y-3">
          {[1, 2, 3].map((i) => (
            <div
              key={i}
              className="card p-4 h-20 animate-pulse bg-pb-bg-surface"
            />
          ))}
        </div>
      ) : threads.length === 0 ? (
        <div className="card p-8 text-center">
          <p className="text-pb-text-muted mb-4">
            No threads yet. Be the first to drop a signal.
          </p>
          {session ? (
            <Link
              href={`/community/new?section=${sectionSlug}`}
              className="btn-primary text-sm"
            >
              {t("newThread")}
            </Link>
          ) : (
            <p className="text-sm text-pb-text-secondary">
              Join the Tribe to participate.
            </p>
          )}
        </div>
      ) : (
        <div className="space-y-3">
          {threads.map((thread) => (
            <ThreadCard
              key={thread.id}
              thread={thread}
              sectionSlug={sectionSlug}
            />
          ))}
        </div>
      )}
    </section>
  );
}
