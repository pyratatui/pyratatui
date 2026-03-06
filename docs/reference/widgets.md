# Widgets Reference

All widgets follow an immutable builder pattern: every configuration method returns a **new** widget instance. You can safely chain calls and reuse partial configurations.

---

## Block

```python
from pyratatui import Block, BorderType
```

A bordered container. `Block` is commonly used as a wrapper for other widgets to add titles and visual boundaries.

### Constructor

```python
Block()
```

Creates an empty block with no borders or title.

### Builder Methods

#### `.title(title: str) → Block`

Set the top title. By default left-aligned in the top border.

#### `.title_bottom(title: str) → Block`

Set a title at the bottom border.

#### `.bordered() → Block`

Enable all four borders (shorthand for `.borders(top=True, right=True, bottom=True, left=True)`).

#### `.borders(top=True, right=True, bottom=True, left=True) → Block`

Enable specific sides.

```python
# Only top and bottom borders
Block().borders(top=True, right=False, bottom=True, left=False)
```

#### `.border_type(bt: BorderType) → Block`

Set the border character style.

| `BorderType` | Appearance |
|---|---|
| `BorderType.Plain` | `─ │ ┌ ┐ └ ┘` (default) |
| `BorderType.Rounded` | `─ │ ╭ ╮ ╰ ╯` |
| `BorderType.Double` | `═ ║ ╔ ╗ ╚ ╝` |
| `BorderType.Thick` | `━ ┃ ┏ ┓ ┗ ┛` |
| `BorderType.QuadrantInside` | Block element borders |
| `BorderType.QuadrantOutside` | Block element borders (outer) |

#### `.style(style: Style) → Block`

Apply style to the entire block (background and text inside the borders).

#### `.border_style(style: Style) → Block`

Apply style only to the border characters.

#### `.title_style(style: Style) → Block`

Apply style only to the title text.

#### `.title_alignment(alignment: str) → Block`

Set title alignment: `"left"` (default), `"center"`, `"right"`.

#### `.padding(left=0, right=0, top=0, bottom=0) → Block`

Add inner padding between the border and the content area.

#### `.inner(area: Rect) → Rect`

Compute the inner area of a block for a given outer `area`. This subtracts
borders and padding from the provided `Rect`, returning the space available
for content rendered inside the block.

```python
block = Block().bordered().title("Panel")
inner = block.inner(frame.area)   # area minus 1-cell border on each side
frame.render_widget(block, frame.area)
frame.render_widget(content, inner)
```

> **Added in 0.2.0.** Use this instead of manually computing `Rect(x+1, y+1, w-2, h-2)`.

### Example

```python
from pyratatui import Block, BorderType, Style, Color

block = (Block()
    .title("Service Monitor")
    .title_alignment("center")
    .title_style(Style().fg(Color.cyan()).bold())
    .bordered()
    .border_type(BorderType.Rounded)
    .border_style(Style().fg(Color.dark_gray()))
    .style(Style().bg(Color.black()))
    .padding(left=1, right=1))
```

---

## Paragraph

```python
from pyratatui import Paragraph, Text
```

Renders multi-line text with optional wrapping, scrolling, and block container.

### Constructors

```python
Paragraph(text: Text)            # from a Text object
Paragraph.from_string("text")    # convenience: plain string
```

### Builder Methods

#### `.block(block: Block) → Paragraph`

Wrap in a `Block` container.

#### `.style(style: Style) → Paragraph`

Apply a base style to all text.

#### `.wrap(wrap: bool, trim: bool = True) → Paragraph`

Enable word-wrapping. `trim=True` removes leading whitespace from wrapped lines.

#### `.scroll(y: int, x: int) → Paragraph`

Scroll offset in rows (`y`) and columns (`x`). Used for scrollable content.

#### `.alignment(alignment: str) → Paragraph`

Set text alignment: `"left"`, `"center"`, `"right"`.

#### `.left_aligned()` / `.centered()` / `.right_aligned()`

Shorthand alignment setters.

### Examples

