# Quickstart

## Your First TUI

```python
from pyratatui import Terminal, Paragraph, Block, Style, Color

with Terminal() as term:
    while True:
        def ui(frame):
            frame.render_widget(
                Paragraph.from_string("Hello! Press q to quit.")
                    .block(Block().bordered().title("pyratatui"))
                    .style(Style().fg(Color.cyan())),
                frame.area,
            )
        term.draw(ui)
        ev = term.poll_event(timeout_ms=100)
        if ev and ev.code == "q":
            break
```

## Using `run_app`

The `run_app` helper removes the boilerplate:

```python
from pyratatui import run_app, Paragraph, Block

def ui(frame):
    frame.render_widget(
        Paragraph.from_string("Hello from run_app!")
            .block(Block().bordered()),
        frame.area,
    )

run_app(ui)   # Press q to quit
```

## Layout

Split the screen into sections:

```python
from pyratatui import (
    Terminal, Layout, Constraint, Direction,
    Paragraph, Block, Style, Color,
)

with Terminal() as term:
    while True:
        def ui(frame):
            chunks = (
                Layout()
                .direction(Direction.Vertical)
                .constraints([
                    Constraint.length(3),   # header
                    Constraint.fill(1),     # body
                    Constraint.length(1),   # footer
                ])
                .split(frame.area)
            )
            frame.render_widget(
                Block().bordered().title("Header"),
                chunks[0],
            )
            frame.render_widget(
                Paragraph.from_string("Main content here")
                    .block(Block().bordered()),
                chunks[1],
            )
            frame.render_widget(
                Paragraph.from_string(" q: Quit  ↑/↓: Navigate"),
                chunks[2],
            )
        term.draw(ui)
        ev = term.poll_event(timeout_ms=100)
        if ev and ev.code == "q":
            break
```

## Styled Text

```python
from pyratatui import Span, Line, Text, Paragraph, Style, Color, Modifier

text = Text([
    Line([
        Span("Status: ", Style().bold()),
        Span("OK", Style().fg(Color.green()).bold()),
    ]),
    Line.from_string("All systems nominal."),
])

para = Paragraph(text)
```

## Selectable List

```python
from pyratatui import List, ListItem, ListState, Style, Color, Block

items = [ListItem(f"Server {i+1}") for i in range(10)]
state = ListState()
state.select(0)

lst = (List(items)
    .block(Block().bordered().title("Servers"))
    .highlight_style(Style().fg(Color.yellow()).bold())
    .highlight_symbol("▶ "))

# In your draw callback:
# frame.render_stateful_list(lst, area, state)
```

## Table

```python
from pyratatui import Table, Row, Cell, TableState, Constraint, Style, Color, Block

header = Row([Cell("Name"), Cell("CPU"), Cell("Status")])
rows = [
    Row.from_strings(["nginx", "0.2%", "Running"]),
    Row.from_strings(["postgres", "1.1%", "Running"]),
    Row.from_strings(["redis", "0.0%", "Stopped"]),
]
widths = [Constraint.fill(1), Constraint.length(8), Constraint.length(10)]

table = (Table(rows, widths, header=header)
    .block(Block().bordered().title("Processes"))
    .highlight_style(Style().fg(Color.cyan())))

state = TableState()
state.select(0)
# frame.render_stateful_table(table, area, state)
```
