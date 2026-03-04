# Table & List Updates

This tutorial covers building interactive, live-updating tables and lists — the backbone of most TUI dashboards.

---

## Basic Static Table

```python
from pyratatui import (
    Terminal, Table, Row, Cell, TableState,
    Constraint, Block, Style, Color,
)

headers = Row([
    Cell("Name").style(Style().bold()),
    Cell("Role").style(Style().bold()),
    Cell("Status").style(Style().bold()),
])

data = [
    Row.from_strings(["Alice", "Engineer",  "Active"]),
    Row.from_strings(["Bob",   "Designer",  "Away"]),
    Row.from_strings(["Carol", "Manager",   "Active"]),
]

state = TableState()
state.select(0)

with Terminal() as term:
    while True:
        snap_state = state

        def ui(frame, _state=snap_state):
            frame.render_stateful_table(
                Table(data,
                      widths=[Constraint.percentage(35),
                              Constraint.percentage(35),
                              Constraint.fill(1)],
                      header=headers)
                    .block(Block().bordered().title("Staff"))
                    .highlight_style(Style().fg(Color.cyan()).bold())
                    .highlight_symbol("▶ "),
                frame.area,
                _state,
            )
        term.draw(ui)

        ev = term.poll_event(timeout_ms=100)
        if ev:
            if ev.code == "q":
                break
            elif ev.code == "Down":
                state.select_next()
            elif ev.code == "Up":
                state.select_previous()
```

---

## Table with Per-Cell Styling

Individual cells can carry their own `Style`, overriding the row style:

```python
def status_color(s: str):
    return {
        "Active":   Color.green(),
        "Away":     Color.yellow(),
        "Offline":  Color.red(),
    }.get(s, Color.white())

def make_rows(services):
    rows = []
    for svc in services:
        rows.append(Row([
            Cell(svc["name"]),
            Cell(f"{svc['cpu']}%").style(Style().fg(
                Color.green() if svc["cpu"] < 50 else
                Color.yellow() if svc["cpu"] < 80 else Color.red()
            )),
            Cell(f"{svc['mem']}%").style(Style().fg(Color.blue())),
            Cell(svc["status"]).style(Style().fg(status_color(svc["status"]))),
            Cell(svc["uptime"]),
        ]))
    return rows
```

---

## Live-Updating Table with Async

```python
import asyncio
import random
from pyratatui import (
    AsyncTerminal,
    Layout, Constraint, Direction,
    Table, Row, Cell, TableState,
    Block, Style, Color, Paragraph,
    BorderType,
)

SERVICES = ["nginx", "postgres", "redis", "kafka", "prometheus"]


def fresh_data():
    return [
        {
            "name":   name,
            "cpu":    random.randint(0, 100),
            "mem":    random.randint(5, 95),
            "status": random.choice(["Running"] * 4 + ["Degraded", "Stopped"]),
            "uptime": f"{random.randint(1, 999)}h",
        }
        for name in SERVICES
    ]


state = {
    "data":        fresh_data(),
    "table_state": TableState(),
}
state["table_state"].select(0)


async def refresh_loop():
    while True:
        await asyncio.sleep(1.5)
        state["data"] = fresh_data()


def cpu_color(p):
    return Color.green() if p < 50 else Color.yellow() if p < 80 else Color.red()


def status_color(s):
    return {"Running": Color.green(), "Degraded": Color.yellow(), "Stopped": Color.red()}.get(s, Color.white())


def build_table(data):
    header = Row([
        Cell(h).style(Style().bold().fg(Color.white()))
        for h in ["Service", "CPU %", "MEM %", "Status", "Uptime"]
    ])
    rows = [
        Row([
            Cell(d["name"]),
            Cell(f"{d['cpu']}%").style(Style().fg(cpu_color(d["cpu"]))),
            Cell(f"{d['mem']}%").style(Style().fg(Color.blue())),
            Cell(d["status"]).style(Style().fg(status_color(d["status"]))),
            Cell(d["uptime"]),
        ])
        for d in data
    ]
    return Table(rows,
                 widths=[Constraint.fill(1)] * 5,
                 header=header)


async def main():
    asyncio.create_task(refresh_loop())

    async with AsyncTerminal() as term:
        term.hide_cursor()

        async for ev in term.events(fps=20):
            data  = list(state["data"])
            ts    = state["table_state"]

            def ui(frame, _data=data, _ts=ts):
                area = frame.area
                chunks = (
                    Layout()
                    .direction(Direction.Vertical)
                    .constraints([Constraint.fill(1), Constraint.length(1)])
                    .split(area)
                )

                frame.render_stateful_table(
                    build_table(_data)
                        .block(Block().bordered()
                               .title(" Service Monitor  (auto-refresh 1.5s) ")
                               .border_type(BorderType.Rounded))
                        .highlight_style(Style().fg(Color.cyan()).bold())
                        .highlight_symbol("▶ ")
                        .column_spacing(1),
                    chunks[0],
                    _ts,
                )

                frame.render_widget(
                    Paragraph.from_string(" ↑/↓: Navigate  r: Refresh  q: Quit")
                        .style(Style().fg(Color.dark_gray())),
                    chunks[1],
                )

            term.draw(ui)

            if ev:
                if ev.code == "Down":
                    state["table_state"].select_next()
                elif ev.code == "Up":
                    state["table_state"].select_previous()
                elif ev.code == "Home":
                    state["table_state"].select_first()
                elif ev.code == "End":
                    state["table_state"].select_last()
                elif ev.code == "r":
                    state["data"] = fresh_data()

        term.show_cursor()


asyncio.run(main())
```

