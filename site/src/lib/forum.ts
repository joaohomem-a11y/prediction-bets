export const FORUM_SECTIONS = [
  {
    key: "signalDrop",
    slug: "signal-drop",
    description: "Breaking prediction market news and fresh signals",
    emoji: "📡",
  },
  {
    key: "contrarianTakes",
    slug: "contrarian-takes",
    description: "Challenge the consensus. Defend your position.",
    emoji: "🔥",
  },
  {
    key: "predictionBattles",
    slug: "prediction-battles",
    description: "Head-to-head prediction challenges",
    emoji: "⚔️",
  },
  {
    key: "realityCheck",
    slug: "reality-check",
    description: "When markets prove opinions wrong",
    emoji: "✅",
  },
  {
    key: "edgeLab",
    slug: "edge-lab",
    description: "Strategies, tools, and analytical frameworks",
    emoji: "🧪",
  },
  {
    key: "offMarket",
    slug: "off-market",
    description: "Everything else. Memes, meta, and tribe vibes.",
    emoji: "🎲",
  },
] as const;

export type ForumSection = (typeof FORUM_SECTIONS)[number]["slug"];

export function getSectionBySlug(slug: string) {
  return FORUM_SECTIONS.find((s) => s.slug === slug);
}

export function getSectionByKey(key: string) {
  return FORUM_SECTIONS.find((s) => s.key === key);
}
