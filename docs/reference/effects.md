# Effects Reference (TachyonFX)

pyratatui integrates [tachyonfx](https://github.com/ratatui/tachyonfx) —
a shader-like effects and animation library for terminal UIs.

## How Effects Work

TachyonFX effects are **stateful post-processors**: they transform terminal buffer
cells *after* your widgets have been rendered. The flow is:

```
┌──────────────────────────────────────┐
│  1. frame.render_widget(...)         │  ← Widget draws into buffer
│  2. mgr.process(elapsed_ms, buf, area) │  ← Effects transform buffer cells
│  3. Terminal flushes buffer          │  ← User sees result
└──────────────────────────────────────┘
```

---

## Interpolation

Easing curves that control the tempo of an effect.

```python
from pyratatui import Interpolation

# Available variants:
Interpolation.Linear
Interpolation.QuadIn / QuadOut / QuadInOut
Interpolation.CubicIn / CubicOut / CubicInOut
Interpolation.QuartIn / QuartOut / QuartInOut
Interpolation.QuintIn / QuintOut / QuintInOut
Interpolation.SineIn / SineOut / SineInOut
Interpolation.CircIn / CircOut / CircInOut
Interpolation.ExpoIn / ExpoOut / ExpoInOut
Interpolation.ElasticIn / ElasticOut
Interpolation.BounceIn / BounceOut / BounceInOut
Interpolation.BackIn / BackOut / BackInOut
```

---

## Motion

Directional constants for slide/sweep effects.

```python
from pyratatui import Motion

Motion.LeftToRight
Motion.RightToLeft
Motion.UpToDown
Motion.DownToUp
```

---

## EffectTimer

Controls duration and easing for a single effect.

```python
from pyratatui import EffectTimer, Interpolation

timer = EffectTimer(500, Interpolation.BounceOut)   # 500ms, bounce easing
linear = EffectTimer(1000)                           # 1s, linear (default)
```

---

## CellFilter

Selects which buffer cells an effect is applied to.

```python
from pyratatui import CellFilter, Color

CellFilter.all()                        # All cells (no filter)
CellFilter.text()                       # Only non-empty cells
CellFilter.fg_color(Color.red())        # Only cells with red fg
CellFilter.bg_color(Color.black())      # Only cells with black bg
CellFilter.inner(1, 1)                  # Inner area (exclude border)
CellFilter.outer(1, 1)                  # Border cells only
CellFilter.all_of([f1, f2])            # Must match ALL filters
CellFilter.any_of([f1, f2])            # Must match ANY filter
```

---

## Effect

The main animation type. All effects are created via static factory methods.

### Color Transitions

```python
from pyratatui import Effect, Color, Interpolation

# Fade in from black (bg and fg)
e = Effect.fade_from(Color.black(), Color.black(), 600, Interpolation.QuadOut)

# Fade only foreground from black
e = Effect.fade_from_fg(Color.black(), 500, Interpolation.SineOut)

# Fade to a target color
e = Effect.fade_to(Color.black(), Color.black(), 400)
e = Effect.fade_to_fg(Color.white(), 300)
```

### Text Materialization

```python
# Text coalesces (appears) from noise
e = Effect.coalesce(500, Interpolation.SineIn)

# Text dissolves into noise
e = Effect.dissolve(800, Interpolation.BounceOut)
```

### Sliding & Sweeping

```python
from pyratatui import Motion

# Slide content in/out
e = Effect.slide_in(Motion.LeftToRight, 600, Interpolation.QuadOut)
e = Effect.slide_out(Motion.RightToLeft, 400)

# Sweep with background fill
e = Effect.sweep_in(Motion.UpToDown, sweep_span=15, gradient_len=0,
                    color=Color.black(), duration_ms=600,
                    interpolation=Interpolation.QuadOut)
e = Effect.sweep_out(Motion.DownToUp, 15, 0, Color.black(), 600)
```

### Timing

```python
# Pause for N ms (useful in sequences)
e = Effect.sleep(300)
```

### Composition

```python
# Run effects one after another
seq = Effect.sequence([
    Effect.coalesce(400, Interpolation.SineOut),
    Effect.sleep(200),
    Effect.dissolve(500, Interpolation.BounceOut),
])

# Run effects simultaneously
par = Effect.parallel([
    Effect.fade_from_fg(Color.black(), 500),
    Effect.slide_in(Motion.LeftToRight, 600),
])

# Loop effects
looped = Effect.repeat(Effect.coalesce(500), times=3)  # -1 = infinite
bouncing = Effect.ping_pong(Effect.fade_from_fg(Color.black(), 800))
eternal = Effect.never_complete(Effect.dissolve(500))
```

### Cell Filtering

```python
e = Effect.coalesce(500)
e.with_filter(CellFilter.text())          # Only apply to text cells
e.with_filter(CellFilter.fg_color(Color.red()))  # Only red text
```

### Runtime Control

```python
e.done()    # True when effect has completed
e.reset()   # Restart the effect from the beginning
e.process(elapsed_ms, buffer, area)   # Advance and apply directly
```

---

## EffectManager

Manages a collection of running effects with automatic cleanup.

```python
from pyratatui import EffectManager, Effect, Color, Interpolation

mgr = EffectManager()

# Add regular effects (run until complete, then removed)
mgr.add(Effect.fade_from_fg(Color.black(), 800, Interpolation.SineOut))

# Add named effects (new effect with same key cancels the old one)
mgr.add_unique("header_fade", Effect.coalesce(500))
mgr.add_unique("header_fade", Effect.dissolve(300))  # cancels the above

# Process all effects each frame
mgr.process(elapsed_ms, buffer, area)

# Inspect state
mgr.active_count()   # number of running effects
mgr.has_active()     # bool
mgr.clear()          # cancel all effects
```

---

## DSL (Domain Specific Language)

Compile effects from text strings at runtime — useful for config files,
live reloading, and user-customizable animations.

```python
from pyratatui import compile_effect

# Simple
e = compile_effect("fx::dissolve(500)")

# With easing shorthand
e = compile_effect("fx::coalesce((400, BounceOut))")

# With color
e = compile_effect("fx::fade_from_fg(Color::Black, (600, QuadOut))")

# Complex composition
e = compile_effect("""
    fx::sequence(&[
        fx::fade_from(Color::Black, Color::Black, (400, SineOut)),
        fx::sleep(200),
        fx::dissolve((500, BounceOut))
    ])
""")

# With let bindings
e = compile_effect("""
    let color = Color::from_u32(0xff5500);
    let timer = (800, ElasticOut);
    fx::fade_to_fg(color, timer)
""")
```

DSL features:
- All `fx::*` functions are available
- Enum variants can be unqualified (`BounceOut` instead of `Interpolation::BounceOut`)
- Timer shorthand: `(ms, Easing)` instead of `EffectTimer::from_ms(ms, Easing)`
- Method chaining: `fx::dissolve(500).with_filter(CellFilter::Text)`
- `let` bindings for reusable values

---

## Complete Example

```python
import time
from pyratatui import (
    Terminal, Buffer, Paragraph, Block,
    Effect, EffectManager, Interpolation, CellFilter, Color,
)

mgr = EffectManager()
mgr.add(Effect.fade_from_fg(Color.black(), 800, Interpolation.SineOut))

last = time.time()

with Terminal() as term:
    while True:
        now = time.time()
        elapsed_ms = int((now - last) * 1000)
        last = now

        def ui(frame):
            area = frame.area
            frame.render_widget(
                Paragraph.from_string("Hello Effects!")
                    .block(Block().bordered().title("TachyonFX")),
                area,
            )
            # Apply running effects to this frame's buffer
            # (advanced: access via frame.buffer_mut_ptr in Rust extensions)

        term.draw(ui)

        ev = term.poll_event(timeout_ms=16)
        if ev and ev.code == "q":
            break
```