```python
from pyratatui import Paragraph, Text, Line, Span, Style, Color, Block

# Simple
frame.render_widget(
    Paragraph.from_string("Hello, World!")
        .block(Block().bordered().title("Info")),
    area,
)

# Wrapped long content
frame.render_widget(
    Paragraph.from_string(long_text).wrap(True),
    area,
)

# Rich styled text
frame.render_widget(
    Paragraph(Text([
        Line([Span("Status: "), Span("OK", Style().fg(Color.green()))]),
        Line.from_string("All systems nominal"),
    ])).block(Block().bordered()),
    area,
)
```

---

## List

```python
from pyratatui import List, ListItem, ListState, ListDirection
```

A scrollable, selectable list of items. Requires a `ListState` for selection tracking.

### `ListItem`

```python
ListItem(text: str, style: Style | None = None)
ListItem.from_text(text: Text)   # from a Text object
item.style(style: Style)         # return new item with style
```

### `ListState`

Tracks the currently selected index and scroll offset.

| Method | Description |
|---|---|
| `ListState()` | Create new state (nothing selected) |
| `.select(index)` | Select by index (`None` = deselect) |
| `.select_next()` | Move selection down |
| `.select_previous()` | Move selection up |
| `.select_first()` | Jump to first item |
| `.select_last()` | Jump to last item |
| `.selected` | Currently selected index or `None` |
| `.offset` | Scroll offset (read-only) |

### `List` Builder Methods

| Method | Description |
|---|---|
| `List(items)` | Constructor — list of `ListItem` |
| `.block(block)` | Wrap in a `Block` |
| `.style(style)` | Base style for all items |
| `.highlight_style(style)` | Style for the selected item |
| `.highlight_symbol(sym)` | Prefix string for selected item |
| `.direction(dir)` | `ListDirection.TopToBottom` or `ListDirection.BottomToTop` |
| `.repeat_highlight_symbol(bool)` | Repeat symbol on all items |

### Rendering

```python
frame.render_stateful_list(list_widget, area, list_state)
```

### Example

```python
from pyratatui import List, ListItem, ListState, Style, Color, Block, BorderType

items = [
    ListItem("● nginx",      Style().fg(Color.green())),
    ListItem("● postgres",   Style().fg(Color.green())),
    ListItem("◐ redis",      Style().fg(Color.yellow())),
    ListItem("○ kafka",      Style().fg(Color.red())),
]

state = ListState()
state.select(0)

# In draw callback:
frame.render_stateful_list(
    List(items)
        .block(Block().bordered().title("Services").border_type(BorderType.Rounded))
        .highlight_style(Style().fg(Color.white()).bg(Color.blue()).bold())
        .highlight_symbol("▶ "),
    area,
    state,
)
```

---

## Table

```python
from pyratatui import Table, Row, Cell, TableState
```

A data grid with optional header, column widths, and row selection.

### `Cell`

```python
Cell(text: str, style: Style | None = None)
cell.style(style: Style)   # return new cell with style
```

### `Row`

```python
Row(cells: list[Cell])
Row.from_strings(texts: list[str])   # convenience factory
row.style(style: Style)              # style applied to all cells
row.height(n: int)                   # override row height (default: 1)
```

### `TableState`

Same interface as `ListState`:

| Method | Description |
|---|---|
| `.select(index)` | Select row |
| `.select_next()` | Move down |
| `.select_previous()` | Move up |
| `.select_first()` / `.select_last()` | Jump to extremes |
| `.selected` | Current index or `None` |
| `.offset` | Scroll offset |

### `Table` Constructor

```python
Table(
    rows: list[Row],
    widths: list[Constraint],
    header: Row | None = None,
)
```

| Parameter | Type | Description |
|---|---|---|
| `rows` | `list[Row]` | Data rows |
| `widths` | `list[Constraint]` | Column sizing constraints |
| `header` | `Row \| None` | Optional header row |

### `Table` Builder Methods

| Method | Description |
|---|---|
| `.block(block)` | Container block |
| `.style(style)` | Base style |
| `.header_style(style)` | Override header style |
| `.highlight_style(style)` | Selected row style |
| `.highlight_symbol(sym)` | Prefix for selected row |
| `.column_spacing(n)` | Extra gap between columns |

