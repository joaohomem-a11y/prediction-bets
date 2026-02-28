"use client";

import { useState, useEffect, useCallback } from "react";
import { useParams } from "next/navigation";
import { useSession } from "next-auth/react";
import { useTranslations } from "next-intl";
import { Link } from "@/i18n/navigation";
import { getSectionBySlug } from "@/lib/forum";
import { timeAgo } from "@/lib/utils";
import VoteButton from "@/components/forum/VoteButton";
import ReplyCard from "@/components/forum/ReplyCard";
import ReplyForm from "@/components/forum/ReplyForm";

type ReplyData = {
  id: string;
  body: string;
  upvotes: number;
  downvotes: number;
  createdAt: string;
  parentReplyId: string | null;
  author: { id: string; name: string | null; image: string | null; role: string };
  _count: { childReplies: number };
};

type ThreadDetail = {
  id: string;
  title: string;
  body: string;
  section: string;
  upvotes: number;
  downvotes: number;
  createdAt: string;
  author: { id: string; name: string | null; image: string | null; role: string };
  replies: ReplyData[];
  _count: { replies: number };
};

export default function ThreadDetailPage() {
  const params = useParams();
  const sectionSlug = params.section as string;
  const threadId = params.threadId as string;
  const section = getSectionBySlug(sectionSlug);
  const { data: session } = useSession();
  const t = useTranslations("community");

  const [thread, setThread] = useState<ThreadDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [replyTo, setReplyTo] = useState<string | null>(null);

  const fetchThread = useCallback(async () => {
    try {
      const res = await fetch(`/api/forum/threads/${threadId}`);
      if (res.ok) {
        const data = await res.json();
        setThread(data);
      }
    } catch {
      // silently fail
    } finally {
      setLoading(false);
    }
  }, [threadId]);

  useEffect(() => {
    fetchThread();
  }, [fetchThread]);

  if (loading) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-12">
        <div className="card p-6 animate-pulse bg-pb-bg-surface h-48" />
      </div>
    );
  }

  if (!thread) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-12 text-center">
        <h1 className="text-2xl font-bold text-pb-text-primary">
          Thread not found
        </h1>
      </div>
    );
  }

  // Build nested reply tree
  const topLevelReplies = thread.replies.filter((r) => !r.parentReplyId);
  const childRepliesMap = new Map<string, ReplyData[]>();
  for (const reply of thread.replies) {
    if (reply.parentReplyId) {
      const children = childRepliesMap.get(reply.parentReplyId) ?? [];
      children.push(reply);
      childRepliesMap.set(reply.parentReplyId, children);
    }
  }

  function renderReplies(replies: ReplyData[], depth: number) {
    return replies.map((reply) => {
      const children = childRepliesMap.get(reply.id) ?? [];
      return (
        <div key={reply.id}>
          <ReplyCard
            reply={reply}
            depth={depth}
            onReply={session ? (id) => setReplyTo(id) : undefined}
          />
          {replyTo === reply.id && session && (
            <div
              className="pl-6 pb-4"
              style={{ marginLeft: `${Math.min(depth + 1, 4) * 1.5}rem` }}
            >
              <ReplyForm
                threadId={thread!.id}
                parentReplyId={reply.id}
                onSuccess={() => {
                  setReplyTo(null);
                  fetchThread();
                }}
                onCancel={() => setReplyTo(null)}
              />
            </div>
          )}
          {children.length > 0 && renderReplies(children, depth + 1)}
        </div>
      );
    });
  }

  return (
    <section className="max-w-4xl mx-auto px-4 py-12">
      {/* Breadcrumb */}
      <div className="flex items-center gap-2 text-sm text-pb-text-muted mb-6">
        <Link
          href="/community"
          className="hover:text-pb-accent-blue transition-colors"
        >
          {t("title")}
        </Link>
        <span>/</span>
        <Link
          href={`/community/${sectionSlug}`}
          className="hover:text-pb-accent-blue transition-colors"
        >
          {section
            ? t(`sections.${section.key}` as Parameters<typeof t>[0])
            : sectionSlug}
        </Link>
      </div>

      {/* Thread content */}
      <div className="card p-6 mb-6">
        <div className="flex items-start gap-4">
          <VoteButton
            threadId={thread.id}
            upvotes={thread.upvotes}
            downvotes={thread.downvotes}
          />
          <div className="flex-1 min-w-0">
            <h1 className="text-2xl font-bold text-pb-text-primary mb-3">
              {thread.title}
            </h1>
            <div className="flex items-center gap-3 text-sm text-pb-text-muted mb-4">
              <span className="flex items-center gap-1.5">
                {thread.author.image ? (
                  <img
                    src={thread.author.image}
                    alt=""
                    className="w-5 h-5 rounded-full"
                  />
                ) : (
                  <span className="w-5 h-5 rounded-full bg-pb-bg-surface-hover inline-block" />
                )}
                <span className={`font-medium ${thread.author.role === "moderator" ? "text-amber-400" : "text-pb-text-secondary"}`}>
                  {thread.author.name ?? "Anonymous"}
                </span>
                {thread.author.role === "moderator" && (
                  <span className="text-[10px] font-bold uppercase tracking-wider bg-amber-400/20 text-amber-400 px-1.5 py-0.5 rounded">
                    MOD
                  </span>
                )}
              </span>
              <span>{timeAgo(thread.createdAt)}</span>
            </div>
            <div className="text-pb-text-primary leading-relaxed whitespace-pre-wrap">
              {thread.body}
            </div>
          </div>
        </div>
      </div>

      {/* Replies section */}
      <div className="mb-6">
        <h2 className="text-lg font-semibold text-pb-text-primary mb-4">
          {thread._count.replies}{" "}
          {thread._count.replies === 1 ? "Reply" : "Replies"}
        </h2>

        {thread.replies.length > 0 ? (
          <div className="card divide-y divide-white/5">
            {renderReplies(topLevelReplies, 0)}
          </div>
        ) : (
          <div className="card p-6 text-center text-pb-text-muted">
            No replies yet. Be the first to share your take.
          </div>
        )}
      </div>

      {/* Reply form */}
      {session ? (
        <div className="card p-6">
          <h3 className="text-sm font-medium text-pb-text-secondary mb-3">
            {t("reply")}
          </h3>
          <ReplyForm threadId={thread.id} onSuccess={fetchThread} />
        </div>
      ) : (
        <div className="card p-6 text-center">
          <p className="text-pb-text-muted">
            Join the Tribe to participate in the discussion.
          </p>
        </div>
      )}
    </section>
  );
}
