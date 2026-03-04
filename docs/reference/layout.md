# Layout Reference

## Rect

A rectangular area of the terminal.

```python
from pyratatui import Rect

r = Rect(x=0, y=0, width=80, height=24)
r.x, r.y, r.width, r.height
r.left, r.right, r.top, r.bottom
r.area()      # int: width * height
r.is_empty()  # bool
r.inner(horizontal=1, vertical=1)   # Rect shrunk by margin
r.intersection(other)               # Optional[Rect]
r.union(other)                      # Rect
r.contains(other)                   # bool
```

## Constraint

Sizing rules for layout children.

```python
from pyratatui import Constraint

Constraint.length(20)        # Fixed size in cells
Constraint.percentage(50)    # Percentage of parent (0-100)
Constraint.fill(1)           # Fill remaining space (weight-based)
Constraint.min(10)           # At least N cells
Constraint.max(40)           # At most N cells
Constraint.ratio(1, 3)       # Exact ratio
```

## Direction

```python
from pyratatui import Direction

Direction.Vertical    # Split top → bottom
Direction.Horizontal  # Split left → right
```

## Alignment

```python
from pyratatui import Alignment

Alignment.Left
Alignment.Center
Alignment.Right
```

## Layout

Splits a `Rect` into child `Rect`s according to constraints.

```python
from pyratatui import Layout, Constraint, Direction, Rect

area = Rect(0, 0, 80, 24)

# Vertical split: header | body | footer
chunks = (Layout()
    .direction(Direction.Vertical)
    .constraints([
        Constraint.length(3),   # header: 3 rows
        Constraint.fill(1),     # body:   fills remaining
        Constraint.length(1),   # footer: 1 row
    ])
    .margin(1)      # optional uniform margin
    .spacing(0)     # optional gap between panels
    .split(area))

header, body, footer = chunks
```

### Nested layouts

```python
# Horizontal split inside a panel
left, right = (Layout()
    .direction(Direction.Horizontal)
    .constraints([Constraint.percentage(40), Constraint.fill(1)])
    .split(body))
```
