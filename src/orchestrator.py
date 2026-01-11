"""Orchestrates the three-stage news generation pipeline."""

import asyncio
import random

from anthropic import Anthropic
from rich.console import Console
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TaskProgressColumn,
    TextColumn,
)

from src.agents.builder import BuilderAgent
from src.agents.curator import CuratorAgent
from src.agents.gatherer import GathererAgent
from src.config import Config
from src.models.article import AgentResult, NewsCategory, PipelineState
from src.prompts.builder_prompt import get_builder_prompt_template
from src.prompts.curator_prompt import CURATOR_PROMPT
from src.prompts.gatherer_prompts import get_gatherer_prompt
from src.utils.file_logger import setup_file_logger, get_logger


class NewsOrchestrator:
    """Orchestrates the three-stage news generation pipeline."""

    def __init__(self, config: Config, console: Console):
        self.config = config
        self.console = console
        self.client = Anthropic(api_key=config.anthropic_api_key)
        self.state = PipelineState()
        # Set up file logging
        self.logger = setup_file_logger("generation.log")
        self.logger.info("NewsOrchestrator initialized")

    async def run(self) -> str:
        """Execute the full pipeline and return HTML."""

        # Stage 1: Gather news
        await self._stage_1_gather()

        # Check if we have enough articles
        if self.state.total_articles_gathered < 10:
            raise ValueError(
                f"Insufficient articles gathered: {self.state.total_articles_gathered} "
                f"(need at least 10)"
            )

        # Wait before Stage 2 to avoid rate limits
        await self._wait_between_stages(1, 2)

        # Stage 2: Curate
        await self._stage_2_curate()

        # Wait before Stage 3 to avoid rate limits
        await self._wait_between_stages(2, 3)

        # Stage 3: Build webpage
        await self._stage_3_build()

        if not self.state.build_result or not self.state.build_result.success:
            raise ValueError("Failed to build webpage")

        return self.state.build_result.html_content

    async def _wait_between_stages(self, from_stage: int, to_stage: int):
        """Wait 1-2 minutes between stages to avoid rate limits."""
        wait_seconds = random.randint(60, 120)
        self.console.print(
            f"\n[yellow]Waiting {wait_seconds}s before Stage {to_stage} "
            f"to avoid rate limits...[/yellow]"
        )
        self.logger.info(
            f"Waiting {wait_seconds}s between Stage {from_stage} and Stage {to_stage}"
        )
        await asyncio.sleep(wait_seconds)

    async def _stage_1_gather(self):
        """Stage 1: Run 15 gatherer agents in parallel."""
        self.console.print("\n[bold cyan]Stage 1: Gathering News[/bold cyan]")
        self.console.print("Launching 15 agents in parallel...\n")

        # Create all 15 agents
        agents = []
        for category in NewsCategory:
            prompt = get_gatherer_prompt(category)
            agent = GathererAgent(
                client=self.client,
                category=category,
                prompt_template=prompt,
                max_searches=self.config.max_searches_per_agent,
            )
            agents.append(agent)

        # Run all agents in parallel with progress tracking
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=self.console,
        ) as progress:

            task = progress.add_task(
                "[cyan]Gathering news from 15 agents...", total=len(agents)
            )

            # Execute all agents
            results = await asyncio.gather(
                *[agent.execute() for agent in agents], return_exceptions=True
            )

            # Process results
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    # Agent failed - create error result
                    agent = agents[i]
                    error_result = AgentResult(
                        agent_name=agent.name,
                        category=agent.category,
                        success=False,
                        error_message=str(result),
                    )
                    self.state.agent_results.append(error_result)
                else:
                    self.state.agent_results.append(result)

                progress.update(task, advance=1)

        # Summary
        self._print_stage_1_summary()

    def _print_stage_1_summary(self):
        """Print summary of gathering stage."""
        self.console.print("\n[bold]Stage 1 Complete[/bold]")
        self.console.print(f"  Total articles: {self.state.total_articles_gathered}")
        self.console.print(
            f"  Successful agents: {self.state.successful_agents}/15"
        )
        self.console.print(f"  Failed agents: {self.state.failed_agents}/15")

        if self.state.failed_agents > 0:
            self.console.print("\n[yellow]Failed agents:[/yellow]")
            for result in self.state.agent_results:
                if not result.success:
                    self.console.print(
                        f"  - {result.agent_name}: {result.error_message}"
                    )

        # Show per-category breakdown
        self.console.print("\n[dim]Articles by category:[/dim]")
        for result in sorted(
            self.state.agent_results, key=lambda r: len(r), reverse=True
        ):
            if result.success:
                self.console.print(
                    f"  {result.category.value}: {len(result)} articles "
                    f"({result.search_count} searches, {result.execution_time_seconds:.1f}s)"
                )

    async def _stage_2_curate(self):
        """Stage 2: Curate articles with Opus."""
        self.console.print("\n[bold cyan]Stage 2: Curating Articles[/bold cyan]")

        curator = CuratorAgent(client=self.client, prompt_template=CURATOR_PROMPT)

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console,
        ) as progress:

            progress.add_task("[cyan]Opus is reviewing all articles...")

            result = await curator.execute(self.state.all_articles)
            self.state.curation_result = result

        # Summary
        if result.success:
            self.console.print("\n[bold]Stage 2 Complete[/bold]")
            self.console.print(f"  Selected: {len(result.selected_uuids)} articles")
            self.console.print(f"  Time: {result.execution_time_seconds:.1f}s")
            self.console.print(f"  Reasoning: {result.reasoning}")
        else:
            self.console.print(f"\n[red]Stage 2 Failed: {result.error_message}[/red]")
            raise ValueError("Curation failed")

    async def _stage_3_build(self):
        """Stage 3: Build webpage with Sonnet."""
        self.console.print("\n[bold cyan]Stage 3: Building Webpage[/bold cyan]")

        # Load builder prompt template
        builder_prompt = get_builder_prompt_template(
            self.config.original_prompt_path
        )

        builder = BuilderAgent(client=self.client, prompt_template=builder_prompt)

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console,
        ) as progress:

            progress.add_task("[cyan]Generating HTML webpage...")

            result = await builder.execute(self.state.selected_articles)
            self.state.build_result = result

        # Summary
        if result.success:
            self.console.print("\n[bold]Stage 3 Complete[/bold]")
            self.console.print(f"  HTML size: {len(result.html_content)} characters")
            self.console.print(f"  Time: {result.execution_time_seconds:.1f}s")
        else:
            self.console.print(f"\n[red]Stage 3 Failed: {result.error_message}[/red]")
            raise ValueError("Build failed")
