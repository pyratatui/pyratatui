# Changelog

All notable changes to this project will be documented in this file.

The format loosely follows [Keep a Changelog](https://keepachangelog.com) conventions
and [Semantic Versioning](https://semver.org).

---

## [0.2.0] — 2025-03-06

### Summary

`0.2.0` upgrades the native backend to **ratatui 0.30** (the largest ratatui
release ever, featuring a modular workspace architecture) and repairs all
compile-time errors and deprecation warnings introduced by that upgrade.
This release also adds `Block.inner(area)` and fixes all example API mismatches.

### Changed (breaking — Rust internals only)

- **ratatui 0.30** is now the native backend (`ratatui-core 0.1`, `ratatui-widgets 0.3`).
- `Terminal::area()` now returns `Rect` converted from ratatui 0.30's `Size` type.
- `Frame::apply_effect` no longer requires `tachyonfx::Shader` in scope.
- `LineGauge::line_set()` now uses `filled_symbol` / `unfilled_symbol` internally.
- `Table::row_highlight_style()` replaces deprecated `highlight_style()`.
- `Table::to_ratatui()` now returns `RTable<'_>` (lifetime-aware) instead of `'static`.

### Added

- **`Block.inner(area: Rect) -> Rect`** — compute the inner area of a bordered
  block after subtracting borders and padding. Previously unavailable in Python
  bindings, causing examples 16 and 17 to fail at runtime.
- `ratatui_compat` internal dependency bridges tui-textarea 0.7 (ratatui 0.29) types
  with ratatui 0.30 types via zero-cost memory-layout transmutes.
- Examples renumbered sequentially (01–24) with no gaps.

### Fixed

- **Example 06 (`06_table_dynamic.py`)**: `Table(rows, widths, header=hdr)` constructor
  does not exist. Fixed to `Table(rows).column_widths(widths).header(hdr)`.
- **Example 10 (`10_full_app.py`)**: Same Table constructor bug fixed.
- **Example 15 (`15_textarea_advanced.py`)**: `Layout.default()` does not exist (use
  `Layout()`); `Constraint.Min/Length` → `Constraint.min/length` (lowercase).
- **Example 16 (`16_scrollview.py`)**: `Block` had no `inner()` method; added to
  Rust bindings. Example now uses `Block.inner(area)` correctly.
- **Example 17 (`17_qrcode.py`)**: `Layout.default()` → `Layout()`;
  `Constraint.Length/Min` → lowercase; `Block.inner(area)` now available.
- All 18 compile errors from ratatui 0.29 → 0.30 upgrade resolved.
- All 54 deprecation warnings resolved:
  - `Python::with_gil` → `Python::attach` (PyO3 0.28).
  - `PyObject` → `Py<PyAny>` (PyO3 0.28).
  - `ScrollViewState::scroll_*_by(n)` → loop over `scroll_*()` (tui-scrollview 0.6.2 API).
  - `KnownSizeWrapper` type bridge: `u16` → `usize` cast for width/height.
  - `tui-textarea` 0.7 Widget/Style/Block cross-version compatibility via safe `unsafe transmute`.
  - All `#[pyclass]` with `Clone` now opt-in via `from_py_object` attribute.
  - Unused imports (`EcLevel`, `Version`, `tachyonfx::Shader`) removed.
  - `StatefulWidget` trait imported in `scrollview/mod.rs`.

---

## [0.1.3] — 2025-03-06

### Summary

`0.1.3` is the largest single-feature release to date, adding **four major
third-party widget integrations** covering floating dialogs, full text editing,
scrollable viewports, and terminal QR codes.

| New module | Backing crate | Version | What it adds |
|---|---|---|---|
| `Popup` family | `tui-popup` | 0.7 | Centered floating dialogs with drag/scroll |
| `TextArea` family | `tui-textarea` | 0.7 | Full multi-line text editor (Emacs + Vim) |
| `ScrollView` family | `tui-scrollview` | 0.6 | Scrollable viewport for large content |
| `QrCodeWidget` family | `tui-qrcode` | 0.4 | Terminal QR code renderer |

All new types are importable directly from `pyratatui`:

```python
from pyratatui import (
    Popup, PopupState, KnownSizeWrapper,
    TextArea, CursorMove, Scrolling,
    ScrollView, ScrollViewState,
    QrCodeWidget, QrColors,
)
```

---

### Added

#### 🪟 `Popup`, `PopupState`, `KnownSizeWrapper` — `tui-popup` v0.7

Centered floating dialog widgets backed by [`tui-popup`](https://crates.io/crates/tui-popup).

**`Popup(content)`** — floating popup widget accepting a plain `str` body or a
`KnownSizeWrapper` for scrollable content. Builder methods: `.title(str)`,
`.style(Style)`.

**`PopupState`** — tracks popup position for draggable popups.
Methods: `move_up(n)`, `move_down(n)`, `move_left(n)`, `move_right(n)`,
`move_to(x, y)`, `mouse_down(col, row)`, `mouse_up(col, row)`,
`mouse_drag(col, row)`, `reset()`.

**`KnownSizeWrapper(lines, width, height, scroll=0)`** — wraps a list of strings
at a fixed display size for use as scrollable popup content.
Methods: `scroll_up(n)`, `scroll_down(n)`, `with_scroll(n)`.

**New `Frame` methods:**

```python
frame.render_popup(popup, area)                    # stateless centered popup
frame.render_stateful_popup(popup, area, state)    # draggable with position state
```

Examples: `11_popup_basic.py`, `12_popup_stateful.py`, `13_popup_scrollable.py`
Docs: `docs/reference/popups.md`

---

#### ✏️ `TextArea`, `CursorMove`, `Scrolling` — `tui-textarea` v0.7

Full integration of [`tui-textarea`](https://crates.io/crates/tui-textarea), a rich
multi-line text editor with Emacs-style default key bindings, undo/redo, yank/paste,
line numbers, cursor-line highlighting, and optional regex search.

> **Crate note:** `ratatui-textarea` on crates.io is deprecated (last release Jan 2024,
> maintainer archived). The actively maintained fork is `tui-textarea` by the original
> author. pyratatui uses `tui-textarea`.

**`TextArea`**

```python
ta = TextArea()                                  # empty editor
ta = TextArea.from_lines(["line 1", "line 2"])   # pre-filled
```

Key input — processes events through the default Emacs shortcuts:

```python
consumed: bool = ta.input_key(code, ctrl, alt, shift)
consumed: bool = ta.input_without_shortcuts(code, ctrl, alt, shift)
```

The underlying `tui_textarea::Input` struct carries `{ key, ctrl, alt }` (no `shift`
field). The Python `input_key` method accepts `shift` for API consistency with
pyratatui's `KeyEvent`, forwarding only `ctrl` and `alt` to the Rust side.

Editing methods (return `bool` — `True` if buffer was modified):

```python
ta.insert_str(s)          # insert string at cursor
ta.delete_char()          # Backspace
ta.delete_next_char()     # Delete key
ta.insert_newline()       # Enter / Ctrl+J
ta.delete_line_by_end()   # Ctrl+K — kill to end of line (→ yank buffer)
ta.delete_line_by_head()  # Ctrl+U — kill from head of line
ta.delete_word()          # Ctrl+W — delete word backward
ta.delete_next_word()     # Alt+D  — delete word forward
```

Clipboard / selection:

```python
ta.undo()                 # Ctrl+Z
ta.redo()                 # Ctrl+Y / Ctrl+R
ta.paste()                # paste yank buffer
ta.start_selection()
ta.cancel_selection()
ta.copy()
ta.cut()
ta.selection_range()      # → Optional[((r0,c0),(r1,c1))]
```

Cursor movement:

```python
ta.move_cursor(CursorMove.WordForward)
ta.move_cursor_to(row=5, col=0)   # absolute jump (clamped to valid range)
```

Viewport scrolling without moving the cursor:

```python
ta.scroll(Scrolling.HalfPageDown)
ta.scroll(Scrolling.PageUp)
```

Accessors:

```python
ta.lines()            # → list[str] — all text lines
ta.cursor()           # → (row: int, col: int)
ta.is_empty()         # → bool
ta.len()              # → int — number of lines
ta.selection_range()  # → Optional[((int,int),(int,int))]
```

Styling:

```python
ta.set_block(Block().bordered().title(" Editor "))
ta.set_cursor_style(Style().fg(Color.black()).bg(Color.white()))
ta.set_cursor_line_style(Style().bg(Color.dark_gray()))
ta.set_line_number_style(Style().fg(Color.dark_gray()))
ta.remove_line_number()
ta.set_placeholder_text("Start typing…")
ta.set_placeholder_style(Style().fg(Color.dark_gray()))
```

Configuration:

```python
ta.set_tab_length(2)           # spaces per tab stop (default: 4)
ta.set_hard_tab_indent(True)   # insert literal \t instead of spaces
ta.set_max_histories(100)      # undo stack depth (default: 50; 0 = unlimited)
```

**`CursorMove`** enum — cursor movement commands for `ta.move_cursor()`:

| Value | Effect |
|---|---|
| `Forward` / `Back` | One character right/left |
| `Up` / `Down` | One line up/down |
| `WordForward` / `WordBack` | One word forward/backward |
| `WordEnd` | End of current or next word |
| `Head` / `End` | Start/end of current line |
| `Top` / `Bottom` | First/last line |
| `ViewportTop/Middle/Bottom` | Edges of visible viewport |
| `ParagraphBack/Forward` | Blank-line-delimited paragraph boundaries |

**`Scrolling`** enum — scroll amounts for `ta.scroll()`:

| Value | Effect |
|---|---|
| `HalfPageDown` / `HalfPageUp` | Half a viewport |
| `PageDown` / `PageUp` | Full viewport |
| `DeltaDown` / `DeltaUp` | Single line |

**New `Frame` method:**

```python
frame.render_textarea(ta, area)
```

Examples: `14_textarea_basic.py` (Emacs), `15_textarea_advanced.py` (Vim modal)
Docs: `docs/reference/textarea.md`

---

#### 📜 `ScrollView`, `ScrollViewState` — `tui-scrollview` v0.6

Scrollable viewport for content larger than the terminal, backed by
[`tui-scrollview`](https://crates.io/crates/tui-scrollview) by joshka
(part of the `tui-widgets` suite).

The Rust crate implements `StatefulWidget`, meaning the full render call is:

```rust
// Rust (for reference):
let mut sv = ScrollView::new(Size::new(100, 200));
sv.render_widget(paragraph, Rect::new(0, 0, 100, 200));
StatefulWidget::render(sv, area, buf, &mut state);
```

The Python binding abstracts away buffer access entirely:

```python
sv = ScrollView.from_lines(lines, content_width=80)
frame.render_stateful_scrollview(sv, frame.area, state)
```

**`ScrollView`** — the scrollable canvas (create a new instance each frame;
it's cheap to build):

```python
# From a flat list of lines:
sv = ScrollView.from_lines(lines, content_width=80)

# From multiple positioned sections:
sv = ScrollView(content_width=80, content_height=50)
sv.add_paragraph("Header", x=0, y=0, width=80, height=3, title=" § ")
sv.add_paragraph("Body\nmore", x=0, y=3, width=80, height=20)

sv.content_width   # int
sv.content_height  # int
```

**`ScrollViewState`** — persistent scroll position, lives across frames:

```python
state = ScrollViewState()

state.scroll_down(n)      # scroll down n rows
state.scroll_up(n)        # scroll up n rows
state.scroll_right(n)     # scroll right n columns
state.scroll_left(n)      # scroll left n columns
state.scroll_to_top()     # jump to row 0
state.scroll_to_bottom()  # jump to last row
state.reset()             # alias for scroll_to_top

x, y = state.offset()    # current (col, row) scroll offset
```

**New `Frame` method:**

```python
frame.render_stateful_scrollview(sv, area, state)
```

Examples: `16_scrollview.py`
Docs: `docs/reference/scrollview.md`

---

#### 📱 `QrCodeWidget`, `QrColors` — `tui-qrcode` v0.4

Terminal QR code renderer backed by [`tui-qrcode`](https://crates.io/crates/tui-qrcode)
by joshka (part of the `tui-widgets` suite). Renders scannable QR codes using
Unicode block characters.

The upstream Rust API requires first creating a `qrcode::QrCode`:

```rust
// Rust (for reference):
let qr_code = QrCode::new("https://ratatui.rs").unwrap();
let widget = QrCodeWidget::new(qr_code).colors(Colors::Inverted);
frame.render_widget(widget, frame.area());
```

The Python binding internalises the `qrcode::QrCode` creation step so you always
work with plain strings:

```python
qr = QrCodeWidget("https://ratatui.rs").colors(QrColors.Inverted)
frame.render_qrcode(qr, frame.area)
```

**`QrCodeWidget(data: str)`** — accepts any QR-encodable string (URL, text, etc.).
Raises `ValueError` at construction time if the data cannot be encoded
(e.g. string exceeds QR capacity). Builder: `.colors(QrColors)`.

**`QrColors`** enum — color scheme:

| Value | Terminal appearance |
|---|---|
| `QrColors.Default` | Dark modules on light background |
| `QrColors.Inverted` | Light modules on dark background — recommended for dark terminals |

**New `Frame` method:**

```python
frame.render_qrcode(qr, area)
```

Examples: `17_qrcode.py`
Docs: `docs/reference/qrcode.md`

---

### Cargo.toml additions

```toml
tui-popup       = { version = "0.7", features = ["crossterm"] }
tui-textarea    = { version = "0.7" }
tui-scrollview  = { version = "0.6" }
tui-qrcode      = { version = "0.4" }
qrcode          = { version = "0.14", default-features = false }
```

### New Rust source files

```
src/popups/mod.rs      — Popup, PopupState, KnownSizeWrapper
src/textarea/mod.rs    — TextArea, CursorMove, Scrolling
src/scrollview/mod.rs  — ScrollView, ScrollViewState
src/qrcode/mod.rs      — QrCodeWidget, QrColors
```

### Python package additions

- `python/pyratatui/__init__.py` — all 10 new types exported at top level
- `python/pyratatui/__init__.pyi` — complete `.pyi` stub coverage including
  the new `Frame.render_textarea`, `Frame.render_stateful_scrollview`, and
  `Frame.render_qrcode` method signatures
- `docs/reference/textarea.md` — new
- `docs/reference/scrollview.md` — new
- `docs/reference/qrcode.md` — new
- `docs/reference/popups.md` — new
- `mkdocs.yml` — nav updated with four new reference pages
- `README.md` — new sections for each widget; module table updated

---

## [0.1.2] — Previous Release

_(Changelog entries for 0.1.2 and earlier are tracked in git history.)_
