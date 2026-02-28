#!/usr/bin/env python3
"""
Seed the database with realistic multilingual forum conversations.

Uses Claude API to generate complete threads (title + body + replies) based on
predefined topic seeds per forum section.  Each character posts in their native
language (en / pt / es) and Sgt Peixoto appears in ~35 % of threads, replying
in the language of the person he addresses.

Usage:
    python seed_conversations.py                    # Generate ~150 threads
    python seed_conversations.py --threads 50       # Custom count
    python seed_conversations.py --dry-run          # Preview without inserting
"""

from __future__ import annotations

import argparse
import json
import random
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import anthropic

from config import ANTHROPIC_API_KEY, CLAUDE_MODEL
from db import generate_cuid, get_connection
from persona_config import FORUM_SECTIONS, SGT_PEIXOTO

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

PERSONAS_PATH = Path(__file__).parent / "personas.json"

# ---------------------------------------------------------------------------
# Topic seeds — predefined ideas per forum section
# ---------------------------------------------------------------------------

TOPIC_SEEDS: dict[str, list[str]] = {
    "signal-drop": [
        "Polymarket shows 70% chance of Fed rate cut before September",
        "New Kalshi markets on AI regulation — early movers have edge",
        "Election prediction markets diverging from polls again",
        "Crypto prediction markets seeing record volume this week",
        "European prediction market platforms gaining traction",
        "Sports betting data now feeding into prediction algorithms",
    ],
    "contrarian-takes": [
        "Prediction markets are LESS accurate than people think",
        "The wisdom of crowds fails when crowds are biased",
        "Small prediction markets are more accurate than large ones",
        "Political prediction markets should be regulated like financial markets",
        "AI will make human prediction markets obsolete within 5 years",
        "Most prediction market gurus are just lucky",
    ],
    "prediction-battles": [
        "Will Bitcoin hit 200K by end of 2026?",
        "Will there be a major geopolitical conflict in 2026?",
        "Will AI replace 50% of customer service jobs by 2028?",
        "Will a third-party candidate get over 10% in next US election?",
        "Will Polymarket reach 1B daily volume this year?",
        "Will the next pandemic prediction market trigger before 2028?",
    ],
    "reality-check": [
        "Remember when everyone said the housing market would crash in 2025?",
        "Markets predicted the election outcome 6 months before pundits caught on",
        "The prediction market that correctly called the tech layoffs wave",
        "When I ignored the market signal and lost big — my lesson learned",
        "Prediction markets called the inflation peak before any economist",
        "My worst prediction market loss and what it taught me",
    ],
    "edge-lab": [
        "My framework for identifying mispriced prediction markets",
        "Using sentiment analysis to find edge in political markets",
        "The Kelly criterion applied to prediction market sizing",
        "How I automated my prediction market research pipeline",
        "Correlation analysis between prediction markets and traditional indicators",
        "Backtesting prediction market strategies: what works and what doesnt",
    ],
    "off-market": [
        "What got you into prediction markets? Share your origin story",
        "Best prediction market memes of the month",
        "If prediction markets existed 100 years ago...",
        "The psychology of betting against the consensus",
        "How do you explain prediction markets to friends and family?",
        "Book recommendations for probabilistic thinking",
    ],
}

# ---------------------------------------------------------------------------
# Helpers — persona loading
# ---------------------------------------------------------------------------


def load_personas() -> list[dict]:
    """Load personas from personas.json."""
    if not PERSONAS_PATH.exists():
        print(f"ERROR: {PERSONAS_PATH} not found.")
        print("Run generate_personas.py first to create it.")
        sys.exit(1)

    data = json.loads(PERSONAS_PATH.read_text(encoding="utf-8"))
    if not isinstance(data, list) or len(data) == 0:
        print("ERROR: personas.json is empty or not a JSON array.")
        sys.exit(1)

    return data


def personas_with_db_id(personas: list[dict]) -> list[dict]:
    """Return only personas that have a _db_user_id (i.e. already seeded)."""
    return [p for p in personas if p.get("_db_user_id")]


def find_sgt_persona(personas: list[dict]) -> dict | None:
    """Find Sgt Peixoto among the personas list."""
    for p in personas:
        if p.get("id") == SGT_PEIXOTO["id"] or p.get("username") == SGT_PEIXOTO["username"]:
            return p
    return None


# ---------------------------------------------------------------------------
# Helpers — pick participants for a thread
# ---------------------------------------------------------------------------


