# Progress Bar Tutorial

pyratatui provides two progress widgets: `Gauge` (a filled block bar) and `LineGauge` (a single-line indicator). Both accept either a percentage (0–100) or a float ratio (0.0–1.0).

---

## Gauge — Filled Block Progress Bar

```
┌ Downloads ────────────────────────────────────────────┐
│ ██████████████████████████░░░░░░░░░░░░░  67%           │
└───────────────────────────────────────────────────────┘
```

### Minimal Gauge

```python
from pyratatui import Terminal, Gauge, Block, Style, Color

progress = 0

with Terminal() as term:
    while progress <= 100:
        def ui(frame, p=progress):
            frame.render_widget(
                Gauge()
                    .percent(p)
                    .label(f"{p}%")
                    .block(Block().bordered().title("Progress"))
                    .style(Style().fg(Color.green())),
                frame.area,
            )
        term.draw(ui)
        term.poll_event(timeout_ms=50)
        progress += 1
```

### Gauge with Dynamic Color

The color can change based on the value — common for CPU/memory meters:

```python
from pyratatui import Terminal, Gauge, Block, Style, Color

def gauge_color(pct: int):
    if pct < 50:
        return Color.green()
    elif pct < 80:
        return Color.yellow()
    else:
        return Color.red()

progress = 0

with Terminal() as term:
    while True:
        def ui(frame, p=progress):
            color = gauge_color(p)
            frame.render_widget(
                Gauge()
                    .percent(p)
                    .label(f"CPU: {p}%")
                    .style(Style().fg(color))
                    .gauge_style(Style().fg(Color.dark_gray()))
                    .block(Block().bordered().title("CPU Usage")),
                frame.area,
            )
        term.draw(ui)
        ev = term.poll_event(timeout_ms=50)
        if ev and ev.code == "q":
            break
        progress = (progress + 1) % 101
```

### Gauge with Ratio (float precision)

Use `.ratio()` instead of `.percent()` when you have a float in the range `[0.0, 1.0]`:

```python
downloaded = 4_200_000   # bytes received
total       = 10_000_000  # bytes total

gauge = (Gauge()
    .ratio(downloaded / total)
    .label(f"{downloaded / 1e6:.1f} MB / {total / 1e6:.1f} MB")
    .style(Style().fg(Color.cyan())))
```

### Unicode Gauge

Enable smooth 8ths-of-a-character filling with `.use_unicode(True)`:

```python
gauge = Gauge().percent(67).use_unicode(True).style(Style().fg(Color.blue()))
```

!!! note
    `use_unicode` requires a terminal font that includes the Unicode block characters U+2580–U+2588.

---

## LineGauge — Single-Line Progress Indicator

```
Downloads ──────────────────────────────────────── 67%
```

```python
from pyratatui import Terminal, LineGauge, Block, Style, Color

progress = 0.0

with Terminal() as term:
    while True:
        def ui(frame, p=progress):
            frame.render_widget(
                LineGauge()
                    .ratio(p)
                    .label(f"{p*100:.0f}%")
                    .style(Style().fg(Color.cyan()))
                    .gauge_style(Style().fg(Color.dark_gray()))
                    .block(Block().bordered().title("Download")),
                frame.area,
            )
        term.draw(ui)
        ev = term.poll_event(timeout_ms=30)
        if ev and ev.code == "q":
            break
        progress = min(1.0, progress + 0.005)
```

### LineGauge Line Sets

Control the character used for the filled portion:

```python
# "normal" (default) — ─
lg = LineGauge().ratio(0.5).line_set("normal")

# "thick"  — ━
lg = LineGauge().ratio(0.5).line_set("thick")

# "double" — ═
lg = LineGauge().ratio(0.5).line_set("double")
```

---

## Multiple Progress Bars in a Layout

