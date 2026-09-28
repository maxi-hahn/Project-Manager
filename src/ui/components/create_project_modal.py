import shutil
import subprocess
import threading
from pathlib import Path

import customtkinter as ctk

from src.core.editors import get_editor_by_key, open_in_editor
from src.logic.project_builder import build_project

# ============================================================
# MODAL DE CREACIÓN DE PROYECTO
# ============================================================
# Flujo de tres estados:
#
#   1. Confirmación  → muestra resumen y selector de editor.
#   2. Progreso      → oculta selector y botón Cancelar,
#                      muestra logs en tiempo real.
#   3. Finalizado    → habilita el botón Cerrar.
# ============================================================

MODAL_WIDTH = 600
MODAL_HEIGHT_CONFIRM = 280
MODAL_HEIGHT_PROGRESS = 500


class CreateProjectModal(ctk.CTkToplevel):
    def __init__(self, master, project_data: dict):
        super().__init__(master)

        self.project_data = project_data

        # Path to the created project (set after a successful build)
        self._project_path: Path | None = None

        # Whether the build succeeded (used to decide whether to close the app on Close)
        self._success: bool = False

        # Map option labels to execution commands
        self._editor_options_map: dict[str, str | None] = {}

        # Extract display data
        info = project_data.get("info", {})
        template = project_data.get("template", {})
        self._project_name = info.get("name", "")
        self._template_name = template.get("name", "")

        # Window setup
        self.title("Confirmar creación")
        self.resizable(False, False)

        # Block input to the main window
        self.grab_set()

        # Build UI in confirmation state, then center
        self._build_ui()
        self.after(50, self._center_on_parent)

    # ============================================================
    # UTILITIES
    # ============================================================

    def _center_on_parent(self):
        """Centers the modal window relative to the parent window."""
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

    # ============================================================
    # UI CONSTRUCTION
    # ============================================================

    def _build_ui(self):
        """Builds the full modal layout (confirmation state)."""

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # --------------------------------------------------------
        # Summary label
        # --------------------------------------------------------

        summary_text = (
            f"Proyecto:  {self._project_name}\n"
            f"Template:  {self._template_name}"
        )

        self.summary_label = ctk.CTkLabel(
            self,
            text=summary_text,
            font=ctk.CTkFont(size=13),
            justify="left",
            anchor="w",
        )
        self.summary_label.grid(
            row=0, column=0, sticky="ew", padx=24, pady=(24, 12)
        )

        # --------------------------------------------------------
        # Editor selection dropdown
        # --------------------------------------------------------

        editor_keys = self.project_data.get("editors", [])
        custom_editors = self.project_data.get("custom_editors", [])

        self._editor_options_map = {"No abrir": None}
        options_list = ["No abrir"]

        for key in editor_keys:
            ed = get_editor_by_key(key)
            if ed:
                name = ed["name"]
                cmd = ed["command"]
                options_list.append(name)
                self._editor_options_map[name] = cmd

        for c_ed in custom_editors:
            name = c_ed.get("name")
            cmd = c_ed.get("command")
            if name and cmd and name not in self._editor_options_map:
                options_list.append(name)
                self._editor_options_map[name] = cmd

        self.editor_var = ctk.StringVar(value="No abrir")

        self.editor_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.editor_frame.grid(
            row=1, column=0, sticky="w", padx=24, pady=(0, 16)
        )

        has_configured_editors = len(options_list) > 1

        if has_configured_editors:
            ctk.CTkLabel(
                self.editor_frame,
                text="¿Abrir con qué editor?",
                font=ctk.CTkFont(size=12, weight="bold"),
                anchor="w",
            ).pack(side="top", anchor="w", pady=(0, 4))

        self.editor_dropdown = ctk.CTkOptionMenu(
            self.editor_frame,
            variable=self.editor_var,
            values=options_list,
        )
        self.editor_dropdown.pack(side="top", anchor="w")

        # --------------------------------------------------------
        # Log textbox (hidden initially, shown during progress)
        # --------------------------------------------------------

        self.log_textbox = ctk.CTkTextbox(
            self,
            state="disabled",
            font=ctk.CTkFont(size=12, family="Consolas"),
            wrap="word",
        )
        # Not placed in the grid until creation begins

        # --------------------------------------------------------
        # Button row
        # --------------------------------------------------------

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.grid(row=3, column=0, sticky="ew", padx=24, pady=(0, 20))
        btn_frame.grid_columnconfigure(0, weight=1)

        self.cancel_button = ctk.CTkButton(
            btn_frame,
            text="Cancelar",
            width=120,
            fg_color="gray30",
            hover_color="gray20",
            command=self._on_cancel,
        )
        self.cancel_button.grid(row=0, column=1, padx=(0, 10))

        self.action_button = ctk.CTkButton(
            btn_frame,
            text="Crear proyecto",
            width=140,
            command=self._on_create,
        )
        self.action_button.grid(row=0, column=2)

        # Apply confirmation-state geometry
        self.geometry(f"{MODAL_WIDTH}x{MODAL_HEIGHT_CONFIRM}")

    # ============================================================
    # STATE TRANSITIONS
    # ============================================================

    def _enter_progress_state(self):
        """Transitions to progress state: shows the log area, hides controls."""

        self.title("Creando proyecto...")

        # Hide the editor selector frame and Cancel button
        if hasattr(self, "editor_frame") and self.editor_frame.winfo_manager():
            self.editor_frame.grid_forget()
        self.cancel_button.grid_forget()

        # Disable the action button while the build is running
        self.action_button.configure(text="Cerrar", state="disabled")

        # Show the log textbox
        self.log_textbox.grid(
            row=2, column=0, sticky="nsew", padx=24, pady=(0, 12)
        )

        # Expand to progress-state size and re-center
        self.geometry(f"{MODAL_WIDTH}x{MODAL_HEIGHT_PROGRESS}")
        self.after(50, self._center_on_parent)

    def _enter_finished_state(
        self,
        success: bool,
        message: str,
        project_path: Path | None,
    ):
        """Transitions to finished state: appends result and enables close button."""

        self._project_path = project_path
        self._success = success

        if success:
            self.title("Proyecto creado")
            final_message = f"\n✓ Proyecto creado correctamente\n{project_path}"
        else:
            self.title("Error al crear el proyecto")
            final_message = f"\n✗ {message}"

        self._append_log(final_message)

        # Show a modal error notification on failure
        if not success:
            from tkinter import messagebox

            self.after(
                100,
                lambda: messagebox.showerror(
                    "Error al crear el proyecto",
                    message or "Ocurrió un error inesperado.",
                    parent=self,
                ),
            )

        # Enable the close button
        self.action_button.configure(state="normal", command=self._on_close)

    # ============================================================
    # LOGGING
    # ============================================================

    def _append_log(self, message: str):
        """Appends a message to the log textbox. Must be called from the main thread."""
        self.log_textbox.configure(state="normal")
        self.log_textbox.insert("end", message + "\n")
        self.log_textbox.see("end")
        self.log_textbox.configure(state="disabled")

    def _thread_safe_log(self, message: str):
        """Logger callback that can be called safely from a background thread."""
        self.after(0, self._append_log, message)

    # ============================================================
    # BUTTON HANDLERS
    # ============================================================

    def _on_cancel(self):
        """Closes the modal without performing any action."""
        self.destroy()

    def _on_create(self):
        """Starts project creation in a background thread."""
        self._enter_progress_state()

        thread = threading.Thread(target=self._run_build, daemon=True)
        thread.start()

    def _on_close(self):
        """Closes the modal. If the build succeeded, also closes the app."""

        selected_option = self.editor_var.get()
        command = self._editor_options_map.get(selected_option)

        # Attempt to open the selected editor when project creation succeeded
        if (
            self._success
            and command is not None
            and self._project_path is not None
        ):
            launched = open_in_editor(command, str(self._project_path))
            if not launched:
                self._append_log(
                    f"\n⚠ No se pudo abrir {selected_option} automáticamente."
                )

        # Release the modal grab and destroy it
        try:
            self.grab_release()
        except Exception:
            pass
        self.destroy()

        # If the build failed, keep the main app open so the user can retry
        if self._success:
            self.master.quit()
            self.master.destroy()

    # ============================================================
    # PROJECT CREATION (runs in background thread)
    # ============================================================

    def _run_build(self):
        """Calls build_project and schedules the UI update on the main thread."""

        # Wrap the entire flow so any unexpected error still lands the modal
        # in the finished state instead of freezing the UI.
        try:
            info = self.project_data.get("info", {})
            template = self.project_data.get("template", {})
            config = self.project_data.get("config", {})
            projects_root = self.project_data.get("projects_root")
            default_location = self.project_data.get("default_location", "")
            auto_install = self.project_data.get(
                "auto_install_dependencies", True
            )

            location = info.get("location", default_location)

            if projects_root:
                projects_dir = Path(projects_root) / location
            else:
                from config import PROJECTS_DIR

                projects_dir = Path(PROJECTS_DIR) / location

            result = build_project(
                projects_dir=projects_dir,
                template_path=Path(template["path"]),
                project_name=info.get("name", ""),
                description=info.get("description", ""),
                tools=config.get("tools", []),
                features=config.get("features", []),
                environments=config.get("environments", []),
                technologies=config.get("technologies", []),
                template_language=template.get("language", "").lower(),
                template_runtime=template.get("runtime", "python").lower(),
                install_dependencies=auto_install,
                logger=self._thread_safe_log,
            )

            success = result.success
            error_message = result.error_message
            project_path = result.project_path

        except Exception as error:
            # Catch anything that escaped build_project
            success = False
            error_message = f"Error inesperado: {error}"
            project_path = None

        # Hand off the result to the main thread
        self.after(
            0,
            self._enter_finished_state,
            success,
            error_message,
            project_path,
        )