### Rendering

```python
frame.render_stateful_table(table, area, state)
```

### Example

```python
from pyratatui import Table, Row, Cell, TableState, Constraint, Style, Color, Block

header = Row([
    Cell("Service").style(Style().bold()),
    Cell("CPU %").style(Style().bold()),
    Cell("Status").style(Style().bold()),
])

rows = [
    Row([Cell("nginx"),    Cell("32%").style(Style().fg(Color.green())), Cell("Running")]),
    Row([Cell("postgres"), Cell("71%").style(Style().fg(Color.yellow())), Cell("Running")]),
    Row([Cell("redis"),    Cell("5%").style(Style().fg(Color.green())),   Cell("Degraded")]),
]

state = TableState()
state.select(0)

frame.render_stateful_table(
    Table(rows,
          widths=[Constraint.fill(1), Constraint.length(8), Constraint.length(10)],
          header=header)
        .block(Block().bordered().title("Services"))
        .highlight_style(Style().fg(Color.cyan()).bold())
        .column_spacing(1),
    area,
    state,
)
```

---

## Gauge

```python
from pyratatui import Gauge
```

A filled horizontal progress bar.

### Builder Methods

| Method | Type | Description |
|---|---|---|
| `.percent(pct)` | `int` 0–100 | Set progress as percentage |
| `.ratio(r)` | `float` 0.0–1.0 | Set progress as ratio |
| `.label(text)` | `str` | Override center label (default: percentage) |
| `.style(style)` | `Style` | Style of the filled portion |
| `.gauge_style(style)` | `Style` | Style of the empty portion |
| `.use_unicode(v)` | `bool` | Enable smooth Unicode block chars |
| `.block(block)` | `Block` | Container block |

### Example

```python
from pyratatui import Gauge, Style, Color, Block

frame.render_widget(
    Gauge()
        .percent(67)
        .label("CPU: 67%")
        .style(Style().fg(Color.yellow()))
        .gauge_style(Style().fg(Color.dark_gray()))
        .use_unicode(True)
        .block(Block().bordered().title("CPU Usage")),
    area,
)
```

---

## LineGauge

```python
from pyratatui import LineGauge
```

A single-line progress indicator using Unicode line characters.

### Builder Methods

| Method | Type | Description |
|---|---|---|
| `.ratio(r)` | `float` 0.0–1.0 | Progress ratio |
| `.percent(pct)` | `int` 0–100 | Shorthand for `.ratio(pct/100)` |
| `.label(text)` | `str` | Label to the right |
| `.line_set(name)` | `str` | `"normal"`, `"thick"`, `"double"` |
| `.style(style)` | `Style` | Filled line style |
| `.gauge_style(style)` | `Style` | Empty line style |
| `.block(block)` | `Block` | Container |

---

## BarChart

```python
from pyratatui import BarChart, BarGroup, Bar
```

A vertical or horizontal bar chart.

### `Bar`

```python
Bar(value: int, label: str | None = None)
bar.style(style: Style)           # bar color
bar.value_style(style: Style)     # value number style
bar.text_value(tv: str)           # override value display string
```

### `BarGroup`

```python
BarGroup(bars: list[Bar], label: str | None = None)
```

### `BarChart` Builder Methods

| Method | Default | Description |
|---|---|---|
| `.data(group: BarGroup)` | — | Add a bar group (call multiple times) |
| `.bar_width(w)` | `3` | Width of each bar |
| `.bar_gap(g)` | `1` | Gap between bars |
| `.group_gap(g)` | `3` | Gap between groups |
| `.max(m)` | auto | Scale maximum value |
| `.style(s)` | — | Overall chart style |
| `.bar_style(s)` | — | Default bar fill style |
| `.value_style(s)` | — | Value label style |
| `.label_style(s)` | — | Bar label style |
| `.block(b)` | — | Container block |

### Example

