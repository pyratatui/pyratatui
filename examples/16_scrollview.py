#!/usr/bin/env python3
"""
Example 16 — ScrollView
========================
Demonstrates a large scrollable content area using pyratatui's ScrollView.

Controls:
  ↑ / ↓        Scroll by 1 line
  Page Up/Dn   Scroll by 10 lines
  Home         Jump to top
  End          Jump to bottom
  ← / →        Scroll left/right
  q / Esc      Quit

Run:
    python examples/16_scrollview.py
"""

from pyratatui import Block, ScrollView, ScrollViewState, Terminal

# ── Content ───────────────────────────────────────────────────────────────────

CONTENT_WIDTH = 100

SECTIONS = [
    (
        "Introduction",
        [
            "Welcome to the ScrollView demo!",
            "This widget lets you scroll through content larger than the screen.",
            "The scroll area is backed by tui-scrollview from the tui-widgets suite.",
            "",
            "You can put any number of text paragraphs into a scroll view.",
            "Each section occupies a region of the virtual canvas.",
        ],
    ),
    (
        "Lorem Ipsum",
        [
            "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
            "Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
            "Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris.",
            "Duis aute irure dolor in reprehenderit in voluptate velit esse.",
            "Excepteur sint occaecat cupidatat non proident, sunt in culpa.",
            "Officia deserunt mollit anim id est laborum.",
        ],
    ),
    (
        "Data Table",
        [
            f"  Row {i:03d}:  "
            + " | ".join([f"col{j}={i * j:5d}" for j in range(1, 7)])
            for i in range(1, 31)
        ],
    ),
    (
        "More Content",
        [
            "This section demonstrates that you can have many sections.",
            "Each section is positioned at a specific y-offset within the canvas.",
            "The tui-scrollview crate handles all the clipping and scrolling logic.",
            "",
            "Use Home/End to jump quickly between the top and bottom.",
            "Use Page Up/Down for faster scrolling.",
        ],
    ),
]


def build_lines() -> list[str]:
    """Flatten all sections into a single list of lines with headers."""
    result: list[str] = []
    for title, body in SECTIONS:
        result.append("=" * CONTENT_WIDTH)
        result.append(f"  {title.upper()}")
        result.append("=" * CONTENT_WIDTH)
        for line in body:
            result.append(f"  {line}")
        result.append("")
    return result


# ── Main ──────────────────────────────────────────────────────────────────────


def main() -> None:
    lines = build_lines()
    state = ScrollViewState()

    with Terminal() as term:
        term.hide_cursor()
        running = True

        while running:
            # Snapshot scroll offset and content size for title string.
            offset = state.offset()  # returns (x, y)
            sv = ScrollView.from_lines(lines, content_width=CONTENT_WIDTH)
            total = sv.content_height
            title = (
                f" ScrollView Demo  "
                f"line {offset[1] + 1}/{total}  "
                f"[↑/↓ scroll · Home/End jump · q quit] "
            )

            # ── Capture-by-value to avoid late-binding bugs ──────────────────
            _sv = sv
            _st = state
            _t = title

            def ui(frame, sv=_sv, st=_st, t=_t) -> None:  # noqa: E731
                # Block.inner() computes the Rect inside the borders.
                outer = Block().bordered().title(t)
                inner = outer.inner(frame.area)
                frame.render_widget(outer, frame.area)
                frame.render_stateful_scrollview(sv, inner, st)

            term.draw(ui)

            # ── Input handling ───────────────────────────────────────────────
            ev = term.poll_event(timeout_ms=50)
            if ev is None:
                continue
            code = ev.code
            if code in ("q", "Esc"):
                running = False
            elif code == "Down":
                state.scroll_down(1)
            elif code == "Up":
                state.scroll_up(1)
            elif code == "PageDown":
                state.scroll_down(10)
            elif code == "PageUp":
                state.scroll_up(10)
            elif code == "Home":
                state.scroll_to_top()
            elif code == "End":
                state.scroll_to_bottom()
            elif code == "Right":
                state.scroll_right(4)
            elif code == "Left":
                state.scroll_left(4)

        term.show_cursor()


if __name__ == "__main__":
    main()
