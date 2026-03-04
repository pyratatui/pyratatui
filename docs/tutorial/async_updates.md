# Async Updates

pyratatui's `AsyncTerminal` lets you run background `asyncio` tasks that update shared state while the render loop redraws the screen at a configurable frame rate. This is the recommended pattern for dashboards, monitors, and any UI with live data.

---

## Threading Model

The native `Terminal` object is **unsendable** — PyO3 records which OS thread created it and panics if any method is called from a different thread. Python's default asyncio event loop runs entirely on a single thread (the one that called `asyncio.run()`), so as long as you never touch `Terminal` via `asyncio.to_thread` or `loop.run_in_executor`, you are safe.

`AsyncTerminal` enforces this by:

1. Calling `terminal.poll_event(0)` (non-blocking) on the main thread, and
2. Using `await asyncio.sleep(frame_interval)` to yield to background coroutines between frames.

**Never do this:**

```python
# ❌ WRONG — sends Terminal to a thread-pool worker → panics
ev = await asyncio.to_thread(term.poll_event, 100)
```

**Do this instead:**

```python
# ✅ CORRECT — AsyncTerminal handles the threading internally
async for ev in term.events(fps=30):
    ...
```

---

## Basic Async App

```python
import asyncio
from pyratatui import AsyncTerminal, Paragraph, Block, Style, Color

async def main():
    async with AsyncTerminal() as term:
        async for ev in term.events(fps=30):
            def ui(frame):
                frame.render_widget(
                    Paragraph.from_string("Async pyratatui! Press q to quit.")
                        .block(Block().bordered().title("Hello Async"))
                        .style(Style().fg(Color.green())),
                    frame.area,
                )
            term.draw(ui)
            # events() auto-stops on 'q' (stop_on_quit=True by default)

asyncio.run(main())
```

---

## Live Dashboard with Background Tasks

The pattern for reactive data is:

1. Store shared mutable state in a plain dict (or dataclass).
2. Launch background coroutines that update the state.
3. In the render loop, read and snapshot the current state into the draw closure.

```python
import asyncio
import random
import time
from pyratatui import (
    AsyncTerminal,
    Layout, Constraint, Direction,
    Block, Paragraph, Gauge, Sparkline,
    Style, Color, Text, Line, Span,
)

# ── Shared state ──────────────────────────────────────────────────────────────
state = {
    "cpu": 0,
    "mem": 50,
    "requests": 0,
    "history": [0] * 30,
    "tick": 0,
    "log": [],
}


# ── Background task ───────────────────────────────────────────────────────────

async def simulate_metrics():
    """Updates state every 300 ms — runs concurrently with the render loop."""
    while True:
        await asyncio.sleep(0.3)
        state["cpu"] = max(0, min(100, state["cpu"] + random.randint(-8, 10)))
        state["mem"] = max(10, min(95, state["mem"] + random.randint(-3, 4)))
        state["requests"] += random.randint(10, 50)
        state["tick"] += 1
        state["history"].append(state["cpu"])
        state["history"] = state["history"][-30:]
        if state["tick"] % 5 == 0:
            ts = time.strftime("%H:%M:%S")
            state["log"].append(f"[{ts}] tick {state['tick']}")
            state["log"] = state["log"][-6:]


# ── Render function ───────────────────────────────────────────────────────────

def build_ui(frame, cpu, mem, reqs, hist, log, tick):
    area = frame.area
    outer = (
        Layout()
        .direction(Direction.Vertical)
        .constraints([
            Constraint.length(3),   # CPU gauge
            Constraint.length(3),   # MEM gauge
            Constraint.length(5),   # Sparkline
            Constraint.fill(1),     # Stats + log
            Constraint.length(1),   # Footer
        ])
        .split(area)
    )

    cpu_color = (
        Color.green() if cpu < 50 else
        Color.yellow() if cpu < 80 else
        Color.red()
    )

    # CPU gauge
    frame.render_widget(
        Gauge()
            .percent(cpu)
            .label(f"CPU: {cpu}%  (tick {tick})")
            .style(Style().fg(cpu_color))
            .gauge_style(Style().fg(Color.dark_gray()))
            .block(Block().bordered().title("CPU")),
        outer[0],
    )

    # Memory gauge
    frame.render_widget(
        Gauge()
            .percent(mem)
            .label(f"MEM: {mem}%")
            .style(Style().fg(Color.blue()))
            .gauge_style(Style().fg(Color.dark_gray()))
            .block(Block().bordered().title("Memory")),
        outer[1],
    )

    # CPU history sparkline
    frame.render_widget(
        Sparkline()
            .data([int(h) for h in hist])
            .max(100)
            .style(Style().fg(cpu_color))
            .block(Block().bordered().title("CPU History (30 samples)")),
        outer[2],
    )

    # Stats and log side-by-side
    body = (
        Layout()
        .direction(Direction.Horizontal)
        .constraints([Constraint.percentage(40), Constraint.fill(1)])
        .split(outer[3])
    )

    frame.render_widget(
        Paragraph(Text([
            Line([
                Span("Requests: ", Style().bold()),
                Span(f"{reqs:,}", Style().fg(Color.cyan())),
            ]),
            Line([
                Span("Uptime:   ", Style().bold()),
                Span(f"{tick * 0.3:.1f}s", Style().fg(Color.green())),
            ]),
        ])).block(Block().bordered().title("Stats")),
        body[0],
    )

    frame.render_widget(
        Paragraph.from_string("\n".join(log) or "(waiting…)")
            .block(Block().bordered().title("Log"))
            .style(Style().fg(Color.gray())),
        body[1],
    )

    frame.render_widget(
        Paragraph.from_string(" q: Quit  (auto-refreshing)")
            .style(Style().fg(Color.dark_gray())),
        outer[4],
    )


# ── Main ──────────────────────────────────────────────────────────────────────

async def main():
    metrics_task = asyncio.create_task(simulate_metrics())

    async with AsyncTerminal() as term:
        term.hide_cursor()

        async for ev in term.events(fps=20):
            # Snapshot state for this frame
            cpu   = state["cpu"]
            mem   = state["mem"]
            reqs  = state["requests"]
            hist  = list(state["history"])
            log   = list(state["log"])
            tick  = state["tick"]

            # Capture snapshots into closure default args to avoid late-binding
            def ui(frame, _cpu=cpu, _mem=mem, _reqs=reqs,
                   _hist=hist, _log=log, _tick=tick):
                build_ui(frame, _cpu, _mem, _reqs, _hist, _log, _tick)

            term.draw(ui)

        term.show_cursor()

    metrics_task.cancel()
    try:
        await metrics_task
    except asyncio.CancelledError:
        pass


asyncio.run(main())
```

