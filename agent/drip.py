#!/usr/bin/env python3
"""
Daily drip of new forum conversations.

Generates 5-10 new threads with replies per day to keep the
community feeling alive. Designed to run as a cron job.

Usage:
    python drip.py              # Generate 5-10 new threads
    python drip.py --count 3    # Custom count
    python drip.py --dry-run    # Preview only
"""

from __future__ import annotations

import argparse
import random
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import anthropic

from config import ANTHROPIC_API_KEY, CLAUDE_MODEL
from db import get_connection
from persona_config import FORUM_SECTIONS, SGT_PEIXOTO
from seed_conversations import (
    TOPIC_SEEDS,
    generate_conversation,
    insert_conversation,
    load_personas,
    personas_with_db_id,
    find_sgt_persona,
    pick_participants,
)

PERSONAS_FILE = Path(__file__).parent / "personas.json"


# ---------------------------------------------------------------------------
# Fresh trending topics via Claude
# ---------------------------------------------------------------------------


def get_fresh_topics(client: anthropic.Anthropic) -> list[str]:
    """Ask Claude for 6 current trending prediction market topics."""
    prompt = """List 6 current trending topics in prediction markets as of today.
One topic per line. Be specific and timely.
Focus on: elections, crypto, AI, geopolitics, economics, sports.
Return ONLY the 6 topics, one per line, no numbering or bullets."""

    try:
        message = client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=500,
            messages=[{"role": "user", "content": prompt}],
        )
        topics = [
            line.strip()
            for line in message.content[0].text.strip().split("\n")
            if line.strip()
        ]
        return topics if topics else []
    except Exception as e:
        print(f"  WARN: Could not get fresh topics: {e}")
        return []


# ---------------------------------------------------------------------------
# Topic selection helpers
# ---------------------------------------------------------------------------


def pick_topic(fresh_topics: list[str], section: str) -> str:
    """50% chance of a fresh topic, 50% an evergreen TOPIC_SEED."""
    evergreen = TOPIC_SEEDS.get(section, [])

    use_fresh = random.random() < 0.5 and fresh_topics
    if use_fresh:
        return random.choice(fresh_topics)

    if evergreen:
        return random.choice(evergreen)

    # Fallback: if somehow no topics at all
    if fresh_topics:
        return random.choice(fresh_topics)
    return "General prediction market discussion"


# ---------------------------------------------------------------------------
# Dry-run preview
# ---------------------------------------------------------------------------


