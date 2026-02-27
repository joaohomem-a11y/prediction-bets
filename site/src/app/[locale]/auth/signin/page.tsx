"use client";

import { useState } from "react";
import { signIn } from "next-auth/react";
import { useTranslations } from "next-intl";

export default function SignInPage() {
  const t = useTranslations("auth");
  const [email, setEmail] = useState("");

  return (
    <div className="min-h-screen flex items-center justify-center px-4">
      <div className="card p-8 sm:p-10 w-full max-w-md">
        <h1 className="text-2xl font-bold text-pb-text-primary text-center mb-2">
          {t("signUp")}
        </h1>
        <p className="text-pb-text-muted text-center text-sm mb-8">
          {t("verifyEmail")}
        </p>

        {/* Social providers */}
        <div className="flex flex-col gap-3 mb-6">
          <button
            onClick={() => signIn("google", { callbackUrl: "/" })}
            className="btn-secondary w-full gap-2"
          >
            <svg className="w-5 h-5" viewBox="0 0 24 24" fill="currentColor">
              <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92a5.06 5.06 0 0 1-2.2 3.32v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.1z" />
              <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" />
              <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" />
              <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" />
            </svg>
            Google
          </button>

          <button
            onClick={() => signIn("apple", { callbackUrl: "/" })}
            className="btn-secondary w-full gap-2"
          >
            <svg className="w-5 h-5" viewBox="0 0 24 24" fill="currentColor">
              <path d="M17.05 20.28c-.98.95-2.05.88-3.08.4-1.09-.5-2.08-.48-3.24 0-1.44.62-2.2.44-3.06-.4C2.79 15.25 3.51 7.59 9.05 7.31c1.35.07 2.29.74 3.08.8 1.18-.24 2.31-.93 3.57-.84 1.51.12 2.65.72 3.4 1.8-3.12 1.87-2.38 5.98.48 7.13-.57 1.5-1.31 2.99-2.54 4.09zM12.03 7.25c-.15-2.23 1.66-4.07 3.74-4.25.29 2.58-2.34 4.5-3.74 4.25z" />
            </svg>
            Apple
          </button>

          <button
            onClick={() => signIn("facebook", { callbackUrl: "/" })}
            className="btn-secondary w-full gap-2"
          >
            <svg className="w-5 h-5" viewBox="0 0 24 24" fill="currentColor">
              <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z" />
            </svg>
            Facebook
          </button>
        </div>

        {/* Divider */}
        <div className="flex items-center gap-3 mb-6">
          <div className="flex-1 h-px bg-white/10" />
          <span className="text-xs text-pb-text-muted uppercase tracking-wider">
            {t("orContinueWith")}
          </span>
          <div className="flex-1 h-px bg-white/10" />
        </div>

        {/* Email magic link */}
        <form
          onSubmit={(e) => {
            e.preventDefault();
            signIn("email", { email, callbackUrl: "/" });
          }}
          className="flex flex-col gap-3"
        >
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder={t("email")}
            required
            className="w-full px-4 py-3 rounded-lg bg-pb-bg-primary border border-white/10 text-pb-text-primary placeholder:text-pb-text-muted focus:outline-none focus:border-pb-accent-blue transition-colors"
            aria-label={t("email")}
          />
          <button type="submit" className="btn-primary w-full">
            {t("signIn")}
          </button>
        </form>
      </div>
    </div>
  );
}
