"""
examples/09_effects_dsl.py — TachyonFX DSL effect compilation demo.

Demonstrates: compile_effect(), Effect DSL syntax, EffectManager,
              Frame.apply_effect_manager, frame-local effect state.

The DSL mirrors Rust / tachyonfx syntax and compiles at runtime — ideal for:
  - Config-driven effects
  - Live-reloadable animations
  - User-customisable transitions

Press ↑/↓ to select a DSL demo, Space/Enter to (re-)run it, q to quit.
"""

import time

from pyratatui import (
    Block,
    Color,
    Constraint,
    Direction,
    EffectManager,
    Layout,
    Line,
    Paragraph,
    Span,
    Style,
    Terminal,
    Text,
    compile_effect,
)

# ── DSL demo entries ──────────────────────────────────────────────────────────

DSL_DEMOS = [
    (
        "coalesce 500ms (Linear)",
        "fx::coalesce(500)",
    ),
    (
        "dissolve 800ms (BounceOut)",
        "fx::dissolve((800, BounceOut))",
    ),
    (
        "fade_from_fg black 600ms (QuadOut)",
        "fx::fade_from_fg(Color::Black, (600, QuadOut))",
    ),
    (
        "fade_to_fg black 700ms (SineIn)",
        "fx::fade_to_fg(Color::Black, (700, SineIn))",
    ),
    (
        "sequence: coalesce → sleep → dissolve",
        "fx::sequence(&[fx::coalesce((400, SineOut)), fx::sleep(300), fx::dissolve((500, BounceOut))])",
    ),
    (
        "sweep_in LeftToRight",
        "fx::sweep_in(LeftToRight, 15, 0, Color::Black, (800, QuadOut))",
    ),
]

# ── Pre-compile all DSL effects ───────────────────────────────────────────────

compiled: list[tuple[str, object | None, bool, str]] = []
for label, dsl in DSL_DEMOS:
    try:
        eff = compile_effect(dsl)
        compiled.append((label, eff, True, ""))
    except Exception as exc:
        compiled.append((label, None, False, str(exc)))

# ── State ─────────────────────────────────────────────────────────────────────

index = 0
mgr = EffectManager()
last_frame = time.monotonic()
running = False


def launch(idx: int) -> None:
    """(Re-)launch the selected effect."""
    global running
    mgr.clear()
    label, eff, ok, _ = compiled[idx]
    if ok and eff is not None:
        # compile_effect returns the same Effect object; reset it first.
        eff.reset()
        mgr.add(eff)
        running = True
    else:
        running = False


# Auto-launch the first demo.
launch(index)

PREVIEW_TEXT = (
    "  The quick brown fox\n"
    "  jumps over the lazy dog.\n\n"
    "  0123456789  !@#$%^&*()\n"
    "  ABCDEFGHIJKLMNOPQRSTUVWXYZ"
)

with Terminal() as term:
    term.hide_cursor()

    while True:
        now = time.monotonic()
        elapsed_ms = max(0, int((now - last_frame) * 1000))
        last_frame = now

        _elapsed = elapsed_ms
        _idx = index

        def ui(frame, _mgr=mgr, _ms=_elapsed, _i=_idx):
            area = frame.area
            outer = (
                Layout()
                .direction(Direction.Vertical)
                .constraints([Constraint.fill(1), Constraint.length(1)])
                .split(area)
            )

            body = (
                Layout()
                .direction(Direction.Horizontal)
                .constraints([Constraint.percentage(40), Constraint.fill(1)])
                .split(outer[0])
            )

            # ── Left: effect selector ──────────────────────────────────
            items_lines = []
            for i, (lbl, _, ok, _err) in enumerate(compiled):
                marker = "▶ " if i == _i else "  "
                status = "✓" if ok else "✗"
                color = Color.green() if ok else Color.red()
                sel_col = Color.yellow() if i == _i else Color.white()
                items_lines.append(
                    Line(
                        [
                            Span(marker, Style().fg(Color.cyan())),
                            Span(f"{status} ", Style().fg(color)),
                            Span(
                                lbl,
                                (
                                    Style().fg(sel_col).bold()
                                    if i == _i
                                    else Style().fg(sel_col)
                                ),
                            ),
                        ]
                    )
                )

            frame.render_widget(
                Paragraph(Text(items_lines)).block(
                    Block().bordered().title(" DSL Effects  ↑/↓ select  Space run ")
                ),
                body[0],
            )

            # ── Right: preview + DSL source ───────────────────────────
            label, _, ok, err = compiled[_i]
            _, dsl_src = DSL_DEMOS[_i]
            status_span = (
                Span("✓ compiled", Style().fg(Color.green()))
                if ok
                else Span(f"✗ {err}", Style().fg(Color.red()))
            )

            src_lines = [
                Line([Span(ln, Style().fg(Color.gray()))])
                for ln in dsl_src.strip().splitlines()
            ]

            preview_lines = [
                Line([Span("Preview:", Style().fg(Color.cyan()).bold())]),
                *[
                    Line([Span(ln, Style().fg(Color.white()))])
                    for ln in PREVIEW_TEXT.splitlines()
                ],
                Line([]),
                Line([Span("Status: ", Style().bold()), status_span]),
                Line([]),
                Line([Span("DSL:", Style().fg(Color.cyan()).bold())]),
                *src_lines,
            ]

            # Render the preview text — effects will transform these cells.
            frame.render_widget(
                Paragraph(Text(preview_lines)).block(
                    Block()
                    .bordered()
                    .title(f" Effect {_i + 1}/{len(compiled)}: {label} ")
                ),
                body[1],
            )

            # Apply effects to the right panel only.
            frame.apply_effect_manager(_mgr, _ms, body[1])

            frame.render_widget(
                Paragraph.from_string(
                    " ↑/↓: select   Space/Enter: run   q: quit"
                ).style(Style().fg(Color.dark_gray())),
                outer[1],
            )

        term.draw(ui)

        ev = term.poll_event(timeout_ms=16)
        if ev:
            if ev.code == "q":
                break
            elif ev.code in ("Down", "j"):
                index = (index + 1) % len(compiled)
                launch(index)
            elif ev.code in ("Up", "k"):
                index = (index - 1) % len(compiled)
                launch(index)
            elif ev.code in (" ", "Enter"):
                launch(index)

    term.show_cursor()
