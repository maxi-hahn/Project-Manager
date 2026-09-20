import customtkinter as ctk


class Step3Config(ctk.CTkFrame):
    def __init__(self, master, on_change=None):
        super().__init__(master, fg_color="transparent")

        self.on_change = on_change

        self.grid_columnconfigure(0, weight=1)

        title = ctk.CTkLabel(
            self,
            text="Paso 3: Configuración técnica",
            font=ctk.CTkFont(size=18, weight="bold"),
            anchor="w",
        )
        title.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 20))

        placeholder = ctk.CTkLabel(
            self,
            text="(en construcción)",
            text_color="gray",
            anchor="w",
        )
        placeholder.grid(row=1, column=0, sticky="ew", padx=20)