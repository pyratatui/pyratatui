"""
tests/python/test_pyratatui.py

Integration tests for pyratatui.  Validates the Python API surface
without opening a real terminal.  All tests must pass with
``pytest tests/python/test_pyratatui.py``.
"""

from __future__ import annotations

import inspect
from datetime import date as _pydate

import pytest

# ── Style ─────────────────────────────────────────────────────────────────────


class TestColor:
    def test_named_colors(self):
        from pyratatui import Color

        assert Color.red() is not None
        assert Color.green() is not None
        assert Color.blue() is not None
        assert Color.cyan() is not None
        assert Color.reset() is not None

    def test_indexed_color(self):
        from pyratatui import Color

        c = Color.indexed(196)
        assert c is not None
        assert "196" in repr(c)

    def test_rgb_color(self):
        from pyratatui import Color

        c = Color.rgb(255, 128, 0)
        assert c is not None

    def test_equality(self):
        from pyratatui import Color

        assert Color.red() == Color.red()
        assert Color.red() != Color.green()


class TestModifier:
    def test_bold(self):
        from pyratatui import Modifier

        assert Modifier.bold() is not None

    def test_or_combine(self):
        from pyratatui import Modifier

        m = Modifier.bold() | Modifier.italic()
        assert m is not None


class TestStyle:
    def test_default_style(self):
        from pyratatui import Style

        s = Style()
        assert s.foreground is None
        assert s.background is None

    def test_fg_bg_chain(self):
        from pyratatui import Color, Style

        s = Style().fg(Color.red()).bg(Color.black())
        assert s.foreground == Color.red()
        assert s.background == Color.black()

    def test_modifier_chain(self):
        from pyratatui import Style

        s = Style().bold().italic().underlined()
        assert s is not None

    def test_patch(self):
        from pyratatui import Color, Style

        base = Style().fg(Color.red())
        overlay = Style().bg(Color.black())
        merged = base.patch(overlay)
        assert merged.foreground == Color.red()
        assert merged.background == Color.black()

    def test_repr(self):
        from pyratatui import Style

        assert "Style" in repr(Style())


# ── Text primitives ───────────────────────────────────────────────────────────


class TestSpan:
    def test_plain_span(self):
        from pyratatui import Span

        s = Span("hello")
        assert s.content == "hello"
        assert s.style is None
        assert s.width() == 5

    def test_styled_span(self):
        from pyratatui import Color, Span, Style

        s = Span("hi", Style().fg(Color.green()))
        assert s.style is not None

    def test_styled_method(self):
        from pyratatui import Color, Span, Style

        s = Span("test").styled(Style().fg(Color.blue()))
        assert s.style is not None


class TestLine:
    def test_from_string(self):
        from pyratatui import Line

        ln = Line.from_string("Hello World")
        assert len(ln.spans) == 1
        assert ln.width() == 11

    def test_alignment(self):
        from pyratatui import Line

        ln = Line.from_string("test")
        assert ln.centered() is not None
        assert ln.right_aligned() is not None
        assert ln.left_aligned() is not None

    def test_push_span(self):
        from pyratatui import Line, Span

        ln = Line()
        ln.push_span(Span("a"))
        ln.push_span(Span("b"))
        assert len(ln.spans) == 2


class TestText:
    def test_from_string_multiline(self):
        from pyratatui import Text

        t = Text.from_string("line1\nline2\nline3")
        assert t.height == 3

    def test_push_str(self):
        from pyratatui import Text

        t = Text()
        t.push_str("first")
        t.push_str("second")
        assert t.height == 2

    def test_centered(self):
        from pyratatui import Text

        t = Text.from_string("hello").centered()
        assert t is not None


# ── Layout ────────────────────────────────────────────────────────────────────


