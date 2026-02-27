"use client";

import { useState } from "react";
import { useRouter } from "@/i18n/navigation";
import { FORUM_SECTIONS } from "@/lib/forum";

type Props = {
  defaultSection?: string;
};

export default function NewThreadForm({ defaultSection }: Props) {
  const router = useRouter();
  const [title, setTitle] = useState("");
  const [body, setBody] = useState("");
  const [section, setSection] = useState(defaultSection ?? "signal-drop");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!title.trim() || !body.trim() || loading) return;

    setLoading(true);
    setError("");

    try {
      const res = await fetch("/api/forum/threads", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          title: title.trim(),
          body: body.trim(),
          section,
        }),
      });

      if (!res.ok) {
        const data = await res.json();
        setError(data.error ?? "Failed to create thread");
        return;
      }

      const thread = await res.json();
      router.push(`/community/${section}/${thread.id}`);
    } catch {
      setError("Failed to create thread");
    } finally {
      setLoading(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-5">
      <div>
        <label
          htmlFor="section"
          className="block text-sm font-medium text-pb-text-secondary mb-1.5"
        >
          Section
        </label>
        <select
          id="section"
          value={section}
          onChange={(e) => setSection(e.target.value)}
          className="w-full bg-pb-bg-secondary border border-white/10 rounded-lg p-3 text-sm text-pb-text-primary focus:outline-none focus:border-pb-accent-blue"
        >
          {FORUM_SECTIONS.map((s) => (
            <option key={s.slug} value={s.slug}>
              {s.emoji} {s.description}
            </option>
          ))}
        </select>
      </div>

      <div>
        <label
          htmlFor="title"
          className="block text-sm font-medium text-pb-text-secondary mb-1.5"
        >
          Title
        </label>
        <input
          id="title"
          type="text"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="What's your signal?"
          className="w-full bg-pb-bg-secondary border border-white/10 rounded-lg p-3 text-sm text-pb-text-primary placeholder:text-pb-text-muted focus:outline-none focus:border-pb-accent-blue"
        />
      </div>

      <div>
        <label
          htmlFor="body"
          className="block text-sm font-medium text-pb-text-secondary mb-1.5"
        >
          Body
        </label>
        <textarea
          id="body"
          value={body}
          onChange={(e) => setBody(e.target.value)}
          placeholder="Share your analysis, take, or signal..."
          rows={8}
          className="w-full bg-pb-bg-secondary border border-white/10 rounded-lg p-3 text-sm text-pb-text-primary placeholder:text-pb-text-muted focus:outline-none focus:border-pb-accent-blue resize-none"
        />
      </div>

      {error && <p className="text-pb-danger text-sm">{error}</p>}

      <button
        type="submit"
        disabled={loading || !title.trim() || !body.trim()}
        className="btn-primary w-full disabled:opacity-50"
      >
        {loading ? "Posting..." : "Drop Signal"}
      </button>
    </form>
  );
}
