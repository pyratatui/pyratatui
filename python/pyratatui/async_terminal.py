"""
async_terminal.py — AsyncTerminal: asyncio-friendly wrapper around Terminal.

Threading model
---------------
``Terminal`` (and ``Frame``, ``Effect``, ``EffectManager``) are PyO3
``unsendable`` objects.  PyO3 records the OS thread ID at construction time
and **panics** if any method is called from a different thread::

    pyo3_runtime.PanicException: assertion `left == right` failed:
    pyratatui::terminal::Terminal is unsendable, but sent to another thread

Python's default asyncio event-loop runs entirely on **one thread** (the
thread that called ``asyncio.run()``).  As long as we never use
``loop.run_in_executor`` (or ``asyncio.to_thread``) with Terminal methods,
we are safe.

The previous implementation used ``run_in_executor`` to avoid blocking the
event loop during ``poll_event``.  The fix is dead simple:

* Use **non-blocking** ``poll_event(timeout_ms=0)`` on the main thread.
* Use ``await asyncio.sleep(frame_interval)`` to yield to the event loop
  between frames — this lets background tasks (metric updates, timers, …)
  run without ever touching Terminal from another thread.
"""

from __future__ import annotations

import asyncio
import contextlib
import time
from collections.abc import AsyncIterator, Callable

from ._pyratatui import Frame
from ._pyratatui import PyKeyEvent as KeyEvent
from ._pyratatui import Terminal


class AsyncTerminal:
    """
    Asyncio-compatible terminal driver.

    All calls to ``Terminal`` happen on the **asyncio event-loop thread**.
    ``run_in_executor`` is intentionally absent — it would send Terminal to
    a thread-pool thread and trigger PyO3's unsendable panic.

    ```python
    async with AsyncTerminal() as term:
        async for event in term.events(fps=30):
            term.draw(lambda f: f.render_widget(..., f.area))
            if event and event.code == "q":
                break
    ```
    """

    def __init__(self) -> None:
        self._term: Terminal | None = None

    # ── Context manager ──────────────────────────────────────────────────────

    async def __aenter__(self) -> AsyncTerminal:
        self._term = Terminal()
        self._term.__enter__()
        return self

    async def __aexit__(self, *args: object) -> bool:
        if self._term is not None:
            with contextlib.suppress(Exception):
                self._term.restore()
            self._term = None
        return False

    # ── Drawing ──────────────────────────────────────────────────────────────

    def draw(self, draw_fn: Callable[[Frame], None]) -> None:
        """Render one frame on the main event-loop thread."""
        if self._term is None:
            raise RuntimeError("AsyncTerminal is not active — use `async with`")
        self._term.draw(draw_fn)

    # ── Events ───────────────────────────────────────────────────────────────

    async def poll_event(self, timeout_ms: int = 0) -> KeyEvent | None:
        """
        Poll for a keyboard event without leaving the main thread.

        Yields to the event loop via ``await asyncio.sleep(0)`` then does a
        non-blocking poll.  The ``timeout_ms`` arg is kept for API compat but
        frame pacing is handled by ``events()``.
        """
        if self._term is None:
            raise RuntimeError("AsyncTerminal is not active")
        # Yield control so other coroutines run, then poll on the same thread.
        # NEVER use run_in_executor here — that sends Terminal to another thread.
        await asyncio.sleep(0)
        return self._term.poll_event(0)

    async def events(
        self,
        fps: float = 30.0,
        *,
        stop_on_quit: bool = True,
    ) -> AsyncIterator[KeyEvent | None]:
        """
        Async generator yielding one tick per frame at the requested rate.

        Each tick:
          1. Non-blocking event poll on the main thread.
          2. Yield the event (or ``None``).
          3. Sleep the remainder of the frame interval — gives background
             coroutines CPU time without touching Terminal from another thread.

        Args:
            fps:           Target frames per second.
            stop_on_quit:  Auto-stop on ``q`` or Ctrl-C.
        """
        if self._term is None:
            raise RuntimeError("AsyncTerminal is not active")

        frame_interval = 1.0 / max(1.0, fps)

        while True:
            t_start = time.monotonic()

            # Non-blocking poll — always on the main event-loop thread.
            ev = self._term.poll_event(0)

            if (
                stop_on_quit
                and ev is not None
                and (ev.code == "q" or (ev.code == "c" and ev.ctrl))
            ):
                return

            yield ev

            # Sleep for the rest of the frame interval.
            elapsed = time.monotonic() - t_start
            sleep_s = max(0.0, frame_interval - elapsed)
            await asyncio.sleep(sleep_s if sleep_s > 0 else 0)

    # ── Utilities ────────────────────────────────────────────────────────────

    def area(self) -> object:
        if self._term is None:
            raise RuntimeError("AsyncTerminal is not active")
        return self._term.area()

    def clear(self) -> None:
        if self._term is None:
            raise RuntimeError("AsyncTerminal is not active")
        self._term.clear()

    def hide_cursor(self) -> None:
        if self._term is None:
            raise RuntimeError("AsyncTerminal is not active")
        self._term.hide_cursor()

    def show_cursor(self) -> None:
        if self._term is None:
            raise RuntimeError("AsyncTerminal is not active")
        self._term.show_cursor()

    def __repr__(self) -> str:
        return f"AsyncTerminal(active={self._term is not None})"
