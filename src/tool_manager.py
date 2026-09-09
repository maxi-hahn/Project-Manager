import json
from pathlib import Path


class ToolManager:
    def __init__(self, tools_dir: Path):
        self.tools_dir = tools_dir

    def discover_tools(self):
        tools = []

        if not self.tools_dir.exists():
            return tools

        for tool_file in self.tools_dir.rglob("tool.json"):
            try:
                with open(tool_file, "r", encoding="utf-8") as file:
                    metadata = json.load(file)

                metadata["path"] = tool_file.parent

                tools.append(metadata)

            except (json.JSONDecodeError, OSError):
                continue

        return tools