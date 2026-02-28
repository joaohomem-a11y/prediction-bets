#!/usr/bin/env python3
"""
Generate ~300 diverse community personas for the Prediction Bets forum.

Uses Claude API to create realistic persona profiles following demographic
distribution rules defined in persona_config.py. Saves output to personas.json.

Usage:
    python generate_personas.py               # Generate all personas
    python generate_personas.py --dry-run     # Preview prompt without calling API
    python generate_personas.py --batch-size 25  # Custom batch size
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
from persona_config import (
    DISTRIBUTION,
    INTERESTS,
    NATIONALITIES,
    PERSONALITY_TRAITS,
    SGT_PEIXOTO,
)


def build_prompt(batch_size: int, batch_number: int, total_batches: int) -> str:
    """Build the Claude prompt for generating a batch of personas."""
    dist = DISTRIBUTION
    return f"""You are generating realistic community member personas for a prediction markets forum called "Prediction Bets".

Generate exactly {batch_size} unique personas as a JSON array. This is batch {batch_number} of {total_batches}.

DEMOGRAPHIC DISTRIBUTION (apply proportionally to this batch):
- Gender: {dist['gender']['male']*100:.0f}% male, {dist['gender']['female']*100:.0f}% female
- Primary language: {dist['language']['en']*100:.0f}% English, {dist['language']['pt']*100:.0f}% Portuguese, {dist['language']['es']*100:.0f}% Spanish, {dist['language']['other']*100:.0f}% other
- Age: {dist['age_range']['min']}-{dist['age_range']['max']} years old, peak between {dist['age_range']['peak_min']}-{dist['age_range']['peak_max']}
- Market knowledge: {', '.join(f'{k} {v*100:.0f}%' for k, v in dist['market_knowledge'].items())}
- Financial levels: {', '.join(dist['financial_level'])}
- Education: {', '.join(dist['education'])}

NATIONALITIES BY LANGUAGE:
{json.dumps(NATIONALITIES, indent=2)}

PERSONALITY TRAITS (pick 2-4 per persona):
{json.dumps(PERSONALITY_TRAITS)}

INTERESTS (pick 2-5 per persona):
{json.dumps(INTERESTS)}

Each persona MUST be a JSON object with these exact fields:
- "id": lowercase slug (e.g., "maria-silva-42") — must be unique
- "name": full realistic name matching nationality
- "username": creative forum username (lowercase, underscores/hyphens allowed)
- "nationality": 2-letter country code from the lists above
- "language": primary language code ("en", "pt", "es", or the actual language for "other" nationalities like "de", "fr", "ja", etc.)
- "gender": "male" or "female"
- "age": integer
- "education": one of {json.dumps(dist['education'])}
- "financial_level": one of {json.dumps(dist['financial_level'])}
- "market_knowledge": one of {json.dumps(list(dist['market_knowledge'].keys()))}
- "personality_traits": array of 2-4 traits
- "interests": array of 2-5 interests
- "writing_style": 1-2 sentence description of how they write forum posts
- "backstory": 2-3 sentence background story explaining how they found prediction markets

IMPORTANT RULES:
- Names MUST be culturally appropriate for the nationality
- Usernames should feel organic (not formulaic) — mix of styles: crypto-inspired, sports-related, meme-ish, professional, etc.
- Writing styles should vary dramatically: some formal, some use slang, some use emojis, some are terse
- Backstories should be diverse and realistic
- Each persona must feel like a real person, not a template
- Vary the combination of traits — avoid repetitive patterns

Return ONLY a valid JSON array. No markdown, no explanation, no code fences."""


def strip_markdown_fences(text: str) -> str:
    """Remove markdown code fences from Claude's response if present."""
    text = text.strip()
    # Remove ```json ... ``` or ``` ... ```
    text = re.sub(r"^```(?:json)?\s*\n?", "", text)
    text = re.sub(r"\n?```\s*$", "", text)
    return text.strip()


def generate_batch(
    client: anthropic.Anthropic,
    batch_size: int,
    batch_number: int,
    total_batches: int,
) -> list[dict]:
    """Generate a single batch of personas via Claude API."""
    prompt = build_prompt(batch_size, batch_number, total_batches)

    print(f"  Calling Claude API (batch {batch_number}/{total_batches}, "
          f"requesting {batch_size} personas)...")

    response = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=16384,
        messages=[{"role": "user", "content": prompt}],
    )

    raw = response.content[0].text
    cleaned = strip_markdown_fences(raw)

    try:
        personas = json.loads(cleaned)
    except json.JSONDecodeError as exc:
        print(f"  WARN: JSON parse failed: {exc}")
        print(f"  Retrying batch {batch_number}...")
        time.sleep(2)

        response = client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=16384,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = response.content[0].text
        cleaned = strip_markdown_fences(raw)
        personas = json.loads(cleaned)  # Let it raise if it fails again

    if not isinstance(personas, list):
        raise ValueError(f"Expected a JSON array, got {type(personas).__name__}")

    print(f"  Got {len(personas)} personas")
    return personas


