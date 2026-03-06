#!/usr/bin/env python3
"""
Example 11 — Basic Popup
========================
Demonstrates the simplest possible popup: a centered text popup that closes
when any key is pressed.

Run:
    python examples/11_popup_basic.py
"""

from pyratatui import Color, Paragraph, Popup, Style, Terminal


def main() -> None:
    popup = (
        Popup("Press any key to exit.")
        .title(" tui-popup demo ")
        .style(Style().fg(Color.white()).bg(Color.blue()))
    )

    background = Paragraph.from_string("\n".join(["─" * 80] * 40)).style(
        Style().fg(Color.dark_gray())
    )

    with Terminal() as term:
        running = True
        while running:

            def ui(frame, _pop=popup, _bg=background):
                frame.render_widget(_bg, frame.area)
                frame.render_popup(_pop, frame.area)

            term.draw(ui)

            ev = term.poll_event(timeout_ms=200)
            if ev is not None:
                running = False

    print("Popup closed!")


if __name__ == "__main__":
    main()
