import type { JsonValue } from "@prisma/client/runtime/library";

type Translations = Record<string, Record<string, string>>;

function parseTranslations(raw: JsonValue | null | undefined): Translations | null {
  if (!raw || typeof raw !== "object" || Array.isArray(raw)) return null;
  return raw as unknown as Translations;
}

/**
 * Apply translations to a thread object based on the requested locale.
 * Falls back to original content if translation is unavailable.
 */
export function translateThread<
  T extends { title: string; body: string; translations?: JsonValue | null },
>(thread: T, locale: string): T {
  const trans = parseTranslations(thread.translations);
  if (!trans || !trans[locale]) return thread;

  return {
    ...thread,
    title: trans[locale].title ?? thread.title,
    body: trans[locale].body ?? thread.body,
  };
}

/**
 * Apply translations to a reply object based on the requested locale.
 */
export function translateReply<
  T extends { body: string; translations?: JsonValue | null },
>(reply: T, locale: string): T {
  const trans = parseTranslations(reply.translations);
  if (!trans || !trans[locale]) return reply;

  return {
    ...reply,
    body: trans[locale].body ?? reply.body,
  };
}
