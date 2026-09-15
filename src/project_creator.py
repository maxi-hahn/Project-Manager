import os
import shutil
import subprocess
import sys
from pathlib import Path

# Directories to skip during placeholder replacement (e.g. dependencies, build artifacts, venvs)
SKIP_DIRECTORIES = {
    "node_modules",
    ".venv",
    "venv",
    "env",
    ".git",
    "dist",
    "build",
    "__pycache__",
}


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
        features: list[dict] | None = None,
        environments: list[dict] | None = None,
        template_language: str = "",
        template_runtime: str = "python",
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

            shutil.copytree(
                template_path,
                project_path,
                ignore=shutil.ignore_patterns("template.json")
            )

            print("✓ Plantilla copiada.")

                        # ------------------------------------------------
            # 2. Configurar runtime (varía según el lenguaje)
            # ------------------------------------------------

            if template_runtime == "python":
                self._setup_python_runtime(project_path, tools)
            elif template_runtime == "node":
                self._setup_node_runtime(project_path)
            else:
                print(f"→ Runtime '{template_runtime}' sin configuración específica.")

            # ------------------------------------------------
            # 3. Ejecutar Tools
            # ------------------------------------------------

            if tools:
                self._run_tools(project_path, tools)

            # ------------------------------------------------
            # 4. Copiar Features
            # ------------------------------------------------

            if features:
                self._run_features(project_path, features)

            # ------------------------------------------------
            # 5. Copiar Environments
            # ------------------------------------------------

            if environments:
                self._run_environments(
                    project_path,
                    environments,
                    template_language,
                )

            # ------------------------------------------------
            # 6. Reemplazar placeholders (después de copiar todo)
            # ------------------------------------------------

            print("→ Generando configuración...")

            self._replace_placeholders(
                project_path,
                {"{{PROJECT_NAME}}": project_name, "{{DESCRIPTION}}": description},
            )

            print("✓ Configuración generada.")

            # ------------------------------------------------
            # 7. Actualizar requirements.txt (solo Python)
            # ------------------------------------------------

            if template_runtime == "python" and tools:
                self._update_requirements(project_path, tools)

        except (OSError, subprocess.CalledProcessError):

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
    # CONFIGURAR RUNTIME PYTHON
    # ========================================================
    # Pasos específicos para proyectos Python:
    #   1. Crear .venv
    #   2. Instalar dependencias del template
    #   3. Verificar el entorno
    # ========================================================

    def _setup_python_runtime(self, project_path: Path, tools: list[dict] | None):

        # ------------------------------------------------
        # 1. Crear entorno virtual
        # ------------------------------------------------

        print("→ Creando entorno virtual (.venv)...")

        self._create_virtual_environment(project_path)

        print("✓ Entorno virtual creado.")

        # ------------------------------------------------
        # 2. Instalar dependencias del template
        # ------------------------------------------------

        self._install_template_dependencies(project_path)

        # ------------------------------------------------
        # 3. Verificar entorno virtual
        # ------------------------------------------------

        print("→ Verificando entorno virtual...")

        self._run_command(
            project_path,
            [str(project_path / ".venv" / "Scripts" / "python.exe"), "--version"],
        )

        print("✓ Entorno virtual verificado.")

    # ========================================================
    # CONFIGURAR RUNTIME NODE
    # ========================================================
    # Pasos específicos para proyectos Node/JavaScript:
    #   1. Ejecutar npm install
    #
    # No se crea .venv porque Node usa node_modules/.
    # ========================================================

    def _setup_node_runtime(self, project_path: Path):

        # ------------------------------------------------
        # 1. Instalar dependencias con npm
        # ------------------------------------------------

        print("→ Instalando dependencias con npm...")
        print("  (esto puede tardar unos minutos la primera vez)")

        subprocess.run(
            ["npm", "install"],
            cwd=project_path,
            check=True,
            shell=True,  # Necesario en Windows para encontrar npm
        )

        print("✓ Dependencias instaladas.")



    # ========================================================
    # INSTALAR DEPENDENCIAS DEL TEMPLATE
    # ========================================================
    # Instala las dependencias declaradas en el archivo
    # requirements.txt del template dentro del .venv.
    #
    # Esto deja el proyecto listo para ejecutarse sin que
    # el usuario tenga que instalar nada manualmente.
    # ========================================================

    def _install_template_dependencies(self, project_path: Path):

        requirements_file = project_path / "requirements.txt"

        if not requirements_file.exists():
            return

        # Verificar que el archivo tenga contenido real
        content = requirements_file.read_text(encoding="utf-8").strip()

        if not content:
            return

        print("→ Instalando dependencias del template...")

        self._run_command(
            project_path,
            ["python", "-m", "pip", "install", "-r", "requirements.txt"],
        )

        print("✓ Dependencias del template instaladas.")

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
    # EJECUTAR FEATURES
    # ========================================================
    # Copia los archivos de cada Feature seleccionada.
    #
    # A diferencia de las Tools, las Features solo copian
    # archivos. No instalan ni ejecutan comandos (por ahora).
    # ========================================================

    def _run_features(self, project_path: Path, features: list[dict]):

        for feature in features:

            print(f"→ Copiando feature {feature['name']}...")

            self._copy_tool_files(project_path, feature) # No es un error, reutilizamos copy_TOOL por que hace lo mismo, en un futuro puede llegar a cambiar 

            print(f"✓ {feature['name']} copiada.")


        # ========================================================
    # EJECUTAR ENVIRONMENTS
    # ========================================================
    # Copia los archivos de cada Environment seleccionado.
    #
    # Algunos archivos son genéricos (docker-compose.yml) y
    # otros son específicos por lenguaje (Dockerfile).
    #
    # El campo files_by_language indica qué archivo copiar
    # según el lenguaje del template seleccionado.
    # ========================================================

    def _run_environments(
        self,
        project_path: Path,
        environments: list[dict],
        template_language: str,
    ):

        for env in environments:

            print(f"→ Configurando {env['name']}...")

            env_path = Path(env.get("path", ""))

            # ------------------------------------------------
            # Copiar archivos genéricos (files/)
            # ------------------------------------------------

            self._copy_tool_files(project_path, env)

            # ------------------------------------------------
            # Copiar archivos específicos por lenguaje
            # ------------------------------------------------

            files_by_language = env.get("files_by_language", {})
            language_file = files_by_language.get(template_language)

            if language_file:

                source = env_path / language_file

                if source.exists():

                    destination = project_path / Path(language_file).name

                    destination.parent.mkdir(parents=True, exist_ok=True)

                    shutil.copy2(source, destination)

                    print(f"  + {destination.name}")

            print(f"✓ {env['name']} configurado.")

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

        # Skip heavy dependency, build, and version control directories to avoid scanning thousands of unnecessary files
        for root, dirs, files in os.walk(project_path):
            dirs[:] = [d for d in dirs if d not in SKIP_DIRECTORIES]

            for file_name in files:
                file_path = Path(root) / file_name

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
