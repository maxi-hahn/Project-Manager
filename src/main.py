from config import (
    TEMPLATES_DIR,
    PROJECTS_DIR,
    TOOLS_DIR,
    FEATURES_DIR,
    ENVIRONMENTS_DIR,
)

from src.template_manager import TemplateManager
from src.resource_manager import ResourceManager
from src.logic.filters import (
    filter_features_by_template,
    filter_environments_by_template,
    filter_tools_by_language,
)
from src.logic.validators import (
    validate_project_name,
    validate_required_field,
)
from src.logic.prerequisites import check_prerequisites, PREREQUISITE_MESSAGES
from src.logic.project_builder import build_project

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
    # Check template prerequisites
    # (TEMPORARY: CLI visual feedback, will be removed when GUI is implemented)
    # --------------------------------------------------------

    requires = selected_template.get("requires", [])
    if requires:
        print("\n→ Verificando prerrequisitos...")
        missing_prerequisites = check_prerequisites(requires)
        if missing_prerequisites:
            print("\nNo se puede crear el proyecto. Faltan los siguientes requisitos:\n")
            for req in missing_prerequisites:
                description = PREREQUISITE_MESSAGES.get(req)
                if description:
                    print(f"  - {req}: {description}\n")
                else:
                    print(f"  - {req}\n")
            print("  Instalá los requisitos faltantes y volvé a intentarlo.")
            return

        print("✓ Todos los prerrequisitos están disponibles.")

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
    template_language = selected_template.get("language", "")
    tools = filter_tools_by_language(tools, template_language)
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
    compatible_features = filter_features_by_template(features, selected_template)
    if template_language:
        target_lang = template_language.lower()
        compatible_features = [
            f
            for f in compatible_features
            if "language" not in f
            or not f["language"]
            or f["language"].lower() == target_lang
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
    # Buscar Environments disponibles
    # --------------------------------------------------------
    # Los Environments definen cómo se ejecuta el proyecto.
    # Solo se muestran los compatibles con el template.
    # --------------------------------------------------------

    env_manager = ResourceManager(ENVIRONMENTS_DIR, "environment.json")
    environments = env_manager.discover()

    # Filtrar por compatibilidad con el template
    compatible_environments = filter_environments_by_template(
        environments, selected_template
    )
    if template_language:
        target_lang = template_language.lower()
        compatible_environments = [
            env
            for env in compatible_environments
            if "language" not in env
            or not env["language"]
            or env["language"].lower() == target_lang
        ]

    selected_environments = []

    if compatible_environments:
        print("\nEnvironments disponibles:")

        for index, env in enumerate(compatible_environments, start=1):
            print(f"{index}. {env['name']}")
            print(f"   {env['description']}")

        print("0. Ninguno")

        while True:
            option = input("\nSeleccioná un environment (0 para continuar): ").strip()

            if option == "0":
                break

            try:
                option = int(option)

                if 1 <= option <= len(compatible_environments):
                    env = compatible_environments[option - 1]

                    if env not in selected_environments:
                        selected_environments.append(env)
                        print(f"✓ {env['name']} seleccionado.")
                    else:
                        print("Ese environment ya fue seleccionado.")

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

    result = build_project(
            projects_dir=project_location,
            template_path=selected_template["path"],
            project_name=project_name,
            description=description,
            tools=selected_tools,
            features=selected_features,
            environments=selected_environments,
            template_language=selected_template.get("language", "").lower(),
            template_runtime=selected_template.get("runtime", "python").lower(),
        )

    if result.success:
        print("\n¡Proyecto creado correctamente!")
        print(f"Ruta: {result.project_path}")
    else:
        print(f"\n{result.error_message}")


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

        is_valid, error_message = validate_project_name(project_name)
        if not is_valid:
            print(error_message)
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

        is_valid, err = validate_required_field(value, error_message)
        if not is_valid:
            print(err)
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
