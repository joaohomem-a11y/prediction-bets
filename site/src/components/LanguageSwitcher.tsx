"use client";

import { useLocale } from "next-intl";
import { useRouter, usePathname } from "@/i18n/navigation";
import { useTransition } from "react";

const LOCALES = [
  { code: "en", label: "EN" },
  { code: "pt", label: "PT" },
  { code: "es", label: "ES" },
] as const;

export default function LanguageSwitcher() {
  const locale = useLocale();
  const router = useRouter();
  const pathname = usePathname();
  const [isPending, startTransition] = useTransition();

  function handleLocaleChange(nextLocale: string) {
    startTransition(() => {
      router.replace(pathname, { locale: nextLocale });
    });
  }

  return (
    <div
      className="flex items-center gap-0.5 rounded-md bg-pb-bg-surface border border-white/10 p-0.5"
      aria-label="Language switcher"
    >
      {LOCALES.map(({ code, label }) => (
        <button
          key={code}
          onClick={() => handleLocaleChange(code)}
          disabled={isPending}
          aria-pressed={locale === code}
          className={[
            "font-mono text-xs font-medium px-2 py-1 rounded transition-all duration-150 cursor-pointer",
            locale === code
              ? "bg-pb-accent-blue text-white"
              : "text-pb-text-secondary hover:text-pb-text-primary",
            isPending ? "opacity-50 cursor-not-allowed" : "",
          ]
            .filter(Boolean)
            .join(" ")}
        >
          {label}
        </button>
      ))}
    </div>
  );
}
