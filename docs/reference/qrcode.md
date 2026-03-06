# QrCodeWidget

`QrCodeWidget` renders a scannable QR code directly in the terminal using
Unicode half-block characters (`▀` `▄` `█` `space`). QR codes are encoded
natively with the `qrcode` crate and painted directly into the ratatui frame
buffer — no external process, no image renderer, no font required.

> **Implementation note:** pyratatui uses native Unicode half-block rendering
> rather than `tui-qrcode`, which depends on a pre-release ratatui API
> incompatible with ratatui 0.30. The result is identical quality, fully
> compatible, and has zero extra dependencies.

---

## Overview

| Class | Purpose |
|---|---|
| `QrCodeWidget` | The QR code renderer widget |
| `QrColors` | Color scheme (Default vs Inverted) |

---

## Quick Start

```python
from pyratatui import QrCodeWidget, QrColors, Block, Terminal

qr = QrCodeWidget("https://ratatui.rs").colors(QrColors.Inverted)

with Terminal() as term:
    while True:
        def ui(frame):
            block = Block().bordered().title(" QR Code ")
            inner = block.inner(frame.area)  # compute inner area
            frame.render_widget(block, frame.area)
            frame.render_qrcode(qr, inner)
        term.draw(ui)
        ev = term.poll_event(timeout_ms=30_000)
        if ev and ev.code == "q":
            break
```

---

## `QrCodeWidget`

### Constructor

```python
qr = QrCodeWidget(data: str)
```

Raises `ValueError` if the data cannot be encoded (e.g. string too long for QR).

### Builder methods

```python
qr = (QrCodeWidget("https://example.com")
      .colors(QrColors.Inverted)
      .quiet_zone(2))   # quiet zone width in modules (spec recommends ≥4)
```

### Rendering

```python
frame.render_qrcode(qr, area)
```

Pass the frame and a `Rect`. Use `Block.inner(area)` to get the inner area
when wrapping the QR code in a bordered block.

---

## `QrColors`

| Value | Description |
|---|---|
| `QrColors.Default` | Dark modules on light background (standard) |
| `QrColors.Inverted` | Light modules on dark background — best for dark terminals |

---

## How it works

Each terminal cell represents two QR modules using Unicode half-block characters:

| top module | bottom module | character |
|---|---|---|
| dark | dark | `█` (U+2588 FULL BLOCK) |
| dark | light | `▀` (U+2580 UPPER HALF) |
| light | dark | `▄` (U+2584 LOWER HALF) |
| light | light | ` ` (SPACE) |

This halves the vertical space cost — one QR code row per two terminal rows.

---

## Tips

- Make the area at least 30×30 cells for reliable scanning.
- Use `QrColors.Inverted` on dark-background terminals for best scan results.
- The quiet zone (white border around the QR code) is required for scanning.
  Use `.quiet_zone(4)` for the spec-recommended minimum.
- If the area is too small to fit the QR code, nothing is rendered (no panic).

---

## Complete Example

See [examples/17_qrcode.py](../../examples/17_qrcode.py).

```python
from pyratatui import (
    Block, Color, Constraint, Direction,
    Layout, Paragraph, QrCodeWidget, QrColors, Style, Terminal,
)

URLS = ["https://ratatui.rs", "https://pyo3.rs"]
url_idx = 0
color_scheme = QrColors.Inverted

with Terminal() as term:
    while True:
        url = URLS[url_idx % len(URLS)]
        qr = QrCodeWidget(url).colors(color_scheme)

        def ui(frame, _qr=qr, _url=url):
            chunks = (
                Layout()
                .direction(Direction.Horizontal)
                .constraints([Constraint.length(50), Constraint.min(0)])
                .split(frame.area)
            )
            qr_block = Block().bordered().title(" QR Code ")
            qr_inner = qr_block.inner(chunks[0])
            frame.render_widget(qr_block, chunks[0])
            frame.render_qrcode(_qr, qr_inner)

            help = Paragraph.from_string(f"\n  URL: {_url}\n\n  n=next  i=invert  q=quit")
            frame.render_widget(help.block(Block().bordered()), chunks[1])

        term.draw(ui)
        ev = term.poll_event(timeout_ms=200)
        if ev:
            if ev.code in ("q", "Esc"): break
            elif ev.code == "n": url_idx += 1
            elif ev.code == "i":
                color_scheme = (
                    QrColors.Default if color_scheme == QrColors.Inverted
                    else QrColors.Inverted
                )
```

---

## See Also

- [Example 17 — QrCodeWidget](../../examples/17_qrcode.py)
- [qrcode crate](https://crates.io/crates/qrcode) — the underlying encoder
