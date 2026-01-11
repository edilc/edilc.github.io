#!/usr/bin/env python3
"""Generate a news webpage using Claude AI with web search capabilities."""

import asyncio
import os
from datetime import datetime

import typer
from anthropic import Anthropic
from rich.console import Console

app = typer.Typer()
console = Console(stderr=True)


async def generate_news_webpage() -> str:
    """Generate a news webpage using Claude with official web search tool."""

    # Get API key from environment
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        console.print(
            "[red]Error: ANTHROPIC_API_KEY environment variable not set[/red]"
        )
        raise typer.Exit(1)

    # Initialize Anthropic client
    client = Anthropic(api_key=api_key)

    # Use Anthropic's official web search tool
    tools = [
        {
            "type": "web_search_20250305",
            "name": "web_search",
            "max_uses": 10,  # Allow up to 10 searches for comprehensive news coverage
        }
    ]

    # Initial prompt to Claude
    today = datetime.now().strftime("%B %d, %Y")

    # Read prompt from prompt.txt
    prompt_file = os.path.join(os.path.dirname(__file__), "prompt.txt")
    try:
        with open(prompt_file, "r") as f:
            prompt_template = f.read()
    except FileNotFoundError:
        console.print("[red]Error: prompt.txt not found[/red]")
        raise typer.Exit(1)

    initial_prompt = f"Today is {today}.\n\n{prompt_template}"

    messages = [{"role": "user", "content": initial_prompt}]

    console.print("[cyan]Sending request to Claude with web search enabled...[/cyan]", style="dim")

    # Make the API call - the API handles all web searches automatically
    response = client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=16000,
        tools=tools,
        messages=messages,
    )

    console.print(f"[dim]Response received (stop_reason: {response.stop_reason})[/dim]")

    # Log search usage
    if hasattr(response, "usage") and hasattr(response.usage, "server_tool_use"):
        server_tool_use = response.usage.server_tool_use
        if hasattr(server_tool_use, "web_search_requests"):
            search_count = server_tool_use.web_search_requests
            console.print(f"[green]Completed {search_count} web searches[/green]", style="dim")

    # Extract the HTML content
    console.print("[green]Generation complete![/green]", style="dim")

    # Combine all text blocks
    html_parts = []
    for block in response.content:
        if hasattr(block, "text"):
            html_parts.append(block.text)

    if html_parts:
        full_response = "".join(html_parts)

        # Strip everything before <!DOCTYPE html>
        doctype_index = full_response.find("<!DOCTYPE html>")
        if doctype_index != -1:
            return full_response[doctype_index:]
        else:
            console.print("[yellow]Warning: No <!DOCTYPE html> found, returning full response[/yellow]", style="dim")
            return full_response
    else:
        console.print("[red]Warning: No text content in response[/red]", style="dim")
        return ""


@app.command()
def main():
    """Generate today's news webpage using Claude AI."""
    console.print("[bold cyan]News Generator[/bold cyan]", style="dim")
    console.print(f"[dim]Date: {datetime.now().strftime('%B %d, %Y')}[/dim]\n")

    try:
        # Run the async function
        html_content = asyncio.run(generate_news_webpage())

        if html_content:
            # Output to stdout (everything else goes to stderr via console)
            print(html_content)
        else:
            console.print("[red]Error: No HTML content generated[/red]")
            raise typer.Exit(1)

    except KeyboardInterrupt:
        console.print("\n[yellow]Cancelled by user[/yellow]")
        raise typer.Exit(130)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()