class TestRect:
    def test_creation(self):
        from pyratatui import Rect

        r = Rect(0, 0, 80, 24)
        assert r.x == 0
        assert r.y == 0
        assert r.width == 80
        assert r.height == 24

    def test_area(self):
        from pyratatui import Rect

        assert Rect(0, 0, 80, 24).area() == 1920

    def test_inner(self):
        from pyratatui import Rect

        r = Rect(0, 0, 80, 24)
        inner = r.inner(2, 1)
        assert inner.width == 76
        assert inner.height == 22

    def test_edges(self):
        from pyratatui import Rect

        r = Rect(10, 5, 20, 10)
        assert r.right == 30
        assert r.bottom == 15
        assert r.left == 10
        assert r.top == 5

    def test_is_empty(self):
        from pyratatui import Rect

        assert Rect(0, 0, 0, 0).is_empty()
        assert not Rect(0, 0, 1, 1).is_empty()

    def test_intersection(self):
        from pyratatui import Rect

        a = Rect(0, 0, 10, 10)
        b = Rect(5, 5, 10, 10)
        i = a.intersection(b)
        assert i is not None
        assert i.width == 5
        assert i.height == 5

    def test_no_intersection(self):
        from pyratatui import Rect

        a = Rect(0, 0, 5, 5)
        b = Rect(10, 10, 5, 5)
        assert a.intersection(b) is None

    def test_equality(self):
        from pyratatui import Rect

        assert Rect(0, 0, 80, 24) == Rect(0, 0, 80, 24)
        assert Rect(0, 0, 80, 24) != Rect(1, 0, 80, 24)


class TestConstraint:
    def test_all_variants(self):
        from pyratatui import Constraint

        assert Constraint.length(10) is not None
        assert Constraint.percentage(50) is not None
        assert Constraint.fill(1) is not None
        assert Constraint.min(5) is not None
        assert Constraint.max(20) is not None
        assert Constraint.ratio(1, 3) is not None


class TestLayout:
    def test_vertical_split(self):
        from pyratatui import Constraint, Direction, Layout, Rect

        area = Rect(0, 0, 80, 24)
        chunks = (
            Layout()
            .direction(Direction.Vertical)
            .constraints([Constraint.length(3), Constraint.fill(1)])
            .split(area)
        )
        assert len(chunks) == 2
        assert chunks[0].height == 3
        assert chunks[1].y == 3

    def test_horizontal_split(self):
        from pyratatui import Constraint, Direction, Layout, Rect

        area = Rect(0, 0, 80, 24)
        chunks = (
            Layout()
            .direction(Direction.Horizontal)
            .constraints([Constraint.percentage(50), Constraint.percentage(50)])
            .split(area)
        )
        assert len(chunks) == 2

    def test_nested_layout(self):
        from pyratatui import Constraint, Direction, Layout, Rect

        area = Rect(0, 0, 100, 40)
        outer = (
            Layout()
            .direction(Direction.Vertical)
            .constraints([Constraint.length(5), Constraint.fill(1)])
            .split(area)
        )
        inner = (
            Layout()
            .direction(Direction.Horizontal)
            .constraints([Constraint.fill(1), Constraint.fill(1)])
            .split(outer[1])
        )
        assert len(inner) == 2


# ── Widgets ───────────────────────────────────────────────────────────────────


class TestBlock:
    def test_default(self):
        from pyratatui import Block

        assert Block() is not None

    def test_chain(self):
        from pyratatui import Block, BorderType, Color, Style

        b = (
            Block()
            .title("Test")
            .bordered()
            .border_type(BorderType.Rounded)
            .style(Style().fg(Color.cyan()))
            .padding(1, 1, 0, 0)
        )
        assert "Test" in repr(b)

    def test_borders(self):
        from pyratatui import Block

        b = Block().borders(top=True, right=False, bottom=True, left=False)
        assert b is not None


class TestParagraph:
    def test_from_string(self):
        from pyratatui import Paragraph

        assert Paragraph.from_string("Hello") is not None

    def test_chain(self):
        from pyratatui import Block, Color, Paragraph, Style

        p = (
            Paragraph.from_string("Test")
            .block(Block().bordered())
            .style(Style().fg(Color.white()))
            .wrap(True, True)
            .scroll(2, 0)
            .centered()
        )
        assert p is not None


