# Layout Reference

The layout system splits a `Rect` into child `Rect`s based on sizing constraints. It mirrors ratatui's constraint-based layout engine.

---

## Rect

```python
from pyratatui import Rect
```

A rectangular region on the terminal screen defined by its top-left corner and dimensions. All values are in terminal cells (columns × rows).

### Constructor

```python
Rect(x: int, y: int, width: int, height: int)
```

| Parameter | Type | Description |
|---|---|---|
| `x` | `int` (u16) | Left column (0-based) |
| `y` | `int` (u16) | Top row (0-based) |
| `width` | `int` (u16) | Width in columns |
| `height` | `int` (u16) | Height in rows |

```python
r = Rect(0, 0, 80, 24)
```

### Properties (read-only)

| Property | Type | Description |
|---|---|---|
| `x` | `int` | Left column |
| `y` | `int` | Top row |
| `width` | `int` | Width in columns |
| `height` | `int` | Height in rows |
| `left` | `int` | Alias for `x` |
| `top` | `int` | Alias for `y` |
| `right` | `int` | Column just past the right edge (`x + width`) |
| `bottom` | `int` | Row just past the bottom edge (`y + height`) |

### Methods

#### `area() → int`

Total cell count: `width × height`.

#### `is_empty() → bool`

Returns `True` if `width == 0` or `height == 0`.

#### `inner(horizontal=1, vertical=1) → Rect`

Returns a new `Rect` shrunk by the given margin on each side.

```python
r = Rect(0, 0, 80, 24)
inner = r.inner(horizontal=2, vertical=1)
# inner.x=2, inner.y=1, inner.width=76, inner.height=22
```

| Parameter | Default | Description |
|---|---|---|
| `horizontal` | `1` | Columns to remove from left and right |
| `vertical` | `1` | Rows to remove from top and bottom |

#### `contains(other: Rect) → bool`

Returns `True` if `other` is fully contained within `self`.

#### `intersection(other: Rect) → Rect | None`

Returns the overlapping region, or `None` if the rectangles don't intersect.

#### `union(other: Rect) → Rect`

Returns the smallest bounding box that contains both rectangles.

---

## Constraint

```python
from pyratatui import Constraint
```

A sizing rule for a layout slot. All constraints are created via static factory methods.

### Factory Methods

| Method | Description | Example |
|---|---|---|
| `Constraint.length(n)` | Exactly `n` cells | `Constraint.length(3)` |
| `Constraint.percentage(pct)` | `pct`% of parent (0–100) | `Constraint.percentage(50)` |
| `Constraint.fill(weight)` | Proportional share of remaining space | `Constraint.fill(1)` |
| `Constraint.min(n)` | At least `n` cells | `Constraint.min(10)` |
| `Constraint.max(n)` | At most `n` cells | `Constraint.max(40)` |
| `Constraint.ratio(num, den)` | Fractional ratio `num/den` | `Constraint.ratio(1, 3)` |

### Constraint Behavior

**`length(n)`** — fixed size, never grows or shrinks regardless of available space. Use for toolbars, status lines, and fixed headers.

**`percentage(pct)`** — computed from the parent area before any fills. The percentage applies to the total space, not the remaining space.

**`fill(weight)`** — distributes remaining space after fixed and percentage constraints are satisfied. Two `fill(1)` constraints split remaining space equally; `fill(2)` + `fill(1)` gives a 2:1 split.

**`min(n)` / `max(n)`** — these are hints. ratatui's solver may adjust them to satisfy all constraints; they guarantee a floor or ceiling under normal conditions.

**`ratio(numerator, denominator)`** — similar to percentage but expressed as a fraction. `ratio(1, 3)` is equivalent to `percentage(33)` but avoids floating-point issues.

### Examples

```python
from pyratatui import Constraint

# Three-row layout: 3-row header, fill body, 1-row footer
[Constraint.length(3), Constraint.fill(1), Constraint.length(1)]

# Two equal columns
[Constraint.fill(1), Constraint.fill(1)]

# Sidebar + content (30% / 70%)
[Constraint.percentage(30), Constraint.percentage(70)]

# Three columns: fixed 20, flexible min-10, fill
[Constraint.length(20), Constraint.min(10), Constraint.fill(1)]
```

---

## Direction

```python
from pyratatui import Direction

Direction.Vertical    # top → bottom (default)
Direction.Horizontal  # left → right
```

