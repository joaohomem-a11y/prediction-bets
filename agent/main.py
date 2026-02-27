#!/usr/bin/env python3
"""
Prediction Bets content pipeline.

Orchestrates the full content generation flow:
1. Fetch prediction market news from RSS feeds
2. Rewrite articles in the Prediction Bets voice using Claude
3. Source relevant images from Unsplash
4. Translate to PT and ES
5. Publish as Markdown files to the Next.js site

Usage:
    python main.py                  # Run full pipeline
    python main.py --dry-run        # Preview without writing files
    python main.py --limit 3        # Process max 3 articles
"""

from __future__ import annotations

import argparse
import random
import sys

from config import FICTIONAL_AUTHORS, RSS_FEEDS
from fetcher import FeedFetcher
from rewriter import Rewriter
from translator import Translator
from image_sourcer import ImageSourcer
from publisher import Publisher


def main() -> None:
    """Run the Prediction Bets content pipeline."""
    parser = argparse.ArgumentParser(
        description="Prediction Bets content pipeline"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print output without writing files",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=5,
        help="Max articles to process (default: 5)",
    )
    args = parser.parse_args()

    # Initialize pipeline components
    fetcher = FeedFetcher()
    rewriter = Rewriter()
    translator = Translator()
    image_sourcer = ImageSourcer()
    publisher = Publisher()

    # -----------------------------------------------------------------------
    # 1. Fetch
    # -----------------------------------------------------------------------
    print("=" * 60)
    print("PREDICTION BETS CONTENT PIPELINE")
    print("=" * 60)
    print("\n[1/5] Fetching feeds...")
    items = fetcher.fetch_all(RSS_FEEDS, limit=args.limit)
    print(f"Found {len(items)} items to process")

    if not items:
        print("\nNo new items found. Exiting.")
        sys.exit(0)

    published_count = 0
    failed_count = 0

    for i, item in enumerate(items):
        print(f"\n{'—' * 50}")
        print(f"[{i + 1}/{len(items)}] Processing: {item['title'][:70]}")
        print(f"  Source: {item['source']} | Category: {item['category']}")

        # -------------------------------------------------------------------
        # 2. Rewrite
        # -------------------------------------------------------------------
        print("[2/5] Rewriting in Prediction Bets voice...")
        rewritten = rewriter.rewrite(item, language="English")
        if not rewritten:
            print("  SKIP: Rewrite failed")
            failed_count += 1
            continue

        print(f"  New title: {rewritten['title'][:60]}")

        # -------------------------------------------------------------------
        # 3. Source image
        # -------------------------------------------------------------------
        print("[3/5] Sourcing image...")
        image = image_sourcer.get_image(item["category"])

        # -------------------------------------------------------------------
        # 4. Assign author
        # -------------------------------------------------------------------
        author = random.choice(FICTIONAL_AUTHORS)
        print(f"  Author: {author}")

        # -------------------------------------------------------------------
        # 5. Build article data & publish EN
        # -------------------------------------------------------------------
        article_data = {
            **rewritten,
            "author": author,
            "category": item["category"],
            "content_type": item["content_type"],
            "image": image["url"],
            "image_caption": image["caption"],
            "lang": "en",
            "featured": i == 0,  # First article is featured
            "published": item.get("published"),
        }

        if args.dry_run:
            print(f"  [DRY RUN] Would publish: {rewritten['title']}")
            print(f"    Tags: {', '.join(rewritten.get('tags', []))}")
            continue

        print("[4/5] Publishing EN...")
        slug = publisher.publish(article_data, locale="en")
        print(f"  Published EN: {slug}")

        # -------------------------------------------------------------------
        # 6. Translate & publish PT/ES
        # -------------------------------------------------------------------
        print("[5/5] Translating & publishing PT/ES...")
        for lang_code, lang_name in [("pt", "Portuguese"), ("es", "Spanish")]:
            print(f"  Translating to {lang_name}...")
            translated = translator.translate(rewritten, target_language=lang_name)
            if translated:
                trans_data = {
                    **article_data,
                    **translated,
                    "lang": lang_code,
                }
                publisher.publish(trans_data, locale=lang_code, slug=slug)
                print(f"  Published {lang_code.upper()}: {slug}")
            else:
                print(f"  WARN: Translation to {lang_name} failed, skipping")

        published_count += 1

    # -----------------------------------------------------------------------
    # Summary
    # -----------------------------------------------------------------------
    print(f"\n{'=' * 60}")
    print("PIPELINE COMPLETE")
    print(f"{'=' * 60}")
    print(f"  Processed: {len(items)} items")
    print(f"  Published: {published_count}")
    print(f"  Failed:    {failed_count}")
    if args.dry_run:
        print("  (DRY RUN — no files were written)")
    print()


if __name__ == "__main__":
    main()
