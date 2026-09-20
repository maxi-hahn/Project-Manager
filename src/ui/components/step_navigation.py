import customtkinter as ctk


# ============================================================
# NAVEGACIÓN DE PASOS
# ============================================================
# Widget reutilizable con botones "Atrás" y "Siguiente".
# Se coloca al final de cada screen del wizard.
# ============================================================


class StepNavigation(ctk.CTkFrame):
    def __init__(
        self,
        master,
        on_back=None,
        on_next=None,
        next_text="Siguiente →",
        show_back=True,
    ):
        super().__init__(master, fg_color="transparent")

        self.on_back = on_back
        self.on_next = on_next

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)
        self.grid_columnconfigure(2, weight=0)

        if show_back:
            self.back_button = ctk.CTkButton(
                self,
                text="← Atrás",
                width=120,
                fg_color="gray30",
                hover_color="gray20",
                command=self._handle_back,
            )
            self.back_button.grid(row=0, column=1, padx=(0, 10))

        self.next_button = ctk.CTkButton(
            self,
            text=next_text,
            width=140,
            command=self._handle_next,
        )
        self.next_button.grid(row=0, column=2)

    def _handle_back(self):
        if self.on_back:
            self.on_back()

    def _handle_next(self):
        if self.on_next:
            self.on_next()

    def set_next_enabled(self, enabled: bool):
        """Habilita o deshabilita el botón Siguiente."""
        state = "normal" if enabled else "disabled"
        self.next_button.configure(state=state)