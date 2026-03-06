#!/usr/bin/env python3
"""
Example 12 — Stateful (Draggable) Popup
=========================================
Demonstrates a popup that can be moved around the screen using:
  - Arrow keys (↑ ↓ ← →) to move
  - Mouse drag on the title bar
  - 'r' to reset position to center
  - 'q' / Esc to quit

Run:
    python examples/12_popup_stateful.py
"""

from pyratatui import Color, Paragraph, Popup, PopupState, Style, Terminal

HELP = [
    " ↑/↓/←/→  Move popup",
    " r         Reset to center",
    " q / Esc   Quit",
    "",
    " (drag title bar with mouse)",
]


def make_background() -> Paragraph:
    lines = []
    for i in range(50):
        lines.append(f"Background content line {i:02d} " + "· " * 20)
    return Paragraph.from_string("\n".join(lines)).style(Style().fg(Color.dark_gray()))


def main() -> None:
    state = PopupState()
    background = make_background()

    popup_body = "\n".join(HELP)
    popup = (
        Popup(popup_body)
        .title(" Draggable Popup — arrow keys to move ")
        .style(Style().fg(Color.white()).bg(Color.dark_gray()))
    )

    with Terminal() as term:
        running = True
        while running:

            def ui(frame, _pop=popup, _bg=background, _st=state):
                frame.render_widget(_bg, frame.area)
                frame.render_stateful_popup(_pop, frame.area, _st)

            term.draw(ui)

            ev = term.poll_event(timeout_ms=50)
            if ev is None:
                continue

            code = ev.code
            if code in ("q", "Esc"):
                running = False
            elif code == "Up":
                state.move_up(1)
            elif code == "Down":
                state.move_down(1)
            elif code == "Left":
                state.move_left(1)
            elif code == "Right":
                state.move_right(1)
            elif code == "r":
                state.reset()

    print("Bye!")


if __name__ == "__main__":
    main()
