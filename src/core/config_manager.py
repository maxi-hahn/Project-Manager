import json
from pathlib import Path


class ConfigManager:
    CONFIG_DIR_NAME = ".project_manager"
    CONFIG_FILE_NAME = "config.json"

    DEFAULT_CONFIG = {
        "user_name": "",
        "projects_root": "",
        "resources_root": "",
        "default_location": "",
        "default_editor": "vscode",
        "auto_install_dependencies": True,
    }

    def __init__(self):
        self.config_path = Path.home() / self.CONFIG_DIR_NAME / self.CONFIG_FILE_NAME
        self.config: dict = {}
        self.load()

    def exists(self) -> bool:
        """Check if the configuration file exists on disk."""
        return self.config_path.exists()

    def load(self) -> bool:
        """Load configuration from disk. Return True on success, False on failure or if file doesn't exist."""
        if not self.config_path.exists():
            self.config = {}
            return False

        try:
            content = self.config_path.read_text(encoding="utf-8")
            data = json.loads(content)
            if isinstance(data, dict):
                self.config = data
                return True
            else:
                self.config = {}
                return False
        except (json.JSONDecodeError, OSError):
            self.config = {}
            return False

    def save(self, config: dict | None = None) -> None:
        """Save configuration to disk. If config dictionary is provided, update self.config."""
        if config is not None:
            self.config = config

        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        self.config_path.write_text(
            json.dumps(self.config, indent=4), encoding="utf-8"
        )

    def get(self, key: str, default=None):
        """Get a configuration value by key."""
        return self.config.get(key, default)

    def set(self, key: str, value) -> None:
        """Set a configuration value and persist changes to disk."""
        self.config[key] = value
        self.save()

    def get_all(self) -> dict:
        """Get a copy of all configuration settings."""
        return self.config.copy()

    def reset(self) -> None:
        """Reset configuration to default settings and save to disk."""
        self.config = self.DEFAULT_CONFIG.copy()
        self.save()
