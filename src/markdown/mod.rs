// src/markdown/mod.rs — Python bindings for tui-markdown 0.3
//
// API (tui-markdown 0.3.x):
//   tui_markdown::from_str(input: &str) -> ratatui::text::Text<'_>
//   (borrows from input — we must call into_static() to get Text<'static>)

use crate::text::Text;
use pyo3::prelude::*;
use ratatui::text::{Line as RLine, Span as RSpan, Text as RText};

/// Convert `Text<'_>` (borrows from source string) into `Text<'static>`
/// by cloning all string data into owned `Cow::Owned` spans.
fn into_static(t: RText<'_>) -> RText<'static> {
    RText {
        lines: t
            .lines
            .into_iter()
            .map(|line| RLine {
                spans: line
                    .spans
                    .into_iter()
                    .map(|span| RSpan::styled(span.content.into_owned(), span.style))
                    .collect(),
                style: line.style,
                alignment: line.alignment,
            })
            .collect(),
        style: t.style,
        alignment: t.alignment,
    }
}

/// Convert a Markdown string into a `Text` object suitable for rendering.
///
/// ```python
/// from pyratatui import markdown_to_text, Paragraph
/// text = markdown_to_text("# Hello\n\n**bold** _italic_")
/// frame.render_widget(Paragraph.new(text), area)
/// ```
#[pyfunction]
pub fn markdown_to_text(src: &str) -> Text {
    let ratatui_text = tui_markdown::from_str(src);
    Text::from_ratatui(into_static(ratatui_text))
}

// ─── Registration ─────────────────────────────────────────────────────────────

pub fn register_markdown(_py: Python<'_>, m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(markdown_to_text, m)?)?;
    Ok(())
}
