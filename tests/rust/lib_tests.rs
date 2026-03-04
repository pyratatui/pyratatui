// tests/rust/lib_tests.rs
//! Rust-side unit tests for pyratatui bindings.
//!
//! Run with: `cargo test`

#[cfg(test)]
mod tests {
    use ratatui::{
        layout::{Rect, Constraint, Layout, Direction, Flex},
        style::{Color, Style, Modifier},
        text::{Span, Line, Text},
        widgets::{Block, Borders, Paragraph},
    };

    // ── Layout tests ──────────────────────────────────────────────────────────

    #[test]
    fn test_rect_basic() {
        let r = Rect { x: 0, y: 0, width: 80, height: 24 };
        assert_eq!(r.area(), 1920);
        assert_eq!(r.right(), 80);
        assert_eq!(r.bottom(), 24);
    }

    #[test]
    fn test_layout_vertical_split() {
        let area = Rect { x: 0, y: 0, width: 80, height: 24 };
        let chunks = Layout::default()
            .direction(Direction::Vertical)
            .constraints([Constraint::Length(3), Constraint::Fill(1)])
            .split(area);
        assert_eq!(chunks.len(), 2);
        assert_eq!(chunks[0].height, 3);
        assert_eq!(chunks[1].y, 3);
    }

    #[test]
    fn test_layout_horizontal_split() {
        let area = Rect { x: 0, y: 0, width: 80, height: 24 };
        let chunks = Layout::default()
            .direction(Direction::Horizontal)
            .constraints([Constraint::Percentage(50), Constraint::Percentage(50)])
            .split(area);
        assert_eq!(chunks.len(), 2);
    }

    #[test]
    fn test_nested_layout() {
        let area = Rect { x: 0, y: 0, width: 100, height: 40 };
        let outer = Layout::default()
            .direction(Direction::Vertical)
            .constraints([Constraint::Length(5), Constraint::Fill(1)])
            .split(area);
        let inner = Layout::default()
            .direction(Direction::Horizontal)
            .constraints([Constraint::Fill(1), Constraint::Fill(1)])
            .split(outer[1]);
        assert_eq!(inner.len(), 2);
    }

    // ── Style tests ───────────────────────────────────────────────────────────

    #[test]
    fn test_style_fg_bg() {
        let s = Style::default().fg(Color::Red).bg(Color::Black);
        assert_eq!(s.fg, Some(Color::Red));
        assert_eq!(s.bg, Some(Color::Black));
    }

    #[test]
    fn test_style_modifier() {
        let s = Style::default()
            .add_modifier(Modifier::BOLD)
            .add_modifier(Modifier::ITALIC);
        assert!(s.add_modifier.contains(Modifier::BOLD));
        assert!(s.add_modifier.contains(Modifier::ITALIC));
    }

    #[test]
    fn test_style_patch() {
        let base = Style::default().fg(Color::Red);
        let overlay = Style::default().bg(Color::Black);
        let merged = base.patch(overlay);
        assert_eq!(merged.fg, Some(Color::Red));
        assert_eq!(merged.bg, Some(Color::Black));
    }

    // ── Text tests ────────────────────────────────────────────────────────────

    #[test]
    fn test_span_creation() {
        let s = Span::raw("hello");
        assert_eq!(s.content, "hello");
        assert_eq!(s.width(), 5);
    }

    #[test]
    fn test_styled_span() {
        let s = Span::styled("world", Style::default().fg(Color::Green));
        assert_eq!(s.content, "world");
        assert_eq!(s.style.fg, Some(Color::Green));
    }

    #[test]
    fn test_line_from_spans() {
        let line = Line::from(vec![
            Span::raw("Hello"),
            Span::styled(" World", Style::default().fg(Color::Blue)),
        ]);
        assert_eq!(line.spans.len(), 2);
    }

    #[test]
    fn test_text_multiline() {
        let text = Text::from("line1\nline2\nline3");
        assert_eq!(text.lines.len(), 3);
    }

    // ── Widget construction tests ──────────────────────────────────────────────

    #[test]
    fn test_block_construction() {
        let block = Block::default()
            .title("Test")
            .borders(Borders::ALL);
        // Simply verify it compiles and constructs without panic.
        let _ = block;
    }

    #[test]
    fn test_paragraph_construction() {
        let para = Paragraph::new(Text::from("Hello, World!"))
            .block(Block::default().borders(Borders::ALL))
            .style(Style::default().fg(Color::White));
        let _ = para;
    }

    // ── Buffer test ───────────────────────────────────────────────────────────

    #[test]
    fn test_buffer_write_read() {
        use ratatui::buffer::Buffer;
        let area = Rect { x: 0, y: 0, width: 10, height: 1 };
        let mut buf = Buffer::empty(area);
        buf.set_string(0, 0, "Hello", Style::default());
        let idx = buf.index_of(0, 0);
        assert_eq!(buf.content[idx].symbol(), "H");
    }

    // ── TestBackend render test ───────────────────────────────────────────────

    #[test]
    fn test_terminal_render_with_test_backend() {
        use ratatui::{Terminal, backend::TestBackend};
        let backend = TestBackend::new(80, 24);
        let mut terminal = Terminal::new(backend).unwrap();
        terminal.draw(|frame| {
            let area = frame.area();
            frame.render_widget(
                Block::default().title("Test").borders(Borders::ALL),
                area,
            );
        }).unwrap();
        let buf = terminal.backend().buffer().clone();
        // Top-left corner character should be a border.
        let idx = buf.index_of(0, 0);
        let sym = buf.content[idx].symbol();
        assert!(!sym.is_empty(), "Border character should be present");
    }

    #[test]
    fn test_gauge_render() {
        use ratatui::{Terminal, backend::TestBackend, widgets::Gauge};
        let backend = TestBackend::new(40, 3);
        let mut terminal = Terminal::new(backend).unwrap();
        terminal.draw(|frame| {
            frame.render_widget(
                Gauge::default().percent(50).label("50%"),
                frame.area(),
            );
        }).unwrap();
    }
}
