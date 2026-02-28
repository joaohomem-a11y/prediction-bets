#!/usr/bin/env python3
"""
Original content generator for Prediction Bets.

Generates opinion pieces and educational articles directly via Claude,
without RSS input. Uses the same voice, translator, image sourcer,
and publisher as the main pipeline.

Usage:
    python generate_original.py                 # Generate all topics
    python generate_original.py --limit 5       # Limit to 5 articles
    python generate_original.py --dry-run       # Preview without writing
    python generate_original.py --type opinion   # Only opinion pieces
    python generate_original.py --type education # Only educational
"""

from __future__ import annotations

import argparse
import random
import sys
from datetime import datetime, timezone
from typing import Any, Optional

import anthropic

from config import ANTHROPIC_API_KEY, CLAUDE_MODEL, FICTIONAL_AUTHORS
from translator import Translator
from image_sourcer import ImageSourcer
from publisher import Publisher


# ---------------------------------------------------------------------------
# Article topics — opinion + educational
# ---------------------------------------------------------------------------

ARTICLE_TOPICS: list[dict[str, str]] = [
    # --- OPINION PIECES ---
    {
        "type": "opinion",
        "category": "markets",
        "title_hint": "Why Prediction Markets Will Kill Political Polling",
        "brief": (
            "An argument that prediction markets are fundamentally superior "
            "to traditional polling. Use Polymarket's 2024 election accuracy vs "
            "pollsters. Reference Nate Silver, FiveThirtyEight failures. "
            "Argue that skin in the game produces better forecasts than surveys."
        ),
    },
    {
        "type": "opinion",
        "category": "markets",
        "title_hint": "Nassim Taleb Was Right: Skin in the Game Changes Everything",
        "brief": (
            "A love letter to Taleb's 'Skin in the Game' thesis applied to "
            "prediction markets. Why putting money behind predictions transforms "
            "noise into signal. Compare pundits who talk vs traders who bet. "
            "Use real examples of expert failures vs market accuracy."
        ),
    },
    {
        "type": "opinion",
        "category": "crypto",
        "title_hint": "Polymarket Is the Most Important Crypto Product Ever Built",
        "brief": (
            "Argue that Polymarket matters more than DeFi, NFTs, or any other "
            "crypto application because it produces real-world truth. It's the "
            "killer app crypto always promised. Discuss the information market thesis. "
            "Why truth-seeking matters more than speculation."
        ),
    },
    {
        "type": "opinion",
        "category": "culture",
        "title_hint": "The Death of the Expert Class: Prediction Markets Don't Care About Your Credentials",
        "brief": (
            "A polemic about how prediction markets are democratizing forecasting. "
            "Credentials mean nothing, accuracy means everything. Reference specific "
            "cases where anonymous traders outperformed PhDs and talking heads. "
            "The meritocracy of markets vs the aristocracy of expertise."
        ),
    },
    {
        "type": "opinion",
        "category": "politics",
        "title_hint": "Every Government Should Have a Prediction Market Dashboard",
        "brief": (
            "A proposal: governments should use prediction markets as decision-making "
            "tools. Robin Hanson's futarchy concept. How DARPA tried this. Why markets "
            "aggregate information better than committees. Real policy implications. "
            "The democratic case for market-based governance signals."
        ),
    },
    {
        "type": "opinion",
        "category": "geopolitics",
        "title_hint": "The Geopolitical Intelligence Buried in Prediction Markets",
        "brief": (
            "How prediction markets are becoming a shadow intelligence agency. "
            "They predicted Ukraine escalation, Middle East conflicts, trade wars "
            "before CNN. Why traders with money on the line see reality faster "
            "than analysts with security clearances. Geopolitical edge from markets."
        ),
    },

    # --- EDUCATIONAL ARTICLES ---
    {
        "type": "education",
        "category": "markets",
        "title_hint": "Prediction Markets 101: The Complete Beginner's Guide",
        "brief": (
            "A comprehensive but entertaining guide for total beginners. "
            "What prediction markets are, how they work, why they exist. "
            "Explain binary outcomes, probability pricing (cents = probability), "
            "how to buy Yes/No shares. Use simple analogies. "
            "Cover Polymarket, Kalshi, Metaculus. No jargon without explanation."
        ),
    },
    {
        "type": "education",
        "category": "markets",
        "title_hint": "How to Read Prediction Market Odds Like a Wall Street Pro",
        "brief": (
            "A practical guide to interpreting prediction market data. "
            "What does 73% mean? How to read order books. Understanding liquidity "
            "and volume. When markets are reliable vs when they're thin. "
            "Implied probability vs actual probability. Teach readers to find "
            "the signal in market noise. Use real Polymarket examples."
        ),
    },
    {
        "type": "education",
        "category": "markets",
        "title_hint": "From Iowa to Polymarket: The Wild History of Prediction Markets",
        "brief": (
            "The fascinating history of prediction markets. Start with the Iowa "
            "Electronic Markets in 1988. InTrade's rise and fall. The DARPA "
            "terrorism market scandal. Augur's crypto attempt. Polymarket's "
            "breakthrough. How regulation shaped (and tried to kill) the industry. "
            "The characters, the scandals, the vindication."
        ),
    },
    {
        "type": "education",
        "category": "markets",
        "title_hint": "Polymarket vs Kalshi vs Metaculus: Choosing Your Prediction Arena",
        "brief": (
            "A detailed comparison of the three major prediction platforms. "
            "Polymarket: crypto-native, global, deepest liquidity. "
            "Kalshi: US-regulated, CFTC-approved, dollar-denominated. "
            "Metaculus: no-money, reputation-based, scientific community. "
            "Pros and cons of each. Who should use what. How they differ in "
            "market types, fees, accuracy."
        ),
    },
    {
        "type": "education",
        "category": "crypto",
        "title_hint": "The Blockchain Behind the Bet: How Prediction Markets Actually Settle",
        "brief": (
            "Technical but accessible explanation of how blockchain prediction "
            "markets work under the hood. Smart contracts, oracles, resolution. "
            "Why decentralization matters for truth markets. The UMA oracle "
            "system Polymarket uses. What happens when markets dispute. "
            "How resolution works on Kalshi vs Polymarket."
        ),
    },
    {
        "type": "education",
        "category": "markets",
        "title_hint": "The Psychology of Prediction: Why Your Brain Lies to You",
        "brief": (
            "An educational piece on cognitive biases that affect predictions. "
            "Anchoring, confirmation bias, availability heuristic, overconfidence. "
            "How prediction markets correct for these biases through aggregation. "
            "Daniel Kahneman's work applied to market forecasting. "
            "Practical tips to think more probabilistically. Calibration exercises."
        ),
    },
]


