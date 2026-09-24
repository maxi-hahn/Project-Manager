import customtkinter as ctk
from pathlib import Path
from tkinter import filedialog, messagebox

EDITOR_OPTIONS = [
    ("VS Code", "vscode"),
    ("PyCharm", "pycharm"),
    ("Cursor", "cursor"),
    ("Ninguno", "none"),
]
EDITOR_LABEL_TO_VALUE = {label: val for label, val in EDITOR_OPTIONS}
EDITOR_VALUE_TO_LABEL = {val: label for label, val in EDITOR_OPTIONS}


class SettingsDialog(ctk.CTkToplevel):
    def __init__(
        self,
        master,
        config_manager,
        is_first_run=False,
        on_save=None,
        on_cancel=None,
    ):
        super().__init__(master)

        self.config_manager = config_manager
        self.is_first_run = is_first_run
        self.on_save = on_save
        self.on_cancel = on_cancel

        # Title & window configuration
        title_text = "Configuración inicial" if is_first_run else "Configuración"
        self.title(title_text)
        self.resizable(False, False)

        # Modal window setup
        self.grab_set()
        self.transient(master)
        self.protocol("WM_DELETE_WINDOW", self._on_wm_delete)

        # State variables
        config = self.config_manager.get_all()
        self.user_name_var = ctk.StringVar(value=config.get("user_name", ""))

        proj_root_str = config.get("projects_root", "")
        self.projects_root_path = Path(proj_root_str) if proj_root_str else None

        res_root_str = config.get("resources_root", "")
        self.resources_root_path = Path(res_root_str) if res_root_str else None

        self.default_location_var = ctk.StringVar(
            value=config.get("default_location", "")
        )

        current_editor_val = config.get("default_editor", "vscode")
        current_editor_label = EDITOR_VALUE_TO_LABEL.get(
            current_editor_val, "VS Code"
        )
        self.editor_var = ctk.StringVar(value=current_editor_label)

        self.auto_install_var = ctk.BooleanVar(
            value=config.get("auto_install_dependencies", True)
        )

        self._build_ui(title_text)
        self._update_location_dropdown()
        self._check_resources_warning()

        self.after(50, self._center_on_parent)

    def _center_on_parent(self):
        """Centers the dialog relative to the parent window."""
        self.update_idletasks()
        parent = self.master
        px = parent.winfo_x()
        py = parent.winfo_y()
        pw = parent.winfo_width()
        ph = parent.winfo_height()

        mw = self.winfo_width()
        mh = self.winfo_height()

        x = px + (pw - mw) // 2
        y = py + (ph - mh) // 2
        self.geometry(f"+{x}+{y}")

    def _build_ui(self, title_text: str):
        """Builds the dialog components inside a scrollable frame."""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        scroll_frame = ctk.CTkScrollableFrame(self, width=540, height=520)
        scroll_frame.grid(row=0, column=0, sticky="nsew", padx=15, pady=15)
        scroll_frame.grid_columnconfigure(0, weight=1)

        # 1. Header Title
        title_label = ctk.CTkLabel(
            scroll_frame,
            text=title_text,
            font=ctk.CTkFont(size=18, weight="bold"),
            anchor="w",
        )
        title_label.pack(fill="x", padx=10, pady=(10, 15))

        # 2. User Name Field
        ctk.CTkLabel(
            scroll_frame,
            text="Nombre:",
            font=ctk.CTkFont(weight="bold"),
            anchor="w",
        ).pack(fill="x", padx=10, pady=(5, 2))

        self.name_entry = ctk.CTkEntry(
            scroll_frame,
            textvariable=self.user_name_var,
            placeholder_text="Tu nombre",
        )
        self.name_entry.pack(fill="x", padx=10, pady=(0, 10))

        # 3. Projects Root Field
        ctk.CTkLabel(
            scroll_frame,
            text="Carpeta de proyectos:",
            font=ctk.CTkFont(weight="bold"),
            anchor="w",
        ).pack(fill="x", padx=10, pady=(5, 2))

        proj_frame = ctk.CTkFrame(scroll_frame)
        proj_frame.pack(fill="x", padx=10, pady=(0, 2))
        proj_frame.grid_columnconfigure(0, weight=1)

        proj_path_text = (
            str(self.projects_root_path)
            if self.projects_root_path
            else "Sin seleccionar"
        )
        self.proj_path_label = ctk.CTkLabel(
            proj_frame,
            text=proj_path_text,
            anchor="w",
            text_color="white" if self.projects_root_path else "gray",
        )
        self.proj_path_label.grid(row=0, column=0, padx=10, pady=8, sticky="w")

        proj_btn = ctk.CTkButton(
            proj_frame,
            text="Elegir carpeta",
            width=120,
            command=self._pick_projects_root,
        )
        proj_btn.grid(row=0, column=1, padx=10, pady=8, sticky="e")

        proj_help = ctk.CTkLabel(
            scroll_frame,
            text=(
                "Elegí una carpeta que contenga subcarpetas (por ejemplo, ACTIVOS, "
                "PERSONALES, ARCHIVADOS). Cada subcarpeta será una ubicación donde se crearán los proyectos."
            ),
            font=ctk.CTkFont(size=11),
            text_color="gray",
            justify="left",
            anchor="w",
            wraplength=480,
        )
        proj_help.pack(fill="x", padx=10, pady=(0, 2))

        self.proj_warning_label = ctk.CTkLabel(
            scroll_frame,
            text="",
            font=ctk.CTkFont(size=11),
            text_color="#ff6b6b",
            anchor="w",
        )
        self.proj_warning_label.pack(fill="x", padx=10, pady=(0, 10))

        # 4. Resources Root Field
        ctk.CTkLabel(
            scroll_frame,
            text="Carpeta de recursos:",
            font=ctk.CTkFont(weight="bold"),
            anchor="w",
        ).pack(fill="x", padx=10, pady=(5, 2))

        res_frame = ctk.CTkFrame(scroll_frame)
        res_frame.pack(fill="x", padx=10, pady=(0, 2))
        res_frame.grid_columnconfigure(0, weight=1)

        res_path_text = (
            str(self.resources_root_path)
            if self.resources_root_path
            else "Sin seleccionar"
        )
        self.res_path_label = ctk.CTkLabel(
            res_frame,
            text=res_path_text,
            anchor="w",
            text_color="white" if self.resources_root_path else "gray",
        )
        self.res_path_label.grid(row=0, column=0, padx=10, pady=8, sticky="w")

        res_btn = ctk.CTkButton(
            res_frame,
            text="Elegir carpeta",
            width=120,
            command=self._pick_resources_root,
        )
        res_btn.grid(row=0, column=1, padx=10, pady=8, sticky="e")

        res_help = ctk.CTkLabel(
            scroll_frame,
            text=(
                "Elegí la carpeta que contiene tus recursos (TEMPLATES, TOOLS, "
                "FEATURES, ENVIRONMENTS, TECHNOLOGIES)."
            ),
            font=ctk.CTkFont(size=11),
            text_color="gray",
            justify="left",
            anchor="w",
            wraplength=480,
        )
        res_help.pack(fill="x", padx=10, pady=(0, 2))

        self.res_warning_label = ctk.CTkLabel(
            scroll_frame,
            text="",
            font=ctk.CTkFont(size=11),
            text_color="#ff6b6b",
            anchor="w",
        )
        self.res_warning_label.pack(fill="x", padx=10, pady=(0, 10))

        # 5. Default Location Field
        ctk.CTkLabel(
            scroll_frame,
            text="Ubicación por defecto:",
            font=ctk.CTkFont(weight="bold"),
            anchor="w",
        ).pack(fill="x", padx=10, pady=(5, 2))

        self.location_dropdown = ctk.CTkOptionMenu(
            scroll_frame,
            variable=self.default_location_var,
            values=["(sin ubicaciones)"],
        )
        self.location_dropdown.pack(fill="x", padx=10, pady=(0, 10))

        # 6. Preferred Editor Field
        ctk.CTkLabel(
            scroll_frame,
            text="Editor preferido:",
            font=ctk.CTkFont(weight="bold"),
            anchor="w",
        ).pack(fill="x", padx=10, pady=(5, 2))

        self.editor_dropdown = ctk.CTkOptionMenu(
            scroll_frame,
            variable=self.editor_var,
            values=[label for label, _ in EDITOR_OPTIONS],
        )
        self.editor_dropdown.pack(fill="x", padx=10, pady=(0, 10))

        # 7. Auto-install Dependencies Checkbox
        self.auto_install_cb = ctk.CTkCheckBox(
            scroll_frame,
            text="Instalar dependencias automáticamente al crear",
            variable=self.auto_install_var,
        )
        self.auto_install_cb.pack(fill="x", padx=10, pady=(10, 15))

        # 8. Buttons Row
        btn_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        btn_frame.pack(fill="x", padx=10, pady=(10, 10))
        btn_frame.grid_columnconfigure(0, weight=1)

        if not self.is_first_run:
            cancel_btn = ctk.CTkButton(
                btn_frame,
                text="Cancelar",
                width=110,
                fg_color="gray30",
                hover_color="gray20",
                command=self._on_cancel_click,
            )
            cancel_btn.grid(row=0, column=1, padx=(0, 10))

        save_btn = ctk.CTkButton(
            btn_frame,
            text="Guardar",
            width=120,
            command=self._on_save_click,
        )
        save_btn.grid(row=0, column=2)

    def _update_location_dropdown(self):
        """Updates the default_location dropdown based on current projects_root subfolders."""
        subfolders = []
        if (
            self.projects_root_path
            and self.projects_root_path.exists()
            and self.projects_root_path.is_dir()
        ):
            try:
                subfolders = [
                    f.name for f in self.projects_root_path.iterdir() if f.is_dir()
                ]
            except OSError:
                subfolders = []

        if subfolders:
            self.location_dropdown.configure(state="normal", values=subfolders)
            current = self.default_location_var.get()
            if current not in subfolders:
                self.default_location_var.set(subfolders[0])
            self.proj_warning_label.configure(text="")
        else:
            self.location_dropdown.configure(
                values=["(sin ubicaciones)"], state="disabled"
            )
            self.default_location_var.set("(sin ubicaciones)")
            if self.projects_root_path:
                self.proj_warning_label.configure(
                    text="La carpeta seleccionada no contiene subcarpetas de ubicación."
                )
            else:
                self.proj_warning_label.configure(text="")

    def _check_resources_warning(self):
        """Checks if the resources folder contains all required resource subdirectories."""
        if not self.resources_root_path:
            self.res_warning_label.configure(text="")
            return

        if not self.resources_root_path.exists():
            self.res_warning_label.configure(text="La carpeta de recursos no existe.")
            return

        required = [
            "TEMPLATES",
            "TOOLS",
            "FEATURES",
            "ENVIRONMENTS",
            "TECHNOLOGIES",
        ]
        missing = [
            folder
            for folder in required
            if not (self.resources_root_path / folder).is_dir()
        ]

        if missing:
            self.res_warning_label.configure(
                text=f"Faltan subcarpetas obligatorias: {', '.join(missing)}"
            )
        else:
            self.res_warning_label.configure(text="")

    def _pick_projects_root(self):
        chosen = filedialog.askdirectory(
            parent=self, title="Seleccionar carpeta de proyectos"
        )
        if chosen:
            self.projects_root_path = Path(chosen)
            self.proj_path_label.configure(
                text=str(self.projects_root_path), text_color="white"
            )
            self._update_location_dropdown()

    def _pick_resources_root(self):
        chosen = filedialog.askdirectory(
            parent=self, title="Seleccionar carpeta de recursos"
        )
        if chosen:
            self.resources_root_path = Path(chosen)
            self.res_path_label.configure(
                text=str(self.resources_root_path), text_color="white"
            )
            self._check_resources_warning()

    def _on_save_click(self):
        user_name = self.user_name_var.get().strip()
        if not user_name:
            messagebox.showerror(
                "Error de validación", "Ingresá tu nombre.", parent=self
            )
            return

        if not self.projects_root_path or not self.projects_root_path.exists():
            messagebox.showerror(
                "Error de validación",
                "Seleccioná una carpeta de proyectos válida.",
                parent=self,
            )
            return

        subfolders = []
        try:
            subfolders = [
                f.name for f in self.projects_root_path.iterdir() if f.is_dir()
            ]
        except OSError:
            subfolders = []

        if not subfolders:
            messagebox.showerror(
                "Error de validación",
                "La carpeta de proyectos debe contener al menos una subcarpeta de ubicación.",
                parent=self,
            )
            return

        if not self.resources_root_path or not self.resources_root_path.exists():
            messagebox.showerror(
                "Error de validación",
                "Seleccioná una carpeta de recursos válida.",
                parent=self,
            )
            return

        default_loc = self.default_location_var.get()
        if not default_loc or default_loc == "(sin ubicaciones)":
            messagebox.showerror(
                "Error de validación",
                "Seleccioná una ubicación por defecto.",
                parent=self,
            )
            return

        config = {
            "user_name": user_name,
            "projects_root": str(self.projects_root_path),
            "resources_root": str(self.resources_root_path),
            "default_location": default_loc,
            "default_editor": EDITOR_LABEL_TO_VALUE.get(
                self.editor_var.get(), "vscode"
            ),
            "auto_install_dependencies": self.auto_install_var.get(),
        }

        self.config_manager.save(config)

        if self.on_save:
            self.on_save()

        self.destroy()

    def _on_cancel_click(self):
        if self.on_cancel:
            self.on_cancel()
        self.destroy()

    def _on_wm_delete(self):
        if self.is_first_run:
            if self.on_cancel:
                self.on_cancel()
            else:
                self.destroy()
        else:
            self.destroy()
