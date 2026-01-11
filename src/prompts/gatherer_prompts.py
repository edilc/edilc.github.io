"""Prompt templates for each gathering agent."""

from src.models.article import NewsCategory

# Base template used by all gatherers
GATHERER_BASE = """Today is {today}.

You are a specialized news gathering agent for {category_name}.

Your task:
1. Search for recent news (last 24 hours preferred) in your domain
2. Find 5-10 high-quality articles
3. Return results in JSON format

Focus areas for {category_name}:
{focus_areas}

Output format (JSON only, no other text):
{{{{
  "articles": [
    {{{{
      "title": "Article headline",
      "summary": "2-3 sentence summary of the article",
      "source_url": "https://...",
      "credibility_tier": 1-3 (1=official/primary, 2=major outlet, 3=blog/social),
      "published_date": "YYYY-MM-DD or null"
    }}}}
  ]
}}}}

Prioritize:
- Recent articles (last 24h)
- Diverse sources
- Credible outlets
- Interesting/significant stories
"""


# Domain-specific configurations
GATHERER_CONFIGS = {
    NewsCategory.POLITICS: {
        "category_name": "Politics & Policy",
        "focus_areas": """
        - Federal/state legislation
        - Political campaigns and elections
        - Policy debates and proposals
        - Government appointments
        - Congressional actions
        """,
    },
    NewsCategory.BUSINESS: {
        "category_name": "Business & Markets",
        "focus_areas": """
        - Stock market movements
        - Major corporate announcements
        - Earnings reports
        - Mergers and acquisitions
        - Economic indicators
        """,
    },
    NewsCategory.SPORTS: {
        "category_name": "Sports",
        "focus_areas": """
        - Game results and highlights
        - Player trades and signings
        - Championships and tournaments
        - Sports controversies
        - Record-breaking performances
        """,
    },
    NewsCategory.ENTERTAINMENT: {
        "category_name": "Entertainment",
        "focus_areas": """
        - Movie and TV releases
        - Celebrity news
        - Awards shows
        - Music releases
        - Entertainment industry news
        """,
    },
    NewsCategory.WORLD: {
        "category_name": "World Affairs",
        "focus_areas": """
        - International conflicts
        - Diplomatic relations
        - Global crises
        - International policy
        - Cross-border events
        """,
    },
    NewsCategory.VIRAL: {
        "category_name": "Viral & Cultural",
        "focus_areas": """
        - Trending social media stories
        - Internet phenomena
        - Cultural moments
        - Memes and viral content
        - Pop culture trends
        """,
    },
    NewsCategory.MEDICAL: {
        "category_name": "Medical Research",
        "focus_areas": """
        - Clinical trial results
        - New treatments and therapies
        - Disease research
        - Public health studies
        - Medical breakthroughs
        """,
    },
    NewsCategory.SCIENCE: {
        "category_name": "Scientific Discoveries",
        "focus_areas": """
        - Research publications
        - Scientific breakthroughs
        - Physics, chemistry, biology discoveries
        - Academic research
        - Scientific controversies
        """,
    },
    NewsCategory.REGULATORY: {
        "category_name": "Regulatory Filings",
        "focus_areas": """
        - SEC filings
        - FCC announcements
        - EPA regulations
        - FDA approvals/warnings
        - Government regulatory actions
        """,
    },
    NewsCategory.FINANCIAL: {
        "category_name": "Financial Filings",
        "focus_areas": """
        - Corporate financial disclosures
        - Bankruptcy filings
        - Major financial statements
        - Insider trading reports
        - Financial regulatory actions
        """,
    },
    NewsCategory.LEGAL: {
        "category_name": "Legal & Court Decisions",
        "focus_areas": """
        - Supreme Court rulings
        - Major court cases
        - Legal precedents
        - Corporate lawsuits
        - Criminal justice news
        """,
    },
    NewsCategory.CLIMATE: {
        "category_name": "Climate & Environment",
        "focus_areas": """
        - Climate research
        - Environmental policy
        - Natural disasters
        - Conservation efforts
        - Renewable energy
        """,
    },
    NewsCategory.SPACE: {
        "category_name": "Space & Aerospace",
        "focus_areas": """
        - Space missions
        - Astronomical discoveries
        - Satellite launches
        - Space exploration
        - Aerospace technology
        """,
    },
    NewsCategory.AI_TECH: {
        "category_name": "AI & Emerging Tech",
        "focus_areas": """
        - AI developments
        - Machine learning breakthroughs
        - Emerging technologies
        - Tech policy
        - Future tech trends
        """,
    },
    NewsCategory.CORRECTIONS: {
        "category_name": "Corrections & Retractions",
        "focus_areas": """
        - Media corrections
        - Story retractions
        - Fact-check updates
        - Clarifications on major stories
        - Journalistic accountability
        """,
    },
}


def get_gatherer_prompt(category: NewsCategory) -> str:
    """Get the prompt template for a specific category."""
    config = GATHERER_CONFIGS[category]
    return GATHERER_BASE.format(
        category_name=config["category_name"],
        focus_areas=config["focus_areas"],
        today="{today}",  # Keep for later formatting
    )
