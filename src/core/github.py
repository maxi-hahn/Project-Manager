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

    Returns True on success (exit code 0), False otherwise.
    Never raises.
    """
    try:
        # 1. git init
        if logger:
            logger("→ Inicializando repositorio git local...")
        if not _run_git_command(["git", "init"], path, logger):
            if logger:
                logger("✗ Error al inicializar el repositorio git local.")
                logger("  El proyecto local se creó correctamente.")
            return False
        if logger:
            logger("  ✓ git init completado.")

        # 2. git add .
        if logger:
            logger("→ Preparando archivos para el commit inicial...")
        if not _run_git_command(["git", "add", "."], path, logger):
            if logger:
                logger("✗ Error al preparar los archivos.")
                logger("  El proyecto local se creó correctamente.")
            return False
        if logger:
            logger("  ✓ Archivos preparados.")

        # 3. git commit
        if logger:
            logger("→ Creando commit inicial...")
        if _run_git_command(
            ["git", "commit", "-m", "Initial commit"], path, logger
        ):
            if logger:
                logger("  ✓ Commit inicial creado.")
        else:
            if logger:
                logger(
                    "  ⚠ No se pudo crear el commit inicial. Configurá git con 'git config --global user.name' y 'user.email'."
                )

        # 4. gh repo create
        visibility_flag = "--private" if private else "--public"
        cmd = f'gh repo create "{name}" {visibility_flag} --source=. --push'

        if logger:
            logger("→ Creando repositorio en GitHub...")
            logger("  Esto puede tardar varios minutos la primera vez.")
            logger("  Se están subiendo los archivos del proyecto.")

        res = subprocess.run(
            cmd,
            cwd=path,
            capture_output=True,
            text=True,
            shell=True,
        )

        if res.stdout:
            for line in res.stdout.splitlines():
                cleaned = line.strip()
                if cleaned and logger:
                    logger(cleaned)

        if res.stderr:
            for line in res.stderr.splitlines():
                cleaned = line.strip()
                if cleaned and logger:
                    logger(cleaned)

        if res.returncode == 0:
            url = _get_repo_url(path)
            if logger:
                logger("✓ Repositorio creado y subido correctamente.")
                if url:
                    logger(f"  URL: {url}")
            return True
        else:
            if logger:
                logger("✗ No se pudo crear el repositorio en GitHub.")
                logger("  El proyecto local se creó correctamente.")
            return False

    except Exception as e:
        if logger:
            logger(f"✗ Error al ejecutar gh: {e}")
            logger("  El proyecto local se creó correctamente.")
        return False


def _run_git_command(
    args: list[str],
    cwd: Path,
    logger: Callable[[str], None] | None = None,
) -> bool:
    """Runs a git command. Returns True on success, False otherwise."""
    try:
        res = subprocess.run(
            args,
            cwd=cwd,
            capture_output=True,
            text=True,
            shell=True,
        )
        return res.returncode == 0
    except Exception:
        return False


def _get_repo_url(path: Path) -> str | None:
    """Returns the GitHub URL of the repo at `path`, or None on failure."""
    try:
        res = subprocess.run(
            "gh repo view --json url -q .url",
            cwd=path,
            capture_output=True,
            text=True,
            shell=True,
        )
        if res.returncode == 0 and res.stdout.strip():
            return res.stdout.strip()
    except Exception:
        pass
    return None
