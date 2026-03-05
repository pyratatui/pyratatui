# Changelog

All notable changes to this project will be documented in this file.

The format loosely follows Keep a Changelog principles and semantic versioning.

---

## [0.1.2] - Latest Release

### Added

#### Formatting Scripts

- `scripts/format.ps1`
- `scripts/format.sh`

#### Prompt widgets (`pyratatui.prompts`)

New stateful prompt system built directly on ratatui 0.29 — no extra crate
dependency required.

| Class / function | Description |
|---|---|
| `TextState` | Mutable input buffer, cursor, focus flag, and lifecycle status |
| `TextPrompt` | Single-line text input with live block cursor |
| `PasswordPrompt` | Masked password input (`*` for every character) |
| `TextRenderStyle` | `Normal` / `Password` / `Invisible` display modes |
| `PromptStatus` | `Pending` / `Complete` / `Aborted` lifecycle enum |
| `prompt_text(label)` | Blocking helper — opens a TUI dialog and returns `str \| None` |
| `prompt_password(label)` | Same as above but input is masked |

Prompts are rendered inside the normal `draw()` callback via two new `Frame`
methods:

```python
frame.render_text_prompt(TextPrompt("Name: "), area, state)
frame.render_password_prompt(PasswordPrompt("Password: "), area, state)
```

`TextState.handle_key()` implements full readline / emacs key bindings:

| Key | Action |
|---|---|
| Enter | Complete (`status → Complete`) |
| Esc / Ctrl+C | Abort (`status → Aborted`) |
| Backspace / Delete | Delete character |
| Left / Right | Move cursor |
| Home / Ctrl+A, End / Ctrl+E | Jump to start / end |
| Ctrl+K | Kill to end of line |
| Ctrl+U | Kill entire line |
| Ctrl+W | Delete word before cursor |

Example:

```python
from pyratatui import Terminal, TextPrompt, TextState

state = TextState()
state.focus()

with Terminal() as term:
    term.hide_cursor()
    while state.is_pending():
        def ui(frame, _s=state):
            frame.render_text_prompt(TextPrompt("Name: "), frame.area, _s)
        term.draw(ui)
        ev = term.poll_event(timeout_ms=50)
        if ev:
            state.handle_key(ev)

if state.is_complete():
    print(f"Hello, {state.value()}!")
```

#### New examples

| File | Demonstrates |
|---|---|
| `examples/effects_glitch.py` | `dissolve → sleep → coalesce` sequence, SPACE to replay |
| `examples/effects_matrix.py` | `sweep_in → sweep_out` with selectable direction |
| `examples/prompt_text.py` | Full `TextPrompt` / `TextState` loop with readline hint panel |
| `examples/prompt_confirm.py` | y/n confirmation prompt using `TextState` |
| `examples/prompt_select.py` | Arrow-key menu selection built on the core event loop |

### Changed

#### Examples 08 and 09 — SPACE bar replay

`examples/08_effects_fade.py` and `examples/09_effects_dsl.py` now respond to
the **SPACE** key by resetting and replaying the current effect animation.
Previously the only way to rewatch an effect was to restart the program.

### Fixed

#### Rust / Clippy (all errors under `cargo clippy -- -D warnings`)

| Location | Issue | Fix |
|---|---|---|
| `src/effects/mod.rs` | `EffectTimer::to_tachyonfx` reported as dead code | Added `#[allow(dead_code)]` — kept for future use |
| `src/effects/mod.rs` | `CellFilterKind::AllOf` / `AnyOf` unused `Vec<CellFilter>` fields | Changed payload to `()` and updated constructors |
| `src/layout/mod.rs` | `Alignment::to_ratatui` reported as dead code | Added `#[allow(dead_code)]` — kept for future widget use |
| `src/widgets/mod.rs` | `register_canvas` declared but never called | Added call in `register_widgets` |
| `src/widgets/sparkline.rs` | `bar_set` and `direction` struct fields never read | Removed fields and their initialisers |
| `src/terminal/mod.rs` | Unnecessary double pointer cast `*mut RFrame<'_> as *mut RFrame<'static>` | Replaced with `std::mem::transmute` (invariant lifetime) |
| `src/terminal/mod.rs` | Single-arm `match` should be `if let` | Replaced `match event::read()` block with `if let` |
| `src/text/mod.rs` | Redundant closure `\|l\| Line::from_string(l)` | Replaced with `Line::from_string` method reference |
| `src/prompts/mod.rs` | `cursor_col + 1 <= len()` (clippy `int_plus_one`) | Simplified to `cursor_col < len()` |

#### Python tests

| Test | Issue | Fix |
|---|---|---|
| `TestEffect::test_slide_in` | `NameError: name 'Color' is not defined` | Added `Color` to the local import |
| `TestEffect::test_slide_out` | Same | Same |
| `TestAsyncTerminal::test_run_app_import` | `asyncio.iscoroutinefunction` deprecated in Python 3.14 | Changed to `inspect.iscoroutinefunction` |

#### Pytest configuration

Removed the `asyncio_mode = "auto"` key from `[tool.pytest.ini_options]` in
`pyproject.toml`.  It is a `pytest-asyncio` plugin option that is not
recognised by the base pytest config parser, causing a `PytestConfigWarning`
on every run.

#### `examples/prompt_confirm.py` — terminal hang

`Block` has no `.inner()` method in the Python bindings.  The original code
called `block.inner(rows[1])` inside the `draw()` callback.  Because
`Terminal.draw()` silently discards Python exceptions from the callback, this
caused the terminal to go blank and the event loop to spin indefinitely.

**Fix:** replaced `block.inner(rows[1])` with `rows[1].inner(1, 1)`.
`Rect.inner(horizontal, vertical)` is the correct API — it returns the area
remaining after removing one cell of margin on each edge (the standard inset
of a bordered `Block`).

---

## [0.1.1] - Previous Release

### Changed

* Improved GitHub workflows for CI reliability.
* Updated repository workflows to modern action versions.

### Documentation

* Refined project README for clarity.
* Improved installation instructions and usage guidance.

---

## [0.1.0] - Initial Release

### Added

* First public release of **pyratatui**.
* Python bindings for the Rust `ratatui` crate using **PyO3** and **maturin**.
* Core ratatui types exposed to Python: `Terminal`, `Frame`, `Buffer`, `Rect`.
* Full widget set: `Paragraph`, `Block`, `List`, `Table`, `Gauge`, `LineGauge`,
  `BarChart`, `Sparkline`, `Scrollbar`, `Tabs`, `Clear`.
* Style system: `Color`, `Modifier`, `Style`.
* Text primitives: `Span`, `Line`, `Text`.
* Layout engine: `Layout`, `Constraint`, `Direction`, `Alignment`.
* TachyonFX animation effects: `Effect`, `EffectManager`, `CellFilter`,
  `Interpolation`, `Motion`, `EffectTimer`, `compile_effect()`.
* Terminal lifecycle management through a context-manager API.
* Async support via `AsyncTerminal` and `run_app` / `run_app_async` helpers.
* Initial examples (01–10) covering hello-world through full async apps.

```python
from pyratatui import Terminal, Paragraph, Block, Style, Color

with Terminal() as term:
    while True:
        def ui(frame):
            frame.render_widget(
                Paragraph.from_string("Hello, pyratatui!")
                    .block(Block().bordered().title("Hello World"))
                    .style(Style().fg(Color.cyan())),
                frame.area,
            )
        term.draw(ui)
        ev = term.poll_event(timeout_ms=100)
        if ev and ev.code == "q":
            break
```
