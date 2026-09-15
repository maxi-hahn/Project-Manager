# ============================================================
# PREREQUISITES LOGIC
# ============================================================
# Pure logic functions for checking system prerequisite commands.
# ============================================================

import shutil

# Messages for missing prerequisite commands
PREREQUISITE_MESSAGES = {
    "node": "Node.js es necesario para proyectos de JavaScript/React. Descargalo en https://nodejs.org/",
    "npm": "npm es necesario para instalar dependencias de JavaScript. Se instala junto con Node.js.",
}


def check_command(command: str) -> bool:
    """
    Returns True if the given command is available in the system PATH.
    Uses shutil.which().
    """
    return shutil.which(command) is not None


def check_prerequisites(requires: list[str]) -> list[str]:
    """
    Given a list of required commands (e.g. ["node", "npm"]),
    returns a list of the ones that are MISSING.
    Empty list means all are available.
    """
    return [command for command in requires if not check_command(command)]
