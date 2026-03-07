# Calendar Widget

The `Monthly` widget renders a full monthly calendar in the terminal with
per-day event styling, optional surrounding days, weekday headers, and a
month/year title.

The widget is backed by ratatui's built-in `widget-calendar` feature and uses
the [`time`](https://docs.rs/time) crate for date handling.

---

## Imports

```python
from pyratatui import (
    CalendarDate,
    CalendarEventStore,
    Monthly,
    Style,
    Color,
)
```

---

## CalendarDate

Wraps `time::Date`. Represents a specific calendar day.

```python
# From explicit year/month/day
d = CalendarDate.from_ymd(2024, 3, 15)   # March 15, 2024

# Today (UTC)
today = CalendarDate.today()

# Properties
print(today.year)    # int
print(today.month)   # int (1-12)
print(today.day)     # int
```

`from_ymd` raises `ValueError` for invalid dates (e.g. Feb 30).

---

## CalendarEventStore

A mapping from `CalendarDate` to `Style` that the `Monthly` widget uses
to style individual days.

```python
store = CalendarEventStore()

# Mark a specific date
store.add(CalendarDate.from_ymd(2024, 12, 25), Style().fg(Color.red()).bold())

# Mark today
store.add_today(Style().fg(Color.green()).bold())

# Create a store with today pre-highlighted
store = CalendarEventStore.today_highlighted(Style().fg(Color.green()).bold())
```

---

## Monthly

The calendar widget itself.

```python
store = CalendarEventStore.today_highlighted(Style().fg(Color.green()).bold())
cal   = (
    Monthly(CalendarDate.today(), store)
    .block(Block().bordered().title(" My Calendar "))
    .show_month_header(Style().bold().fg(Color.cyan()))
    .show_weekdays_header(Style().italic().fg(Color.white()))
    .show_surrounding(Style().dim())
    .default_style(Style().fg(Color.white()))
)

# Render like any other widget
frame.render_widget(cal, area)
```

### Constructor

```python
Monthly(display_date: CalendarDate, events: CalendarEventStore)
```

`display_date` — any date in the month to display.
`events`       — the event store providing per-day styles.

### Builder methods

| Method | Description |
|--------|-------------|
| `.block(Block)` | Wrap in a Block with border/title |
| `.default_style(Style)` | Style for all un-styled days |
| `.show_surrounding(Style)` | Show adjacent-month days in this style |
| `.show_month_header(Style)` | Show the "Month Year" header in this style |
| `.show_weekdays_header(Style)` | Show "Su Mo Tu …" header in this style |

All builder methods return a new `Monthly` instance (immutable builder
pattern).  The original is not modified.

---

## Minimum size

The `Monthly` widget requires at least **9 columns × 8 rows** for a single
month without any surrounding days.  Add 2 rows for headers.

---

## Full interactive example

See [examples/25_calendar.py](../../examples/25_calendar.py):

```bash
python examples/25_calendar.py
```

Controls: `←/→` change months, `↑/↓` change years, `t` jump to today, `q` quit.

---

## Weekend highlighting recipe

```python
import calendar

def make_store_with_weekends(year: int, month: int) -> CalendarEventStore:
    store = CalendarEventStore()
    store.add_today(Style().fg(Color.green()).bold())

    _, days = calendar.monthrange(year, month)
    for day in range(1, days + 1):
        if calendar.weekday(year, month, day) >= 5:   # Sat/Sun
            store.add(
                CalendarDate.from_ymd(year, month, day),
                Style().fg(Color.yellow()).dim(),
            )
    return store
```
