# FAQ

---

## Installation & Setup

**Q: I get `ModuleNotFoundError: No module named 'pyratatui._pyratatui'` after installing.**

The native extension was not built or installed correctly. Solutions in order of likelihood:

1. Reinstall: `pip install --force-reinstall pyratatui`
2. Build from source: `maturin develop --release` inside the cloned repo
3. Check Python version: `python --version` must be 3.10+
4. Verify the wheel matches your platform: `pip show pyratatui` and check the platform tag

---

**Q: `pip install pyratatui` triggers a Rust compilation. How do I avoid this?**

This means no pre-built wheel exists for your platform+Python combination. Options:

- Use a Python version that has a published wheel (3.10, 3.11, 3.12, 3.13)
- Build once and cache: `pip wheel pyratatui -w ./cache/` then install from cache offline
- Add Rust to your environment: `curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh`

---

**Q: How do I install pyratatui in a Docker container?**

```dockerfile
FROM python:3.12-slim

# Install Rust (only needed if building from source)
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"

RUN pip install pyratatui
```

Or use a pre-built wheel copied into the image to skip the Rust toolchain entirely.

---

## Terminal & Display

**Q: The terminal is left in a broken state after Ctrl-C.**

Always use `Terminal` as a context manager. If you bypass it or the process is killed with `SIGKILL`, run `reset` or `stty sane` in your shell to restore the terminal.

For graceful Ctrl-C handling, catch `KeyboardInterrupt`:

```python
try:
    with Terminal() as term:
        main_loop(term)
except KeyboardInterrupt:
    pass  # Terminal restored by context manager __exit__
```

---

**Q: Colors look wrong / washed out.**

Check your terminal's color support:

```bash
echo $COLORTERM   # should be "truecolor" or "24bit" for Color.rgb()
tput colors       # should be 256 for Color.indexed()
```

Use `Color.indexed()` (0–255) for maximum compatibility. Use `Color.rgb()` only in true-color terminals.

---

**Q: Unicode characters (▶, █, ●) display as `?` or boxes.**

Your terminal font doesn't include those code points. Solutions:

- Switch to a Nerd Font (JetBrains Mono, Fira Code Nerd Font, etc.)
- Use ASCII fallbacks (`>` instead of `▶`, `#` instead of `█`)
- On Windows, use Windows Terminal with Cascadia Code

---

**Q: Screen flickers on every frame.**

Ratatui's diffing algorithm only repaints cells that changed, so the native side should not flicker. Flickering usually means:

1. You are re-creating widget objects with different content every frame unnecessarily
2. Your render function is taking >33ms (dropping below 30 fps)
3. A `term.clear()` is being called every frame — only call it when you need a full repaint

---

## Async & Threading

**Q: I get `PanicException: pyratatui::terminal::Terminal is unsendable`.**

You called a `Terminal` method from a different thread than the one that created it. This is a PyO3 safety guarantee.

The fix: never pass `Terminal`, `Frame`, `Effect`, or `EffectManager` to `asyncio.to_thread` or `loop.run_in_executor`. Use `AsyncTerminal` which calls everything on the main event-loop thread.

```python
# ❌ WRONG
ev = await asyncio.to_thread(term.poll_event, 100)

# ✅ CORRECT
async for ev in term.events(fps=30):
    ...
```

---

**Q: Background asyncio tasks are not running smoothly — the UI blocks them.**

`term.draw()` is synchronous and blocks the event loop while executing. If your draw function is expensive (many widgets, large tables), the sleep in `events()` may not fire frequently enough for background tasks.

Solutions:

- Keep draw functions under 2ms
- Add `await asyncio.sleep(0)` inside background tasks to yield more aggressively
- Reduce fps: `events(fps=15)` gives background tasks more time per frame

---

**Q: How do I run multiple async background tasks safely?**

```python
async def main():
    tasks = [
        asyncio.create_task(task_a()),
        asyncio.create_task(task_b()),
    ]
    async with AsyncTerminal() as term:
        async for ev in term.events(fps=30):
            term.draw(ui)

    # Cancel all tasks and wait for cleanup
    for t in tasks:
        t.cancel()
    await asyncio.gather(*tasks, return_exceptions=True)

asyncio.run(main())
```

---

## Layout

**Q: `LayoutError: No constraints set on Layout` — how do I fix this?**

