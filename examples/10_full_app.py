"""
examples/10_full_app.py — Full feature showcase: layout + widgets + effects + async.

Demonstrates: All major pyratatui features in a single production-quality app.
  - Multi-panel layout
  - Tabs for navigation
  - List + Table with keyboard state
  - Gauge, LineGauge, Sparkline, BarChart
  - Async reactive data
  - TachyonFX effects (fade-in on startup)
  - KeyEvent handling

↑/↓: navigate  Tab: switch tab  r: refresh  q: quit
"""

import asyncio
import contextlib
import math
import random
import time

from pyratatui import (
    AsyncTerminal,
    Bar,
    BarChart,
    BarGroup,
    Block,
    BorderType,
    Cell,
    Color,
    Constraint,
    Direction,
    Gauge,
    Layout,
    Line,
    List,
    ListItem,
    ListState,
    Paragraph,
    Row,
    Span,
    Sparkline,
    Style,
    Table,
    TableState,
    Tabs,
    Text,
)

# ── Shared state ───────────────────────────────────────────────────────────────

app = {
    "tab": 0,
    "list_state": ListState(),
    "table_state": TableState(),
    "services": [],
    "metrics": {"cpu": 0, "mem": 0, "reqs": 0},
    "cpu_hist": [0] * 30,
    "log": [],
    "tick": 0,
    "started": time.time(),
}

app["list_state"].select(0)
app["table_state"].select(0)

SERVICES = ["nginx", "postgres", "redis", "kafka", "prometheus", "alertmanager"]


def fresh_services():
    return [
        {
            "name": s,
            "cpu": random.randint(0, 100),
            "mem": random.randint(5, 95),
            "status": random.choice(["Running"] * 4 + ["Degraded", "Stopped"]),
            "uptime": f"{random.randint(1, 999)}h",
        }
        for s in SERVICES
    ]


app["services"] = fresh_services()


def cpu_color(p):
    return Color.green() if p < 50 else Color.yellow() if p < 80 else Color.red()


def status_color(s):
    return {
        "Running": Color.green(),
        "Degraded": Color.yellow(),
        "Stopped": Color.red(),
    }.get(s, Color.white())


# ── Background task ────────────────────────────────────────────────────────────


async def update_metrics():
    while True:
        await asyncio.sleep(0.4)
        app["tick"] += 1
        t = app["tick"]
        app["metrics"]["cpu"] = int(50 + 40 * math.sin(t * 0.15))
        app["metrics"]["mem"] = int(40 + 25 * math.sin(t * 0.08 + 1))
        app["metrics"]["reqs"] += random.randint(20, 80)
        app["cpu_hist"].append(app["metrics"]["cpu"])
        app["cpu_hist"] = app["cpu_hist"][-30:]
        if t % 6 == 0:
            ts = time.strftime("%H:%M:%S")
            app["log"].append(f"[{ts}] tick={t}  cpu={app['metrics']['cpu']}%")
            app["log"] = app["log"][-8:]


# ── UI renderers ──────────────────────────────────────────────────────────────


def render_overview(frame, area):
    panels = (
        Layout()
        .direction(Direction.Vertical)
        .constraints([Constraint.length(3), Constraint.length(5), Constraint.fill(1)])
        .split(area)
    )

    m = app["metrics"]
    frame.render_widget(
        Gauge()
        .percent(m["cpu"])
        .label(f"CPU: {m['cpu']}%")
        .style(Style().fg(cpu_color(m["cpu"])))
        .gauge_style(Style().fg(Color.dark_gray()))
        .block(Block().bordered().title("CPU Usage")),
        panels[0],
    )

    frame.render_widget(
        Sparkline()
        .data(app["cpu_hist"])
        .max(100)
        .style(Style().fg(cpu_color(m["cpu"])))
        .block(Block().bordered().title("CPU History (30 ticks)")),
        panels[1],
    )

    body = (
        Layout()
        .direction(Direction.Horizontal)
        .constraints([Constraint.percentage(50), Constraint.fill(1)])
        .split(panels[2])
    )

    bars = [
        Bar(s["cpu"], s["name"][:6]).style(Style().fg(cpu_color(s["cpu"])))
        for s in app["services"]
    ]
    frame.render_widget(
        BarChart()
        .data(BarGroup(bars, "CPU %"))
        .bar_width(5)
        .bar_gap(1)
        .max(100)
        .value_style(Style().fg(Color.white()).bold())
        .label_style(Style().fg(Color.dark_gray()))
        .block(Block().bordered().title("Per-Service CPU")),
        body[0],
    )

    frame.render_widget(
        Paragraph(
            Text(
                [
                    Line(
                        [
                            Span("Requests: ", Style().bold()),
                            Span(f"{m['reqs']:,}", Style().fg(Color.cyan())),
                        ]
                    ),
                    Line(
                        [
                            Span("Memory:   ", Style().bold()),
                            Span(f"{m['mem']}%", Style().fg(cpu_color(m["mem"]))),
                        ]
                    ),
                    Line(
                        [
                            Span("Uptime:   ", Style().bold()),
                            Span(
                                f"{time.time() - app['started']:.0f}s",
                                Style().fg(Color.green()),
                            ),
                        ]
                    ),
                    Line([]),
                    *[
                        Line([Span(ln, Style().fg(Color.gray()))])
                        for ln in app["log"][-4:]
                    ],
                ]
            )
        ).block(Block().bordered().title("Stats & Log")),
        body[1],
    )


