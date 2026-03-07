#!/usr/bin/env python3
"""
28_markdown_renderer.py — tui-markdown: render Markdown in the terminal

Converts a multi-section Markdown document and displays it with full
ratatui styling.  Scroll with ↑/↓, quit with 'q'.
"""

from __future__ import annotations

from pyratatui import (
    Block,
    Color,
    Constraint,
    Direction,
    Layout,
    Paragraph,
    Style,
    Terminal,
    markdown_to_text,
)

SAMPLE_MARKDOWN = """
# pyratatui 0.2.1 — What's New

Welcome to **pyratatui**, Python bindings for the blazing-fast
[ratatui](https://ratatui.rs) terminal UI library.

## New Widgets

### tui-bar-graph
Colorful gradient bar graphs with support for multiple styles:

- **Braille** — dense unicode braille characters
- **HalfBlock** — unicode half-block characters
- **Block** — full block characters

### tui-tree-widget
Interactive hierarchical tree view:

```python
tree = Tree([TreeItem("Root", [TreeItem("Child")])])
state = TreeState()
frame.render_stateful_tree(tree, area, state)
```

### tui-markdown
Convert Markdown → `Text` for terminal rendering (*this very demo!*).

### tui-logger
Real-time log viewer widget with level filtering.

### ratatui-image
Display images using sixel, kitty, or unicode halfblock protocols.

## Installation

```bash
pip install pyratatui
```

---

> "The terminal is a canvas." — Anonymous Rust developer

## License

MIT
"""


def main():
    text = markdown_to_text(SAMPLE_MARKDOWN)
    total_lines = text.height
    scroll = 0

    with Terminal() as term:
        while True:

            def ui(frame, _text=text, _scroll=scroll):
                area = frame.area
                chunks = (
                    Layout()
                    .direction(Direction.Vertical)
                    .constraints([Constraint.length(1), Constraint.fill(1)])
                    .split(area)
                )
                frame.render_widget(
                    Paragraph.from_string(
                        f"  Markdown Renderer Demo  (↑↓ scroll, q quit)  "
                        f"[{_scroll + 1}/{total_lines}]"
                    ).style(Style().fg(Color.cyan()).bold()),
                    chunks[0],
                )
                frame.render_widget(
                    Paragraph(_text)
                    .block(Block().bordered())
                    .wrap(True)
                    .scroll(_scroll, 0),
                    chunks[1],
                )

            term.draw(ui)
            ev = term.poll_event(timeout_ms=50)
            if ev:
                if ev.code == "q" or (ev.code == "c" and ev.ctrl):
                    break
                elif ev.code == "Up":
                    scroll = max(0, scroll - 1)
                elif ev.code == "Down":
                    scroll = min(total_lines - 1, scroll + 1)
                elif ev.code == "PageUp":
                    scroll = max(0, scroll - 10)
                elif ev.code == "PageDown":
                    scroll = min(total_lines - 1, scroll + 10)


if __name__ == "__main__":
    main()
