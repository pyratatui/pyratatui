# Effects (TachyonFX) Reference

TachyonFX is a post-render animation engine integrated into pyratatui. Effects are applied to the frame buffer *after* widgets are rendered, transforming the already-drawn cells.

---

## Rendering Order

```
frame.render_widget(...)         ← 1. Draw widgets into buffer
frame.apply_effect_manager(...)  ← 2. Apply effects to buffer cells
```

Effects applied before widget rendering operate on blank or stale cells and will not produce meaningful results.

---

## Effect

```python
from pyratatui import Effect
```

A stateful animation shader. All factory methods are static — `Effect` is never instantiated directly.

### Color Fade

#### `Effect.fade_from(from_bg, from_fg, duration_ms, interpolation=None)`

Transitions both background and foreground colors from the given colors to the widget's actual rendered colors.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `from_bg` | `Color` | required | Starting background color |
| `from_fg` | `Color` | required | Starting foreground color |
| `duration_ms` | `int` | required | Duration in milliseconds |
| `interpolation` | `Interpolation \| None` | `Linear` | Easing curve |

```python
# Fade in from black
effect = Effect.fade_from(Color.black(), Color.black(), 1000, Interpolation.SineOut)
```

#### `Effect.fade_from_fg(from_color, duration_ms, interpolation=None)`

Transitions only the foreground color. Background is unaffected.

```python
effect = Effect.fade_from_fg(Color.black(), 800, Interpolation.QuadOut)
```

#### `Effect.fade_to(to_bg, to_fg, duration_ms, interpolation=None)`

Transitions both colors toward the given target colors.

```python
# Fade out to black
effect = Effect.fade_to(Color.black(), Color.black(), 1000, Interpolation.SineIn)
```

#### `Effect.fade_to_fg(to_color, duration_ms, interpolation=None)`

Transitions only the foreground toward `to_color`.

```python
effect = Effect.fade_to_fg(Color.black(), 800, Interpolation.QuadIn)
```

---

### Text Materialization

#### `Effect.coalesce(duration_ms, interpolation=None)`

Text characters appear to coalesce (assemble from random positions).

```python
effect = Effect.coalesce(1200, Interpolation.QuadOut)
```

#### `Effect.dissolve(duration_ms, interpolation=None)`

Text characters dissolve into random positions.

```python
effect = Effect.dissolve(600, Interpolation.QuadIn)
```

---

### Sliding

#### `Effect.slide_in(direction, begin_sweep=0, end_sweep=0, color=None, duration_ms=500, interpolation=None)`

Content slides in from the specified direction.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `direction` | `Motion` | required | Direction to slide from |
| `begin_sweep` | `int` | `0` | Leading edge width |
| `end_sweep` | `int` | `0` | Trailing edge width |
| `color` | `Color \| None` | `Color.black()` | Color of the sweep edge |
| `duration_ms` | `int` | `500` | Duration |
| `interpolation` | `Interpolation \| None` | `Linear` | Easing |

```python
effect = Effect.slide_in(Motion.LeftToRight, duration_ms=600, interpolation=Interpolation.QuadOut)
```

#### `Effect.slide_out(direction, begin_sweep=0, end_sweep=0, color=None, duration_ms=500, interpolation=None)`

Content slides out in the specified direction.

```python
effect = Effect.slide_out(Motion.RightToLeft, duration_ms=400)
```

---

### Sweeping

#### `Effect.sweep_in(direction, sweep_span=15, gradient_len=0, color=None, duration_ms=600, interpolation=None)`

A reveal sweep from the given direction.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `direction` | `Motion` | required | Sweep direction |
| `sweep_span` | `int` | `15` | Width of the sweep front |
| `gradient_len` | `int` | `0` | Gradient fade length |
| `color` | `Color \| None` | `Color.black()` | Sweep color |
| `duration_ms` | `int` | `600` | Duration |
| `interpolation` | `Interpolation \| None` | `Linear` | Easing |

```python
effect = Effect.sweep_in(
    Motion.LeftToRight,
    sweep_span=20,
    gradient_len=5,
    color=Color.black(),
    duration_ms=800,
    interpolation=Interpolation.QuadOut,
)
```

