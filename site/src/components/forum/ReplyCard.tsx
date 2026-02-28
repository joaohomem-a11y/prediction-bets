"use client";

import VoteButton from "./VoteButton";
import { timeAgo } from "@/lib/utils";

type ReplyData = {
  id: string;
  body: string;
  upvotes: number;
  downvotes: number;
  createdAt: string;
  parentReplyId: string | null;
  author: {
    id: string;
    name: string | null;
    image: string | null;
    role: string;
  };
};

type Props = {
  reply: ReplyData;
  depth?: number;
  onReply?: (replyId: string) => void;
};

export default function ReplyCard({ reply, depth = 0, onReply }: Props) {
  const indent = Math.min(depth, 4);

  return (
    <div
      className={`${indent > 0 ? "border-l border-white/5" : ""}`}
      style={{ marginLeft: indent > 0 ? `${indent * 1.5}rem` : 0 }}
    >
      <div className="p-4 flex items-start gap-3">
        <VoteButton
          replyId={reply.id}
          upvotes={reply.upvotes}
          downvotes={reply.downvotes}
        />
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 text-sm text-pb-text-muted mb-1">
            <span className="flex items-center gap-1.5">
              {reply.author.image ? (
                <img
                  src={reply.author.image}
                  alt=""
                  className="w-4 h-4 rounded-full"
                />
              ) : (
                <span className="w-4 h-4 rounded-full bg-pb-bg-surface-hover inline-block" />
              )}
              <span className="font-medium text-pb-text-secondary">
                {reply.author.name ?? "Anonymous"}
              </span>
            </span>
            <span>{timeAgo(reply.createdAt)}</span>
          </div>
          <p className="text-pb-text-primary text-sm leading-relaxed whitespace-pre-wrap">
            {reply.body}
          </p>
          {onReply && (
            <button
              onClick={() => onReply(reply.id)}
              className="text-xs text-pb-text-muted hover:text-pb-accent-blue transition-colors mt-2"
            >
              Reply
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