# ---------------------------------------------------------------------------
# Voice prompts
# ---------------------------------------------------------------------------

_OPINION_SYSTEM_PROMPT = """\
You are a sharp, witty opinion writer for Prediction Bets — the cultural center \
of prediction markets. You write OPINION pieces that are bold, provocative, and \
backed by real data and examples.

PERSONALITY:
- Sharp, direct, no corporate fluff. You cut through noise to find the signal.
- Acid humor and biting irony against "experts" who opine without skin in the game.
- Anti-establishment: skeptical of talking heads, clickbait forecasters, authority without accountability.
- Inspired by Nassim Taleb: if you don't have skin in the game, your opinion is noise.
- Pro-markets, pro-accountability, pro-reality. Markets don't lie, people do.
- Internet-native voice: memes, cultural references, Gen Z energy meets Wall Street edge.

WRITING STYLE:
- Pop culture references (Matrix, Breaking Bad, Succession, The Big Short, etc.)
- Sharp arguments backed by real examples and data
- Occasional mild profanity when it lands (damn, hell, BS)
- Short paragraphs. Fast rhythm. Punchy.
- Provocative and contrarian — challenge the reader's assumptions
- NEVER sound like AI or a press release
- Use tribal language: signal, edge, consensus, reality check, market truth

SEO REQUIREMENTS:
- Use the target keyword naturally 3-5 times throughout the article
- Include related LSI keywords organically
- Structure with H2 and H3 subheadings that include keywords
- Write a compelling meta-description-ready excerpt
- Front-load the most important points

ARTICLE STRUCTURE:
1. Opening provocation — a bold claim that grabs attention
2. Build the argument with real data, examples, and analogies
3. Address counterarguments and demolish them
4. Cultural/historical references that reinforce your point
5. Close with a challenge to the reader — make them think

TEMPORAL AWARENESS — CRITICAL:
- TODAY'S DATE: {today}. You are writing in {year}.
- Past events (2024 election, etc.) = PAST TENSE with explicit year.
- Future events must actually be in the future relative to {today}.
- Double-check every date, number, and statistic. Remove any you're unsure about.

LANGUAGE: Write in {language}.
LENGTH: 800-1200 words. This is a serious opinion piece, not a hot take.
OUTPUT: Return TITLE:, SUBTITLE:, EXCERPT:, the body, then TAGS: at the end.
"""

