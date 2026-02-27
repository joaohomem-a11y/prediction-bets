"use client";

import { useState } from "react";
import { useTranslations } from "next-intl";
import { Link, usePathname } from "@/i18n/navigation";
import LanguageSwitcher from "@/components/LanguageSwitcher";
import MobileMenu from "@/components/MobileMenu";

const NAV_LINKS = [
  { key: "trending", href: "/" },
  { key: "politics", href: "/category/politics" },
  { key: "crypto", href: "/category/crypto" },
  { key: "aiTech", href: "/category/ai-tech" },
  { key: "sports", href: "/category/sports" },
  { key: "markets", href: "/category/markets" },
  { key: "culture", href: "/category/culture" },
] as const;

export default function Header() {
  const t = useTranslations("nav");
  const pathname = usePathname();
  const [mobileOpen, setMobileOpen] = useState(false);

  return (
    <>
      <header className="sticky top-0 z-50 bg-pb-bg-primary/95 backdrop-blur-md border-b border-white/5">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16 gap-4">

            {/* Logo */}
            <Link
              href="/"
              className="flex-shrink-0 flex items-center gap-0 font-bold text-lg tracking-tight select-none"
              aria-label="Prediction Bets home"
            >
              <span className="text-pb-text-primary">PREDICTION</span>
              <span className="text-pb-accent-blue">BETS</span>
            </Link>

            {/* Desktop category nav */}
            <nav
              className="hidden lg:flex items-center gap-1 flex-1 justify-center"
              aria-label="Category navigation"
            >
              {NAV_LINKS.map(({ key, href }) => {
                const isActive = pathname === href;
                return (
                  <Link
                    key={key}
                    href={href}
                    className={[
                      "px-3 py-1.5 rounded-md text-sm font-medium transition-all duration-150 whitespace-nowrap",
                      isActive
                        ? "text-pb-accent-blue bg-pb-accent-blue/10"
                        : "text-pb-text-secondary hover:text-pb-text-primary hover:bg-pb-bg-surface",
                    ].join(" ")}
                  >
                    {t(key)}
                  </Link>
                );
              })}
            </nav>

            {/* Desktop right actions */}
            <div className="hidden lg:flex items-center gap-3 flex-shrink-0">
              <Link
                href="/community"
                className="text-sm font-medium text-pb-text-secondary hover:text-pb-text-primary transition-colors"
              >
                {t("community")}
              </Link>
              <LanguageSwitcher />
              <Link
                href="/auth/signup"
                className="btn-primary text-sm px-4 py-2"
              >
                {t("joinTribe")}
              </Link>
            </div>

            {/* Mobile hamburger */}
            <button
              className="lg:hidden flex items-center justify-center w-9 h-9 rounded-md text-pb-text-secondary hover:text-pb-text-primary hover:bg-pb-bg-surface transition-colors"
              onClick={() => setMobileOpen((prev) => !prev)}
              aria-expanded={mobileOpen}
              aria-controls="mobile-menu"
              aria-label={mobileOpen ? "Close menu" : "Open menu"}
            >
              {mobileOpen ? (
                /* X icon */
                <svg
                  width="20"
                  height="20"
                  viewBox="0 0 20 20"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  aria-hidden="true"
                >
                  <line x1="4" y1="4" x2="16" y2="16" />
                  <line x1="16" y1="4" x2="4" y2="16" />
                </svg>
              ) : (
                /* Hamburger icon */
                <svg
                  width="20"
                  height="20"
                  viewBox="0 0 20 20"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  aria-hidden="true"
                >
                  <line x1="3" y1="6" x2="17" y2="6" />
                  <line x1="3" y1="10" x2="17" y2="10" />
                  <line x1="3" y1="14" x2="17" y2="14" />
                </svg>
              )}
            </button>
          </div>
        </div>
      </header>

      {/* Mobile menu — rendered outside header so it overlays content */}
      {mobileOpen && (
        <MobileMenu onClose={() => setMobileOpen(false)} />
      )}
    </>
  );
}
