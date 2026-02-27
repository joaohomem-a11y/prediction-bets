"use client";

import { useTranslations } from "next-intl";
import { Link } from "@/i18n/navigation";

const SIGNAL_LINKS = [
  { key: "politics", href: "/category/politics" },
  { key: "crypto", href: "/category/crypto" },
  { key: "aiTech", href: "/category/ai-tech" },
  { key: "markets", href: "/category/markets" },
] as const;

const TRIBE_LINKS = [
  { key: "community", href: "/community" },
  { key: "about", href: "/about" },
  { key: "newsletter", href: "/newsletter" },
] as const;

export default function Footer() {
  const tNav = useTranslations("nav");
  const tFooter = useTranslations("footer");
  const year = new Date().getFullYear();

  return (
    <footer className="bg-pb-bg-secondary border-t border-white/5">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">

        {/* Main grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-8 lg:gap-12">

          {/* Col 1–2: Brand */}
          <div className="sm:col-span-2 flex flex-col gap-4">
            <Link
              href="/"
              className="inline-flex items-center font-bold text-xl tracking-tight select-none w-fit"
              aria-label="Prediction Bets home"
            >
              <span className="text-pb-text-primary">PREDICTION</span>
              <span className="text-pb-accent-blue">BETS</span>
            </Link>
            <p className="text-pb-text-secondary text-sm leading-relaxed max-w-xs">
              {tFooter("tagline")}
            </p>
            {/* Social / decorative dots */}
            <div className="flex items-center gap-2 mt-2">
              <span className="w-2 h-2 rounded-full bg-pb-accent-blue" />
              <span className="w-2 h-2 rounded-full bg-pb-accent-amber" />
              <span className="w-2 h-2 rounded-full bg-pb-success" />
            </div>
          </div>

          {/* Col 3: Signal links */}
          <div className="flex flex-col gap-3">
            <p className="text-pb-text-muted text-xs font-mono uppercase tracking-widest">
              Signal
            </p>
            <ul className="flex flex-col gap-2">
              {SIGNAL_LINKS.map(({ key, href }) => (
                <li key={key}>
                  <Link
                    href={href}
                    className="text-sm text-pb-text-secondary hover:text-pb-text-primary transition-colors"
                  >
                    {tNav(key)}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          {/* Col 4: Tribe links */}
          <div className="flex flex-col gap-3">
            <p className="text-pb-text-muted text-xs font-mono uppercase tracking-widest">
              Tribe
            </p>
            <ul className="flex flex-col gap-2">
              {TRIBE_LINKS.map(({ key, href }) => (
                <li key={key}>
                  <Link
                    href={href}
                    className="text-sm text-pb-text-secondary hover:text-pb-text-primary transition-colors"
                  >
                    {tNav(key)}
                  </Link>
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* Bottom bar */}
        <div className="mt-12 pt-6 border-t border-white/5 flex flex-col sm:flex-row items-center justify-between gap-2">
          <p className="text-pb-text-muted text-xs font-mono">
            &copy; {year} PredictionBets.
          </p>
          <p className="text-pb-text-muted text-xs">
            {tFooter("rights")}
          </p>
        </div>
      </div>
    </footer>
  );
}
