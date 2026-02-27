# Prediction Bets — Phase 1 Design Document

**Date:** 2026-02-27
**Status:** Approved
**Scope:** Content site + Community forum (Phase 1)

---

## 1. Vision

Prediction Bets is a **culture engine** — the global epicenter of prediction markets.

Not a trading platform. Not an analytics dashboard. A **living culture** built around the
idea that markets reveal truth, opinions don't.

Phase 1 delivers: a **content/news site** with a distinctive voice that entertains and
educates, combined with a **closed community forum** where members debate, predict,
and build tribal identity.

---

## 2. Core Principles (from Guidance)

1. **Tribe First** — Users must feel "I am part of something"
2. **Us vs Them** — Against opinion without skin in the game
3. **Controlled Chaos** — Internet-native, slightly rebellious, meme-capable
4. **Entertainment is mandatory** — Every article must be worth reading for pleasure, not duty
5. **Reality beats opinion. Markets reveal truth.**

---

## 3. Tech Stack

| Layer              | Technology                                      |
|--------------------|------------------------------------------------|
| **Framework**      | Next.js 15 (App Router, SSR for SEO)            |
| **Styling**        | Tailwind CSS 3                                  |
| **i18n**           | next-intl (EN/PT/ES)                            |
| **Content**        | Markdown + YAML frontmatter                     |
| **Auth**           | NextAuth.js (Google, Apple, Facebook, X, email) |
| **Forum DB**       | PostgreSQL (via Supabase or Neon)               |
| **Forum ORM**      | Prisma                                          |
| **Agent pipeline** | Python (fetcher, rewriter, translator, publisher)|
| **AI**             | Claude API (rewrite + translate)                |
| **Images**         | Unsplash API                                    |
| **Deploy**         | Vercel                                          |

---

## 4. Visual Identity

### Direction: Polymarket DNA + Tribal Personality

Visually familiar to prediction market users (Polymarket-inspired) but with its own bold,
editorial personality.

### Color System

