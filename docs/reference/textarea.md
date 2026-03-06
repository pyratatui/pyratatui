# TextArea

The `TextArea` widget provides a fully-featured multi-line text editor for your
terminal UI, powered by the [`tui-textarea`](https://crates.io/crates/tui-textarea) crate.

---

## Overview

| Class | Purpose |
|---|---|
| `TextArea` | The multi-line text editor widget |
| `CursorMove` | Cursor movement commands |
| `Scrolling` | Scroll amounts for `TextArea.scroll()` |

---

## `TextArea`

### Creating

```python
from pyratatui import TextArea

ta = TextArea()                                   # empty
ta = TextArea.from_lines(["Line 1", "Line 2"])    # pre-filled
```

### Rendering

```python
frame.render_textarea(ta, frame.area)
```

### Key Input

```python
# Inside your event loop:
ev = term.poll_event(timeout_ms=50)
if ev:
    consumed = ta.input_key(ev.code, ev.ctrl, ev.alt, ev.shift)
```

`input_key` returns `True` if the event modified the text.

Default Emacs key bindings are applied automatically. To use custom mappings
instead, call `input_without_shortcuts()` and dispatch edit methods manually.

### Built-in Key Bindings

| Key | Action |
|-----|--------|
| `Ctrl+F` / `Right` | Move forward |
| `Ctrl+B` / `Left` | Move back |
| `Ctrl+P` / `Up` | Move up |
| `Ctrl+N` / `Down` | Move down |
| `Ctrl+A` / `Home` | Beginning of line |
| `Ctrl+E` / `End` | End of line |
| `Ctrl+H` / `Backspace` | Delete previous char |
| `Ctrl+D` / `Delete` | Delete next char |
| `Ctrl+K` | Kill to end of line |
| `Ctrl+W` | Delete word before cursor |
| `Ctrl+J` / `Enter` | Insert newline |
| `Ctrl+Z` | Undo |
| `Ctrl+Y` | Paste (yank) |
| `Tab` | Insert tab/spaces |

---

## `CursorMove`

Pass to `ta.move_cursor()` for programmatic cursor movement:

```python
from pyratatui import CursorMove

ta.move_cursor(CursorMove.WordForward)
ta.move_cursor(CursorMove.Head)
ta.move_cursor(CursorMove.Bottom)
ta.move_cursor_to(row=5, col=0)    # absolute position
```

| Value | Effect |
|---|---|
| `Forward` / `Back` | One character left/right |
| `Up` / `Down` | One line up/down |
| `WordForward` / `WordBack` | One word forward/backward |
| `WordEnd` | End of current/next word |
| `Head` / `End` | Beginning/end of line |
| `Top` / `Bottom` | First/last line |
| `ViewportTop/Middle/Bottom` | Visible area |
| `ParagraphBack/Forward` | Block paragraph navigation |

---

## Styling

```python
from pyratatui import Block, Style, Color, Modifier

# Add a border with title
ta.set_block(Block().bordered().title(" My Editor "))

# Cursor style (REVERSED modifier shows a block cursor by default)
ta.set_cursor_style(Style().fg(Color.black()).bg(Color.white()))

# Cursor line (the whole row)
ta.set_cursor_line_style(Style().bg(Color.dark_gray()))

# Line numbers in the gutter
ta.set_line_number_style(Style().fg(Color.dark_gray()))
ta.remove_line_number()  # hide line numbers

# Placeholder text (shown when empty)
ta.set_placeholder_text("Start typing…")
ta.set_placeholder_style(Style().fg(Color.dark_gray()))
```

---

## Configuration

```python
ta.set_tab_length(2)            # tab width in spaces (default 4)
ta.set_hard_tab_indent(True)    # insert \t instead of spaces
ta.set_max_histories(100)       # undo history depth (default 50)
```

---

## Undo / Redo

```python
ta.undo()   # Ctrl+Z equivalent
ta.redo()   # Ctrl+Y / Ctrl+R equivalent
```

---

## Clipboard (Yank / Kill)

```python
ta.delete_line_by_end()   # Ctrl+K: kill to end of line → stored in yank buffer
ta.paste()                # Ctrl+Y: paste yank buffer
ta.copy()                 # copy selection (no delete)
ta.cut()                  # cut selection
```

---

## Text Selection

```python
ta.start_selection()    # begin selection at current cursor
ta.move_cursor(CursorMove.WordForward)
ta.cut()                # cut selected text
# or
ta.copy()               # copy selected text
ta.cancel_selection()   # clear selection
r = ta.selection_range()  # ((row_start, col_start), (row_end, col_end)) or None
```

---

## Accessing Content

```python
lines = ta.lines()              # list[str]
text = "\n".join(ta.lines())    # full text
row, col = ta.cursor()          # current cursor position
n = ta.len()                    # number of lines
empty = ta.is_empty()           # bool
```

---

## Vim-style Modal Example

See `examples/15_textarea_advanced.py` for a full modal (NORMAL/INSERT) editor.

```python
if mode == "NORMAL":
    if ev.code == "i":
        mode = "INSERT"
    elif ev.code == "h":
        ta.move_cursor(CursorMove.Back)
    elif ev.code == "u":
        ta.undo()
    # ...
elif mode == "INSERT":
    if ev.code == "Esc":
        mode = "NORMAL"
    else:
        ta.input_key(ev.code, ev.ctrl, ev.alt, ev.shift)
```

---

## See Also

- [`tui-textarea` crate](https://crates.io/crates/tui-textarea)
- [Example 14 — Basic TextArea](../../examples/14_textarea_basic.py)
- [Example 15 — Advanced (Vim modal)](../../examples/15_textarea_advanced.py)