---

## List with Navigation

`List` is for single-column scrollable items with optional selection highlighting:

```python
from pyratatui import (
    Terminal, List, ListItem, ListState,
    Block, Style, Color, BorderType,
)

items = [ListItem(f"Option {i+1}") for i in range(20)]
state = ListState()
state.select(0)

with Terminal() as term:
    while True:
        def ui(frame, _state=state):
            frame.render_stateful_list(
                List(items)
                    .block(Block().bordered()
                           .title("Menu")
                           .border_type(BorderType.Rounded))
                    .highlight_style(Style().fg(Color.yellow()).bold())
                    .highlight_symbol("▶ "),
                frame.area,
                _state,
            )
        term.draw(ui)

        ev = term.poll_event(timeout_ms=50)
        if ev:
            if ev.code == "q":
                break
            elif ev.code == "Down":
                state.select_next()
            elif ev.code == "Up":
                state.select_previous()
            elif ev.code == "Home":
                state.select_first()
            elif ev.code == "End":
                state.select_last()
```

---

## List with Styled Items

Each `ListItem` can carry its own style:

```python
from pyratatui import ListItem, Style, Color

def make_items(services):
    symbols = {"Running": "●", "Degraded": "◐", "Stopped": "○"}
    colors  = {"Running": Color.green(), "Degraded": Color.yellow(), "Stopped": Color.red()}
    return [
        ListItem(
            f"{symbols[s['status']]} {s['name']:14s}  {s['cpu']:3d}%",
            Style().fg(colors[s["status"]]),
        )
        for s in services
    ]
```

---

## Synchronized List + Table

The full-app pattern keeps `ListState` and `TableState` in sync so selecting in the list highlights the same row in the table:

```python
async for ev in term.events(fps=25):
    if ev:
        if ev.code == "Down":
            state["list_state"].select_next()
            state["table_state"].select_next()
        elif ev.code == "Up":
            state["list_state"].select_previous()
            state["table_state"].select_previous()
```

---

## Table API Quick Reference

See also: [Table reference](../reference/widgets.md#table)

| Method | Description |
|---|---|
| `Table(rows, widths, header=None)` | Constructor |
| `.block(b)` | Wrap in a `Block` container |
| `.style(s)` | Base style for all cells |
| `.header_style(s)` | Override header row style |
| `.highlight_style(s)` | Style for the selected row |
| `.highlight_symbol(sym)` | Prefix for selected row (e.g. `"▶ "`) |
| `.column_spacing(n)` | Extra gap between columns |
| `frame.render_stateful_table(widget, area, state)` | Render with selection |

## List API Quick Reference

See also: [List reference](../reference/widgets.md#list)

| Method | Description |
|---|---|
| `List(items)` | Constructor — list of `ListItem` |
| `.block(b)` | Wrap in a `Block` |
| `.highlight_style(s)` | Style for selected item |
| `.highlight_symbol(sym)` | Prefix character(s) |
| `.direction(dir)` | `ListDirection.TopToBottom` (default) or `BottomToTop` |
| `frame.render_stateful_list(widget, area, state)` | Render with selection |