class TestList:
    def test_list_creation(self):
        from pyratatui import List, ListItem

        items = [ListItem(f"Item {i}") for i in range(5)]
        lst = List(items)
        assert lst is not None
        assert "5" in repr(lst)

    def test_list_state(self):
        from pyratatui import ListState

        state = ListState()
        state.select(2)
        assert state.selected == 2
        state.select_next()
        assert state.selected == 3
        state.select_previous()
        assert state.selected == 2
        state.select(None)
        assert state.selected is None

    def test_list_chain(self):
        from pyratatui import Block, Color, List, ListItem, Style

        lst = (
            List([ListItem("item")])
            .block(Block().bordered())
            .highlight_style(Style().fg(Color.yellow()))
            .highlight_symbol("\u25b6 ")
        )
        assert lst is not None


class TestTable:
    def test_table_state(self):
        from pyratatui import TableState

        s = TableState()
        s.select(0)
        assert s.selected == 0
        s.select_next()
        assert s.selected == 1


class TestGauge:
    def test_gauge(self):
        from pyratatui import Color, Gauge, Style

        g = Gauge().percent(75).style(Style().fg(Color.green())).label("75%")
        assert "75" in repr(g)

    def test_gauge_ratio(self):
        from pyratatui import Gauge

        assert Gauge().ratio(0.5) is not None

    def test_line_gauge(self):
        from pyratatui import LineGauge

        lg = LineGauge().ratio(0.65).line_set("double")
        assert "0.65" in repr(lg)


class TestBarChart:
    def test_bar_chart(self):
        from pyratatui import Bar, BarChart, BarGroup

        chart = (
            BarChart()
            .data(BarGroup([Bar(10, "Jan"), Bar(20, "Feb")]))
            .bar_width(5)
            .max(30)
        )
        assert chart is not None

    def test_bar_repr(self):
        from pyratatui import Bar

        assert "42" in repr(Bar(42, "Test"))


class TestSparkline:
    def test_sparkline(self):
        from pyratatui import Color, Sparkline, Style

        s = Sparkline().data([10, 20, 15, 35, 25]).style(Style().fg(Color.green()))
        assert "5" in repr(s)


class TestScrollbar:
    def test_scrollbar_state(self):
        from pyratatui import ScrollbarState

        assert ScrollbarState().content_length(100).position(20) is not None

    def test_scrollbar(self):
        from pyratatui import Scrollbar, ScrollbarOrientation

        assert Scrollbar(ScrollbarOrientation.VerticalRight) is not None


class TestTabs:
    def test_tabs(self):
        from pyratatui import Color, Style, Tabs

        tabs = (
            Tabs(["Tab 1", "Tab 2", "Tab 3"])
            .select(1)
            .highlight_style(Style().fg(Color.yellow()))
            .divider(" | ")
        )
        assert "3" in repr(tabs)
        assert "selected=1" in repr(tabs)


# ── Calendar (0.2.1) ──────────────────────────────────────────────────────────


class TestCalendarDate:
    def test_today(self):
        from pyratatui import CalendarDate

        d = CalendarDate.today()
        today = _pydate.today()
        assert d.year == today.year
        assert d.month == today.month
        assert d.day == today.day

    def test_from_ymd_valid(self):
        from pyratatui import CalendarDate

        d = CalendarDate.from_ymd(2024, 3, 15)
        assert d.year == 2024
        assert d.month == 3
        assert d.day == 15

    def test_from_ymd_invalid_raises(self):
        from pyratatui import CalendarDate

        with pytest.raises(ValueError):
            CalendarDate.from_ymd(2024, 2, 30)
        with pytest.raises(ValueError):
            CalendarDate.from_ymd(2024, 13, 1)

    def test_repr(self):
        from pyratatui import CalendarDate

        d = CalendarDate.from_ymd(2024, 3, 15)
        assert "2024" in repr(d)
        assert "15" in repr(d)

    def test_str(self):
        from pyratatui import CalendarDate

        d = CalendarDate.from_ymd(2024, 3, 15)
        s = str(d)
        assert "2024" in s and "15" in s

    def test_equality(self):
        from pyratatui import CalendarDate

        a = CalendarDate.from_ymd(2024, 1, 1)
        b = CalendarDate.from_ymd(2024, 1, 1)
        c = CalendarDate.from_ymd(2024, 1, 2)
        assert a == b
        assert a != c

    def test_hashable(self):
        from pyratatui import CalendarDate

        d1 = CalendarDate.from_ymd(2024, 6, 15)
        d2 = CalendarDate.from_ymd(2024, 6, 15)
        s = {d1, d2}
        assert len(s) == 1
        m = {d1: "event"}
        assert m[d2] == "event"