def pick_participants(
    personas: list[dict],
    sgt: dict | None,
    section: str,
) -> list[dict]:
    """Select 3-7 random participants for a conversation.

    Sgt Peixoto has a ~35 % chance of joining.
    """
    pool = [p for p in personas if p.get("id") != SGT_PEIXOTO["id"]]
    count = random.randint(3, 7)
    selected = random.sample(pool, min(count, len(pool)))

    # ~35 % chance of adding Sgt Peixoto
    if sgt and random.random() < 0.35:
        selected.append(sgt)

    return selected


# ---------------------------------------------------------------------------
# Claude prompt construction
# ---------------------------------------------------------------------------


def build_prompt(section: str, topic: str, participants: list[dict]) -> str:
    """Build the Claude prompt for generating a conversation."""
    has_sgt = any(
        p.get("id") == SGT_PEIXOTO["id"] or p.get("username") == SGT_PEIXOTO["username"]
        for p in participants
    )

    participant_lines: list[str] = []
    for p in participants:
        if p.get("id") == SGT_PEIXOTO["id"] or p.get("username") == SGT_PEIXOTO["username"]:
            continue  # Described separately in the SPECIAL block
        traits = ", ".join(p.get("personality_traits", []))
        participant_lines.append(
            f"- {p['name']} (username: {p.get('username', p['id'])}, "
            f"language: {p.get('language', 'en')}, "
            f"knowledge: {p.get('market_knowledge', 'intermediate')}, "
            f"style: {p.get('writing_style', 'casual')}, "
            f"traits: {traits})"
        )

    participants_block = "\n".join(participant_lines)

    sgt_block = ""
    if has_sgt:
        sgt_block = (
            "\n\nSPECIAL: Sargento Peixoto (username: sgt_peixoto, moderator) is "
            "participating. He responds in the SAME language as the person he's "
            "replying to (PT, EN, or ES). Moderates if debate gets heated. "
            "Educates beginners. Uses occasional military metaphors."
        )

    prompt = f"""Generate a realistic forum conversation for a prediction market community.

SECTION: {section}
TOPIC SEED: {topic}

PARTICIPANTS:
{participants_block}{sgt_block}

RULES:
1. Each person writes in their NATIVE language
2. Respect knowledge level — beginners ask simple questions, gurus give deep analysis
3. Match writing_style and personality_traits exactly
4. Include natural disagreements but keep respectful
5. Generate 4-12 replies
6. Some replies can be responses TO other replies (nested)
7. The thread author must be one of the participants listed above

OUTPUT: JSON only, no markdown fences:
{{
  "thread": {{"title": "...", "body": "...", "author_username": "..."}},
  "replies": [
    {{"body": "...", "author_username": "...", "parent_index": null}},
    {{"body": "...", "author_username": "...", "parent_index": 0}}
  ]
}}"""
    return prompt


# ---------------------------------------------------------------------------
# Claude API call
# ---------------------------------------------------------------------------


def generate_conversation(
    client: anthropic.Anthropic,
    section: str,
    topic: str,
    participants: list[dict],
) -> dict | None:
    """Call Claude to produce a thread + replies as JSON.

    Returns the parsed dict or None on failure.
    """
    prompt = build_prompt(section, topic, participants)

    try:
        response = client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}],
        )

        raw = response.content[0].text.strip()

        # Strip markdown fences if Claude added them anyway
        if raw.startswith("```"):
            first_nl = raw.index("\n")
            raw = raw[first_nl + 1 :]
        if raw.endswith("```"):
            raw = raw[: raw.rfind("```")]

        raw = raw.strip()
        data = json.loads(raw)

        # Basic validation
        if "thread" not in data or "replies" not in data:
            print("    WARN: Claude response missing thread or replies key.")
            return None

        return data

    except json.JSONDecodeError as exc:
        print(f"    WARN: Failed to parse JSON from Claude: {exc}")
        return None
    except anthropic.APIError as exc:
        print(f"    WARN: Claude API error: {exc}")
        return None
    except Exception as exc:  # noqa: BLE001
        print(f"    WARN: Unexpected error during generation: {exc}")
        return None


# ---------------------------------------------------------------------------
# Database insertion
# ---------------------------------------------------------------------------


def random_backdate() -> datetime:
    """Return a datetime between 7 and 180 days ago."""
    days_ago = random.randint(7, 180)
    hours_offset = random.randint(0, 23)
    minutes_offset = random.randint(0, 59)
    return datetime.now(timezone.utc) - timedelta(
        days=days_ago, hours=hours_offset, minutes=minutes_offset
    )


