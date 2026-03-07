# Advanced Examples

Full-featured mini-applications demonstrating real-world usage patterns.

---

## Full Dashboard — Async + All Widgets

A production-quality monitoring dashboard combining all major features: tabs, list, table, gauges, sparkline, barchart, async data, and TachyonFX effects.

```python
"""
Full monitoring dashboard.

Features:
- Multi-panel layout with Tabs
- Live async data simulation
- Synchronized List + Table
- CPU/Memory Gauges
- Sparkline history
- BarChart per-service
- TachyonFX startup sweep

↑/↓: navigate  Tab: switch tab  r: refresh  q: quit
"""
import asyncio, math, random, time
from pyratatui import (
    AsyncTerminal,
    Layout, Constraint, Direction,
    Block, Paragraph, BorderType,
    List, ListItem, ListState,
    Table, Row, Cell, TableState,
    Gauge, Sparkline, BarChart, BarGroup, Bar, Tabs,
    Style, Color, Text, Line, Span,
    Effect, EffectManager, Motion, Interpolation,
)

# ── State ─────────────────────────────────────────────────────────────────────

SERVICES = ["nginx", "postgres", "redis", "kafka", "prometheus", "alertmanager"]

def fresh_services():
    return [{
        "name":   s,
        "cpu":    random.randint(0, 100),
        "mem":    random.randint(5, 95),
        "status": random.choice(["Running"] * 4 + ["Degraded", "Stopped"]),
        "uptime": f"{random.randint(1, 999)}h",
    } for s in SERVICES]

app = {
    "tab":         0,
    "list_state":  ListState(),
    "table_state": TableState(),
    "services":    fresh_services(),
    "metrics":     {"cpu": 0, "mem": 0, "reqs": 0},
    "cpu_hist":    [0] * 30,
    "log":         [],
    "tick":        0,
    "started":     time.time(),
}
app["list_state"].select(0)
app["table_state"].select(0)

# ── Color helpers ─────────────────────────────────────────────────────────────

def cpu_color(p):
    return Color.green() if p < 50 else Color.yellow() if p < 80 else Color.red()

def status_color(s):
    return {"Running": Color.green(), "Degraded": Color.yellow(),
            "Stopped": Color.red()}.get(s, Color.white())

# ── Background tasks ──────────────────────────────────────────────────────────

async def update_metrics():
    while True:
        await asyncio.sleep(0.4)
        t = app["tick"] + 1
        app["tick"] = t
        app["metrics"]["cpu"] = int(50 + 40 * math.sin(t * 0.15))
        app["metrics"]["mem"] = int(40 + 25 * math.sin(t * 0.08 + 1))
        app["metrics"]["reqs"] += random.randint(20, 80)
        app["cpu_hist"].append(app["metrics"]["cpu"])
        app["cpu_hist"] = app["cpu_hist"][-30:]
        if t % 6 == 0:
            ts = time.strftime("%H:%M:%S")
            app["log"].append(f"[{ts}] tick={t} cpu={app['metrics']['cpu']}%")
            app["log"] = app["log"][-8:]

# ── Overview tab ──────────────────────────────────────────────────────────────

def render_overview(frame, area, m, hist, services, log, started):
    panels = (Layout().direction(Direction.Vertical)
        .constraints([Constraint.length(3), Constraint.length(5), Constraint.fill(1)])
        .split(area))

    frame.render_widget(
        Gauge().percent(m["cpu"]).label(f"CPU: {m['cpu']}%")
            .style(Style().fg(cpu_color(m["cpu"])))
            .gauge_style(Style().fg(Color.dark_gray()))
            .use_unicode(True)
            .block(Block().bordered().title("CPU Usage")),
        panels[0])

    frame.render_widget(
        Sparkline().data(hist).max(100)
            .style(Style().fg(cpu_color(m["cpu"])))
            .block(Block().bordered().title("CPU History (30 ticks)")),
        panels[1])

    body = (Layout().direction(Direction.Horizontal)
        .constraints([Constraint.percentage(50), Constraint.fill(1)])
        .split(panels[2]))

    bars = [Bar(s["cpu"], s["name"][:6]).style(Style().fg(cpu_color(s["cpu"])))
            for s in services]
    frame.render_widget(
        BarChart().data(BarGroup(bars, "CPU %")).bar_width(5).max(100)
            .value_style(Style().fg(Color.white()).bold())
            .label_style(Style().fg(Color.dark_gray()))
            .block(Block().bordered().title("Per-Service CPU")),
        body[0])

    frame.render_widget(
        Paragraph(Text([
            Line([Span("Requests: ", Style().bold()),
                  Span(f"{m['reqs']:,}", Style().fg(Color.cyan()))]),
            Line([Span("Memory:   ", Style().bold()),
                  Span(f"{m['mem']}%", Style().fg(cpu_color(m["mem"])))]),
            Line([Span("Uptime:   ", Style().bold()),
                  Span(f"{time.time()-started:.0f}s", Style().fg(Color.green()))]),
            Line.from_string(""),
            *[Line([Span(l, Style().fg(Color.gray()))]) for l in log[-4:]],
        ])).block(Block().bordered().title("Stats & Log")),
        body[1])

# ── Services tab ──────────────────────────────────────────────────────────────

def render_services(frame, area, services, list_state, table_state):
    panels = (Layout().direction(Direction.Horizontal)
        .constraints([Constraint.percentage(40), Constraint.fill(1)])
        .split(area))

    items = [ListItem(
        f"{'●' if s['status']=='Running' else '◐' if s['status']=='Degraded' else '○'}"
        f" {s['name']:14s} {s['cpu']:3d}%",
        Style().fg(status_color(s["status"])))
        for s in services]
    frame.render_stateful_list(
        List(items)
            .block(Block().bordered().title("Services")
                   .border_type(BorderType.Rounded))
            .highlight_style(Style().fg(Color.yellow()).bold())
            .highlight_symbol("▶ "),
        panels[0], list_state)

    hdr = Row([Cell(h).style(Style().bold())
               for h in ["Service", "CPU", "MEM", "Status", "Uptime"]])
    rows = [Row([
        Cell(s["name"]),
        Cell(f"{s['cpu']}%").style(Style().fg(cpu_color(s["cpu"]))),
        Cell(f"{s['mem']}%").style(Style().fg(Color.blue())),
        Cell(s["status"]).style(Style().fg(status_color(s["status"]))),
        Cell(s["uptime"]),
    ]) for s in services]
    frame.render_stateful_table(
        Table(rows).column_widths([Constraint.fill(1)] * 5).header(hdr)
            .block(Block().bordered().title("Process Table")
                   .border_type(BorderType.Rounded))
            .highlight_style(Style().fg(Color.cyan()).bold()),
        panels[1], table_state)

# ── Main ──────────────────────────────────────────────────────────────────────

async def main():
    # TachyonFX: one-shot startup sweep
    mgr  = EffectManager()
    last = time.monotonic()
    mgr.add(Effect.sweep_in(Motion.LeftToRight, sweep_span=20, gradient_len=5,
                             color=Color.black(), duration_ms=800,
                             interpolation=Interpolation.QuadOut))

    tasks = [asyncio.create_task(update_metrics())]

    async with AsyncTerminal() as term:
        term.hide_cursor()

        async for ev in term.events(fps=25, stop_on_quit=False):
            now = time.monotonic()
            ms  = int((now - last) * 1000)
            last = now

            # Snapshot state for this frame
            tab      = app["tab"]
            m        = dict(app["metrics"])
            hist     = list(app["cpu_hist"])
            services = list(app["services"])
            log      = list(app["log"])
            ls       = app["list_state"]
            ts       = app["table_state"]
            started  = app["started"]
            tick     = app["tick"]

            def ui(frame, _tab=tab, _m=m, _hist=hist, _svcs=services,
                   _log=log, _ls=ls, _ts=ts, _st=started, _tick=tick,
                   _mgr=mgr, _ms=ms):
                area = frame.area
                outer = (Layout().direction(Direction.Vertical)
                    .constraints([Constraint.length(3), Constraint.fill(1),
                                  Constraint.length(1)])
                    .split(area))

                frame.render_widget(
                    Tabs(["Overview", "Services"]).select(_tab)
                        .block(Block().bordered()
                               .title(f" pyratatui Monitor  · tick={_tick} "))
                        .highlight_style(Style().fg(Color.cyan()).bold())
                        .style(Style().fg(Color.dark_gray())),
                    outer[0])

                if _tab == 0:
                    render_overview(frame, outer[1], _m, _hist, _svcs, _log, _st)
                else:
                    render_services(frame, outer[1], _svcs, _ls, _ts)

                frame.render_widget(
                    Paragraph.from_string(
                        " ↑/↓: Navigate  Tab: Switch  r: Refresh  q: Quit")
                        .style(Style().fg(Color.dark_gray())),
                    outer[2])

                # Apply startup sweep effect
                if _mgr.has_active():
                    frame.apply_effect_manager(_mgr, _ms, area)

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

    for t in tasks:
        t.cancel()
    await asyncio.gather(*tasks, return_exceptions=True)


asyncio.run(main())
```

