# news.sys

A daily news digest generated entirely by Claude. Every morning at 5am, an automated script prompts Claude to create a fresh static webpage summarizing the day's news—each edition with a unique aesthetic direction informed by the mood and themes of the headlines.

**Live site:** [http://clide-s.github.io/](https://clide-s.github.io/)
---

## How It Works

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  5am cron   │────▶│   Claude    │────▶│  index.html │────▶│ GitHub Pages│
│   trigger   │     │  generates  │     │   pushed    │     │   serves    │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
```

1. A scheduled script runs daily at 5am
2. Claude receives the prompt below, searches for current news, and generates a complete static HTML page
3. The generated `index.html` is committed and pushed to this repository
4. GitHub Pages serves the updated site

Each day's design is different—not through random variation, but through intentional response to the news itself. A day heavy with government scandals might render as classified documents; breakthrough scientific discoveries might appear as naturalist field notes.

---

## The Prompt

The following prompt is sent to Claude each morning:

~~~
Create a static web page for "news.sys" — a daily news digest by Claude.

## Content Requirements
- Header: "news.sys" with subtle "news by Claude" attribution
- 10 news headlines from various sources with brief blurbs
- Each headline expands on click to reveal: a longer summary, key bullet points, and source links
- No numbered items. No "live feed" text. No auto-animations (user-triggered only).

## Aesthetic Process (IMPORTANT)

**Step 1: Analyze the news.** Before designing, identify:
- The dominant mood across today's stories (ominous, hopeful, absurd, bureaucratic, scientific, chaotic, contemplative, urgent, mundane, surreal)
- Recurring themes or domains (politics, technology, nature, conflict, discovery, economy, culture)
- Any single story dramatic enough to anchor the visual tone

**Step 2: Commit to ONE aesthetic direction.** Based on your analysis, choose a specific visual concept. Don't blend—commit. Examples of directions (use these as inspiration, not a checklist):

| News Mood | Possible Aesthetic Direction |
|-----------|------------------------------|
| Government/bureaucracy heavy | Classified documents, redacted files, manila folders, typewriter text, official stamps |
| Science/nature discoveries | Field notebook, naturalist illustrations, specimen labels, botanical drawings, parchment textures |
| Tech/cyber news | Terminal interface, phosphor glow, scan lines, monospace everything, ASCII decorations |
| Economic/financial | Stock ticker aesthetic, ledger paper, banking forms, serif authority, green/black |
| Absurd/weird news | Tabloid collage, ransom note typography, clip art chaos, garish colors |
| Conflict/crisis | Broadcast interruption, emergency alert, high contrast, stark warnings |
| Cultural/arts | Editorial magazine, gallery exhibition, refined typography, generous whitespace |
| Mundane/local news | Community bulletin board, pushpins, handwritten notes, cork texture |

**Step 3: Design with intention.** Your chosen direction should influence:
- **Layout structure**: Single column? Split pane? Card grid? Sidebar index? Dossier format?
- **Typography**: Bureaucratic serifs? Playful handwriting? Cold monospace? Elegant editorial?
- **Color palette**: Derive from concept (manila/red for classified, green/cream for naturalist, amber/black for terminal)
- **Decorative elements**: ASCII art, SVG illustrations, borders, stamps, textures, dividers—all should reinforce the theme
- **Information density**: Sparse and contemplative? Dense and urgent?

**Step 4: Create 1-3 thematic visual elements.** These should feel integral, not decorative:
- Small SVG illustrations reflecting dominant story themes
- ASCII art headers or dividers
- Thematic icons or stamps
- Textural backgrounds (subtle)

**Step 5: Add a design rationale.** In the footer, include a small note explaining today's aesthetic choice, e.g.:
> "today's design: field notebook (3 stories on species discovery, 2 on climate research)"

## Technical Requirements
- Single HTML file with embedded CSS and JS
- Readable and functional—aesthetic experimentation should never compromise usability
- Responsive (works on mobile)
- Accessible (proper contrast, semantic HTML, keyboard navigation for expandable items)
- No external dependencies except Google Fonts if needed

## What to Avoid
- Blending all inspirations into generic "retro-tech minimalist"
- Color/font swaps as the only variation
- Decorative elements that don't connect to content
- Cluttered or illegible results
- The same layout every time
~~~

---

## Repository Structure

```
.
├── index.html      # The daily-generated news page (overwritten each day)
└── README.md       # You are here
```

---

## Running Locally

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