def insert_conversation(
    conn,
    conversation: dict,
    section: str,
    username_to_user_id: dict[str, str],
    base_time: datetime | None = None,
) -> bool:
    """Insert a generated conversation (thread + replies) into the DB.

    If *base_time* is provided it is used as the thread creation time;
    otherwise a random back-dated time is generated via ``random_backdate()``.

    Returns True on success, False on skip/error.
    """
    thread_data = conversation["thread"]
    replies_data = conversation.get("replies", [])

    # Resolve thread author
    author_username = thread_data.get("author_username", "")
    author_id = username_to_user_id.get(author_username)
    if not author_id:
        print(f"    WARN: Unknown thread author '{author_username}', skipping.")
        return False

    thread_id = generate_cuid()
    thread_created = base_time if base_time is not None else random_backdate()
    thread_upvotes = random.randint(3, 80)
    thread_downvotes = random.randint(0, 10)

    try:
        with conn.cursor() as cur:
            # Insert thread
            cur.execute(
                """
                INSERT INTO "Thread" (id, title, body, section, "isPinned",
                                      upvotes, downvotes, "createdAt", "updatedAt",
                                      "authorId")
                VALUES (%(id)s, %(title)s, %(body)s, %(section)s, %(isPinned)s,
                        %(upvotes)s, %(downvotes)s, %(createdAt)s, %(updatedAt)s,
                        %(authorId)s)
                """,
                {
                    "id": thread_id,
                    "title": thread_data["title"],
                    "body": thread_data["body"],
                    "section": section,
                    "isPinned": False,
                    "upvotes": thread_upvotes,
                    "downvotes": thread_downvotes,
                    "createdAt": thread_created,
                    "updatedAt": thread_created,
                    "authorId": author_id,
                },
            )

            # Insert replies sequentially, tracking IDs for nested refs
            reply_ids: list[str] = []
            reply_time = thread_created

            for reply in replies_data:
                reply_username = reply.get("author_username", "")
                reply_author_id = username_to_user_id.get(reply_username)
                if not reply_author_id:
                    print(
                        f"    WARN: Unknown reply author '{reply_username}', "
                        "skipping this reply."
                    )
                    reply_ids.append("")
                    continue

                reply_id = generate_cuid()
                offset_minutes = random.randint(5, 120)
                reply_time = reply_time + timedelta(minutes=offset_minutes)
                reply_upvotes = random.randint(0, 40)
                reply_downvotes = random.randint(0, 5)

                # Resolve parent reply
                parent_index = reply.get("parent_index")
                parent_reply_id = None
                if parent_index is not None and isinstance(parent_index, int):
                    if 0 <= parent_index < len(reply_ids) and reply_ids[parent_index]:
                        parent_reply_id = reply_ids[parent_index]

                cur.execute(
                    """
                    INSERT INTO "Reply" (id, body, upvotes, downvotes,
                                         "createdAt", "updatedAt",
                                         "authorId", "threadId", "parentReplyId")
                    VALUES (%(id)s, %(body)s, %(upvotes)s, %(downvotes)s,
                            %(createdAt)s, %(updatedAt)s,
                            %(authorId)s, %(threadId)s, %(parentReplyId)s)
                    """,
                    {
                        "id": reply_id,
                        "body": reply["body"],
                        "upvotes": reply_upvotes,
                        "downvotes": reply_downvotes,
                        "createdAt": reply_time,
                        "updatedAt": reply_time,
                        "authorId": reply_author_id,
                        "threadId": thread_id,
                        "parentReplyId": parent_reply_id,
                    },
                )
                reply_ids.append(reply_id)

        conn.commit()
        return True

    except Exception as exc:  # noqa: BLE001
        conn.rollback()
        print(f"    ERROR: Database insert failed: {exc}")
        return False


# ---------------------------------------------------------------------------
# Dry-run preview
# ---------------------------------------------------------------------------


