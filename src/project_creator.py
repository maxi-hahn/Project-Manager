import json
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
        self._env_port = None
        self._pre_feature_package_json = None

    # ========================================================
    # CREAR PROYECTO
    # ========================================================
    # Coordina todo el proceso de creación:
    #
    # 1. Copiar plantilla
    # 2. Crear .venv (solo Python)
    # 3. Ejecutar Tools
    # 4. Copiar Features (+ merge package.json)
    # 5. Actualizar requirements.txt (solo Python si hay tools)
    # 6. Instalar dependencias
    # 7. Copiar Environments
    # 8. Reemplazar placeholders
    # 9. Verificar entorno virtual (solo Python)
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
        technologies: list[dict] | None = None,
    ) -> Path:

        project_path = self.projects_dir / project_name

        if project_path.exists():
            raise FileExistsError(
                f"Ya existe un proyecto con el nombre '{project_name}'."
            )

        try:

            # ------------------------------------------------
            # 1. Copy template
            # ------------------------------------------------

            print("\n→ Copiando plantilla...")

            shutil.copytree(
                template_path,
                project_path,
                ignore=shutil.ignore_patterns("template.json"),
            )

            print("✓ Plantilla copiada.")

            # ------------------------------------------------
            # 2. Create .venv (only if template_runtime == "python")
            # ------------------------------------------------

            if template_runtime == "python":
                print("→ Creando entorno virtual (.venv)...")
                self._create_virtual_environment(project_path)
                print("✓ Entorno virtual creado.")

            # ------------------------------------------------
            # 3. Run Tools
            # ------------------------------------------------

            if tools:
                self._run_tools(project_path, tools)

            # ------------------------------------------------
            # 4. Copy Features + merge package.json
            # ------------------------------------------------

            if features:
                self._run_features(project_path, features)

            # ------------------------------------------------
            # 5. Copy Technologies
            # ------------------------------------------------

            if technologies:
                self._run_technologies(project_path, technologies)

            # ------------------------------------------------
            # 6. Update requirements.txt / package.json (if tools or technologies exist)
            # ------------------------------------------------

            if tools or technologies:
                resources = (tools or []) + (technologies or [])
                if template_runtime == "python":
                    self._update_requirements(project_path, resources)
                elif template_runtime == "node":
                    self._add_node_dependencies(project_path, resources)

            # ------------------------------------------------
            # 7. Install dependencies (single step)
            # ------------------------------------------------

            self._install_dependencies(project_path, template_runtime)

            # ------------------------------------------------
            # 7. Copy Environments
            # ------------------------------------------------

            if environments:
                self._run_environments(
                    project_path,
                    environments,
                    template_language,
                )

            # ------------------------------------------------
            # Limpiar .gitkeep de carpetas con contenido
            # ------------------------------------------------

            self._cleanup_gitkeep(project_path)
            
            # ------------------------------------------------
            # 8. Replace placeholders
            # ------------------------------------------------

            print("→ Generando configuración...")

            replacements = {
                "{{PROJECT_NAME}}": project_name,
                "{{DESCRIPTION}}": description,
            }
            # Si un Environment definió un puerto, agregarlo
            if self._env_port is not None:
                replacements["{{PORT}}"] = self._env_port

            self._replace_placeholders(project_path, replacements)

            print("✓ Configuración generada.")

            # ------------------------------------------------
            # 9. Verify Python venv (only if template_runtime == "python")
            # ------------------------------------------------

            if template_runtime == "python":
                self._verify_virtual_environment(project_path)

        except (OSError, subprocess.CalledProcessError):

            # Si algo falla, eliminamos el proyecto incompleto.
            if project_path.exists():
                shutil.rmtree(project_path)

            raise

        # Resetear estado para el próximo proyecto
        self._env_port = None
        self._pre_feature_package_json = None

        return project_path

    # ========================================================
    # CREAR ENTORNO VIRTUAL
    # ========================================================
    # Crea el entorno .venv utilizando el mismo Python que
    # está ejecutando Project Manager.
    # ========================================================

    def _create_virtual_environment(self, project_path: Path) -> None:

        subprocess.run(
            [sys.executable, "-m", "venv", str(project_path / ".venv")], check=True
        )

    # ========================================================
    # VERIFICAR ENTORNO VIRTUAL
    # ========================================================
    # Comprueba que el entorno virtual Python funciona.
    # ========================================================

    def _verify_virtual_environment(self, project_path: Path) -> None:

        print("→ Verificando entorno virtual...")

        self._run_command(
            project_path,
            [str(project_path / ".venv" / "Scripts" / "python.exe"), "--version"],
        )

        print("✓ Entorno virtual verificado.")

    # ========================================================
    # INSTALAR DEPENDENCIAS
    # ========================================================
    # Instala todas las dependencias del proyecto al final.
    # ========================================================

    def _install_dependencies(self, project_path: Path, template_runtime: str) -> None:

        if template_runtime == "python":
            requirements_file = project_path / "requirements.txt"

            if not requirements_file.exists():
                return

            content = requirements_file.read_text(encoding="utf-8").strip()

            if not content:
                return

            print("→ Instalando dependencias...")

            self._run_command(
                project_path,
                ["python", "-m", "pip", "install", "-r", "requirements.txt"],
            )

            print("✓ Dependencias instaladas.")

        elif template_runtime == "node":
            print("→ Instalando dependencias (npm install)...")
            print("  (esto puede tardar unos minutos la primera vez)")

            subprocess.run(
                ["npm", "install"],
                cwd=project_path,
                check=True,
                shell=True,  # Necesario en Windows para encontrar npm
            )

            print("✓ Dependencias instaladas.")

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
    # Copia los archivos de cada Feature seleccionada y
    # fusiona package.json si la Feature contiene uno.
    # ========================================================

    def _run_features(self, project_path: Path, features: list[dict]):

        for feature in features:

            print(f"→ Copiando feature {feature['name']}...")

            # Backup pre-existing package.json before copying feature files
            project_pkg = project_path / "package.json"
            self._pre_feature_package_json = None
            if project_pkg.exists():
                try:
                    self._pre_feature_package_json = json.loads(
                        project_pkg.read_text(encoding="utf-8")
                    )
                except (json.JSONDecodeError, OSError):
                    self._pre_feature_package_json = None

            self._copy_tool_files(project_path, feature)

            feature_pkg = Path(feature.get("path", "")) / "files" / "package.json"
            if feature_pkg.exists():
                self._merge_package_json(project_path, feature)

            self._pre_feature_package_json = None

            print(f"✓ {feature['name']} copiada.")

    # ========================================================
    # EJECUTAR TECHNOLOGIES
    # ========================================================
    # Copia los archivos de cada Tecnología seleccionada.
    # ========================================================

    def _run_technologies(self, project_path: Path, technologies: list[dict]) -> None:

        for tech in technologies:

            print(f"→ Copiando tecnología {tech['name']}...")

            self._copy_tool_files(project_path, tech)

            print(f"✓ {tech['name']} copiada.")

    # ========================================================
    # FUSIONAR PACKAGE.JSON
    # ========================================================
    # Fusiona dependencias y devDependencies de una Feature
    # en el package.json del proyecto.
    # ========================================================

    def _merge_package_json(self, project_path: Path, feature: dict) -> None:

        feature_pkg_file = Path(feature.get("path", "")) / "files" / "package.json"

        if not feature_pkg_file.exists():
            return

        project_pkg_file = project_path / "package.json"

        # Read project's package.json
        project_data = None
        if getattr(self, "_pre_feature_package_json", None) is not None:
            project_data = self._pre_feature_package_json
        elif project_pkg_file.exists():
            try:
                project_data = json.loads(project_pkg_file.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                project_data = None

        # Delete feature's package.json copied to project if project has no package.json
        if project_data is None:
            if project_pkg_file.exists():
                try:
                    project_pkg_file.unlink()
                except OSError:
                    pass
            return

        # Read feature's package.json
        try:
            feature_data = json.loads(feature_pkg_file.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return

        # Merge dependencies and devDependencies (project values take precedence)
        added_deps = []

        for dep_type in ["dependencies", "devDependencies"]:
            project_deps = project_data.get(dep_type)
            if not isinstance(project_deps, dict):
                project_deps = {}
                project_data[dep_type] = project_deps

            feature_deps = feature_data.get(dep_type, {})
            if isinstance(feature_deps, dict):
                for dep_name, dep_version in feature_deps.items():
                    if dep_name not in project_deps:
                        project_deps[dep_name] = dep_version
                        added_deps.append(dep_name)

        # Write merged JSON back to project package.json with indent=2
        project_pkg_file.write_text(
            json.dumps(project_data, indent=2) + "\n", encoding="utf-8"
        )

        # Print added dependencies
        for dep_name in added_deps:
            print(f"  + {dep_name} (agregado a package.json)")

    # ========================================================
    # EJECUTAR ENVIRONMENTS
    # ========================================================
    # Copia los archivos de cada Environment seleccionado.
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

            # ------------------------------------------------
            # Guardar el puerto por defecto para este lenguaje
            # ------------------------------------------------

            default_ports = env.get("default_ports", {})

            if template_language in default_ports:

                self._env_port = str(default_ports[template_language])

            print(f"✓ {env['name']} configurado.")

    # ========================================================
    # COPIAR ARCHIVOS DE CONFIGURACIÓN DE TOOLS
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

    def _run_command(self, project_path: Path, command: list[str]):

        venv_python = project_path / ".venv" / "Scripts" / "python.exe"

        command = [
            str(venv_python) if argument == "python" else argument
            for argument in command
        ]

        subprocess.run(command, cwd=project_path, check=True)


        # ========================================================
    # LIMPIAR ARCHIVOS .gitkeep
    # ========================================================
    # Elimina archivos .gitkeep de carpetas que ya tienen
    # contenido. El .gitkeep solo tiene sentido en carpetas
    # vacías (para que Git las rastree).
    #
    # Después de copiar Features y Environments, algunas
    # carpetas que estaban vacías ahora tienen archivos, así
    # que su .gitkeep ya no es necesario.
    # ========================================================

    def _cleanup_gitkeep(self, project_path: Path):

        for gitkeep in project_path.rglob(".gitkeep"):

            parent = gitkeep.parent

            # Ver si la carpeta tiene otros archivos además del .gitkeep
            has_other_files = any(
                item for item in parent.iterdir()
                if item.name != ".gitkeep"
            )

            if has_other_files:
                gitkeep.unlink()
    # ========================================================
    # REEMPLAZAR PLACEHOLDERS
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

    def _update_requirements(self, project_path: Path, resources: list[dict]):

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

        # Recopilar dependencias de los recursos (tools, tecnologías)
        new_dependencies = []

        for item in resources:
            dependencies = item.get("dependencies", [])
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

    # ========================================================
    # AGREGAR DEPENDENCIAS A PACKAGE.JSON (NODE)
    # ========================================================
    # Agrega las dependencias declaradas por los recursos
    # (tools, tecnologías) al archivo package.json del proyecto Node.
    # ========================================================

    def _add_node_dependencies(
        self, project_path: Path, resources: list[dict]
    ) -> None:

        package_file = project_path / "package.json"

        if not package_file.exists():
            return

        try:
            package_data = json.loads(package_file.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return

        dependencies = package_data.get("dependencies")
        if not isinstance(dependencies, dict):
            dependencies = {}
            package_data["dependencies"] = dependencies

        added_deps = []

        for item in resources:
            item_deps = item.get("dependencies", [])
            for dep_str in item_deps:
                if not dep_str or not isinstance(dep_str, str):
                    continue

                # Parse dep_str into name and version
                if dep_str.startswith("@"):
                    at_idx = dep_str.find("@", 1)
                else:
                    at_idx = dep_str.find("@")

                if at_idx != -1:
                    dep_name = dep_str[:at_idx]
                    dep_version = dep_str[at_idx + 1 :]
                else:
                    dep_name = dep_str
                    dep_version = "*"

                if dep_name not in dependencies:
                    dependencies[dep_name] = dep_version
                    added_deps.append(dep_name)

        if not added_deps:
            return

        package_file.write_text(
            json.dumps(package_data, indent=2) + "\n", encoding="utf-8"
        )

        for dep_name in added_deps:
            print(f"  + {dep_name} (agregado a package.json)")

