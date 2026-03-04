"""
examples/04_list_navigation.py — Keyboard-navigable list.

Demonstrates: List, ListItem, ListState, keyboard input handling.
↑/↓ to navigate, q to quit.
"""
from pyratatui import (
    Terminal, List, ListItem, ListState,
    Block, Paragraph, Layout, Constraint, Direction,
    Style, Color,
)

ITEMS = [
    "🌍  Earth — Status: Online",
    "🔥  Mars  — Status: Degraded",
    "🪐  Saturn — Status: Online",
    "⚡  Jupiter — Status: Online",
    "❄️   Neptune — Status: Offline",
    "🌑  Pluto  — Status: Unknown",
]

state = ListState()
state.select(0)

with Terminal() as term:
    while True:
        selected = state.selected or 0
        detail = ITEMS[selected] if selected < len(ITEMS) else ""

        def ui(frame, sel=selected, det=detail):
            chunks = (Layout()
                .direction(Direction.Horizontal)
                .constraints([Constraint.percentage(50), Constraint.fill(1)])
                .split(frame.area))

            items = [ListItem(item) for item in ITEMS]
            frame.render_stateful_list(
                List(items)
                    .block(Block().bordered().title("Planets"))
                    .highlight_style(Style().fg(Color.yellow()).bold())
                    .highlight_symbol("▶ "),
                chunks[0],
                state,
            )
            frame.render_widget(
                Paragraph.from_string(f"Selected:\n\n{det}\n\nIndex: {sel}")
                    .block(Block().bordered().title("Detail"))
                    .style(Style().fg(Color.white())),
                chunks[1],
            )

        term.draw(ui)
        ev = term.poll_event(timeout_ms=50)
        if ev:
            if ev.code == "q":   break
            elif ev.code == "Down": state.select_next()
            elif ev.code == "Up":   state.select_previous()
            elif ev.code == "Home": state.select_first()
            elif ev.code == "End":  state.select_last()
