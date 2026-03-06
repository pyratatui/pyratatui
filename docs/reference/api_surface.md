# API Surface — Full Parity Map

This document maps every Rust API exposed to Python, its Python binding,
its type stub, documentation location, and example file.

> **Source of truth**: Rust implementation. Python always mirrors Rust.

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

## Terminal & Frame

| Rust API | Python Name | Stub | Doc | Example |
|---|---|---|---|---|
| `Terminal` | `Terminal` | ✅ | `terminal.md` | `01_hello_world.py` |
| `Frame` | `Frame` | ✅ | `terminal.md` | `01_hello_world.py` |
| `PyKeyEvent` | `KeyEvent` | ✅ | `terminal.md` | `04_list_navigation.py` |
| `CrosstermBackend` | `CrosstermBackend` | ✅ | `terminal.md` | — |

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

## Prompts

| Rust API | Python Name | Stub | Doc | Example |
|---|---|---|---|---|
| `TextPrompt` | `TextPrompt` | ✅ | `prompts.md` | `23_prompt_text.py` |
| `PasswordPrompt` | `PasswordPrompt` | ✅ | `prompts.md` | `23_prompt_text.py` |
| `TextState` | `TextState` | ✅ | `prompts.md` | `23_prompt_text.py` |
| `TextRenderStyle` | `TextRenderStyle` | ✅ | `prompts.md` | `23_prompt_text.py` |
| `PromptStatus` | `PromptStatus` | ✅ | `prompts.md` | `21_prompt_confirm.py` |
| `prompt_text` | `prompt_text` | ✅ | `prompts.md` | `23_prompt_text.py` |
| `prompt_password` | `prompt_password` | ✅ | `prompts.md` | `23_prompt_text.py` |

## Popups

| Rust API | Python Name | Stub | Doc | Example |
|---|---|---|---|---|
| `Popup` | `Popup` | ✅ | `popups.md` | `11_popup_basic.py` |
| `PopupState` | `PopupState` | ✅ | `popups.md` | `12_popup_stateful.py` |
| `KnownSizeWrapper` | `KnownSizeWrapper` | ✅ | `popups.md` | `13_popup_scrollable.py` |

## TextArea

| Rust API | Python Name | Stub | Doc | Example |
|---|---|---|---|---|
| `TextArea` | `TextArea` | ✅ | `textarea.md` | `14_textarea_basic.py` |
| `CursorMove` | `CursorMove` | ✅ | `textarea.md` | `15_textarea_advanced.py` |
| `Scrolling` | `Scrolling` | ✅ | `textarea.md` | `15_textarea_advanced.py` |

## ScrollView

| Rust API | Python Name | Stub | Doc | Example |
|---|---|---|---|---|
| `ScrollView` | `ScrollView` | ✅ | `scrollview.md` | `16_scrollview.py` |
| `ScrollViewState` | `ScrollViewState` | ✅ | `scrollview.md` | `16_scrollview.py` |

## QR Code

| Rust API | Python Name | Stub | Doc | Example |
|---|---|---|---|---|
| `QrCodeWidget` | `QrCodeWidget` | ✅ | `qrcode.md` | `17_qrcode.py` |
| `QrColors` | `QrColors` | ✅ | `qrcode.md` | `17_qrcode.py` |

## Python-only helpers

| Python API | Type | Doc | Example |
|---|---|---|---|
| `AsyncTerminal` | class | `terminal.md` | `07_async_reactive.py` |
| `run_app` | function | `terminal.md` | `10_full_app.py` |
| `run_app_async` | function | `terminal.md` | `07_async_reactive.py` |
