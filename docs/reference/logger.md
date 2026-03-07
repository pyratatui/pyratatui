# Logger Widget

The `TuiLoggerWidget` displays captured log messages in a scrollable view using
[tui-logger](https://crates.io/crates/tui-logger).

## Quick Start

```python
from pyratatui import init_logger, log_message, TuiLoggerWidget, TuiWidgetState, Block, Style, Color

# Call once at startup
init_logger("debug")

widget = (
    TuiLoggerWidget()
    .block(Block().bordered().title(" Logs "))
    .error_style(Style().fg(Color.red()).bold())
    .warn_style(Style().fg(Color.yellow()))
    .info_style(Style().fg(Color.green()))
)
state = TuiWidgetState()

# In render loop:
# frame.render_logger(widget, area, state)

# To emit log messages:
log_message("info", "Application started")
log_message("warn", "Low memory")
```

## API

### `init_logger(level="info")`

Initialise the logger backend. Must be called once before rendering.
Valid levels: `"error"`, `"warn"`, `"info"`, `"debug"`, `"trace"`.

### `log_message(level, message)`

Emit a log message at the given level.

### `TuiWidgetState()`

| Method | Description |
|--------|-------------|
| `.transition(key)` | Send navigation event (`"up"`, `"down"`, `"+"`, `"-"`, `"pageup"`, etc.) |

### `TuiLoggerWidget()`

| Method | Description |
|--------|-------------|
| `.block(block)` | Wrap in a border block |
| `.style(style)` | Overall widget style |
| `.error_style(style)` | Style for ERROR messages |
| `.warn_style(style)` | Style for WARN messages |
| `.info_style(style)` | Style for INFO messages |
| `.debug_style(style)` | Style for DEBUG messages |
| `.trace_style(style)` | Style for TRACE messages |

## Rendering

```python
frame.render_logger(widget, area, state)
```

See `examples/29_logger_demo.py`.
