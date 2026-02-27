"""
Translation module for the Prediction Bets content pipeline.

Translates English articles to Portuguese and Spanish using Claude.
Preserves the voice, tone, tribal language, and Markdown formatting.
"""

from __future__ import annotations

from typing import Any, Optional

import anthropic

from config import ANTHROPIC_API_KEY, CLAUDE_MODEL

# ---------------------------------------------------------------------------
# Translation prompts
# ---------------------------------------------------------------------------

_TRANSLATION_SYSTEM = """\
You are a professional translator specializing in prediction markets content.
You translate articles while:

1. Preserving the author's unique voice: sharp, witty, anti-establishment,
   internet-native, with acid humor and pop culture references.
2. Keeping all Markdown formatting intact (headers, bold, italics, lists).
3. Adapting idioms naturally — never doing literal translations of slang.
4. Preserving any mild profanity at the same intensity level in the target language.
5. Keeping prediction market terms accurate but explained in plain language.
6. Preserving tribal language: signal, edge, consensus, reality check, skin in the game.
7. For Portuguese: use Brazilian Portuguese with a punchy, direct tone.
8. For Spanish: use neutral Latin American Spanish, not Castilian.

Return ONLY the translated content. No explanations, no notes, no preamble.
"""

_TRANSLATION_USER = """\
Translate the following English prediction markets article to {target_language}.

TITLE: {title}
SUBTITLE: {subtitle}
EXCERPT: {excerpt}

BODY:
{body}

---
Return in this exact format:
TRANSLATED_TITLE: <translated title>
TRANSLATED_SUBTITLE: <translated subtitle, or "none" if empty>
TRANSLATED_EXCERPT: <translated excerpt>
<translated body in Markdown>
"""


# ---------------------------------------------------------------------------
# Translator
# ---------------------------------------------------------------------------


class Translator:
    """
    Translates rewritten English articles to Portuguese and Spanish.

    Uses the Claude API with a translation-focused system prompt that
    preserves the Prediction Bets voice across languages.
    """

    def __init__(self) -> None:
        self._client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    def translate(
        self,
        article: dict[str, Any],
        target_language: str = "Portuguese",
    ) -> Optional[dict[str, Any]]:
        """
        Translate an article to the target language.

        Args:
            article: Dict with keys: title, subtitle, excerpt, body.
            target_language: Human-readable target language name
                             (e.g. "Portuguese", "Spanish").

        Returns:
            Dict with keys: title, subtitle, excerpt, body.
            Returns None if the API call fails.
        """
        prompt = _TRANSLATION_USER.format(
            target_language=target_language,
            title=article["title"],
            subtitle=article.get("subtitle", "") or "(no subtitle)",
            excerpt=article.get("excerpt", ""),
            body=article["body"][:5000],
        )

        try:
            message = self._client.messages.create(
                model=CLAUDE_MODEL,
                max_tokens=2048,
                system=_TRANSLATION_SYSTEM,
                messages=[{"role": "user", "content": prompt}],
            )

            raw = message.content[0].text.strip()
            return self._parse_translation(
                raw,
                fallback_title=article["title"],
                fallback_subtitle=article.get("subtitle", ""),
                fallback_excerpt=article.get("excerpt", ""),
            )

        except anthropic.APIError as exc:
            print(f"  Translation API error ({target_language}): {exc}")
            return None
        except Exception as exc:
            print(f"  Unexpected translation error ({target_language}): {exc}")
            return None

    @staticmethod
    def _parse_translation(
        raw: str,
        fallback_title: str,
        fallback_subtitle: str,
        fallback_excerpt: str,
    ) -> dict[str, Any]:
        """
        Parse the structured translation output from Claude.

        Expected format:
            TRANSLATED_TITLE: <title>
            TRANSLATED_SUBTITLE: <subtitle or "none">
            TRANSLATED_EXCERPT: <excerpt>
            <translated body>
        """
        lines = raw.splitlines()
        title = fallback_title
        subtitle = fallback_subtitle
        excerpt = fallback_excerpt
        body_lines: list[str] = []
        in_body = False

        for line in lines:
            stripped = line.strip()

            if stripped.upper().startswith("TRANSLATED_TITLE:"):
                title = stripped.split(":", 1)[1].strip().strip('"')
                continue

            if stripped.upper().startswith("TRANSLATED_SUBTITLE:"):
                raw_sub = stripped.split(":", 1)[1].strip()
                if raw_sub.lower() in ("none", "nenhum", "ninguno", "(no subtitle)"):
                    subtitle = ""
                else:
                    subtitle = raw_sub.strip('"')
                continue

            if stripped.upper().startswith("TRANSLATED_EXCERPT:"):
                excerpt = stripped.split(":", 1)[1].strip().strip('"')
                in_body = True
                continue

            if in_body:
                body_lines.append(line)

        body = "\n".join(body_lines).strip()

        # Fallback if parsing completely failed
        if not body:
            body = raw

        return {
            "title": title,
            "subtitle": subtitle,
            "excerpt": excerpt,
            "body": body,
        }
