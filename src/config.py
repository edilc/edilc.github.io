"""Configuration for the news generator."""

import os
from dataclasses import dataclass


@dataclass
class Config:
    """Configuration for the news generator."""

    # API credentials
    anthropic_api_key: str

    # Agent settings
    max_searches_per_agent: int = 5

    # File paths
    original_prompt_path: str = "prompt.txt"

    # Models
    gatherer_model: str = "claude-sonnet-4-5-20250929"
    curator_model: str = "claude-opus-4-5-20251101"
    builder_model: str = "claude-sonnet-4-5-20250929"

    @classmethod
    def from_env(cls) -> "Config":
        """Load configuration from environment variables."""
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")

        return cls(
            anthropic_api_key=api_key,
            max_searches_per_agent=int(os.environ.get("MAX_SEARCHES", "3")),
            original_prompt_path=os.environ.get("PROMPT_PATH", "prompt.txt"),
        )
