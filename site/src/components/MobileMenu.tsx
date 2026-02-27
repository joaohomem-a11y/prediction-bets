"use client";

import { useTranslations } from "next-intl";
import { Link, usePathname } from "@/i18n/navigation";

const NAV_LINKS = [
  { key: "trending", href: "/" },
  { key: "politics", href: "/category/politics" },
  { key: "crypto", href: "/category/crypto" },
  { key: "aiTech", href: "/category/ai-tech" },
  { key: "sports", href: "/category/sports" },
  { key: "markets", href: "/category/markets" },
  { key: "culture", href: "/category/culture" },
] as const;

const EXTRA_LINKS = [
  { key: "community", href: "/community" },
  { key: "about", href: "/about" },
  { key: "newsletter", href: "/newsletter" },
] as const;

interface MobileMenuProps {
  onClose: () => void;
}

export default function MobileMenu({ onClose }: MobileMenuProps) {
  const t = useTranslations("nav");
  const pathname = usePathname();

  return (
    <div className="fixed inset-0 z-40 flex flex-col">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/60 backdrop-blur-sm"
        onClick={onClose}
        aria-hidden="true"
      />

      {/* Panel */}
      <nav
        className="relative z-50 mt-16 bg-pb-bg-secondary border-t border-white/5 flex flex-col overflow-y-auto max-h-[calc(100vh-4rem)]"
        aria-label="Mobile navigation"
      >
        {/* Category links */}
        <div className="px-4 py-3 border-b border-white/5">
          <p className="text-pb-text-muted text-xs font-mono uppercase tracking-widest mb-2 px-2">
            Signal
          </p>
          {NAV_LINKS.map(({ key, href }) => {
            const isActive = pathname === href;
            return (
              <Link
                key={key}
                href={href}
                onClick={onClose}
                className={[
                  "flex items-center gap-3 px-2 py-3 rounded-lg text-sm font-medium transition-colors",
                  isActive
                    ? "text-pb-accent-blue bg-pb-accent-blue/10"
                    : "text-pb-text-secondary hover:text-pb-text-primary hover:bg-pb-bg-surface",
                ]
                  .filter(Boolean)
                  .join(" ")}
              >
                {isActive && (
                  <span className="w-1 h-1 rounded-full bg-pb-accent-blue" />
                )}
                {t(key)}
              </Link>
            );
          })}
        </div>

        {/* Extra links */}
        <div className="px-4 py-3 border-b border-white/5">
          <p className="text-pb-text-muted text-xs font-mono uppercase tracking-widest mb-2 px-2">
            Tribe
          </p>
          {EXTRA_LINKS.map(({ key, href }) => (
            <Link
              key={key}
              href={href}
              onClick={onClose}
              className="flex items-center px-2 py-3 rounded-lg text-sm font-medium text-pb-text-secondary hover:text-pb-text-primary hover:bg-pb-bg-surface transition-colors"
            >
              {t(key)}
            </Link>
          ))}
        </div>

        {/* CTA */}
        <div className="px-4 py-4">
          <Link
            href="/auth/signin"
            onClick={onClose}
            className="btn-primary w-full text-sm justify-center"
          >
            {t("joinTribe")}
          </Link>
        </div>
      </nav>
    </div>
  );
}
