"""
utils.py — Shared utilities for the pyratatui manager.

Provides path helpers, subprocess wrappers, metadata loading,
and other pieces reused across install / uninstall / list / run.

Entrypoint encoding
-------------------
``detect_entrypoint`` returns a string with a two-part prefix so callers know
*how* to launch the app, not just *what* to launch:

    "script:main.py"     → python main.py          (flat-layout root script)
    "module:myapp"       → python -m myapp          (package with __main__.py)
    "module:myapp.main"  → python -m myapp.main     (package with main.py)

``parse_entrypoint(ep)`` decodes this into ``(kind, target)``.

Backward compatibility
----------------------
Metadata written by v0.2.6 and earlier stored bare strings like ``"__main__"``
or ``"myapp.main"``.  ``parse_entrypoint`` handles those transparently:

    "__main__"   → ("script", "main.py")
    other bare   → ("module", value)
"""

from __future__ import annotations

import json
import os
import shutil
import stat
import subprocess
import sys
from pathlib import Path

# ── Directory layout ──────────────────────────────────────────────────────────


def apps_root() -> Path:
    """Return (and create if missing) the root directory for installed apps.

    Layout::

        ~/.pyratatui/
            apps/
                <github_user>/
                    <repo>/
                        ...cloned source...
            bin/
                <repo>          ← executable wrapper
            meta/
                <github_user>__<repo>.json
    """
    root = Path.home() / ".pyratatui"
    for sub in ("apps", "bin", "meta"):
        (root / sub).mkdir(parents=True, exist_ok=True)
    return root


def app_dir(user: str, repo: str) -> Path:
    """Return the source directory for a given user/repo app."""
    return apps_root() / "apps" / user / repo


def bin_dir() -> Path:
    """Return the directory that holds executable wrappers."""
    return apps_root() / "bin"


def meta_file(user: str, repo: str) -> Path:
    """Return the path to the JSON metadata file for a given app."""
    return apps_root() / "meta" / f"{user}__{repo}.json"


# ── Metadata helpers ──────────────────────────────────────────────────────────


def write_meta(user: str, repo: str, data: dict) -> None:  # type: ignore[type-arg]
    """Persist metadata for an installed app."""
    mf = meta_file(user, repo)
    mf.write_text(json.dumps(data, indent=2), encoding="utf-8")


def read_meta(user: str, repo: str) -> dict | None:  # type: ignore[type-arg]
    """Load metadata for an installed app, or return None if absent."""
    mf = meta_file(user, repo)
    if not mf.exists():
        return None
    try:
        return json.loads(mf.read_text(encoding="utf-8"))  # type: ignore[no-any-return]
    except (json.JSONDecodeError, OSError):
        return None


def list_installed() -> list[dict]:  # type: ignore[type-arg]
    """Return a list of metadata dicts for all installed apps."""
    meta_dir = apps_root() / "meta"
    apps: list[dict] = []  # type: ignore[type-arg]
    for mf in sorted(meta_dir.glob("*.json")):
        try:
            apps.append(json.loads(mf.read_text(encoding="utf-8")))
        except (json.JSONDecodeError, OSError):
            continue
    return apps


# ── Process helpers ───────────────────────────────────────────────────────────


def run_cmd(
    args: list[str],
    cwd: Path | None = None,
    check: bool = True,
) -> subprocess.CompletedProcess:  # type: ignore[type-arg]
    """Run a subprocess, streaming output live and optionally checking returncode."""
    return subprocess.run(args, cwd=cwd, check=check, text=True)


def require_git() -> str:
    """Return the path to git, or raise RuntimeError if not found."""
    git = shutil.which("git")
    if git is None:
        raise RuntimeError(
            "git is not installed or not on PATH. " "Install git and try again."
        )
    return git


def require_python() -> str:
    """Return the current Python interpreter path."""
    return sys.executable


# ── Entrypoint encoding / decoding ────────────────────────────────────────────


def detect_entrypoint(src_dir: Path) -> str:
    """
    Return an encoded entrypoint string for the app rooted at *src_dir*.

    Format: ``"<kind>:<target>"``

    Priority:
    1. ``main.py`` at root          → ``"script:main.py"``
    2. ``<repo>/__main__.py``       → ``"module:<repo>"``
    3. ``<repo>/main.py``           → ``"module:<repo>.main"``
    4. Fallback                     → ``"script:main.py"``

    The ``script:`` kind is run as ``python main.py`` (avoids the
    ``__main__.__spec__ is None`` error that occurs with ``python -m __main__``
    on flat-layout projects in Python 3.12+).
    """
    repo = src_dir.name

    if (src_dir / "main.py").exists():
        return "script:main.py"
    if (src_dir / repo / "__main__.py").exists():
        return f"module:{repo}"
    if (src_dir / repo / "main.py").exists():
        return f"module:{repo}.main"
    return "script:main.py"