class TestCalendarEventStore:
    def test_new(self):
        from pyratatui import CalendarEventStore

        store = CalendarEventStore()
        assert store is not None

    def test_add(self):
        from pyratatui import CalendarDate, CalendarEventStore, Color, Style

        store = CalendarEventStore()
        store.add(CalendarDate.from_ymd(2024, 12, 25), Style().fg(Color.red()).bold())
        assert "1" in repr(store)

    def test_add_today(self):
        from pyratatui import CalendarEventStore, Color, Style

        store = CalendarEventStore()
        store.add_today(Style().fg(Color.green()))
        assert store is not None

    def test_today_highlighted(self):
        from pyratatui import CalendarEventStore, Color, Style

        store = CalendarEventStore.today_highlighted(Style().fg(Color.cyan()).bold())
        assert store is not None
        assert "1" in repr(store)

    def test_repr(self):
        from pyratatui import CalendarEventStore

        r = repr(CalendarEventStore())
        assert "CalendarEventStore" in r


class TestMonthly:
    def test_creation(self):
        from pyratatui import CalendarDate, CalendarEventStore, Monthly

        d = CalendarDate.from_ymd(2024, 3, 1)
        store = CalendarEventStore()
        cal = Monthly(d, store)
        assert cal is not None

    def test_builder_methods(self):
        from pyratatui import (
            Block,
            CalendarDate,
            CalendarEventStore,
            Color,
            Monthly,
            Style,
        )

        d = CalendarDate.from_ymd(2024, 6, 1)
        store = CalendarEventStore()
        cal = (
            Monthly(d, store)
            .block(Block().bordered().title(" June "))
            .show_month_header(Style().bold().fg(Color.cyan()))
            .show_weekdays_header(Style().italic())
            .show_surrounding(Style().dim())
            .default_style(Style().fg(Color.white()))
        )
        assert cal is not None

    def test_repr(self):
        from pyratatui import CalendarDate, CalendarEventStore, Monthly

        cal = Monthly(CalendarDate.from_ymd(2024, 3, 1), CalendarEventStore())
        r = repr(cal)
        assert "Monthly" in r
        assert "2024" in r


# ── BarGraph (new) ────────────────────────────────────────────────────────────


class TestBarGraph:
    def test_creation(self):
        from pyratatui import BarGraph

        bg = BarGraph([0.1, 0.5, 0.9])
        assert bg is not None
        assert bg.len == 3

    def test_builder_chain(self):
        from pyratatui import BarColorMode, BarGraph, BarGraphStyle

        bg = (
            BarGraph([0.2, 0.4, 0.6, 0.8])
            .bar_style(BarGraphStyle.Braille)
            .color_mode(BarColorMode.VerticalGradient)
            .gradient("viridis")
        )
        assert bg is not None
        assert bg.len == 4

    def test_style_variants(self):
        from pyratatui import BarGraph, BarGraphStyle

        assert BarGraph([0.5]).bar_style(BarGraphStyle.Braille) is not None
        assert BarGraph([0.5]).bar_style(BarGraphStyle.HalfBlock) is not None
        assert BarGraph([0.5]).bar_style(BarGraphStyle.Block) is not None

    def test_color_modes(self):
        from pyratatui import BarColorMode, BarGraph

        assert BarGraph([0.5]).color_mode(BarColorMode.VerticalGradient) is not None
        assert BarGraph([0.5]).color_mode(BarColorMode.HorizontalGradient) is not None
        assert BarGraph([0.5]).color_mode(BarColorMode.Bar) is not None

    def test_gradient_presets(self):
        from pyratatui import BarGraph

        for name in ["turbo", "rainbow", "sinebow", "plasma", "viridis"]:
            assert BarGraph([0.5]).gradient(name) is not None

    def test_data_replacement(self):
        from pyratatui import BarGraph

        bg = BarGraph([0.1, 0.2]).data([0.5, 0.6, 0.7])
        assert bg.len == 3

    def test_repr(self):
        from pyratatui import BarGraph

        r = repr(BarGraph([0.1, 0.2, 0.3]))
        assert "BarGraph" in r
        assert "3" in r


