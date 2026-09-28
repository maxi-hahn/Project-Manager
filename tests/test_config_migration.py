import json
import tempfile
import unittest
from pathlib import Path

from src.core.config_manager import ConfigManager


class TestConfigMigration(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.config_dir = Path(self.temp_dir.name) / ".project_manager"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.config_file = self.config_dir / "config.json"

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_legacy_default_editor_migration(self):
        legacy_data = {
            "user_name": "Test User",
            "projects_root": "/tmp/projects",
            "resources_root": "/tmp/resources",
            "default_location": "ACTIVOS",
            "default_editor": "pycharm",
            "auto_install_dependencies": True,
        }
        self.config_file.write_text(json.dumps(legacy_data), encoding="utf-8")

        cm = ConfigManager()
        cm.config_path = self.config_file
        loaded = cm.load()

        self.assertTrue(loaded)
        self.assertEqual(cm.get("editors"), ["pycharm"])
        self.assertEqual(cm.get("custom_editors"), [])
        self.assertIsNone(cm.get("default_editor"))

        # Verify persisted file on disk
        disk_data = json.loads(self.config_file.read_text(encoding="utf-8"))
        self.assertEqual(disk_data.get("editors"), ["pycharm"])
        self.assertNotIn("default_editor", disk_data)

    def test_legacy_default_editor_none_migration(self):
        legacy_data = {
            "user_name": "Test User",
            "default_editor": "none",
        }
        self.config_file.write_text(json.dumps(legacy_data), encoding="utf-8")

        cm = ConfigManager()
        cm.config_path = self.config_file
        cm.load()

        self.assertEqual(cm.get("editors"), [])
        self.assertNotIn("default_editor", cm.config)

    def test_editors_precedence_over_default_editor(self):
        data = {
            "user_name": "Test User",
            "default_editor": "vscode",
            "editors": ["pycharm", "cursor"],
        }
        self.config_file.write_text(json.dumps(data), encoding="utf-8")

        cm = ConfigManager()
        cm.config_path = self.config_file
        cm.load()

        # Requirement 6: "editors" list takes precedence over default_editor
        self.assertEqual(cm.get("editors"), ["pycharm", "cursor"])
        self.assertNotIn("default_editor", cm.config)


if __name__ == "__main__":
    unittest.main()
