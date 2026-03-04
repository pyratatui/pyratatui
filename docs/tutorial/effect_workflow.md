# Effect Workflow Tutorial

This tutorial walks through integrating TachyonFX effects into a real pyratatui application.

## The Effect Lifecycle

```
Create → Add to Manager → Process each frame → Effect completes → Removed automatically
```

## Step 1: Create Effects

```python
from pyratatui import Effect, Interpolation, Color

# Fade in from black over 800ms with smooth easing
fade_in = Effect.fade_from_fg(Color.black(), 800, Interpolation.SineOut)

# Dissolve out over 600ms with bounce
fade_out = Effect.dissolve(600, Interpolation.BounceOut)

# Sequence them
transition = Effect.sequence([fade_in, Effect.sleep(500), fade_out])
```

## Step 2: Create a Manager

```python
from pyratatui import EffectManager

mgr = EffectManager()
mgr.add(transition)
```

## Step 3: Process in the Draw Loop

```python
import time

last = time.time()

with Terminal() as term:
    while True:
        now = time.time()
        elapsed_ms = int((now - last) * 1000)
        last = now

        def ui(frame):
            area = frame.area
            # 1. Render your widgets
            frame.render_widget(my_widget, area)

        term.draw(ui)
        # (mgr.process is called with the buffer inside Rust via Frame integration)
        # For pure Python, track timing and drive effect logic here

        ev = term.poll_event(timeout_ms=16)
        if ev and ev.code == "q":
            break
```

## Targeted Effects with CellFilter

Apply effects only to specific parts of the buffer:

```python
from pyratatui import Effect, CellFilter, Color

# Only fade text cells (not background/empty)
e = Effect.coalesce(500)
e.with_filter(CellFilter.text())

# Only affect cells with a specific fg color
e = Effect.dissolve(400)
e.with_filter(CellFilter.fg_color(Color.cyan()))

# Only the border region
border_only = CellFilter.all_of([
    CellFilter.outer(1, 1),
    CellFilter.text(),
])
e = Effect.fade_from_fg(Color.black(), 600)
e.with_filter(border_only)
```

## Using the DSL for Config-Driven Effects

```python
from pyratatui import compile_effect, EffectManager

# Load effect definitions from a config file
EFFECTS_CONFIG = {
    "startup": "fx::coalesce((600, SineOut))",
    "shutdown": "fx::dissolve((400, BounceOut))",
    "highlight": """
        fx::sequence(&[
            fx::fade_to_fg(Color::Yellow, (200, QuadOut)),
            fx::sleep(500),
            fx::fade_from_fg(Color::Yellow, (200, QuadIn))
        ])
    """,
}

effects = {name: compile_effect(expr) for name, expr in EFFECTS_CONFIG.items()}
mgr = EffectManager()
mgr.add(effects["startup"])
```

## Async Effect Updates

```python
import asyncio
from pyratatui import AsyncTerminal, EffectManager, Effect, Color, Interpolation

async def main():
    mgr = EffectManager()

    async with AsyncTerminal() as term:
        # Startup animation
        mgr.add(Effect.fade_from_fg(Color.black(), 1000, Interpolation.SineOut))

        async for ev in term.events(fps=60):
            def ui(frame):
                frame.render_widget(my_widget, frame.area)
                # mgr integrates with frame buffer here

            term.draw(ui)

            if ev and ev.code == "q":
                # Fade out before quitting
                mgr.clear()
                mgr.add(Effect.fade_to_fg(Color.black(), 500))
                # Wait for effect to complete...
                break

asyncio.run(main())
```

## Named Effects (Cancellable)

Named effects cancel any previous effect with the same key:

```python
mgr = EffectManager()

# Highlight row 3
mgr.add_unique("row_highlight", Effect.fade_from_fg(Color.yellow(), 300))

# When user presses Down, cancel and highlight row 4
mgr.add_unique("row_highlight", Effect.fade_from_fg(Color.cyan(), 300))
# The row 3 effect is automatically cancelled
```
