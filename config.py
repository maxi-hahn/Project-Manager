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
TOOLS_DIR = PROGRAMACION_ROOT / "TOOLS"
ENVIRONMENTS_DIR = PROGRAMACION_ROOT / "ENVIRONMENTS"
FEATURES_DIR = PROGRAMACION_ROOT / "FEATURES"
TECHNOLOGIES_DIR = PROGRAMACION_ROOT / "TECHNOLOGIES"


def get_resource_dirs(resources_root: Path) -> dict:
    """Returns the paths of all resources from a resources_root folder."""
    return {
        "templates": resources_root / "TEMPLATES",
        "tools": resources_root / "TOOLS",
        "features": resources_root / "FEATURES",
        "environments": resources_root / "ENVIRONMENTS",
        "technologies": resources_root / "TECHNOLOGIES",
    }