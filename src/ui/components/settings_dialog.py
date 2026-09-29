import threading
from pathlib import Path
from tkinter import filedialog, messagebox
import customtkinter as ctk

from src.core.editors import get_available_known_editors
from src.ui.components.custom_editor_dialog import CustomEditorDialog
from src.ui.components.editor_instructions_dialog import EditorInstructionsDialog


class SettingsDialog(ctk.CTkToplevel):
    def __init__(
        self,
        master,
        config_manager,
        is_first_run=False,
        on_save=None,
        on_cancel=None,
        on_templates_downloaded=None,
    ):
        super().__init__(master)

        self.config_manager = config_manager
        self.is_first_run = is_first_run
        self.on_save = on_save
        self.on_cancel = on_cancel
        self.on_templates_downloaded = on_templates_downloaded

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

        self.saved_editors = config.get("editors", [])
        self.custom_editors = list(config.get("custom_editors", []))
        self.known_editor_vars = {}
        self.custom_editor_vars = {}

        self.auto_install_var = ctk.BooleanVar(
            value=config.get("auto_install_dependencies", False)
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

        scroll_frame = ctk.CTkScrollableFrame(self, width=560, height=540)
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

        # 4b. Download templates sub-section
        dl_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        dl_frame.pack(fill="x", padx=10, pady=(0, 10))

        dl_title = ctk.CTkLabel(
            dl_frame,
            text="¿No tenés templates?",
            font=ctk.CTkFont(size=12, weight="bold"),
            anchor="w",
        )
        dl_title.pack(fill="x", pady=(0, 4))

        self.download_templates_btn = ctk.CTkButton(
            dl_frame,
            text="⬇ Descargar templates oficiales",
            command=self._on_download_templates_click,
            width=220,
        )
        self.download_templates_btn.pack(anchor="w", pady=(0, 4))

        self.download_help_label = ctk.CTkLabel(
            dl_frame,
            text="",
            font=ctk.CTkFont(size=11),
            text_color="gray",
            anchor="w",
        )
        self.download_help_label.pack(fill="x")
        self._update_download_templates_button_state()

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

        # 6. Editores de código Section
        ctk.CTkLabel(
            scroll_frame,
            text="Editores de código",
            font=ctk.CTkFont(weight="bold"),
            anchor="w",
        ).pack(fill="x", padx=10, pady=(5, 2))

        self.editors_container = ctk.CTkFrame(scroll_frame)
        self.editors_container.pack(fill="x", padx=10, pady=(0, 10))

        self._render_editors_section()

        # 7. Auto-install Dependencies Checkbox
        ctk.CTkLabel(
            scroll_frame,
            text="Instalar dependencias automáticamente al crear:",
            font=ctk.CTkFont(weight="bold"),
            anchor="w",
        ).pack(fill="x", padx=10, pady=(5, 2))

        auto_install_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        auto_install_frame.pack(fill="x", padx=10, pady=(0, 15))

        self.auto_install_cb = ctk.CTkCheckBox(
            auto_install_frame,
            text="",
            variable=self.auto_install_var,
            width=24,
        )
        self.auto_install_cb.pack(side="left", padx=(0, 5))

        auto_install_explanation = ctk.CTkLabel(
            auto_install_frame,
            text="(deja el proyecto listo para arrancar, pero demora mucho más la creación)",
            font=ctk.CTkFont(size=11),
            text_color="gray",
            anchor="w",
        )
        auto_install_explanation.pack(side="left")

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

    def _render_editors_section(self):
        """Renders known available editors and custom editors with action buttons."""
        for widget in self.editors_container.winfo_children():
            widget.destroy()

        available_known = get_available_known_editors()

        if available_known:
            for editor in available_known:
                key = editor["key"]
                name = editor["name"]
                if key not in self.known_editor_vars:
                    is_selected = key in self.saved_editors
                    self.known_editor_vars[key] = ctk.BooleanVar(value=is_selected)

                cb = ctk.CTkCheckBox(
                    self.editors_container,
                    text=name,
                    variable=self.known_editor_vars[key],
                )
                cb.pack(fill="x", padx=10, pady=4)
        else:
            no_avail_label = ctk.CTkLabel(
                self.editors_container,
                text="No se detectaron editores conocidos en el PATH del sistema.",
                text_color="gray",
                font=ctk.CTkFont(size=11),
                anchor="w",
            )
            no_avail_label.pack(fill="x", padx=10, pady=4)

        if self.custom_editors:
            for c_editor in self.custom_editors:
                cmd = c_editor["command"]
                name = c_editor["name"]
                if cmd not in self.custom_editor_vars:
                    self.custom_editor_vars[cmd] = ctk.BooleanVar(value=True)

                row_frame = ctk.CTkFrame(self.editors_container, fg_color="transparent")
                row_frame.pack(fill="x", padx=10, pady=2)
                row_frame.grid_columnconfigure(0, weight=1)

                cb = ctk.CTkCheckBox(
                    row_frame,
                    text=name,
                    variable=self.custom_editor_vars[cmd],
                )
                cb.grid(row=0, column=0, sticky="w")

                del_btn = ctk.CTkButton(
                    row_frame,
                    text="✕",
                    width=26,
                    height=24,
                    fg_color="#ff4d4d",
                    hover_color="#cc0000",
                    command=lambda c=c_editor: self._remove_custom_editor(c),
                )
                del_btn.grid(row=0, column=1, sticky="e")

        btn_box = ctk.CTkFrame(self.editors_container, fg_color="transparent")
        btn_box.pack(fill="x", padx=10, pady=(10, 8))

        add_custom_btn = ctk.CTkButton(
            btn_box,
            text="Agregar editor personalizado",
            command=self._open_custom_editor_dialog,
            width=190,
        )
        add_custom_btn.pack(side="left", padx=(0, 10))

        help_btn = ctk.CTkButton(
            btn_box,
            text="¿No ves tu editor? Ver cómo habilitarlo",
            command=self._open_instructions_dialog,
            fg_color="transparent",
            border_width=1,
            text_color=("gray10", "gray90"),
            width=220,
        )
        help_btn.pack(side="left")

    def _remove_custom_editor(self, editor_dict):
        if editor_dict in self.custom_editors:
            self.custom_editors.remove(editor_dict)
            cmd = editor_dict.get("command")
            if cmd in self.custom_editor_vars:
                del self.custom_editor_vars[cmd]
            self._render_editors_section()

    def _open_custom_editor_dialog(self):
        CustomEditorDialog(self, on_save=self._on_custom_editor_added)

    def _on_custom_editor_added(self, new_editor):
        exists = any(e["command"] == new_editor["command"] for e in self.custom_editors)
        if not exists:
            self.custom_editors.append(new_editor)
            self.custom_editor_vars[new_editor["command"]] = ctk.BooleanVar(value=True)
            self._render_editors_section()

    def _open_instructions_dialog(self):
        EditorInstructionsDialog(self)

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
            self._update_download_templates_button_state()

    def _update_download_templates_button_state(self):
        if self.resources_root_path:
            self.download_templates_btn.configure(state="normal")
            self.download_help_label.configure(
                text="ℹ Se descargará la última versión desde GitHub."
            )
        else:
            self.download_templates_btn.configure(state="disabled")
            self.download_help_label.configure(
                text="Primero elegí la carpeta de recursos."
            )

    def _on_download_templates_click(self):
        if not self.resources_root_path:
            return

        dest = self.resources_root_path
        confirm = messagebox.askyesno(
            "Descargar templates",
            f"Se descargarán los templates en:\n{dest}\n\n¿Continuar?",
            parent=self,
        )
        if not confirm:
            return

        templates_folder = dest / "TEMPLATES"
        overwrite = False
        if templates_folder.exists() and templates_folder.is_dir():
            overwrite_confirm = messagebox.askyesno(
                "Sobreescribir templates",
                "La carpeta ya contiene templates. ¿Sobreescribir?",
                parent=self,
            )
            if not overwrite_confirm:
                return
            overwrite = True

        DownloadProgressModal(
            self,
            destination=dest,
            overwrite=overwrite,
            on_success=self._on_download_success,
        )

    def _on_download_success(self):
        self._check_resources_warning()
        if self.on_templates_downloaded:
            self.on_templates_downloaded(self.resources_root_path)

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

        selected_editors = [
            key for key, var in self.known_editor_vars.items() if var.get()
        ]

        selected_custom_editors = [
            e
            for e in self.custom_editors
            if self.custom_editor_vars.get(
                e["command"], ctk.BooleanVar(value=True)
            ).get()
        ]

        config = {
            "user_name": user_name,
            "projects_root": str(self.projects_root_path),
            "resources_root": str(self.resources_root_path),
            "default_location": default_loc,
            "editors": selected_editors,
            "custom_editors": selected_custom_editors,
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


class DownloadProgressModal(ctk.CTkToplevel):
    def __init__(
        self, master, destination: Path, overwrite: bool = False, on_success=None
    ):
        super().__init__(master)
        self.destination = destination
        self.overwrite = overwrite
        self.on_success = on_success

        self.title("Descargando templates")
        self.geometry("460x320")
        self.resizable(False, False)

        self.grab_set()
        self.transient(master)

        self.grid_columnconfigure(0, weight=1)

        # Header Title
        header = ctk.CTkLabel(
            self,
            text="Descargando templates oficiales",
            font=ctk.CTkFont(size=15, weight="bold"),
            anchor="w",
        )
        header.pack(fill="x", padx=20, pady=(15, 10))

        # Spinner
        self.progress_bar = ctk.CTkProgressBar(self, mode="indeterminate")
        self.progress_bar.pack(fill="x", padx=20, pady=(0, 10))
        self.progress_bar.start()

        # Status area
        self.status_box = ctk.CTkTextbox(
            self,
            font=ctk.CTkFont(size=11, family="Consolas"),
            height=110,
            activate_scrollbars=True,
        )
        self.status_box.pack(fill="both", expand=True, padx=20, pady=(0, 10))
        self.status_box.insert("1.0", "Descargando templates...\n")
        self.status_box.configure(state="disabled")

        # Help message below status
        self.help_label = ctk.CTkLabel(
            self,
            text=(
                "Revisá la página del proyecto cada tanto para ver si hay una versión nueva. "
                "Para actualizar, simplemente volvé a tocar este botón."
            ),
            font=ctk.CTkFont(size=11),
            text_color="gray",
            wraplength=420,
            justify="left",
            anchor="w",
        )
        self.help_label.pack(fill="x", padx=20, pady=(0, 10))

        # Finalizar button (disabled initially)
        self.finish_btn = ctk.CTkButton(
            self,
            text="Finalizar",
            width=110,
            state="disabled",
            command=self._on_finish_click,
        )
        self.finish_btn.pack(pady=(0, 15))

        self.after(50, self._center_on_parent)

        threading.Thread(target=self._run_download, daemon=True).start()

    def _center_on_parent(self):
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

    def _append_status(self, message: str):
        self.status_box.configure(state="normal")
        self.status_box.insert("end", message + "\n")
        self.status_box.see("end")
        self.status_box.configure(state="disabled")

    def log(self, message: str):
        self.after(0, lambda: self._append_status(message))

    def _run_download(self):
        from src.core.templates_downloader import download_templates

        res = download_templates(
            destination=self.destination,
            logger=self.log,
            overwrite=self.overwrite,
        )
        self.after(0, lambda: self._on_download_finished(res))

    def _on_download_finished(self, success: bool):
        self.progress_bar.stop()
        self.progress_bar.pack_forget()
        self.finish_btn.configure(state="normal")

        if success and self.on_success:
            self.on_success()

    def _on_finish_click(self):
        self.destroy()
