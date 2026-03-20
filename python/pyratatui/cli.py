"""
cli.py — PyRatatui unified CLI.

Entry point: ``pyratatui``  (registered via [project.scripts] in pyproject.toml)

Commands
--------
  pyratatui install <user/repo>    Clone & install a TUI app from GitHub
  pyratatui uninstall <app>        Remove an installed app
  pyratatui list                   List installed apps
  pyratatui run <app>              Run an installed app
  pyratatui info <app>             Show detailed metadata for an installed app
  pyratatui init <project>         Scaffold a new PyRatatui project
  pyratatui version                Print the pyratatui package version
"""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from .manager.install import install_app
from .manager.list import list_apps
from .manager.run import run_app
from .manager.uninstall import uninstall_app
from .manager.utils import list_installed

# ── Typer app ─────────────────────────────────────────────────────────────────

app = typer.Typer(
    name="pyratatui",
    help=(
        "🐀 PyRatatui — Professional Python TUI framework.\n\n"
        "Manage apps with install / uninstall / list / run, "
        "or scaffold a new project with init."
    ),
    no_args_is_help=True,
    add_completion=True,
)

# ── Init templates ─────────────────────────────────────────────────────────────

_MAIN_TEMPLATE = '''\
#!/usr/bin/env python3
"""
{project_name} — a PyRatatui terminal UI application.

Run:
    python main.py
    # or after `pip install -e .`:
    {project_name}
"""

from pyratatui import Block, Color, Paragraph, Style, Terminal


def main() -> None:
    """Application entry point."""
    with Terminal() as term:
        while True:

            def ui(frame):
                frame.render_widget(
                    Paragraph.from_string(
                        "Hello from {project_name}!  Press q to quit."
                    )
                    .block(Block().bordered().title(" {project_name} "))
                    .style(Style().fg(Color.cyan())),
                    frame.area,
                )

            term.draw(ui)
            ev = term.poll_event(timeout_ms=100)
            if ev and ev.code == "q":
                break


if __name__ == "__main__":
    main()
'''

# pyproject.toml written into every scaffolded project.
# - hatchling is the build backend (zero extra config, flat-layout friendly)
# - pyratatui is declared as a runtime dep so `pip install .` pulls it in
# - the console script matches the entry point in main.py
# - `pyratatui install user/repo` will clone the project and run
#   `pip install .` automatically, making it fully self-contained
_PYPROJECT_TEMPLATE = """\
[build-system]
requires      = ["hatchling"]
build-backend = "hatchling.build"

[project]
name           = "{project_name}"
version        = "0.1.0"
description    = "A PyRatatui terminal UI application"
readme         = "README.md"
requires-python = ">=3.10"
license        = {{ text = "MIT" }}
dependencies   = [
    "pyratatui>=0.2.7",
]

[project.scripts]
# `pip install .` (or `pip install -e .`) makes this command available globally.
# `pyratatui install user/{project_name}` uses this same entry point.
{project_name} = "main:main"

[tool.hatch.build.targets.wheel]
# Flat layout: include main.py directly (no package directory needed)
include = ["main.py"]

[tool.hatch.build.targets.sdist]
include = ["main.py", "README.md", "pyproject.toml", ".gitignore"]
"""

_README_TEMPLATE = """\
# {project_name}

A [PyRatatui](https://github.com/pyratatui/pyratatui) terminal UI application.

## Quick start

```bash
# Clone and run directly
git clone https://github.com/<your-username>/{project_name}.git
cd {project_name}
pip install .
python main.py
```

Or install it with the PyRatatui app manager:

```bash
pyratatui install <your-username>/{project_name}
pyratatui run {project_name}
```

## Development

```bash
# Editable install — changes to main.py take effect immediately
pip install -e .

# Run
python main.py
# or:
{project_name}
```

## Built with

- [pyratatui](https://github.com/pyratatui/pyratatui) ≥ 0.2.7
- Python ≥ 3.10
"""