def parse_entrypoint(entrypoint: str) -> tuple[str, str]:
    """
    Decode an entrypoint string into ``(kind, target)``.

    ``kind``   is ``"script"`` or ``"module"``.
    ``target`` is the script filename or the dotted module name.

    Handles legacy bare strings written by v0.2.6 and earlier::

        "__main__"       → ("script", "main.py")
        "myapp"          → ("module", "myapp")
        "myapp.main"     → ("module", "myapp.main")
    """
    if ":" in entrypoint:
        kind, _, target = entrypoint.partition(":")
        return kind, target

    # ── Legacy bare strings ───────────────────────────────────────────────────
    if entrypoint == "__main__":
        return "script", "main.py"
    return "module", entrypoint


# ── Executable wrapper ────────────────────────────────────────────────────────


def _wrapper_script(src_dir: Path, entrypoint: str) -> str:
    """Generate the content of a POSIX shell wrapper."""
    python = require_python()
    kind, target = parse_entrypoint(entrypoint)

    if kind == "script":
        # Run the script file directly — avoids __main__.__spec__ is None.
        script = src_dir / target
        return (
            "#!/bin/sh\n"
            f'export PYTHONPATH="{src_dir}${{PYTHONPATH:+:$PYTHONPATH}}"\n'
            f'exec "{python}" "{script}" "$@"\n'
        )
    else:
        # Package with __main__.py or explicit module path.
        return (
            "#!/bin/sh\n"
            f'export PYTHONPATH="{src_dir}${{PYTHONPATH:+:$PYTHONPATH}}"\n'
            f'exec "{python}" -m "{target}" "$@"\n'
        )


def _wrapper_bat(src_dir: Path, entrypoint: str) -> str:
    """Generate the content of a Windows .bat wrapper."""
    python = require_python()
    kind, target = parse_entrypoint(entrypoint)

    if kind == "script":
        # Run the script file directly.
        script = src_dir / target
        return (
            "@echo off\n"
            f'set "PYTHONPATH={src_dir};%PYTHONPATH%"\n'
            f'"{python}" "{script}" %*\n'
        )
    else:
        return (
            "@echo off\n"
            f'set "PYTHONPATH={src_dir};%PYTHONPATH%"\n'
            f'"{python}" -m {target} %*\n'
        )


def create_wrapper(user: str, repo: str, entrypoint: str) -> Path:
    """
    Write an executable wrapper for *repo* into ``~/.pyratatui/bin/``.

    Returns the path to the created wrapper.
    """
    src_dir = app_dir(user, repo)

    if sys.platform == "win32":
        wrapper_path = bin_dir() / f"{repo}.bat"
        wrapper_path.write_text(_wrapper_bat(src_dir, entrypoint), encoding="utf-8")
    else:
        wrapper_path = bin_dir() / repo
        wrapper_path.write_text(_wrapper_script(src_dir, entrypoint), encoding="utf-8")
        wrapper_path.chmod(
            wrapper_path.stat().st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH
        )

    return wrapper_path


def remove_wrapper(repo: str) -> None:
    """Delete the executable wrapper for *repo*, if present."""
    for suffix in ("", ".bat"):
        wp = bin_dir() / f"{repo}{suffix}"
        if wp.exists():
            wp.unlink()


# ── PATH advisory ─────────────────────────────────────────────────────────────


def bin_dir_in_path() -> bool:
    """Return True if ``~/.pyratatui/bin`` is already on the user's PATH."""
    bd = str(bin_dir())
    return bd in os.environ.get("PATH", "").split(os.pathsep)


def path_advisory() -> str:
    """Return a human-readable hint about adding ``~/.pyratatui/bin`` to PATH."""
    bd = bin_dir()
    if sys.platform == "win32":
        return (
            f"\nTo run apps directly, add {bd} to your PATH:\n"
            f"  [System.Environment]::SetEnvironmentVariable('Path', "
            f"$env:Path + ';{bd}', 'User')\n"
        )
    shell_rc = "~/.bashrc"
    if "zsh" in os.environ.get("SHELL", ""):
        shell_rc = "~/.zshrc"
    return (
        f"\nTo run apps directly, add {bd} to your PATH:\n"
        f"  echo 'export PATH=\"{bd}:$PATH\"' >> {shell_rc}\n"
        f"  source {shell_rc}\n"
    )