---

## Popup / Modal Dialog

Overlay a popup on top of the main UI using `Clear`:

```python
"""
Popup dialog demo.

Press 'p' to open the popup, Enter/Esc to close.
"""
from pyratatui import (
    Terminal, Layout, Constraint, Direction,
    Paragraph, Block, Clear, Style, Color,
    Rect, BorderType,
)

show_popup = False

def centered_rect(area, width, height):
    x = max(0, (area.width  - width)  // 2)
    y = max(0, (area.height - height) // 2)
    return Rect(area.x + x, area.y + y, width, height)

with Terminal() as term:
    while True:
        popup = show_popup

        def ui(frame, _popup=popup):
            area = frame.area

            # Main content (always rendered)
            frame.render_widget(
                Paragraph.from_string(
                    "Main application content.\n\n"
                    "Press 'p' to open popup.\nPress 'q' to quit."
                ).block(Block().bordered().title("Main")),
                area,
            )

            # Popup overlay
            if _popup:
                dialog = centered_rect(area, 40, 7)
                frame.render_widget(Clear(), dialog)  # clear background
                frame.render_widget(
                    Paragraph.from_string(
                        "Are you sure?\n\nPress Enter to confirm, Esc to cancel."
                    ).block(
                        Block().bordered()
                            .title(" ⚠ Confirm Action ")
                            .border_type(BorderType.Double)
                            .border_style(Style().fg(Color.yellow()))
                    ).centered(),
                    dialog,
                )

        term.draw(ui)
        ev = term.poll_event(timeout_ms=50)
        if ev:
            if ev.code == "q" and not show_popup:
                break
            elif ev.code == "p":
                show_popup = True
            elif ev.code in ("Enter", "Esc"):
                show_popup = False
```

