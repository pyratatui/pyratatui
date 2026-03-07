#!/usr/bin/env python3
"""
29_logger_demo.py — tui-logger: real-time log viewer widget

Actual tui-logger key bindings (from the library docs):
  Left / Right   — decrease / increase the SHOWN log level
  +  /  -        — decrease / increase the CAPTURED log level
  PageUp         — enter page mode, scroll ~half page up in history
  PageDown       — scroll 10 events down (page mode only)
  Escape         — exit page mode, return to live-scroll view
  Up / Down      — navigate target selector (not used here)
  q / Ctrl-C     — quit
"""

from __future__ import annotations

import random
import threading
import time

from pyratatui import (
    Block,
    Color,
    Constraint,
    Direction,
    Layout,
    Paragraph,
    Style,
    Terminal,
    TuiLoggerWidget,
    TuiWidgetState,
    init_logger,
    log_message,
)

LOG_MESSAGES = [
    ("info", "Request processed in {ms}ms"),
    ("debug", "Cache hit for key '{key}'"),
    ("warn", "Response time {ms}ms exceeds threshold"),
    ("error", "Connection timeout to {host}"),
    ("debug", "Worker {id} completed task"),
    ("info", "New connection from {host}:{port}"),
    ("trace", "Entering function process_data()"),
    ("info", "Batch of {n} items queued"),
    ("warn", "Memory usage at {pct}%"),
    ("error", "Failed to parse config: unexpected token"),
]

HOSTS = ["10.0.0.1", "192.168.1.5", "api.example.com", "db.local"]
KEYS = ["session:abc", "user:42", "cache:v1", "prefs:en"]


def log_background() -> None:
    """Emit random log messages in a background thread."""
    while True:
        level, tmpl = random.choice(LOG_MESSAGES)
        msg = tmpl.format(
            ms=random.randint(5, 3000),
            key=random.choice(KEYS),
            host=random.choice(HOSTS),
            port=random.randint(1024, 65535),
            id=random.randint(1, 8),
            n=random.randint(10, 500),
            pct=random.randint(50, 95),
        )
        log_message(level, msg)
        time.sleep(random.uniform(0.1, 0.4))


HELP = (
    "  \u2190/\u2192 shown level   +/- captured level"
    "   PgUp scroll up   PgDn scroll dn"
    "   Esc live view   q quit"
)

# Map ev.code values -> what state.transition() understands.
# The Rust binding matches these strings case-insensitively.
#
# Actual tui-logger key semantics (from library docs):
#   Up / Down    -> navigate TARGET SELECTOR  (not log scroll!)
#   Left / Right -> reduce / increase SHOWN log level
#   +  /  -      -> increase / decrease CAPTURED log level
#   PageUp       -> enter page mode + scroll ~half page up in history
#   PageDown     -> scroll 10 events down (only in page mode)
#   Escape       -> exit page mode, resume live-scroll view
#   Space        -> toggle hiding of targets with level Off
#   h            -> toggle target-selector widget hidden/visible
#   f            -> toggle focus on selected target only
KEY_MAP: dict[str, str] = {
    "PageUp": "PageUp",
    "PageDown": "PageDown",
    "Esc": "Escape",
    "Left": "Left",
    "Right": "Right",
    "+": "+",
    "-": "-",
    "Up": "Up",
    "Down": "Down",
    " ": "Space",
    "h": "hide",
    "f": "focus",
}


def main() -> None:
    init_logger("trace")

    t = threading.Thread(target=log_background, daemon=True)
    t.start()

    widget = (
        TuiLoggerWidget()
        .block(Block().bordered().title(" Application Logs "))
        .style(Style().fg(Color.white()))
        .error_style(Style().fg(Color.red()).bold())
        .warn_style(Style().fg(Color.yellow()))
        .info_style(Style().fg(Color.green()))
        .debug_style(Style().fg(Color.cyan()))
        .trace_style(Style().fg(Color.dark_gray()))
    )
    state = TuiWidgetState()

    with Terminal() as term:
        while True:

            def ui(frame, _w=widget, _s=state):
                area = frame.area
                chunks = (
                    Layout()
                    .direction(Direction.Vertical)
                    .constraints([Constraint.fill(1), Constraint.length(1)])
                    .split(area)
                )
                frame.render_logger(_w, chunks[0], _s)
                frame.render_widget(
                    Paragraph.from_string(HELP).style(Style().fg(Color.dark_gray())),
                    chunks[1],
                )

            term.draw(ui)

            ev = term.poll_event(timeout_ms=200)
            if ev:
                if ev.code == "q" or (ev.code == "c" and ev.ctrl):
                    break
                tui_key = KEY_MAP.get(ev.code)
                if tui_key:
                    state.transition(tui_key)


if __name__ == "__main__":
    main()
