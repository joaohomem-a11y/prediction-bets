"""
Article rewriter using the Anthropic Claude API.

Takes a raw feed item and rewrites it in the Prediction Bets voice:
sharp, witty, anti-establishment, Taleb-inspired, prediction-market-native,
with pop culture references and plain-language explanations.
"""

from __future__ import annotations

from typing import Any, Optional

import anthropic

from config import ANTHROPIC_API_KEY, CLAUDE_MODEL

# ---------------------------------------------------------------------------
# Voice prompt — the soul of the agent
# ---------------------------------------------------------------------------

_VOICE_SYSTEM_PROMPT = """\
You are a sharp, witty writer covering prediction markets for Prediction Bets —
the cultural center of prediction markets. Your style:

PERSONALITY:
- Sharp, direct, no corporate fluff. You cut through noise to find the signal.
- Acid humor and biting irony against "experts" who opine without skin in the game.
- Anti-establishment: skeptical of talking heads, clickbait forecasters, authority without accountability.
- Inspired by Nassim Taleb: if you don't have skin in the game, your opinion is noise.
- Pro-markets, pro-accountability, pro-reality. Markets don't lie, people do.
- Internet-native voice: memes, cultural references, Gen Z energy meets Wall Street edge.

WRITING STYLE:
- Pop culture and movie references (Matrix, Breaking Bad, Succession, The Big Short, etc.)
- Explain prediction market jargon in plain language with humor
- Occasional mild profanity when it lands (damn, hell, BS — never gratuitous)
- Deep analysis, never surface-level. Go beyond the headline.
- Use real examples: Polymarket, Kalshi, Metaculus data when relevant
- Provocative questions to the reader at the end
- Tone of insider letter, not corporate article
- Short paragraphs. Fast rhythm. Punchy.
- NEVER sound like AI or a press release
- Use tribal language naturally: signal, edge, consensus, reality check, market truth

ARTICLE STRUCTURE:
1. Opening punch (quote, anecdote, paradox, cultural reference, or slap in the face)
2. Cultural/historical analogy connecting to the prediction market event
3. Real analysis of what the market data actually says — no sugar coating
4. Education disguised as entertainment — teach a prediction concept naturally
5. Provocative close that challenges the reader. No summaries. End with a punch.

LANGUAGE: Write in {language}.
OUTPUT: Only the article body in Markdown. No frontmatter. No H1 title at the start.
"""

_CONTENT_TYPE_INSTRUCTIONS = {
    "signal": (
        "Write as a SIGNAL piece: report the news with your sharp analysis on top. "
        "Focus on what the prediction market data reveals. 400-800 words."
    ),
    "analysis": (
        "Write as a deep ANALYSIS piece: break down the topic thoroughly, "
        "use data, challenge conventional wisdom. 600-1200 words."
    ),
    "reality-check": (
        "Write as a REALITY CHECK: take a popular narrative or expert consensus "
        "and tear it apart with market data and clear thinking. 500-900 words."
    ),
    "culture": (
        "Write as a CULTURE piece: explore the social, cultural, or community "
        "side of prediction markets. Lighter tone, more fun. 400-700 words."
    ),
    "edge": (
        "Write as an EDGE piece: provide actionable insight or a contrarian "
        "perspective that gives the reader an information advantage. 500-900 words."
    ),
}

_REWRITE_USER_TEMPLATE = """\
Rewrite the article below in the style described. The original is in English.

ORIGINAL TITLE: {title}

SOURCE: {source}

ORIGINAL CONTENT:
{summary}

---
ADDITIONAL INSTRUCTIONS:
- CONTENT TYPE: {content_type_instruction}
- Suggested category: {category}
- Create a catchy, provocative title (return as first line: TITLE: <title here>)
- Create a subtitle that hooks the reader (return as second line: SUBTITLE: <subtitle here>)
- Create a 1-2 sentence excerpt that makes people click (return as: EXCERPT: <excerpt here>)
- After the excerpt, write the full article body in Markdown
- Choose 3-5 relevant tags in lowercase (return at the end: TAGS: tag1, tag2, tag3)
"""


# ---------------------------------------------------------------------------
# Rewriter
# ---------------------------------------------------------------------------


class Rewriter:
    """
    Rewrites feed items into full articles using the Claude API.

    Sends the original article data along with the Prediction Bets
    voice prompt, then parses the structured output into article components.
    """

    def __init__(self) -> None:
        self._client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    def rewrite(
        self,
        item: dict[str, str],
        language: str = "English",
    ) -> Optional[dict[str, Any]]:
        """
        Rewrite a single feed item in the Prediction Bets voice.

        Args:
            item: Feed item dict with keys: title, summary, source,
                  category, content_type.
            language: Target language name (e.g. "English").

        Returns:
            Dict with keys: title, subtitle, excerpt, body, tags.
            Returns None if the API call fails.
        """
        content_type = item.get("content_type", "signal")
        content_type_instruction = _CONTENT_TYPE_INSTRUCTIONS.get(
            content_type, _CONTENT_TYPE_INSTRUCTIONS["signal"]
        )

        system_prompt = _VOICE_SYSTEM_PROMPT.format(language=language)

        user_prompt = _REWRITE_USER_TEMPLATE.format(
            title=item["title"],
            source=item["source"],
            summary=item.get("summary", "")[:5000],
            category=item["category"],
            content_type_instruction=content_type_instruction,
        )

        try:
            message = self._client.messages.create(
                model=CLAUDE_MODEL,
                max_tokens=2048,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}],
            )

            raw_output = message.content[0].text.strip()
            return self._parse_output(raw_output, item)

        except anthropic.APIError as exc:
            print(f"  Claude API error: {exc}")
            return None
        except Exception as exc:
            print(f"  Unexpected rewrite error: {exc}")
            return None

    def _parse_output(
        self,
        raw_output: str,
        original: dict[str, str],
    ) -> dict[str, Any]:
        """
        Parse the structured output from Claude into article components.

        Expected format:
            TITLE: <title>
            SUBTITLE: <subtitle>
            EXCERPT: <excerpt>
            <body markdown>
            TAGS: tag1, tag2, tag3
        """
        lines = raw_output.splitlines()
        title = original["title"]
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

        # Fallback: if parsing failed, use the full output as body
        if not body:
            body = raw_output

        # Ensure we have at least some tags
        if not tags:
            tags = [original["category"], "prediction-markets", "market-signal"]

        # Generate excerpt from body if not provided
        if not excerpt and body:
            excerpt = self._make_excerpt(body)

        return {
            "title": title,
            "subtitle": subtitle,
            "excerpt": excerpt,
            "body": body,
            "tags": tags,
        }

    @staticmethod
    def _make_excerpt(body: str, max_chars: int = 160) -> str:
        """Extract a plain-text excerpt from the article body."""
        import re

        text = re.sub(r"#+\s*", "", body)
        text = re.sub(r"\*{1,3}(.+?)\*{1,3}", r"\1", text)
        text = re.sub(r"`{1,3}[^`]*`{1,3}", "", text)
        text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
        text = re.sub(r">\s*", "", text)
        text = re.sub(r"\n+", " ", text)
        text = re.sub(r"\s{2,}", " ", text)
        text = text.strip()

        if len(text) <= max_chars:
            return text

        trimmed = text[:max_chars]
        last_space = trimmed.rfind(" ")
        if last_space > max_chars * 0.7:
            trimmed = trimmed[:last_space]
        return trimmed + "..."
