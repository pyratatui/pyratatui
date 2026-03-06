#!/usr/bin/env python3
"""
Example 13 — Scrollable Popup with KnownSizeWrapper
=====================================================
Demonstrates a popup with scrollable content using `KnownSizeWrapper`.
The content is a long list of lines that can be scrolled with ↑/↓.

Controls:
  - ↑/↓        Scroll content
  - Page Up/Dn Fast scroll (5 lines)
  - Home/End   Jump to top/bottom
  - q / Esc    Quit

Run:
    python examples/13_popup_scrollable.py
"""

from pyratatui import Color, KnownSizeWrapper, Paragraph, Popup, Style, Terminal

# Generate a long list of content lines.
LINES = [
    f"  {i:03d}  Lorem ipsum dolor sit amet, consectetur adipiscing elit. Line {i}."
    for i in range(1, 51)
]

POPUP_WIDTH = 60
POPUP_HEIGHT = 12


def main() -> None:
    background = Paragraph.from_string("\n".join(["░" * 80] * 40)).style(
        Style().fg(Color.dark_gray())
    )

    # KnownSizeWrapper wraps scrollable content with a fixed display size.
    wrapper = KnownSizeWrapper(
        lines=LINES,
        width=POPUP_WIDTH,
        height=POPUP_HEIGHT,
        scroll=0,
    )

    with Terminal() as term:
        running = True
        while running:
            popup = (
                Popup(wrapper)
                .title(
                    f" Scrollable Content  [{wrapper.scroll + 1}–"
                    f"{min(wrapper.scroll + POPUP_HEIGHT, len(LINES))}"
                    f"/{len(LINES)}]  ↑/↓ to scroll, q to quit "
                )
                .style(Style().fg(Color.white()).bg(Color.blue()))
            )

            def ui(frame, _pop=popup, _bg=background):
                frame.render_widget(_bg, frame.area)
                frame.render_popup(_pop, frame.area)

            term.draw(ui)

            ev = term.poll_event(timeout_ms=100)
            if ev is None:
                continue

            code = ev.code
            if code in ("q", "Esc"):
                running = False
            elif code == "Up":
                wrapper.scroll_up(1)
            elif code == "Down":
                wrapper.scroll_down(1)
            elif code == "PageUp":
                wrapper.scroll_up(5)
            elif code == "PageDown":
                wrapper.scroll_down(5)
            elif code == "Home":
                wrapper = KnownSizeWrapper(LINES, POPUP_WIDTH, POPUP_HEIGHT, scroll=0)
            elif code == "End":
                max_scroll = max(0, len(LINES) - POPUP_HEIGHT)
                wrapper = KnownSizeWrapper(
                    LINES, POPUP_WIDTH, POPUP_HEIGHT, scroll=max_scroll
                )

    print(f"Closed at scroll position {wrapper.scroll}.")


if __name__ == "__main__":
    main()