_EDUCATION_SYSTEM_PROMPT = """\
You are an expert educator and writer for Prediction Bets — the cultural center \
of prediction markets. You write EDUCATIONAL articles that make complex topics \
accessible, entertaining, and genuinely useful.

PERSONALITY:
- Knowledgeable but never condescending. You respect the reader's intelligence.
- Enthusiastic about prediction markets — you genuinely believe this knowledge is valuable.
- Uses humor and analogies to explain complex concepts
- Anti-jargon: if you use a technical term, you explain it immediately
- Inspired by the best explainer writers: Tim Urban (Wait But Why), Matt Levine (Bloomberg)

WRITING STYLE:
- Simple analogies that make abstract concepts click (betting odds = probability)
- Real examples from Polymarket, Kalshi, Metaculus
- Step-by-step explanations when teaching processes
- Pop culture references to make education fun
- Short paragraphs, clear structure, scannable content
- Tables or bullet points for comparisons
- NEVER sound like a textbook or Wikipedia
- Conversational tone — like a smart friend explaining over coffee

SEO REQUIREMENTS:
- Use the target keyword naturally 4-6 times throughout the article
- Include related long-tail keywords organically
- Structure with clear H2 and H3 subheadings (keyword-rich)
- Write a compelling excerpt that would work as a meta description
- Answer the user's search intent completely — be the definitive resource
- Include "what is", "how to", "why" phrasing naturally

ARTICLE STRUCTURE:
1. Hook — why this matters to the reader personally
2. Foundation — establish the basics clearly
3. Deep dive — break down the topic systematically with examples
4. Practical takeaway — what the reader can DO with this knowledge
5. Resources or next steps — where to go from here

TEMPORAL AWARENESS — CRITICAL:
- TODAY'S DATE: {today}. You are writing in {year}.
- Past events (2024 election, etc.) = PAST TENSE with explicit year.
- Future events must actually be in the future relative to {today}.
- Double-check every date, number, and statistic. Remove any you're unsure about.

LANGUAGE: Write in {language}.
LENGTH: 1000-1800 words. This is a comprehensive educational piece.
OUTPUT: Return TITLE:, SUBTITLE:, EXCERPT:, the body, then TAGS: at the end.
"""

_USER_TEMPLATE = """\
Write an original {article_type} article about the following topic:

TOPIC: {title_hint}

BRIEF:
{brief}

CATEGORY: {category}

INSTRUCTIONS:
- Create a catchy, SEO-optimized title (return as: TITLE: <title>)
- Create a subtitle that hooks the reader (return as: SUBTITLE: <subtitle>)
- Create a 1-2 sentence excerpt optimized for search/social sharing (return as: EXCERPT: <excerpt>)
- Write the full article body in Markdown with proper H2/H3 headings
- Choose 5-7 relevant SEO tags in lowercase (return at end as: TAGS: tag1, tag2, ...)
- Include internal linking opportunities with markdown links like [related topic](/category/markets)
"""


# ---------------------------------------------------------------------------
# Generator
# ---------------------------------------------------------------------------

