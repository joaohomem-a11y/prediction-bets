"use client";

import { Link } from "@/i18n/navigation";
import VoteButton from "./VoteButton";
import { timeAgo } from "@/lib/utils";

type ThreadData = {
  id: string;
  title: string;
  section: string;
  upvotes: number;
  downvotes: number;
  createdAt: string;
  author: {
    id: string;
    name: string | null;
    image: string | null;
    role: string;
  };
  _count: {
    replies: number;
  };
};

type Props = {
  thread: ThreadData;
  sectionSlug: string;
};

export default function ThreadCard({ thread, sectionSlug }: Props) {
  return (
    <div className="card p-4 flex items-start gap-4">
      <VoteButton
        threadId={thread.id}
        upvotes={thread.upvotes}
        downvotes={thread.downvotes}
      />
      <div className="flex-1 min-w-0">
        <Link
          href={`/community/${sectionSlug}/${thread.id}`}
          className="text-pb-text-primary hover:text-pb-accent-blue transition-colors font-semibold text-lg leading-snug block"
        >
          {thread.title}
        </Link>
        <div className="flex items-center gap-3 mt-2 text-sm text-pb-text-muted">
          <span className="flex items-center gap-1.5">
            {thread.author.image ? (
              <img
                src={thread.author.image}
                alt=""
                className="w-4 h-4 rounded-full"
              />
            ) : (
              <span className="w-4 h-4 rounded-full bg-pb-bg-surface-hover inline-block" />
            )}
            <span className={thread.author.role === "moderator" ? "font-semibold text-amber-400" : ""}>
              {thread.author.name ?? "Anonymous"}
            </span>
            {thread.author.role === "moderator" && (
              <span className="text-[10px] font-bold uppercase tracking-wider bg-amber-400/20 text-amber-400 px-1.5 py-0.5 rounded">
                MOD
              </span>
            )}
          </span>
          <span>{timeAgo(thread.createdAt)}</span>
          <span className="flex items-center gap-1">
            <svg
              width="14"
              height="14"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
            </svg>
            {thread._count.replies}
          </span>
        </div>
      </div>
    </div>
  );
}
