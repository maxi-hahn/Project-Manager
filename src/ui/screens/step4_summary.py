import customtkinter as ctk


# ============================================================
# PASO 4: RESUMEN
# ============================================================
# Muestra un resumen de solo lectura con toda la información
# recopilada en los pasos anteriores.
# Se reconstruye llamando a refresh(data) cada vez que se
# navega a este paso.
# ============================================================


class Step4Summary(ctk.CTkFrame):
    def __init__(self, master, on_change=None):
        super().__init__(master, fg_color="transparent")

        self.on_change = on_change

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # --------------------------------------------------------
        # Fixed title
        # --------------------------------------------------------

        title = ctk.CTkLabel(
            self,
            text="Paso 4: Resumen",
            font=ctk.CTkFont(size=18, weight="bold"),
            anchor="w",
        )
        title.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))

        # --------------------------------------------------------
        # Scrollable content area
        # --------------------------------------------------------

        self.scroll_frame = ctk.CTkScrollableFrame(
            self, fg_color="transparent"
        )
        self.scroll_frame.grid(
            row=1, column=0, sticky="nsew", padx=20, pady=(0, 10)
        )
        self.scroll_frame.grid_columnconfigure(0, weight=1)

        # Placeholder shown before the first refresh() call
        self._placeholder = ctk.CTkLabel(
            self.scroll_frame,
            text="(completá los pasos anteriores para ver el resumen)",
            text_color="gray",
            anchor="w",
        )
        self._placeholder.grid(row=0, column=0, sticky="ew", pady=20)

        # Internal list of dynamically created widgets
        self._content_widgets: list[ctk.CTkBaseClass] = []

    # ============================================================
    # INTERNAL HELPERS
    # ============================================================

    def _clear_content(self):
        """Removes all dynamically created summary widgets."""
        for widget in self._content_widgets:
            widget.destroy()
        self._content_widgets.clear()

    def _add_section_header(self, text: str, row: int) -> int:
        """Adds a bold section header and a separator line. Returns the next row index."""

        header = ctk.CTkLabel(
            self.scroll_frame,
            text=text,
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w",
        )
        header.grid(row=row, column=0, sticky="ew", pady=(16, 2))
        self._content_widgets.append(header)
        row += 1

        separator = ctk.CTkFrame(self.scroll_frame, height=1, fg_color="gray30")
        separator.grid(row=row, column=0, sticky="ew", pady=(0, 6))
        self._content_widgets.append(separator)
        row += 1

        return row

    def _add_field(self, label: str, value: str, row: int) -> int:
        """Adds a label-value pair. Returns the next row index."""
        text = f"{label}:  {value}" if value else f"{label}:  —"
        widget = ctk.CTkLabel(
            self.scroll_frame,
            text=text,
            anchor="w",
            justify="left",
        )
        widget.grid(row=row, column=0, sticky="ew", pady=2, padx=8)
        self._content_widgets.append(widget)
        return row + 1

    def _add_bullet_list(self, items: list[str], row: int) -> int:
        """Adds a bullet-point list of items. Returns the next row index."""
        for item in items:
            widget = ctk.CTkLabel(
                self.scroll_frame,
                text=f"  · {item}",
                anchor="w",
                justify="left",
            )
            widget.grid(row=row, column=0, sticky="ew", pady=1, padx=8)
            self._content_widgets.append(widget)
            row += 1
        return row

    # ============================================================
    # PUBLIC API
    # ============================================================

    def refresh(self, data: dict) -> None:
        """Rebuilds the summary content from scratch based on the provided data."""

        # Remove any previous content and hide the placeholder
        self._clear_content()
        if self._placeholder.winfo_exists():
            self._placeholder.grid_forget()

        info = data.get("info", {})
        template = data.get("template", {}) or {}
        config = data.get("config", {})

        row = 0

        # --------------------------------------------------------
        # Section: Project information
        # --------------------------------------------------------

        row = self._add_section_header("Información del proyecto", row)
        row = self._add_field("Nombre", info.get("name", ""), row)
        row = self._add_field("Descripción", info.get("description", ""), row)
        row = self._add_field("Ubicación", info.get("location", ""), row)

        # --------------------------------------------------------
        # Section: Template
        # --------------------------------------------------------

        row = self._add_section_header("Template", row)
        row = self._add_field("Nombre", template.get("name", ""), row)

        # --------------------------------------------------------
        # Optional sections: Tools, Features, Environments, Technologies
        # --------------------------------------------------------

        optional_sections = [
            ("Tools", config.get("tools", [])),
            ("Features", config.get("features", [])),
            ("Environments", config.get("environments", [])),
            ("Technologies", config.get("technologies", [])),
        ]

        for section_title, resources in optional_sections:
            if resources:
                row = self._add_section_header(section_title, row)
                names = [r.get("name", "") for r in resources]
                row = self._add_bullet_list(names, row)