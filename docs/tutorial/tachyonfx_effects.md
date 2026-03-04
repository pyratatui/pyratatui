# TachyonFX Effects

pyratatui ships with [tachyonfx](https://github.com/junkdog/tachyonfx) 0.11 — a post-render animation engine for ratatui. Effects are pixel-level transforms applied to the frame buffer *after* widgets have been rendered.

---

## How Effects Work

The critical insight is that effects are **post-render transforms** — they mutate cells that have already been drawn into the frame buffer:

```
1. frame.render_widget(...)      → write widget pixels into buffer
2. frame.apply_effect_manager()  → mutate those same pixels
```

Both steps happen **inside** the `term.draw(ui)` callback. The order matters: if you apply an effect before rendering widgets, the effect operates on blank/stale cells.

---

## Your First Fade Effect

```python
import time
from pyratatui import (
    Terminal, Paragraph, Block, Style, Color,
    Effect, EffectManager, Interpolation,
)

mgr  = EffectManager()
mgr.add(Effect.fade_from_fg(Color.black(), 1500, Interpolation.SineOut))

last = time.monotonic()

with Terminal() as term:
    term.hide_cursor()
    while True:
        now = time.monotonic()
        elapsed_ms = int((now - last) * 1000)
        last = now

        _ms = elapsed_ms
        def ui(frame, _mgr=mgr, ms=_ms):
            area = frame.area
            # Step 1: render widgets
            frame.render_widget(
                Paragraph.from_string("Fading in…")
                    .block(Block().bordered().title(" Fade Demo "))
                    .style(Style().fg(Color.white())),
                area,
            )
            # Step 2: apply effects
            frame.apply_effect_manager(_mgr, ms, area)

        term.draw(ui)
        ev = term.poll_event(timeout_ms=16)  # ~60 fps ceiling
        if ev and ev.code == "q":
            break
    term.show_cursor()
```

---

## Available Effects

### Color Fade Effects

| Factory | Description |
|---|---|
| `Effect.fade_from(from_bg, from_fg, ms)` | Transition both bg+fg from given colors to their rendered values |
| `Effect.fade_from_fg(from_color, ms)` | Transition only foreground color from `from_color` |
| `Effect.fade_to(to_bg, to_fg, ms)` | Transition both bg+fg to given colors |
| `Effect.fade_to_fg(to_color, ms)` | Fade foreground out to `to_color` |

### Text Materialization

| Factory | Description |
|---|---|
| `Effect.coalesce(ms)` | Particles assemble into text |
| `Effect.dissolve(ms)` | Text dissolves into particles |

### Sliding / Sweeping

| Factory | Description |
|---|---|
| `Effect.slide_in(direction, begin_sweep, end_sweep, color, ms)` | Slide content in from a direction |
| `Effect.slide_out(direction, begin_sweep, end_sweep, color, ms)` | Slide content out |
| `Effect.sweep_in(direction, sweep_span, gradient_len, color, ms)` | Sweep reveal |
| `Effect.sweep_out(direction, sweep_span, gradient_len, color, ms)` | Sweep conceal |

### Timing

| Factory | Description |
|---|---|
| `Effect.sleep(ms)` | No-op delay (useful in sequences) |

### Composition

| Factory | Description |
|---|---|
| `Effect.sequence(effects)` | Play effects one after another |
| `Effect.parallel(effects)` | Play effects simultaneously |
| `Effect.repeat(effect, times=-1)` | Repeat an effect; `-1` = forever |
| `Effect.ping_pong(effect)` | Play forward then backward, forever |
| `Effect.never_complete(effect)` | Prevent an effect from ever reporting done |

---

## Motion Directions

```python
from pyratatui import Motion

Motion.LeftToRight
Motion.RightToLeft
Motion.UpToDown
Motion.DownToUp
```

---

## Interpolation Curves

```python
from pyratatui import Interpolation

# Linear (default)
Interpolation.Linear

# Quadratic
Interpolation.QuadIn, Interpolation.QuadOut, Interpolation.QuadInOut

# Cubic, Quartic, Quintic (stronger acceleration)
Interpolation.CubicIn, Interpolation.CubicOut, Interpolation.CubicInOut
# ... QuartIn/Out/InOut, QuintIn/Out/InOut

# Sinusoidal (smooth)
Interpolation.SineIn, Interpolation.SineOut, Interpolation.SineInOut

# Exponential (sharp)
Interpolation.ExpoIn, Interpolation.ExpoOut, Interpolation.ExpoInOut

# Circular
Interpolation.CircIn, Interpolation.CircOut, Interpolation.CircInOut

# Elastic (overshoot + bounce)
Interpolation.ElasticIn, Interpolation.ElasticOut

# Bounce
Interpolation.BounceIn, Interpolation.BounceOut, Interpolation.BounceInOut

# Back (slight overshoot)
Interpolation.BackIn, Interpolation.BackOut, Interpolation.BackInOut
```

---

## Fade In / Out Cycle

The following example cycles between fade-in and fade-out continuously:

```python
import time
from pyratatui import (
    Terminal, Paragraph, Block, Style, Color,
    Effect, EffectManager, Interpolation,
)

CYCLE_MS = 2000
HOLD_MS  = 400

mgr         = EffectManager()
phase       = "in"
phase_start = time.monotonic()
last_frame  = time.monotonic()

mgr.add(Effect.fade_from_fg(Color.black(), CYCLE_MS, Interpolation.SineOut))

CONTENT = "Watch text fade in and out.\n\nPress q to quit."

with Terminal() as term:
    term.hide_cursor()
    while True:
        now           = time.monotonic()
        elapsed_ms    = int((now - last_frame) * 1000)
        last_frame    = now
        phase_elapsed = int((now - phase_start) * 1000)

        if not mgr.has_active():
            if phase == "in" and phase_elapsed >= HOLD_MS:
                phase = "out"
                phase_start = now
                mgr.add(Effect.fade_to_fg(Color.black(), CYCLE_MS, Interpolation.SineIn))
            elif phase == "out" and phase_elapsed >= HOLD_MS:
                phase = "in"
                phase_start = now
                mgr.add(Effect.fade_from_fg(Color.black(), CYCLE_MS, Interpolation.SineOut))

        _ms = elapsed_ms
        _ph = phase

        def ui(frame, _mgr=mgr, ms=_ms, ph=_ph):
            area = frame.area
            frame.render_widget(
                Paragraph.from_string(CONTENT)
                    .block(Block().bordered().title(f" Fade [{ph}] "))
                    .style(Style().fg(Color.white())),
                area,
            )
            frame.apply_effect_manager(_mgr, ms, area)

        term.draw(ui)
        ev = term.poll_event(timeout_ms=16)
        if ev and ev.code == "q":
            break
    term.show_cursor()
```

---

## Sweep-In on Startup

A one-shot sweep animation plays when the app starts, then the UI runs normally:

```python
import time
from pyratatui import (
    Terminal, Paragraph, Block, Style, Color,
    Effect, EffectManager, Motion, Interpolation,
)

mgr = EffectManager()
# One-shot sweep: play once and stop
mgr.add(Effect.sweep_in(Motion.LeftToRight,
                         sweep_span=20, gradient_len=5,
                         color=Color.black(),
                         duration_ms=800,
                         interpolation=Interpolation.QuadOut))

last = time.monotonic()

with Terminal() as term:
    term.hide_cursor()
    while True:
        now = time.monotonic()
        ms  = int((now - last) * 1000)
        last = now

        def ui(frame, _mgr=mgr, _ms=ms):
            area = frame.area
            frame.render_widget(
                Paragraph.from_string("Welcome to my app!\n\nLoading complete.")
                    .block(Block().bordered().title(" Startup "))
                    .style(Style().fg(Color.cyan())),
                area,
            )
            if _mgr.has_active():
                frame.apply_effect_manager(_mgr, _ms, area)

        term.draw(ui)
        ev = term.poll_event(timeout_ms=16)
        if ev and ev.code == "q":
            break
    term.show_cursor()
```

---

## Sequence and Parallel Composition

```python
from pyratatui import Effect, Interpolation, Color

# Sequential: fade in, hold 500ms, fade out
intro = Effect.sequence([
    Effect.fade_from_fg(Color.black(), 1000, Interpolation.SineOut),
    Effect.sleep(500),
    Effect.fade_to_fg(Color.black(), 800, Interpolation.SineIn),
])

# Parallel: coalesce text AND fade background simultaneously
combo = Effect.parallel([
    Effect.coalesce(1200, Interpolation.QuadOut),
    Effect.fade_from(Color.black(), Color.black(), 600),
])

# Looping: repeat an effect 3 times
loop3 = Effect.repeat(
    Effect.fade_from_fg(Color.black(), 500),
    times=3,
)

# Ping-pong: fade in then out, forever
ping_pong = Effect.ping_pong(
    Effect.fade_from_fg(Color.black(), 1000, Interpolation.SineInOut)
)

mgr = EffectManager()
mgr.add(intro)
```

---

## CellFilter — Apply Effects to a Subset of Cells

`CellFilter` restricts which cells an effect transforms:

```python
from pyratatui import Effect, CellFilter, Color, Interpolation

# Only affect text cells (non-space foreground)
effect = Effect.fade_from_fg(Color.black(), 800)
effect.with_filter(CellFilter.text())

# Only affect cells with a specific foreground color
effect2 = Effect.coalesce(600)
effect2.with_filter(CellFilter.fg_color(Color.cyan()))

# Only affect the inner area (exclude border cells)
effect3 = Effect.dissolve(500)
effect3.with_filter(CellFilter.inner(horizontal=1, vertical=1))

# Only affect the border/outer area
effect4 = Effect.fade_from_fg(Color.black(), 400)
effect4.with_filter(CellFilter.outer(horizontal=1, vertical=1))
```

---

## EffectManager

`EffectManager` maintains a list of active effects and auto-removes completed ones:

```python
from pyratatui import EffectManager, Effect, Color, Interpolation

mgr = EffectManager()

# Add effects
mgr.add(Effect.fade_from_fg(Color.black(), 1000))

# Add a named effect (replaces any previous with the same key)
mgr.add_unique("startup", Effect.sweep_in(Motion.LeftToRight, 15, 0, Color.black(), 800))

# Check state
print(mgr.active_count())   # number of running effects
print(mgr.has_active())     # bool

# Clear all effects
mgr.clear()
```

Inside the draw callback:

```python
frame.apply_effect_manager(mgr, elapsed_ms, area)
```

Or apply a single `Effect` directly:

```python
frame.apply_effect(effect, elapsed_ms, area)
```

---

## DSL Compiler

tachyonfx includes a text DSL for composing effects from strings:

```python
from pyratatui import compile_effect

# Compile a DSL expression into an Effect
effect = compile_effect("fade_from_fg(black, 800ms, sine_out)")
mgr.add(effect)
```

The DSL supports all built-in effects, timing, and composition. Raises `ValueError` on syntax errors.

---

## Performance Tips

- **Apply effects sparingly.** Each `process()` call iterates over every cell in `area`. For a full 80×24 terminal that is 1,920 cells per effect per frame.
- **Use `CellFilter`** to limit the area processed when you only need to affect part of the screen.
- **One-shot effects** (like startup sweeps) complete and are auto-removed from `EffectManager`, so they add zero overhead after finishing.
- **`EffectManager.add_unique`** prevents duplicate effects from stacking when a trigger fires multiple times.
- **Target fps 30–60.** The `elapsed_ms` passed to `apply_effect_manager` must reflect actual wall-clock time between frames, not a constant, so the animation progresses smoothly regardless of system load.
