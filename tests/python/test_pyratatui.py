"""
tests/python/test_pyratatui.py

Integration tests for pyratatui.  These tests validate the Python API surface
without opening an actual terminal (uses ratatui's TestBackend concept via
mocked draws where needed).
"""

from __future__ import annotations

import asyncio
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
        m = Modifier.bold()
        assert m is not None

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
        from pyratatui import Style, Color
        s = Style().fg(Color.red()).bg(Color.black())
        assert s.foreground == Color.red()
        assert s.background == Color.black()

    def test_modifier_chain(self):
        from pyratatui import Style, Modifier
        s = Style().bold().italic().underlined()
        assert s is not None

    def test_patch(self):
        from pyratatui import Style, Color
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
        from pyratatui import Span, Style, Color
        s = Span("hi", Style().fg(Color.green()))
        assert s.style is not None

    def test_styled_method(self):
        from pyratatui import Span, Style, Color
        s = Span("test").styled(Style().fg(Color.blue()))
        assert s.style is not None


class TestLine:
    def test_from_string(self):
        from pyratatui import Line
        l = Line.from_string("Hello World")
        assert len(l.spans) == 1
        assert l.width() == 11

    def test_alignment(self):
        from pyratatui import Line
        l = Line.from_string("test")
        assert l.centered() is not None
        assert l.right_aligned() is not None
        assert l.left_aligned() is not None

    def test_push_span(self):
        from pyratatui import Line, Span
        l = Line()
        l.push_span(Span("a"))
        l.push_span(Span("b"))
        assert len(l.spans) == 2


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
        r = Rect(0, 0, 80, 24)
        assert r.area() == 1920

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
        from pyratatui import Layout, Constraint, Direction, Rect
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
        from pyratatui import Layout, Constraint, Direction, Rect
        area = Rect(0, 0, 80, 24)
        chunks = (
            Layout()
            .direction(Direction.Horizontal)
            .constraints([Constraint.percentage(50), Constraint.percentage(50)])
            .split(area)
        )
        assert len(chunks) == 2

    def test_nested_layout(self):
        from pyratatui import Layout, Constraint, Direction, Rect
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

    def test_no_constraints_raises(self):
        from pyratatui import Layout, Rect
        with pytest.raises(Exception):
            Layout().split(Rect(0, 0, 80, 24))


# ── Widgets ───────────────────────────────────────────────────────────────────

class TestBlock:
    def test_default(self):
        from pyratatui import Block
        b = Block()
        assert b is not None

    def test_chain(self):
        from pyratatui import Block, Style, Color, BorderType
        b = (Block()
             .title("Test")
             .bordered()
             .border_type(BorderType.Rounded)
             .style(Style().fg(Color.cyan()))
             .padding(1, 1, 0, 0))
        assert "Test" in repr(b)

    def test_borders(self):
        from pyratatui import Block
        b = Block().borders(top=True, right=False, bottom=True, left=False)
        assert b is not None


class TestParagraph:
    def test_from_string(self):
        from pyratatui import Paragraph
        p = Paragraph.from_string("Hello")
        assert p is not None

    def test_chain(self):
        from pyratatui import Paragraph, Block, Style, Color
        p = (Paragraph.from_string("Test")
             .block(Block().bordered())
             .style(Style().fg(Color.white()))
             .wrap(True, True)
             .scroll(2, 0)
             .centered())
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
        from pyratatui import List, ListItem, Block, Style, Color
        lst = (List([ListItem("item")])
               .block(Block().bordered())
               .highlight_style(Style().fg(Color.yellow()))
               .highlight_symbol("▶ "))
        assert lst is not None


class TestTable:
    def test_table_creation(self):
        from pyratatui import Table, Row, Cell, Constraint
        rows = [Row([Cell("Alice"), Cell("Engineer")])]
        widths = [Constraint.percentage(50), Constraint.percentage(50)]
        tbl = Table(rows, widths)
        assert "2" in repr(tbl)

    def test_table_with_header(self):
        from pyratatui import Table, Row, Cell, Constraint
        header = Row([Cell("Name"), Cell("Role")])
        rows = [Row.from_strings(["Alice", "Engineer"])]
        widths = [Constraint.fill(1), Constraint.fill(1)]
        tbl = Table(rows, widths, header=header)
        assert tbl is not None

    def test_table_state(self):
        from pyratatui import TableState
        s = TableState()
        s.select(0)
        assert s.selected == 0
        s.select_next()
        assert s.selected == 1


