from config import (
    TEMPLATES_DIR,
    PROJECTS_DIR,
    TOOLS_DIR,
    FEATURES_DIR,
    # ENVIRONMENTS_DIR,
    # TECHNOLOGIES_DIR,
)

from src.template_manager import TemplateManager
from src.resource_manager import ResourceManager
from src.project_creator import ProjectCreator

# ============================================================
# MENÚ PRINCIPAL
# ============================================================
# Es el punto de entrada de la aplicación.
# Muestra las opciones disponibles y mantiene el programa
# funcionando hasta que el usuario elige salir.
# ============================================================


def main():
    while True:
        print("\nProject Manager")
        print("----------------")
        print("\n¿Qué querés hacer?")
        print("1. Crear proyecto")
        print("0. Salir")

        option = input("\nSeleccioná una opción: ").strip()

        if option == "1":
            create_project()

        elif option == "0":
            print("\nHasta luego.")
            break

        else:
            print("\nOpción no válida.")


# ============================================================
# CREACIÓN DE PROYECTOS
# ============================================================
# Esta función coordina todo el proceso:
#
# 1. Buscar plantillas
# 2. Elegir una plantilla
# 3. Buscar Tools disponibles
# 4. Elegir Tools
# 5. Elegir ubicación
# 6. Definir nombre y descripción
# 7. Pedirle a ProjectCreator que cree el proyecto
#
# La función coordina el proceso, pero no se encarga de
# copiar archivos ni ejecutar comandos directamente.
# Esa responsabilidad pertenece a ProjectCreator.
# ============================================================


def create_project():

    # --------------------------------------------------------
    # Buscar plantillas disponibles
    # --------------------------------------------------------

    template_manager = TemplateManager(TEMPLATES_DIR)
    templates = template_manager.discover_templates()

    if not templates:
        print("\nNo se encontraron plantillas.")
        return

    print("\nPlantillas disponibles:")

    for index, template in enumerate(templates, start=1):
        print(f"\n{index}. {template['name']}")
        print(f"   Lenguaje: {template['language']}")
        print(f"   Descripción: {template['description']}")
        print(f"   Versión: {template['version']}")

    # --------------------------------------------------------
    # Seleccionar plantilla
    # --------------------------------------------------------

    while True:
        option = input("\nSeleccioná una plantilla (0 para volver): ").strip()

        if option == "0":
            return

        try:
            option = int(option)

            if 1 <= option <= len(templates):
                selected_template = templates[option - 1]
                break

            print("Opción no válida.")

        except ValueError:
            print("Ingresá un número válido.")

    # --------------------------------------------------------
    # Buscar Tools disponibles
    # --------------------------------------------------------
    # Las Tools son funcionalidades adicionales que pueden
    # modificar o configurar el proyecto después de crearlo.
    #
    # Por ejemplo:
    # Pytest → instala pytest dentro del .venv.
    # --------------------------------------------------------

    tool_manager = ResourceManager(TOOLS_DIR, "tool.json")
    tools = tool_manager.discover()
    selected_tools = []

    if tools:
        print("\nTools disponibles:")

        for index, tool in enumerate(tools, start=1):
            print(f"{index}. {tool['name']}")
            print(f"   {tool['description']}")

        print("0. Ninguna")

        # ----------------------------------------------------
        # Seleccionar Tools
        # ----------------------------------------------------
        # Se pueden seleccionar varias Tools.
        # El usuario escribe 0 cuando terminó de seleccionar.
        # ----------------------------------------------------

        while True:
            option = input("\nSeleccioná una tool (0 para continuar): ").strip()

            if option == "0":
                break

            try:
                option = int(option)

                if 1 <= option <= len(tools):
                    tool = tools[option - 1]

                    if tool not in selected_tools:
                        selected_tools.append(tool)
                        print(f"✓ {tool['name']} seleccionada.")
                    else:
                        print("Esa tool ya fue seleccionada.")

                else:
                    print("Opción no válida.")

            except ValueError:
                print("Ingresá un número válido.")

    # --------------------------------------------------------
    # Buscar Features disponibles
    # --------------------------------------------------------
    # Las Features son módulos de código reutilizable que
    # se copian al proyecto. Solo se muestran las compatibles
    # con el template seleccionado.
    # --------------------------------------------------------

    feature_manager = ResourceManager(FEATURES_DIR, "feature.json")
    features = feature_manager.discover()

    # Filtrar por compatibilidad con el template
    compatible_features = [
        feature
        for feature in features
        if selected_template["name"].lower().replace(" ", "_")
        in feature.get("compatible_with", [])
    ]

    selected_features = []

    if compatible_features:
        print("\nFeatures disponibles:")

        for index, feature in enumerate(compatible_features, start=1):
            print(f"{index}. {feature['name']}")
            print(f"   {feature['description']}")

        print("0. Ninguna")

        while True:
            option = input("\nSeleccioná una feature (0 para continuar): ").strip()

            if option == "0":
                break

            try:
                option = int(option)

                if 1 <= option <= len(compatible_features):
                    feature = compatible_features[option - 1]

                    if feature not in selected_features:
                        selected_features.append(feature)
                        print(f"✓ {feature['name']} seleccionada.")
                    else:
                        print("Esa feature ya fue seleccionada.")

                else:
                    print("Opción no válida.")

            except ValueError:
                print("Ingresá un número válido.")

    # --------------------------------------------------------
    # Seleccionar ubicación del proyecto
    # --------------------------------------------------------

    project_location = select_project_location()

    if project_location is None:
        return

    # --------------------------------------------------------
    # Obtener nombre del proyecto
    # --------------------------------------------------------

    project_name = get_project_name()

    if project_name is None:
        return

    # --------------------------------------------------------
    # Obtener descripción
    # --------------------------------------------------------

    description = get_required_input(
        "\nDescripción: ", "La descripción no puede estar vacía."
    )

    if description is None:
        return

    # --------------------------------------------------------
    # Crear proyecto
    # --------------------------------------------------------
    # ProjectCreator recibe toda la información necesaria.
    # Se encarga de copiar la plantilla, reemplazar los
    # placeholders, crear el .venv y ejecutar las Tools.
    # --------------------------------------------------------

    project_creator = ProjectCreator(project_location)

    try:
        project_path = project_creator.create_project(
            template_path=selected_template["path"],
            project_name=project_name,
            description=description,
            tools=selected_tools,
            features=selected_features,
        )

        print("\n¡Proyecto creado correctamente!")
        print(f"Ruta: {project_path}")

    except FileExistsError as error:
        print(f"\n{error}")

    except OSError as error:
        print("\nNo se pudo crear el proyecto.")
        print(f"Detalle: {error}")


