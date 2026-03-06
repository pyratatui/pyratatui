#!/usr/bin/env python3
"""
Example 17 — QrCodeWidget
==========================
Renders a scannable QR code in the terminal using the official `tui-qrcode`
crate.  tui-qrcode uses Unicode half-block characters for crisp output that
most phone cameras can read directly from the screen.

Controls:
  n           Next URL
  p           Previous URL
  i           Toggle Default / Inverted colors
  q / Esc     Quit

Run:
    python examples/17_qrcode.py
"""

from pyratatui import (
    Block,
    Color,
    Constraint,
    Direction,
    Layout,
    Paragraph,
    QrCodeWidget,
    QrColors,
    Style,
    Terminal,
)

URLS = [
    "https://ratatui.rs",
    "https://pyo3.rs",
    "https://github.com/pyratatui/pyratatui",
    "https://crates.io/crates/ratatui",
]


def main() -> None:
    url_idx = 0
    color_scheme = QrColors.Inverted

    with Terminal() as term:
        term.hide_cursor()
        running = True

        while running:
            url = URLS[url_idx % len(URLS)]
            scheme_name = "Inverted" if color_scheme == QrColors.Inverted else "Default"

            # Build the QR widget for this frame.
            qr = QrCodeWidget(url).colors(color_scheme)

            # Capture loop-local values to avoid late-binding inside the closure.
            _qr = qr
            _url = url
            _scheme = scheme_name

            def ui(frame, qr=_qr, url=_url, scheme=_scheme) -> None:  # noqa: E731
                # Split horizontally: QR on the left, info panel on the right.
                chunks = (
                    Layout()
                    .direction(Direction.Horizontal)
                    .constraints([Constraint.length(50), Constraint.min(0)])
                    .split(frame.area)
                )

                # ── QR code pane ─────────────────────────────────────────────
                # Block.inner() gives the area inside the borders for content.
                qr_block = Block().bordered().title(f" QR Code ({scheme}) ")
                qr_inner = qr_block.inner(chunks[0])
                frame.render_widget(qr_block, chunks[0])
                frame.render_qrcode(qr, qr_inner)

                # ── Info pane ─────────────────────────────────────────────────
                help_lines = [
                    "",
                    "  Scan this QR code with",
                    "  your phone camera!",
                    "",
                    "  URL:",
                    f"  {url}",
                    "",
                    "  " + "-" * 29,
                    "  Controls:",
                    "  n         Next URL",
                    "  p         Previous URL",
                    "  i         Toggle colors",
                    "  q / Esc   Quit",
                    "",
                    f"  Colors: {scheme}",
                    "",
                    "  Powered by tui-qrcode",
                ]
                info = (
                    Paragraph.from_string("\n".join(help_lines))
                    .block(Block().bordered().title(" Info "))
                    .style(Style().fg(Color.white()))
                )
                frame.render_widget(info, chunks[1])

            term.draw(ui)

            # ── Input handling ────────────────────────────────────────────────
            ev = term.poll_event(timeout_ms=200)
            if ev is None:
                continue
            if ev.code in ("q", "Esc"):
                running = False
            elif ev.code == "i":
                color_scheme = (
                    QrColors.Default
                    if color_scheme == QrColors.Inverted
                    else QrColors.Inverted
                )
            elif ev.code == "n":
                url_idx += 1
            elif ev.code == "p":
                url_idx = max(0, url_idx - 1)

        term.show_cursor()


if __name__ == "__main__":
    main()