#### `Effect.sweep_out(direction, sweep_span=15, gradient_len=0, color=None, duration_ms=600, interpolation=None)`

A conceal sweep.

---

### Timing

#### `Effect.sleep(duration_ms)`

A no-op delay. Useful as a pause inside sequences.

```python
Effect.sleep(500)  # hold for 500ms
```

---

### Composition

#### `Effect.sequence(effects: list[Effect])`

Play effects one after another. Each starts when the previous completes.

```python
intro = Effect.sequence([
    Effect.fade_from_fg(Color.black(), 800),
    Effect.sleep(300),
    Effect.fade_to_fg(Color.black(), 600),
])
```

#### `Effect.parallel(effects: list[Effect])`

Play all effects simultaneously. Completes when all effects are done.

```python
combo = Effect.parallel([
    Effect.coalesce(1000),
    Effect.fade_from(Color.black(), Color.black(), 500),
])
```

#### `Effect.repeat(effect, times=-1)`

Repeat an effect `times` times. Pass `-1` (default) for infinite looping.

```python
blink = Effect.repeat(
    Effect.fade_to_fg(Color.black(), 400),
    times=3,
)

forever = Effect.repeat(Effect.coalesce(800), times=-1)
```

#### `Effect.ping_pong(effect)`

Play the effect forward, then backward, forever.

```python
pulse = Effect.ping_pong(
    Effect.fade_from_fg(Color.black(), 1000, Interpolation.SineInOut)
)
```

#### `Effect.never_complete(effect)`

Wraps an effect so it never reports `done()=True`. Useful for looping effects that you want to manage manually.

---

### Instance Methods

#### `.with_filter(filter: CellFilter)`

Restrict the effect to a subset of cells. Mutates the effect in-place.

```python
effect = Effect.coalesce(800)
effect.with_filter(CellFilter.text())  # only affect text cells
```

#### `.process(elapsed_ms, buffer, area)`

Manually advance the effect. Normally called via `frame.apply_effect_manager()`.

#### `.done() → bool`

Returns `True` if the effect has completed.

#### `.reset()`

Restart the effect from the beginning.

---

## EffectManager

```python
from pyratatui import EffectManager
```

Manages a list of active effects, auto-removing completed ones each frame.

### Constructor

```python
mgr = EffectManager()
```

### Methods

#### `.add(effect: Effect)`

Add an effect to the manager. The effect runs until `done()`.

```python
mgr.add(Effect.fade_from_fg(Color.black(), 1000))
```

#### `.add_unique(key: str, effect: Effect)`

Add a named effect, replacing any existing effect registered under the same key.

```python
mgr.add_unique("startup", Effect.sweep_in(Motion.LeftToRight, 15, 0, Color.black(), 800))
```

#### `.process(elapsed_ms, buffer, area)`

Advance all effects and remove completed ones. Called automatically via `frame.apply_effect_manager()`.

#### `.active_count() → int`

Number of currently running effects.

#### `.has_active() → bool`

`True` if any effect is still running.

#### `.clear()`

Remove all effects immediately.

### Usage Pattern

```python
import time

mgr   = EffectManager()
last  = time.monotonic()

# Add startup animation
mgr.add(Effect.sweep_in(Motion.LeftToRight, sweep_span=20, duration_ms=800))

with Terminal() as term:
    while True:
        now = time.monotonic()
        ms  = int((now - last) * 1000)
        last = now

        def ui(frame, _mgr=mgr, _ms=ms):
            area = frame.area
            frame.render_widget(my_widget, area)          # 1. render
            frame.apply_effect_manager(_mgr, _ms, area)  # 2. animate

        term.draw(ui)
        ev = term.poll_event(timeout_ms=16)
        if ev and ev.code == "q":
            break
```

---

## CellFilter

```python
from pyratatui import CellFilter
```

Restricts which buffer cells an effect transforms.

### Factory Methods

| Method | Description |
|---|---|
| `CellFilter.all()` | All cells in the area |
| `CellFilter.text()` | Only cells with non-space foreground (text cells) |
| `CellFilter.fg_color(color)` | Only cells with matching foreground color |
| `CellFilter.bg_color(color)` | Only cells with matching background color |
| `CellFilter.inner(horizontal=1, vertical=1)` | Only cells inside the margin |
| `CellFilter.outer(horizontal=1, vertical=1)` | Only cells in the margin (borders) |
| `CellFilter.all_of(filters)` | Intersection of multiple filters |
| `CellFilter.any_of(filters)` | Union of multiple filters |

