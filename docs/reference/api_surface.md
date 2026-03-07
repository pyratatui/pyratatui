# API Surface — Full Parity Map

This document maps every Python-exposed Rust API to its Python binding,
type stub, documentation page, and example file.

> **Source of truth:** Rust implementation in `src/`. Python always mirrors Rust.

---

## Core Types

| Rust API | Python Name | Stub | Doc | Example |
|---|---|---|---|---|
| `Color` | `Color` | ✅ | `style.md` | `03_styled_text.py` |
| `Modifier` | `Modifier` | ✅ | `style.md` | `03_styled_text.py` |
| `Style` | `Style` | ✅ | `style.md` | `03_styled_text.py` |
| `Span` | `Span` | ✅ | `text.md` | `03_styled_text.py` |
| `Line` | `Line` | ✅ | `text.md` | `03_styled_text.py` |
| `Text` | `Text` | ✅ | `text.md` | `03_styled_text.py` |
| `Rect` | `Rect` | ✅ | `layout.md` | `02_layout.py` |
| `Constraint` | `Constraint` | ✅ | `layout.md` | `02_layout.py` |
| `Direction` | `Direction` | ✅ | `layout.md` | `02_layout.py` |
| `Alignment` | `Alignment` | ✅ | `layout.md` | `02_layout.py` |
| `Layout` | `Layout` | ✅ | `layout.md` | `02_layout.py` |
| `Buffer` | `Buffer` | ✅ | `buffer.md` | — |

---

## Widgets

| Rust API | Python Name | Stub | Doc | Example |
|---|---|---|---|---|
| `Block` | `Block` | ✅ | `widgets.md` | `01_hello_world.py` |
| `BorderType` | `BorderType` | ✅ | `widgets.md` | `01_hello_world.py` |
| `Paragraph` | `Paragraph` | ✅ | `widgets.md` | `01_hello_world.py` |
| `List` | `List` | ✅ | `widgets.md` | `04_list_navigation.py` |
| `ListItem` | `ListItem` | ✅ | `widgets.md` | `04_list_navigation.py` |
| `ListState` | `ListState` | ✅ | `widgets.md` | `04_list_navigation.py` |
| `ListDirection` | `ListDirection` | ✅ | `widgets.md` | `04_list_navigation.py` |
| `Table` | `Table` | ✅ | `widgets.md` | `06_table_dynamic.py` |
| `TableState` | `TableState` | ✅ | `widgets.md` | `06_table_dynamic.py` |
| `Cell` | `Cell` | ✅ | `widgets.md` | `06_table_dynamic.py` |
| `Row` | `Row` | ✅ | `widgets.md` | `06_table_dynamic.py` |
| `Gauge` | `Gauge` | ✅ | `widgets.md` | `05_progress_bar.py` |
| `LineGauge` | `LineGauge` | ✅ | `widgets.md` | `05_progress_bar.py` |
| `BarChart` | `BarChart` | ✅ | `widgets.md` | `24_dashboard.py` |
| `Bar` | `Bar` | ✅ | `widgets.md` | `24_dashboard.py` |
| `BarGroup` | `BarGroup` | ✅ | `widgets.md` | `24_dashboard.py` |
| `Sparkline` | `Sparkline` | ✅ | `widgets.md` | `24_dashboard.py` |
| `Clear` | `Clear` | ✅ | `widgets.md` | `11_popup_basic.py` |
| `Scrollbar` | `Scrollbar` | ✅ | `widgets.md` | `10_full_app.py` |
| `ScrollbarState` | `ScrollbarState` | ✅ | `widgets.md` | `10_full_app.py` |
| `ScrollbarOrientation` | `ScrollbarOrientation` | ✅ | `widgets.md` | `10_full_app.py` |
| `Tabs` | `Tabs` | ✅ | `widgets.md` | `10_full_app.py` |
| `Monthly` *(calendar)* | `Monthly` | ✅ | `calendar.md` | `25_calendar.py` |
| `CalendarDate` *(time::Date)* | `CalendarDate` | ✅ | `calendar.md` | `25_calendar.py` |
| `CalendarEventStore` | `CalendarEventStore` | ✅ | `calendar.md` | `25_calendar.py` |

---

## Terminal & Frame

| Rust API | Python Name | Stub | Doc | Example |
|---|---|---|---|---|
| `Terminal` | `Terminal` | ✅ | `terminal.md` | `01_hello_world.py` |
| `Frame` | `Frame` | ✅ | `terminal.md` | `01_hello_world.py` |
| `PyKeyEvent` | `KeyEvent` | ✅ | `terminal.md` | `04_list_navigation.py` |
| `CrosstermBackend` | `CrosstermBackend` | ✅ | `terminal.md` | — |
| *(Python)* `AsyncTerminal` | `AsyncTerminal` | ✅ | `terminal.md` | `07_async_reactive.py` |

### Frame render methods

