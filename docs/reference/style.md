# Style & Text Reference

---

## Color

```python
from pyratatui import Color
```

Represents a terminal color. Created via static factory methods — never instantiated directly.

### Named Colors (16-color)

```python
Color.reset()         # Terminal default / transparent
Color.black()
Color.red()
Color.green()
Color.yellow()
Color.blue()
Color.magenta()
Color.cyan()
Color.gray()
Color.dark_gray()
Color.light_red()
Color.light_green()
Color.light_yellow()
Color.light_blue()
Color.light_magenta()
Color.light_cyan()
Color.white()
```

These map to the terminal's standard 16-color palette and render correctly in all modern terminal emulators.

### Indexed Color (256-color)

```python
Color.indexed(n: int)  # n = 0–255
```

Selects a color from the terminal's 256-color xterm palette. Requires a terminal with 256-color support (virtually all modern terminals).

```python
orange  = Color.indexed(208)
purple  = Color.indexed(135)
bright  = Color.indexed(196)   # bright red
```

The standard xterm 256-color map:

- 0–7: Standard colors (same as 16-color)
- 8–15: Bright variants
- 16–231: 6×6×6 RGB cube
- 232–255: Grayscale ramp (dark to light)

### True-Color RGB

```python
Color.rgb(r: int, g: int, b: int)  # r, g, b = 0–255
```

Full 24-bit color. Requires a truecolor-capable terminal (`COLORTERM=truecolor`).

```python
orange = Color.rgb(255, 128,   0)
teal   = Color.rgb(  0, 180, 180)
custom = Color.rgb( 30,  30,  46)   # Catppuccin Mocha base
```

### Comparison

```python
Color.red() == Color.red()    # True
Color.red() == Color.green()  # False
```

---

## Modifier

```python
from pyratatui import Modifier
```

A bitfield of text style modifiers. Combine with `|` (bitwise OR).

### Static Factories

| Method | Visual effect |
|---|---|
| `Modifier.bold()` | **Bold** text |
| `Modifier.dim()` | Dimmed/faint text |
| `Modifier.italic()` | *Italic* text |
| `Modifier.underlined()` | Underlined text |
| `Modifier.slow_blink()` | Slow blink (0.5 Hz) |
| `Modifier.rapid_blink()` | Fast blink (3+ Hz) |
| `Modifier.reversed()` | Swap foreground and background |
| `Modifier.hidden()` | Invisible (same color as background) |
| `Modifier.crossed_out()` | ~~Strikethrough~~ |

### Combining Modifiers

```python
m = Modifier.bold() | Modifier.italic()          # bold + italic
m = Modifier.bold() | Modifier.underlined()       # bold + underline
m = Modifier.bold() | Modifier.italic() | Modifier.underlined()
```

Use `&` (bitwise AND) to intersect:

```python
shared = (Modifier.bold() | Modifier.italic()) & Modifier.bold()
# → Modifier.bold()
```

---

## Style

```python
from pyratatui import Style
```

A complete style descriptor combining foreground color, background color, and text modifiers. All builder methods return a **new** `Style` (immutable, chainable).

### Constructor

```python
Style()  # Empty style (inherits everything from parent)
```

### Builder Methods

#### `.fg(color: Color) → Style`

Set the foreground (text) color.

```python
style = Style().fg(Color.cyan())
```

#### `.bg(color: Color) → Style`

Set the background (cell fill) color.

```python
style = Style().bg(Color.black())
```

#### `.add_modifier(modifier: Modifier) → Style`

Add a text modifier.

```python
style = Style().add_modifier(Modifier.bold())
```

#### `.remove_modifier(modifier: Modifier) → Style`

Remove a specific modifier.

```python
style = original.remove_modifier(Modifier.italic())
```

#### `.patch(other: Style) → Style`

Merge `other` into `self`, overriding only the fields set in `other`. Useful for theming — apply a base style and patch with overrides.

```python
base   = Style().fg(Color.white()).bg(Color.black())
accent = Style().fg(Color.cyan()).bold()
merged = base.patch(accent)
# merged.fg = cyan, bg = black, bold = True
```

### Convenience Shorthand Methods

These are equivalent to calling `.add_modifier(Modifier.xxx())`:

```python
Style().bold()
Style().italic()
Style().underlined()
Style().dim()
Style().reversed()
Style().hidden()
Style().crossed_out()
Style().slow_blink()
Style().rapid_blink()
```

### Properties

| Property | Type | Description |
|---|---|---|
| `foreground` | `Color \| None` | Current foreground color |
| `background` | `Color \| None` | Current background color |

### Examples