# ── TreeWidget (new) ──────────────────────────────────────────────────────────


class TestTreeItem:
    def test_leaf_node(self):
        from pyratatui import TreeItem

        item = TreeItem("Leaf")
        assert item.text == "Leaf"
        assert item.children == []

    def test_with_children(self):
        from pyratatui import TreeItem

        child = TreeItem("Child")
        parent = TreeItem("Parent", [child])
        assert len(parent.children) == 1
        assert parent.children[0].text == "Child"

    def test_with_child_method(self):
        from pyratatui import TreeItem

        parent = TreeItem("Parent")
        child = TreeItem("Child")
        parent2 = parent.with_child(child)
        assert len(parent2.children) == 1

    def test_repr(self):
        from pyratatui import TreeItem

        item = TreeItem("Root", [TreeItem("A"), TreeItem("B")])
        r = repr(item)
        assert "TreeItem" in r
        assert "Root" in r


class TestTree:
    def test_creation(self):
        from pyratatui import Tree, TreeItem

        items = [TreeItem("Root")]
        t = Tree(items)
        assert t is not None
        assert t.len == 1

    def test_builder_chain(self):
        from pyratatui import Block, Color, Style, Tree, TreeItem

        items = [
            TreeItem("Documents", [TreeItem("notes.txt")]),
            TreeItem("Downloads"),
        ]
        t = (
            Tree(items)
            .block(Block().bordered().title(" Files "))
            .highlight_style(Style().fg(Color.yellow()).bold())
            .highlight_symbol("> ")
        )
        assert t is not None
        assert t.len == 2

    def test_repr(self):
        from pyratatui import Tree, TreeItem

        t = Tree([TreeItem("A"), TreeItem("B")])
        r = repr(t)
        assert "Tree" in r
        assert "2" in r


class TestTreeState:
    def test_creation(self):
        from pyratatui import TreeState

        state = TreeState()
        assert state is not None
        assert state.selected is None

    def test_select(self):
        from pyratatui import TreeState

        state = TreeState()
        state.select([0])
        assert state.selected == [0]

    def test_clear_selection(self):
        from pyratatui import TreeState

        state = TreeState()
        state.select([0])
        state.select([])
        assert state.selected is None

    def test_open_close(self):
        from pyratatui import TreeState

        state = TreeState()
        opened = state.open([0])
        assert isinstance(opened, bool)
        closed = state.close([0])
        assert isinstance(closed, bool)

    def test_toggle(self):
        from pyratatui import TreeState

        state = TreeState()
        result = state.toggle([0])
        assert isinstance(result, bool)

    def test_navigation(self):
        from pyratatui import TreeState

        state = TreeState()
        assert isinstance(state.key_up(), bool)
        assert isinstance(state.key_down(), bool)
        assert isinstance(state.key_left(), bool)
        assert isinstance(state.key_right(), bool)

    def test_repr(self):
        from pyratatui import TreeState

        state = TreeState()
        r = repr(state)
        assert "TreeState" in r


# ── Markdown (new) ────────────────────────────────────────────────────────────


