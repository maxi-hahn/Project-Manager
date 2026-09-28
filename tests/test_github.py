from unittest.mock import MagicMock, patch
from pathlib import Path
from src.core.github import (
    is_gh_available,
    is_gh_authenticated,
    is_gh_ready,
    create_repository,
)


def test_is_gh_available():
    with patch("shutil.which", return_value="/usr/bin/gh"):
        assert is_gh_available() is True
    with patch("shutil.which", return_value=None):
        assert is_gh_available() is False


def test_is_gh_authenticated():
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0)
        assert is_gh_authenticated() is True

        mock_run.return_value = MagicMock(returncode=1)
        assert is_gh_authenticated() is False


def test_is_gh_ready():
    with patch("src.core.github.is_gh_available", return_value=True), patch(
        "src.core.github.is_gh_authenticated", return_value=True
    ):
        assert is_gh_ready() is True

    with patch("src.core.github.is_gh_available", return_value=False), patch(
        "src.core.github.is_gh_authenticated", return_value=True
    ):
        assert is_gh_ready() is False


def test_create_repository_success():
    logs = []
    logger = lambda msg: logs.append(msg)

    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="Creating repository...\n✓ Created repository on GitHub\n",
            stderr="",
        )
        res = create_repository(
            name="test-repo",
            path=Path("/tmp/test"),
            private=True,
            logger=logger,
        )
        assert res is True
        assert "Creating repository..." in logs
        assert "✓ Created repository on GitHub" in logs
        mock_run.assert_called_once()
        args, kwargs = mock_run.call_args
        assert 'gh repo create "test-repo" --private --source=. --push' in args[0]
        assert kwargs["cwd"] == Path("/tmp/test")


def test_create_repository_failure():
    logs = []
    logger = lambda msg: logs.append(msg)

    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(
            returncode=1,
            stdout="",
            stderr="GraphQL: Name already exists (createRepository)\n",
        )
        res = create_repository(
            name="test-repo",
            path=Path("/tmp/test"),
            private=False,
            logger=logger,
        )
        assert res is False
        assert "GraphQL: Name already exists (createRepository)" in logs
        args, kwargs = mock_run.call_args
        assert 'gh repo create "test-repo" --public --source=. --push' in args[0]


def test_create_repository_exception():
    logs = []
    logger = lambda msg: logs.append(msg)

    with patch("subprocess.run", side_effect=OSError("Command not found")):
        res = create_repository(
            name="test-repo",
            path=Path("/tmp/test"),
            private=True,
            logger=logger,
        )
        assert res is False
        assert any("Error al ejecutar gh" in line for line in logs)
