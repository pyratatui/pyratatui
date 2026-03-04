# Async Updates

pyratatui supports asyncio natively via `AsyncTerminal`.

## AsyncTerminal

```python
import asyncio
from pyratatui import AsyncTerminal, Paragraph, Layout, Constraint, Block, Style, Color

async def main():
    tick = 0

    async with AsyncTerminal() as term:
        async for ev in term.events(fps=30):
            def ui(frame):
                chunks = (
                    Layout()
                    .direction_vertical()
                    .constraints([Constraint.fill(1), Constraint.length(1)])
                    .split(frame.area)
                )
                frame.render_widget(
                    Paragraph.from_string(f"Tick {tick}")
                        .block(Block().bordered().title("Async Demo")),
                    chunks[0],
                )
                frame.render_widget(
                    Paragraph.from_string(" q: Quit"),
                    chunks[1],
                )
            term.draw(ui)
            tick += 1

asyncio.run(main())
```

## Background Tasks

Combine with asyncio tasks for background data fetching:

```python
import asyncio
from pyratatui import AsyncTerminal, Paragraph

data = {"value": 0}

async def fetch_data():
    """Simulate background I/O."""
    while True:
        await asyncio.sleep(0.5)
        data["value"] += 1

async def main():
    fetch_task = asyncio.create_task(fetch_data())
    try:
        async with AsyncTerminal() as term:
            async for ev in term.events(fps=10):
                def ui(frame):
                    frame.render_widget(
                        Paragraph.from_string(f"Value: {data['value']}"),
                        frame.area,
                    )
                term.draw(ui)
    finally:
        fetch_task.cancel()

asyncio.run(main())
```

## run_app_async

```python
import asyncio
from pyratatui import run_app_async, Paragraph

tick = 0

async def main():
    global tick

    async def ui(frame):
        frame.render_widget(
            Paragraph.from_string(f"Async: {tick}"),
            frame.area,
        )
        tick += 1

    await run_app_async(ui)

asyncio.run(main())
```
