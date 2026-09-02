from pathlib import Path


# ProjectManager/
PROJECT_ROOT = Path(__file__).resolve().parent

# ProjectManager/
#     ↓
# PERSONALES/
#     ↓
# PROYECTOS/
#     ↓
# PROGRAMACION/
PROGRAMACION_ROOT = PROJECT_ROOT.parent.parent.parent

TEMPLATES_DIR = PROGRAMACION_ROOT / "TEMPLATES"
PROJECTS_DIR = PROGRAMACION_ROOT / "PROYECTOS"