import customtkinter as ctk

from config import PROJECTS_DIR


# ============================================================
# PASO 1: INFORMACIÓN DEL PROYECTO
# ============================================================
# Pide:
#   - Nombre del proyecto
#   - Descripción
#   - Ubicación (dropdown de carpetas en PROYECTOS)
#
# Valida en tiempo real que no exista un proyecto con el mismo
# nombre en la ubicación seleccionada.
# ============================================================


class Step1Info(ctk.CTkFrame):
    def __init__(self, master, on_change=None):
        super().__init__(master, fg_color="transparent")

        self.on_change = on_change

        # Variables de estado
        self.name_var = ctk.StringVar()
        self.description_var = ctk.StringVar()
        self.location_var = ctk.StringVar()

        # Notificar cambios en tiempo real
        self.name_var.trace_add("write", self._notify_change)
        self.location_var.trace_add("write", self._notify_change)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(99, weight=1)

        # Título
        title = ctk.CTkLabel(
            self,
            text="Paso 1: Información del proyecto",
            font=ctk.CTkFont(size=18, weight="bold"),
            anchor="w",
        )
        title.grid(row=0, column=0, sticky="ew", pady=(20, 20), padx=20)

        # Nombre
        ctk.CTkLabel(self, text="Nombre:", anchor="w").grid(
            row=1, column=0, sticky="ew", padx=20
        )
        self.name_entry = ctk.CTkEntry(
            self,
            textvariable=self.name_var,
            placeholder_text="MiProyecto",
        )
        self.name_entry.grid(
            row=2, column=0, sticky="ew", padx=20, pady=(0, 5)
        )

        # Mensaje de error de nombre duplicado
        self.name_error_label = ctk.CTkLabel(
            self,
            text="",
            text_color="#ff6b6b",
            font=ctk.CTkFont(size=12),
            anchor="w",
        )
        self.name_error_label.grid(
            row=3, column=0, sticky="ew", padx=20, pady=(0, 10)
        )

        # Descripción
        ctk.CTkLabel(self, text="Descripción:", anchor="w").grid(
            row=4, column=0, sticky="ew", padx=20
        )
        self.description_entry = ctk.CTkTextbox(
            self,
            height=100,
        )
        self.description_entry.grid(
            row=5, column=0, sticky="ew", padx=20, pady=(0, 15)
        )
        self.description_entry.bind(
            "<KeyRelease>", self._on_description_change
        )

        # Ubicación
        ctk.CTkLabel(self, text="Ubicación:", anchor="w").grid(
            row=6, column=0, sticky="ew", padx=20
        )
        self.location_dropdown = ctk.CTkOptionMenu(
            self,
            variable=self.location_var,
            values=["(cargando...)"],
            command=lambda _: self._on_location_change(),
        )
        self.location_dropdown.grid(
            row=7, column=0, sticky="ew", padx=20, pady=(0, 15)
        )

    # ============================================================
    # VALIDACIÓN
    # ============================================================

    def _check_duplicate(self) -> str | None:
        """Devuelve un mensaje de error si el proyecto ya existe."""
        name = self.name_var.get().strip()
        location = self.location_var.get()

        if not name or not location:
            return None

        project_path = PROJECTS_DIR / location / name

        if project_path.exists():
            return "Ya existe un proyecto con ese nombre en esa ubicación."

        return None

    def _update_name_error(self):
        """Actualiza el mensaje de error visual del campo nombre."""
        error = self._check_duplicate()
        self.name_error_label.configure(text=error or "")

    # ============================================================
    # EVENT HANDLERS
    # ============================================================

    def _on_description_change(self, event):
        self.description_var.set(self.description_entry.get("1.0", "end-1c"))
        self._notify_change()

    def _on_location_change(self):
        self._update_name_error()
        self._notify_change()

    def _notify_change(self, *args):
        self._update_name_error()
        if self.on_change:
            self.on_change()

    # ============================================================
    # API PÚBLICA
    # ============================================================

    def set_locations(self, locations: list[str]):
        if not locations:
            self.location_dropdown.configure(values=["(sin ubicaciones)"])
            return

        self.location_dropdown.configure(values=locations)
        self.location_var.set(locations[0])

    def set_default_location(self, location: str):
        """Selecciona una ubicación por defecto si existe en las opciones."""
        current_values = self.location_dropdown.cget("values")
        if location in current_values:
            self.location_var.set(location)

    def get_data(self) -> dict:
        return {
            "name": self.name_var.get().strip(),
            "description": self.description_var.get().strip(),
            "location": self.location_var.get(),
        }

    def is_valid(self) -> bool:
        data = self.get_data()

        if not data["name"]:
            return False
        if not data["description"]:
            return False
        if not data["location"]:
            return False
        if self._check_duplicate() is not None:
            return False

        return True