def deduplicate(personas: list[dict]) -> list[dict]:
    """Remove duplicate personas by id, keeping the first occurrence."""
    seen: set[str] = set()
    unique: list[dict] = []
    for p in personas:
        pid = p.get("id", "")
        if pid not in seen:
            seen.add(pid)
            unique.append(p)
    return unique


def print_summary(personas: list[dict]) -> None:
    """Print distribution summary of the generated personas."""
    total = len(personas)
    print(f"\n{'=' * 60}")
    print("PERSONA GENERATION SUMMARY")
    print(f"{'=' * 60}")
    print(f"  Total personas: {total}")

    # Gender
    genders: dict[str, int] = {}
    for p in personas:
        g = p.get("gender", "unknown")
        genders[g] = genders.get(g, 0) + 1
    print("\n  Gender:")
    for g, count in sorted(genders.items()):
        print(f"    {g}: {count} ({count / total * 100:.1f}%)")

    # Language
    langs: dict[str, int] = {}
    for p in personas:
        lang = p.get("language", "unknown")
        langs[lang] = langs.get(lang, 0) + 1
    print("\n  Language:")
    for lang, count in sorted(langs.items(), key=lambda x: -x[1]):
        print(f"    {lang}: {count} ({count / total * 100:.1f}%)")

    # Market knowledge
    knowledge: dict[str, int] = {}
    for p in personas:
        k = p.get("market_knowledge", "unknown")
        knowledge[k] = knowledge.get(k, 0) + 1
    print("\n  Market Knowledge:")
    for k, count in sorted(knowledge.items()):
        print(f"    {k}: {count} ({count / total * 100:.1f}%)")

    # Nationality (top 10)
    nats: dict[str, int] = {}
    for p in personas:
        n = p.get("nationality", "unknown")
        nats[n] = nats.get(n, 0) + 1
    print("\n  Top 10 Nationalities:")
    for n, count in sorted(nats.items(), key=lambda x: -x[1])[:10]:
        print(f"    {n}: {count} ({count / total * 100:.1f}%)")

    # Age stats
    ages = [p.get("age", 0) for p in personas if isinstance(p.get("age"), int)]
    if ages:
        print(f"\n  Age: min={min(ages)}, max={max(ages)}, "
              f"avg={sum(ages) / len(ages):.1f}")

    print(f"\n{'=' * 60}\n")


def main() -> None:
    """Generate community personas and save to personas.json."""
    parser = argparse.ArgumentParser(
        description="Generate community personas for Prediction Bets"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview prompt without calling the API",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=20,
        help="Personas per API call (default: 20)",
    )
    args = parser.parse_args()

    total = DISTRIBUTION["total"]
    batch_size = args.batch_size
    total_batches = (total + batch_size - 1) // batch_size  # ceiling division

    if args.dry_run:
        print("=" * 60)
        print("DRY RUN — Prompt preview (batch 1)")
        print("=" * 60)
        print(build_prompt(batch_size, 1, total_batches))
        print(f"\n{'=' * 60}")
        print(f"Would generate {total} personas in {total_batches} batches "
              f"of ~{batch_size}")
        print(f"Model: {CLAUDE_MODEL}")
        print(f"Sgt Peixoto will be added as persona #1")
        print(f"Output: agent/personas.json")
        print(f"{'=' * 60}")
        return

    if not ANTHROPIC_API_KEY:
        print("ERROR: ANTHROPIC_API_KEY is not set. Check your .env file.")
        sys.exit(1)

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    # Start with Sgt Peixoto
    all_personas: list[dict] = [SGT_PEIXOTO]
    remaining = total - 1  # Sgt Peixoto counts as one

    print("=" * 60)
    print("PERSONA GENERATION")
    print("=" * 60)
    print(f"  Target: {total} personas")
    print(f"  Batch size: {batch_size}")
    print(f"  Batches needed: {total_batches}")
    print(f"  Model: {CLAUDE_MODEL}")
    print(f"  Persona #1: {SGT_PEIXOTO['name']} (pre-defined)")
    print()

    batch_num = 0
    while remaining > 0:
        batch_num += 1
        current_batch_size = min(batch_size, remaining)
        recalc_total = (total - 1 + batch_size - 1) // batch_size
        try:
            batch = generate_batch(
                client, current_batch_size, batch_num, recalc_total
            )
            all_personas.extend(batch)
            remaining -= len(batch)
            print(f"  Progress: {len(all_personas)}/{total} personas\n")
        except (json.JSONDecodeError, ValueError) as exc:
            print(f"  ERROR: Batch {batch_num} failed permanently: {exc}")
            print("  Continuing with what we have...")
            break

        # Brief pause between batches to avoid rate limits
        if remaining > 0:
            time.sleep(1)

    # Deduplicate
    all_personas = deduplicate(all_personas)
    print(f"After deduplication: {len(all_personas)} unique personas")

    # Save
    output_path = Path(__file__).parent / "personas.json"
    output_path.write_text(json.dumps(all_personas, indent=2, ensure_ascii=False))
    print(f"Saved to {output_path}")

    # Summary
    print_summary(all_personas)


if __name__ == "__main__":
    main()
