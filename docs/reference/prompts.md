# Prompts Reference

pyratatui provides interactive text-input prompt widgets built natively on ratatui 0.29.
Prompts use a stateful model: a **state object** holds the mutable input value and is passed
to both the render call and the event handler each frame.

---

## Quick start

```python
from pyratatui import Terminal, TextPrompt, TextState

state = TextState()
state.focus()

with Terminal() as term:
    term.hide_cursor()

    while state.is_pending():
        def ui(frame, _s=state):
            frame.render_text_prompt(
                TextPrompt("Name: "),
                frame.area,
                _s,
            )
        term.draw(ui)

        ev = term.poll_event(timeout_ms=50)
        if ev:
            state.handle_key(ev)

if state.is_complete():
    print(f"Hello, {state.value()}!")
```

---

## TextState

`TextState` holds all mutable input data for a prompt. One instance is shared
between the render call and the event handler each frame.

### Constructor

```python
state = TextState()
state = TextState("prefilled value")
```

| Parameter | Type | Default | Description |
|---|---|---|---|
| `initial` | `str` | `""` | Optional pre-filled value |

### Focus

```python
state.focus()   # enable cursor rendering
state.blur()    # hide cursor
state.is_focused  # property → bool
```

### Value

```python
state.value()           # → str  current input
state.set_value("new")  # replace content, cursor to end
state.clear_input()     # erase buffer
state.cursor_pos        # property → int  cursor character index
```

### Status

```python
state.status       # property → PromptStatus
state.is_pending() # True while waiting for input
state.is_complete()# True after Enter
state.is_aborted() # True after Esc / Ctrl+C
state.reset_status()  # reset to Pending, keep value
state.reset()         # clear value + reset to Pending
```

### Key handling

```python
consumed = state.handle_key(ev)  # ev: KeyEvent (or any obj with .code/.ctrl/.alt)
```

Returns `True` if the event was consumed by the prompt.

---

## Key Bindings

| Key | Action |
|---|---|
| **Enter** | Complete the prompt (`status → Complete`) |
| **Esc** | Abort the prompt (`status → Aborted`) |
| **Ctrl+C** | Abort the prompt |
| **Backspace** | Delete character before cursor |
| **Delete** | Delete character at cursor |
| **Left** / **Ctrl+B** | Move cursor one character left |
| **Right** / **Ctrl+F** | Move cursor one character right |
| **Home** / **Ctrl+A** | Move cursor to beginning |
| **End** / **Ctrl+E** | Move cursor to end |
| **Ctrl+K** | Delete from cursor to end of line |
| **Ctrl+U** | Delete entire line |
| **Ctrl+W** | Delete word before cursor |

---

## PromptStatus

```python
from pyratatui import PromptStatus
```

An enum describing the current lifecycle state of a prompt.

| Value | Meaning |
|---|---|
| `PromptStatus.Pending` | Input is still in progress |
| `PromptStatus.Complete` | User pressed Enter; call `state.value()` |
| `PromptStatus.Aborted` | User pressed Esc or Ctrl+C |

---

## TextRenderStyle

```python
from pyratatui import TextRenderStyle
```

Controls how the typed characters are displayed.

| Value | Description |
|---|---|
| `TextRenderStyle.Normal` | Characters shown as typed (default) |
| `TextRenderStyle.Password` | Each character replaced with `*` |
| `TextRenderStyle.Invisible` | Input is hidden entirely |

```python
# Create a password-masked prompt
prompt = TextPrompt("Token: ", TextRenderStyle.Password)
# or via builder:
prompt = TextPrompt("Token: ").with_render_style(TextRenderStyle.Password)
```

---

## TextPrompt

A single-line text input prompt that renders a label + live input field.

### Constructor

```python
TextPrompt(label: str, render_style: TextRenderStyle = TextRenderStyle.Normal)
```

### Builder

```python
prompt = TextPrompt("Input: ").with_render_style(TextRenderStyle.Password)
```

### Rendering

```python
def ui(frame):
    frame.render_text_prompt(
        TextPrompt("Search: "),
        area,
        state,
    )
```

The cursor is rendered as a highlighted block when `state.is_focused` is `True`.

---

## PasswordPrompt

A convenience alias for a masked text prompt.  Identical to
`TextPrompt("…", TextRenderStyle.Password)`.

### Constructor

```python
PasswordPrompt(label: str)
```

### Rendering

```python
def ui(frame):
    frame.render_password_prompt(
        PasswordPrompt("Password: "),
        area,
        state,
    )
```

---

## Frame render methods

Both prompt types are rendered via methods on `Frame` inside a `draw()` callback.

### `frame.render_text_prompt(prompt, area, state)`

| Parameter | Type | Description |
|---|---|---|
| `prompt` | `TextPrompt` | The prompt widget |
| `area` | `Rect` | The area to render into |
| `state` | `TextState` | The mutable state |

### `frame.render_password_prompt(prompt, area, state)`

Same signature but `prompt` is a `PasswordPrompt` instance.

---

## Blocking helpers

For simple scripts that just need to collect a value, pyratatui provides
one-liner blocking helpers that manage the full terminal lifecycle:

### `prompt_text(label) → str | None`

```python
from pyratatui import prompt_text

name = prompt_text("Enter your name: ")
if name:
    print(f"Hello, {name}!")
```

Opens a centered TUI input dialog, waits for the user to press Enter or Esc,
then restores the terminal and returns the entered string (or `None` if aborted).

### `prompt_password(label) → str | None`

```python
from pyratatui import prompt_password

token = prompt_password("API token: ")
```

Same as `prompt_text` but input characters are masked with `*`.

---

## Multi-prompt form example

```python
import time
from pyratatui import (
    Terminal, Layout, Constraint, Direction, Block, Style, Color,
    TextPrompt, PasswordPrompt, TextState,
)

fields = [
    ("username", TextState(), TextPrompt("Username: ")),
    ("password", TextState(), PasswordPrompt("Password: ")),
]
current = 0
fields[0][1].focus()

with Terminal() as term:
    term.hide_cursor()
    running = True

    while running:
        _cur = current

        def ui(frame, _fields=fields, _c=_cur):
            area = frame.area
            rows = (Layout()
                .direction(Direction.Vertical)
                .constraints([Constraint.length(3)] * len(_fields) + [Constraint.min(0)])
                .split(area))

            for i, (name, state, prompt) in enumerate(_fields):
                block = Block().bordered().title(f" {name} ") \
                    .style(Style().fg(Color.cyan() if i == _c else Color.gray()))
                inner = block.inner(rows[i])
                frame.render_widget(block, rows[i])

                if isinstance(prompt, PasswordPrompt):
                    frame.render_password_prompt(prompt, inner, state)
                else:
                    frame.render_text_prompt(prompt, inner, state)

        term.draw(ui)

        ev = term.poll_event(timeout_ms=50)
        if ev:
            name, state, prompt = fields[current]
            if ev.code == "Tab":
                state.blur()
                current = (current + 1) % len(fields)
                fields[current][1].focus()
            elif ev.code == "Esc":
                running = False
            elif ev.code == "Enter" and current == len(fields) - 1:
                # Last field — submit
                running = False
            else:
                state.handle_key(ev)
```

---

## Examples

| File | Description |
|---|---|
| `examples/23_prompt_text.py` | Single text field with readline hints |
| `examples/21_prompt_confirm.py` | Yes/No confirmation prompt |
| `examples/22_prompt_select.py` | Arrow-key selection menu |