```python
from pyratatui import BarChart, BarGroup, Bar, Style, Color, Block

bars = [
    Bar(42, "Jan").style(Style().fg(Color.cyan())),
    Bar(68, "Feb").style(Style().fg(Color.yellow())),
    Bar(35, "Mar").style(Style().fg(Color.green())),
    Bar(91, "Apr").style(Style().fg(Color.red())),
]

frame.render_widget(
    BarChart()
        .data(BarGroup(bars, label="Monthly CPU %"))
        .bar_width(5)
        .bar_gap(1)
        .max(100)
        .value_style(Style().fg(Color.white()).bold())
        .label_style(Style().fg(Color.dark_gray()))
        .block(Block().bordered().title("CPU by Month")),
    area,
)
```

---

## Sparkline

```python
from pyratatui import Sparkline
```

A compact single-row chart using Unicode block characters (`▁▂▃▄▅▆▇█`).

### Builder Methods

| Method | Description |
|---|---|
| `.data(values: list[int])` | Set the data series |
| `.max(m: int)` | Scale maximum |
| `.style(style: Style)` | Bar color |
| `.block(block: Block)` | Container |

### Example

```python
from pyratatui import Sparkline, Style, Color, Block

frame.render_widget(
    Sparkline()
        .data([10, 25, 40, 15, 60, 80, 45, 20])
        .max(100)
        .style(Style().fg(Color.green()))
        .block(Block().bordered().title("CPU History")),
    area,
)
```

---

## Tabs

```python
from pyratatui import Tabs
```

A horizontal tab bar for switching between views.

### Constructor + Builder

```python
Tabs(titles: list[str])
```

| Method | Description |
|---|---|
| `.select(index: int)` | Highlight the active tab |
| `.block(block: Block)` | Container block |
| `.style(style: Style)` | Default tab style |
| `.highlight_style(style: Style)` | Active tab style |
| `.divider(text: str)` | Separator string (default: `"│"`) |
| `.padding(left: str, right: str)` | Padding around each tab label |

### Example

```python
from pyratatui import Tabs, Style, Color, Block

frame.render_widget(
    Tabs(["Overview", "Services", "Logs"])
        .select(current_tab)
        .block(Block().bordered().title(" My App "))
        .highlight_style(Style().fg(Color.cyan()).bold())
        .style(Style().fg(Color.dark_gray()))
        .divider(" | "),
    header_area,
)
```

---

## Scrollbar

```python
from pyratatui import Scrollbar, ScrollbarState, ScrollbarOrientation
```

A scroll position indicator.

### `ScrollbarOrientation`

```python
ScrollbarOrientation.VerticalRight    # default
ScrollbarOrientation.VerticalLeft
ScrollbarOrientation.HorizontalBottom
ScrollbarOrientation.HorizontalTop
```

### `ScrollbarState`

| Method/Property | Description |
|---|---|
| `ScrollbarState()` | New state |
| `.content_length(n)` | Total scrollable items |
| `.position(p)` | Set scroll position (builder) |
| `.scroll_next()` | Scroll down/right |
| `.scroll_prev()` | Scroll up/left |
| `.first()` / `.last()` | Jump to extremes |
| `.get_position()` | Current scroll position |

### `Scrollbar` Builder Methods

| Method | Description |
|---|---|
| `Scrollbar(orientation=None)` | Constructor |
| `.orientation(o)` | Set orientation |
| `.thumb_style(style)` | Scrollbar thumb (filled portion) |
| `.track_style(style)` | Scrollbar track (empty portion) |
| `.begin_style(style)` | Arrow at start end |
| `.end_style(style)` | Arrow at end |

### Example

```python
from pyratatui import Scrollbar, ScrollbarState, ScrollbarOrientation, Style, Color

scroll_state = ScrollbarState().content_length(100).position(20)

frame.render_stateful_scrollbar(
    Scrollbar()
        .thumb_style(Style().fg(Color.cyan()))
        .track_style(Style().fg(Color.dark_gray())),
    area,
    scroll_state,
)
```

---

## Clear

```python
from pyratatui import Clear
```

A widget that paints its area with the current background color — useful for popup overlays.

```python
# Create and clear a popup area
popup = Rect(x, y, width, height)
frame.render_widget(Clear(), popup)
frame.render_widget(Block().bordered().title("Popup"), popup)
```

`Clear` has no builder methods. Construct with `Clear()`.
