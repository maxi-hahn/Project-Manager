import customtkinter as ctk

from src.core.editors import KNOWN_EDITORS, get_instructions


class EditorInstructionsDialog(ctk.CTkToplevel):
    def __init__(self, master):
        super().__init__(master)

        self.title("Cómo habilitar el comando de tu editor")
        self.resizable(False, False)

        # Modal configuration
        self.grab_set()
        self.transient(master)

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
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Header Title
        title_label = ctk.CTkLabel(
            self,
            text="Cómo habilitar el comando de tu editor",
            font=ctk.CTkFont(size=16, weight="bold"),
            anchor="w",
        )
        title_label.grid(row=0, column=0, sticky="ew", padx=20, pady=(15, 10))

        # Instructions scrollable frame
        scroll_frame = ctk.CTkScrollableFrame(self, width=500, height=380)
        scroll_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 15))
        scroll_frame.grid_columnconfigure(0, weight=1)

        instructions = get_instructions()

        for editor in KNOWN_EDITORS:
            key = editor["key"]
            name = editor["name"]
            text = instructions.get(key, "")

            item_frame = ctk.CTkFrame(scroll_frame)
            item_frame.pack(fill="x", pady=5, padx=5)

            ctk.CTkLabel(
                item_frame,
                text=name,
                font=ctk.CTkFont(weight="bold", size=13),
                anchor="w",
            ).pack(fill="x", padx=10, pady=(6, 2))

            ctk.CTkLabel(
                item_frame,
                text=text,
                font=ctk.CTkFont(size=12),
                text_color="gray",
                anchor="w",
                justify="left",
                wraplength=450,
            ).pack(fill="x", padx=10, pady=(0, 6))

        # Close button frame
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=(0, 15))
        btn_frame.grid_columnconfigure(0, weight=1)

        close_btn = ctk.CTkButton(
            btn_frame,
            text="Cerrar",
            width=100,
            command=self.destroy,
        )
        close_btn.grid(row=0, column=1)
