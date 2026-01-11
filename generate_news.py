#!/usr/bin/env python3
"""Generate a news webpage using multi-agent Claude AI system."""

import asyncio
from datetime import datetime

import typer

from src.config import Config
from src.orchestrator import NewsOrchestrator
from src.utils.logging import create_console, log_metrics

app = typer.Typer()


async def generate_news_webpage(config: Config) -> str:
    """Generate news webpage using multi-agent pipeline."""
    console = create_console()

    console.print("[bold cyan]News.sys Multi-Agent Generator[/bold cyan]")
    console.print(f"[dim]Date: {datetime.now().strftime('%B %d, %Y')}[/dim]")
    console.print(
        "[dim]Using Opus for curation, Sonnet for gathering & building[/dim]\n"
    )

    # Create orchestrator
    orchestrator = NewsOrchestrator(config, console)

    # Run pipeline
    try:
        html_content = await orchestrator.run()

        # Final summary
        console.print("\n[bold green]✓ Generation Complete![/bold green]")

        # Metrics
        state = orchestrator.state
        metrics = {
            "Total articles gathered": state.total_articles_gathered,
            "Successful agents": f"{state.successful_agents}/15",
            "Failed agents": f"{state.failed_agents}/15",
            "Articles selected": len(state.selected_articles),
            "HTML size": f"{len(html_content)} chars",
        }
        log_metrics(console, metrics)

        return html_content

    except Exception as e:
        console.print(f"\n[error]Pipeline failed: {e}[/error]")
        raise


@app.command()
def main():
    """Generate today's news webpage using multi-agent Claude AI."""
    console = create_console()

    try:
        # Load configuration
        config = Config.from_env()

        # Run async pipeline
        html_content = asyncio.run(generate_news_webpage(config))

        if html_content:
            # Output to stdout (everything else goes to stderr)
            print(html_content)
        else:
            raise typer.Exit(1)

    except KeyboardInterrupt:
        console.print("\n[warning]Cancelled by user[/warning]")
        raise typer.Exit(130)

    except Exception as e:
        console.print(f"[error]Error: {e}[/error]")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()