# pyratatui Migration: ratatui 0.28/0.29 → 0.30

## Summary of Changes

### Cargo.toml

| Dependency | Old | New | Reason |
|---|---|---|---|
| `ratatui` | `"0.29"` | `"0.30"` | Core upgrade |
| `ratatui` features | `all-widgets` | `all-widgets, crossterm_0_29` | Pins crossterm version for ecosystem compat |
| `tui-textarea` | `"0.7"` | `"0.7"` | Unchanged; `>=0.23, <1` range covers 0.30 |
| `tui-popup` | `"0.6"` | `"0.7"` | ratatui 0.30 compatible |
| `tui-scrollview` | `"0.6"` | `"0.7"` | ratatui 0.30 compatible |
| `tui-qrcode` | `"0.1"` | **removed** | Incompatible alpha dep; replaced with native |
| `qrcode` | — | `"0.14"` | Native QR rendering |
| `tachyonfx` | `"0.11"` | `"0.11"` | Already compatible |

---

## ratatui 0.30 Breaking Changes Applied

### 1. `Block::title()` removed → `title_top()` / `title_bottom()`

The old `block::Title` struct and `Block::title()` method were removed.

```rust
// BEFORE (0.29)
block.title("My Title")
block.title_bottom("Footer")

// AFTER (0.30) — both API sides
block.title_top(Line::from("My Title"))
block.title_bottom(Line::from("Footer"))
```

### 2. `Alignment` → `HorizontalAlignment` (alias kept)

`ratatui::layout::Alignment` is now a type alias for `HorizontalAlignment`. The old import path still compiles.

### 3. `Sparkline::data()` now accepts `IntoIterator<Item = SparklineBar>`

```rust
// BEFORE
sparkline.data(&data)              // data: &[u64]

// AFTER
let bars: Vec<SparklineBar> = data.iter().copied().map(SparklineBar::from).collect();
sparkline.data(bars)
```

### 4. `Frame::size()` removed → `Frame::area()`

```rust
// BEFORE
let area = frame.size();

// AFTER
let area = frame.area();
```

### 5. `Terminal::size()` now returns `Result<Rect, B::Error>`

```rust
// BEFORE
term.get_frame().area()

// AFTER
term.size()?
```

### 6. `Bar::label()` / `BarGroup::label()` now accept `Into<Line<'a>>`

Callers that passed `.label("text".into())` can now just pass `.label(Line::from("text"))`.

### 7. `List::highlight_symbol()` now accepts `Into<Line>`

Same pattern — wrap in `Line::from(...)`.

### 8. Backend `Error` associated type

`Terminal<B: Backend>` now requires `B::Error` to implement `std::error::Error`. `CrosstermBackend` satisfies this automatically.

---

## tui-popup 0.7 API Changes

```rust
// BEFORE (0.6)
Popup::new("title", "body content")

// AFTER (0.7) — body is the first arg, title is a builder method
Popup::new("body content").title("title").style(...)
frame.render_widget(popup, area)           // stateless
frame.render_stateful_widget(popup, area, state)  // stateful
```

`KnownSizeWrapper` struct fields: `{ inner, width, height }` (unchanged).

---

## tui-scrollview 0.7 API Changes

```rust
// render API
let mut sv = ScrollView::new(Size::new(w, h));
sv.render_widget(widget, area);
sv.render(area, buf, state);   // ← direct method, NOT StatefulWidget trait
```

`ScrollViewState` scroll methods: `scroll_down_by(n)`, `scroll_up_by(n)`, `scroll_left_by(n)`, `scroll_right_by(n)`, `scroll_to_top()`, `scroll_to_bottom()`.

---

## tui-qrcode Replacement

`tui-qrcode` was removed (depends on incompatible `ratatui-core 0.1.0-alpha`).

Replaced with a native implementation using `qrcode = "0.14"` + Unicode half-block characters:
- `█` — both modules dark  
- `▀` — top dark, bottom light  
- `▄` — top light, bottom dark  
- ` ` — both light  

This halves the vertical height of QR codes (2 QR rows → 1 terminal row).

---

## Python API Compatibility

**All Python APIs are 100% backwards compatible.** No changes to:
- Class names, method names, or signatures
- Import paths (`from pyratatui import ...`)
- Behavior or semantics

---

## Python Example API Fixes (0.2.0)

Several examples had API mismatches that caused blank screens or runtime errors.
If you copied patterns from earlier examples, update them:

### `Table` constructor

```python
# ❌ WRONG (does not exist — Table takes only rows)
Table(rows, [Constraint.fill(1)], header=header_row)

# ✅ CORRECT — chain .column_widths() and .header()
Table(rows).column_widths([Constraint.fill(1)]).header(header_row)
```

### `Layout` construction

```python
# ❌ WRONG — Layout has no .default() static method
Layout.default().direction(Direction.Vertical)

# ✅ CORRECT
Layout().direction(Direction.Vertical)
```

### `Constraint` method names

```python
# ❌ WRONG — PascalCase does not exist
Constraint.Length(10)
Constraint.Min(0)
Constraint.Max(100)

# ✅ CORRECT — always snake_case
Constraint.length(10)
Constraint.min(0)
Constraint.max(100)
```

### `Block.inner(area)` — new in 0.2.0

```python
# ❌ WRONG (0.1.x — Block had no .inner() method)
# caused AttributeError at runtime

# ✅ CORRECT (0.2.0+)
block = Block().bordered().title("Panel")
inner = block.inner(frame.area)   # returns Rect with borders subtracted
frame.render_widget(block, frame.area)
frame.render_widget(content_widget, inner)
```
