from pathlib import Path
import pytest
from src.logic.project_builder import BuildResult, build_project


def test_build_project_success(tmp_path: Path):
    template_path = tmp_path / "template"
    template_path.mkdir()
    (template_path / "README.md").write_text("# {{PROJECT_NAME}}\n{{DESCRIPTION}}")

    projects_dir = tmp_path / "projects"
    projects_dir.mkdir()

    result = build_project(
        projects_dir=projects_dir,
        template_path=template_path,
        project_name="my_test_project",
        description="Test project description",
        tools=[],
        features=[],
        environments=[],
        template_language="python",
    )

    assert isinstance(result, BuildResult)
    assert result.success is True
    assert result.project_path == projects_dir / "my_test_project"
    assert result.error_message == ""
    assert (projects_dir / "my_test_project" / "README.md").exists()


def test_build_project_file_exists_error(tmp_path: Path):
    template_path = tmp_path / "template"
    template_path.mkdir()

    projects_dir = tmp_path / "projects"
    projects_dir.mkdir()
    existing_project = projects_dir / "existing_project"
    existing_project.mkdir()

    result = build_project(
        projects_dir=projects_dir,
        template_path=template_path,
        project_name="existing_project",
        description="Description",
        tools=[],
        features=[],
        environments=[],
        template_language="python",
    )

    assert isinstance(result, BuildResult)
    assert result.success is False
    assert result.project_path is None
    assert "Ya existe un proyecto con el nombre" in result.error_message


def test_build_result_structure():
    res = BuildResult(success=True, project_path=Path("/tmp/foo"), error_message="")
    assert res.success is True
    assert res.project_path == Path("/tmp/foo")
    assert res.error_message == ""


def test_build_project_with_technologies(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr("src.project_creator.ProjectCreator._install_dependencies", lambda self, p, r: None)

    template_path = tmp_path / "template"
    template_path.mkdir()
    (template_path / "README.md").write_text("# {{PROJECT_NAME}}")

    tech_path = tmp_path / "technologies" / "sqlalchemy"
    tech_files = tech_path / "files"
    tech_files.mkdir(parents=True)
    (tech_files / "database.py").write_text("# DB config")

    projects_dir = tmp_path / "projects"
    projects_dir.mkdir()

    technology = {
        "name": "SQLAlchemy",
        "path": str(tech_path),
        "dependencies": ["sqlalchemy>=2.0.0"],
    }

    result = build_project(
        projects_dir=projects_dir,
        template_path=template_path,
        project_name="tech_test_project",
        description="Test description",
        tools=[],
        features=[],
        environments=[],
        technologies=[technology],
        template_language="python",
    )

    assert result.success is True
    project_dir = projects_dir / "tech_test_project"
    assert (project_dir / "database.py").exists()
    assert (project_dir / "requirements.txt").exists()
    assert "sqlalchemy>=2.0.0" in (project_dir / "requirements.txt").read_text()


