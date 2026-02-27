import { useTranslations } from "next-intl";

export default function HomePage() {
  const t = useTranslations("home");
  return (
    <div className="flex flex-col items-center justify-center min-h-screen p-8">
      <h1 className="text-5xl font-bold text-pb-text-primary mb-4 tracking-tight">
        PREDICTION<span className="text-pb-accent-blue">BETS</span>
      </h1>
      <p className="text-xl text-pb-accent-blue font-mono">
        {t("hero")}
      </p>
      <p className="mt-2 text-pb-text-secondary">
        {t("subtitle")}
      </p>
    </div>
  );
}