_GITIGNORE_TEMPLATE = """\
# Python
__pycache__/
*.py[cod]
*.pyo
*.pyd
*.egg
*.egg-info/
dist/
build/
.eggs/
pip-wheel-metadata/
*.whl

# Virtual environments
.venv/
venv/
env/
ENV/

# Hatch / build artefacts
.hatch/
*.dist-info/

# Type checkers & linters
.mypy_cache/
.ruff_cache/
.pytype/

# Editors
.vscode/
.idea/
*.swp
*.swo
*~

# macOS
.DS_Store

# Windows
Thumbs.db
desktop.ini

# Testing
.pytest_cache/
.coverage
htmlcov/
"""

# ── install ───────────────────────────────────────────────────────────────────


@app.command("install")
def cmd_install(
    repo_slug: Annotated[
        str,
        typer.Argument(
            help="GitHub repo in user/repo format, e.g.  pyratatui/test_app",
            metavar="USER/REPO",
        ),
    ],
    branch: Annotated[
        str | None,
        typer.Option("--branch", "-b", help="Branch, tag, or commit to checkout."),
    ] = None,
    force: Annotated[
        bool,
        typer.Option("--force", "-f", help="Re-install even if already present."),
    ] = False,
    quiet: Annotated[
        bool,
        typer.Option("--quiet", "-q", help="Suppress non-error output."),
    ] = False,
) -> None:
    """Clone and install a TUI app from GitHub.

    Examples:

        pyratatui install pyratatui/test_app

        pyratatui install pyratatui/test_app --branch dev

        pyratatui install pyratatui/test_app --force
    """
    install_app(repo_slug, branch=branch, force=force, quiet=quiet)


# ── uninstall ─────────────────────────────────────────────────────────────────


@app.command("uninstall")
def cmd_uninstall(
    repo: Annotated[
        str,
        typer.Argument(
            help="Short app name (repo name), e.g.  test_app", metavar="APP"
        ),
    ],
    yes: Annotated[
        bool,
        typer.Option("--yes", "-y", help="Skip the confirmation prompt."),
    ] = False,
) -> None:
    """Remove an installed app.

    Examples:

        pyratatui uninstall test_app

        pyratatui uninstall test_app --yes
    """
    uninstall_app(repo, yes=yes)


# ── list ──────────────────────────────────────────────────────────────────────


@app.command("list")
def cmd_list(
    as_json: Annotated[
        bool,
        typer.Option("--json", help="Output raw JSON."),
    ] = False,
) -> None:
    """List all installed pyratatui apps.

    Examples:

        pyratatui list

        pyratatui list --json
    """
    list_apps(as_json=as_json)


# ── run ───────────────────────────────────────────────────────────────────────


@app.command(
    "run",
    context_settings={"allow_extra_args": True, "ignore_unknown_options": True},
)
def cmd_run(
    ctx: typer.Context,
    app_name: Annotated[
        str,
        typer.Argument(
            help="Short app name (repo name), e.g.  test_app", metavar="APP"
        ),
    ],
) -> None:
    """Run an installed app.

    Any arguments after APP are forwarded verbatim to the app.

    Examples:

        pyratatui run test_app

        pyratatui run test_app -- --help
    """
    run_app(app_name, extra_args=ctx.args)


# ── info ──────────────────────────────────────────────────────────────────────


@app.command("info")
def cmd_info(
    app_name: Annotated[
        str,
        typer.Argument(
            help="Short app name (repo name), e.g.  test_app", metavar="APP"
        ),
    ],
) -> None:
    """Show detailed metadata for an installed app.

    Example:

        pyratatui info test_app
    """
    all_apps = list_installed()
    matches = [a for a in all_apps if a.get("repo") == app_name]

    if not matches:
        typer.echo(
            typer.style(f"Error: '{app_name}' is not installed.", fg=typer.colors.RED),
            err=True,
        )
        raise typer.Exit(1)

    meta = matches[0]
    src_dir = Path(meta.get("app_dir", ""))
    present = src_dir.exists()

    typer.echo(typer.style(f"\n📦 {meta.get('repo', '?')}", bold=True))
    typer.echo(f"  Source    : {meta.get('slug', '?')}")
    typer.echo(f"  URL       : {meta.get('url', '?')}")
    typer.echo(f"  Branch    : {meta.get('branch', '?')}")
    typer.echo(f"  Installed : {meta.get('installed_at', '?')}")
    typer.echo(f"  Directory : {meta.get('app_dir', '?')}")
    typer.echo(f"  Wrapper   : {meta.get('wrapper', '?')}")
    typer.echo(f"  Entry pt  : {meta.get('entrypoint', '?')}")
    status_str = (
        typer.style("present ✓", fg=typer.colors.GREEN)
        if present
        else typer.style("MISSING ✗", fg=typer.colors.RED)
    )
    typer.echo(f"  Status    : {status_str}")


