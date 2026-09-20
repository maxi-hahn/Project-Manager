import customtkinter as ctk


# ============================================================
# TEMPLATE CARD
# ============================================================
# Card seleccionable que muestra un template.
# Cuando se hace click, notifica al padre.
# ============================================================


class TemplateCard(ctk.CTkFrame):
    def __init__(self, master, template: dict, on_select=None):
        super().__init__(master, corner_radius=8)

        self.template = template
        self.on_select = on_select
        self.is_selected = False

        self.grid_columnconfigure(0, weight=1)

        # Nombre
        self.name_label = ctk.CTkLabel(
            self,
            text=template["name"],
            font=ctk.CTkFont(size=15, weight="bold"),
            anchor="w",
        )
        self.name_label.grid(row=0, column=0, sticky="ew", padx=15, pady=(12, 2))

        # Categoría + lenguaje
        meta_text = f"{self._category_label(template)} · {template.get('language', '')}"
        self.meta_label = ctk.CTkLabel(
            self,
            text=meta_text,
            font=ctk.CTkFont(size=11),
            text_color="gray",
            anchor="w",
        )
        self.meta_label.grid(row=1, column=0, sticky="ew", padx=15, pady=(0, 4))

        # Descripción
        self.description_label = ctk.CTkLabel(
            self,
            text=template.get("description", ""),
            font=ctk.CTkFont(size=12),
            anchor="w",
            justify="left",
            wraplength=400,
        )
        self.description_label.grid(
            row=2, column=0, sticky="ew", padx=15, pady=(0, 12)
        )

        # Bind click en toda la card y en los labels
        for widget in [self, self.name_label, self.meta_label, self.description_label]:
            widget.bind("<Button-1>", self._on_click)

        self._update_appearance()

    def _category_label(self, template: dict) -> str:
        """Devuelve el label amigable de la categoría."""
        if "category_label" in template:
            return template["category_label"]
        category = template.get("category", "")
        return category.replace("_", " ").title()

    def _on_click(self, event=None):
        if self.on_select:
            self.on_select(self.template)

    def set_selected(self, selected: bool):
        self.is_selected = selected
        self._update_appearance()

    def _update_appearance(self):
        if self.is_selected:
            self.configure(fg_color=("gray75", "gray25"), border_width=2, border_color=("gray10", "cyan"))
        else:
            self.configure(fg_color=("gray85", "gray20"), border_width=0)