---

## Scrollable Log Viewer

Scrollable paragraph with `Scrollbar`:

```python
"""
Scrollable log viewer.
↑/↓/PageUp/PageDown: scroll  q: quit
"""
from pyratatui import (
    Terminal, Layout, Constraint, Direction,
    Paragraph, Block, Scrollbar, ScrollbarState,
    Text, Line, Span, Style, Color,
)

# Generate 100 log lines
LOG_LINES = [
    f"[2024-01-{(i % 28)+1:02d} 12:{i%60:02d}:00] "
    f"{'ERROR' if i % 13 == 0 else 'INFO '} "
    f"Request {i} processed in {(i * 7) % 100}ms"
    for i in range(100)
]

scroll_pos = 0
VISIBLE = 20  # approximate visible lines

def make_text(lines):
    def line_color(l):
        return Color.red() if "ERROR" in l else Color.gray()
    return Text([Line([Span(l, Style().fg(line_color(l)))]) for l in lines])

with Terminal() as term:
    term.hide_cursor()
    while True:
        pos = scroll_pos

        def ui(frame, _pos=pos):
            area = frame.area
            chunks = (Layout().direction(Direction.Horizontal)
                .constraints([Constraint.fill(1), Constraint.length(1)])
                .split(area))

            # Visible slice
            visible = LOG_LINES[_pos: _pos + (area.height - 2)]
            frame.render_widget(
                Paragraph(make_text(visible))
                    .block(Block().bordered()
                           .title(f" Logs  [{_pos+1}–{_pos+len(visible)}/{len(LOG_LINES)}] ")),
                chunks[0],
            )

            sb_state = (ScrollbarState()
                        .content_length(max(0, len(LOG_LINES) - area.height + 2))
                        .position(_pos))
            frame.render_stateful_scrollbar(
                Scrollbar().thumb_style(Style().fg(Color.cyan()))
                           .track_style(Style().fg(Color.dark_gray())),
                chunks[1],
                sb_state,
            )

        term.draw(ui)
        ev = term.poll_event(timeout_ms=50)
        if ev:
            area = term.area()
            page = max(1, area.height - 4)
            max_pos = max(0, len(LOG_LINES) - area.height + 2)
            if ev.code == "q":
                break
            elif ev.code == "Down":
                scroll_pos = min(max_pos, scroll_pos + 1)
            elif ev.code == "Up":
                scroll_pos = max(0, scroll_pos - 1)
            elif ev.code == "PageDown":
                scroll_pos = min(max_pos, scroll_pos + page)
            elif ev.code == "PageUp":
                scroll_pos = max(0, scroll_pos - page)
            elif ev.code == "Home":
                scroll_pos = 0
            elif ev.code == "End":
                scroll_pos = max_pos
    term.show_cursor()
```

