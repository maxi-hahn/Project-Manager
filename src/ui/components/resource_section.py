import customtkinter as ctk


# ============================================================
# RESOURCE SECTION
# ============================================================
# Sección con título, contador y lista de checkboxes.
# Se usa para Tools, Features, Environments y Technologies.
# ============================================================


class ResourceSection(ctk.CTkFrame):
    def __init__(self, master, title: str, resources: list[dict], on_change=None):
        super().__init__(master, fg_color="transparent")

        self.title = title
        self.resources = resources
        self.on_change = on_change
        self.checkboxes = []
        self.selected = []

        self.grid_columnconfigure(0, weight=1)

        # Título con contador
        self.title_label = ctk.CTkLabel(
            self,
            text=self._build_title(),
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w",
        )
        self.title_label.grid(row=0, column=0, sticky="ew", pady=(15, 5))

        # Separador
        separator = ctk.CTkFrame(self, height=1, fg_color="gray30")
        separator.grid(row=1, column=0, sticky="ew", pady=(0, 5))

        # Checkboxes
        for index, resource in enumerate(resources):
            var = ctk.BooleanVar(value=False)

            checkbox = ctk.CTkCheckBox(
                self,
                text=f"{resource['name']} — {resource['description']}",
                variable=var,
                command=lambda r=resource, v=var: self._on_checkbox_toggle(r, v),
            )
            checkbox.grid(
                row=2 + index, column=0, sticky="w", pady=3, padx=(0, 0)
            )

            self.checkboxes.append((resource, var, checkbox))

    def _build_title(self) -> str:
        count = len(self.selected)
        total = len(self.resources)
        if count == 0:
            return f"{self.title} ({total} disponibles)"
        return f"{self.title} ({count} seleccionadas)"

    def _on_checkbox_toggle(self, resource: dict, var: ctk.BooleanVar):
        if var.get():
            if resource not in self.selected:
                self.selected.append(resource)
        else:
            if resource in self.selected:
                self.selected.remove(resource)

        self.title_label.configure(text=self._build_title())

        if self.on_change:
            self.on_change()

    # --------------------------------------------------------
    # API PÚBLICA
    # --------------------------------------------------------

    def get_selected(self) -> list[dict]:
        return self.selected

    def clear(self):
        """Deselecciona todo."""
        for resource, var, checkbox in self.checkboxes:
            var.set(False)
        self.selected = []
        self.title_label.configure(text=self._build_title())