# ============================================================
# SELECCIONAR UBICACIÓN
# ============================================================
# Busca las carpetas existentes dentro de PROYECTOS.
#
# Por ejemplo:
#
# PROYECTOS/
# ├── ACTIVOS/
# ├── PERSONALES/
# ├── ARCHIVADOS/
# └── GITHUB/
#
# El usuario elige en cuál de ellas crear el nuevo proyecto.
# ============================================================


def select_project_location():

    locations = [folder for folder in PROJECTS_DIR.iterdir() if folder.is_dir()]

    if not locations:
        print("\nNo se encontraron ubicaciones de proyectos.")
        return None

    print("\n¿Dónde querés crear el proyecto?")

    for index, location in enumerate(locations, start=1):
        print(f"{index}. {location.name}")

    print("0. Volver")

    while True:
        option = input("\nSeleccioná una ubicación: ").strip()

        if option == "0":
            return None

        try:
            option = int(option)

            if 1 <= option <= len(locations):
                return locations[option - 1]

            print("Opción no válida.")

        except ValueError:
            print("Ingresá un número válido.")


# ============================================================
# OBTENER NOMBRE DEL PROYECTO
# ============================================================
# Valida que el nombre no esté vacío y que no contenga
# caracteres que Windows no permite en nombres de carpetas.
# ============================================================


def get_project_name():

    while True:
        project_name = input("\nNombre del proyecto (0 para volver): ").strip()

        if project_name == "0":
            return None

        if not project_name:
            print("El nombre del proyecto no puede estar vacío.")
            continue

        if any(character in project_name for character in '<>:"/\\|?*'):
            print("El nombre contiene caracteres no válidos.")
            continue

        return project_name


# ============================================================
# OBTENER DATO OBLIGATORIO
# ============================================================
# Función reutilizable para pedir información que no puede
# quedar vacía.
#
# También permite escribir 0 para cancelar y volver atrás.
# ============================================================


def get_required_input(message, error_message):

    while True:
        value = input(message).strip()

        if value == "0":
            print("\nVolviendo...")
            return None

        if not value:
            print(error_message)
            continue

        return value


# ============================================================
# INICIO DEL PROGRAMA
# ============================================================
# Python ejecuta main() solamente cuando este archivo se
# ejecuta directamente.
#
# run.py importa main() y también termina llegando a esta
# función, pero este bloque permite ejecutar main.py por sí
# mismo si alguna vez lo necesitamos.
# ============================================================

if __name__ == "__main__":
    main()
