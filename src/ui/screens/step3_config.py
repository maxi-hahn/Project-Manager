import customtkinter as ctk

from config import ENVIRONMENTS_DIR, FEATURES_DIR, TECHNOLOGIES_DIR, TOOLS_DIR
from src.logic.filters import (
    filter_environments_by_template,
    filter_features_by_template,
    filter_tools_by_language,
)
from src.resource_manager import ResourceManager
from src.ui.components.resource_section import ResourceSection

# ============================================================
# PASO 3: CONFIGURACIÓN TÉCNICA
# ============================================================
# Muestra secciones con checkboxes para:
#   - Tools
#   - Features
#   - Environments
#   - Technologies
#
# Cada sección solo muestra los recursos compatibles con el
# template seleccionado en el paso 2.
# ============================================================


class Step3Config(ctk.CTkFrame):
    def __init__(self, master, on_change=None):
        super().__init__(master, fg_color="transparent")

        self.on_change = on_change
        self.sections = []
        self.resource_dirs: dict | None = None

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Título
        title = ctk.CTkLabel(
            self,
            text="Paso 3: Configuración técnica",
            font=ctk.CTkFont(size=18, weight="bold"),
            anchor="w",
        )
        title.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))

        # Área scrolleable para las secciones
        self.scroll_frame = ctk.CTkScrollableFrame(
            self, fg_color="transparent"
        )
        self.scroll_frame.grid(
            row=1, column=0, sticky="nsew", padx=20, pady=(0, 10)
        )
        self.scroll_frame.grid_columnconfigure(0, weight=1)

        # Placeholder (se reemplaza cuando se carga un template)
        self.placeholder = ctk.CTkLabel(
            self.scroll_frame,
            text="Seleccioná un template en el paso anterior.",
            text_color="gray",
        )
        self.placeholder.grid(row=0, column=0, sticky="ew", pady=20)

    # ========================================================
    # CARGA DE RECURSOS SEGÚN TEMPLATE
    # ========================================================

    def load_for_template(self, template: dict | None):
        """Carga los recursos compatibles con el template seleccionado."""

        # Limpiar secciones anteriores
        for section in self.sections:
            section.destroy()
        self.sections = []

        if self.placeholder.winfo_exists():
            self.placeholder.destroy()

        if template is None:
            self.placeholder = ctk.CTkLabel(
                self.scroll_frame,
                text="Seleccioná un template en el paso anterior.",
                text_color="gray",
            )
            self.placeholder.grid(row=0, column=0, sticky="ew", pady=20)
            return

        res = self.resource_dirs or {}
        tools_dir = res.get("tools", TOOLS_DIR)
        features_dir = res.get("features", FEATURES_DIR)
        environments_dir = res.get("environments", ENVIRONMENTS_DIR)
        technologies_dir = res.get("technologies", TECHNOLOGIES_DIR)

        template_language = template.get("language", "").lower()

        # ------------------------------------------------
        # Tools
        # ------------------------------------------------

        tool_manager = ResourceManager(tools_dir, "tool.json")
        tools = tool_manager.discover()
        compatible_tools = filter_tools_by_language(tools, template_language)

        if compatible_tools:
            section = ResourceSection(
                self.scroll_frame,
                title="Tools",
                resources=compatible_tools,
                on_change=self._notify_change,
            )
            section.grid(row=len(self.sections), column=0, sticky="ew", pady=5)
            self.sections.append(section)

        # ------------------------------------------------
        # Features
        # ------------------------------------------------

        feature_manager = ResourceManager(features_dir, "feature.json")
        features = feature_manager.discover()
        compatible_features = filter_features_by_template(features, template)

        if template_language:
            compatible_features = [
                f
                for f in compatible_features
                if not f.get("language")
                or f["language"].lower() == template_language
            ]

        if compatible_features:
            section = ResourceSection(
                self.scroll_frame,
                title="Features",
                resources=compatible_features,
                on_change=self._notify_change,
            )
            section.grid(row=len(self.sections), column=0, sticky="ew", pady=5)
            self.sections.append(section)

        # ------------------------------------------------
        # Environments
        # ------------------------------------------------

        env_manager = ResourceManager(environments_dir, "environment.json")
        environments = env_manager.discover()
        compatible_environments = filter_environments_by_template(
            environments, template
        )

        if template_language:
            compatible_environments = [
                e
                for e in compatible_environments
                if not e.get("language")
                or e["language"].lower() == template_language
            ]

        if compatible_environments:
            section = ResourceSection(
                self.scroll_frame,
                title="Environments",
                resources=compatible_environments,
                on_change=self._notify_change,
            )
            section.grid(row=len(self.sections), column=0, sticky="ew", pady=5)
            self.sections.append(section)

        # ------------------------------------------------
        # Technologies
        # ------------------------------------------------

        tech_manager = ResourceManager(technologies_dir, "technology.json")
        technologies = tech_manager.discover()
        compatible_technologies = filter_features_by_template(
            technologies, template
        )

        if template_language:
            compatible_technologies = [
                t
                for t in compatible_technologies
                if not t.get("language")
                or t["language"].lower() == template_language
            ]

        if compatible_technologies:
            section = ResourceSection(
                self.scroll_frame,
                title="Technologies",
                resources=compatible_technologies,
                on_change=self._notify_change,
            )
            section.grid(row=len(self.sections), column=0, sticky="ew", pady=5)
            self.sections.append(section)

        # ------------------------------------------------
        # Si no hay nada compatible
        # ------------------------------------------------

        if not self.sections:
            self.placeholder = ctk.CTkLabel(
                self.scroll_frame,
                text="No hay recursos adicionales compatibles con este template.",
                text_color="gray",
            )
            self.placeholder.grid(row=0, column=0, sticky="ew", pady=20)

    def _notify_change(self):
        if self.on_change:
            self.on_change()

    # ========================================================
    # API PÚBLICA
    # ========================================================

    def set_resource_dirs(self, resource_dirs: dict):
        """Guarda las rutas de directorios de recursos."""
        self.resource_dirs = resource_dirs

    def get_selection(self) -> dict:
        """Devuelve los recursos seleccionados por categoría."""
        result = {
            "tools": [],
            "features": [],
            "environments": [],
            "technologies": [],
        }

        for section in self.sections:
            key = section.title.lower()
            if key in result:
                result[key] = section.get_selected()

        return result