class TestMarkdown:
    def test_plain_text(self):
        from pyratatui import markdown_to_text

        t = markdown_to_text("Hello, world!")
        assert t is not None
        assert t.height >= 1

    def test_heading(self):
        from pyratatui import markdown_to_text

        t = markdown_to_text("# Heading\n\nParagraph text.")
        assert t is not None
        assert t.height >= 2

    def test_bold_italic(self):
        from pyratatui import markdown_to_text

        t = markdown_to_text("**bold** and *italic* text")
        assert t is not None

    def test_list_items(self):
        from pyratatui import markdown_to_text

        t = markdown_to_text("- Item one\n- Item two\n- Item three")
        assert t is not None

    def test_empty_string(self):
        from pyratatui import markdown_to_text

        t = markdown_to_text("")
        assert t is not None

    def test_returns_text_type(self):
        from pyratatui import Text, markdown_to_text

        t = markdown_to_text("# Hello")
        assert isinstance(t, Text)

    def test_usable_in_paragraph(self):
        from pyratatui import Paragraph, markdown_to_text

        t = markdown_to_text("# Hello\n\nWorld")
        p = Paragraph(t)
        assert p is not None


# ── Logger (new) ──────────────────────────────────────────────────────────────


class TestLogger:
    def test_init_logger(self):
        from pyratatui import init_logger

        # init_logger is idempotent — repeated calls just update the level
        init_logger("debug")
        init_logger("info")
        init_logger("trace")
        init_logger("warn")
        init_logger("error")

    def test_invalid_level_raises(self):
        from pyratatui import init_logger

        with pytest.raises(ValueError):
            init_logger("INVALID_LEVEL")

    def test_log_message(self):
        from pyratatui import init_logger, log_message

        init_logger("trace")
        log_message("info", "Test message from pytest")
        log_message("debug", "Debug detail")
        log_message("warn", "Warning!")
        log_message("error", "Error occurred")

    def test_widget_creation(self):
        from pyratatui import TuiLoggerWidget

        w = TuiLoggerWidget()
        assert w is not None

    def test_widget_builder(self):
        from pyratatui import Block, Color, Style, TuiLoggerWidget

        w = (
            TuiLoggerWidget()
            .block(Block().bordered().title(" Logs "))
            .style(Style().fg(Color.white()))
            .error_style(Style().fg(Color.red()).bold())
            .warn_style(Style().fg(Color.yellow()))
            .info_style(Style().fg(Color.green()))
            .debug_style(Style().fg(Color.cyan()))
            .trace_style(Style().fg(Color.gray()))
        )
        assert w is not None

    def test_widget_state(self):
        from pyratatui import TuiWidgetState

        state = TuiWidgetState()
        assert state is not None

    def test_state_transitions(self):
        from pyratatui import TuiWidgetState

        state = TuiWidgetState()
        state.transition("up")
        state.transition("down")
        state.transition("pageup")
        state.transition("pagedown")
        state.transition("+")
        state.transition("-")

    def test_widget_repr(self):
        from pyratatui import TuiLoggerWidget, TuiWidgetState

        assert "TuiLoggerWidget" in repr(TuiLoggerWidget())
        assert "TuiWidgetState" in repr(TuiWidgetState())


# ── Image (new) ───────────────────────────────────────────────────────────────


class TestImageWidget:
    def test_picker_creation(self):
        from pyratatui import ImagePicker

        picker = ImagePicker.halfblocks()
        assert picker is not None

    def test_picker_with_font_size(self):
        from pyratatui import ImagePicker

        picker = ImagePicker.with_font_size(8, 16)
        assert picker is not None

    def test_image_widget_creation(self):
        from pyratatui import ImageWidget

        w = ImageWidget()
        assert w is not None

    def test_image_widget_repr(self):
        from pyratatui import ImageWidget

        assert "ImageWidget" in repr(ImageWidget())

    def test_picker_repr(self):
        from pyratatui import ImagePicker

        r = repr(ImagePicker.halfblocks())
        assert "ImagePicker" in r

    def test_load_nonexistent_raises(self):
        from pyratatui import ImagePicker

        picker = ImagePicker.halfblocks()
        with pytest.raises(OSError):
            picker.load("/nonexistent/path/image.png")