| Method | Widget type | Stateful |
|---|---|---|
| `render_widget(w, area)` | All standard widgets + `Monthly` | — |
| `render_stateful_list(w, area, state)` | `List` | `ListState` |
| `render_stateful_table(w, area, state)` | `Table` | `TableState` |
| `render_stateful_scrollbar(w, area, state)` | `Scrollbar` | `ScrollbarState` |
| `render_popup(popup, area)` | `Popup` | — |
| `render_stateful_popup(popup, area, state)` | `Popup` | `PopupState` |
| `render_textarea(ta, area)` | `TextArea` | *(internal)* |
| `render_stateful_scrollview(sv, area, state)` | `ScrollView` | `ScrollViewState` |
| `render_qrcode(qr, area)` | `QrCodeWidget` | — |
| `apply_effect(effect, ms, area)` | `Effect` | — |
| `apply_effect_manager(mgr, ms, area)` | `EffectManager` | — |
| `render_text_prompt(prompt, area, state)` | `TextPrompt` | `TextState` |
| `render_password_prompt(prompt, area, state)` | `PasswordPrompt` | `TextState` |

---

## Effects (TachyonFX)

| Rust API | Python Name | Stub | Doc | Example |
|---|---|---|---|---|
| `Effect` | `Effect` | ✅ | `effects.md` | `08_effects_fade.py` |
| `EffectManager` | `EffectManager` | ✅ | `effects.md` | `08_effects_fade.py` |
| `EffectTimer` | `EffectTimer` | ✅ | `effects.md` | `08_effects_fade.py` |
| `Interpolation` | `Interpolation` | ✅ | `effects.md` | `08_effects_fade.py` |
| `Motion` | `Motion` | ✅ | `effects.md` | `08_effects_fade.py` |
| `CellFilter` | `CellFilter` | ✅ | `effects.md` | `09_effects_dsl.py` |
| `compile_effect` | `compile_effect` | ✅ | `effects.md` | `09_effects_dsl.py` |

---

## Prompts

| Rust API | Python Name | Stub | Doc | Example |
|---|---|---|---|---|
| `TextPrompt` | `TextPrompt` | ✅ | `prompts.md` | `23_prompt_text.py` |
| `PasswordPrompt` | `PasswordPrompt` | ✅ | `prompts.md` | `21_prompt_confirm.py` |
| `TextState` | `TextState` | ✅ | `prompts.md` | `23_prompt_text.py` |
| `TextRenderStyle` | `TextRenderStyle` | ✅ | `prompts.md` | `23_prompt_text.py` |
| `PromptStatus` | `PromptStatus` | ✅ | `prompts.md` | `23_prompt_text.py` |
| `prompt_text` | `prompt_text` | ✅ | `prompts.md` | — |
| `prompt_password` | `prompt_password` | ✅ | `prompts.md` | — |

---

## Popups

| Rust API | Python Name | Stub | Doc | Example |
|---|---|---|---|---|
| `Popup` | `Popup` | ✅ | `popups.md` | `11_popup_basic.py` |
| `PopupState` | `PopupState` | ✅ | `popups.md` | `12_popup_stateful.py` |
| `KnownSizeWrapper` | `KnownSizeWrapper` | ✅ | `popups.md` | `13_popup_scrollable.py` |

---

## TextArea

| Rust API | Python Name | Stub | Doc | Example |
|---|---|---|---|---|
| `TextArea` | `TextArea` | ✅ | `textarea.md` | `14_textarea_basic.py` |
| `CursorMove` | `CursorMove` | ✅ | `textarea.md` | `15_textarea_advanced.py` |
| `Scrolling` | `Scrolling` | ✅ | `textarea.md` | `15_textarea_advanced.py` |

---

## ScrollView

| Rust API | Python Name | Stub | Doc | Example |
|---|---|---|---|---|
| `ScrollView` | `ScrollView` | ✅ | `scrollview.md` | `16_scrollview.py` |
| `ScrollViewState` | `ScrollViewState` | ✅ | `scrollview.md` | `16_scrollview.py` |

---

## QR Code

| Rust API | Python Name | Stub | Doc | Example |
|---|---|---|---|---|
| `QrCodeWidget` | `QrCodeWidget` | ✅ | `qrcode.md` | `17_qrcode.py` |
| `QrColors` | `QrColors` | ✅ | `qrcode.md` | `17_qrcode.py` |

---

## Calendar *(new in 0.2.1)*

| Rust API | Python Name | Stub | Doc | Example |
|---|---|---|---|---|
| `time::Date` (wrapped) | `CalendarDate` | ✅ | `calendar.md` | `25_calendar.py` |
| `CalendarEventStore` | `CalendarEventStore` | ✅ | `calendar.md` | `25_calendar.py` |
| `Monthly` | `Monthly` | ✅ | `calendar.md` | `25_calendar.py` |

---

## Web TUI *(new in 0.2.1)*

| Python API | Module | Doc | Example |
|---|---|---|---|
| `WebTerminal` | `pyratatui.web` | `web.md` | `26_web_counter.py` |
| `WebKeyEvent` | `pyratatui.web` | `web.md` | `26_web_counter.py` |
| `serve()` | `pyratatui.web` | `web.md` | `26_web_counter.py` |

---

## Python-only Helpers

| Name | Module | Doc |
|---|---|---|
| `AsyncTerminal` | `pyratatui.async_terminal` | `terminal.md` |
| `run_app(ui_fn, fps, on_key)` | `pyratatui.helpers` | `terminal.md` |
| `run_app_async(ui_fn, fps, on_key)` | `pyratatui.helpers` | `terminal.md` |
