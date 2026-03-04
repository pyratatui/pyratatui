# Progress Bar

## Sync Progress Bar

```python
import time
from pyratatui import Terminal, Gauge, Block, Style, Color, Layout, Constraint, Paragraph

def run_with_progress():
    steps = 100
    with Terminal() as term:
        for i in range(steps + 1):
            pct = i
            label = f"{pct}%"

            def ui(frame, _pct=pct, _label=label):
                chunks = (
                    Layout()
                    .direction_vertical()
                    .constraints([Constraint.fill(1), Constraint.length(3)])
                    .split(frame.area)
                )
                frame.render_widget(
                    Paragraph.from_string("Processing…")
                        .block(Block().bordered().title("Task")),
                    chunks[0],
                )
                frame.render_widget(
                    Gauge()
                        .percent(_pct)
                        .label(_label)
                        .style(Style().fg(Color.green()))
                        .gauge_style(Style().fg(Color.dark_gray()))
                        .block(Block().bordered()),
                    chunks[1],
                )
            term.draw(ui)
            time.sleep(0.05)

run_with_progress()
```

## Async Progress Bar

```python
import asyncio
from pyratatui import AsyncTerminal, Gauge, Block, Style, Color

async def main():
    total = 50
    progress = {"value": 0}

    async def worker():
        for _ in range(total):
            await asyncio.sleep(0.1)
            progress["value"] += 1

    async with AsyncTerminal() as term:
        task = asyncio.create_task(worker())

        async for _ in term.events(fps=20, stop_on_quit=False):
            pct = int(progress["value"] / total * 100)

            def ui(frame, p=pct):
                frame.render_widget(
                    Gauge()
                        .percent(p)
                        .label(f"{p}%")
                        .style(Style().fg(Color.cyan()))
                        .block(Block().bordered().title("Async Progress")),
                    frame.area,
                )
            term.draw(ui)

            if progress["value"] >= total:
                break

        await task

asyncio.run(main())
```

## LineGauge Variant

```python
from pyratatui import Terminal, LineGauge, Style, Color

with Terminal() as term:
    for i in range(101):
        def ui(frame, pct=i):
            frame.render_widget(
                LineGauge()
                    .percent(pct)
                    .style(Style().fg(Color.blue()))
                    .gauge_style(Style().fg(Color.dark_gray()))
                    .line_set("thick"),
                frame.area,
            )
        term.draw(ui)
        import time; time.sleep(0.03)
```
