"""
Configuration for the Prediction Bets content pipeline.

Loads environment variables, defines RSS feeds, fictional authors,
categories, and all shared constants used across the pipeline.
"""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------------------------------------
# API Keys
# ---------------------------------------------------------------------------

ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
UNSPLASH_ACCESS_KEY: str = os.getenv("UNSPLASH_ACCESS_KEY", "")

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

PROJECT_ROOT: Path = Path(__file__).parent.parent
ARTICLES_DIR: Path = PROJECT_ROOT / "site" / "src" / "content" / "articles"

# ---------------------------------------------------------------------------
# Languages
# ---------------------------------------------------------------------------

LANGUAGES: list[str] = ["en", "pt", "es"]
PRIMARY_LANGUAGE: str = "en"

# ---------------------------------------------------------------------------
# RSS Feeds
# ---------------------------------------------------------------------------

RSS_FEEDS: list[dict[str, str]] = [
    {
        "name": "Google News Prediction Markets",
        "url": "https://news.google.com/rss/search?q=prediction+markets&hl=en-US",
        "language": "en",
        "category": "markets",
        "content_type": "signal",
    },
    {
        "name": "Google News Polymarket",
        "url": "https://news.google.com/rss/search?q=Polymarket&hl=en-US",
        "language": "en",
        "category": "markets",
        "content_type": "signal",
    },
    {
        "name": "Google News Kalshi",
        "url": "https://news.google.com/rss/search?q=Kalshi&hl=en-US",
        "language": "en",
        "category": "markets",
        "content_type": "signal",
    },
    {
        "name": "CoinDesk",
        "url": "https://www.coindesk.com/arc/outboundfeeds/rss/",
        "language": "en",
        "category": "crypto",
        "content_type": "signal",
    },
    {
        "name": "Google News Elections",
        "url": "https://news.google.com/rss/search?q=election+odds+betting&hl=en-US",
        "language": "en",
        "category": "politics",
        "content_type": "signal",
    },
    {
        "name": "Google News AI Predictions",
        "url": "https://news.google.com/rss/search?q=AI+predictions+forecast&hl=en-US",
        "language": "en",
        "category": "ai-tech",
        "content_type": "signal",
    },
]

# ---------------------------------------------------------------------------
# Fictional Authors
# ---------------------------------------------------------------------------

FICTIONAL_AUTHORS: list[str] = [
    "The Oracle of Odds",
    "Consensus Crusher",
    "Base Rate Betty",
    "Signal Samurai",
    "Edge Lord Eddie",
    "The Contrarian",
    "Probability Pete",
    "Market Truth Marta",
    "Skin-in-the-Game Steve",
    "Black Swan Brenda",
]

# ---------------------------------------------------------------------------
# Categories (must match site/src/types/article.ts Category type)
# ---------------------------------------------------------------------------

CATEGORIES: list[str] = [
    "politics",
    "crypto",
    "ai-tech",
    "sports",
    "markets",
    "culture",
    "geopolitics",
]

# ---------------------------------------------------------------------------
# Content Types (must match site/src/types/article.ts ContentType type)
# ---------------------------------------------------------------------------

CONTENT_TYPES: list[str] = [
    "signal",
    "analysis",
    "reality-check",
    "culture",
    "edge",
]

# ---------------------------------------------------------------------------
# Unsplash search terms per category
# ---------------------------------------------------------------------------

UNSPLASH_SEARCH_TERMS: dict[str, str] = {
    "politics": "political election voting",
    "crypto": "cryptocurrency blockchain digital",
    "ai-tech": "artificial intelligence technology future",
    "sports": "sports competition stadium",
    "markets": "stock market trading finance",
    "culture": "internet culture digital community",
    "geopolitics": "world map geopolitics globe",
}

# ---------------------------------------------------------------------------
# Claude model
# ---------------------------------------------------------------------------

CLAUDE_MODEL: str = "claude-sonnet-4-20250514"
