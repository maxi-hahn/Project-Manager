import shutil
import subprocess
from pathlib import Path
from typing import Callable


def is_gh_available() -> bool:
    """Returns True if `gh` is in PATH."""
    return shutil.which("gh") is not None


def is_gh_authenticated() -> bool:
    """Returns True if `gh auth status` returns exit code 0."""
    try:
        res = subprocess.run(
            "gh auth status",
            capture_output=True,
            text=True,
            shell=True,
        )
        return res.returncode == 0
    except Exception:
        return False


def is_gh_ready() -> bool:
    """Returns True if gh is available AND authenticated."""
    return is_gh_available() and is_gh_authenticated()


def create_repository(
    name: str,
    path: Path,
    private: bool = True,
    logger: Callable[[str], None] | None = None,
) -> bool:
    """
    Runs `gh repo create <name> --<private|public> --source=. --push`
    inside the project directory.

    Uses subprocess.run with capture_output=True, text=True, shell=True.
    Logs the output via logger (if provided) as individual lines.

    Returns True on success (exit code 0), False otherwise.
    Never raises.
    """
    visibility_flag = "--private" if private else "--public"
    cmd = f'gh repo create "{name}" {visibility_flag} --source=. --push'

    try:
        res = subprocess.run(
            cmd,
            cwd=path,
            capture_output=True,
            text=True,
            shell=True,
        )

        if logger:
            if res.stdout:
                for line in res.stdout.splitlines():
                    cleaned = line.strip()
                    if cleaned:
                        logger(cleaned)
            if res.stderr:
                for line in res.stderr.splitlines():
                    cleaned = line.strip()
                    if cleaned:
                        logger(cleaned)

        return res.returncode == 0
    except Exception as e:
        if logger:
            logger(f"Error al ejecutar gh: {e}")
        return False
