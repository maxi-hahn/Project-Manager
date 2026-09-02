from config import TEMPLATES_DIR, PROJECTS_DIR
from src.template_manager import TemplateManager


def main():
    print("Project Manager")
    print("----------------")

    print(f"Templates: {TEMPLATES_DIR}")
    print(f"Projects: {PROJECTS_DIR}")

    print("\nAvailable templates:")

    template_manager = TemplateManager(TEMPLATES_DIR)
    templates = template_manager.discover_templates()

    if not templates:
        print("No templates found.")
        return

    for index, template in enumerate(templates, start=1):
        print(f"\n{index}. {template['name']}")
        print(f"   Language: {template['language']}")
        print(f"   Description: {template['description']}")
        print(f"   Version: {template['version']}")
        print(f"   Path: {template['path']}")


if __name__ == "__main__":
    main()