class TestGauge:
    def test_gauge(self):
        from pyratatui import Gauge, Style, Color
        g = (Gauge()
             .percent(75)
             .style(Style().fg(Color.green()))
             .label("75%"))
        assert "75" in repr(g)

    def test_gauge_ratio(self):
        from pyratatui import Gauge
        g = Gauge().ratio(0.5)
        assert g is not None

    def test_line_gauge(self):
        from pyratatui import LineGauge
        lg = LineGauge().ratio(0.65).line_set("double")
        assert "0.65" in repr(lg)


class TestBarChart:
    def test_bar_chart(self):
        from pyratatui import BarChart, BarGroup, Bar
        chart = (BarChart()
                 .data(BarGroup([Bar(10, "Jan"), Bar(20, "Feb")]))
                 .bar_width(5)
                 .max(30))
        assert chart is not None

    def test_bar_repr(self):
        from pyratatui import Bar
        b = Bar(42, "Test")
        assert "42" in repr(b)


class TestSparkline:
    def test_sparkline(self):
        from pyratatui import Sparkline, Style, Color
        s = (Sparkline()
             .data([10, 20, 15, 35, 25])
             .style(Style().fg(Color.green())))
        assert "5" in repr(s)


class TestScrollbar:
    def test_scrollbar_state(self):
        from pyratatui import ScrollbarState
        state = ScrollbarState().content_length(100).position(20)
        assert state is not None

    def test_scrollbar(self):
        from pyratatui import Scrollbar, ScrollbarOrientation
        sb = Scrollbar(ScrollbarOrientation.VerticalRight)
        assert sb is not None


class TestTabs:
    def test_tabs(self):
        from pyratatui import Tabs, Style, Color
        tabs = (Tabs(["Tab 1", "Tab 2", "Tab 3"])
                .select(1)
                .highlight_style(Style().fg(Color.yellow()))
                .divider(" | "))
        assert "3" in repr(tabs)
        assert "selected=1" in repr(tabs)


# ── Async ─────────────────────────────────────────────────────────────────────

class TestAsyncTerminal:
    """
    Async terminal tests — these don't open a real TTY but verify
    the async API surface is importable and correctly typed.
    """

    def test_import(self):
        from pyratatui import AsyncTerminal
        at = AsyncTerminal()
        assert at is not None
        assert "active=False" in repr(at)

    def test_run_app_import(self):
        from pyratatui import run_app, run_app_async
        assert callable(run_app)
        assert asyncio.iscoroutinefunction(run_app_async)


# ── Error hierarchy ───────────────────────────────────────────────────────────

