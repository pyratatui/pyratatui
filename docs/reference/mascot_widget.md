# Ratatui Mascot

`pyratatui` exposes Ratatui’s built-in mascot widget as a small easter egg:

- `RatatuiMascot`
- `MascotEyeColor`

## API

The widget is builder-style (returns a new widget):

```python
from pyratatui import MascotEyeColor, RatatuiMascot

mascot = RatatuiMascot().set_eye(MascotEyeColor.Red)
```

## Example

```python
from pyratatui import Block, Constraint, Direction, Layout, MascotEyeColor, RatatuiMascot, Terminal

with Terminal() as term:
    while True:
        def ui(frame):
            area = (
                Layout()
                .direction(Direction.Vertical)
                .constraints([Constraint.fill(1), Constraint.length(12), Constraint.fill(1)])
                .split(frame.area)[1]
            )

            frame.render_widget(Block().bordered().title(" Mascot (press q) "), area)
            frame.render_widget(RatatuiMascot(MascotEyeColor.Red), area.inner(1, 1))

        term.draw(ui)
        ev = term.poll_event(timeout_ms=100)
        if ev and ev.code == "q":
            break
```
