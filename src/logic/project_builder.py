# ============================================================
# PROJECT BUILDER LOGIC
# ============================================================
# High-level orchestration for project creation, returning
# structured results suitable for CLI or GUI interfaces.
# ============================================================

from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from src.project_creator import ProjectCreator


@dataclass
class BuildResult:
    """Result container for project creation operations."""

    success: bool
    project_path: Path | None
    error_message: str


def build_project(
    projects_dir: Path,
    template_path: Path,
    project_name: str,
    description: str,
    tools: list[dict],
    features: list[dict],
    environments: list[dict],
    template_language: str,
    template_runtime: str = "python",
    technologies: list[dict] | None = None,
    install_dependencies: bool = True,
    logger: Callable[[str], None] | None = None,
) -> BuildResult:
    """Orchestrate project creation using ProjectCreator and return a BuildResult."""
    creator = ProjectCreator(projects_dir, logger=logger)
    try:
        project_path = creator.create_project(
            template_path=template_path,
            project_name=project_name,
            description=description,
            tools=tools,
            features=features,
            environments=environments,
            template_language=template_language,
            template_runtime=template_runtime,
            technologies=technologies,
            install_dependencies=install_dependencies,
        )
        return BuildResult(
            success=True, project_path=project_path, error_message=""
        )
    except FileExistsError as error:
        return BuildResult(
            success=False, project_path=None, error_message=str(error)
        )
    except OSError as error:
        return BuildResult(
            success=False,
            project_path=None,
            error_message=f"No se pudo crear el proyecto. Detalle: {error}",
        )
    except Exception as error:
        return BuildResult(
            success=False,
            project_path=None,
            error_message=f"Error inesperado: {error}",
        )
