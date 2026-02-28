#!/usr/bin/env python3
"""
Seed the database with User records from personas.json.

Usage:
    python seed_users.py              # Seed all personas
    python seed_users.py --dry-run    # Preview without inserting
    python seed_users.py --clear      # Delete all bot/moderator users first
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from db import generate_cuid, get_connection

PERSONAS_PATH = Path(__file__).parent / "personas.json"

DICEBEAR_URL = "https://api.dicebear.com/9.x/notionists/svg?seed={username}"


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


def clear_bot_users(conn) -> int:
    """Delete all users with role 'bot' or 'moderator'. Returns count deleted."""
    with conn.cursor() as cur:
        cur.execute(
            """DELETE FROM "User" WHERE role IN ('bot', 'moderator')"""
        )
        count = cur.rowcount
    conn.commit()
    return count


def get_existing_emails(conn) -> set[str]:
    """Return a set of all existing email addresses in the User table."""
    with conn.cursor() as cur:
        cur.execute("""SELECT email FROM "User" """)
        return {row[0] for row in cur.fetchall()}


def build_user_record(persona: dict) -> dict:
    """Build a User row dict from a persona object."""
    username = persona.get("username", persona["id"])
    email = f"{username}@bot.predictionbets.club"
    role = "moderator" if persona.get("role") == "moderator" else "bot"
    now = datetime.now(timezone.utc)

    return {
        "id": generate_cuid(),
        "name": persona["name"],
        "email": email,
        "image": DICEBEAR_URL.format(username=username),
        "role": role,
        "createdAt": now,
        "updatedAt": now,
    }


def insert_users(conn, records: list[dict]) -> int:
    """Insert user records into the User table. Returns count inserted."""
    if not records:
        return 0

    with conn.cursor() as cur:
        for rec in records:
            cur.execute(
                """
                INSERT INTO "User" (id, name, email, image, role, "createdAt", "updatedAt")
                VALUES (%(id)s, %(name)s, %(email)s, %(image)s, %(role)s, %(createdAt)s, %(updatedAt)s)
                """,
                rec,
            )
    conn.commit()
    return len(records)


def main() -> None:
    """Seed User records from personas.json into the database."""
    parser = argparse.ArgumentParser(
        description="Seed User records from personas.json"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview without inserting into the database",
    )
    parser.add_argument(
        "--clear",
        action="store_true",
        help="Delete existing bot/moderator users before inserting",
    )
    args = parser.parse_args()

    personas = load_personas()
    print(f"Loaded {len(personas)} personas from {PERSONAS_PATH.name}")

    if args.dry_run:
        print(f"\n{'=' * 60}")
        print("DRY RUN -- Preview only, no database changes")
        print(f"{'=' * 60}\n")

        for p in personas:
            username = p.get("username", p["id"])
            email = f"{username}@bot.predictionbets.club"
            role = "moderator" if p.get("role") == "moderator" else "bot"
            print(f"  {p['name']:30s}  {email:45s}  role={role}")

        print(f"\nWould insert up to {len(personas)} users (minus any existing).")
        return

    # Real run -- connect to database
    conn = get_connection()
    print("Connected to database.")

    try:
        # Optionally clear existing bot/moderator users
        if args.clear:
            deleted = clear_bot_users(conn)
            print(f"Cleared {deleted} existing bot/moderator users.")

        # Get existing emails for dedup
        existing_emails = get_existing_emails(conn)

        # Build records, skipping duplicates
        records: list[dict] = []
        skipped = 0
        id_map: dict[str, str] = {}  # persona_id -> db_user_id

        for p in personas:
            user_rec = build_user_record(p)

            if user_rec["email"] in existing_emails:
                skipped += 1
                # Try to find the existing user ID for the mapping
                continue

            records.append(user_rec)
            id_map[p["id"]] = user_rec["id"]

        # Insert
        inserted = insert_users(conn, records)

        # Also fetch IDs for personas that were skipped (already existed)
        if skipped > 0:
            with conn.cursor() as cur:
                for p in personas:
                    if p["id"] not in id_map:
                        username = p.get("username", p["id"])
                        email = f"{username}@bot.predictionbets.club"
                        cur.execute(
                            """SELECT id FROM "User" WHERE email = %s""",
                            (email,),
                        )
                        row = cur.fetchone()
                        if row:
                            id_map[p["id"]] = row[0]

        # Write back _db_user_id into personas.json
        updated_count = 0
        for p in personas:
            db_id = id_map.get(p["id"])
            if db_id:
                p["_db_user_id"] = db_id
                updated_count += 1

        PERSONAS_PATH.write_text(
            json.dumps(personas, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

        # Summary
        print(f"\n{'=' * 60}")
        print("SEED USERS SUMMARY")
        print(f"{'=' * 60}")
        print(f"  Total personas:    {len(personas)}")
        print(f"  Inserted:          {inserted}")
        print(f"  Skipped (exists):  {skipped}")
        print(f"  IDs written back:  {updated_count}")
        print(f"  personas.json updated with _db_user_id fields")
        print(f"{'=' * 60}\n")

    finally:
        conn.close()


if __name__ == "__main__":
    main()
