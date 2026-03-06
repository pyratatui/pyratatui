"""
examples/21_prompt_confirm.py — Yes/No confirmation prompt demo.

Demonstrates a confirm-style interaction built on top of TextState and
TextPrompt:

  - Accept only y/n/Y/N as valid inputs
  - Enter confirms once a valid choice has been typed
  - Esc or Ctrl+C aborts

Press y or n, then Enter to confirm.  Esc to abort.
"""

from pyratatui import (
    Block,
    Color,
    Constraint,
    Direction,
    Layout,
    Paragraph,
    Style,
    Terminal,
    TextPrompt,
    TextState,
)

# ── State ─────────────────────────────────────────────────────────────────────

answer: bool | None = None

state = TextState()
state.focus()

VALID_CHARS = {"y", "Y", "n", "N"}

# ── Event loop ────────────────────────────────────────────────────────────────

with Terminal() as term:
    term.hide_cursor()

    while state.is_pending():
        _state = state
        _current = state.value()

        def ui(frame, _s=_state, _cur=_current):
            area = frame.area

            # Three-row split: top padding | prompt row (3 tall) | bottom hint
            rows = (
                Layout()
                .direction(Direction.Vertical)
                .constraints(
                    [
                        Constraint.fill(1),
                        Constraint.length(3),
                        Constraint.length(1),
                    ]
                )
                .split(area)
            )

            # ── Colour indicator based on current input ────────────────────
            if _cur in ("y", "Y"):
                choice_color = Color.green()
                choice_label = " YES "
            elif _cur in ("n", "N"):
                choice_color = Color.red()
                choice_label = " NO  "
            else:
                choice_color = Color.gray()
                choice_label = "  —  "

            # ── Draw the outer bordered box over the middle row ────────────
            frame.render_widget(
                Block()
                .bordered()
                .title(" Continue with the operation? ")
                .style(Style().fg(Color.cyan())),
                rows[1],
            )

            # A bordered block removes 1 cell on every edge.
            # Rect.inner(horizontal, vertical) gives the interior area.
            # Block has no .inner() method in the Python bindings —
            # use rows[1].inner(1, 1) instead.
            prompt_area = rows[1].inner(1, 1)

            # ── Split interior: text input left | indicator right ──────────
            inner = (
                Layout()
                .direction(Direction.Horizontal)
                .constraints(
                    [
                        Constraint.fill(1),
                        Constraint.length(7),
                    ]
                )
                .split(prompt_area)
            )

            # Left: readline-style text input
            frame.render_text_prompt(TextPrompt("[y/n]: "), inner[0], _s)

            # Right: live YES / NO label
            frame.render_widget(
                Paragraph.from_string(choice_label).style(
                    Style().fg(choice_color).bold()
                ),
                inner[1],
            )

            # ── Bottom hint bar ────────────────────────────────────────────
            frame.render_widget(
                Paragraph.from_string(
                    " y = YES   n = NO   Enter = confirm   Esc = abort"
                ).style(Style().fg(Color.dark_gray())),
                rows[2],
            )

        term.draw(ui)

        ev = term.poll_event(timeout_ms=50)
        if ev:
            if ev.code == "Esc":
                # Esc → handle_key sets status to Aborted directly
                state.handle_key(ev)

            elif ev.code == "Enter":
                # Confirm only once a valid y/n has been entered
                if state.value() in VALID_CHARS:
                    state.handle_key(ev)  # sets status → Complete

            elif ev.code in VALID_CHARS and not state.value():
                # Accept exactly one valid character; block extras until backspaced
                state.handle_key(ev)

            elif ev.code == "Backspace":
                state.handle_key(ev)

    # ── Capture the result ─────────────────────────────────────────────────
    answer = state.value().lower() == "y" if state.is_complete() else None

    term.show_cursor()

# ── Display outcome ───────────────────────────────────────────────────────────

print()
if answer is None:
    print("  Prompt aborted.")
elif answer:
    print("  Confirmed — proceeding.")
else:
    print("  Cancelled.")
print()
