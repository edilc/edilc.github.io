"""Prompt template for the webpage builder agent."""

# Builder prompt combines original design instructions with article data
BUILDER_PROMPT = """Today is {today}.

You are building today's news.sys webpage.

Here are the 10 selected articles:

{articles}

{original_design_instructions}

IMPORTANT: Use the actual article data provided above. Each article should expand on click to show its full summary and source link.
"""


def get_builder_prompt_template(original_prompt_path: str) -> str:
    """Load and combine with original prompt.txt."""
    with open(original_prompt_path, "r") as f:
        original = f.read()

    return BUILDER_PROMPT.format(
        today="{today}",
        articles="{articles}",
        original_design_instructions=original,
    )
