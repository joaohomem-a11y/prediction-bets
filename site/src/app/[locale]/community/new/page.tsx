"use client";

import { useSearchParams } from "next/navigation";
import { useSession } from "next-auth/react";
import { useTranslations } from "next-intl";
import { Link } from "@/i18n/navigation";
import NewThreadForm from "@/components/forum/NewThreadForm";

export default function NewThreadPage() {
  const searchParams = useSearchParams();
  const defaultSection = searchParams.get("section") ?? undefined;
  const { data: session, status } = useSession();
  const t = useTranslations("community");

  if (status === "loading") {
    return (
      <div className="max-w-2xl mx-auto px-4 py-12">
        <div className="card p-6 animate-pulse bg-pb-bg-surface h-48" />
      </div>
    );
  }

  if (!session) {
    return (
      <section className="max-w-2xl mx-auto px-4 py-12 text-center">
        <div className="card p-8">
          <h1 className="text-2xl font-bold text-pb-text-primary mb-3">
            Join the Tribe
          </h1>
          <p className="text-pb-text-muted mb-6">
            Sign in to drop a signal and participate in the community.
          </p>
          <Link href="/auth/signin" className="btn-primary">
            Sign In
          </Link>
        </div>
      </section>
    );
  }

  return (
    <section className="max-w-2xl mx-auto px-4 py-12">
      <Link
        href="/community"
        className="text-sm text-pb-text-muted hover:text-pb-accent-blue transition-colors mb-6 inline-block"
      >
        &larr; {t("title")}
      </Link>

      <h1 className="text-3xl font-bold text-pb-text-primary mb-8">
        {t("newThread")}
      </h1>

      <div className="card p-6">
        <NewThreadForm defaultSection={defaultSection} />
      </div>
    </section>
  );
}
