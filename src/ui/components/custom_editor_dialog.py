from tkinter import messagebox
import customtkinter as ctk

from src.core.editors import is_available


class CustomEditorDialog(ctk.CTkToplevel):
    def __init__(self, master, on_save=None):
        super().__init__(master)

        self.on_save = on_save

        self.title("Agregar editor personalizado")
        self.resizable(False, False)

        # Modal configuration
        self.grab_set()
        self.transient(master)

        self.name_var = ctk.StringVar()
        self.command_var = ctk.StringVar()

        self._build_ui()
        self.after(50, self._center_on_parent)

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

    def _build_ui(self):
        container = ctk.CTkFrame(self)
        container.pack(fill="both", expand=True, padx=20, pady=20)

        # Title
        ctk.CTkLabel(
            container,
            text="Agregar editor personalizado",
            font=ctk.CTkFont(size=16, weight="bold"),
            anchor="w",
        ).pack(fill="x", pady=(0, 15))

        # Nombre field
        ctk.CTkLabel(
            container,
            text="Nombre:",
            font=ctk.CTkFont(weight="bold"),
            anchor="w",
        ).pack(fill="x", pady=(5, 2))

        self.name_entry = ctk.CTkEntry(
            container,
            textvariable=self.name_var,
            placeholder_text="Ej: Notepad++, Sublime Custom",
            width=300,
        )
        self.name_entry.pack(fill="x", pady=(0, 10))

        # Comando field
        ctk.CTkLabel(
            container,
            text="Comando:",
            font=ctk.CTkFont(weight="bold"),
            anchor="w",
        ).pack(fill="x", pady=(5, 2))

        self.command_entry = ctk.CTkEntry(
            container,
            textvariable=self.command_var,
            placeholder_text="Ej: notepad++, subl, code-insiders",
            width=300,
        )
        self.command_entry.pack(fill="x", pady=(0, 20))

        # Buttons frame
        btn_frame = ctk.CTkFrame(container, fg_color="transparent")
        btn_frame.pack(fill="x")
        btn_frame.grid_columnconfigure(0, weight=1)

        cancel_btn = ctk.CTkButton(
            btn_frame,
            text="Cancelar",
            width=100,
            fg_color="gray30",
            hover_color="gray20",
            command=self.destroy,
        )
        cancel_btn.grid(row=0, column=1, padx=(0, 10))

        save_btn = ctk.CTkButton(
            btn_frame,
            text="Guardar",
            width=100,
            command=self._on_save_click,
        )
        save_btn.grid(row=0, column=2)

    def _on_save_click(self):
        name = self.name_var.get().strip()
        command = self.command_var.get().strip()

        if not name:
            messagebox.showerror(
                "Error de validación", "Ingresá un nombre para el editor.", parent=self
            )
            return

        if not command:
            messagebox.showerror(
                "Error de validación", "Ingresá el comando ejecutable.", parent=self
            )
            return

        if not is_available(command):
            messagebox.showerror(
                "Comando no disponible",
                f"El comando '{command}' no fue encontrado en el PATH del sistema.",
                parent=self,
            )
            return

        if self.on_save:
            self.on_save({"name": name, "command": command})

        self.destroy()
