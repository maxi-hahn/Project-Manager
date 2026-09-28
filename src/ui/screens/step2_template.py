from pathlib import Path
import customtkinter as ctk

from src.logic.prerequisites import PREREQUISITE_MESSAGES, check_prerequisites
from src.template_manager import TemplateManager
from src.ui.components.template_card import TemplateCard

# ============================================================
# PASO 2: ELEGIR TEMPLATE
# ============================================================
# - Filtro por tipo de proyecto (dropdown, opcional).
# - Lista scrolleable de cards con todos los templates.
# - Selección directa de un template.
# ============================================================


class Step2Template(ctk.CTkFrame):
    def __init__(
        self,
        master,
        templates: list[dict] | None = None,
        on_change=None,
        templates_dir: Path | None = None,
    ):
        super().__init__(master, fg_color="transparent")

        self.all_templates = templates or []
        self.on_change = on_change
        self.selected_template = None
        self.filter_var = ctk.StringVar(value="Todos")
        self.cards = []
        self.placeholder_label = None

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        # Título
        title = ctk.CTkLabel(
            self,
            text="Paso 2: Elegir template",
            font=ctk.CTkFont(size=18, weight="bold"),
            anchor="w",
        )
        title.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 15))

        # Filtro
        filter_frame = ctk.CTkFrame(self, fg_color="transparent")
        filter_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 10))
        filter_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(filter_frame, text="Tipo de proyecto:", anchor="w").grid(
            row=0, column=0, sticky="w", padx=(0, 10)
        )

        self.filter_dropdown = ctk.CTkOptionMenu(
            filter_frame,
            variable=self.filter_var,
            values=self._build_filter_options(),
            command=self._on_filter_change,
            width=200,
        )
        self.filter_dropdown.grid(row=0, column=1, sticky="w")

        # Separador
        separator = ctk.CTkFrame(self, height=1, fg_color="gray30")
        separator.grid(row=2, column=0, sticky="ew", padx=20, pady=(5, 10))

        # Lista scrolleable
        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_frame.grid(row=3, column=0, sticky="nsew", padx=20, pady=(0, 10))
        self.scroll_frame.grid_columnconfigure(0, weight=1)

        if templates_dir:
            self.set_templates_dir(templates_dir)
        else:
            self._render_cards()

    # ========================================================
    # FILTRO
    # ========================================================

    def _build_filter_options(self) -> list[str]:
        """Construye las opciones del dropdown: 'Todos' + categorías únicas."""
        categories = {}

        for t in self.all_templates:
            cat = t.get("category", "")
            if cat and cat not in categories:
                categories[cat] = self._category_label(t)

        # Ordenar alfabéticamente por label
        ordered = ["Todos"] + sorted(categories.values(), key=str.lower)
        return ordered

    def _category_label(self, template: dict) -> str:
        if "category_label" in template:
            return template["category_label"]
        return template.get("category", "").replace("_", " ").title()

    def _on_filter_change(self, value: str):
        self._render_cards()

    # ========================================================
    # RENDERIZADO DE CARDS
    # ========================================================

    def _render_cards(self):
        """Limpia y vuelve a renderizar las cards según el filtro."""

        # Limpiar
        if self.placeholder_label:
            self.placeholder_label.destroy()
            self.placeholder_label = None

        for card in self.cards:
            card.destroy()
        self.cards = []

        # Filtrar
        filter_value = self.filter_var.get()

        if filter_value == "Todos":
            filtered = self.all_templates
        else:
            filtered = [
                t for t in self.all_templates if self._category_label(t) == filter_value
            ]

        # Si no hay templates, mostrar placeholder y salir
        if not filtered:
            self.placeholder_label = ctk.CTkLabel(
                self.scroll_frame,
                text="No se encontraron templates. Verificá la configuración.",
                text_color="gray",
            )
            self.placeholder_label.grid(row=0, column=0, sticky="ew", pady=20)
            return

        # Recrear cards
        for index, template in enumerate(filtered):
            card = TemplateCard(
                self.scroll_frame,
                template=template,
                on_select=self._on_card_select,
            )
            card.grid(row=index, column=0, sticky="ew", pady=5)

            # Marcar como seleccionada si corresponde
            if (
                self.selected_template
                and self.selected_template["name"] == template["name"]
            ):
                card.set_selected(True)

            self.cards.append(card)

        # Si el template seleccionado ya no está en la lista, deseleccionar
        if self.selected_template and self.selected_template not in filtered:
            self.selected_template = None
            self._notify_change()

    # ========================================================
    # SELECCIÓN
    # ========================================================

    def _on_card_select(self, template: dict):
        # Verificar prerrequisitos antes de seleccionar
        requires = template.get("requires", [])
        if requires:
            missing = check_prerequisites(requires)
            if missing:
                self._show_prerequisites_error(missing)
                return

        self.selected_template = template

        # Actualizar apariencia de las cards
        for card in self.cards:
            is_selected = card.template["name"] == template["name"]
            card.set_selected(is_selected)

        self._notify_change()

    def _show_prerequisites_error(self, missing: list[str]):
        """Muestra un messagebox con los prerrequisitos faltantes."""
        from tkinter import messagebox

        lines = [
            "No se puede seleccionar este template.\n",
            "Faltan los siguientes requisitos:\n",
        ]
        for req in missing:
            description = PREREQUISITE_MESSAGES.get(req, req)
            lines.append(f"  - {req}: {description}\n")
        lines.append("\nInstalá los requisitos faltantes y volvé a intentarlo.")

        messagebox.showerror(
            "Prerrequisitos faltantes",
            "".join(lines),
            parent=self,
        )

    def _notify_change(self):
        if self.on_change:
            self.on_change()

    # ========================================================
    # API PÚBLICA
    # ========================================================

    def set_templates_dir(self, templates_dir: Path | None):
        """Descubre y carga templates desde la ruta especificada."""
        if templates_dir and templates_dir.exists() and templates_dir.is_dir():
            manager = TemplateManager(templates_dir)
            templates = manager.discover_templates()
            templates.sort(key=lambda t: (t.get("category", ""), t.get("name", "")))
            self.all_templates = templates
        else:
            self.all_templates = []

        self.filter_dropdown.configure(values=self._build_filter_options())
        self.filter_var.set("Todos")
        self._render_cards()

    def get_selected_template(self) -> dict | None:
        return self.selected_template

    def is_valid(self) -> bool:
        return self.selected_template is not None