- **Background**: Dark (#0D0F14 primary, #13161D secondary)
- **Surface**: Cards/panels (#1A1D27)
- **Accent Primary**: Electric Blue (#2D7FF9) — Polymarket association
- **Accent Secondary**: Amber/Gold (#F5A623) — highlights, wins, featured
- **Success**: Green (#22C55E) — correct predictions, positive outcomes
- **Danger**: Red (#EF4444) — wrong predictions, alerts
- **Text Primary**: White (#F8FAFC)
- **Text Secondary**: Gray (#94A3B8)
- **Text Muted**: (#64748B)

### Typography

- **Headlines**: Inter (bold 700/800) — confident, modern, sans-serif
- **Body**: Inter (regular 400) — clean readability
- **Data/Numbers**: JetBrains Mono — monospace for probabilities, stats, market data
- **Accent**: Optional display font for hero sections

### Layout Principles

- Dashboard-style grid with editorial cards
- Category filters/tabs at top (like Polymarket: Trending, Politics, Crypto, AI, etc.)
- Cards show: thumbnail, title, category tag, excerpt, probability data when relevant
- Dark mode default with light mode toggle
- Mobile-first responsive design

### Vibe Statement

> "Polymarket com personalidade. Bloomberg Terminal feito por insiders que entendem
> memes. Parece familiar, mas tem alma."

---

## 5. Voice & Tone

### Personality DNA

The Prediction Bets voice is the **prediction markets version** of Dinheirologia's formula:

- **Sharp and direct** — No corporate fluff. No academic posturing. Get to the point.
- **Acid humor** — Ironic, witty, self-aware. Laughs at the "circus" of experts with no
  skin in the game.
- **Anti-establishment** — Against talking heads, clickbait forecasting, authority without
  accountability.
- **Data-backed provocation** — Every hot take has the data to support it.
- **Pop culture references** — Movies, memes, internet culture woven into analysis.
- **Tribal language** — Signal, Edge, Consensus, Reality Check, Market Truth, Prediction
  Mindset.
- **Entertaining first** — A person reads because it's genuinely fun, not because they
  "need the information."

### Voice Prompt (for Claude Rewriter)

The agent will use a custom system prompt that produces articles with:

1. **Opening punch** — Provocative hook, anecdote, paradox, or cultural reference
2. **Cultural/historical analogy** — Connect the prediction market event to something larger
3. **Deep analysis** — Go beyond the headline, explain what the market is actually saying
4. **Education disguised as entertainment** — Teach prediction market concepts naturally
5. **Provocative close** — End with a question that challenges the reader. No summaries.

### Tone Examples

**Good:**
> "Everyone is screaming 'recession.' The market says 34%. Know what that means? It
> means two-thirds of the smart money thinks you're wrong. But let's look at who's
> actually betting, not who's tweeting."

**Bad:**
> "In this article, we will analyze the current recession probability as indicated by
> prediction market data..."

### Content Types

| Type | Description | Length |
|------|-------------|--------|
| **Signal Report** | What's moving and why. Daily briefing style. | 400-800 words |
| **Deep Analysis** | Contrarian takes backed by data. Weekly. | 800-1500 words |
| **Reality Check** | Expert predictions vs market truth. Accountability. | 500-1000 words |
| **Market Culture** | Memes, community drama, prediction wins/losses. | 300-600 words |
| **Edge Report** | Educational: how to read markets, base rates, methodology. | 600-1200 words |

---

## 6. Content Categories

| Category | Slug | Description |
|----------|------|-------------|
| **Politics** | politics | Elections, policy, geopolitics through prediction lens |
| **Crypto** | crypto | Bitcoin, DeFi, protocol predictions, crypto market events |
| **AI & Tech** | ai-tech | AI timelines, AGI markets, tech predictions |
| **Sports** | sports | Odds, outcomes, sports prediction angles |
| **Markets** | markets | Macro, Fed, recession odds, financial events |
| **Culture** | culture | Memes, community, prediction culture, meta-commentary |
| **Geopolitics** | geopolitics | Wars, trade, international events, conflict markets |

---

## 7. Agent Pipeline

### Architecture

```
[Sources] → Fetcher → Rewriter (Claude) → Translator (Claude) → Image Sourcer → Publisher
```

### Sources (RSS + Scraping)

| Source | Type | Focus |
|--------|------|-------|
| Google News "prediction markets" | RSS | General news coverage |
| Google News "Polymarket" | RSS | Platform-specific news |
| Google News "Kalshi" | RSS | Regulated market news |
| CNBC Finance | RSS | Macro events affecting markets |
| CoinDesk | RSS | Crypto prediction markets |
| Decrypt | RSS | Web3/prediction market intersection |
| Seeking Alpha | RSS | Market analysis |
| Investopedia | RSS | Educational/market news |
| Yahoo Finance | RSS | Breaking financial news |

### Fictional Authors (Prediction Market themed)

- "The Oracle of Odds"
- "Consensus Crusher"
- "Base Rate Betty"
- "Signal Samurai"
- "Edge Lord Eddie"
- "The Contrarian"
- "Probability Pete"
- "Market Truth Marta"
- "Skin-in-the-Game Steve"
- "Black Swan Brenda"

### Pipeline Differences from Dinheirologia

1. **Sources**: Prediction market focused, not general finance
2. **Voice prompt**: Tribal, prediction-native, entertainment-first
3. **Categories**: Prediction market verticals
4. **Authors**: Themed fictional characters
5. **Content types**: Signal Report, Reality Check, Edge Report (new types)
6. **Language**: EN as primary (most sources are English), translated to PT/ES

---

## 8. Site Structure

```
predictionbets.com/
├── /                          → Home: editorial feed with Polymarket-style cards
│   ├── Trending articles
│   ├── Featured analysis (hero card)
│   ├── Category filter tabs
│   └── Newsletter CTA
│
├── /article/[slug]            → Full article page
│   ├── Article content
│   ├── Related articles
│   └── Share buttons (prediction card format)
│
├── /category/[slug]           → Category filtered feed
│
├── /community                 → Forum hub (requires auth)
│   ├── /community/[topic]     → Topic threads
│   └── /community/new         → Create new thread
│
├── /about                     → Manifesto + Creation Story
│   └── Creed, Sacred Words, Origin Story
│
├── /newsletter                → Email capture landing page
│
├── /auth/signin               → Login (social + email)
├── /auth/signup               → Register
│
└── /[locale]/...              → i18n versions (pt, es)
```

---

## 9. Community Forum

### Requirements

- **Closed community**: registration required to post and view forum
- **Authentication**: Social login (Google, Apple, Facebook, X) + email/password
- **Email verification**: Required before posting
- **Registration**: Frictionless — one-click social login preferred

### Forum Structure

| Section | Description |
|---------|-------------|
| **Signal Drop** | Share and discuss market movements, breaking predictions |
| **Contrarian Takes** | Post your contrarian view, community debates it |
| **Prediction Battles** | Public predictions with accountability |
| **Reality Check** | Post-outcome discussion: who got it right? who got it wrong? |
| **Edge Lab** | Educational: share methodology, tools, strategies |
| **Off-Market** | General chat, memes, community culture |

### Forum Features (Phase 1 MVP)

- Thread creation with title + body (Markdown)
- Reply/comment system (nested 1 level)
- Upvote/downvote on threads and replies
- User profiles (avatar, display name, join date, post count)
- Category/section filtering
- Sort by: New, Hot, Top
- Basic moderation (report, admin delete)
- Pinned/featured threads

### Forum Features (Phase 2 — NOT in scope now)

- Prediction tracking (log predictions with outcomes)
- Reputation/accuracy score
- Badges and achievements
- Leaderboards
- Real-time notifications

### Data Model (Core)

```
User
  id, email, name, avatar, provider, emailVerified, createdAt

Thread
  id, title, body, authorId, sectionSlug, upvotes, downvotes,
  isPinned, createdAt, updatedAt

Reply
  id, body, authorId, threadId, parentReplyId, upvotes, downvotes,
  createdAt

Vote
  id, userId, targetType (thread|reply), targetId, value (+1|-1)
```

---

## 10. Pages Detail

### Home Page

- **Hero**: Featured article with large card, probability data overlay
- **Trending Bar**: Horizontal scroll of trending topic tags
- **Article Grid**: 3-column grid of editorial cards
  - Each card: thumbnail, category badge, title, excerpt, author, date
  - Cards styled like Polymarket market cards but for editorial content
- **Sidebar** (desktop): Newsletter CTA, "Join the Tribe" forum CTA
- **Category Tabs**: All, Politics, Crypto, AI & Tech, Sports, Markets, Culture

### Article Page

- Full-width header image
- Category badge + date + author
- Article body (Markdown rendered)
- Share buttons (generate "prediction card" image for social)
- Related articles grid
- CTA: "Join the discussion in the forum"

### Community Pages

- Forum section list with thread counts and latest activity
- Thread list with upvotes, reply count, author, time
- Thread detail with replies
- New thread form (requires auth)
- User profile card in sidebar

### About Page

- **Creation Story**: "Prediction Bets was born because forecasting is broken"
- **Creed**: Reality is measurable. Skin in the game matters.
- **Sacred Words**: Glossary of tribal language
- **The Tribe**: Description of who we are and who we stand against

---

## 11. SEO Strategy

- SSR via Next.js for all content pages
- Dynamic sitemap.xml with all articles
- robots.txt configured properly
- OpenGraph + Twitter Card meta for every article
- Structured data (Article schema) for Google
- Canonical URLs with hreflang for multilingual
- Fast Core Web Vitals (target: all green)

---

## 12. What We Are NOT Building (Phase 2+)

- Real-time market data integration / live odds
- User prediction tracking with accuracy scoring
- Leaderboards and reputation system
- API for external consumption
- Mobile app
- Podcast / video platform
- Automated social media posting
- Payment / premium tier

---

## 13. Success Criteria (Phase 1)

- Site live with 20+ initial articles
- Agent pipeline running and producing 3-5 articles/day
- Forum functional with auth and core features
- Trilingual (EN/PT/ES) working
- Dark mode Polymarket-inspired design
- SEO fundamentals in place
- Newsletter capture working
- Mobile responsive