def preview_plan(
    sections: list[str],
    threads_per_section: int,
    personas: list[dict],
    sgt: dict | None,
) -> None:
    """Print a preview of what would be generated without making API calls."""
    total = len(sections) * threads_per_section
    print(f"\n{'=' * 60}")
    print("DRY RUN -- Preview only, no API calls or database changes")
    print(f"{'=' * 60}\n")
    print(f"  Sections:           {len(sections)}")
    print(f"  Threads per section: {threads_per_section}")
    print(f"  Total threads:       {total}")
    print(f"  Available personas:  {len(personas)}")
    print(f"  Sgt Peixoto:         {'present' if sgt else 'NOT FOUND'}")
    print()

    for section in sections:
        topics = TOPIC_SEEDS.get(section, [])
        print(f"  [{section}]")
        for i in range(threads_per_section):
            topic = topics[i % len(topics)] if topics else "free-form"
            participants = pick_participants(personas, sgt, section)
            names = [p.get("username", p["id"]) for p in participants]
            has_sgt = any(
                p.get("id") == SGT_PEIXOTO["id"]
                for p in participants
            )
            sgt_marker = " [+SGT]" if has_sgt else ""
            print(f"    #{i + 1}: \"{topic[:50]}...\" -> {len(participants)} users{sgt_marker}")
            print(f"         participants: {', '.join(names[:5])}{'...' if len(names) > 5 else ''}")
        print()

    print(f"Would generate {total} threads via Claude API.\n")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    """Generate and seed forum conversations."""
    parser = argparse.ArgumentParser(
        description="Seed forum conversations using Claude API"
    )
    parser.add_argument(
        "--threads",
        type=int,
        default=150,
        help="Total number of threads to generate (default: 150)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview plan without API calls or DB writes",
    )
    args = parser.parse_args()

    # Load personas
    personas = load_personas()
    valid_personas = personas_with_db_id(personas)
    sgt = find_sgt_persona(valid_personas)

    if not valid_personas:
        print("ERROR: No personas with _db_user_id found.")
        print("Run seed_users.py first to insert users and get DB IDs.")
        sys.exit(1)

    print(f"Loaded {len(valid_personas)} personas with DB IDs "
          f"(of {len(personas)} total)")
    if sgt:
        print(f"Sgt Peixoto found: {sgt.get('username')} "
              f"(DB ID: {sgt.get('_db_user_id', 'N/A')})")
    else:
        print("WARNING: Sgt Peixoto not found among personas with DB IDs.")

    # Build username -> user_id mapping
    username_to_user_id: dict[str, str] = {}
    for p in valid_personas:
        uname = p.get("username", p["id"])
        username_to_user_id[uname] = p["_db_user_id"]

    # Distribute threads across sections
    sections = [s for s in FORUM_SECTIONS if s in TOPIC_SEEDS]
    threads_per_section = max(1, args.threads // len(sections))
    remainder = args.threads - (threads_per_section * len(sections))

    if args.dry_run:
        preview_plan(sections, threads_per_section, valid_personas, sgt)
        return

    # ---- Real run ----
    if not ANTHROPIC_API_KEY:
        print("ERROR: ANTHROPIC_API_KEY not set in .env")
        sys.exit(1)

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    conn = get_connection()
    print("Connected to database.\n")

    total_generated = 0
    total_failed = 0

    try:
        for sec_idx, section in enumerate(sections):
            topics = TOPIC_SEEDS.get(section, [])
            count_for_section = threads_per_section + (1 if sec_idx < remainder else 0)

            print(f"[{section}] Generating {count_for_section} threads...")

            for i in range(count_for_section):
                topic = topics[i % len(topics)] if topics else "free-form discussion"
                participants = pick_participants(valid_personas, sgt, section)

                has_sgt = any(
                    p.get("id") == SGT_PEIXOTO["id"]
                    for p in participants
                )
                sgt_tag = " [+SGT]" if has_sgt else ""

                print(
                    f"  Thread {i + 1}/{count_for_section}: "
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
                    conn, conversation, section, username_to_user_id
                )

                if ok:
                    total_generated += 1
                    print(f"    -> OK ({reply_count} replies)")
                else:
                    total_failed += 1
                    print("    -> FAILED (insertion)")

                # Small delay to avoid API rate-limits
                time.sleep(0.5)

            print()

    except KeyboardInterrupt:
        print("\n\nInterrupted by user.")
    finally:
        conn.close()

    # Summary
    print(f"{'=' * 60}")
    print("SEED CONVERSATIONS SUMMARY")
    print(f"{'=' * 60}")
    print(f"  Threads generated: {total_generated}")
    print(f"  Threads failed:    {total_failed}")
    print(f"  Total attempted:   {total_generated + total_failed}")
    print(f"{'=' * 60}\n")


if __name__ == "__main__":
    main()
