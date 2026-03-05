"""
examples/dashboard.py — Full-featured dashboard demo.

Demonstrates: Layout, Block, Paragraph, List, Table, Gauge,
BarChart, Sparkline, Tabs, Scrollbar, and keyboard navigation.

Run:
    python examples/dashboard.py
"""

from __future__ import annotations

import math
import time

from pyratatui import (
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
    LineGauge,
    List,
    ListItem,
    ListState,
    Modifier,
    Paragraph,
    Row,
    Span,
    Sparkline,
    Style,
    Table,
    TableState,
    Tabs,
    Terminal,
    Text,
)

# ── Simulated data ──────────────────────────────────────────────────────────────

SERVERS = [
    {"name": "web-01", "cpu": 23, "mem": 45, "status": "Running"},
    {"name": "web-02", "cpu": 5, "mem": 30, "status": "Running"},
    {"name": "db-01", "cpu": 67, "mem": 80, "status": "Running"},
    {"name": "cache-01", "cpu": 1, "mem": 12, "status": "Running"},
    {"name": "queue-01", "cpu": 34, "mem": 55, "status": "Stopped"},
]

CPU_HISTORY: list[int] = [int(20 + 30 * abs(math.sin(i * 0.4))) for i in range(40)]


def status_color(status: str) -> Color:
    return Color.green() if status == "Running" else Color.red()


def cpu_color(pct: int) -> Color:
    if pct < 40:
        return Color.green()
    if pct < 70:
        return Color.yellow()
    return Color.red()


