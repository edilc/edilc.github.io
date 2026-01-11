"""Curator agent that selects the best articles using Opus."""

import json
import time
from uuid import UUID

from src.agents.base import BaseNewsAgent
from src.models.article import Article, CurationResult
from src.utils.file_logger import get_logger


class CuratorAgent(BaseNewsAgent):
    """Opus agent that selects the best articles."""

    def __init__(self, client, prompt_template: str):
        super().__init__(
            client, name="Curator-Opus", model="claude-opus-4-5-20251101"  # Use Opus
        )
        self.prompt_template = prompt_template

    async def execute(self, articles: list[Article]) -> CurationResult:
        """Select and order the best articles."""
        logger = get_logger()
        start_time = time.time()

        result = CurationResult()

        logger.info(f"\n{'='*60}")
        logger.info(f"Starting {self.name}")
        logger.info(f"{'='*60}")
        logger.info(f"{self.name} - Curating from {len(articles)} articles")

        try:
            # Build article index for the prompt
            article_index = self._build_article_index(articles)

            # Format prompt with articles
            prompt = self._format_prompt(
                self.prompt_template,
                article_count=len(articles),
                article_index=article_index,
            )
            logger.debug(f"{self.name} - Prompt length: {len(prompt)} chars")

            # Call Claude Opus (no web search needed)
            logger.info(f"{self.name} - Calling Claude Opus...")
            response = await self._call_claude(prompt, max_tokens=4000)
            logger.info(f"{self.name} - Response received (stop_reason: {response.stop_reason})")

            # Parse response
            logger.info(f"{self.name} - Parsing selection...")
            selected_data = self._parse_selection(response)
            result.selected_uuids = selected_data["uuids"]
            result.reasoning = selected_data["reasoning"]
            result.success = True
            logger.info(f"{self.name} - Successfully selected {len(result.selected_uuids)} articles")

        except Exception as e:
            result.success = False
            result.error_message = str(e)
            logger.error(f"{self.name} - FAILED: {str(e)}")

        finally:
            result.execution_time_seconds = time.time() - start_time
            logger.info(f"{self.name} - Completed in {result.execution_time_seconds:.2f}s")

        return result

    def _build_article_index(self, articles: list[Article]) -> str:
        """Build a compact article index for the prompt."""
        lines = []

        for article in articles:
            lines.append(
                f"UUID: {article.uuid}\n"
                f"Title: {article.title}\n"
                f"Summary: {article.summary}\n"
                f"Category: {article.category.value}\n"
                f"Credibility: Tier {article.credibility_tier.value}\n"
                f"Published: {article.published_date or 'Unknown'}\n"
                f"---"
            )

        return "\n".join(lines)

    def _parse_selection(self, response) -> dict:
        """Extract selected UUIDs and reasoning."""
        logger = get_logger()
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
            lines = full_text.split("\n")
            lines = lines[1:]  # Remove first line (```json)
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]  # Remove last line (```)
            full_text = "\n".join(lines)
            logger.debug(f"{self.name} - After stripping (first 500 chars):\n{full_text[:500]}")

        # Parse JSON response
        try:
            logger.debug(f"{self.name} - Attempting to parse JSON...")
            data = json.loads(full_text)
            logger.debug(f"{self.name} - JSON parsed successfully")
            logger.debug(f"{self.name} - Found {len(data.get('selected_uuids', []))} UUIDs")

            # Parse UUIDs with better error handling
            uuids = []
            for i, u in enumerate(data["selected_uuids"]):
                try:
                    uuids.append(UUID(u))
                except (ValueError, AttributeError) as e:
                    logger.error(f"{self.name} - Invalid UUID at index {i}: '{u}' - Error: {e}")
                    # Continue processing other UUIDs instead of failing completely
                    continue

            if not uuids:
                logger.error(f"{self.name} - No valid UUIDs parsed!")
                logger.error(f"{self.name} - Raw UUID list: {data.get('selected_uuids', [])}")
                raise ValueError("No valid UUIDs found in curator response")

            logger.info(f"{self.name} - Successfully parsed {len(uuids)} valid UUIDs")

            return {
                "uuids": uuids,
                "reasoning": data.get("reasoning", ""),
            }
        except json.JSONDecodeError as e:
            logger.error(f"{self.name} - JSON parsing failed!")
            logger.error(f"{self.name} - Error: {str(e)}")
            logger.error(f"{self.name} - Full raw response:\n{original_text}")
            logger.error(f"{self.name} - After cleanup:\n{full_text}")
            raise
