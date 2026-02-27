"""
RSS feed fetcher for the Prediction Bets content pipeline.

Fetches articles from configured RSS feeds, deduplicates by title
similarity, and returns structured feed items ready for rewriting.
"""

from __future__ import annotations

import hashlib
import json
import re
import time
from datetime import datetime, timezone
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any

import feedparser

from config import PROJECT_ROOT


# ---------------------------------------------------------------------------
# State tracking — already-processed URLs
# ---------------------------------------------------------------------------

_STATE_FILE: Path = PROJECT_ROOT / "agent" / ".processed_urls.json"


class ProcessedURLStore:
    """Persists the set of already-processed article URLs to avoid duplication."""

    def __init__(self, state_file: Path = _STATE_FILE) -> None:
        self._path = state_file
        self._seen: set[str] = self._load()

    def _load(self) -> set[str]:
        if self._path.exists():
            try:
                data = json.loads(self._path.read_text(encoding="utf-8"))
                return set(data.get("processed_urls", []))
            except (json.JSONDecodeError, KeyError):
                return set()
        return set()

    def save(self) -> None:
        """Persist the current seen-URL set to disk."""
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._path.write_text(
            json.dumps({"processed_urls": sorted(self._seen)}, indent=2),
            encoding="utf-8",
        )

    def has_seen(self, url: str) -> bool:
        return url in self._seen

    def mark_seen(self, url: str) -> None:
        self._seen.add(url)


# ---------------------------------------------------------------------------
# HTML cleaning helpers
# ---------------------------------------------------------------------------


def _strip_html(raw_html: str) -> str:
    """Strip HTML tags and normalize whitespace."""
    if not raw_html:
        return ""
    # Remove HTML tags
    text = re.sub(r"<[^>]+>", " ", raw_html)
    # Collapse whitespace
    text = re.sub(r"\s{2,}", " ", text)
    return text.strip()


def _parse_date(entry: Any) -> str:
    """Extract publication date from a feed entry as ISO date string."""
    for attr in ("published_parsed", "updated_parsed", "created_parsed"):
        t = getattr(entry, attr, None)
        if t:
            dt = datetime(*t[:6], tzinfo=timezone.utc)
            return dt.strftime("%Y-%m-%d")
    return datetime.now(tz=timezone.utc).strftime("%Y-%m-%d")


def _title_hash(title: str) -> str:
    """Generate a short hash from a title for deduplication."""
    normalized = re.sub(r"\W+", "", title.lower())
    return hashlib.sha256(normalized.encode()).hexdigest()[:12]


def _titles_are_similar(a: str, b: str, threshold: float = 0.75) -> bool:
    """Check if two titles are similar enough to be considered duplicates."""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio() >= threshold


# ---------------------------------------------------------------------------
# Core fetcher
# ---------------------------------------------------------------------------


class FeedFetcher:
    """
    Fetches and parses RSS feeds, returning clean feed item dicts.

    Uses a ProcessedURLStore to skip already-seen articles and
    deduplicates by title similarity within each batch.
    """

    def __init__(self) -> None:
        self._store = ProcessedURLStore()

    def fetch_all(
        self,
        feeds: list[dict[str, str]],
        limit: int = 5,
    ) -> list[dict[str, str]]:
        """
        Fetch new articles from all configured RSS feeds.

        Args:
            feeds: List of feed configuration dicts with keys:
                   name, url, language, category, content_type.
            limit: Maximum total articles to return.

        Returns:
            List of feed item dicts with keys: title, link, summary,
            published, source, category, content_type, title_hash.
        """
        all_items: list[dict[str, str]] = []

        for feed_cfg in feeds:
            try:
                items = self._fetch_feed(feed_cfg)
                all_items.extend(items)
                print(f"  Fetched {len(items)} items from {feed_cfg['name']}")
            except Exception as exc:
                print(f"  ERROR fetching {feed_cfg['name']}: {exc}")

        # Deduplicate by title similarity
        deduped = self._deduplicate(all_items)

        # Limit total items
        result = deduped[:limit]

        # Save state
        self._store.save()

        return result

    def _fetch_feed(self, feed_cfg: dict[str, str]) -> list[dict[str, str]]:
        """Parse a single RSS feed and return unseen items."""
        feed = feedparser.parse(feed_cfg["url"])
        items: list[dict[str, str]] = []

        for entry in feed.entries:
            url = entry.get("link", "")
            if not url or self._store.has_seen(url):
                continue

            title = _strip_html(entry.get("title", ""))
            if not title:
                continue

            summary_html = (
                entry.get("summary", "")
                or entry.get("description", "")
                or ""
            )
            summary = _strip_html(summary_html)[:500]

            item = {
                "title": title,
                "link": url,
                "summary": summary,
                "published": _parse_date(entry),
                "source": feed_cfg["name"],
                "category": feed_cfg["category"],
                "content_type": feed_cfg.get("content_type", "signal"),
                "title_hash": _title_hash(title),
            }

            self._store.mark_seen(url)
            items.append(item)

            # Be polite to feed servers
            time.sleep(0.3)

        return items

    def _deduplicate(self, items: list[dict[str, str]]) -> list[dict[str, str]]:
        """Remove items with similar titles, keeping the first occurrence."""
        seen_titles: list[str] = []
        unique: list[dict[str, str]] = []

        for item in items:
            title = item["title"]
            is_dup = any(
                _titles_are_similar(title, seen)
                for seen in seen_titles
            )
            if not is_dup:
                seen_titles.append(title)
                unique.append(item)

        if len(items) != len(unique):
            print(f"  Deduplication: {len(items)} -> {len(unique)} items")

        return unique
