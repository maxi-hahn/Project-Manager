from config import TEMPLATES_DIR, PROJECTS_DIR
from src.template_manager import TemplateManager


def main():
    print("Project Manager")
    print("----------------")

    print(f"Plantillas: {TEMPLATES_DIR}")
    print(f"Proyectos: {PROJECTS_DIR}")

    print("\nPlantillas disponibles:")

    template_manager = TemplateManager(TEMPLATES_DIR)
    templates = template_manager.discover_templates()

    if not templates:
        print("No se encontraron plantillas.")
        return

    for index, template in enumerate(templates, start=1):
        print(f"\n{index}. {template['name']}")
        print(f"   Lenguaje: {template['language']}")
        print(f"   Descripción: {template['description']}")
        print(f"   Versión: {template['version']}")
        print(f"   Ruta: {template['path']}")


if __name__ == "__main__":
    main()