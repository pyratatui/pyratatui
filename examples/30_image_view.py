#!/usr/bin/env python3
"""
30_image_view.py — ratatui-image: display an image in the terminal

Loads an image file (PNG/JPEG) and displays it using unicode halfblocks.

Usage:
    python 30_image_view.py [image_path]

Default image:
    gallery/pyratatui.png

Press 'q' to quit.
"""

from __future__ import annotations

import os
import sys

from pyratatui import (
    Block,
    Color,
    Constraint,
    Direction,
    ImagePicker,
    ImageWidget,
    Layout,
    Paragraph,
    Style,
    Terminal,
)


def main():
    # Determine image path
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
    else:
        image_path = "gallery/alacritty.png"

    if not os.path.exists(image_path):
        print(f"Error: file {image_path!r} not found", file=sys.stderr)
        sys.exit(1)

    picker = ImagePicker.halfblocks()

    try:
        state = picker.load(image_path)
    except OSError as e:
        print(f"Failed to load image: {e}", file=sys.stderr)
        sys.exit(1)

    widget = ImageWidget()

    with Terminal() as term:
        while True:

            def ui(frame, _w=widget, _s=state, _path=image_path):
                area = frame.area

                chunks = (
                    Layout()
                    .direction(Direction.Vertical)
                    .constraints([Constraint.length(1), Constraint.fill(1)])
                    .split(area)
                )

                frame.render_widget(
                    Paragraph.from_string(
                        f"  Image Viewer: {os.path.basename(_path)}  (q = quit)"
                    ).style(Style().fg(Color.cyan())),
                    chunks[0],
                )

                inner_block = Block().bordered()
                frame.render_widget(inner_block, chunks[1])

                inner = chunks[1]

                img_area = type(inner)(
                    inner.x + 1,
                    inner.y + 1,
                    inner.width - 2,
                    inner.height - 2,
                )

                frame.render_stateful_image(_w, img_area, _s)

            term.draw(ui)

            ev = term.poll_event(timeout_ms=50)
            if ev and (ev.code == "q" or (ev.code == "c" and ev.ctrl)):
                break


if __name__ == "__main__":
    main()
