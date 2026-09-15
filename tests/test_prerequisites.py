from unittest.mock import patch
import pytest

from src.logic.prerequisites import (
    PREREQUISITE_MESSAGES,
    check_command,
    check_prerequisites,
)


def test_check_command_existing():
    """Test check_command returns True when command is found in system PATH."""
    with patch("shutil.which", return_value="/usr/bin/node"):
        assert check_command("node") is True


def test_check_command_non_existent():
    """Test check_command returns False when command is not found in system PATH."""
    with patch("shutil.which", return_value=None):
        assert check_command("this_does_not_exist_xyz") is False


def test_check_prerequisites_all_available():
    """Test check_prerequisites returns an empty list when all required commands exist."""
    with patch("shutil.which", side_effect=lambda cmd: f"/usr/bin/{cmd}"):
        missing = check_prerequisites(["node", "npm"])
        assert missing == []


def test_check_prerequisites_some_missing():
    """Test check_prerequisites returns only missing commands."""
    def mock_which(cmd: str) -> str | None:
        if cmd == "node":
            return "/usr/bin/node"
        return None

    with patch("shutil.which", side_effect=mock_which):
        missing = check_prerequisites(["node", "npm", "git"])
        assert missing == ["npm", "git"]


def test_check_prerequisites_empty_list():
    """Test check_prerequisites returns an empty list when input list is empty."""
    assert check_prerequisites([]) == []
