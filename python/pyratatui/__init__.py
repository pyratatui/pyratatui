# ruff: noqa: F403, F405
"""
pyratatui — Professional Python bindings for ratatui.

Public API is available directly from this top-level package:

    from pyratatui import Terminal, Block, Paragraph, Color, Style
    from pyratatui import run_app, run_app_async, AsyncTerminal
    from pyratatui import Layout, Constraint, Direction, Rect, Alignment

Manager subpackage (programmatic access):

    from pyratatui.manager import install_app, list_apps, run_app, uninstall_app

Subpackages for explicit imports:

    from pyratatui.widgets  import Chart, Menu, PieChart, Throbber, ...
    from pyratatui.layout   import Layout, Constraint, Direction, Rect, Alignment
    from pyratatui.styling  import Color, Style, Modifier, Span, Line, Text
    from pyratatui.core     import AsyncTerminal, run_app, run_app_async
"""

from __future__ import annotations

# ── Rust extension (all native symbols) ──────────────────────────────────────
from ._pyratatui import *
from ._pyratatui import (
    Button,
    Canvas,
    Map,
    MapResolution,
    __ratatui_version__,
    __version__,
)

# ── Pure-Python modules ───────────────────────────────────────────────────────
from .async_terminal import AsyncTerminal
from .helpers import run_app, run_app_async

# ── Widget thin-wrappers (kept at top-level for backwards compat) ─────────────
from .widgets.chart import Axis, Chart, Dataset, GraphType, LegendPosition, Marker
from .widgets.checkbox import Checkbox
from .widgets.menu import Menu, MenuEvent, MenuItem, MenuState
from .widgets.piechart import PieChart, PieData, PieStyle
from .widgets.throbber import Throbber

__all__ = [
    # ── meta ─────────────────────────────────────────────────────────────────
    "__version__",
    "__ratatui_version__",
    # ── exceptions ────────────────────────────────────────────────────────────
    "PyratatuiError",
    "BackendError",
    "LayoutError",
    "RenderError",
    "AsyncError",
    "StyleError",
    # ── styling ───────────────────────────────────────────────────────────────
    "Color",
    "Modifier",
    "Style",
    "Span",
    "Line",
    "Text",
    # ── layout ────────────────────────────────────────────────────────────────
    "Rect",
    "Constraint",
    "Direction",
    "Alignment",
    "Layout",
    # ── runtime ───────────────────────────────────────────────────────────────
    "Buffer",
    "Terminal",
    "Frame",
    "AsyncTerminal",
    "run_app",
    "run_app_async",
    # ── core widgets (Rust-native) ─────────────────────────────────────────────
    "Block",
    "BorderType",
    "Paragraph",
    "Gauge",
    "List",
    "Table",
    "BarChart",
    "Sparkline",
    "Canvas",
    "Map",
    "MapResolution",
    "Button",
    "RatatuiMascot",
    "MascotEyeColor",
    # ── Python-wrapped widgets ─────────────────────────────────────────────────
    "Throbber",
    "Menu",
    "MenuItem",
    "MenuState",
    "MenuEvent",
    "PieChart",
    "PieData",
    "PieStyle",
    "Checkbox",
    "Chart",
    "Axis",
    "Dataset",
    "GraphType",
    "Marker",
    "LegendPosition",
    # ── extended Rust widgets ──────────────────────────────────────────────────
    "TreeItem",
    "Tree",
    "TreeState",
    "CalendarDate",
    "CalendarEventStore",
    "Monthly",
    "BarGraph",
    "BarGraphStyle",
    "BarColorMode",
    "Effect",
    "EffectManager",
    "Interpolation",
    "Motion",
    "CellFilter",
    "EffectTimer",
    "compile_effect",
    "ImagePicker",
    "ImageState",
    "ImageWidget",
    "init_logger",
    "log_message",
    "TuiLoggerWidget",
    "TuiWidgetState",
    "markdown_to_text",
]

__all__ = sorted(__all__)
