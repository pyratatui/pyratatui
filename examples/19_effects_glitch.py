"""
examples/19_effects_glitch.py — TachyonFX dissolve / coalesce "glitch" demo.

Demonstrates:
  - Effect.dissolve()  — cells scatter and disappear
  - Effect.coalesce()  — cells materialise from nothing
  - Effect.sequence()  — chain effects one after another
  - EffectManager      — manage multiple active effects
  - SPACE to restart   — reset animation without crashing

Press SPACE to restart, q to quit.
"""

import time

from pyratatui import (
    Block,
    Color,
    Effect,
    EffectManager,
    Interpolation,
    Line,
    Paragraph,
    Span,
    Style,
    Terminal,
    Text,
)

# ── Effect builder ────────────────────────────────────────────────────────────


def make_glitch_effect() -> Effect:
    """Dissolve out → short sleep → coalesce back in."""
    dissolve = Effect.dissolve(600, Interpolation.BounceOut)
    pause = Effect.sleep(200)
    coalesce = Effect.coalesce(700, Interpolation.ElasticOut)
    return Effect.sequence([dissolve, pause, coalesce])


# ── State ─────────────────────────────────────────────────────────────────────

mgr = EffectManager()
last_frame = time.monotonic()
cycle = 0


def restart():
    global cycle
    mgr.clear()
    mgr.add(make_glitch_effect())
    cycle += 1


# Auto-start on launch.
restart()

CONTENT_LINES = [
    Line([Span("  TachyonFX Glitch Demo", Style().fg(Color.green()).bold())]),
    Line([]),
    Line([Span("  dissolve → sleep → coalesce", Style().fg(Color.white()))]),
    Line([]),
    Line([Span("  Effects chain together using", Style().fg(Color.gray()))]),
    Line([Span("  Effect.sequence([...]) so each", Style().fg(Color.gray()))]),
    Line([Span("  transition runs in order.", Style().fg(Color.gray()))]),
    Line([]),
    Line([Span("  Press  SPACE  to restart", Style().fg(Color.cyan()))]),
    Line([Span("  Press    q    to quit", Style().fg(Color.cyan()))]),
]

# ── Main loop ─────────────────────────────────────────────────────────────────

with Terminal() as term:
    term.hide_cursor()

    while True:
        now = time.monotonic()
        elapsed_ms = max(0, int((now - last_frame) * 1000))
        last_frame = now

        _ms = elapsed_ms
        _cycle = cycle

        def ui(frame, _mgr=mgr, _ms=_ms, _c=_cycle):
            area = frame.area

            frame.render_widget(
                Paragraph(Text(CONTENT_LINES)).block(
                    Block()
                    .bordered()
                    .title(f" Glitch Effect  [run #{_c}] ")
                    .style(Style().fg(Color.green()))
                ),
                area,
            )

            frame.apply_effect_manager(_mgr, _ms, area)

        term.draw(ui)

        ev = term.poll_event(timeout_ms=16)
        if ev:
            if ev.code == "q":
                break
            elif ev.code == " ":
                restart()

    term.show_cursor()
