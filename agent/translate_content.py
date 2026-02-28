#!/usr/bin/env python3
"""
Translate all forum threads and replies into EN, PT, and ES.

Stores translations as JSON in the `translations` column.
Format:
  Thread: {"en": {"title": "...", "body": "..."}, "pt": {...}, "es": {...}}
  Reply:  {"en": {"body": "..."}, "pt": {...}, "es": {...}}

Usage:
    python translate_content.py              # Translate all untranslated content
    python translate_content.py --dry-run    # Preview without updating
    python translate_content.py --force      # Re-translate everything
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path

import anthropic

from config import ANTHROPIC_API_KEY, CLAUDE_MODEL
from db import get_connection

LOCALES = ["en", "pt", "es"]
BATCH_SIZE = 15  # items per API call


def strip_markdown_fences(text: str) -> str:
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*\n?", "", text)
    text = re.sub(r"\n?```\s*$", "", text)
    return text.strip()


def build_translation_prompt(items: list[dict], target_locales: list[str]) -> str:
    """Build a prompt to translate multiple texts at once."""
    locale_names = {"en": "English", "pt": "Brazilian Portuguese", "es": "Spanish"}
    targets = ", ".join(locale_names[loc] for loc in target_locales)

    items_json = json.dumps(items, ensure_ascii=False, indent=2)

    return f"""Translate the following forum posts into {targets}.

INPUT (JSON array of objects with "id" and text fields like "title", "body"):
{items_json}

RULES:
- Preserve the original tone, slang, emojis, and formatting of each post
- Keep proper nouns, platform names (Polymarket, Kalshi, etc.), and technical terms as-is
- Translations should feel natural, not robotic — match the writing style
- If the text is already in the target language, return it as-is

OUTPUT: Return a JSON object where each key is an item "id", and the value is an object with locale keys.

Example output format:
{{
  "item-1": {{
    "en": {{"title": "English title", "body": "English body"}},
    "pt": {{"title": "Portuguese title", "body": "Portuguese body"}},
    "es": {{"title": "Spanish title", "body": "Spanish body"}}
  }},
  "item-2": {{
    "en": {{"body": "English body"}},
    "pt": {{"body": "Portuguese body"}},
    "es": {{"body": "Spanish body"}}
  }}
}}