# ── init ──────────────────────────────────────────────────────────────────────


@app.command("init")
def cmd_init(
    project_name: Annotated[
        str,
        typer.Argument(help="Name of the new project directory to create."),
    ],
    verbose: Annotated[
        bool,
        typer.Option("--verbose", "-v", help="Print each file as it is created."),
    ] = False,
) -> None:
    """Scaffold a new PyRatatui project.

    Creates a ready-to-publish project with:
      main.py         — runnable TUI application
      pyproject.toml  — packaging config (hatchling, entry point, pyratatui dep)
      .gitignore      — standard Python gitignore
      README.md       — usage instructions

    The generated pyproject.toml is configured so the project can be pushed to
    GitHub as-is and installed with:

        pyratatui install <github-user>/{project_name}

    Examples:

        pyratatui init my-tui-app

        pyratatui init my-tui-app --verbose
    """
    # Normalise: hyphens are fine in the directory name, but the Python
    # identifier used in entry points must use underscores.
    py_name = project_name.replace("-", "_")

    project_path = Path(project_name)
    if project_path.exists():
        typer.echo(
            typer.style(
                f"Error: directory '{project_name}' already exists.",
                fg=typer.colors.RED,
            ),
            err=True,
        )
        raise typer.Exit(1)

    try:
        project_path.mkdir(parents=True)

        files: dict[Path, str] = {
            project_path
            / "main.py": _MAIN_TEMPLATE.format(
                project_name=project_name,
                py_name=py_name,
            ),
            project_path
            / "pyproject.toml": _PYPROJECT_TEMPLATE.format(
                project_name=project_name,
                py_name=py_name,
            ),
            project_path / ".gitignore": _GITIGNORE_TEMPLATE,
            project_path
            / "README.md": _README_TEMPLATE.format(
                project_name=project_name,
                py_name=py_name,
            ),
        }

        for fp, content in files.items():
            fp.write_text(content, encoding="utf-8")
            if verbose:
                typer.echo(f"  created {fp}")

        typer.echo(
            typer.style(f"\n✓ Created project '{project_name}'.", fg=typer.colors.GREEN)
        )
        typer.echo("\nNext steps:")
        typer.echo(f"  cd {project_name}")
        typer.echo(
            "  pip install -e .          # installs pyratatui + registers the CLI script"
        )
        typer.echo("  python main.py            # run directly")
        typer.echo(f"  {project_name}            # or via the installed entry point")
        typer.echo("\nWhen ready to share:")
        typer.echo("  git init && git add . && git commit -m 'init'")
        typer.echo(
            "  git remote add origin https://github.com/<you>/{project_name}.git"
        )
        typer.echo("  git push -u origin main")
        typer.echo("\nOthers can then install it with:")
        typer.echo(f"  pyratatui install <you>/{project_name}")

    except OSError as exc:
        typer.echo(typer.style(f"Error: {exc}", fg=typer.colors.RED), err=True)
        raise typer.Exit(1) from exc


# ── version ───────────────────────────────────────────────────────────────────


@app.command("version")
def cmd_version() -> None:
    """Print the installed pyratatui version.

    Example:

        pyratatui version
    """
    try:
        import pyratatui

        typer.echo(f"pyratatui {pyratatui.__version__}")
        typer.echo(f"ratatui   {pyratatui.__ratatui_version__}")
    except (ImportError, AttributeError) as exc:
        typer.echo("pyratatui is not properly installed.", err=True)
        raise typer.Exit(1) from exc


# ── entry point ───────────────────────────────────────────────────────────────


def main() -> None:
    """CLI entry point registered in pyproject.toml."""
    app()


if __name__ == "__main__":
    main()
