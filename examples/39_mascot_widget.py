"""
examples/39_mascot_widget.py — Ratatui mascot widget (easter egg).

Keys:
  e   toggle eyes (Default/Red)
  q   quit
"""

from __future__ import annotations

from pyratatui import (
    Block,
    Color,
    Constraint,
    Direction,
    Layout,
    MascotEyeColor,
    Paragraph,
    RatatuiMascot,
    Style,
    Terminal,
)


def main() -> None:
    eye = MascotEyeColor.Default

    with Terminal() as term:
        while True:
            mascot = RatatuiMascot(eye)

            def ui(frame, _eye=eye, _mascot=mascot):
                areas = (
                    Layout()
                    .direction(Direction.Vertical)
                    .constraints(
                        [
                            Constraint.fill(1),
                            Constraint.length(13),
                            Constraint.length(3),
                            Constraint.fill(1),
                        ]
                    )
                    .split(frame.area)
                )

                frame.render_widget(Block().bordered().title(" Mascot "), areas[1])
                frame.render_widget(_mascot, areas[1].inner(1, 1))

                frame.render_widget(
                    Paragraph.from_string(
                        f"eye={_eye}  [e] toggle eyes  [q] quit"
                    ).style(Style().fg(Color.dark_gray())),
                    areas[2],
                )

            term.draw(ui)
            ev = term.poll_event(timeout_ms=100)
            if not ev:
                continue
            if ev.code == "q":
                break
            if ev.code == "e":
                eye = (
                    MascotEyeColor.Red
                    if eye == MascotEyeColor.Default
                    else MascotEyeColor.Default
                )


if __name__ == "__main__":
    main()

