"""Design memory system to track recent design choices and encourage variation."""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import TypedDict


class DesignSummary(TypedDict):
    """Summary of a design from a specific day."""

    date: str
    brief: str


# Memory file location (at project root)
MEMORY_FILE = Path(__file__).parent.parent.parent / "design_memory.json"


def extract_design_summary(html: str, date: str) -> DesignSummary:
    """
    Extract design summary from generated HTML.

    Looks for the DESIGN BRIEF comment and extracts it.
    If not found, creates a minimal summary.
    """
    # Try to find the DESIGN BRIEF comment
    brief_match = re.search(
        r"<!--\s*DESIGN BRIEF:\s*(.*?)\s*-->", html, re.DOTALL | re.IGNORECASE
    )

    if brief_match:
        brief = brief_match.group(1).strip()
        # Clean up excessive whitespace
        brief = re.sub(r"\s+", " ", brief)
    else:
        # Fallback if no design brief found
        brief = "No design brief found in generated HTML"

    return {"date": date, "brief": brief}


def save_design_summary(summary: DesignSummary) -> None:
    """
    Append today's design to memory file.

    Keeps only the last 7 days of designs.
    """
    memories = load_design_memory()

    # Add new summary
    memories.append(summary)

    # Keep only last 7 days
    memories = memories[-7:]

    # Save back to file
    MEMORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    MEMORY_FILE.write_text(json.dumps(memories, indent=2))


def load_design_memory() -> list[DesignSummary]:
    """Load recent design summaries from file."""
    if MEMORY_FILE.exists():
        try:
            content = MEMORY_FILE.read_text()
            data = json.loads(content)
            # Validate structure
            if isinstance(data, list):
                return data
        except (json.JSONDecodeError, ValueError):
            # If file is corrupted, start fresh
            pass

    return []


def get_recent_designs(n: int = 3) -> list[DesignSummary]:
    """Get the N most recent design summaries."""
    memories = load_design_memory()
    return memories[-n:] if memories else []


def format_design_memory(recent_designs: list[DesignSummary]) -> str:
    """
    Format recent designs as context for the prompt.

    Returns XML-formatted section describing recent designs.
    """
    if not recent_designs:
        return """<recent_designs>
No previous designs on record. This is your first design!
</recent_designs>"""

    lines = ["<recent_designs>"]
    lines.append(
        "The following designs were used in recent days. DO NOT repeat these approaches—find something different.\n"
    )

    for design in recent_designs:
        # Truncate brief if too long
        brief = design["brief"]
        if len(brief) > 300:
            brief = brief[:297] + "..."

        lines.append(f"**{design['date']}**: {brief}\n")

    lines.append("</recent_designs>")
    return "\n".join(lines)


def get_today_date() -> str:
    """Get today's date in YYYY-MM-DD format."""
    return datetime.now().strftime("%Y-%m-%d")