```python
import asyncio
import random
from pyratatui import (
    AsyncTerminal,
    Layout, Constraint, Direction,
    Gauge, LineGauge, Block, Style, Color, Paragraph,
)

tasks = [
    {"name": "nginx",      "pct": 0},
    {"name": "postgres",   "pct": 0},
    {"name": "redis",      "pct": 0},
    {"name": "kafka",      "pct": 0},
]


async def advance_tasks():
    while True:
        await asyncio.sleep(0.1)
        for t in tasks:
            t["pct"] = min(100, t["pct"] + random.randint(0, 3))


async def main():
    asyncio.create_task(advance_tasks())

    async with AsyncTerminal() as term:
        term.hide_cursor()

        async for ev in term.events(fps=20):
            snapshot = [dict(t) for t in tasks]

            def ui(frame, snap=snapshot):
                area = frame.area
                # One row per task (3 rows each) + 1 footer
                constraints = [Constraint.length(3)] * len(snap) + [Constraint.length(1)]
                chunks = (
                    Layout()
                    .direction(Direction.Vertical)
                    .constraints(constraints)
                    .split(area)
                )

                for i, task in enumerate(snap):
                    color = (
                        Color.green() if task["pct"] < 50 else
                        Color.yellow() if task["pct"] < 80 else
                        Color.cyan()
                    )
                    done = task["pct"] >= 100
                    frame.render_widget(
                        Gauge()
                            .percent(task["pct"])
                            .label("Done! ✓" if done else f"{task['pct']}%")
                            .style(Style().fg(color))
                            .gauge_style(Style().fg(Color.dark_gray()))
                            .block(Block().bordered()
                                   .title(f" {task['name']} ")),
                        chunks[i],
                    )

                frame.render_widget(
                    Paragraph.from_string(" q: Quit")
                        .style(Style().fg(Color.dark_gray())),
                    chunks[-1],
                )

            term.draw(ui)

        term.show_cursor()


asyncio.run(main())
```

---

## Async Animated Progress Bar

This example shows a single download bar that advances autonomously:

```python
import asyncio
from pyratatui import (
    AsyncTerminal,
    Layout, Constraint, Direction,
    Gauge, Paragraph, Block, Style, Color,
)

state = {"progress": 0.0, "done": False}


async def download():
    import random
    while state["progress"] < 1.0:
        await asyncio.sleep(0.05)
        state["progress"] = min(1.0, state["progress"] + random.uniform(0.005, 0.02))
    state["done"] = True


async def main():
    dl_task = asyncio.create_task(download())

    async with AsyncTerminal() as term:
        term.hide_cursor()

        async for ev in term.events(fps=30):
            p    = state["progress"]
            done = state["done"]

            def ui(frame, _p=p, _done=done):
                area = frame.area
                chunks = (
                    Layout()
                    .direction(Direction.Vertical)
                    .constraints([
                        Constraint.fill(1),
                        Constraint.length(3),
                        Constraint.length(3),
                        Constraint.fill(1),
                    ])
                    .split(area)
                )

                label = "Download complete! ✓" if _done else f"{_p*100:.1f}%"
                color = Color.green() if _done else Color.cyan()

                frame.render_widget(
                    Gauge()
                        .ratio(_p)
                        .label(label)
                        .style(Style().fg(color))
                        .gauge_style(Style().fg(Color.dark_gray()))
                        .use_unicode(True)
                        .block(Block().bordered().title(" Downloading ")),
                    chunks[1],
                )
                frame.render_widget(
                    Paragraph.from_string(
                        "Done! Press q to exit." if _done else "Downloading…  q: cancel"
                    ).style(Style().fg(Color.dark_gray())).centered(),
                    chunks[2],
                )

            term.draw(ui)
            if done:
                ev2 = term.area()  # keep rendering until user quits
            # stop_on_quit=True (default) handles 'q'

        term.show_cursor()

    await dl_task


asyncio.run(main())
```

---

## Gauge API Summary

See also: [Gauge reference](../reference/widgets.md#gauge)

| Method | Type | Default | Description |
|---|---|---|---|
| `.percent(pct)` | `int` (0–100) | `0` | Set progress as a percentage |
| `.ratio(r)` | `float` (0.0–1.0) | `0.0` | Set progress as a float ratio |
| `.label(text)` | `str` | auto | Override the center label |
| `.style(s)` | `Style` | — | Foreground/background of the filled portion |
| `.gauge_style(s)` | `Style` | — | Style of the empty (unfilled) portion |
| `.use_unicode(v)` | `bool` | `False` | Enable smooth Unicode block filling |
| `.block(b)` | `Block` | — | Wrap in a bordered container |

## LineGauge API Summary

| Method | Type | Default | Description |
|---|---|---|---|
| `.ratio(r)` | `float` (0.0–1.0) | `0.0` | Progress ratio |
| `.percent(pct)` | `int` (0–100) | — | Shorthand for `.ratio(pct/100)` |
| `.label(text)` | `str` | auto | Text shown to the right |
| `.line_set(name)` | `"normal"/"thick"/"double"` | `"normal"` | Fill character |
| `.style(s)` | `Style` | — | Style of the filled line |
| `.gauge_style(s)` | `Style` | — | Style of the empty line |
| `.block(b)` | `Block` | — | Container block |