def main() -> None:
    tab_index = 0
    list_state = ListState()
    list_state.select(0)
    table_state = TableState()
    table_state.select(0)
    tick = 0

    with Terminal() as term:
        term.hide_cursor()

        while True:
            t = tick
            ti = tab_index
            selected_server = list_state.selected or 0
            srv = SERVERS[selected_server]

            def ui(frame, _tick=t, _ti=ti, _srv=srv):  # noqa: ANN001
                area = frame.area

                # ── Top-level vertical split ─────────────────────────────────
                outer = (
                    Layout()
                    .direction(Direction.Vertical)
                    .constraints(
                        [
                            Constraint.length(3),  # tabs / header
                            Constraint.fill(1),  # main body
                            Constraint.length(3),  # bottom gauge
                            Constraint.length(1),  # status bar
                        ]
                    )
                    .split(area)
                )

                # ── Tabs ─────────────────────────────────────────────────────
                frame.render_widget(
                    Tabs(["Overview", "Processes", "Logs"])
                    .select(_ti)
                    .block(
                        Block()
                        .bordered()
                        .title(f" pyratatui Dashboard  ·  {time.strftime('%H:%M:%S')} ")
                    )
                    .highlight_style(Style().fg(Color.cyan()).bold())
                    .style(Style().fg(Color.dark_gray())),
                    outer[0],
                )

                # ── Main body horizontal split ───────────────────────────────
                body = (
                    Layout()
                    .direction(Direction.Horizontal)
                    .constraints(
                        [
                            Constraint.percentage(35),
                            Constraint.fill(1),
                        ]
                    )
                    .split(outer[1])
                )

                left_panels = (
                    Layout()
                    .direction(Direction.Vertical)
                    .constraints([Constraint.fill(1), Constraint.length(8)])
                    .split(body[0])
                )

                # ── Server list ──────────────────────────────────────────────
                items = [
                    ListItem(
                        f"{'● ' if s['status']=='Running' else '○ '}{s['name']:10s}"
                        f"  CPU:{s['cpu']:3d}%",
                        Style().fg(status_color(s["status"])),
                    )
                    for s in SERVERS
                ]
                frame.render_stateful_list(
                    List(items)
                    .block(
                        Block()
                        .bordered()
                        .title("Servers")
                        .border_type(BorderType.Rounded)
                    )
                    .highlight_style(Style().fg(Color.yellow()).bold())
                    .highlight_symbol("▶ "),
                    left_panels[0],
                    list_state,
                )

                # ── Sparkline (CPU history) ──────────────────────────────────
                history = CPU_HISTORY[-left_panels[1].width :]
                frame.render_widget(
                    Sparkline()
                    .data(history)
                    .max(100)
                    .style(Style().fg(cpu_color(_srv["cpu"])))
                    .block(Block().bordered().title(f"CPU History — {_srv['name']}")),
                    left_panels[1],
                )

                # ── Right side panels ────────────────────────────────────────
                right_panels = (
                    Layout()
                    .direction(Direction.Vertical)
                    .constraints([Constraint.fill(1), Constraint.length(10)])
                    .split(body[1])
                )

                # ── Process table ────────────────────────────────────────────
                hdr = Row([Cell("Server"), Cell("CPU"), Cell("Memory"), Cell("Status")])
                rows = [
                    Row(
                        [
                            Cell(s["name"]),
                            Cell(f"{s['cpu']}%").style(Style().fg(cpu_color(s["cpu"]))),
                            Cell(f"{s['mem']}%"),
                            Cell(s["status"]).style(
                                Style().fg(status_color(s["status"]))
                            ),
                        ]
                    )
                    for s in SERVERS
                ]
                frame.render_stateful_table(
                    Table(
                        rows,
                        [
                            Constraint.fill(1),
                            Constraint.length(7),
                            Constraint.length(9),
                            Constraint.length(10),
                        ],
                        header=hdr,
                    )
                    .block(
                        Block()
                        .bordered()
                        .title("Process Table")
                        .border_type(BorderType.Rounded)
                    )
                    .highlight_style(Style().fg(Color.cyan()).bold()),
                    right_panels[0],
                    table_state,
                )

                # ── Bar chart ────────────────────────────────────────────────
                bars = [
                    Bar(s["cpu"], s["name"][:6]).style(Style().fg(cpu_color(s["cpu"])))
                    for s in SERVERS
                ]
                frame.render_widget(
                    BarChart()
                    .data(BarGroup(bars, "CPU %"))
                    .bar_width(4)
                    .bar_gap(1)
                    .max(100)
                    .value_style(Style().fg(Color.white()).bold())
                    .label_style(Style().fg(Color.dark_gray()))
                    .block(Block().bordered().title("CPU Overview")),
                    right_panels[1],
                )

                # ── Bottom gauge ─────────────────────────────────────────────
                frame.render_widget(
                    Gauge()
                    .percent(_srv["cpu"])
                    .label(f"{_srv['name']} — CPU: {_srv['cpu']}%")
                    .style(Style().fg(cpu_color(_srv["cpu"])))
                    .gauge_style(Style().fg(Color.dark_gray()))
                    .block(Block().bordered().title("Selected Server")),
                    outer[2],
                )

                # ── Status bar ───────────────────────────────────────────────
                frame.render_widget(
                    Paragraph(
                        Text(
                            [
                                Line(
                                    [
                                        Span(" ↑/↓", Style().fg(Color.yellow()).bold()),
                                        Span(
                                            ": Navigate  ",
                                            Style().fg(Color.dark_gray()),
                                        ),
                                        Span("Tab", Style().fg(Color.yellow()).bold()),
                                        Span(
                                            ": Switch tab  ",
                                            Style().fg(Color.dark_gray()),
                                        ),
                                        Span("q", Style().fg(Color.yellow()).bold()),
                                        Span(": Quit", Style().fg(Color.dark_gray())),
                                    ]
                                )
                            ]
                        )
                    ),
                    outer[3],
                )

            term.draw(ui)
            tick += 1

            # ── Update simulated data ────────────────────────────────────────
            for srv in SERVERS:
                srv["cpu"] = max(0, min(100, srv["cpu"] + (tick % 3 - 1) * 2))
            CPU_HISTORY.append(SERVERS[0]["cpu"])
            if len(CPU_HISTORY) > 100:
                CPU_HISTORY.pop(0)

            ev = term.poll_event(timeout_ms=80)
            if ev:
                if ev.code == "q" or (ev.code == "c" and ev.ctrl):
                    break
                elif ev.code == "Down":
                    list_state.select_next()
                    table_state.select_next()
                elif ev.code == "Up":
                    list_state.select_previous()
                    table_state.select_previous()
                elif ev.code == "Tab":
                    tab_index = (tab_index + 1) % 3

        term.show_cursor()


if __name__ == "__main__":
    main()