---

## Animated Startup Sequence

A sequence of tachyonfx effects played on startup before entering the normal UI:

```python
"""
Animated startup with TachyonFX sequence effect.
"""
import time
from pyratatui import (
    Terminal, Paragraph, Block, Style, Color,
    Effect, EffectManager, Motion, Interpolation,
)

mgr  = EffectManager()
last = time.monotonic()

# Play: sweep in → hold → coalesce text
startup = Effect.sequence([
    Effect.sweep_in(Motion.LeftToRight, sweep_span=25, gradient_len=8,
                    color=Color.black(), duration_ms=700,
                    interpolation=Interpolation.QuadOut),
    Effect.sleep(200),
    Effect.coalesce(600, Interpolation.QuadOut),
])
mgr.add(startup)

SPLASH = (
    "████████████████████████████████\n"
    "██   pyratatui  Dashboard  ██\n"
    "████████████████████████████████\n"
    "\n"
    "       Loading…  please wait\n"
)

with Terminal() as term:
    term.hide_cursor()
    while True:
        now = time.monotonic()
        ms  = int((now - last) * 1000)
        last = now

        def ui(frame, _mgr=mgr, _ms=ms):
            area = frame.area
            frame.render_widget(
                Paragraph.from_string(SPLASH)
                    .block(Block().bordered().border_style(Style().fg(Color.cyan())))
                    .style(Style().fg(Color.cyan()).bold())
                    .centered(),
                area,
            )
            if _mgr.has_active():
                frame.apply_effect_manager(_mgr, _ms, area)

        term.draw(ui)
        ev = term.poll_event(timeout_ms=16)
        if ev and ev.code == "q":
            break
        # Transition to main app after startup completes
        if not mgr.has_active():
            term.poll_event(timeout_ms=800)  # brief hold
            break  # enter main loop here

    term.show_cursor()
    print("Startup complete — entering main app.")
```

---

## 25. Calendar — Interactive Month Browser *(new in 0.2.1)*

A fully interactive monthly calendar with event highlighting, weekend styling,
and keyboard navigation.

```python
"""
examples/25_calendar.py

Controls:
  ←/→  Previous / next month
  ↑/↓  Previous / next year
  t    Jump to today
  q    Quit
"""
from __future__ import annotations
import calendar as _cal
from datetime import date as _pydate
from pyratatui import (
    Block, CalendarDate, CalendarEventStore, Color, Constraint,
    Direction, Layout, Line, Monthly, Paragraph, Span, Style, Terminal, Text,
)

_today = _pydate.today()
_year  = _today.year
_month = _today.month

_MONTHS = ["", "January","February","March","April","May","June",
           "July","August","September","October","November","December"]

def make_store(year, month):
    store = CalendarEventStore()
    if year == _today.year and month == _today.month:
        store.add_today(Style().fg(Color.green()).bold())
    _, days = _cal.monthrange(year, month)
    for day in range(1, days + 1):
        if _cal.weekday(year, month, day) >= 5:
            store.add(CalendarDate.from_ymd(year, month, day),
                      Style().fg(Color.yellow()).dim())
    store.add(CalendarDate.from_ymd(year, month, 1),
              Style().fg(Color.cyan()).bold())
    if days >= 15:
        store.add(CalendarDate.from_ymd(year, month, 15),
                  Style().fg(Color.magenta()).bold())
    return store

def ui(frame):
    outer = (Layout().direction(Direction.Vertical)
             .constraints([Constraint.length(3), Constraint.min(1), Constraint.length(3)])
             .split(frame.area))
    frame.render_widget(
        Paragraph.from_string(f"  {_MONTHS[_month]}  {_year}")
        .block(Block().bordered().title(" Calendar "))
        .centered().style(Style().fg(Color.cyan()).bold()), outer[0])
    body = (Layout().direction(Direction.Horizontal)
            .constraints([Constraint.length(30), Constraint.fill(1)])
            .split(outer[1]))
    frame.render_widget(
        Monthly(CalendarDate.from_ymd(_year, _month, 1), make_store(_year, _month))
        .block(Block().bordered().title(" Monthly "))
        .show_month_header(Style().bold().fg(Color.cyan()))
        .show_weekdays_header(Style().italic().fg(Color.light_blue()))
        .show_surrounding(Style().dim())
        .default_style(Style().fg(Color.white())), body[0])
    legend = Text([
        Line([Span("Legend:", Style().bold())]), Line([]),
        Line([Span("  today",       Style().fg(Color.green()).bold())]),
        Line([Span("  weekend",     Style().fg(Color.yellow()).dim())]),
        Line([Span("  1st",         Style().fg(Color.cyan()).bold())]),
        Line([Span("  15th",        Style().fg(Color.magenta()).bold())]),
        Line([]), Line([Span(f"Today: {_today}", Style().dim())]),
    ])
    frame.render_widget(
        Paragraph(legend).block(Block().bordered().title(" Legend ")), body[1])
    frame.render_widget(
        Paragraph.from_string("  ←/→ month   ↑/↓ year   t today   q quit")
        .block(Block().bordered()).style(Style().fg(Color.dark_gray())), outer[2])

def main():
    global _year, _month
    with Terminal() as term:
        while True:
            term.draw(ui)
            ev = term.poll_event(timeout_ms=200)
            if not ev: continue
            if ev.code == "q":     break
            elif ev.code == "Left":
                _month -= 1
                if _month < 1: _month = 12; _year -= 1
            elif ev.code == "Right":
                _month += 1
                if _month > 12: _month = 1; _year += 1
            elif ev.code == "Up":   _year += 1
            elif ev.code == "Down": _year -= 1
            elif ev.code == "t":    _year = _today.year; _month = _today.month

main()
```