def preview_drip(
    count: int,
    personas: list[dict],
    sgt: dict | None,
    fresh_topics: list[str],
) -> None:
    """Print a preview of what would be generated without API calls."""
    print(f"\n{'=' * 60}")
    print("DRY RUN -- Preview only, no API calls or database changes")
    print(f"{'=' * 60}\n")
    print(f"  Threads to generate: {count}")
    print(f"  Available personas:  {len(personas)}")
    print(f"  Sgt Peixoto:         {'present' if sgt else 'NOT FOUND'}")
    print(f"  Fresh topics:        {len(fresh_topics)}")
    if fresh_topics:
        for t in fresh_topics:
            print(f"    - {t}")
    print()

    sections = [s for s in FORUM_SECTIONS if s in TOPIC_SEEDS]

    for i in range(count):
        section = random.choice(sections)
        topic = pick_topic(fresh_topics, section)
        participants = pick_participants(personas, sgt, section)
        names = [p.get("username", p["id"]) for p in participants]
        has_sgt = any(
            p.get("id") == SGT_PEIXOTO["id"] or p.get("username") == SGT_PEIXOTO["username"]
            for p in participants
        )
        sgt_marker = " [+SGT]" if has_sgt else ""
        base_time = datetime.now(timezone.utc) - timedelta(
            hours=random.randint(0, 4)
        )
        print(
            f"  Thread #{i + 1}: [{section}] \"{topic[:55]}...\""
            f"{sgt_marker} ({len(participants)} users)"
        )
        print(
            f"         base_time: {base_time.strftime('%Y-%m-%d %H:%M UTC')}"
        )
        print(
            f"         participants: "
            f"{', '.join(names[:5])}{'...' if len(names) > 5 else ''}"
        )
        print()

    print(f"Would generate {count} threads via Claude API.\n")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    """Generate daily drip of forum conversations."""
    parser = argparse.ArgumentParser(
        description="Daily drip of forum conversations using Claude API"
    )
    parser.add_argument(
        "--count",
        type=int,
        default=None,
        help="Number of threads to generate (default: random 5-10)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview plan without API calls or DB writes",
    )
    args = parser.parse_args()

    # Determine thread count
    thread_count = args.count if args.count is not None else random.randint(5, 10)
    if thread_count < 1:
        print("ERROR: --count must be >= 1")
        sys.exit(1)

    # Load personas
    personas = load_personas()
    valid_personas = personas_with_db_id(personas)
    sgt = find_sgt_persona(valid_personas)

    if not valid_personas:
        print("ERROR: No personas with _db_user_id found.")
        print("Run seed_users.py first to insert users and get DB IDs.")
        sys.exit(1)

    print(
        f"Loaded {len(valid_personas)} personas with DB IDs "
        f"(of {len(personas)} total)"
    )
    if sgt:
        print(
            f"Sgt Peixoto found: {sgt.get('username')} "
            f"(DB ID: {sgt.get('_db_user_id', 'N/A')})"
        )
    else:
        print("WARNING: Sgt Peixoto not found among personas with DB IDs.")

    # Build username -> user_id mapping
    username_to_user_id: dict[str, str] = {}
    for p in valid_personas:
        uname = p.get("username", p["id"])
        username_to_user_id[uname] = p["_db_user_id"]

    # ---- Get fresh topics ----
    # For dry-run we still show fresh topics (needs API key)
    fresh_topics: list[str] = []
    if ANTHROPIC_API_KEY:
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        print("Fetching fresh trending topics from Claude...")
        fresh_topics = get_fresh_topics(client)
        if fresh_topics:
            print(f"  Got {len(fresh_topics)} fresh topics.")
        else:
            print("  No fresh topics returned, will use evergreen seeds only.")
    else:
        if not args.dry_run:
            print("ERROR: ANTHROPIC_API_KEY not set in .env")
            sys.exit(1)
        print("WARN: No API key, skipping fresh topics in dry-run.")
        client = None  # type: ignore[assignment]

    # ---- Dry run ----
    if args.dry_run:
        preview_drip(thread_count, valid_personas, sgt, fresh_topics)
        return

    # ---- Real run ----
    conn = get_connection()
    print(f"Connected to database.\n")
    print(f"Generating {thread_count} drip threads...\n")

    sections = [s for s in FORUM_SECTIONS if s in TOPIC_SEEDS]
    total_generated = 0
    total_failed = 0

    try:
        for i in range(thread_count):
            section = random.choice(sections)
            topic = pick_topic(fresh_topics, section)
            participants = pick_participants(valid_personas, sgt, section)

            has_sgt = any(
                p.get("id") == SGT_PEIXOTO["id"]
                or p.get("username") == SGT_PEIXOTO["username"]
                for p in participants
            )
            sgt_tag = " [+SGT]" if has_sgt else ""

            # Recent base_time: 0-4 hours ago
            base_time = datetime.now(timezone.utc) - timedelta(
                hours=random.randint(0, 4)
            )

            print(
                f"  Thread {i + 1}/{thread_count}: [{section}] "
                f"\"{topic[:45]}...\"{sgt_tag} "
                f"({len(participants)} participants)"
            )

            conversation = generate_conversation(
                client, section, topic, participants
            )

            if conversation is None:
                total_failed += 1
                print("    -> FAILED (generation)")
                continue

            reply_count = len(conversation.get("replies", []))
            ok = insert_conversation(
                conn,
                conversation,
                section,
                username_to_user_id,
                base_time=base_time,
            )

            if ok:
                total_generated += 1
                print(f"    -> OK ({reply_count} replies)")
            else:
                total_failed += 1
                print("    -> FAILED (insertion)")

            # Small delay to avoid API rate-limits
            time.sleep(0.5)

    except KeyboardInterrupt:
        print("\n\nInterrupted by user.")
    finally:
        conn.close()

    # Summary
    print(f"\n{'=' * 60}")
    print("DAILY DRIP SUMMARY")
    print(f"{'=' * 60}")
    print(f"  Threads generated: {total_generated}")
    print(f"  Threads failed:    {total_failed}")
    print(f"  Total attempted:   {total_generated + total_failed}")
    print(f"{'=' * 60}\n")


if __name__ == "__main__":
    main()