# ── No web/ratxilla module ────────────────────────────────────────────────────


class TestNoWebModule:
    def test_ratxilla_not_importable(self):
        with pytest.raises(ImportError):
            import pyratatui.ratxilla  # noqa: F401

    def test_web_not_importable(self):
        with pytest.raises(ImportError):
            import pyratatui.web  # noqa: F401


# ── Async ─────────────────────────────────────────────────────────────────────


class TestAsyncTerminal:
    def test_import(self):
        from pyratatui import AsyncTerminal

        at = AsyncTerminal()
        assert at is not None
        assert "active=False" in repr(at)

    def test_run_app_import(self):
        from pyratatui import run_app, run_app_async

        assert callable(run_app)
        assert inspect.iscoroutinefunction(run_app_async)


# ── Error hierarchy ───────────────────────────────────────────────────────────


class TestExceptions:
    def test_hierarchy(self):
        from pyratatui import (
            AsyncError,
            BackendError,
            LayoutError,
            PyratatuiError,
            RenderError,
            StyleError,
        )

        assert issubclass(BackendError, PyratatuiError)
        assert issubclass(LayoutError, PyratatuiError)
        assert issubclass(RenderError, PyratatuiError)
        assert issubclass(AsyncError, PyratatuiError)
        assert issubclass(StyleError, PyratatuiError)
        assert issubclass(PyratatuiError, Exception)

    def test_raise_and_catch(self):
        from pyratatui import LayoutError, PyratatuiError

        with pytest.raises(PyratatuiError):
            raise LayoutError("test error")


# ── Version ───────────────────────────────────────────────────────────────────


class TestVersion:
    def test_version_present(self):
        import pyratatui

        assert hasattr(pyratatui, "__version__")
        assert hasattr(pyratatui, "__ratatui_version__")
        assert pyratatui.__version__ == "0.2.1"
        assert pyratatui.__ratatui_version__ == "0.30"

    def test_public_api_complete(self):
        import pyratatui

        required = [
            # Core
            "Terminal",
            "Frame",
            "Layout",
            "Rect",
            "Constraint",
            # Widgets
            "Block",
            "Paragraph",
            "Style",
            "Color",
            "Text",
            "Gauge",
            "List",
            "Table",
            "BarChart",
            "Sparkline",
            # Calendar
            "CalendarDate",
            "CalendarEventStore",
            "Monthly",
            # Effects
            "Effect",
            "EffectManager",
            "Interpolation",
            "Motion",
            "CellFilter",
            "EffectTimer",
            "compile_effect",
            # New widgets
            "BarGraph",
            "BarGraphStyle",
            "BarColorMode",
            "TreeItem",
            "Tree",
            "TreeState",
            "markdown_to_text",
            "TuiLoggerWidget",
            "TuiWidgetState",
            "ImagePicker",
            "ImageState",
            "ImageWidget",
        ]
        for name in required:
            assert hasattr(pyratatui, name), f"Missing: {name}"


# ── Effects (TachyonFX) ───────────────────────────────────────────────────────


class TestInterpolation:
    def test_variants_present(self):
        from pyratatui import Interpolation

        for v in [
            "Linear",
            "QuadIn",
            "QuadOut",
            "SineIn",
            "SineOut",
            "BounceIn",
            "BounceOut",
            "ElasticIn",
            "ElasticOut",
            "CubicIn",
            "CubicOut",
            "BackIn",
            "BackOut",
        ]:
            assert hasattr(Interpolation, v), f"Missing Interpolation.{v}"

    def test_equality(self):
        from pyratatui import Interpolation

        assert Interpolation.Linear == Interpolation.Linear
        assert Interpolation.QuadIn != Interpolation.QuadOut


class TestMotion:
    def test_variants(self):
        from pyratatui import Motion

        assert Motion.LeftToRight != Motion.RightToLeft
        assert Motion.UpToDown != Motion.DownToUp