Run it:

```bash
python examples/25_calendar.py
```

---

## 26. Web Counter — Browser TUI *(new in 0.2.1)*

An interactive counter that runs entirely in your browser via `pyratatui.web`.

```python
"""
examples/26_web_counter.py

Open http://localhost:7700/ in your browser after starting.
↑/↓: change counter   r: reset   f: fill   q: quit
"""
from pyratatui import Block, Color, Constraint, Direction, Gauge, Layout, Line, Paragraph, Span, Style, Text
from pyratatui.web import WebTerminal

counter = 0
MAX, MIN = 100, 0
status  = "Ready — ↑/↓ to change, r reset, f fill, q quit"

def ui(frame):
    area = frame.area
    outer = (Layout().direction(Direction.Vertical)
             .constraints([
                 Constraint.length(3), Constraint.length(4),
                 Constraint.length(3), Constraint.min(1), Constraint.length(3),
             ]).split(area))
    frame.render_widget(
        Paragraph.from_string("  PyRatatui Web — Interactive Counter")
        .block(Block().bordered().title(" pyratatui.web "))
        .style(Style().fg(Color.cyan()).bold()), outer[0])
    c_color = Color.green() if counter >= 50 else Color.yellow() if counter >= 20 else Color.red()
    frame.render_widget(
        Paragraph(Text([Line([
            Span("  Counter: "),
            Span(f"{counter:>4}", Style().fg(c_color).bold()),
            Span(f" / {MAX}", Style().dim()),
        ]), Line([])]))
        .block(Block().bordered().title(" Value ")), outer[1])
    frame.render_widget(
        Gauge().block(Block().bordered().title(" Progress "))
        .ratio(max(0.0, min(1.0, counter / MAX)))
        .label(f"{counter}%")
        .gauge_style(Style().fg(c_color)), outer[2])
    frame.render_widget(
        Paragraph.from_string(f"  {status}")
        .block(Block().bordered()).style(Style().fg(Color.dark_gray())), outer[4])

def main():
    global counter, status
    with WebTerminal(cols=100, rows=32, fps=20) as term:
        print(f"\n  Open: {term.url}\n")
        while True:
            term.draw(ui)
            ev = term.poll_event(timeout_ms=50)
            if not ev: continue
            if ev.code == "q":     break
            elif ev.code == "Up":  counter = min(MAX, counter + 1); status = f"Counter: {counter}"
            elif ev.code == "Down":counter = max(MIN, counter - 1); status = f"Counter: {counter}"
            elif ev.code == "r":   counter = 0; status = "Reset"
            elif ev.code == "f":   counter = MAX; status = f"Filled to {MAX}"

main()
```

Run it:

```bash
python examples/26_web_counter.py
# Open http://localhost:7700/ in your browser
```
