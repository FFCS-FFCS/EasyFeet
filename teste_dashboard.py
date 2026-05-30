"""
Protótipo do dashboard EasyFeet.

Uso: duplo clique em EF_teste_dashboard.bat (pasta oficial OneDrive).
"""

from __future__ import annotations

import customtkinter as ctk

from easyfeet.dashboard_ui import render_dashboard
from easyfeet.db import SessionLocal, init_db
from easyfeet.services import EasyFeetService

UI_FONT_PT = 15


class TesteDashboardApp(ctk.CTk):
    def __init__(self, service: EasyFeetService) -> None:
        super().__init__()
        self.service = service
        self.title("EasyFeet — Teste dashboard")
        self.geometry("900x520")
        self.minsize(720, 420)
        ctk.set_appearance_mode("light")

        root = ctk.CTkFrame(self, fg_color="#f5f5f5")
        root.pack(fill="both", expand=True, padx=16, pady=16)
        root.grid_columnconfigure(0, weight=1)
        root.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            root,
            text="Dashboard (protótipo)",
            font=ctk.CTkFont(size=UI_FONT_PT, weight="bold"),
        ).grid(row=0, column=0, sticky="w", padx=4, pady=(0, 12))

        dash = ctk.CTkFrame(root, fg_color="transparent")
        dash.grid(row=1, column=0, sticky="nsew")
        render_dashboard(dash, service, font_pt=UI_FONT_PT)


def main() -> None:
    init_db()
    with SessionLocal() as session:
        app = TesteDashboardApp(EasyFeetService(session))
        app.mainloop()


if __name__ == "__main__":
    main()
