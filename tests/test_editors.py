import unittest
from unittest.mock import patch

from src.core.editors import (
    KNOWN_EDITORS,
    get_available_known_editors,
    get_editor_by_key,
    get_instructions,
    is_available,
    open_in_editor,
)


class TestEditorsModule(unittest.TestCase):
    def test_known_editors_structure(self):
        self.assertIsInstance(KNOWN_EDITORS, list)
        self.assertGreater(len(KNOWN_EDITORS), 0)
        for ed in KNOWN_EDITORS:
            self.assertIn("key", ed)
            self.assertIn("name", ed)
            self.assertIn("command", ed)

    def test_get_editor_by_key(self):
        vscode = get_editor_by_key("vscode")
        self.assertIsNotNone(vscode)
        self.assertEqual(vscode["name"], "VS Code")
        self.assertEqual(vscode["command"], "code")

        unknown = get_editor_by_key("unknown_editor")
        self.assertIsNone(unknown)

    @patch("shutil.which")
    def test_is_available(self, mock_which):
        mock_which.side_effect = lambda cmd: "/usr/bin/code" if cmd == "code" else None
        self.assertTrue(is_available("code"))
        self.assertFalse(is_available("nonexistent_cmd"))
        self.assertFalse(is_available(""))

    @patch("shutil.which")
    def test_get_available_known_editors(self, mock_which):
        mock_which.side_effect = lambda cmd: "/usr/bin/" + cmd if cmd in ["code", "cursor"] else None
        available = get_available_known_editors()
        keys = [ed["key"] for ed in available]
        self.assertIn("vscode", keys)
        self.assertIn("cursor", keys)
        self.assertNotIn("pycharm", keys)
        for ed in available:
            self.assertTrue(ed.get("available"))

    @patch("subprocess.Popen")
    def test_open_in_editor_success(self, mock_popen):
        res = open_in_editor("code", "/path/to/proj")
        self.assertTrue(res)
        mock_popen.assert_called_once_with(["code", "/path/to/proj"], shell=True)

    @patch("subprocess.Popen", side_effect=Exception("Failed to spawn"))
    def test_open_in_editor_failure(self, mock_popen):
        res = open_in_editor("code", "/path/to/proj")
        self.assertFalse(res)

    def test_get_instructions(self):
        instructions = get_instructions()
        self.assertIsInstance(instructions, dict)
        self.assertIn("vscode", instructions)
        self.assertIn("pycharm", instructions)


if __name__ == "__main__":
    unittest.main()
