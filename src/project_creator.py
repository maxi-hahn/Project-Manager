import shutil
from pathlib import Path


class ProjectCreator:
    def __init__(self, projects_dir: Path):
        self.projects_dir = projects_dir

    def create_project(
        self,
        template_path: Path,
        project_name: str,
        description: str,
        author: str,
        version: str
    ) -> Path:
        project_path = self.projects_dir / project_name

        if project_path.exists():
            raise FileExistsError(
                f"Ya existe un proyecto con el nombre '{project_name}'."
            )

        shutil.copytree(template_path, project_path)

        self._replace_placeholders(
            project_path,
            {
                "{{PROJECT_NAME}}": project_name,
                "{{DESCRIPTION}}": description,
                "{{AUTHOR}}": author,
                "{{VERSION}}": version
            }
        )

        return project_path

    def _replace_placeholders(
        self,
        project_path: Path,
        replacements: dict[str, str]
    ):
        for file_path in project_path.rglob("*"):
            if not file_path.is_file():
                continue

            try:
                content = file_path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue

            for placeholder, value in replacements.items():
                content = content.replace(placeholder, value)

            file_path.write_text(content, encoding="utf-8")