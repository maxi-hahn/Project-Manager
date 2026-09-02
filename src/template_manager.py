import json
from pathlib import Path


class TemplateManager:
    def __init__(self, templates_dir: Path):
        self.templates_dir = templates_dir

    def discover_templates(self):
        templates = []

        if not self.templates_dir.exists():
            return templates

        for template_file in self.templates_dir.rglob("template.json"):
            try:
                with open(template_file, "r", encoding="utf-8") as file:
                    metadata = json.load(file)

                metadata["path"] = template_file.parent

                templates.append(metadata)

            except (json.JSONDecodeError, OSError):
                continue

        return templates