class OriginalGenerator:
    """Generates original opinion and educational articles via Claude."""

    def __init__(self) -> None:
        self._client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    def generate(
        self,
        topic: dict[str, str],
        language: str = "English",
    ) -> Optional[dict[str, Any]]:
        """Generate an original article from a topic brief."""
        article_type = topic["type"]

        now = datetime.now(tz=timezone.utc)
        fmt = dict(language=language, today=now.strftime("%Y-%m-%d"), year=now.year)

        if article_type == "opinion":
            system_prompt = _OPINION_SYSTEM_PROMPT.format(**fmt)
        else:
            system_prompt = _EDUCATION_SYSTEM_PROMPT.format(**fmt)

        user_prompt = _USER_TEMPLATE.format(
            article_type=article_type,
            title_hint=topic["title_hint"],
            brief=topic["brief"],
            category=topic["category"],
        )

        try:
            message = self._client.messages.create(
                model=CLAUDE_MODEL,
                max_tokens=4096,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}],
            )

            raw_output = message.content[0].text.strip()
            return self._parse_output(raw_output, topic)

        except anthropic.APIError as exc:
            print(f"  Claude API error: {exc}")
            return None
        except Exception as exc:
            print(f"  Unexpected error: {exc}")
            return None

    def _parse_output(
        self,
        raw_output: str,
        topic: dict[str, str],
    ) -> dict[str, Any]:
        """Parse structured output into article components."""
        lines = raw_output.splitlines()
        title = topic["title_hint"]
        subtitle = ""
        excerpt = ""
        tags: list[str] = []
        body_lines: list[str] = []
        in_body = False

        for line in lines:
            stripped = line.strip()

            if stripped.upper().startswith("TITLE:"):
                title = stripped.split(":", 1)[1].strip().strip('"')
                continue

            if stripped.upper().startswith("SUBTITLE:"):
                subtitle = stripped.split(":", 1)[1].strip().strip('"')
                continue

            if stripped.upper().startswith("EXCERPT:"):
                excerpt = stripped.split(":", 1)[1].strip().strip('"')
                in_body = True
                continue

            if stripped.upper().startswith("TAGS:"):
                raw_tags = stripped.split(":", 1)[1].strip()
                tags = [t.strip().lower() for t in raw_tags.split(",") if t.strip()]
                continue

            if in_body:
                body_lines.append(line)

        body = "\n".join(body_lines).strip()

        if not body:
            body = raw_output

        content_type = "edge" if topic["type"] == "opinion" else "analysis"

        if not tags:
            tags = [topic["category"], "prediction-markets"]

        return {
            "title": title,
            "subtitle": subtitle,
            "excerpt": excerpt,
            "body": body,
            "tags": tags,
            "content_type": content_type,
        }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    """Run the original content generator."""
    parser = argparse.ArgumentParser(
        description="Generate original opinion & educational articles"
    )
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--limit", type=int, default=0, help="Max articles (0=all)")
    parser.add_argument(
        "--type",
        choices=["opinion", "education", "all"],
        default="all",
        help="Article type filter",
    )
    args = parser.parse_args()

    # Filter topics by type
    topics = ARTICLE_TOPICS
    if args.type != "all":
        topics = [t for t in topics if t["type"] == args.type]
    if args.limit > 0:
        topics = topics[: args.limit]

    generator = OriginalGenerator()
    translator = Translator()
    image_sourcer = ImageSourcer()
    publisher = Publisher()

    print("=" * 60)
    print("PREDICTION BETS — ORIGINAL CONTENT GENERATOR")
    print("=" * 60)
    print(f"Generating {len(topics)} articles ({args.type})\n")

    published = 0
    failed = 0

    for i, topic in enumerate(topics):
        print(f"\n{'—' * 50}")
        print(f"[{i + 1}/{len(topics)}] {topic['type'].upper()}: {topic['title_hint'][:60]}")
        print(f"  Category: {topic['category']}")

        # Generate
        print("  Generating article...")
        article = generator.generate(topic, language="English")
        if not article:
            print("  FAIL: Generation failed")
            failed += 1
            continue

        print(f"  Title: {article['title'][:60]}")

        # Image
        print("  Sourcing image...")
        image = image_sourcer.get_image(topic["category"])

        # Author
        author = random.choice(FICTIONAL_AUTHORS)
        print(f"  Author: {author}")

        # Build article data
        article_data = {
            **article,
            "author": author,
            "category": topic["category"],
            "image": image["url"],
            "image_caption": image["caption"],
            "lang": "en",
            "featured": False,
        }

        if args.dry_run:
            print(f"  [DRY RUN] Would publish: {article['title']}")
            print(f"    Tags: {', '.join(article.get('tags', []))}")
            continue

        # Publish EN
        print("  Publishing EN...")
        slug = publisher.publish(article_data, locale="en")
        print(f"  Published EN: {slug}")

        # Translate & publish PT/ES
        print("  Translating...")
        for lang_code, lang_name in [("pt", "Portuguese"), ("es", "Spanish")]:
            translated = translator.translate(article, target_language=lang_name)
            if translated:
                trans_data = {
                    **article_data,
                    **translated,
                    "lang": lang_code,
                }
                publisher.publish(trans_data, locale=lang_code, slug=slug)
                print(f"  Published {lang_code.upper()}: {slug}")
            else:
                print(f"  WARN: {lang_name} translation failed")

        published += 1

    print(f"\n{'=' * 60}")
    print("GENERATION COMPLETE")
    print(f"{'=' * 60}")
    print(f"  Total:     {len(topics)}")
    print(f"  Published: {published}")
    print(f"  Failed:    {failed}")
    if args.dry_run:
        print("  (DRY RUN — no files written)")
    print()


if __name__ == "__main__":
    main()
