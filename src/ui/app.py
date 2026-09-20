import customtkinter as ctk


# ============================================================
# CONFIGURACIÓN GLOBAL
# ============================================================

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

WINDOW_TITLE = "Project Manager"
WINDOW_MIN_WIDTH = 1000
WINDOW_MIN_HEIGHT = 700

# Proporción del panel de preview (derecha)
PREVIEW_WIDTH_RATIO = 0.30


# ============================================================
# VENTANA PRINCIPAL
# ============================================================
# Estructura:
#
# ┌──────────────────────────────────────────────────┐
# │  Título                              [Ajustes]  │
# ├──────────────────────────┬───────────────────────┤
# │                          │                       │
# │   Contenido principal    │   Preview (30%)       │
# │   (70%)                  │                       │
# │                          │                       │
# └──────────────────────────┴───────────────────────┘
# ============================================================


class ProjectManagerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title(WINDOW_TITLE)
        self.minsize(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)
        self.geometry(f"{WINDOW_MIN_WIDTH}x{WINDOW_MIN_HEIGHT}")

        # ------------------------------------------------
        # Layout principal: 2 columnas (contenido + preview)
        # ------------------------------------------------

        self.grid_columnconfigure(0, weight=7)   # 70%
        self.grid_columnconfigure(1, weight=3)   # 30%
        self.grid_rowconfigure(1, weight=1)

        # ------------------------------------------------
        # Header (fila 0, ocupa ambas columnas)
        # ------------------------------------------------

        self._build_header()

        # ------------------------------------------------
        # Contenido principal (fila 1, columna 0)
        # ------------------------------------------------

        self._build_main_content()

        # ------------------------------------------------
        # Panel de preview (fila 1, columna 1)
        # ------------------------------------------------

        self._build_preview_panel()

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
        content = ctk.CTkFrame(self, corner_radius=0)
        content.grid(row=1, column=0, sticky="nsew", padx=(10, 5), pady=10)

        label = ctk.CTkLabel(
            content,
            text="Contenido principal (en construcción)",
            font=ctk.CTkFont(size=14),
        )
        label.pack(expand=True)

    # ========================================================
    # PANEL DE PREVIEW (derecha)
    # ========================================================

    def _build_preview_panel(self):
        preview = ctk.CTkFrame(self, corner_radius=0)
        preview.grid(row=1, column=1, sticky="nsew", padx=(5, 10), pady=10)

        label = ctk.CTkLabel(
            preview,
            text="Preview del proyecto",
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        label.pack(pady=(10, 5))

        # Área de texto donde se mostrará el árbol de carpetas.
        # Por ahora, un placeholder.

        placeholder = ctk.CTkLabel(
            preview,
            text="(acá aparecerá el árbol de carpetas)",
            font=ctk.CTkFont(size=12),
            text_color="gray",
        )
        placeholder.pack(expand=True)

    # ========================================================
    # HANDLERS
    # ========================================================

    def _on_settings_click(self):
        # Placeholder: cuando implementemos el sistema de
        # configuración persistente, acá se abrirá un modal
        # o una ventana de ajustes.
        print("Ajustes: próximamente")


# ============================================================
# PUNTO DE ENTRADA
# ============================================================


def run():
    app = ProjectManagerApp()
    app.mainloop()