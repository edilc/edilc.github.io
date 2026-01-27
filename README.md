# news.sys

A daily news digest generated entirely by Claude. Every morning at 5am, an automated script prompts Claude to create a fresh static webpage summarizing the day's news—each edition with a unique aesthetic direction informed by the mood and themes of the headlines. Claude designs and generates complete HTML pages from scratch, responding aesthetically to the content.

**Live site:** [http://edilc.github.io/](https://edilc.github.io/)
---

## How It Works

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│GitHub Actions│────▶│   Claude    │────▶│  index.html │────▶│ GitHub Pages│
│  5am EST    │     │  designs &  │     │   pushed    │     │   serves    │
│             │     │  generates  │     │             │     │             │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
```

1. A GitHub Actions workflow runs daily at 5am EST
2. Claude's multi-agent system:
   - Searches for and gathers current news articles
   - Curates the top stories
   - Analyzes themes and mood across the selected articles
   - Designs and generates a complete HTML page from scratch
3. The generated `index.html` is committed and pushed to this repository
4. GitHub Pages serves the updated site

Each day's design is completely different—not through random variation, but through intentional response to the news itself. Claude has total creative freedom to invent a unique page from scratch each day.

---

## The Design Approach

The Builder agent receives a prompt that gives it complete creative freedom while requiring only a few essential elements:

### Required Elements (The Only Rules)
- The text "news.sys" and "News by Claude" appear somewhere
- All articles are presented (can mix full summaries and title-only with ways to access blurbs)
- Designer's notes included somewhere on the page
- Self-contained, responsive, and accessible HTML

### Total Design Freedom

Claude is encouraged to experiment radically with every aspect:
- **Layout**: Any structure imaginable—grids, floating elements, overlapping layers, spatial canvases
- **Hierarchy**: Emphasize stories differently, make some huge and others tiny
- **Typography**: Any fonts, any sizes, break all the rules
- **Color**: Full spectrum—from stark monochrome to wild gradients
- **Visual Elements**: SVG illustrations, ASCII art, textures, patterns, icons
- **Interactions**: Animations (CSS or JS), unconventional reveals, playful micro-interactions
- **Structure**: Doesn't need to feel like a "news site" at all

### Possible Aesthetic Directions

Each day, Claude analyzes the news and commits to one unique aesthetic. Possible inspirations include:
- Terminal/command line interface
- Field research notebook
- Classified government documents
- Museum exhibition labels
- Video game UI
- Scientific poster
- Illuminated manuscript
- Weather map
- Evidence board
- Technical manual
- Tarot card spread
- Comic book
- Windows '98 OS
- Pixel art game
- Movie script
- ...or anything else that fits the day's news

The page itself becomes part of the editorial voice. Some days feel like emergency broadcasts. Others feel like naturalist observations or technical diagrams or protest flyers. The aesthetic should amplify and respond to the content.

---

## Repository Structure

```
.
├── .github/
│   └── workflows/
│       └── generate-daily-news.yml  # GitHub Actions workflow
├── src/                             # Multi-agent pipeline source code
│   ├── agents/                      # Gatherer, Curator, and Builder agents
│   ├── models/                      # Data models
│   ├── prompts/                     # Agent prompts (including design prompt)
│   └── utils/                       # Logging and utilities
├── generate_news.py                 # Main generation script
├── index.html                       # The daily-generated news page
└── README.md                        # You are here
```

---

## Automation

The entire workflow is automated using GitHub Actions:

- **Schedule:** Daily at 5:00 AM EST (10:00 AM UTC)
- **Workflow:** `.github/workflows/generate-daily-news.yml`
- **Trigger:** Can also be manually triggered from the Actions tab

The workflow:
1. Deletes the previous `index.html`
2. Runs `generate_news.py` which executes a multi-agent pipeline:
   - Gatherer agents search for and collect news articles
   - Curator agent selects the top stories
   - Builder agent analyzes themes and designs a complete HTML page from scratch
3. The generated page is committed and pushed to the repository
4. GitHub Pages automatically deploys the update

---

## Running Locally

To generate a news page manually:

```bash
# Ensure ANTHROPIC_API_KEY is set in your environment
uv run generate_news.py > index.html
```

The output is a single static HTML file with no dependencies. Just open `index.html` in a browser.

---

## Why?

This is an experiment in AI-generated editorial design. Traditional news aggregators apply the same template to every story. news.sys asks: *what if the design itself was responsive to the news?*

Some days feel like emergency broadcasts. Others feel like quiet naturalist observations. The aesthetic should reflect that.

---

## License

The generation prompt and automation scripts are released under MIT. Individual news summaries link back to their original sources.

---

<p align="center">
  <em>news by Claude</em>
</p>
