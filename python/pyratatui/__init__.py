"""
pyratatui — Python bindings for ratatui 0.29
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
    # Meta
    __version__,
    __ratatui_version__,

    # ── Exceptions ──────────────────────────────────────────────
    PyratatuiError,
    BackendError,
    LayoutError,
    RenderError,
    AsyncError,
    StyleError,

    # ── Style ───────────────────────────────────────────────────
    Color,
    Modifier,
    Style,

    # ── Text primitives ─────────────────────────────────────────
    Span,
    Line,
    Text,

    # ── Layout ──────────────────────────────────────────────────
    Rect,
    Constraint,
    Direction,
    Alignment,
    Layout,

    # ── Buffer ──────────────────────────────────────────────────
    Buffer,

    # ── Widgets ─────────────────────────────────────────────────
    Block,
    BorderType,
    Paragraph,
    List,
    ListItem,
    ListState,
    ListDirection,
    Table,
    TableState,
    Cell,
    Row,
    Gauge,
    LineGauge,
    BarChart,
    Bar,
    BarGroup,
    Sparkline,
    Clear,
    Scrollbar,
    ScrollbarState,
    ScrollbarOrientation,
    Tabs,

    # ── Terminal / Frame ────────────────────────────────────────
    Terminal,
    Frame,
    CrosstermBackend,

    # ── Events ──────────────────────────────────────────────────
    PyKeyEvent as KeyEvent,

    # ── Effects (TachyonFX) ─────────────────────────────────────
    Interpolation,
    Motion,
    EffectTimer,
    CellFilter,
    Effect,
    EffectManager,
    compile_effect,
)

from .async_terminal import AsyncTerminal
from .helpers import run_app, run_app_async

__all__ = [
    # Meta
    "__version__",
    "__ratatui_version__",
    # Exceptions
    "PyratatuiError", "BackendError", "LayoutError",
    "RenderError", "AsyncError", "StyleError",
    # Style
    "Color", "Modifier", "Style",
    # Text
    "Span", "Line", "Text",
    # Layout
    "Rect", "Constraint", "Direction", "Alignment", "Layout",
    # Buffer
    "Buffer",
    # Widgets
    "Block", "BorderType", "Paragraph",
    "List", "ListItem", "ListState", "ListDirection",
    "Table", "TableState", "Cell", "Row",
    "Gauge", "LineGauge",
    "BarChart", "Bar", "BarGroup",
    "Sparkline", "Clear",
    "Scrollbar", "ScrollbarState", "ScrollbarOrientation",
    "Tabs",
    # Terminal
    "Terminal", "Frame", "CrosstermBackend", "KeyEvent",
    # Python helpers
    "AsyncTerminal", "run_app", "run_app_async",
    # Effects
    "Interpolation", "Motion", "EffectTimer", "CellFilter",
    "Effect", "EffectManager", "compile_effect",
]
