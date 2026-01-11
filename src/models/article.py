"""Data models for the news aggregator multi-agent system."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4


class CredibilityTier(Enum):
    """Source credibility classification."""

    PRIMARY = 1  # Official sources, primary documents
    MAJOR = 2  # Established news outlets
    ALTERNATIVE = 3  # Blogs, social media, unverified


class NewsCategory(Enum):
    """News domain categories."""

    # Mainstream
    POLITICS = "politics_policy"
    BUSINESS = "business_markets"
    SPORTS = "sports"
    ENTERTAINMENT = "entertainment"
    WORLD = "world_affairs"
    VIRAL = "viral_cultural"

    # Deep cuts
    MEDICAL = "medical_research"
    SCIENCE = "scientific_discoveries"
    REGULATORY = "regulatory_filings"
    FINANCIAL = "financial_filings"
    LEGAL = "legal_courts"
    CLIMATE = "climate_environment"
    SPACE = "space_aerospace"
    AI_TECH = "ai_emerging_tech"

    # Meta
    CORRECTIONS = "corrections_retractions"


@dataclass
class Article:
    """Single news article with metadata."""

    # Unique identifier
    uuid: UUID = field(default_factory=uuid4)

    # Core content
    title: str = ""
    summary: str = ""  # 2-3 sentences
    source_url: str = ""

    # Metadata
    category: NewsCategory = NewsCategory.WORLD
    credibility_tier: CredibilityTier = CredibilityTier.ALTERNATIVE
    published_date: Optional[datetime] = None

    # Attribution
    gathered_by_agent: str = ""  # Which agent found this

    def __post_init__(self):
        """Validation after initialization."""
        if not self.title or not self.summary:
            raise ValueError("Article must have title and summary")
        if not self.source_url.startswith(("http://", "https://")):
            raise ValueError(f"Invalid source URL: {self.source_url}")


@dataclass
class AgentResult:
    """Result from a single gathering agent."""

    agent_name: str
    category: NewsCategory
    articles: list[Article] = field(default_factory=list)

    # Performance metrics
    execution_time_seconds: float = 0.0
    search_count: int = 0

    # Error tracking
    success: bool = True
    error_message: Optional[str] = None

    def __len__(self) -> int:
        """Number of articles found."""
        return len(self.articles)


@dataclass
class CurationResult:
    """Result from curator agent."""

    selected_uuids: list[UUID] = field(default_factory=list)
    reasoning: str = ""  # Why these articles were selected

    execution_time_seconds: float = 0.0
    success: bool = True
    error_message: Optional[str] = None


@dataclass
class BuildResult:
    """Result from webpage builder agent."""

    html_content: str = ""
    design_rationale: str = ""  # Aesthetic choice explanation

    execution_time_seconds: float = 0.0
    success: bool = True
    error_message: Optional[str] = None


@dataclass
class PipelineState:
    """Complete state of the news generation pipeline."""

    # Stage 1: Gathering
    agent_results: list[AgentResult] = field(default_factory=list)

    # Stage 2: Curation
    curation_result: Optional[CurationResult] = None

    # Stage 3: Building
    build_result: Optional[BuildResult] = None

    # Metadata
    started_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None

    @property
    def all_articles(self) -> list[Article]:
        """Flatten all articles from all agents."""
        articles = []
        for result in self.agent_results:
            articles.extend(result.articles)
        return articles

    @property
    def selected_articles(self) -> list[Article]:
        """Get articles selected by curator."""
        if not self.curation_result:
            return []

        selected_uuids = set(self.curation_result.selected_uuids)
        return [a for a in self.all_articles if a.uuid in selected_uuids]

    @property
    def total_articles_gathered(self) -> int:
        """Total articles from all agents."""
        return len(self.all_articles)

    @property
    def successful_agents(self) -> int:
        """Number of agents that completed successfully."""
        return sum(1 for r in self.agent_results if r.success)

    @property
    def failed_agents(self) -> int:
        """Number of agents that failed."""
        return sum(1 for r in self.agent_results if not r.success)
