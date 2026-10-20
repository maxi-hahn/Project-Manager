import subprocess
import threading
from pathlib import Path
from tkinter import messagebox

try:
    import winsound
except ImportError:
    winsound = None

import customtkinter as ctk

from config import PROJECTS_DIR, TEMPLATES_DIR, get_resource_dirs
from src.__version__ import __version__
from src.core.config_manager import ConfigManager
from src.logic.tree_builder import build_tree, merge_trees, render_tree
from src.template_manager import TemplateManager
from src.ui.components.create_project_modal import CreateProjectModal
from src.ui.components.settings_dialog import SettingsDialog
from src.ui.components.step_navigation import StepNavigation
from src.ui.screens.step1_info import Step1Info
from src.ui.screens.step2_template import Step2Template
from src.ui.screens.step3_config import Step3Config
from src.ui.screens.step4_summary import Step4Summary

# ============================================================
# CONFIGURACIÓN GLOBAL
# ============================================================

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

WINDOW_MIN_WIDTH = 1000
WINDOW_MIN_HEIGHT = 700


# ============================================================
# VENTANA PRINCIPAL
# ============================================================


class ProjectManagerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title(f"Project Manager v{__version__}")
        self.minsize(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)
        self.geometry(f"{WINDOW_MIN_WIDTH}x{WINDOW_MIN_HEIGHT}")

        # Configuración y estado
        self.config_manager = ConfigManager()
        self.projects_root: Path | None = None
        self.resources_root: Path | None = None
        self.resource_dirs: dict = {}
        self.editors: list[str] = []
        self.custom_editors: list[dict] = []
        self.auto_install_dependencies: bool = False

        self._background_install_running = False
        self._install_process = None  # subprocess.Popen
        self._created_repo_name = None  # str or None
        self._created_repo_path = None  # Path or None

        # Estado del wizard
        self.current_step = 0
        self.screens = []
        self.current_screen = None

        # Datos
        self.templates = []
        self.selected_template = None
        self._loaded_template = None  # Template cargado en Paso 3

        # Layout principal
        self.grid_columnconfigure(0, weight=7)
        self.grid_columnconfigure(1, weight=3)
        self.grid_rowconfigure(1, weight=1)

        self._build_header()
        self._build_main_content()
        self._build_preview_panel()

        # Inicializar wizard
        self._build_screens()

        self.protocol("WM_DELETE_WINDOW", self._on_main_window_close)

        if self.config_manager.exists():
            self._apply_config()
        else:
            self.after(100, self._open_initial_config)

        self._show_step(0)

    # ========================================================
    # CONFIGURACIÓN WIZARD
    # ========================================================

    def _open_initial_config(self):
        SettingsDialog(
            self,
            self.config_manager,
            is_first_run=True,
            on_save=self._on_initial_config_saved,
            on_cancel=self._on_initial_config_cancelled,
            on_templates_downloaded=self._on_templates_downloaded,
        )

    def _on_templates_downloaded(self, resources_root: Path | None = None):
        if resources_root and len(self.screens) > 1:
            resource_dirs = get_resource_dirs(resources_root)
            self.screens[1].set_templates_dir(resource_dirs["templates"])
        self._apply_config()

    def _on_initial_config_saved(self):
        self._apply_config()

    def _on_initial_config_cancelled(self):
        self.quit()
        self.destroy()

    def _apply_config(self):
        config = self.config_manager.get_all()

        projects_root = config.get("projects_root", "")
        resources_root = config.get("resources_root", "")
        default_location = config.get("default_location", "")

        if not projects_root or not resources_root:
            return

        self.projects_root = Path(projects_root)
        self.resources_root = Path(resources_root)
        self.resource_dirs = get_resource_dirs(self.resources_root)
        self.editors = config.get("editors", [])
        self.custom_editors = config.get("custom_editors", [])
        self.auto_install_dependencies = config.get(
            "auto_install_dependencies", False
        )

        # Pass paths to screens
        if len(self.screens) > 0:
            self.screens[0].set_projects_root(self.projects_root)
            if default_location:
                self.screens[0].set_default_location(default_location)

        if len(self.screens) > 1:
            self.screens[1].set_templates_dir(self.resource_dirs["templates"])

        if len(self.screens) > 2:
            self.screens[2].set_resource_dirs(self.resource_dirs)

        self._update_next_button()
        self._update_preview()

    def _on_change_projects_root(self, new_path: Path):
        self.config_manager.set("projects_root", str(new_path))
        self._apply_config()

    # ========================================================
    # DATOS
    # ========================================================

    def _load_templates(self):
        """Carga y ordena los templates disponibles por defecto."""
        if not TEMPLATES_DIR.exists():
            self.templates = []
            return

        manager = TemplateManager(TEMPLATES_DIR)
        templates = manager.discover_templates()

        # Ordenar por categoría y luego por nombre
        templates.sort(
            key=lambda t: (t.get("category", ""), t.get("name", ""))
        )

        self.templates = templates

    # ========================================================
    # HEADER
    # ========================================================

    def _build_header(self):
        header = ctk.CTkFrame(self, height=60, corner_radius=0)
        header.grid(row=0, column=0, columnspan=2, sticky="ew")
        header.grid_columnconfigure(0, weight=1)
        header.grid_columnconfigure(1, weight=0)  # Middle column
        header.grid_columnconfigure(2, weight=1)  # Right column

        # Title (left)
        title = ctk.CTkLabel(
            header,
            text="Project Manager",
            font=ctk.CTkFont(size=20, weight="bold"),
        )
        title.grid(row=0, column=0, padx=20, pady=10, sticky="w")

        # Status label (middle)
        self.status_label = ctk.CTkLabel(
            header,
            text="",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=("#f59e0b", "#f59e0b"),  # Orange-ish
        )
        self.status_label.grid(row=0, column=1, padx=20, pady=10)

        # Settings button (right)
        self.settings_button = ctk.CTkButton(
            header,
            text="Ajustes",
            width=100,
            command=self._on_settings_click,
        )
        self.settings_button.grid(row=0, column=2, padx=20, pady=10, sticky="e")

    # ========================================================
    # CONTENIDO PRINCIPAL (izquierda)
    # ========================================================

    def _build_main_content(self):
        self.content_frame = ctk.CTkFrame(self, corner_radius=0)
        self.content_frame.grid(
            row=1, column=0, sticky="nsew", padx=(10, 5), pady=10
        )
        self.content_frame.grid_rowconfigure(0, weight=1)
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_propagate(False)

        self.nav_bar = StepNavigation(
            self.content_frame,
            on_back=self._on_back,
            on_next=self._on_next,
            show_back=False,
        )
        self.nav_bar.grid(row=1, column=0, sticky="ew", padx=10, pady=10)

    # ========================================================
    # PANEL DE PREVIEW (derecha)
    # ========================================================

    def _build_preview_panel(self):
        preview = ctk.CTkFrame(self, corner_radius=0, width=300)
        preview.grid(row=1, column=1, sticky="nsew", padx=(5, 10), pady=10)
        preview.grid_propagate(False)

        header_frame = ctk.CTkFrame(preview, fg_color="transparent")
        header_frame.pack(fill="x", padx=10, pady=(10, 5))
        header_frame.grid_columnconfigure(0, weight=1)
        header_frame.grid_columnconfigure(1, weight=0)

        self.preview_name_label = ctk.CTkLabel(
            header_frame,
            text="",
            font=ctk.CTkFont(size=13, weight="bold"),
            anchor="w",
        )
        self.preview_name_label.grid(row=0, column=0, sticky="w")

        self.preview_location_label = ctk.CTkLabel(
            header_frame,
            text="",
            font=ctk.CTkFont(size=12),
            text_color="gray",
            anchor="e",
        )
        self.preview_location_label.grid(row=0, column=1, sticky="e")

        separator = ctk.CTkFrame(preview, height=1, fg_color="gray30")
        separator.pack(fill="x", padx=10, pady=(5, 10))

        self.preview_template_label = ctk.CTkLabel(
            preview,
            text="",
            font=ctk.CTkFont(size=12),
            text_color="gray",
            anchor="w",
            justify="left",
        )
        self.preview_template_label.pack(fill="x", padx=10, pady=(0, 5))

        self.preview_tree_box = ctk.CTkTextbox(
            preview,
            font=ctk.CTkFont(size=10, family="Consolas"),
            text_color="gray",
            wrap="none",
            activate_scrollbars=True,
        )
        self.preview_tree_box.pack(fill="both", expand=True, padx=10, pady=5)
        self.preview_tree_box.insert("1.0", "(acá aparecerá el árbol de carpetas)")
        self.preview_tree_box.configure(state="disabled")

    # ========================================================
    # WIZARD
    # ========================================================

    def _build_screens(self):
        self.screens = [
            Step1Info(
                self.content_frame,
                on_change=self._on_state_change,
                on_change_projects_root=self._on_change_projects_root,
            ),
            Step2Template(
                self.content_frame,
                templates=[],
                on_change=self._on_state_change,
            ),
            Step3Config(self.content_frame, on_change=self._on_state_change),
            Step4Summary(self.content_frame, on_change=self._on_state_change),
        ]

        # Cargar ubicaciones por defecto si existen
        if PROJECTS_DIR.exists():
            locations = [
                folder.name
                for folder in PROJECTS_DIR.iterdir()
                if folder.is_dir()
            ]
            self.screens[0].set_locations(locations)

    def _show_step(self, index: int):
        if self.current_screen:
            self.current_screen.grid_forget()

        self.current_step = index
        self.current_screen = self.screens[index]
        self.current_screen.grid(row=0, column=0, sticky="nsew")

        self.nav_bar.grid_forget()
        show_back = index > 0
        is_last = index == len(self.screens) - 1

        self.nav_bar = StepNavigation(
            self.content_frame,
            on_back=self._on_back,
            on_next=self._on_next,
            next_text="Crear proyecto" if is_last else "Siguiente →",
            show_back=show_back,
        )
        self.nav_bar.grid(row=1, column=0, sticky="ew", padx=10, pady=10)

        # Si entramos al paso 3, recargar recursos solo si el template cambió
        if index == 2:
            template = self.screens[1].get_selected_template()

            # Comparar por nombre
            current_name = template["name"] if template else None
            loaded_name = (
                self._loaded_template["name"] if self._loaded_template else None
            )

            if current_name != loaded_name:
                self.screens[2].load_for_template(template)
                self._loaded_template = template

        # Si entramos al paso 4, reconstruir el resumen con los datos actuales
        if index == 3:
            data = {
                "info": self.screens[0].get_data(),
                "template": self.screens[1].get_selected_template(),
                "config": self.screens[2].get_selection(),
            }
            self.screens[3].refresh(data)

        self._update_next_button()
        self._update_preview()

    def _on_back(self):
        if self.current_step > 0:
            self._show_step(self.current_step - 1)

    def _on_next(self):
        if self.current_step < len(self.screens) - 1:
            self._show_step(self.current_step + 1)
        else:
            self._on_create_project()

    # ========================================================
    # ESTADO Y VALIDACIÓN
    # ========================================================

    def _on_state_change(self):
        self._update_next_button()
        self._update_preview()

    def _update_next_button(self):
        """Enable or disable the Next button based on step validity."""
        if not self.screens or self.current_step >= len(self.screens):
            self.nav_bar.set_next_enabled(False)
            return

        screen = self.screens[self.current_step]

        if hasattr(screen, "is_valid"):
            self.nav_bar.set_next_enabled(screen.is_valid())
        else:
            self.nav_bar.set_next_enabled(True)

    def _set_preview_tree(self, text: str, color: str = "white"):
        self.preview_tree_box.configure(state="normal")
        self.preview_tree_box.delete("1.0", "end")
        self.preview_tree_box.insert("1.0", text)
        self.preview_tree_box.configure(state="disabled", text_color=color)

    def _update_preview(self):
        data = self.screens[0].get_data()
        self.preview_name_label.configure(text=data["name"] or "")
        self.preview_location_label.configure(text=data["location"] or "")

        selected_template = self.screens[1].get_selected_template()
        if selected_template:
            self.preview_template_label.configure(
                text=f"Template: {selected_template['name']}"
            )
        else:
            self.preview_template_label.configure(text="")

        if not selected_template:
            self._set_preview_tree(
                "(acá aparecerá el árbol de carpetas)", color="gray"
            )
            return

        project_name = data["name"] or "<Proyecto>"

        merged = self._get_resource_tree(selected_template, is_template=True)

        if (
            self._loaded_template is not None
            and selected_template is not None
            and self._loaded_template.get("name") == selected_template.get("name")
        ):
            if len(self.screens) > 2 and hasattr(self.screens[2], "get_selection"):
                selection = self.screens[2].get_selection()
                for resources in selection.values():
                    for resource in resources:
                        resource_tree = self._get_resource_tree(
                            resource, is_template=False
                        )
                        merged = merge_trees(merged, resource_tree)

        rendered = render_tree(merged, project_name)

        self._set_preview_tree(rendered, color="white")

    def _get_resource_tree(self, resource: dict, is_template: bool) -> dict:
        cache_key = "_tree_template" if is_template else "_tree_files"

        if cache_key in resource:
            return resource[cache_key]

        path = Path(resource.get("path", ""))

        if is_template:
            tree = build_tree(path, ignore_names={"template.json"})
        else:
            files_dir = path / "files"
            if files_dir.exists():
                tree = build_tree(files_dir)
            else:
                tree = {"type": "dir", "name": "", "children": {}}

        resource[cache_key] = tree
        return tree

    # ========================================================
    # ACCIONES
    # ========================================================

    def register_created_repo(self, name: str, path: Path):
        self._created_repo_name = name
        self._created_repo_path = path

    def _on_main_window_close(self):
        """Intercepts the main window close event."""
        if self._background_install_running:
            answer = messagebox.askyesno(
                "Instalación en curso",
                "Se están instalando las dependencias.\n\n"
                "Si cerrás ahora, la instalación se cancelará y el "
                "proyecto puede quedar incompleto (solo en la parte "
                "de dependencias).\n\n"
                "¿Querés cancelar la instalación y cerrar igual?",
                parent=self,
            )
            if not answer:
                return

            # User wants to cancel
            self._cancel_background_install()

        self.quit()
        self.destroy()

    def _cancel_background_install(self):
        """Kills the install process and rolls back git if needed."""
        # Kill the process
        if self._install_process and self._install_process.poll() is None:
            try:
                self._install_process.terminate()
                self._install_process.wait(timeout=5)
            except Exception:
                try:
                    self._install_process.kill()
                except Exception:
                    pass

        # Rollback git
        if self._created_repo_path:
            self._rollback_git()

    def _rollback_git(self):
        """Removes the local .git folder and the remote repo on GitHub."""
        import shutil

        # 1. Delete .git locally
        git_dir = self._created_repo_path / ".git"
        if git_dir.exists():
            try:
                shutil.rmtree(git_dir, ignore_errors=True)
            except Exception:
                pass

        # 2. Delete remote repo on GitHub (if it was created in this session)
        if self._created_repo_name:
            try:
                subprocess.run(
                    f'gh repo delete "{self._created_repo_name}" --yes',
                    capture_output=True,
                    text=True,
                    shell=True,
                )
            except Exception:
                pass

    def _set_ui_enabled(self, enabled: bool):
        """Enable or disable the main UI while the install runs."""
        state = "normal" if enabled else "disabled"

        # Header buttons
        if hasattr(self, "settings_button"):
            try:
                self.settings_button.configure(state=state)
            except Exception:
                pass

        # Wizard navigation bar (Back / Next)
        if hasattr(self, "nav_bar"):
            try:
                self.nav_bar.set_next_enabled(enabled)
                if hasattr(self.nav_bar, "back_button"):
                    self.nav_bar.back_button.configure(state=state)
            except Exception:
                pass

        # Screen-level input widgets: disable the whole content frame
        # (intercepts clicks) but avoid disabling labels.
        if hasattr(self, "content_frame"):
            try:
                # If we disable the frame, children may still respond.
                # The safest approach is to gray out the nav bar + buttons.
                pass
            except Exception:
                pass

    def start_background_install(self, project_path: Path, runtime: str):
        """Starts installing dependencies in the background."""
        self._background_install_running = True
        self._set_ui_enabled(False)
        self.status_label.configure(
            text="⏳ Instalando dependencias...", text_color=("#f59e0b", "#f59e0b")
        )

        def worker():
            try:
                if runtime == "node":
                    cmd = "npm install"
                elif runtime == "python":
                    python_exe = project_path / ".venv" / "Scripts" / "python.exe"
                    if not python_exe.exists():
                        bin_exe = project_path / ".venv" / "bin" / "python"
                        if bin_exe.exists():
                            python_exe = bin_exe
                    cmd = f'"{python_exe}" -m pip install -r requirements.txt'
                else:
                    self.after(0, self._on_background_install_done, True, "")
                    return

                self._install_process = subprocess.Popen(
                    cmd,
                    cwd=project_path,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    shell=True,
                )
                stdout, stderr = self._install_process.communicate()
                success = self._install_process.returncode == 0
                error_msg = stderr if not success else ""
                self.after(0, self._on_background_install_done, success, error_msg)
            except Exception as e:
                self.after(0, self._on_background_install_done, False, str(e))

        threading.Thread(target=worker, daemon=True).start()

    def _on_background_install_done(self, success: bool, error_msg: str):
        """Called when the background install finishes."""
        self._background_install_running = False
        self._set_ui_enabled(True)
        if success:
            self.status_label.configure(
                text="✓ Dependencias instaladas", text_color=("#22c55e", "#22c55e")
            )
            self._show_install_notification(success=True, error_msg="")
        else:
            self.status_label.configure(
                text="✗ Error en dependencias", text_color=("#ef4444", "#ef4444")
            )
            self._show_install_notification(success=False, error_msg=error_msg)

    def _show_install_notification(self, success: bool, error_msg: str):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Dependencias")
        dialog.geometry("420x280")
        dialog.resizable(False, False)
        dialog.attributes("-topmost", True)
        dialog.grab_set()
        dialog.transient(self)

        try:
            import winsound
            winsound.MessageBeep()
        except Exception:
            pass

        if success:
            title = "✓ Proyecto listo"
            body = (
                "Las dependencias se instalaron correctamente.\n\n"
                "Ya podés ejecutar el proyecto."
            )
            color = "#22c55e"
        else:
            title = "✗ Error en dependencias"
            body = (
                "No pudimos instalar las dependencias.\n"
                "Pedimos disculpas por el inconveniente.\n\n"
                "Ejecutá manualmente en la carpeta del proyecto:\n"
                "  npm install   (Node)\n"
                "  pip install -r requirements.txt   (Python)"
            )
            color = "#ef4444"

        ctk.CTkLabel(
            dialog, text=title,
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=color,
        ).pack(pady=(20, 10))

        ctk.CTkLabel(
            dialog, text=body,
            font=ctk.CTkFont(size=12),
            justify="center",
            wraplength=380,
        ).pack(pady=(0, 15))

        countdown_var = ctk.StringVar(value="5")
        ctk.CTkLabel(
            dialog, textvariable=countdown_var,
            font=ctk.CTkFont(size=24, weight="bold"),
        ).pack()

        progress = ctk.CTkProgressBar(dialog, width=300, progress_color="#7c3aed")
        progress.set(1.0)
        progress.pack(pady=(5, 15))

        remaining = [5]
        cancelled = [False]

        def tick():
            if cancelled[0]:
                return
            remaining[0] -= 1
            if remaining[0] <= 0:
                self.quit()
                self.destroy()
            else:
                countdown_var.set(str(remaining[0]))
                progress.set(remaining[0] / 5)
                dialog.after(1000, tick)

        def cancel():
            cancelled[0] = True
            dialog.destroy()

        ctk.CTkButton(
            dialog, text="Cancelar cierre", width=140,
            fg_color="gray30", hover_color="gray20",
            command=cancel,
        ).pack(pady=(0, 15))

        dialog.after(1000, tick)
        dialog.protocol("WM_DELETE_WINDOW", cancel)

    def _on_create_project(self):
        """Gathers wizard data and opens the project creation modal."""
        data = {
            "info": self.screens[0].get_data(),
            "template": self.screens[1].get_selected_template(),
            "config": self.screens[2].get_selection(),
            "projects_root": str(self.projects_root) if self.projects_root else "",
            "default_location": self.config_manager.get("default_location", ""),
            "editors": self.editors,
            "custom_editors": self.custom_editors,
            "auto_install_dependencies": self.auto_install_dependencies,
            "config_manager": self.config_manager,
            "github_last_visibility": self.config_manager.get(
                "github_last_visibility", "private"
            ),
        }
        CreateProjectModal(self, data)

    def _on_settings_click(self):
        SettingsDialog(
            self,
            self.config_manager,
            is_first_run=False,
            on_save=self._apply_config,
            on_templates_downloaded=self._on_templates_downloaded,
        )


# ============================================================
# PUNTO DE ENTRADA
# ============================================================


def run():
    app = ProjectManagerApp()
    app.mainloop()