```python
from pyratatui import Style, Color, Modifier

# Bold cyan on dark background
Style().fg(Color.cyan()).bg(Color.black()).bold()

# Italic gray for secondary text
Style().fg(Color.gray()).italic()

# Highlighted selection row
Style().fg(Color.black()).bg(Color.cyan()).bold()

# Error state
Style().fg(Color.red()).bold().underlined()

# Combine via patch (theming)
header_style = Style().fg(Color.white()).bold()
selected     = header_style.patch(Style().bg(Color.blue()))
```

---

## Span

```python
from pyratatui import Span
```

A single styled string fragment. The atomic unit of text.

### Constructor

```python
Span(content: str, style: Style | None = None)
```

| Parameter | Type | Default | Description |
|---|---|---|---|
| `content` | `str` | required | The text content |
| `style` | `Style \| None` | `None` | Optional style |

```python
s = Span("Hello")                              # unstyled
s = Span("Error", Style().fg(Color.red()))     # red text
s = Span("OK",    Style().fg(Color.green()))
```

### Properties

| Property | Type | Description |
|---|---|---|
| `content` | `str` | The text string |
| `style` | `Style \| None` | The applied style |

### Methods

#### `.styled(style: Style) → Span`

Return a new `Span` with the given style applied (replaces any existing style).

#### `.width() → int`

Character count (not byte count — handles multi-byte Unicode correctly).

---

## Line

```python
from pyratatui import Line
```

An ordered list of `Span` objects forming a single line of text.

### Constructor

```python
Line(spans: list[Span] | None = None, style: Style | None = None)
```

```python
line = Line([
    Span("Status: "),
    Span("OK", Style().fg(Color.green())),
])
```

### Factory

```python
Line.from_string("Plain text line")
```

Creates a `Line` with a single unstyled span.

### Properties

| Property | Type | Description |
|---|---|---|
| `spans` | `list[Span]` | The spans in this line |

### Builder Methods

All return a new `Line` instance.

| Method | Description |
|---|---|
| `.left_aligned()` | Left-align the line |
| `.centered()` | Center the line within its area |
| `.right_aligned()` | Right-align the line |
| `.styled(style: Style)` | Apply a base style to the whole line |
| `.push_span(span: Span)` | Append a span in-place (mutating) |

### `width() → int`

Total character width of all spans.

---

## Text

```python
from pyratatui import Text
```

A list of `Line` objects — the full content for a `Paragraph` or other multi-line widget.

### Constructor

```python
Text(lines: list[Line] | None = None, style: Style | None = None)
```

```python
text = Text([
    Line.from_string("Line one"),
    Line([
        Span("Bold: ", Style().bold()),
        Span("value", Style().fg(Color.cyan())),
    ]),
])
```

### Factory

```python
Text.from_string("Line 1\nLine 2\nLine 3")
```

Splits on newlines and creates a `Line.from_string` for each.

### Properties

| Property | Type | Description |
|---|---|---|
| `lines` | `list[Line]` | All lines |
| `height` | `int` | Number of lines |

### Methods

| Method | Description |
|---|---|
| `.push_line(line: Line)` | Append a `Line` in-place |
| `.push_str(s: str)` | Append a plain string as a new line |
| `.width() → int` | Width of the widest line |
| `.centered()` | Return a new `Text` with center alignment |
| `.right_aligned()` | Return a new `Text` with right alignment |
| `.styled(style: Style)` | Return a new `Text` with a base style |

---

## Style & Text Cookbook

### Colorize a word in a sentence

```python
line = Line([
    Span("Server is "),
    Span("ONLINE", Style().fg(Color.green()).bold()),
    Span(" — uptime 24h"),
])
```

### Mixed Alignment in a Multi-Line Block

```python
text = Text([
    Line.from_string("Centered title").centered(),
    Line.from_string(""),
    Line.from_string("Left aligned body text"),
    Line.from_string("Right aligned note").right_aligned(),
])
```

### Styled Table of Key/Value Pairs

```python
def kv_line(key: str, value: str, value_color=None):
    return Line([
        Span(f"{key:<12}", Style().fg(Color.gray())),
        Span(value, Style().fg(value_color or Color.white())),
    ])

text = Text([
    kv_line("CPU",      "72%",       Color.yellow()),
    kv_line("Memory",   "4.2 GB",    Color.cyan()),
    kv_line("Requests", "1,024,000", Color.green()),
    kv_line("Errors",   "0",         Color.green()),
])
```

### Building Text Progressively

```python
text = Text()
for message in log_entries:
    color = Color.red() if "ERROR" in message else Color.gray()
    text.push_line(Line([Span(message, Style().fg(color))]))
```
