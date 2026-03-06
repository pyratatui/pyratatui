#!/usr/bin/env python3
"""
Example 21 — TextArea Advanced (Modal Vim-style editing)
=========================================================
Demonstrates custom key mapping with two modes:
  NORMAL mode  — navigation (hjkl, w, b, ^, $, u, r)
  INSERT mode  — Emacs-default editing

Controls:
  NORMAL mode:
    h/j/k/l     ←/↓/↑/→
    w           Word forward
    b           Word back
    ^           Head of line
    $           End of line
    i           Enter INSERT mode
    a           Enter INSERT mode after cursor
    D           Delete to end of line
    p           Paste
    u           Undo
    Ctrl+R      Redo
    q           Quit

  INSERT mode:
    Esc         Back to NORMAL mode
    All other keys use default Emacs bindings

Run:
    python examples/15_textarea_advanced.py
"""

from pyratatui import (
    Block,
    Color,
    Constraint,
    CursorMove,
    Direction,
    Layout,
    Paragraph,
    Style,
    Terminal,
    TextArea,
)

INITIAL_TEXT = [
    "The quick brown fox jumps over the lazy dog.",
    "Press 'i' to enter INSERT mode.",
    "Press 'Esc' to return to NORMAL mode.",
    "Press 'q' in NORMAL mode to quit.",
    "",
    "Vim-like navigation:",
    "  h j k l  ←↓↑→",
    "  w         word forward",
    "  b         word backward",
    "  ^ $        head / end of line",
]


def mode_style(mode: str) -> Style:
    if mode == "NORMAL":
        return Style().fg(Color.white()).bg(Color.blue())
    return Style().fg(Color.black()).bg(Color.green())


def main() -> None:
    ta = TextArea.from_lines(INITIAL_TEXT)
    mode = "NORMAL"

    def update_ui_for_mode():
        nonlocal mode
        block = Block().bordered().title(f" Modal Editor — {mode} mode  (q to quit) ")
        ta.set_block(block)
        if mode == "NORMAL":
            ta.set_cursor_style(Style().fg(Color.white()).bg(Color.blue()))
            ta.set_cursor_line_style(Style().bg(Color.dark_gray()))
        else:
            ta.set_cursor_style(Style().fg(Color.black()).bg(Color.green()))
            ta.set_cursor_line_style(Style())

    update_ui_for_mode()

    with Terminal() as term:
        running = True
        while running:

            def ui(frame, _ta=ta, _mode=mode):
                # Split: editor takes most, status line at bottom
                chunks = (
                    Layout()
                    .direction(Direction.Vertical)
                    .constraints([Constraint.min(0), Constraint.length(1)])
                    .split(frame.area)
                )
                frame.render_textarea(_ta, chunks[0])
                status = Paragraph.from_string(
                    f"  -- {_mode} --  │  Lines: {_ta.len()}  │  "
                    f"Cursor: {_ta.cursor()}  │  Esc=normal, i=insert, q=quit"
                ).style(mode_style(_mode))
                frame.render_widget(status, chunks[1])

            term.draw(ui)
            ev = term.poll_event(timeout_ms=50)
            if ev is None:
                continue

            if mode == "NORMAL":
                if ev.code == "q":
                    running = False
                elif ev.code == "i":
                    mode = "INSERT"
                    update_ui_for_mode()
                elif ev.code == "a":
                    ta.move_cursor(CursorMove.Forward)
                    mode = "INSERT"
                    update_ui_for_mode()
                elif ev.code == "h":
                    ta.move_cursor(CursorMove.Back)
                elif ev.code == "j":
                    ta.move_cursor(CursorMove.Down)
                elif ev.code == "k":
                    ta.move_cursor(CursorMove.Up)
                elif ev.code == "l":
                    ta.move_cursor(CursorMove.Forward)
                elif ev.code == "w":
                    ta.move_cursor(CursorMove.WordForward)
                elif ev.code == "b":
                    ta.move_cursor(CursorMove.WordBack)
                elif ev.code == "^":
                    ta.move_cursor(CursorMove.Head)
                elif ev.code == "$":
                    ta.move_cursor(CursorMove.End)
                elif ev.code == "D":
                    ta.delete_line_by_end()
                elif ev.code == "p":
                    ta.paste()
                elif ev.code == "u" and not ev.ctrl:
                    ta.undo()
                elif ev.code == "r" and ev.ctrl:
                    ta.redo()
                elif ev.code == "g":
                    ta.move_cursor(CursorMove.Top)
                elif ev.code == "G":
                    ta.move_cursor(CursorMove.Bottom)
            else:  # INSERT mode
                if ev.code == "Esc":
                    mode = "NORMAL"
                    update_ui_for_mode()
                else:
                    ta.input_key(ev.code, ev.ctrl, ev.alt, ev.shift)


if __name__ == "__main__":
    main()
