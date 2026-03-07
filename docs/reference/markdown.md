# Markdown Renderer

`markdown_to_text()` converts Markdown source into a styled `Text` object
using [tui-markdown](https://crates.io/crates/tui-markdown).

## Quick Start

```python
from pyratatui import markdown_to_text, Paragraph, Block

md = """
# Hello, pyratatui!

This is **bold**, *italic*, and `code`.

- Item one
- Item two
"""

text = markdown_to_text(md)
para = Paragraph(text).block(Block().bordered().title(" Markdown "))
frame.render_widget(para, area)
```

## API

### `markdown_to_text(src: str) -> Text`

Parses the Markdown `src` string and returns a `Text` object with appropriate
styles applied (bold, italic, code blocks, headings, lists, etc.).

The returned `Text` can be used anywhere a `Text` or `Paragraph` argument is expected.

## Notes

Not all Markdown features are supported. Supported elements include:
headings, bold, italic, code spans, fenced code blocks, bullet lists, and blockquotes.

See `examples/28_markdown_renderer.py`.
