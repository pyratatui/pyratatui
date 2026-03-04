# Text Primitives Reference

The text system in pyratatui is a three-level hierarchy:

```
Span   →  a single styled string fragment
Line   →  an ordered list of Spans (one line of text)
Text   →  an ordered list of Lines (a complete block of text)
```

All three types are documented in full in the [Style & Text Reference](style.md).

---

## Quick Reference

### Span

```python
from pyratatui import Span, Style, Color

Span("text")                         # unstyled
Span("text", Style().fg(Color.red())) # styled
span.styled(style)                   # return new span with style
span.width()                         # character count
span.content                         # the text string
span.style                           # Style | None
```

### Line

```python
from pyratatui import Line

Line([span1, span2, span3])          # from spans
Line.from_string("plain text")       # single unstyled span
line.left_aligned()                  # alignment (returns new Line)
line.centered()
line.right_aligned()
line.styled(style)                   # apply base style
line.push_span(span)                 # append span (mutating)
line.spans                           # list[Span]
line.width()                         # total character width
```

### Text

```python
from pyratatui import Text

Text([line1, line2])                 # from lines
Text.from_string("line1\nline2")     # split on newlines
text.push_line(line)                 # append (mutating)
text.push_str("plain text")         # append as plain Line (mutating)
text.centered()                     # return new Text with alignment
text.right_aligned()
text.styled(style)                  # return new Text with base style
text.lines                          # list[Line]
text.height                         # number of lines
text.width()                        # width of widest line
```

---

## Pass Text to Widgets

```python
from pyratatui import Paragraph

# From a Text object
frame.render_widget(Paragraph(text), area)

# Convenience shortcut for plain strings
frame.render_widget(Paragraph.from_string("Hello!"), area)
```

See [Style & Text Reference](style.md) for complete documentation with examples.
