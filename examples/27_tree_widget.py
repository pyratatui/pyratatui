#!/usr/bin/env python3
"""
27_tree_widget.py — tui-tree-widget: interactive tree view

Displays a file-system-like tree.  Navigate with arrow keys:
  ↑/↓ = move, → = open node, ← = close/go up, q = quit.
"""

from __future__ import annotations

from pyratatui import (
    Block,
    Color,
    Constraint,
    Direction,
    Layout,
    Paragraph,
    Style,
    Terminal,
    Tree,
    TreeItem,
    TreeState,
)


def build_tree() -> list[TreeItem]:
    return [
        TreeItem(
            "📁 Documents",
            [
                TreeItem("📄 report.pdf"),
                TreeItem("📄 notes.md"),
                TreeItem(
                    "📁 Projects",
                    [
                        TreeItem(
                            "📁 pyratatui",
                            [
                                TreeItem("📄 Cargo.toml"),
                                TreeItem("📄 README.md"),
                                TreeItem(
                                    "📁 src",
                                    [
                                        TreeItem("📄 lib.rs"),
                                        TreeItem("📄 widgets/mod.rs"),
                                    ],
                                ),
                            ],
                        ),
                        TreeItem("📁 other-project"),
                    ],
                ),
            ],
        ),
        TreeItem(
            "📁 Downloads",
            [
                TreeItem("📦 rustup-init.sh"),
                TreeItem("📦 python3.12.tar.gz"),
            ],
        ),
        TreeItem(
            "📁 Pictures",
            [
                TreeItem("🖼 vacation.jpg"),
                TreeItem("🖼 screenshot.png"),
            ],
        ),
        TreeItem("📄 .bashrc"),
        TreeItem("📄 .gitconfig"),
    ]


def main():
    items = build_tree()
    tree = (
        Tree(items)
        .block(
            Block()
            .bordered()
            .title(" File Tree — ↑↓ navigate, → open, ← close, q quit ")
        )
        .highlight_style(Style().fg(Color.yellow()).bold())
        .highlight_symbol("► ")
    )
    state = TreeState()
    state.select([0])  # start on first item

    with Terminal() as term:
        while True:

            def ui(frame, _tree=tree, _state=state):
                area = frame.area
                chunks = (
                    Layout()
                    .direction(Direction.Vertical)
                    .constraints([Constraint.fill(1), Constraint.length(1)])
                    .split(area)
                )
                frame.render_stateful_tree(_tree, chunks[0], _state)

                sel = _state.selected
                hint = f" selected: {sel}" if sel else " (nothing selected)"
                frame.render_widget(
                    Paragraph.from_string(hint).style(Style().fg(Color.dark_gray())),
                    chunks[1],
                )

            term.draw(ui)
            ev = term.poll_event(timeout_ms=50)
            if ev:
                if ev.code == "q" or (ev.code == "c" and ev.ctrl):
                    break
                elif ev.code == "Up":
                    state.key_up()
                elif ev.code == "Down":
                    state.key_down()
                elif ev.code == "Left":
                    state.key_left()
                elif ev.code == "Right":
                    state.key_right()


if __name__ == "__main__":
    main()
