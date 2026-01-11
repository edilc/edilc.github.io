"""Builder agent that creates the final HTML webpage."""

import time

from src.agents.base import BaseNewsAgent
from src.models.article import Article, BuildResult


class BuilderAgent(BaseNewsAgent):
    """Sonnet agent that builds the final HTML webpage."""

    def __init__(self, client, prompt_template: str):
        super().__init__(
            client, name="Builder-Sonnet", model="claude-sonnet-4-5-20250929"
        )
        self.prompt_template = prompt_template

    async def execute(self, articles: list[Article]) -> BuildResult:
        """Build the final HTML webpage."""
        start_time = time.time()

        result = BuildResult()

        try:
            # Format articles for the prompt
            article_data = self._format_articles(articles)

            # Format prompt
            prompt = self._format_prompt(self.prompt_template, articles=article_data)

            # Call Claude (no web search, higher token limit for HTML)
            response = await self._call_claude(prompt, max_tokens=16000)

            # Extract HTML
            html_content = self._extract_html(response)
            result.html_content = html_content
            result.success = True

        except Exception as e:
            result.success = False
            result.error_message = str(e)

        finally:
            result.execution_time_seconds = time.time() - start_time

        return result

    def _format_articles(self, articles: list[Article]) -> str:
        """Format articles for the builder prompt."""
        lines = []

        for i, article in enumerate(articles, 1):
            lines.append(
                f"Article {i}:\n"
                f"Title: {article.title}\n"
                f"Summary: {article.summary}\n"
                f"Source: {article.source_url}\n"
                f"Category: {article.category.value}\n"
                f"---"
            )

        return "\n".join(lines)

    def _extract_html(self, response) -> str:
        """Extract HTML from response."""
        text_parts = []
        for block in response.content:
            if hasattr(block, "text"):
                text_parts.append(block.text)

        full_response = "".join(text_parts)

        # Strip everything before <!DOCTYPE html>
        doctype_index = full_response.find("<!DOCTYPE html>")
        if doctype_index != -1:
            return full_response[doctype_index:]

        return full_response