class TestExceptions:
    def test_hierarchy(self):
        from pyratatui import (
            PyratatuiError, BackendError, LayoutError,
            RenderError, AsyncError, StyleError,
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
        assert pyratatui.__ratatui_version__ == "0.30.0"

    def test_public_api_complete(self):
        import pyratatui
        required = [
            "Terminal", "Frame", "Layout", "Rect", "Constraint",
            "Block", "Paragraph", "Style", "Color", "Text",
            "Gauge", "List", "Table", "BarChart", "Sparkline",
            # Effects
            "Effect", "EffectManager", "Interpolation", "Motion",
            "CellFilter", "EffectTimer", "compile_effect",
        ]
        for name in required:
            assert hasattr(pyratatui, name), f"Missing: {name}"

# ── Effects (TachyonFX) ───────────────────────────────────────────────────────

class TestInterpolation:
    def test_variants_present(self):
        from pyratatui import Interpolation
        variants = [
            "Linear", "QuadIn", "QuadOut", "SineIn", "SineOut",
            "BounceIn", "BounceOut", "ElasticIn", "ElasticOut",
            "CubicIn", "CubicOut", "BackIn", "BackOut",
        ]
        for v in variants:
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
        assert f is not None
        f2 = CellFilter.any_of([CellFilter.fg_color(Color.red()), CellFilter.text()])
        assert f2 is not None


class TestEffect:
    def test_fade_from_fg(self):
        from pyratatui import Effect, Color, Interpolation
        e = Effect.fade_from_fg(Color.black(), 500, Interpolation.QuadOut)
        assert e is not None
        assert not e.done()

    def test_fade_to_fg(self):
        from pyratatui import Effect, Color
        e = Effect.fade_to_fg(Color.white(), 300)
        assert e is not None

    def test_fade_from_full(self):
        from pyratatui import Effect, Color, Interpolation
        e = Effect.fade_from(Color.black(), Color.white(), 600, Interpolation.SineOut)
        assert e is not None

    def test_fade_to_full(self):
        from pyratatui import Effect, Color
        e = Effect.fade_to(Color.black(), Color.black(), 400)
        assert e is not None

    def test_coalesce(self):
        from pyratatui import Effect, Interpolation
        e = Effect.coalesce(500, Interpolation.SineIn)
        assert e is not None

    def test_dissolve(self):
        from pyratatui import Effect, Interpolation
        e = Effect.dissolve(800, Interpolation.BounceOut)
        assert e is not None

    def test_slide_in(self):
        from pyratatui import Effect, Motion, Interpolation
        e = Effect.slide_in(Motion.LeftToRight, 0, 0, Color.black(), 600, Interpolation.QuadOut)
        assert e is not None

    def test_slide_out(self):
        from pyratatui import Effect, Motion
        e = Effect.slide_out(Motion.RightToLeft, 0, 0, Color.black(), 400)
        assert e is not None

    def test_sweep_in(self):
        from pyratatui import Effect, Motion, Color, Interpolation
        e = Effect.sweep_in(Motion.UpToDown, 15, 0, Color.black(), 600, Interpolation.QuadOut)
        assert e is not None

    def test_sleep(self):
        from pyratatui import Effect
        e = Effect.sleep(200)
        assert e is not None

    def test_sequence(self):
        from pyratatui import Effect, Color, Interpolation
        e1 = Effect.fade_from_fg(Color.black(), 300)
        e2 = Effect.dissolve(400)
        seq = Effect.sequence([e1, e2])
        assert seq is not None

    def test_parallel(self):
        from pyratatui import Effect, Color, Motion
        e1 = Effect.fade_from_fg(Color.black(), 300)
        e2 = Effect.slide_in(Motion.LeftToRight, 0, 0, Color.black(), 400)
        par = Effect.parallel([e1, e2])
        assert par is not None

    def test_repeat(self):
        from pyratatui import Effect, Color
        e = Effect.fade_from_fg(Color.black(), 200)
        r = Effect.repeat(e, 3)
        assert r is not None

    def test_ping_pong(self):
        from pyratatui import Effect, Color
        e = Effect.fade_from_fg(Color.black(), 300)
        pp = Effect.ping_pong(e)
        assert pp is not None

    def test_never_complete(self):
        from pyratatui import Effect, Color
        e = Effect.fade_from_fg(Color.black(), 300)
        nc = Effect.never_complete(e)
        assert nc is not None

    def test_reset(self):
        from pyratatui import Effect, Color
        e = Effect.sleep(100)
        e.reset()   # Should not raise

    def test_with_filter(self):
        from pyratatui import Effect, CellFilter, Color
        e = Effect.coalesce(500)
        e.with_filter(CellFilter.text())   # Should not raise

    def test_repr(self):
        from pyratatui import Effect
        e = Effect.sleep(100)
        assert "Effect" in repr(e)


class TestEffectManager:
    def test_creation(self):
        from pyratatui import EffectManager
        mgr = EffectManager()
        assert mgr is not None
        assert mgr.active_count() == 0
        assert not mgr.has_active()

    def test_add_and_clear(self):
        from pyratatui import EffectManager, Effect, Color
        mgr = EffectManager()
        mgr.add(Effect.fade_from_fg(Color.black(), 1000))
        assert mgr.has_active()
        mgr.clear()
        assert not mgr.has_active()

    def test_add_unique(self):
        from pyratatui import EffectManager, Effect, Color
        mgr = EffectManager()
        mgr.add_unique("header", Effect.fade_from_fg(Color.black(), 1000))
        assert mgr.has_active()
        # Adding another with same key should cancel the first
        mgr.add_unique("header", Effect.dissolve(500))
        assert mgr.has_active()

    def test_repr(self):
        from pyratatui import EffectManager
        assert "EffectManager" in repr(EffectManager())


class TestCompileEffect:
    def test_simple_dissolve(self):
        from pyratatui import compile_effect
        e = compile_effect("fx::dissolve(500)")
        assert e is not None

    def test_coalesce(self):
        from pyratatui import compile_effect
        e = compile_effect("fx::coalesce((400, SineOut))")
        assert e is not None

    def test_fade_from_fg(self):
        from pyratatui import compile_effect
        e = compile_effect("fx::fade_from_fg(Color::Black, (600, QuadOut))")
        assert e is not None

    def test_sequence_dsl(self):
        from pyratatui import compile_effect
        e = compile_effect("""
            fx::sequence(&[
                fx::coalesce(300),
                fx::sleep(100),
                fx::dissolve(400)
            ])
        """)
        assert e is not None

    def test_invalid_dsl_raises(self):
        from pyratatui import compile_effect
        import pytest
        with pytest.raises(Exception):
            compile_effect("not_valid_dsl(!!)")

    def test_repr(self):
        from pyratatui import compile_effect
        e = compile_effect("fx::sleep(50)")
        assert "Effect" in repr(e)
