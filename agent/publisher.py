"""
Markdown publisher for the Prediction Bets content pipeline.

Creates locale-specific markdown files with YAML frontmatter for
the Next.js site, organized by language subdirectory.

Directory structure produced:
    <articles_dir>/
        <slug>.md          (EN — primary language, root level)
        pt/<slug>.md       (PT — Portuguese)
        es/<slug>.md       (ES — Spanish)

Frontmatter matches the ArticleFrontmatter TypeScript type defined in
site/src/types/article.ts.
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from config import ARTICLES_DIR


# ---------------------------------------------------------------------------
# Slug generation
# ---------------------------------------------------------------------------


def _slugify(text: str, max_length: int = 70) -> str:
    """
    Generate a URL-safe slug from text.

    Converts to lowercase, replaces non-alphanumeric characters with
    hyphens, collapses multiple hyphens, and trims to max_length at
    a word boundary.

    Args:
        text: Input text to slugify.
        max_length: Maximum slug length.

    Returns:
        A clean slug string.
    """
    # Lowercase and replace non-alphanumeric with hyphens
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower())
    # Remove leading/trailing hyphens
    slug = slug.strip("-")
    # Collapse multiple hyphens
    slug = re.sub(r"-{2,}", "-", slug)

    if len(slug) <= max_length:
        return slug

    # Trim at a hyphen boundary
    trimmed = slug[:max_length]
    last_hyphen = trimmed.rfind("-")
    if last_hyphen > max_length * 0.5:
        trimmed = trimmed[:last_hyphen]
    return trimmed


def _make_author_slug(author: str) -> str:
    """Generate an author slug from the display name."""
    return _slugify(author, max_length=60)


# ---------------------------------------------------------------------------
# Frontmatter builder
# ---------------------------------------------------------------------------


def _build_frontmatter(
    title: str,
    subtitle: str,
    author: str,
    category: str,
    tags: list[str],
    image_url: str,
    image_caption: str,
    excerpt: str,
    content_type: str,
    featured: bool,
    lang: str,
    published_date: str | None = None,
) -> dict[str, Any]:
    """
    Build the frontmatter dictionary for a markdown article.

    The output dict matches the ArticleFrontmatter TypeScript interface:
        title, subtitle?, date, author, authorSlug, category, tags,
        image, imageCaption, excerpt, contentType, featured, lang.

    Args:
        title: Article title.
        subtitle: Optional subtitle (empty string if none).
        author: Author display name.
        category: Content category slug.
        tags: List of article tags.
        image_url: Header image URL.
        image_caption: Image caption/attribution.
        excerpt: 1-2 sentence article excerpt.
        content_type: One of: signal, analysis, reality-check, culture, edge.
        featured: Whether this article is featured on the homepage.
        lang: Language code (en, pt, es).
        published_date: ISO date string. Defaults to today.

    Returns:
        Dict ready for YAML serialization.
    """
    if not published_date:
        published_date = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d")

    fm: dict[str, Any] = {
        "title": title,
        "date": published_date,
        "author": author,
        "authorSlug": _make_author_slug(author),
        "category": category,
        "tags": tags,
        "image": image_url,
        "imageCaption": image_caption,
        "excerpt": excerpt,
        "contentType": content_type,
        "featured": featured,
        "lang": lang,
    }

    # Only include subtitle if it's non-empty (it's optional in the TS type)
    if subtitle:
        fm["subtitle"] = subtitle

    return fm


def _render_markdown(frontmatter: dict[str, Any], body: str) -> str:
    """
    Render a complete markdown file string with YAML frontmatter.

    Args:
        frontmatter: Dict of frontmatter key-value pairs.
        body: Article body in Markdown.

    Returns:
        Full markdown file content as a string.
    """
    fm_yaml = yaml.dump(
        frontmatter,
        allow_unicode=True,
        default_flow_style=False,
        sort_keys=False,
    ).strip()

    return f"---\n{fm_yaml}\n---\n\n{body}\n"


# ---------------------------------------------------------------------------
# Publisher
# ---------------------------------------------------------------------------


class Publisher:
    """
    Writes localized markdown files to the Next.js content directory.

    EN articles go in the root articles/ directory.
    PT articles go in articles/pt/.
    ES articles go in articles/es/.
    """

    def __init__(self, output_dir: Path = ARTICLES_DIR) -> None:
        self._output_dir = output_dir
        self._ensure_dirs()

    def _ensure_dirs(self) -> None:
        """Create language subdirectories if they do not exist."""
        self._output_dir.mkdir(parents=True, exist_ok=True)
        for lang in ("pt", "es"):
            (self._output_dir / lang).mkdir(parents=True, exist_ok=True)

    def publish(
        self,
        article_data: dict[str, Any],
        locale: str = "en",
        slug: str | None = None,
    ) -> str:
        """
        Write an article to disk as a Markdown file with YAML frontmatter.

        Args:
            article_data: Dict containing all article fields:
                title, subtitle, body, excerpt, tags, author,
                category, content_type, image, image_caption,
                lang, featured.
            locale: Language code for this version (en, pt, es).
            slug: Optional pre-determined slug. If None, generated from title.

        Returns:
            The article slug.
        """
        if not slug:
            slug = _slugify(article_data["title"])

        frontmatter = _build_frontmatter(
            title=article_data["title"],
            subtitle=article_data.get("subtitle", ""),
            author=article_data["author"],
            category=article_data["category"],
            tags=article_data.get("tags", []),
            image_url=article_data.get("image", ""),
            image_caption=article_data.get("image_caption", ""),
            excerpt=article_data.get("excerpt", ""),
            content_type=article_data.get("content_type", "signal"),
            featured=article_data.get("featured", False),
            lang=locale,
            published_date=article_data.get("published", None),
        )

        body = article_data.get("body", "")
        content = _render_markdown(frontmatter, body)

        # EN files go in the root; PT/ES go in subdirectories
        if locale == "en":
            file_path = self._output_dir / f"{slug}.md"
        else:
            file_path = self._output_dir / locale / f"{slug}.md"

        file_path.write_text(content, encoding="utf-8")
        return slug
