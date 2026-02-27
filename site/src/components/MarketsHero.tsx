import { useTranslations } from "next-intl";

/** Hardcoded trending markets — replace with API/DB data later */
const MARKETS = [
  {
    id: "btc-150k",
    question: "Bitcoin above $150K by Dec 2026?",
    questionPt: "Bitcoin acima de $150K até Dez 2026?",
    questionEs: "¿Bitcoin sobre $150K para Dic 2026?",
    yesPercent: 42,
    volume: "$12.4M",
    category: "crypto",
  },
  {
    id: "fed-cuts",
    question: "Fed cuts rates before July 2026?",
    questionPt: "Fed corta juros antes de Julho 2026?",
    questionEs: "¿Fed recorta tasas antes de Julio 2026?",
    yesPercent: 61,
    volume: "$8.7M",
    category: "markets",
  },
  {
    id: "ai-jobs",
    question: "AI replaces 10% of US jobs by 2028?",
    questionPt: "IA substitui 10% dos empregos nos EUA até 2028?",
    questionEs: "¿IA reemplaza 10% de empleos en EEUU para 2028?",
    yesPercent: 34,
    volume: "$5.2M",
    category: "ai-tech",
  },
  {
    id: "trump-2028",
    question: "Trump wins 2028 presidential election?",
    questionPt: "Trump vence eleição presidencial de 2028?",
    questionEs: "¿Trump gana elección presidencial 2028?",
    yesPercent: 28,
    volume: "$31.1M",
    category: "politics",
  },
  {
    id: "eth-flip",
    question: "Ethereum flips Bitcoin market cap by 2027?",
    questionPt: "Ethereum ultrapassa Bitcoin em market cap até 2027?",
    questionEs: "¿Ethereum supera Bitcoin en market cap para 2027?",
    yesPercent: 8,
    volume: "$3.8M",
    category: "crypto",
  },
] as const;

const CATEGORY_COLORS: Record<string, string> = {
  crypto: "text-pb-accent-amber bg-pb-accent-amber/10",
  markets: "text-pb-accent-blue bg-pb-accent-blue/10",
  "ai-tech": "text-purple-400 bg-purple-400/10",
  politics: "text-red-400 bg-red-400/10",
  sports: "text-green-400 bg-green-400/10",
  culture: "text-pink-400 bg-pink-400/10",
  geopolitics: "text-orange-400 bg-orange-400/10",
};

function MarketCard({
  market,
  locale,
}: {
  market: (typeof MARKETS)[number];
  locale: string;
}) {
  const question =
    locale === "pt"
      ? market.questionPt
      : locale === "es"
        ? market.questionEs
        : market.question;

  const noPercent = 100 - market.yesPercent;
  const catColor = CATEGORY_COLORS[market.category] ?? CATEGORY_COLORS.markets;

  return (
    <div className="group bg-pb-bg-surface border border-white/5 rounded-lg p-4 hover:border-pb-accent-blue/20 transition-all cursor-pointer">
      {/* Top row: category + volume */}
      <div className="flex items-center justify-between mb-2">
        <span className={`text-[10px] font-semibold uppercase tracking-wider px-2 py-0.5 rounded-full ${catColor}`}>
          {market.category.replace("-", " ")}
        </span>
        <span className="text-[10px] font-mono text-pb-text-muted">
          {market.volume} Vol
        </span>
      </div>

      {/* Question */}
      <p className="text-sm font-medium text-pb-text-primary leading-snug mb-3 line-clamp-2 group-hover:text-pb-accent-blue transition-colors">
        {question}
      </p>

      {/* Probability bar */}
      <div className="flex items-center gap-2 mb-2">
        <div className="flex-1 h-1.5 rounded-full bg-pb-bg-primary overflow-hidden">
          <div
            className="h-full rounded-full bg-pb-success transition-all"
            style={{ width: `${market.yesPercent}%` }}
          />
        </div>
      </div>

      {/* Yes / No buttons */}
      <div className="flex items-center gap-2">
        <button className="flex-1 flex items-center justify-center gap-1.5 py-1.5 rounded-md bg-pb-success/10 text-pb-success text-xs font-semibold hover:bg-pb-success/20 transition-colors">
          Yes {market.yesPercent}¢
        </button>
        <button className="flex-1 flex items-center justify-center gap-1.5 py-1.5 rounded-md bg-pb-danger/10 text-pb-danger text-xs font-semibold hover:bg-pb-danger/20 transition-colors">
          No {noPercent}¢
        </button>
      </div>
    </div>
  );
}

export default function MarketsHero({ locale }: { locale: string }) {
  const t = useTranslations("home");

  return (
    <div className="flex flex-col h-full">
      <div className="flex items-center justify-between mb-3">
        <h2 className="text-sm font-semibold text-pb-text-secondary uppercase tracking-wider">
          {t("trendingMarkets")}
        </h2>
        <a
          href="https://polymarket.com"
          target="_blank"
          rel="noopener noreferrer"
          className="text-[10px] font-mono text-pb-text-muted hover:text-pb-accent-blue transition-colors flex items-center gap-1"
        >
          Powered by Polymarket
          <svg width="10" height="10" viewBox="0 0 12 12" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
            <path d="M4.5 1.5H2.5a1 1 0 00-1 1v7a1 1 0 001 1h7a1 1 0 001-1v-2" />
            <path d="M7.5 1.5h3v3" />
            <path d="M5 7L10.5 1.5" />
          </svg>
        </a>
      </div>

      <div className="flex flex-col gap-2.5 flex-1">
        {MARKETS.map((market) => (
          <MarketCard key={market.id} market={market} locale={locale} />
        ))}
      </div>
    </div>
  );
}