Controls the axis along which `Layout.split()` divides the parent area.

---

## Alignment

```python
from pyratatui import Alignment

Alignment.Left    # default
Alignment.Center
Alignment.Right
```

Used for text and widget alignment within their containing area.

---

## Layout

```python
from pyratatui import Layout
```

The layout engine. Constructed with a fluent builder API and finalized with `.split(area)`.

### Constructor

```python
Layout()
```

Creates a new layout with defaults: `direction=Vertical`, `margin=0`, `spacing=0`, `flex=start`.

### Builder Methods

All builder methods return a **new** `Layout` instance (immutable builder pattern).

#### `.direction(dir: Direction) → Layout`

Set the split axis.

```python
layout = Layout().direction(Direction.Horizontal)
```

#### `.constraints(constraints: list[Constraint]) → Layout`

Set the sizing rules for each slot. The number of constraints determines the number of child `Rect`s returned by `.split()`.

```python
layout = Layout().constraints([
    Constraint.length(3),
    Constraint.fill(1),
    Constraint.length(1),
])
```

#### `.margin(margin: int) → Layout`

Apply a uniform margin on all sides of the parent area before splitting.

```python
layout = Layout().margin(1)  # 1-cell border around all children
```

#### `.spacing(spacing: int) → Layout`

Gap in cells between adjacent child slots.

```python
layout = Layout().spacing(1)  # 1-cell gap between slots
```

#### `.flex_mode(mode: str) → Layout`

Control how remaining space is distributed when `fill` constraints are present.

| Mode | Description |
|---|---|
| `"start"` (default) | Slots aligned to the start |
| `"end"` | Slots aligned to the end |
| `"center"` | Slots centered |
| `"space_between"` | Equal space between slots |
| `"space_around"` | Equal space around slots |

### `.split(area: Rect) → list[Rect]`

Compute and return child rectangles. The list has one entry per constraint.

```python
area = frame.area  # or any Rect
chunks = (
    Layout()
    .direction(Direction.Vertical)
    .constraints([
        Constraint.length(3),
        Constraint.fill(1),
        Constraint.length(1),
    ])
    .split(area)
)
header, body, footer = chunks
```

**Raises:** `LayoutError` if no constraints are set.

---

## Nested Layouts

Split recursively to build complex UIs:

```python
def ui(frame):
    area = frame.area

    # Outer: header / body / footer
    outer = (
        Layout()
        .direction(Direction.Vertical)
        .constraints([
            Constraint.length(3),
            Constraint.fill(1),
            Constraint.length(1),
        ])
        .split(area)
    )
    header, body, footer = outer

    # Body: sidebar + main (horizontal split)
    inner = (
        Layout()
        .direction(Direction.Horizontal)
        .constraints([
            Constraint.percentage(30),
            Constraint.fill(1),
        ])
        .split(body)
    )
    sidebar, main = inner

    # Main area: top panel + bottom panel (vertical split)
    panels = (
        Layout()
        .direction(Direction.Vertical)
        .constraints([Constraint.fill(1), Constraint.fill(1)])
        .split(main)
    )
    top_panel, bottom_panel = panels
```

---

## Layout with Margin and Spacing

```python
layout = (
    Layout()
    .direction(Direction.Horizontal)
    .constraints([Constraint.fill(1)] * 3)
    .margin(1)     # 1-cell padding around the whole layout
    .spacing(1)    # 1-cell gap between the 3 panels
    .split(area)
)
left, center, right = layout
```

---

## Common Layout Recipes

### Status Bar at Bottom

```python
chunks = (Layout()
    .direction(Direction.Vertical)
    .constraints([Constraint.fill(1), Constraint.length(1)])
    .split(area))
main, status = chunks
```

### Three-Pane

```python
chunks = (Layout()
    .direction(Direction.Horizontal)
    .constraints([
        Constraint.percentage(25),
        Constraint.fill(1),
        Constraint.percentage(25),
    ])
    .split(area))
left, center, right = chunks
```

### Centered Dialog

```python
# Create a centered popup of fixed size
def centered_rect(area, width, height):
    x = (area.width  - width)  // 2
    y = (area.height - height) // 2
    return Rect(area.x + x, area.y + y, width, height)

popup = centered_rect(frame.area, 40, 10)
frame.render_widget(Clear(), popup)           # clear background
frame.render_widget(Block().bordered(), popup) # draw popup
```
