import type { Category } from "@/types/article";

const categoryStyles: Record<Category, string> = {
  politics: "bg-purple-500/10 text-purple-400",
  crypto: "bg-orange-500/10 text-orange-400",
  "ai-tech": "bg-cyan-500/10 text-cyan-400",
  sports: "bg-green-500/10 text-green-400",
  markets: "bg-blue-500/10 text-blue-400",
  culture: "bg-pink-500/10 text-pink-400",
  geopolitics: "bg-red-500/10 text-red-400",
};

const categoryLabels: Record<Category, string> = {
  politics: "Politics",
  crypto: "Crypto",
  "ai-tech": "AI & Tech",
  sports: "Sports",
  markets: "Markets",
  culture: "Culture",
  geopolitics: "Geopolitics",
};

export default function CategoryBadge({ category }: { category: Category }) {
  return (
    <span className={`badge ${categoryStyles[category] ?? "bg-white/5 text-white/60"}`}>
      {categoryLabels[category] ?? category}
    </span>
  );
}
