"""
examples/20_effects_matrix.py — TachyonFX sweep-in / sweep-out matrix-style demo.

Demonstrates:
  - Effect.sweep_in()  — a sweeping reveal from one direction
  - Effect.sweep_out() — sweeping disappearance
  - Effect.fade_from() / fade_to()  — full colour cross-fade
  - Effect.parallel()  — run two effects simultaneously
  - Effect.repeat()    — loop an effect N times
  - ping-pong cycling  — chain sweep-in → sweep-out endlessly

Press SPACE to restart, ↑/↓ to change direction, q to quit.
"""

import time

from pyratatui import (
    Block,
    Color,
    Constraint,
    Direction,
    Effect,
    EffectManager,
    Interpolation,
    Layout,
    Line,
    Motion,
    Paragraph,
    Span,
    Style,
    Terminal,
    Text,
)

# ── Directions cycle ──────────────────────────────────────────────────────────

DIRECTIONS: list[tuple[str, Motion]] = [
    ("Left → Right", Motion.LeftToRight),
    ("Right → Left", Motion.RightToLeft),
    ("Top → Bottom", Motion.UpToDown),
    ("Bottom → Top", Motion.DownToUp),
]

dir_index = 0

# ── Effect builder ────────────────────────────────────────────────────────────


def make_sweep_effect(motion: Motion) -> Effect:
    """Sweep in from the chosen direction, hold, then sweep out."""
    sweep_in = Effect.sweep_in(
        motion,
        sweep_span=20,
        gradient_len=5,
        color=Color.black(),
        duration_ms=700,
        interpolation=Interpolation.QuadOut,
    )
    hold = Effect.sleep(400)
    sweep_out = Effect.sweep_out(
        motion,
        sweep_span=20,
        gradient_len=5,
        color=Color.black(),
        duration_ms=700,
        interpolation=Interpolation.QuadIn,
    )
    return Effect.sequence([sweep_in, hold, sweep_out])


# ── State ─────────────────────────────────────────────────────────────────────

mgr = EffectManager()
last_frame = time.monotonic()
run_count = 0


def restart():
    global run_count
    _, motion = DIRECTIONS[dir_index]
    mgr.clear()
    mgr.add(make_sweep_effect(motion))
    run_count += 1


restart()

# ── Main loop ─────────────────────────────────────────────────────────────────

with Terminal() as term:
    term.hide_cursor()

    while True:
        now = time.monotonic()
        elapsed_ms = max(0, int((now - last_frame) * 1000))
        last_frame = now

        dir_label = DIRECTIONS[dir_index][0]
        _ms = elapsed_ms
        _label = dir_label
        _run = run_count

        def ui(frame, _mgr=mgr, _ms=_ms, _lbl=_label, _r=_run, _di=dir_index):
            area = frame.area

            rows = (
                Layout()
                .direction(Direction.Vertical)
                .constraints([Constraint.fill(1), Constraint.length(1)])
                .split(area)
            )

            dir_items: list[Line] = []
            for i, (name, _) in enumerate(DIRECTIONS):
                marker = "▶ " if i == _di else "  "
                color = Color.yellow() if i == _di else Color.white()
                dir_items.append(Line([Span(marker + name, Style().fg(color))]))

            content_lines = [
                Line([Span("  Matrix Sweep Demo", Style().fg(Color.cyan()).bold())]),
                Line([]),
                *dir_items,
                Line([]),
                Line([Span(f"  Run: #{_r}", Style().fg(Color.gray()))]),
                Line([]),
                Line(
                    [
                        Span(
                            "  SPACE: restart   ↑/↓: direction   q: quit",
                            Style().fg(Color.dark_gray()),
                        )
                    ]
                ),
            ]

            frame.render_widget(
                Paragraph(Text(content_lines)).block(
                    Block()
                    .bordered()
                    .title(f" Sweep: {_lbl} ")
                    .style(Style().fg(Color.cyan()))
                ),
                rows[0],
            )

            frame.apply_effect_manager(_mgr, _ms, rows[0])

            frame.render_widget(
                Paragraph.from_string(
                    " ↑/↓: direction   SPACE: restart   q: quit"
                ).style(Style().fg(Color.dark_gray())),
                rows[1],
            )

        term.draw(ui)

        ev = term.poll_event(timeout_ms=16)
        if ev:
            if ev.code == "q":
                break
            elif ev.code == " ":
                restart()
            elif ev.code in ("Up", "k"):
                dir_index = (dir_index - 1) % len(DIRECTIONS)
                restart()
            elif ev.code in ("Down", "j"):
                dir_index = (dir_index + 1) % len(DIRECTIONS)
                restart()

    term.show_cursor()
