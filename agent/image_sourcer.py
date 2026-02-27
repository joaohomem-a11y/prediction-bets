"""
Unsplash image sourcer for article header images.

Queries the Unsplash API for relevant images based on article category.
Falls back to a default placeholder if the API key is missing or the
request fails — the pipeline never breaks due to image sourcing.
"""

from __future__ import annotations

import random
from typing import Any

import requests

from config import UNSPLASH_ACCESS_KEY, UNSPLASH_SEARCH_TERMS

_UNSPLASH_API_BASE = "https://api.unsplash.com"

# Default fallback images per category (free Unsplash URLs)
_DEFAULT_IMAGES: dict[str, dict[str, str]] = {
    "politics": {
        "url": "https://images.unsplash.com/photo-1540910419892-4a36d2c3266c?w=1200&q=80&fit=crop",
        "caption": "Democracy in motion — Photo on Unsplash",
    },
    "crypto": {
        "url": "https://images.unsplash.com/photo-1518546305927-5a555bb7020d?w=1200&q=80&fit=crop",
        "caption": "Digital currency frontier — Photo on Unsplash",
    },
    "ai-tech": {
        "url": "https://images.unsplash.com/photo-1677442135136-760c813028c4?w=1200&q=80&fit=crop",
        "caption": "The future is being predicted — Photo on Unsplash",
    },
    "sports": {
        "url": "https://images.unsplash.com/photo-1461896836934-bd45ba8fdbac?w=1200&q=80&fit=crop",
        "caption": "Where the odds meet the field — Photo on Unsplash",
    },
    "markets": {
        "url": "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=1200&q=80&fit=crop",
        "caption": "Markets never lie — Photo on Unsplash",
    },
    "culture": {
        "url": "https://images.unsplash.com/photo-1522202176988-66273c2fd55f?w=1200&q=80&fit=crop",
        "caption": "Prediction culture — Photo on Unsplash",
    },
    "geopolitics": {
        "url": "https://images.unsplash.com/photo-1526778548025-fa2f459cd5c1?w=1200&q=80&fit=crop",
        "caption": "The world is a prediction market — Photo on Unsplash",
    },
}

_FALLBACK_DEFAULT = {
    "url": "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=1200&q=80&fit=crop",
    "caption": "Prediction markets — Photo on Unsplash",
}


# ---------------------------------------------------------------------------
# Image sourcer
# ---------------------------------------------------------------------------


class ImageSourcer:
    """
    Fetches relevant header images from the Unsplash API.

    Works without an API key by falling back to category-specific
    default images. Never raises exceptions — always returns a usable image.
    """

    def __init__(self) -> None:
        self._access_key = UNSPLASH_ACCESS_KEY

    def get_image(self, category: str) -> dict[str, str]:
        """
        Get a relevant image for the given article category.

        Tries the Unsplash API first (if key is available), then falls
        back to a hardcoded default image for the category.

        Args:
            category: Article category (e.g. "markets", "crypto").

        Returns:
            Dict with keys: url, caption.
        """
        # If no API key, use fallback immediately
        if not self._access_key:
            return self._get_default(category)

        # Try Unsplash API
        query = UNSPLASH_SEARCH_TERMS.get(category, "prediction markets finance")
        try:
            return self._search_unsplash(query, category)
        except Exception as exc:
            print(f"  Unsplash search failed for '{query}': {exc}. Using default.")
            return self._get_default(category)

    def _search_unsplash(self, query: str, category: str) -> dict[str, str]:
        """
        Perform the Unsplash search API call.

        Args:
            query: Search string.
            category: Article category (used for fallback).

        Returns:
            Dict with keys: url, caption.

        Raises:
            requests.RequestException: On network or API errors.
            ValueError: If no results are returned.
        """
        response = requests.get(
            f"{_UNSPLASH_API_BASE}/search/photos",
            headers={
                "Authorization": f"Client-ID {self._access_key}",
                "Accept-Version": "v1",
            },
            params={
                "query": query,
                "per_page": 10,
                "orientation": "landscape",
                "content_filter": "high",
            },
            timeout=10,
        )
        response.raise_for_status()
        data: Any = response.json()

        results = data.get("results", [])
        if not results:
            raise ValueError(f"No Unsplash results for query: '{query}'")

        # Pick a random result from the top 5 for variety
        photo = random.choice(results[: min(5, len(results))])
        url = photo["urls"]["regular"]
        photographer = photo["user"]["name"]
        description = (
            photo.get("description")
            or photo.get("alt_description")
            or query.title()
        )

        # Format URL with standard dimensions
        base_url = url.split("?")[0]
        formatted_url = f"{base_url}?w=1200&q=80&fit=crop"

        caption = f"{description.capitalize()} — Photo by {photographer} on Unsplash"

        print(f"  Image sourced: '{description[:50]}' by {photographer}")

        return {
            "url": formatted_url,
            "caption": caption,
        }

    @staticmethod
    def _get_default(category: str) -> dict[str, str]:
        """Return a default image for the given category."""
        default = _DEFAULT_IMAGES.get(category, _FALLBACK_DEFAULT)
        return {
            "url": default["url"],
            "caption": default["caption"],
        }