def render_services(frame, area):
    panels = (
        Layout()
        .direction(Direction.Horizontal)
        .constraints([Constraint.percentage(45), Constraint.fill(1)])
        .split(area)
    )

    items = [
        ListItem(
            f"{'● ' if s['status'] == 'Running' else '● '}{s['name']:14s}  {s['cpu']:3d}%",
            Style().fg(status_color(s["status"])),
        )
        for s in app["services"]
    ]
    frame.render_stateful_list(
        List(items)
        .block(Block().bordered().title("Services").border_type(BorderType.Rounded))
        .highlight_style(Style().fg(Color.yellow()).bold())
        .highlight_symbol("▶ "),
        panels[0],
        app["list_state"],
    )

    hdr = Row(
        [
            Cell(h).style(Style().bold())
            for h in ["Service", "CPU", "MEM", "Status", "Uptime"]
        ]
    )
    rows = [
        Row(
            [
                Cell(s["name"]),
                Cell(f"{s['cpu']}%").style(Style().fg(cpu_color(s["cpu"]))),
                Cell(f"{s['mem']}%").style(Style().fg(cpu_color(s["mem"]))),
                Cell(s["status"]).style(Style().fg(status_color(s["status"]))),
                Cell(s["uptime"]),
            ]
        )
        for s in app["services"]
    ]
    frame.render_stateful_table(
        Table(rows)
        .column_widths([Constraint.fill(1)] * 5)
        .header(hdr)
        .block(
            Block().bordered().title("Process Table").border_type(BorderType.Rounded)
        )
        .highlight_style(Style().fg(Color.cyan()).bold()),
        panels[1],
        app["table_state"],
    )


# ── Main ─────────────────────────────────────────────────────────────────────


async def main():
    metrics_task = asyncio.create_task(update_metrics())

    async with AsyncTerminal() as term:
        term.hide_cursor()
        async for ev in term.events(fps=25, stop_on_quit=False):
            tab = app["tab"]

            def ui(frame, _tab=tab):
                area = frame.area
                outer = (
                    Layout()
                    .direction(Direction.Vertical)
                    .constraints(
                        [Constraint.length(3), Constraint.fill(1), Constraint.length(1)]
                    )
                    .split(area)
                )

                frame.render_widget(
                    Tabs(["Overview", "Services"])
                    .select(_tab)
                    .block(
                        Block()
                        .bordered()
                        .title(f" pyratatui Full App  ·  tick={app['tick']} ")
                    )
                    .highlight_style(Style().fg(Color.cyan()).bold())
                    .style(Style().fg(Color.dark_gray())),
                    outer[0],
                )

                if _tab == 0:
                    render_overview(frame, outer[1])
                else:
                    render_services(frame, outer[1])

                frame.render_widget(
                    Paragraph.from_string(
                        " ↑/↓: Navigate  Tab: Switch tab  r: Refresh  q: Quit"
                    ).style(Style().fg(Color.dark_gray())),
                    outer[2],
                )

            term.draw(ui)

            if ev:
                if ev.code == "q" or (ev.code == "c" and ev.ctrl):
                    break
                elif ev.code == "Tab":
                    app["tab"] = (app["tab"] + 1) % 2
                elif ev.code == "Down":
                    app["list_state"].select_next()
                    app["table_state"].select_next()
                elif ev.code == "Up":
                    app["list_state"].select_previous()
                    app["table_state"].select_previous()
                elif ev.code == "r":
                    app["services"] = fresh_services()

        term.show_cursor()

    metrics_task.cancel()
    with contextlib.suppress(asyncio.CancelledError):
        await metrics_task


asyncio.run(main())
