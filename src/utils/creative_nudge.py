"""Creative nudge system to encourage design experimentation and variation."""

import random
from typing import TypedDict


class CreativeNudge(TypedDict):
    """A creative nudge to influence design decisions."""

    type: str
    weight: int
    text: str | None


# Weighted list of creative nudges
NUDGES: list[CreativeNudge] = [
    # 30% chance: No nudge (let Claude design freely)
    {"type": "none", "weight": 30, "text": None},
    # Counterbalance heavy news with light design
    {
        "type": "counterbalance",
        "weight": 15,
        "text": "NUDGE: If today's news is heavy, consider responding with lightness, calm, or even quiet optimism. Somber news doesn't require somber design.",
    },
    # Focus on the weirdest story
    {
        "type": "highlight_the_weird",
        "weight": 15,
        "text": "NUDGE: Find the strangest or most surprising story. Let it drive the entire design, even if it's not the 'biggest' story.",
    },
    # Retro aesthetics
    {
        "type": "retro",
        "weight": 10,
        "text": "NUDGE: Commit fully to a retro aesthetic today: {retro_style}.",
    },
    # Color constraints
    {
        "type": "color_constraint",
        "weight": 10,
        "text": "NUDGE: Constrain your palette today: {color_constraint}.",
    },
    # Typography focus
    {
        "type": "typography_focus",
        "weight": 8,
        "text": "NUDGE: Make typography the star today. Minimal decoration—let type hierarchy, spacing, and rhythm do all the work.",
    },
    # Playful approach
    {
        "type": "playful",
        "weight": 7,
        "text": "NUDGE: Make something genuinely playful today. Whimsy, humor, delight—even if the news is serious. The contrast can be meaningful.",
    },
    # Structural experiments
    {
        "type": "structural",
        "weight": 5,
        "text": "NUDGE: Try an unusual structure: {structural_approach}.",
    },
]

# Sub-options for retro nudge
RETRO_STYLES = [
    "90s web (under construction energy, tiled backgrounds, visitor counters)",
    "Teletext/Ceefax (blocky, broadcast, limited color palette)",
    "Early Mac (1-bit graphics, Chicago font, minimal OS aesthetic)",
    "DOS/terminal (text-mode interfaces, ANSI art, command prompts)",
    "Windows 98 (beveled buttons, system gray, desktop metaphor)",
]

# Sub-options for color constraint nudge
COLOR_CONSTRAINTS = [
    "pure monochrome (black, white, gray only)",
    "strict duotone (pick two colors, nothing else)",
    "single accent (one bold color against neutrals)",
    "borrowed palette (steal colors from a specific painting or film)",
    "neon on dark (bright electric colors on black background)",
]

# Sub-options for structural nudge
STRUCTURAL_APPROACHES = [
    "radical asymmetry",
    "extreme density (broadsheet-packed)",
    "radical minimalism (how much can you remove?)",
    "non-linear layout (let the eye wander)",
    "single dramatic focal point",
    "broken grid (intentionally violate layout rules)",
]


def generate_creative_nudge() -> CreativeNudge:
    """
    Generate a random creative nudge based on weighted probabilities.

    Returns a nudge dictionary with type and optional text.
    """
    # Calculate total weight
    total_weight = sum(nudge["weight"] for nudge in NUDGES)

    # Pick a random value
    r = random.uniform(0, total_weight)

    # Select nudge based on weighted random
    cumulative = 0
    for nudge in NUDGES:
        cumulative += nudge["weight"]
        if r <= cumulative:
            # If nudge has placeholders, fill them in
            if nudge["text"] and "{" in nudge["text"]:
                return _fill_nudge_placeholders(nudge)
            return nudge

    # Fallback (should never happen)
    return {"type": "none", "weight": 0, "text": None}


def _fill_nudge_placeholders(nudge: CreativeNudge) -> CreativeNudge:
    """Fill in placeholders in nudge text with random choices."""
    text = nudge["text"]
    if not text:
        return nudge

    # Replace placeholders
    if "{retro_style}" in text:
        text = text.format(retro_style=random.choice(RETRO_STYLES))
    elif "{color_constraint}" in text:
        text = text.format(color_constraint=random.choice(COLOR_CONSTRAINTS))
    elif "{structural_approach}" in text:
        text = text.format(structural_approach=random.choice(STRUCTURAL_APPROACHES))

    return {"type": nudge["type"], "weight": nudge["weight"], "text": text}


def format_nudge(nudge: CreativeNudge) -> str:
    """
    Format nudge for prompt insertion.

    Returns XML-formatted section or empty string if no nudge.
    """
    if nudge["type"] == "none" or not nudge["text"]:
        return ""

    return f"""<creative_nudge>
{nudge['text']}
</creative_nudge>"""