Return ONLY valid JSON. No markdown, no explanation, no code fences."""


def translate_batch(
    client: anthropic.Anthropic,
    items: list[dict],
    target_locales: list[str],
) -> dict:
    """Translate a batch of items via Claude API."""
    prompt = build_translation_prompt(items, target_locales)

    response = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=16384,
        messages=[{"role": "user", "content": prompt}],
    )

    raw = response.content[0].text
    cleaned = strip_markdown_fences(raw)

    try:
        result = json.loads(cleaned)
    except json.JSONDecodeError as exc:
        print(f"  WARN: JSON parse failed: {exc}")
        print(f"  Retrying...")
        time.sleep(2)

        response = client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=16384,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = response.content[0].text
        cleaned = strip_markdown_fences(raw)
        result = json.loads(cleaned)

    return result


def fetch_threads(conn, force: bool) -> list[dict]:
    """Fetch threads that need translation."""
    with conn.cursor() as cur:
        if force:
            cur.execute('SELECT id, title, body, locale FROM "Thread" ORDER BY "createdAt"')
        else:
            cur.execute(
                'SELECT id, title, body, locale FROM "Thread" WHERE translations IS NULL ORDER BY "createdAt"'
            )
        rows = cur.fetchall()
    return [{"id": r[0], "title": r[1], "body": r[2], "locale": r[3]} for r in rows]


def fetch_replies(conn, force: bool) -> list[dict]:
    """Fetch replies that need translation."""
    with conn.cursor() as cur:
        if force:
            cur.execute('SELECT id, body, locale FROM "Reply" ORDER BY "createdAt"')
        else:
            cur.execute(
                'SELECT id, body, locale FROM "Reply" WHERE translations IS NULL ORDER BY "createdAt"'
            )
        rows = cur.fetchall()
    return [{"id": r[0], "body": r[1], "locale": r[2]} for r in rows]


def update_translations(conn, table: str, translations: dict) -> int:
    """Write translations JSON back to the database."""
    count = 0
    with conn.cursor() as cur:
        for item_id, trans in translations.items():
            cur.execute(
                f'UPDATE "{table}" SET translations = %s WHERE id = %s',
                (json.dumps(trans, ensure_ascii=False), item_id),
            )
            count += 1
    conn.commit()
    return count


def detect_locale_from_content(text: str) -> str:
    """Simple heuristic to detect if content is EN, PT, or ES."""
    text_lower = text.lower()
    # Portuguese markers
    pt_words = ["você", "não", "são", "está", "mercado", "previsão", "também",
                "porque", "ainda", "pode", "então", "acho", "muito", "como"]
    # Spanish markers
    es_words = ["está", "también", "porque", "puede", "mercado", "predicción",
                "pero", "como", "más", "todos", "creo", "muy", "ahora"]

    pt_score = sum(1 for w in pt_words if w in text_lower)
    es_score = sum(1 for w in es_words if w in text_lower)

    if pt_score >= 3:
        return "pt"
    if es_score >= 3:
        return "es"
    return "en"


def main() -> None:
    parser = argparse.ArgumentParser(description="Translate forum content")
    parser.add_argument("--dry-run", action="store_true", help="Preview without updating")
    parser.add_argument("--force", action="store_true", help="Re-translate all content")
    args = parser.parse_args()

    if not ANTHROPIC_API_KEY:
        print("ERROR: ANTHROPIC_API_KEY is not set.")
        sys.exit(1)

    conn = get_connection()
    print("Connected to database.")

    # Fetch content
    threads = fetch_threads(conn, args.force)
    replies = fetch_replies(conn, args.force)

    print(f"Threads to translate: {len(threads)}")
    print(f"Replies to translate: {len(replies)}")

    if not threads and not replies:
        print("Nothing to translate!")
        conn.close()
        return

    if args.dry_run:
        print("\nDRY RUN — would translate the above. Exiting.")
        conn.close()
        return

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    # --- Detect and update locale for existing content ---
    print("\nDetecting original language of content...")
    with conn.cursor() as cur:
        for t in threads:
            detected = detect_locale_from_content(t["title"] + " " + t["body"])
            t["locale"] = detected
            cur.execute('UPDATE "Thread" SET locale = %s WHERE id = %s', (detected, t["id"]))
        for r in replies:
            detected = detect_locale_from_content(r["body"])
            r["locale"] = detected
            cur.execute('UPDATE "Reply" SET locale = %s WHERE id = %s', (detected, r["id"]))
    conn.commit()
    print("  Locale detection done.")

    # --- Translate threads ---
    if threads:
        print(f"\nTranslating {len(threads)} threads...")
        total_batches = (len(threads) + BATCH_SIZE - 1) // BATCH_SIZE

        for i in range(0, len(threads), BATCH_SIZE):
            batch = threads[i : i + BATCH_SIZE]
            batch_num = i // BATCH_SIZE + 1
            print(f"  Batch {batch_num}/{total_batches} ({len(batch)} threads)...")

            # Prepare items for API
            api_items = [{"id": t["id"], "title": t["title"], "body": t["body"]} for t in batch]

            try:
                result = translate_batch(client, api_items, LOCALES)
                updated = update_translations(conn, "Thread", result)
                print(f"    Updated {updated} threads")
            except Exception as exc:
                print(f"    ERROR: {exc}")
                print("    Skipping this batch...")

            if i + BATCH_SIZE < len(threads):
                time.sleep(1)

    # --- Translate replies ---
    if replies:
        print(f"\nTranslating {len(replies)} replies...")
        total_batches = (len(replies) + BATCH_SIZE - 1) // BATCH_SIZE

        for i in range(0, len(replies), BATCH_SIZE):
            batch = replies[i : i + BATCH_SIZE]
            batch_num = i // BATCH_SIZE + 1
            print(f"  Batch {batch_num}/{total_batches} ({len(batch)} replies)...")

            api_items = [{"id": r["id"], "body": r["body"]} for r in batch]

            try:
                result = translate_batch(client, api_items, LOCALES)
                updated = update_translations(conn, "Reply", result)
                print(f"    Updated {updated} replies")
            except Exception as exc:
                print(f"    ERROR: {exc}")
                print("    Skipping this batch...")

            if i + BATCH_SIZE < len(replies):
                time.sleep(1)

    conn.close()

    print(f"\n{'=' * 60}")
    print("TRANSLATION COMPLETE")
    print(f"{'=' * 60}")
    print(f"  Threads translated: {len(threads)}")
    print(f"  Replies translated: {len(replies)}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
