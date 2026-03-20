"""
helpers.py — High-level convenience helpers for common TUI patterns.

Exports
-------
Pure-Python helpers
  run_app          — synchronous application loop
  run_app_async    — async application loop

Re-exports from the native _pyratatui extension
  compile_effect   — compile a tachyonfx DSL string into an Effect
  prompt_text      — blocking single-line text prompt
  prompt_password  — blocking password prompt (input masked as *)

These three names live in the Rust extension module but __init__.py
imports them from here, so we re-export them to satisfy that contract.
"""

from __future__ import annotations

from collections.abc import Callable

# Re-export Rust functions that __init__.py expects to find in this module.
from ._pyratatui import compile_effect  # noqa: F401  (tachyonfx DSL compiler)
from ._pyratatui import prompt_password  # noqa: F401  (blocking password prompt)
from ._pyratatui import prompt_text  # noqa: F401  (blocking text prompt)
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
        ui_fn:  A callable that receives ``Frame`` and renders the UI each tick.
        fps:    Target frames per second.
        on_key: Optional callback receiving a ``KeyEvent``. Return ``True`` to
                quit. ``run_app`` no longer handles ``q`` or Ctrl-C for you;
                implement the desired quit logic in ``on_key``.

    Example::

        from pyratatui import run_app, Paragraph

        def ui(frame):
            frame.render_widget(
                Paragraph.from_string("Hello! Press q to quit."),
                frame.area,
            )

        run_app(ui, on_key=lambda ev: ev.code == "q")
    """
    timeout_ms = max(1, int(1000 / fps))
    with Terminal() as term:
        while True:
            term.draw(ui_fn)
            ev = term.poll_event(timeout_ms=timeout_ms)
            if ev is not None and on_key is not None and on_key(ev):
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
        ui_fn:  A callable that receives ``Frame`` and renders the UI each tick.
        fps:    Target frames per second.
        on_key: Optional callback receiving a ``KeyEvent``. Return ``True`` to
                quit. Provide ``on_key`` to explicitly handle quitting; ``run_app_async``
                no longer exits automatically when ``q`` or Ctrl-C are pressed.

    Example::

        import asyncio
        from pyratatui import run_app_async, Paragraph

        async def main():
            tick = 0
            def ui(frame):
                frame.render_widget(
                    Paragraph.from_string(f"Async tick: {tick}"),
                    frame.area,
                )

            await run_app_async(ui, on_key=lambda ev: ev.code == "q")

        asyncio.run(main())
    """
    async with AsyncTerminal() as term:
        async for ev in term.events(fps=fps, stop_on_quit=False):
            term.draw(ui_fn)
            if ev is not None and on_key is not None and on_key(ev):
                break
