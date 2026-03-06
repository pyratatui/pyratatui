"""
helpers.py — High-level convenience helpers for common TUI patterns.

These allow a dead-simple entry point similar to ratatui's `ratatui::run()`.
"""

from __future__ import annotations

from collections.abc import Callable

from ._pyratatui import Frame, Terminal
from .async_terminal import AsyncTerminal


def run_app(
    ui_fn: Callable[[Frame], None],
    *,
    fps: float = 30.0,
    on_key: Callable[[object], bool] | None = None,
) -> None:
    """
    Run a simple synchronous TUI application.

    Args:
        ui_fn:  A callable that receives `Frame` and renders the UI each tick.
        fps:    Target frames per second.
        on_key: Optional callback receiving a `KeyEvent`. Return `True` to quit.
                If not supplied, pressing 'q' or Ctrl-C exits automatically.

    Example::

        from pyratatui import run_app, Paragraph, Text

        def ui(frame):
            frame.render_widget(
                Paragraph.from_string("Hello! Press q to quit."),
                frame.area
            )

        run_app(ui)
    """
    timeout_ms = max(1, int(1000 / fps))
    with Terminal() as term:
        while True:
            term.draw(ui_fn)
            ev = term.poll_event(timeout_ms=timeout_ms)
            if ev is not None:
                if on_key is not None:
                    if on_key(ev):
                        break
                else:
                    # Default: quit on 'q' or Ctrl-C.
                    if ev.code == "q" or (ev.code == "c" and ev.ctrl):
                        break


async def run_app_async(
    ui_fn: Callable[[Frame], None],
    *,
    fps: float = 30.0,
    on_key: Callable[[object], bool] | None = None,
) -> None:
    """
    Run a simple async TUI application.

    Args:
        ui_fn:  A callable that receives `Frame` and renders the UI each tick.
        fps:    Target frames per second.
        on_key: Optional callback receiving a `KeyEvent`. Return `True` to quit.

    Example::

        import asyncio
        from pyratatui import run_app_async, Paragraph

        async def main():
            tick = 0
            def ui(frame):
                frame.render_widget(
                    Paragraph.from_string(f"Async tick: {tick}"),
                    frame.area
                )

            async def on_key_handler(ev):
                return ev.code == "q"

            await run_app_async(ui, on_key=lambda ev: ev.code == "q")

        asyncio.run(main())
    """
    async with AsyncTerminal() as term:
        async for ev in term.events(fps=fps, stop_on_quit=False):
            term.draw(ui_fn)
            if ev is not None:
                if on_key is not None:
                    if on_key(ev):
                        break
                else:
                    if ev.code == "q" or (ev.code == "c" and ev.ctrl):
                        break
