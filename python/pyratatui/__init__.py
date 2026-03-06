"""
pyratatui — Python bindings for ratatui 0.30
===============================================

A production-grade, Pythonic bridge to ratatui — Rust's high-performance
terminal UI engine.  All rendering is done by the native Rust extension;
this package provides a clean, typed, idiomatic Python surface.

Quick-start
-----------
>>> from pyratatui import Terminal, Paragraph, Text, Block, Style, Color
>>>
>>> with Terminal() as term:
...     def ui(frame):
...         frame.render_widget(
...             Paragraph.from_string("Hello, pyratatui!")
...                 .block(Block().bordered().title("Demo"))
...                 .style(Style().fg(Color.cyan())),
...             frame.area
...         )
...     term.draw(ui)

See the project README and https://pyratatui.github.io/pyratatui for full docs.
"""

from __future__ import annotations

from ._pyratatui import (
    Alignment,
    AsyncError,
    BackendError,
    Bar,
    BarChart,
    BarGroup,
    Block,
    BorderType,
    Buffer,
    Cell,
    CellFilter,
    Clear,
    Color,
    Constraint,
    CrosstermBackend,
    CursorMove,
    Direction,
    Effect,
    EffectManager,
    EffectTimer,
    Frame,
    Gauge,
    Interpolation,
    KnownSizeWrapper,
    Layout,
    LayoutError,
    Line,
    LineGauge,
    List,
    ListDirection,
    ListItem,
    ListState,
    Modifier,
    Motion,
    Paragraph,
    PasswordPrompt,
    Popup,
    PopupState,
    PromptStatus,
)
from ._pyratatui import (
    PyKeyEvent as KeyEvent,
)  # Meta; ── Exceptions ──────────────────────────────────────────────; ── Style ───────────────────────────────────────────────────; ── Text primitives ─────────────────────────────────────────; ── Layout ──────────────────────────────────────────────────; ── Buffer ──────────────────────────────────────────────────; ── Widgets ─────────────────────────────────────────────────; ── Terminal / Frame ────────────────────────────────────────; ── Events ──────────────────────────────────────────────────; ── Effects (TachyonFX) ─────────────────────────────────────; ── Prompts ──────────────────────────────────────────────────────────
from ._pyratatui import (
    PyratatuiError,
    QrCodeWidget,
    QrColors,
    Rect,
    RenderError,
    Row,
    Scrollbar,
    ScrollbarOrientation,
    ScrollbarState,
    Scrolling,
    ScrollView,
    ScrollViewState,
    Span,
    Sparkline,
    Style,
    StyleError,
    Table,
    TableState,
    Tabs,
    Terminal,
    Text,
    TextArea,
    TextPrompt,
    TextRenderStyle,
    TextState,
    __ratatui_version__,
    __version__,
    compile_effect,
    prompt_password,
    prompt_text,
)
from .async_terminal import AsyncTerminal
from .helpers import run_app, run_app_async

__all__ = [
    # Meta
    "__version__",
    "__ratatui_version__",
    # Exceptions
    "PyratatuiError",
    "BackendError",
    "LayoutError",
    "RenderError",
    "AsyncError",
    "StyleError",
    # Style
    "Color",
    "Modifier",
    "Style",
    # Text
    "Span",
    "Line",
    "Text",
    # Layout
    "Rect",
    "Constraint",
    "Direction",
    "Alignment",
    "Layout",
    # Buffer
    "Buffer",
    # Widgets
    "Block",
    "BorderType",
    "Paragraph",
    "List",
    "ListItem",
    "ListState",
    "ListDirection",
    "Table",
    "TableState",
    "Cell",
    "Row",
    "Gauge",
    "LineGauge",
    "BarChart",
    "Bar",
    "BarGroup",
    "Sparkline",
    "Clear",
    "Scrollbar",
    "ScrollbarState",
    "ScrollbarOrientation",
    "Tabs",
    # Terminal
    "Terminal",
    "Frame",
    "CrosstermBackend",
    "KeyEvent",
    # Python helpers
    "AsyncTerminal",
    "run_app",
    "run_app_async",
    # Effects
    "Interpolation",
    "Motion",
    "EffectTimer",
    "CellFilter",
    "Effect",
    "EffectManager",
    "compile_effect",
    # Prompts
    "PromptStatus",
    "TextRenderStyle",
    "TextState",
    "TextPrompt",
    "PasswordPrompt",
    "prompt_text",
    "prompt_password",
    # Popups
    "Popup",
    "PopupState",
    "KnownSizeWrapper",
    # TextArea
    "TextArea",
    "CursorMove",
    "Scrolling",
    # ScrollView
    "ScrollView",
    "ScrollViewState",
    # QrCode
    "QrCodeWidget",
    "QrColors",
]
