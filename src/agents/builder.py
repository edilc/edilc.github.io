"""Builder agent that creates the final HTML webpage."""

import time
from xml.sax.saxutils import escape

from src.agents.base import BaseNewsAgent
from src.models.article import Article, BuildResult


class BuilderAgent(BaseNewsAgent):
    """Sonnet agent that builds the final HTML webpage."""

    def __init__(
        self,
        client,
        prompt_template: str,
        recent_designs: str = "",
        creative_nudge: str = "",
    ):
        super().__init__(
            client, name="Builder-Sonnet", model="claude-sonnet-4-5-20250929"
        )
        self.prompt_template = prompt_template
        self.recent_designs = recent_designs
        self.creative_nudge = creative_nudge

    async def execute(self, articles: list[Article]) -> BuildResult:
        """Build the final HTML webpage."""
        start_time = time.time()

        result = BuildResult()

        try:
            # Format articles for the prompt
            article_data = self._format_articles(articles)

            # Format prompt with articles, memory, and nudge
            prompt = self._format_prompt(
                self.prompt_template,
                articles=article_data,
                recent_designs=self.recent_designs,
                creative_nudge=self.creative_nudge,
            )

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
        """Format articles in XML format for the builder prompt."""
        lines = ["<articles>"]

        for article in articles:
            # Extract source name from URL for display
            source_name = self._extract_source_name(article.source_url)

            lines.append("  <article>")
            lines.append(f"    <headline>{escape(article.title)}</headline>")
            lines.append(f"    <source>{escape(source_name)}</source>")
            lines.append(f"    <url>{escape(article.source_url)}</url>")
            lines.append(f"    <summary>{escape(article.summary)}</summary>")
            lines.append("  </article>")

        lines.append("</articles>")
        return "\n".join(lines)

    def _extract_source_name(self, url: str) -> str:
        """Extract a readable source name from a URL."""
        try:
            # Remove protocol
            url = url.replace("https://", "").replace("http://", "")
            # Get domain
            domain = url.split("/")[0]
            # Remove www.
            domain = domain.replace("www.", "")
            # Capitalize first letter
            return domain.split(".")[0].capitalize()
        except Exception:
            return url

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
