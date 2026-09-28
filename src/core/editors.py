import shutil
import subprocess

KNOWN_EDITORS = [
    {"key": "vscode", "name": "VS Code", "command": "code"},
    {"key": "cursor", "name": "Cursor", "command": "cursor"},
    {"key": "visualstudio", "name": "Visual Studio", "command": "devenv"},
    {"key": "pycharm", "name": "PyCharm", "command": "pycharm"},
    {"key": "webstorm", "name": "WebStorm", "command": "webstorm"},
    {"key": "intellij", "name": "IntelliJ IDEA", "command": "idea"},
    {"key": "sublime", "name": "Sublime Text", "command": "subl"},
    {"key": "notepadpp", "name": "Notepad++", "command": "notepad++"},
    {"key": "vim", "name": "Vim", "command": "vim"},
    {"key": "neovim", "name": "Neovim", "command": "nvim"},
]

_INSTRUCTIONS = {
    "vscode": "Viene habilitado por defecto. Si no funciona, reinstalá marcando 'Add to PATH'.",
    "cursor": "Viene habilitado por defecto.",
    "visualstudio": "Abrí Visual Studio Installer, modificá tu instalación y marcá 'Desktop development with C++'.",
    "pycharm": "Abrí PyCharm. Menú Tools → Create Command-line Launcher. Aceptá la ruta por defecto y reiniciá la terminal.",
    "webstorm": "Igual que PyCharm: Tools → Create Command-line Launcher.",
    "intellij": "Igual que PyCharm: Tools → Create Command-line Launcher.",
    "sublime": "Agregá la carpeta de instalación de Sublime al PATH del sistema.",
    "notepadpp": "Generalmente ya está en PATH. Si no, agregá la carpeta de instalación al PATH.",
    "vim": "Disponible si Vim está instalado.",
    "neovim": "Disponible si Neovim está instalado.",
}


def is_available(command: str) -> bool:
    """Returns True if the command is in PATH (uses shutil.which)."""
    if not command:
        return False
    return shutil.which(command) is not None


def get_available_known_editors() -> list[dict]:
    """
    Returns the subset of KNOWN_EDITORS whose command is available.
    Each item is the original dict plus {"available": True}.
    """
    available_editors = []
    for editor in KNOWN_EDITORS:
        if is_available(editor["command"]):
            editor_copy = editor.copy()
            editor_copy["available"] = True
            available_editors.append(editor_copy)
    return available_editors


def get_editor_by_key(key: str) -> dict | None:
    """Returns the known editor dict by key, or None."""
    for editor in KNOWN_EDITORS:
        if editor["key"] == key:
            return editor.copy()
    return None


def open_in_editor(command: str, path: str) -> bool:
    """
    Tries to open `path` with the given command using subprocess.Popen
    with shell=True. Returns True on success, False on failure.
    """
    if not command or not path:
        return False
    try:
        subprocess.Popen([command, str(path)], shell=True)
        return True
    except Exception:
        return False


def get_instructions() -> dict[str, str]:
    """
    Returns a dict mapping editor key to a short Spanish instruction
    string on how to enable its command-line launcher.
    """
    return _INSTRUCTIONS.copy()
