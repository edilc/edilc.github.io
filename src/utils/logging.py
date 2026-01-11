"""Logging utilities using Rich console."""

from datetime import datetime

from rich.console import Console
from rich.theme import Theme


# Custom theme for news.sys
NEWS_THEME = Theme(
    {
        "info": "cyan",
        "success": "green",
        "warning": "yellow",
        "error": "red bold",
        "stage": "bold cyan",
        "metric": "blue",
        "dim": "dim",
    }
)


def create_console() -> Console:
    """Create a Rich console with custom theme."""
    return Console(stderr=True, theme=NEWS_THEME)


def log_stage_start(console: Console, stage_num: int, stage_name: str):
    """Log the start of a pipeline stage."""
    console.print(f"\n[stage]Stage {stage_num}: {stage_name}[/stage]")
    console.print(f"[dim]Started at {datetime.now().strftime('%H:%M:%S')}[/dim]\n")


def log_metrics(console: Console, metrics: dict):
    """Log performance metrics."""
    console.print("\n[bold]Metrics:[/bold]")
    for key, value in metrics.items():
        console.print(f"  [metric]{key}:[/metric] {value}")
