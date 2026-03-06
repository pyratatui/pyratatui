"""
examples/22_prompt_select.py — Arrow-key selection prompt demo.

Demonstrates a menu-selection interaction built on pyratatui primitives:
  - ↑/↓ (or j/k) to navigate
  - Enter to select
  - Esc to abort

This pattern shows how to build custom interactive prompts on top of
the core event loop without needing a dedicated SelectPrompt class.

Press ↑/↓ to navigate, Enter to select, Esc to abort.
"""

from pyratatui import (
    Block,
    Color,
    Constraint,
    Direction,
    Layout,
    Line,
    Paragraph,
    Span,
    Style,
    Terminal,
    Text,
)

# ── Options ───────────────────────────────────────────────────────────────────

OPTIONS = [
    ("🦀 Rust", "Fast, safe, compiled"),
    ("🐍 Python", "Readable, batteries included"),
    ("💎 Ruby", "Elegant, developer-friendly"),
    ("☕ Java", "Write once, run anywhere"),
    ("⚡ JavaScript", "Runs everywhere, for better or worse"),
    ("🐹 Go", "Simple, fast, concurrent"),
    ("🌀 TypeScript", "JavaScript with types"),
]

# ── State ─────────────────────────────────────────────────────────────────────

selected_index = 0
result: str | None = None
running = True

# ── Event loop ────────────────────────────────────────────────────────────────

with Terminal() as term:
    term.hide_cursor()

    while running:
        _idx = selected_index

        def ui(frame, _i=_idx):
            area = frame.area

            rows = (
                Layout()
                .direction(Direction.Vertical)
                .constraints([Constraint.fill(1), Constraint.length(1)])
                .split(area)
            )

            option_lines: list[Line] = [
                Line([Span("  Select a language:\n", Style().fg(Color.cyan()).bold())]),
                Line([]),
            ]

            for i, (lang, desc) in enumerate(OPTIONS):
                if i == _i:
                    marker = " ▶ "
                    lang_style = Style().fg(Color.yellow()).bold()
                    desc_style = Style().fg(Color.white())
                    bg = Style().bg(Color.dark_gray())
                else:
                    marker = "   "
                    lang_style = Style().fg(Color.white())
                    desc_style = Style().fg(Color.gray())
                    bg = Style()

                line = Line(
                    [
                        Span(marker, bg),
                        Span(f"{lang:<20}", lang_style),
                        Span(f"  {desc}", desc_style),
                    ]
                )
                option_lines.append(line)

            frame.render_widget(
                Paragraph(Text(option_lines)).block(
                    Block()
                    .bordered()
                    .title(" Language Selector ")
                    .style(Style().fg(Color.cyan()))
                ),
                rows[0],
            )

            frame.render_widget(
                Paragraph.from_string(
                    " ↑/↓ or j/k: move   Enter: select   Esc: abort"
                ).style(Style().fg(Color.dark_gray())),
                rows[1],
            )

        term.draw(ui)

        ev = term.poll_event(timeout_ms=50)
        if ev:
            if ev.code in ("q", "Esc"):
                running = False
            elif ev.code in ("Down", "j"):
                selected_index = (selected_index + 1) % len(OPTIONS)
            elif ev.code in ("Up", "k"):
                selected_index = (selected_index - 1) % len(OPTIONS)
            elif ev.code == "Enter":
                result = OPTIONS[selected_index][0]
                running = False

    term.show_cursor()

# ── Display outcome ───────────────────────────────────────────────────────────

print()
if result is None:
    print("  Selection aborted.")
else:
    print(f"  You selected: {result}")
print()