### Example

```python
# Fade only text, not border cells
effect = Effect.fade_from_fg(Color.black(), 800)
effect.with_filter(CellFilter.text())

# Fade only cyan cells (e.g. highlights)
effect2 = Effect.dissolve(600)
effect2.with_filter(CellFilter.fg_color(Color.cyan()))

# Affect only the interior (skip borders)
effect3 = Effect.coalesce(1000)
effect3.with_filter(CellFilter.inner(horizontal=1, vertical=1))
```

---

## Interpolation

```python
from pyratatui import Interpolation
```

Easing curves that control the acceleration profile of an effect.

| Enum value | Behavior |
|---|---|
| `Linear` | Constant speed |
| `QuadIn` / `QuadOut` / `QuadInOut` | Quadratic (gentle) |
| `CubicIn` / `CubicOut` / `CubicInOut` | Cubic (moderate) |
| `QuartIn` / `QuartOut` / `QuartInOut` | Quartic (strong) |
| `QuintIn` / `QuintOut` / `QuintInOut` | Quintic (very strong) |
| `SineIn` / `SineOut` / `SineInOut` | Sinusoidal (natural) |
| `ExpoIn` / `ExpoOut` / `ExpoInOut` | Exponential (dramatic) |
| `CircIn` / `CircOut` / `CircInOut` | Circular |
| `ElasticIn` / `ElasticOut` | Elastic/spring overshoot |
| `BounceIn` / `BounceOut` / `BounceInOut` | Bouncing |
| `BackIn` / `BackOut` / `BackInOut` | Slight overshoot |

The `In` suffix = starts slow (accelerates). `Out` = starts fast (decelerates). `InOut` = slow-fast-slow.

**Recommended combinations:**
- Fade-in: `SineOut` or `QuadOut` (fast start, gentle finish)
- Fade-out: `SineIn` or `QuadIn` (gentle start, fast end)
- Sweep/slide: `QuadOut` or `CubicOut` (punchy reveal)
- Ping-pong: `SineInOut` (smooth oscillation)

---

## Motion

```python
from pyratatui import Motion

Motion.LeftToRight
Motion.RightToLeft
Motion.UpToDown
Motion.DownToUp
```

Direction used by slide and sweep effects.

---

## EffectTimer

```python
from pyratatui import EffectTimer
```

A duration + interpolation pair. Used internally by effects but also constructable directly:

```python
timer = EffectTimer(duration_ms=1000, interpolation=Interpolation.SineOut)
```

| Property | Type | Description |
|---|---|---|
| `duration_ms` | `int` | Duration in milliseconds |
| `interpolation` | `Interpolation` | Easing curve |

---

## DSL Compiler

```python
from pyratatui import compile_effect

effect = compile_effect("expression")
```

Compile a tachyonfx DSL expression string into an `Effect`. Raises `ValueError` on parse or compile errors.

The DSL supports all built-in effects with duration in milliseconds and optional interpolation:

```python
effect = compile_effect("fade_from_fg(black, 800ms, sine_out)")
```

---

## Best Practices

**Track elapsed time accurately.** Pass the actual wall-clock time since the last frame (not a fixed value):

```python
last = time.monotonic()
while True:
    now = time.monotonic()
    elapsed_ms = int((now - last) * 1000)
    last = now
    # ... render and apply effects with elapsed_ms
```

**Apply effects after all widget renders.** Effects transform cells in the buffer; if you render widgets after applying effects, the widget will overwrite the animated cells.

**Use `EffectManager` for multiple effects.** It auto-cleans completed effects so you don't need to manually track `effect.done()`.

**Use `add_unique` for retriggerable effects.** If a user action triggers an animation (e.g. row selection change), `add_unique` prevents the same effect from stacking:

```python
mgr.add_unique("selection", Effect.coalesce(300, Interpolation.QuadOut))
```

**Limit effect area.** Smaller areas process faster. For widget-specific effects, pass the widget's `Rect` rather than `frame.area`.
