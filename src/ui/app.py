from pathlib import Path
import customtkinter as ctk

from config import PROJECTS_DIR, TEMPLATES_DIR, get_resource_dirs
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

WINDOW_TITLE = "Project Manager"
WINDOW_MIN_WIDTH = 1000
WINDOW_MIN_HEIGHT = 700


# ============================================================
# VENTANA PRINCIPAL
# ============================================================


class ProjectManagerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title(WINDOW_TITLE)
        self.minsize(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)
        self.geometry(f"{WINDOW_MIN_WIDTH}x{WINDOW_MIN_HEIGHT}")

        # Configuración y estado
        self.config_manager = ConfigManager()
        self.projects_root: Path | None = None
        self.resources_root: Path | None = None
        self.resource_dirs: dict = {}
        self.editors: list[str] = []
        self.custom_editors: list[dict] = []
        self.auto_install_dependencies: bool = True

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

        # Cargar templates por defecto
        self._load_templates()

        # Inicializar wizard
        self._build_screens()

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
        )

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
            "auto_install_dependencies", True
        )

        # Pass paths to screens
        if len(self.screens) > 0:
            self.screens[0].set_projects_root(self.projects_root)
            if default_location:
                self.screens[0].set_default_location(default_location)

        if len(self.screens) > 1:
            self.screens[1].set_templates_dir(
                self.resource_dirs.get("templates")
            )

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

        title = ctk.CTkLabel(
            header,
            text="Project Manager",
            font=ctk.CTkFont(size=20, weight="bold"),
        )
        title.grid(row=0, column=0, padx=20, pady=10, sticky="w")

        settings_button = ctk.CTkButton(
            header,
            text="Ajustes",
            width=100,
            command=self._on_settings_click,
        )
        settings_button.grid(row=0, column=1, padx=20, pady=10, sticky="e")

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
                templates=self.templates,
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
        """Habilita o deshabilita Siguiente según la validez del paso."""
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
        }
        CreateProjectModal(self, data)

    def _on_settings_click(self):
        SettingsDialog(
            self,
            self.config_manager,
            is_first_run=False,
            on_save=self._apply_config,
        )


# ============================================================
# PUNTO DE ENTRADA
# ============================================================


def run():
    app = ProjectManagerApp()
    app.mainloop()