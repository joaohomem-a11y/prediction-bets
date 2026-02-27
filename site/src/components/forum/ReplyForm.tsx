"use client";

import { useState } from "react";

type Props = {
  threadId: string;
  parentReplyId?: string | null;
  onSuccess?: () => void;
  onCancel?: () => void;
};

export default function ReplyForm({
  threadId,
  parentReplyId,
  onSuccess,
  onCancel,
}: Props) {
  const [body, setBody] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!body.trim() || loading) return;

    setLoading(true);
    setError("");

    try {
      const res = await fetch(`/api/forum/threads/${threadId}/replies`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          body: body.trim(),
          parentReplyId: parentReplyId ?? undefined,
        }),
      });

      if (!res.ok) {
        const data = await res.json();
        setError(data.error ?? "Failed to post reply");
        return;
      }

      setBody("");
      onSuccess?.();
    } catch {
      setError("Failed to post reply");
    } finally {
      setLoading(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-3">
      <textarea
        value={body}
        onChange={(e) => setBody(e.target.value)}
        placeholder={parentReplyId ? "Write a reply..." : "Share your take..."}
        rows={3}
        className="w-full bg-pb-bg-secondary border border-white/10 rounded-lg p-3 text-sm text-pb-text-primary placeholder:text-pb-text-muted focus:outline-none focus:border-pb-accent-blue resize-none"
      />
      {error && <p className="text-pb-danger text-sm">{error}</p>}
      <div className="flex items-center gap-2">
        <button
          type="submit"
          disabled={loading || !body.trim()}
          className="btn-primary text-sm px-4 py-2 disabled:opacity-50"
        >
          {loading ? "Posting..." : "Reply"}
        </button>
        {onCancel && (
          <button
            type="button"
            onClick={onCancel}
            className="btn-secondary text-sm px-4 py-2"
          >
            Cancel
          </button>
        )}
      </div>
    </form>
  );
}
