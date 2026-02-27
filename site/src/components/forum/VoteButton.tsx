"use client";

import { useState } from "react";

type Props = {
  threadId?: string;
  replyId?: string;
  upvotes: number;
  downvotes: number;
  userVote?: number | null;
};

export default function VoteButton({
  threadId,
  replyId,
  upvotes: initialUp,
  downvotes: initialDown,
  userVote: initialVote,
}: Props) {
  const [upvotes, setUpvotes] = useState(initialUp);
  const [downvotes, setDownvotes] = useState(initialDown);
  const [userVote, setUserVote] = useState<number | null>(initialVote ?? null);
  const [loading, setLoading] = useState(false);

  const score = upvotes - downvotes;

  async function vote(value: 1 | -1) {
    if (loading) return;
    setLoading(true);

    // Optimistic update
    const prevUp = upvotes;
    const prevDown = downvotes;
    const prevVote = userVote;

    if (userVote === value) {
      // Toggle off
      setUserVote(null);
      if (value === 1) setUpvotes((v) => v - 1);
      else setDownvotes((v) => v - 1);
    } else if (userVote !== null) {
      // Switch vote
      setUserVote(value);
      if (value === 1) {
        setUpvotes((v) => v + 1);
        setDownvotes((v) => v - 1);
      } else {
        setUpvotes((v) => v - 1);
        setDownvotes((v) => v + 1);
      }
    } else {
      // New vote
      setUserVote(value);
      if (value === 1) setUpvotes((v) => v + 1);
      else setDownvotes((v) => v + 1);
    }

    try {
      const res = await fetch("/api/forum/vote", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ threadId, replyId, value }),
      });

      if (!res.ok) {
        // Revert on error
        setUpvotes(prevUp);
        setDownvotes(prevDown);
        setUserVote(prevVote);
      }
    } catch {
      setUpvotes(prevUp);
      setDownvotes(prevDown);
      setUserVote(prevVote);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex items-center gap-1">
      <button
        onClick={() => vote(1)}
        disabled={loading}
        className={`p-1 rounded transition-colors ${
          userVote === 1
            ? "text-pb-accent-blue"
            : "text-pb-text-muted hover:text-pb-text-primary"
        }`}
        aria-label="Upvote"
      >
        <svg
          width="16"
          height="16"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        >
          <path d="M12 19V5M5 12l7-7 7 7" />
        </svg>
      </button>
      <span
        className={`text-sm font-mono font-semibold min-w-[2ch] text-center ${
          score > 0
            ? "text-pb-success"
            : score < 0
              ? "text-pb-danger"
              : "text-pb-text-muted"
        }`}
      >
        {score}
      </span>
      <button
        onClick={() => vote(-1)}
        disabled={loading}
        className={`p-1 rounded transition-colors ${
          userVote === -1
            ? "text-pb-danger"
            : "text-pb-text-muted hover:text-pb-text-primary"
        }`}
        aria-label="Downvote"
      >
        <svg
          width="16"
          height="16"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        >
          <path d="M12 5v14M19 12l-7 7-7-7" />
        </svg>
      </button>
    </div>
  );
}
