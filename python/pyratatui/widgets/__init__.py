"""
pyratatui.widgets — High-level Python widget wrappers.

All names here are re-exported from the top-level ``pyratatui`` namespace,
so you can import from either location:

    from pyratatui import Chart, Menu, PieChart     # top-level
    from pyratatui.widgets import Chart, Menu       # subpackage
"""

from __future__ import annotations

# Also expose native Rust widgets that have no Python wrapper
from .._pyratatui import BarGraph  # noqa: F401
from .._pyratatui import (
    BarChart,
    BarColorMode,
    BarGraphStyle,
    Block,
    BorderType,
    Button,
    CalendarDate,
    CalendarEventStore,
    Canvas,
    Gauge,
    ImagePicker,
    ImageState,
    ImageWidget,
    List,
    Map,
    MapResolution,
    Monthly,
    Paragraph,
    Sparkline,
    Table,
    Tree,
    TreeItem,
    TreeState,
    TuiLoggerWidget,
    TuiWidgetState,
)
from .chart import Axis, Chart, Dataset, GraphType, LegendPosition, Marker
from .checkbox import Checkbox
from .menu import Menu, MenuEvent, MenuItem, MenuState
from .piechart import PieChart, PieData, PieStyle
from .throbber import Throbber

__all__ = [
    # Python-wrapped widgets
    "Axis",
    "Chart",
    "Checkbox",
    "Dataset",
    "GraphType",
    "LegendPosition",
    "Marker",
    "Menu",
    "MenuEvent",
    "MenuItem",
    "MenuState",
    "PieChart",
    "PieData",
    "PieStyle",
    "Throbber",
    # Native Rust widgets
    "BarChart",
    "BarGraph",
    "BarGraphStyle",
    "BarColorMode",
    "Block",
    "BorderType",
    "Button",
    "CalendarDate",
    "CalendarEventStore",
    "Canvas",
    "Gauge",
    "ImagePicker",
    "ImageState",
    "ImageWidget",
    "List",
    "Map",
    "MapResolution",
    "Monthly",
    "Paragraph",
    "Sparkline",
    "Table",
    "Tree",
    "TreeItem",
    "TreeState",
    "TuiLoggerWidget",
    "TuiWidgetState",
]
