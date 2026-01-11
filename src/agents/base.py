"""Base class for all news agents."""

import asyncio
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Optional

from anthropic import Anthropic


class BaseNewsAgent(ABC):
    """Abstract base class for all news agents."""

    def __init__(
        self, client: Anthropic, name: str, model: str = "claude-sonnet-4-5-20250929"
    ):
        self.client = client
        self.name = name
        self.model = model

    @abstractmethod
    async def execute(self, *args, **kwargs) -> Any:
        """Execute the agent's task."""
        pass

    def _format_prompt(self, template: str, **kwargs) -> str:
        """Format a prompt template with date and custom variables."""
        today = datetime.now().strftime("%B %d, %Y")
        return template.format(today=today, **kwargs)

    async def _call_claude(
        self,
        prompt: str,
        tools: Optional[list] = None,
        max_tokens: int = 8000,
    ) -> Any:
        """Make an async API call to Claude."""
        messages = [{"role": "user", "content": prompt}]

        kwargs = {
            "model": self.model,
            "max_tokens": max_tokens,
            "messages": messages,
        }

        if tools:
            kwargs["tools"] = tools

        # Anthropic SDK doesn't have native async, so wrap in executor
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None, lambda: self.client.messages.create(**kwargs)
        )

        return response
