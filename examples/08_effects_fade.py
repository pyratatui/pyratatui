"""
examples/08_effects_fade.py — TachyonFX fade-in / fade-out effect cycle.

Demonstrates: Effect.fade_from_fg, Effect.fade_to_fg, EffectManager,
              Frame.apply_effect_manager, elapsed-time tracking.

How effects work in pyratatui
------------------------------
tachyonfx effects are *post-render* transforms.  The correct call order is:

  1. ``frame.render_widget(...)``   — write widgets into the frame buffer
  2. ``frame.apply_effect_manager(mgr, elapsed_ms, area)``
                                    — mutate those same buffer cells

Both steps must happen **inside** the ``term.draw(ui)`` callback so they
target the live frame buffer that ratatui will flush to the terminal.

Press SPACE to restart the animation, q to quit.
"""

import time

from pyratatui import (
    Block,
    Color,
    Effect,
    EffectManager,
    Interpolation,
    Paragraph,
    Style,
    Terminal,
)

CYCLE_MS = 2000  # fade duration in ms
HOLD_MS = 400  # hold at full visibility before next transition

mgr = EffectManager()
phase = "in"
phase_start = time.monotonic()
last_frame = time.monotonic()

# Start with the first fade-in effect.
mgr.add(Effect.fade_from_fg(Color.black(), CYCLE_MS, Interpolation.SineOut))


def restart_animation():
    """Reset animation state and re-launch the fade-in effect."""
    global phase, phase_start
    mgr.clear()
    phase = "in"
    phase_start = time.monotonic()
    mgr.add(Effect.fade_from_fg(Color.black(), CYCLE_MS, Interpolation.SineOut))


CONTENT = (
    "TachyonFX Fade Demo\n\n"
    "Watch the text fade in and out using\n"
    "Effect.fade_from_fg / fade_to_fg.\n\n"
    "The effect is applied via\n"
    "frame.apply_effect_manager() after\n"
    "rendering the widget — this mutates\n"
    "the live frame buffer directly.\n\n"
    "Press  SPACE  to restart\n"
    "Press    q    to quit"
)

with Terminal() as term:
    term.hide_cursor()

    while True:
        now = time.monotonic()
        elapsed_ms = max(0, int((now - last_frame) * 1000))
        last_frame = now

        phase_elapsed_ms = int((now - phase_start) * 1000)

        # ── Phase transitions ─────────────────────────────────────────────
        # Switch phase only after the current effects are all done.
        if not mgr.has_active():
            if phase == "in" and phase_elapsed_ms >= HOLD_MS:
                phase = "out"
                phase_start = now
                mgr.add(
                    Effect.fade_to_fg(Color.black(), CYCLE_MS, Interpolation.SineIn)
                )
            elif phase == "out" and phase_elapsed_ms >= HOLD_MS:
                phase = "in"
                phase_start = now
                mgr.add(
                    Effect.fade_from_fg(Color.black(), CYCLE_MS, Interpolation.SineOut)
                )

        # Capture loop-local values for the closure (avoids late-binding bugs).
        _elapsed = elapsed_ms
        _phase = phase

        def ui(frame, _mgr=mgr, _ms=_elapsed, _ph=_phase):
            area = frame.area

            # Step 1 — render widget into the frame buffer.
            frame.render_widget(
                Paragraph.from_string(CONTENT)
                .block(
                    Block()
                    .bordered()
                    .title(f" Effects: Fade  [{_ph}] ")
                    .style(Style().fg(Color.cyan()))
                )
                .style(Style().fg(Color.white())),
                area,
            )

            # Step 2 — apply all active effects to the *same* buffer.
            # This is the critical call: without it the effects never touch
            # the pixels that actually reach the terminal.
            frame.apply_effect_manager(_mgr, _ms, area)

        term.draw(ui)

        ev = term.poll_event(timeout_ms=16)  # ~60 fps ceiling
        if ev:
            if ev.code == "q":
                break
            elif ev.code == " ":
                # SPACE — restart the animation from the beginning.
                restart_animation()
                phase_start = time.monotonic()
                last_frame = time.monotonic()

    term.show_cursor()
