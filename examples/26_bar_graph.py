#!/usr/bin/env python3
"""
26_bar_graph.py — tui-bar-graph: gradient bar graph widget

Displays a colorful animated bar graph showing daily temperature readings.
Press 'q' or Ctrl-C to exit.  Press '+'/'-' to cycle gradient presets.
"""

from __future__ import annotations

import random

from pyratatui import (
    BarColorMode,
    BarGraph,
    BarGraphStyle,
    Block,
    Color,
    Constraint,
    Direction,
    Layout,
    Paragraph,
    Rect,
    Style,
    Terminal,
)

GRADIENTS = ["turbo", "viridis", "plasma", "rainbow", "sinebow", "inferno"]
DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


class App:
    def __init__(self):
        self.temps = [random.uniform(0.3, 0.9) for _ in range(7)]
        self.gradient_idx = 0
        self.style = BarGraphStyle.Braille
        self.color_mode = BarColorMode.VerticalGradient

    @property
    def gradient(self) -> str:
        return GRADIENTS[self.gradient_idx % len(GRADIENTS)]

    def tick(self):
        # Animate temperatures slightly each frame
        self.temps = [
            max(0.05, min(0.99, t + random.uniform(-0.03, 0.03))) for t in self.temps
        ]

    def ui(self, frame):
        area = frame.area
        chunks = (
            Layout()
            .direction(Direction.Vertical)
            .constraints(
                [Constraint.length(3), Constraint.fill(1), Constraint.length(2)]
            )
            .split(area)
        )

        # Title
        title = (
            Paragraph.from_string(
                f"  Bar Graph Demo — gradient: {self.gradient}  (+/- = change gradient, q = quit)"
            )
            .block(Block().bordered())
            .style(Style().fg(Color.cyan()))
        )
        frame.render_widget(title, chunks[0])

        # Bar graph
        bg = (
            BarGraph(self.temps)
            .gradient(self.gradient)
            .bar_style(self.style)
            .color_mode(self.color_mode)
        )
        # Wrap in a block
        frame.render_widget(
            Block().bordered().title(" Weekly Temperatures "), chunks[1]
        )
        inner = Rect(
            chunks[1].x + 1,
            chunks[1].y + 1,
            chunks[1].width - 2,
            chunks[1].height - 2,
        )
        frame.render_widget(bg, inner)

        # Day labels
        day_labels = "  ".join(
            f"{d}: {int(t * 40):2d}°C" for d, t in zip(DAYS, self.temps, strict=False)
        )
        frame.render_widget(
            Paragraph.from_string(day_labels).style(Style().fg(Color.white())),
            chunks[2],
        )


def main():
    app = App()
    with Terminal() as term:
        while True:
            app.tick()
            term.draw(app.ui)
            ev = term.poll_event(timeout_ms=100)
            if ev:
                if ev.code == "q" or (ev.code == "c" and ev.ctrl):
                    break
                elif ev.code == "+":
                    app.gradient_idx += 1
                elif ev.code == "-":
                    app.gradient_idx -= 1


if __name__ == "__main__":
    main()
