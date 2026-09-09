import shutil
import subprocess
import sys
from pathlib import Path


class ProjectCreator:

    # ========================================================
    # INICIALIZACIÓN
    # ========================================================
    # Guarda la carpeta donde se crearán los proyectos.
    # ========================================================

    def __init__(self, projects_dir: Path):
        self.projects_dir = projects_dir

    # ========================================================
    # CREAR PROYECTO
    # ========================================================
    # Coordina todo el proceso de creación:
    #
    # 1. Copiar plantilla
    # 2. Reemplazar configuración
    # 3. Crear .venv
    # 4. Ejecutar Tools
    # 5. Actualizar requirements.txt
    # 6. Verificar el entorno
    # ========================================================

    def create_project(
        self,
        template_path: Path,
        project_name: str,
        description: str,
        tools: list[dict] | None = None,
    ) -> Path:

        project_path = self.projects_dir / project_name

        if project_path.exists():
            raise FileExistsError(
                f"Ya existe un proyecto con el nombre '{project_name}'."
            )

        try:

            # ------------------------------------------------
            # 1. Copiar la plantilla
            # ------------------------------------------------

            print("\n→ Copiando plantilla...")

            shutil.copytree(template_path, project_path)

            print("✓ Plantilla copiada.")

            # ------------------------------------------------
            # 2. Reemplazar configuración
            # ------------------------------------------------

            print("→ Generando configuración...")

            self._replace_placeholders(
                project_path,
                {"{{PROJECT_NAME}}": project_name, "{{DESCRIPTION}}": description},
            )

            print("✓ Configuración generada.")

            # ------------------------------------------------
            # 3. Crear entorno virtual
            # ------------------------------------------------

            print("→ Creando entorno virtual (.venv)...")

            self._create_virtual_environment(project_path)

            print("✓ Entorno virtual creado.")

            # ------------------------------------------------
            # 4. Ejecutar Tools
            # ------------------------------------------------

            if tools:
                self._run_tools(project_path, tools)

                # --------------------------------------------
                # 5. Actualizar requirements.txt
                # --------------------------------------------

                self._update_requirements(project_path, tools)

            # ------------------------------------------------
            # 6. Verificar entorno virtual
            # ------------------------------------------------

            print("→ Verificando entorno virtual...")

            self._run_command(
                project_path,
                [str(project_path / ".venv" / "Scripts" / "python.exe"), "--version"],
            )

            print("✓ Entorno virtual verificado.")

        except OSError:

            # Si algo falla, eliminamos el proyecto incompleto.
            if project_path.exists():
                shutil.rmtree(project_path)

            raise

        return project_path

    # ========================================================
    # CREAR ENTORNO VIRTUAL
    # ========================================================
    # Crea el entorno .venv utilizando el mismo Python que
    # está ejecutando Project Manager.
    # ========================================================

    def _create_virtual_environment(self, project_path: Path):

        subprocess.run(
            [sys.executable, "-m", "venv", str(project_path / ".venv")], check=True
        )

    # ========================================================
    # EJECUTAR TOOLS
    # ========================================================
    # Recorre las Tools seleccionadas y ejecuta los comandos
    # definidos en sus respectivos archivos tool.json.
    # ========================================================

    def _run_tools(self, project_path: Path, tools: list[dict]):

        for tool in tools:

            print(f"→ Instalando/configurando {tool['name']}...")

            # Copiar archivos de configuración si existen
            self._copy_tool_files(project_path, tool)

            # Ejecutar comandos de la Tool
            for action in tool.get("commands", []):

                self._run_command(project_path, action["command"])

            print(f"✓ {tool['name']} configurado.")

    # ========================================================
    # COPIAR ARCHIVOS DE CONFIGURACIÓN DE TOOLS
    # ========================================================
    # Copia los archivos de configuración que cada Tool
    # puede incluir en su carpeta files/.
    #
    # Por ejemplo:
    #
    # TOOLS/PYTHON/RUFF/files/.ruff.toml
    #
    # se copia al proyecto como:
    #
    # proyecto/.ruff.toml
    # ========================================================

    def _copy_tool_files(self, project_path: Path, tool: dict):

        tool_path = Path(tool.get("path", ""))
        files_dir = tool_path / "files"

        if not files_dir.exists():
            return

        print(f"→ Copiando archivos de {tool['name']}...")

        for file_path in files_dir.rglob("*"):

            if file_path.is_file():

                # Calcular ruta relativa al files/
                relative_path = file_path.relative_to(files_dir)
                destination = project_path / relative_path

                # Crear directorio destino si no existe
                destination.parent.mkdir(parents=True, exist_ok=True)

                shutil.copy2(file_path, destination)
                print(f"  + {relative_path}")

        print(f"✓ Archivos de {tool['name']} copiados.")

    # ========================================================
    # EJECUTAR UN COMANDO
    # ========================================================
    # Ejecuta comandos utilizando el Python del .venv.
    #
    # Por ejemplo:
    #
    # ["python", "-m", "pip", "install", "pytest"]
    #
    # utiliza automáticamente:
    #
    # .venv/Scripts/python.exe
    #
    # De esta forma las dependencias se instalan dentro del
    # entorno virtual del proyecto.
    # ========================================================

    def _run_command(self, project_path: Path, command: list[str]):

        venv_python = project_path / ".venv" / "Scripts" / "python.exe"

        command = [
            str(venv_python) if argument == "python" else argument
            for argument in command
        ]

        subprocess.run(command, cwd=project_path, check=True)

    # ========================================================
    # REEMPLAZAR PLACEHOLDERS
    # ========================================================
    # Recorre los archivos del proyecto y reemplaza valores
    # como:
    #
    # {{PROJECT_NAME}}
    # {{DESCRIPTION}}
    #
    # por los datos introducidos por el usuario.
    # ========================================================

    def _replace_placeholders(self, project_path: Path, replacements: dict[str, str]):

        for file_path in project_path.rglob("*"):

            if not file_path.is_file():
                continue

            try:
                content = file_path.read_text(encoding="utf-8")

            except UnicodeDecodeError:
                continue

            for placeholder, value in replacements.items():

                content = content.replace(placeholder, value)

            file_path.write_text(content, encoding="utf-8")

    # ========================================================
    # ACTUALIZAR REQUIREMENTS.TXT
    # ========================================================
    # Agrega las dependencias declaradas por las Tools al
    # archivo requirements.txt del proyecto.
    #
    # Esto permite que las dependencias queden documentadas
    # y sean instalables con un simple:
    #
    # pip install -r requirements.txt
    # ========================================================

    def _update_requirements(self, project_path: Path, tools: list[dict]):

        requirements_file = project_path / "requirements.txt"

        # Leer requirements.txt existente
        existing_requirements = []

        if requirements_file.exists():
            try:
                existing_requirements = requirements_file.read_text(
                    encoding="utf-8"
                ).splitlines()

            except UnicodeDecodeError:
                pass

        # Recopilar dependencias de las Tools
        new_dependencies = []

        for tool in tools:
            dependencies = tool.get("dependencies", [])
            new_dependencies.extend(dependencies)

        if not new_dependencies:
            return

        print("→ Actualizando requirements.txt...")

        # Agregar dependencias sin duplicados
        for dependency in new_dependencies:
            if dependency not in existing_requirements:
                existing_requirements.append(dependency)
                print(f"  + {dependency}")

        # Escribir requirements.txt actualizado
        requirements_file.write_text(
            "\n".join(existing_requirements) + "\n", encoding="utf-8"
        )

        print("✓ requirements.txt actualizado.")