class TestEffectTimer:
    def test_default_linear(self):
        from pyratatui import EffectTimer, Interpolation

        t = EffectTimer(500)
        assert t.duration_ms == 500
        assert t.interpolation == Interpolation.Linear

    def test_custom_interpolation(self):
        from pyratatui import EffectTimer, Interpolation

        t = EffectTimer(1000, Interpolation.BounceOut)
        assert t.duration_ms == 1000
        assert t.interpolation == Interpolation.BounceOut

    def test_repr(self):
        from pyratatui import EffectTimer

        assert "500ms" in repr(EffectTimer(500))


class TestCellFilter:
    def test_static_factories(self):
        from pyratatui import CellFilter, Color

        assert CellFilter.all() is not None
        assert CellFilter.text() is not None
        assert CellFilter.fg_color(Color.red()) is not None
        assert CellFilter.bg_color(Color.black()) is not None
        assert CellFilter.inner(1, 1) is not None
        assert CellFilter.outer(2, 1) is not None

    def test_combined_filters(self):
        from pyratatui import CellFilter, Color

        f = CellFilter.all_of([CellFilter.text(), CellFilter.inner(1, 1)])
        f2 = CellFilter.any_of([CellFilter.fg_color(Color.red()), CellFilter.text()])
        assert f is not None
        assert f2 is not None


class TestEffect:
    def test_fade_from_fg(self):
        from pyratatui import Color, Effect, Interpolation

        e = Effect.fade_from_fg(Color.black(), 500, Interpolation.QuadOut)
        assert e is not None
        assert not e.done()

    def test_fade_to_fg(self):
        from pyratatui import Color, Effect

        assert Effect.fade_to_fg(Color.white(), 300) is not None

    def test_coalesce(self):
        from pyratatui import Effect, Interpolation

        assert Effect.coalesce(500, Interpolation.SineIn) is not None

    def test_dissolve(self):
        from pyratatui import Effect, Interpolation

        assert Effect.dissolve(800, Interpolation.BounceOut) is not None

    def test_sleep(self):
        from pyratatui import Effect

        assert Effect.sleep(200) is not None

    def test_sequence(self):
        from pyratatui import Color, Effect

        seq = Effect.sequence(
            [Effect.fade_from_fg(Color.black(), 300), Effect.dissolve(400)]
        )
        assert seq is not None

    def test_parallel(self):
        from pyratatui import Color, Effect, Motion

        par = Effect.parallel(
            [
                Effect.fade_from_fg(Color.black(), 300),
                Effect.slide_in(Motion.LeftToRight, 0, 0, Color.black(), 400),
            ]
        )
        assert par is not None

    def test_repeat(self):
        from pyratatui import Color, Effect

        assert Effect.repeat(Effect.fade_from_fg(Color.black(), 200), 3) is not None

    def test_repr(self):
        from pyratatui import Effect

        assert "Effect" in repr(Effect.sleep(100))


class TestEffectManager:
    def test_creation(self):
        from pyratatui import EffectManager

        mgr = EffectManager()
        assert mgr.active_count() == 0
        assert not mgr.has_active()

    def test_add_and_clear(self):
        from pyratatui import Color, Effect, EffectManager

        mgr = EffectManager()
        mgr.add(Effect.fade_from_fg(Color.black(), 1000))
        assert mgr.has_active()
        mgr.clear()
        assert not mgr.has_active()

    def test_repr(self):
        from pyratatui import EffectManager

        assert "EffectManager" in repr(EffectManager())


class TestCompileEffect:
    def test_simple_dissolve(self):
        from pyratatui import compile_effect

        assert compile_effect("fx::dissolve(500)") is not None

    def test_coalesce(self):
        from pyratatui import compile_effect

        assert compile_effect("fx::coalesce((400, SineOut))") is not None

    def test_repr(self):
        from pyratatui import compile_effect

        assert "Effect" in repr(compile_effect("fx::sleep(50)"))
