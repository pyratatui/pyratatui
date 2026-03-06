"""
examples/async_progress.py — Live async progress bar demo.

Run after installing pyratatui:
    python examples/18_async_progress.py
"""

from __future__ import annotations

import asyncio
import time

from pyratatui import (
    AsyncTerminal,
    Block,
    Color,
    Constraint,
    Direction,
    Gauge,
    Layout,
    Line,
    LineGauge,
    Paragraph,
    Span,
    Style,
    Text,
)


async def main() -> None:
    total_steps = 60
    progress: dict[str, object] = {
        "step": 0,
        "message": "Initialising…",
        "log": [],
    }

    messages = [
        "Connecting to database…",
        "Loading configuration…",
        "Fetching remote data…",
        "Crunching numbers…",
        "Generating report…",
        "Finalising…",
        "Done!",
    ]

    async def worker() -> None:
        for i in range(total_steps + 1):
            await asyncio.sleep(0.08)
            progress["step"] = i
            idx = min(i * len(messages) // (total_steps + 1), len(messages) - 1)
            progress["message"] = messages[idx]
            if i % 10 == 0:
                ts = time.strftime("%H:%M:%S")
                progress["log"].append(f"[{ts}] Step {i}/{total_steps}")  # type: ignore[union-attr]

    async with AsyncTerminal() as term:
        term.hide_cursor()
        worker_task = asyncio.create_task(worker())

        async for ev in term.events(fps=20, stop_on_quit=False):
            step = int(progress["step"])  # type: ignore[arg-type]
            pct = int(step / total_steps * 100)
            msg = str(progress["message"])
            log_lines: list[str] = list(progress["log"])[-6:]  # type: ignore[arg-type]

            def ui(frame, _pct=pct, _msg=msg, _log=log_lines, _step=step):
                area = frame.area
                chunks = (
                    Layout()
                    .direction(Direction.Vertical)
                    .constraints(
                        [
                            Constraint.length(3),  # title
                            Constraint.length(3),  # main gauge
                            Constraint.length(3),  # line gauge
                            Constraint.fill(1),  # log
                            Constraint.length(1),  # footer
                        ]
                    )
                    .split(area)
                )

                # ── Title ───────────────────────────────────────────────
                frame.render_widget(
                    Paragraph(
                        Text(
                            [
                                Line(
                                    [
                                        Span(
                                            "pyratatui ",
                                            Style().fg(Color.cyan()).bold(),
                                        ),
                                        Span(
                                            "Async Progress Demo",
                                            Style().fg(Color.white()),
                                        ),
                                    ]
                                )
                            ]
                        )
                    ).block(Block().bordered()),
                    chunks[0],
                )

                # ── Block gauge ──────────────────────────────────────────
                frame.render_widget(
                    Gauge()
                    .percent(_pct)
                    .label(f"{_msg}  ({_pct}%)")
                    .style(Style().fg(Color.green()))
                    .gauge_style(Style().fg(Color.dark_gray()))
                    .block(Block().bordered().title("Overall Progress")),
                    chunks[1],
                )

                # ── Line gauge ───────────────────────────────────────────
                frame.render_widget(
                    LineGauge()
                    .percent(_pct)
                    .style(Style().fg(Color.blue()))
                    .gauge_style(Style().fg(Color.dark_gray()))
                    .line_set("thick")
                    .label(f"Step {_step}/{total_steps}"),
                    chunks[2],
                )

                # ── Log ─────────────────────────────────────────────────
                log_text = Text.from_string("\n".join(_log) if _log else "(no log yet)")
                frame.render_widget(
                    Paragraph(log_text)
                    .block(Block().bordered().title("Log"))
                    .style(Style().fg(Color.gray())),
                    chunks[3],
                )

                # ── Footer ──────────────────────────────────────────────
                frame.render_widget(
                    Paragraph.from_string(" q: Quit").style(
                        Style().fg(Color.dark_gray())
                    ),
                    chunks[4],
                )

            term.draw(ui)

            if ev and (ev.code == "q" or (ev.code == "c" and ev.ctrl)):
                worker_task.cancel()
                break

            if step >= total_steps:
                await asyncio.sleep(1.5)
                break

        term.show_cursor()


if __name__ == "__main__":
    asyncio.run(main())
