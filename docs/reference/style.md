# Style Reference

## Color

```python
from pyratatui import Color

# Named colors
Color.black(), Color.red(), Color.green(), Color.yellow()
Color.blue(), Color.magenta(), Color.cyan(), Color.white()
Color.gray(), Color.dark_gray(), Color.reset()
Color.light_red(), Color.light_green(), Color.light_yellow()
Color.light_blue(), Color.light_magenta(), Color.light_cyan()

# 256-color palette (0-255)
Color.indexed(196)

# True color (24-bit RGB)
Color.rgb(255, 128, 0)
```

## Modifier

Text attribute flags.

```python
from pyratatui import Modifier

Modifier.bold()
Modifier.italic()
Modifier.underlined()
Modifier.dim()
Modifier.reversed()
Modifier.hidden()
Modifier.crossed_out()
Modifier.slow_blink()
Modifier.rapid_blink()

# Combine with |
m = Modifier.bold() | Modifier.italic()
```

## Style

A complete style descriptor: foreground + background + modifiers.

```python
from pyratatui import Style, Color, Modifier

s = (Style()
    .fg(Color.cyan())
    .bg(Color.black())
    .bold()
    .italic()
    .underlined())

# Patch (override only set fields)
merged = base_style.patch(overlay_style)

# Inspect
s.foreground   # Optional[Color]
s.background   # Optional[Color]
```

Shortcut modifiers directly on `Style`:

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

---

# Text Reference

## Span

A styled string fragment.

```python
from pyratatui import Span, Style, Color

s = Span("hello")
s = Span("world", Style().fg(Color.green()))
s.content   # str
s.style     # Optional[Style]
s.width()   # int: character count
s.styled(style)   # → new Span with style applied
```

## Line

A horizontal sequence of spans.

```python
from pyratatui import Line, Span

l = Line([Span("Hello "), Span("World")])
l = Line.from_string("Plain text")

l.left_aligned()   # → Line
l.centered()       # → Line
l.right_aligned()  # → Line
l.styled(style)    # → Line
l.push_span(span)  # mutates
l.spans            # List[Span]
l.width()          # int
```

## Text

A block of text (multiple lines).

```python
from pyratatui import Text, Line

t = Text([Line.from_string("Line 1"), Line.from_string("Line 2")])
t = Text.from_string("line1\nline2\nline3")   # split on newlines

t.push_line(line)   # append a Line
t.push_str("text")  # append a plain string line
t.height            # int: number of lines
t.width()           # int: max line width
t.centered()        # → Text
t.right_aligned()   # → Text
t.styled(style)     # → Text
t.lines             # List[Line]
```
