#!/usr/bin/env python3
"""
Example 20 — TextArea Basic
============================
A minimal single-file text editor using pyratatui's TextArea widget.

Features:
  - Multi-line editing with Emacs-style keys
  - Line numbers, cursor line highlighting
  - Ctrl+Z undo / Ctrl+Y redo
  - Ctrl+S to print text to stdout and exit

Key bindings (built-in defaults):
  Arrow keys    Move cursor
  Ctrl+F/B      Forward / back one char
  Ctrl+P/N      Up / down one line
  Ctrl+A/E      Beginning / end of line
  Ctrl+K        Kill to end of line
  Ctrl+H        Backspace
  Ctrl+Z        Undo
  Ctrl+Y        Paste last killed text
  Ctrl+S        Save (print to stdout) and exit
  Esc           Exit without saving

Run:
    python examples/14_textarea_basic.py
"""

from pyratatui import Block, Color, Style, Terminal, TextArea

INITIAL_TEXT = [
    "Welcome to pyratatui TextArea! 🐀",
    "",
    "This is a fully functional multi-line editor.",
    "Try Emacs key bindings:",
    "  Ctrl+F/B  →  Forward / Back",
    "  Ctrl+P/N  →  Up / Down",
    "  Ctrl+A/E  →  Head / End of line",
    "  Ctrl+K    →  Kill to end of line",
    "  Ctrl+Z    →  Undo",
    "  Ctrl+Y    →  Paste (yank)",
    "",
    "Press Ctrl+S to save (print to stdout).",
    "Press Esc to quit without saving.",
]


def main() -> None:
    ta = TextArea.from_lines(INITIAL_TEXT)

    # Style the editor
    ta.set_block(Block().bordered().title(" Editor — Ctrl+S save, Esc quit "))
    ta.set_cursor_style(Style().fg(Color.black()).bg(Color.white()))
    ta.set_cursor_line_style(Style().bg(Color.dark_gray()))
    ta.set_line_number_style(Style().fg(Color.dark_gray()))

    saved_text = None  # store text to print after terminal exits

    with Terminal() as term:
        running = True
        while running:

            def ui(frame, _ta=ta):
                frame.render_textarea(_ta, frame.area)

            term.draw(ui)

            ev = term.poll_event(timeout_ms=50)
            if ev is None:
                continue

            if ev.code == "Esc":
                running = False
            elif ev.ctrl and ev.code == "s":
                running = False
                saved_text = "\n".join(ta.lines())
            else:
                ta.input_key(ev.code, ev.ctrl, ev.alt, ev.shift)

    # Now terminal is restored — safe to print to stdout
    if saved_text is not None:
        print("\n--- Saved content: ---")
        print(saved_text)


if __name__ == "__main__":
    main()