---

## `events()` Generator

`AsyncTerminal.events()` is an async generator that drives the render loop:

```python
async for ev in term.events(fps=30, stop_on_quit=True):
    term.draw(ui)
    if ev:
        handle(ev)
```

Each iteration:

1. Non-blocking `poll_event(0)` on the main thread.
2. Yields the `KeyEvent` (or `None` if no key was pressed this tick).
3. Sleeps the remainder of the frame interval via `await asyncio.sleep(...)`, giving background coroutines CPU time.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `fps` | `float` | `30.0` | Target frames per second |
| `stop_on_quit` | `bool` | `True` | Auto-stop on `q` or `Ctrl+C` |

---

## Manual Event Polling

If you need finer control, use `await term.poll_event()` directly:

```python
async with AsyncTerminal() as term:
    while True:
        ev = await term.poll_event()
        term.draw(ui)
        if ev and ev.code == "q":
            break
        await asyncio.sleep(1 / 30)  # ~30 fps
```

---

## Multiple Background Tasks

You can run multiple concurrent tasks — they all share the same state dict:

```python
async def fetch_cpu():
    while True:
        state["cpu"] = await read_cpu_from_system()
        await asyncio.sleep(0.5)

async def fetch_network():
    while True:
        state["net_in"], state["net_out"] = await read_network_stats()
        await asyncio.sleep(1.0)

async def main():
    tasks = [
        asyncio.create_task(fetch_cpu()),
        asyncio.create_task(fetch_network()),
    ]
    async with AsyncTerminal() as term:
        async for ev in term.events(fps=25):
            term.draw(ui)
    for t in tasks:
        t.cancel()
    await asyncio.gather(*tasks, return_exceptions=True)
```

---

## Using `run_app_async`

For simple apps, use the convenience helper:

```python
from pyratatui import run_app_async

async def my_ui(frame):
    frame.render_widget(
        Paragraph.from_string("Simple async app!"),
        frame.area,
    )

asyncio.run(run_app_async(my_ui, fps=30))
```

`run_app_async` creates an `AsyncTerminal`, drives the event loop at `fps`, and quits on `q` or `Ctrl+C`.

---

## Best Practices

- **Always cancel tasks on exit.** Use `try/except asyncio.CancelledError` to suppress the cancellation noise.
- **Never mutate state from the draw function.** The draw callback runs synchronously inside `term.draw()`. Mutations from there are safe but should be avoided — keep rendering purely functional.
- **Snapshot state per frame.** Copy mutable containers (`list(state["history"])`) before passing to the draw closure to avoid tearing if a background task mutates state mid-render.
- **Keep draw functions fast.** The event loop is blocked while `term.draw()` executes. Complex rendering (large tables, many widgets) should complete in under 2 ms.
- **Use `term.hide_cursor()`** at the start and `term.show_cursor()` at the end to prevent the cursor blinking over your UI.
