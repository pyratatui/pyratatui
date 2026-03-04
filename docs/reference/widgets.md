# Widgets Reference

See also: [quickstart tutorial](../tutorial/quickstart.md) for live code examples.

## Block

Bordered container. Accepts all other widgets as inner content via `frame.render_widget`.

```python
Block()
    .title("Header")
    .title_bottom("footer")
    .bordered()
    .border_type(BorderType.Rounded)
    .style(Style().fg(Color.cyan()))
    .border_style(Style().fg(Color.blue()))
    .title_style(Style().bold())
    .padding(left=1, right=1, top=0, bottom=0)
    .title_alignment("center")  # "left" | "center" | "right"
```

`BorderType`: `Plain`, `Rounded`, `Double`, `Thick`, `QuadrantInside`, `QuadrantOutside`

## Paragraph

Renders styled text with optional wrapping.

```python
Paragraph(text_obj)
Paragraph.from_string("plain text")

    .block(Block().bordered())
    .style(Style().fg(Color.white()))
    .wrap(True, trim=True)
    .scroll(y=2, x=0)
    .centered()           # or .left_aligned() / .right_aligned()
```

## List + ListState

```python
items = [ListItem("Item 1"), ListItem("Item 2", Style().fg(Color.green()))]
lst = (List(items)
    .block(Block().bordered())
    .highlight_style(Style().fg(Color.yellow()).bold())
    .highlight_symbol("▶ ")
    .direction(ListDirection.TopToBottom))

state = ListState()
state.select(0)
state.select_next()
state.select_previous()
state.select_first()
state.select_last()
state.selected      # Optional[int]

frame.render_stateful_list(lst, area, state)
```

## Table + TableState

```python
header = Row([Cell("Name").style(Style().bold()), Cell("CPU")])
rows = [
    Row([Cell("nginx"), Cell("2%").style(Style().fg(Color.green()))]),
    Row.from_strings(["redis", "0%"]),
]
widths = [Constraint.fill(1), Constraint.length(8)]

tbl = (Table(rows, widths, header=header)
    .block(Block().bordered())
    .highlight_style(Style().fg(Color.cyan()).bold())
    .column_spacing(2)
    .footer(Row.from_strings(["Total", "2%"])))

state = TableState()
frame.render_stateful_table(tbl, area, state)
```

## Gauge

```python
Gauge()
    .percent(75)          # 0-100
    .ratio(0.75)          # 0.0-1.0
    .label("75%")
    .use_unicode(True)
    .style(Style().fg(Color.green()))
    .gauge_style(Style().fg(Color.dark_gray()))
    .block(Block().bordered())
```

## LineGauge

```python
LineGauge()
    .ratio(0.65)
    .percent(65)
    .label("65%")
    .line_set("thick")   # "normal" | "thick" | "double"
    .style(Style().fg(Color.blue()))
    .gauge_style(Style().fg(Color.dark_gray()))
```

## BarChart

```python
chart = (BarChart()
    .data(BarGroup([Bar(10, "Jan"), Bar(20, "Feb")], label="Monthly"))
    .bar_width(5)
    .bar_gap(1)
    .group_gap(3)
    .max(100)
    .bar_style(Style().fg(Color.cyan()))
    .value_style(Style().fg(Color.white()))
    .label_style(Style().fg(Color.gray()))
    .block(Block().bordered().title("Chart")))
```

## Sparkline

```python
Sparkline()
    .data([10, 20, 15, 35, 25, 40])
    .max(100)
    .style(Style().fg(Color.green()))
    .block(Block().bordered())
```

## Tabs

```python
Tabs(["Overview", "Logs", "Metrics"])
    .select(1)
    .highlight_style(Style().fg(Color.yellow()).bold())
    .style(Style().fg(Color.dark_gray()))
    .divider(" | ")
    .padding(" ", " ")
    .block(Block().bordered())
```

## Scrollbar + ScrollbarState

```python
state = ScrollbarState().content_length(100).position(20)
state.scroll_next()
state.scroll_prev()

sb = (Scrollbar(ScrollbarOrientation.VerticalRight)
    .thumb_style(Style().fg(Color.cyan()))
    .track_style(Style().fg(Color.dark_gray())))

frame.render_stateful_scrollbar(sb, area, state)
```

## Clear

Erases its area — useful for popup overlays.

```python
frame.render_widget(Clear(), popup_area)
frame.render_widget(Block().bordered().title("Popup"), popup_area)
```
