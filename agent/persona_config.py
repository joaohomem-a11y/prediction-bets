"""
Demographic distribution rules and special characters for persona generation.
"""

DISTRIBUTION = {
    "total": 300,
    "gender": {"male": 0.70, "female": 0.30},
    "language": {"en": 0.40, "pt": 0.30, "es": 0.20, "other": 0.10},
    "age_range": {"min": 18, "max": 65, "peak_min": 25, "peak_max": 45},
    "market_knowledge": {
        "beginner": 0.30,
        "intermediate": 0.30,
        "advanced": 0.25,
        "guru": 0.15,
    },
    "financial_level": [
        "student",
        "working-class",
        "middle-class",
        "upper-middle",
        "wealthy",
    ],
    "education": [
        "high-school",
        "some-college",
        "bachelors",
        "masters",
        "MBA",
        "PhD",
        "self-taught",
    ],
}

# Nationalities mapped to languages
NATIONALITIES = {
    "en": ["US", "UK", "CA", "AU", "IE", "NZ", "ZA", "NG", "KE", "IN", "PH", "SG"],
    "pt": ["BR", "PT", "AO", "MZ"],
    "es": ["MX", "AR", "CO", "ES", "CL", "PE", "VE", "EC", "UY"],
    "other": ["DE", "FR", "JP", "KR", "IT", "NL", "SE", "PL", "TR", "IL", "AE", "TH"],
}

FORUM_SECTIONS = [
    "signal-drop",
    "contrarian-takes",
    "prediction-battles",
    "reality-check",
    "edge-lab",
    "off-market",
]

PERSONALITY_TRAITS = [
    "analytical", "impulsive", "cautious", "data-driven", "intuitive",
    "opinionated", "diplomatic", "sarcastic", "helpful", "contrarian",
    "optimistic", "pessimistic", "risk-taker", "conservative", "meme-lord",
    "philosophical", "pragmatic", "aggressive-trader", "passive-observer",
    "storyteller", "technical", "emotional", "skeptical", "enthusiastic",
]

INTERESTS = [
    "crypto", "politics", "sports-betting", "geopolitics", "AI-tech",
    "macro-economics", "climate", "elections", "entertainment",
    "science", "esports", "real-estate", "commodities", "culture",
]

SGT_PEIXOTO = {
    "id": "sargento-peixoto",
    "name": "Sargento Peixoto",
    "username": "sgt_peixoto",
    "nationality": "BR",
    "language": "pt",
    "languages": ["pt", "en", "es"],
    "gender": "male",
    "age": 52,
    "education": "military-academy",
    "financial_level": "upper-middle",
    "market_knowledge": "guru",
    "role": "moderator",
    "personality_traits": ["firm", "paternal", "educational", "fair", "dry-humor"],
    "interests": ["geopolitics", "macro-economics", "risk-management", "community"],
    "writing_style": "Firm and direct, uses military metaphors occasionally. Always respectful but doesn't tolerate nonsense. Explains complex concepts simply. Switches between PT, EN, and ES depending on who he's talking to.",
    "backstory": "Brazilian ex-military officer who served 25 years, discovered prediction markets during geopolitical analysis work. Now retired, dedicates time to educating newcomers about probabilistic thinking and risk management. Believes prediction markets are the most honest information tool ever created."
}
