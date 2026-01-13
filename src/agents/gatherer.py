"""News gathering agent for specific domains."""

import json
import time
from datetime import datetime
from typing import Optional

from src.agents.base import BaseNewsAgent
from src.models.article import (
    AgentType,
    Article,
    AgentResult,
    CredibilityTier,
)
from src.utils.file_logger import get_logger


class GathererAgent(BaseNewsAgent):
    """News gathering agent for a specific domain."""

    def __init__(
        self,
        client,
        agent_type: AgentType,
        prompt_template: str,
        max_searches: int = 5,
    ):
        super().__init__(
            client, name=f"Gatherer-{agent_type.value}", model="claude-sonnet-4-5-20250929"
        )
        self.agent_type = agent_type
        self.prompt_template = prompt_template
        self.max_searches = max_searches

    async def execute(self) -> AgentResult:
        """Gather news articles in this domain."""
        logger = get_logger()
        start_time = time.time()

        result = AgentResult(agent_name=self.name)

        logger.info(f"\n{'='*60}")
        logger.info(f"Starting {self.name}")
        logger.info(f"{'='*60}")

        try:
            # Prepare tools
            tools = [
                {
                    "type": "web_search_20250305",
                    "name": "web_search",
                    "max_uses": self.max_searches,
                }
            ]

            # Format prompt
            prompt = self._format_prompt(self.prompt_template)
            logger.debug(f"{self.name} - Prompt length: {len(prompt)} chars")

            # Call Claude
            logger.info(f"{self.name} - Calling Claude API...")
            response = await self._call_claude(prompt, tools=tools)
            logger.info(f"{self.name} - Response received (stop_reason: {response.stop_reason})")

            # Track search usage
            if hasattr(response, "usage") and hasattr(response.usage, "server_tool_use"):
                server_tool_use = response.usage.server_tool_use
                if hasattr(server_tool_use, "web_search_requests"):
                    result.search_count = server_tool_use.web_search_requests
                    logger.info(f"{self.name} - Performed {result.search_count} web searches")

            # Parse response
            logger.info(f"{self.name} - Parsing response...")
            articles = self._parse_articles(response)
            result.articles = articles
            result.success = True
            logger.info(f"{self.name} - Successfully parsed {len(articles)} articles")

        except Exception as e:
            result.success = False
            result.error_message = str(e)
            logger.error(f"{self.name} - FAILED: {str(e)}")

        finally:
            result.execution_time_seconds = time.time() - start_time
            logger.info(f"{self.name} - Completed in {result.execution_time_seconds:.2f}s")

        return result

    def _parse_articles(self, response) -> list[Article]:
        """Extract articles from Claude's response."""
        logger = get_logger()
        articles = []

        # Extract text content
        text_parts = []
        for block in response.content:
            if hasattr(block, "text"):
                text_parts.append(block.text)

        full_text = "".join(text_parts)

        logger.debug(f"{self.name} - Raw response length: {len(full_text)} chars")
        logger.debug(f"{self.name} - Raw response (first 500 chars):\n{full_text[:500]}")

        # Strip markdown code blocks if present
        original_text = full_text
        full_text = full_text.strip()
        if full_text.startswith("```"):
            logger.debug(f"{self.name} - Detected markdown code block, stripping...")
            # Remove opening ```json or ```
            lines = full_text.split("\n")
            lines = lines[1:]  # Remove first line
            # Remove closing ```
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            full_text = "\n".join(lines)
            logger.debug(f"{self.name} - After stripping (first 500 chars):\n{full_text[:500]}")

        # Extract JSON object if there's surrounding text
        full_text = full_text.strip()
        if not full_text.startswith("{"):
            logger.debug(f"{self.name} - Response doesn't start with '{{', attempting to extract JSON object...")
            # Find the first { and last }
            start_idx = full_text.find("{")
            end_idx = full_text.rfind("}")
            if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                full_text = full_text[start_idx:end_idx + 1]
                logger.debug(f"{self.name} - Extracted JSON object (first 500 chars):\n{full_text[:500]}")
            else:
                logger.error(f"{self.name} - Could not find JSON object in response")

        # Parse JSON response (expected format)
        try:
            logger.debug(f"{self.name} - Attempting to parse JSON...")
            data = json.loads(full_text)
            logger.debug(f"{self.name} - JSON parsed successfully, found {len(data.get('articles', []))} articles")

            for item in data.get("articles", []):
                article = Article(
                    title=item["title"],
                    summary=item["summary"],
                    source_url=item["source_url"],
                    credibility_tier=CredibilityTier(item.get("credibility_tier", 3)),
                    published_date=self._parse_date(item.get("published_date")),
                    gathered_by_agent=self.name,
                )
                articles.append(article)
                logger.debug(f"{self.name} - Parsed article: {article.title}")

        except json.JSONDecodeError as e:
            # Log the full response for debugging
            logger.error(f"{self.name} - JSON parsing failed!")
            logger.error(f"{self.name} - Error: {str(e)}")
            logger.error(f"{self.name} - Full raw response:\n{original_text}")
            logger.error(f"{self.name} - After cleanup:\n{full_text}")
            # Re-raise with more context for debugging
            raise ValueError(f"Failed to parse JSON: {str(e)}\nContent: {full_text[:200]}")

        return articles

    def _parse_date(self, date_str: Optional[str]) -> Optional[datetime]:
        """Parse date string to datetime."""
        if not date_str:
            return None

        # Try common formats
        formats = [
            "%Y-%m-%d",
            "%Y-%m-%dT%H:%M:%S",
            "%B %d, %Y",
        ]

        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue

        return None