You called `.split()` before calling `.constraints()`. Always set constraints before splitting:

```python
# ❌ WRONG
chunks = Layout().split(area)

# ✅ CORRECT
chunks = (Layout()
    .constraints([Constraint.fill(1), Constraint.fill(1)])
    .split(area))
```

---

**Q: My `fill` constraint isn't getting any space.**

`fill` distributes remaining space *after* `length` and `percentage` constraints are satisfied. If your fixed constraints consume all available space, `fill` gets zero.

Check that the sum of your fixed constraints doesn't exceed the available area:

```python
# area.height = 24
# 3 + 20 + 3 = 26 > 24 → fill gets nothing
Layout().constraints([
    Constraint.length(3),
    Constraint.length(20),   # too large
    Constraint.fill(1),
    Constraint.length(3),
])
```

---

## Widgets

**Q: `RenderError: Unknown widget type` — what widget types are supported?**

`frame.render_widget()` supports: `Block`, `Paragraph`, `Gauge`, `LineGauge`, `BarChart`, `Sparkline`, `Clear`, `Tabs`, `List` (stateless), `Table` (stateless).

For `List` and `Table` with selection state, use `frame.render_stateful_list()` and `frame.render_stateful_table()`.

---

**Q: How do I make a popup/modal dialog?**

Use `Clear` to erase the area, then render the popup on top:

```python
def centered_rect(area, width, height):
    x = (area.width  - width)  // 2
    y = (area.height - height) // 2
    return Rect(area.x + x, area.y + y, width, height)

popup = centered_rect(frame.area, 40, 10)
frame.render_widget(Clear(), popup)
frame.render_widget(Block().bordered().title("Confirm"), popup)
```

---

**Q: `ListState.select_next()` wraps around even when I don't want it to.**

`select_next()` is handled by ratatui internally and will not go past the last item. If you're seeing unexpected behavior, check that you're passing the same `ListState` object to both the render call and the event handler — if they're different objects, state won't persist.

---

## Effects (TachyonFX)

**Q: Effects don't appear to do anything.**

Most common cause: the effect is applied before the widget is rendered. Effects transform cells that are **already in the buffer**. The correct order is:

```python
def ui(frame):
    frame.render_widget(my_widget, area)      # 1. render FIRST
    frame.apply_effect_manager(mgr, ms, area) # 2. effect SECOND
```

---

**Q: The effect appears then the screen goes blank.**

You are likely not tracking elapsed time correctly. The `elapsed_ms` parameter must be the actual wall-clock time since the last call, not a constant:

```python
last = time.monotonic()
while True:
    now = time.monotonic()
    ms  = int((now - last) * 1000)
    last = now
    # pass ms to apply_effect_manager
```

---

**Q: `Effect.sequence()` / `Effect.parallel()` consumes my effects — they're empty afterward.**

TachyonFX effects are `unsendable` Rust objects. `sequence()` and `parallel()` take ownership (move) of the effects from the input list. After calling them, the input effects are replaced with no-ops. This is by design — always construct new effects rather than reusing consumed ones:

```python
# ❌ Don't do this
fade = Effect.fade_from_fg(Color.black(), 800)
seq  = Effect.sequence([fade])
seq2 = Effect.sequence([fade])  # fade is now a no-op sleep(0)

# ✅ Do this
def make_sequence():
    return Effect.sequence([
        Effect.fade_from_fg(Color.black(), 800),
        Effect.sleep(200),
    ])
```

---

## Performance

**Q: My app feels slow at 30fps with many widgets.**

Profile the draw function with `cProfile` to find the bottleneck:

```python
import cProfile
cProfile.enable()
term.draw(ui)
cProfile.disable()
```

Common culprits:

- Rebuilding large lists/tables from scratch every frame — cache the widget when data hasn't changed
- Large text objects with many `Line` and `Span` objects — simplify to `Text.from_string()` where styling isn't needed
- Applying effects to `frame.area` when only a small widget needs them — pass the widget's `Rect`

---

**Q: What is the maximum recommended terminal size?**

ratatui is optimized for standard terminal sizes (80–220 columns × 24–60 rows). At very large sizes (e.g. 400×100 = 40,000 cells), per-frame rendering and effect processing time increases proportionally. Most consumer terminals cap at around 220×55.
