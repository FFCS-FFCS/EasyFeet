"""Componentes reutilizáveis do dashboard (app principal e protótipo de teste)."""

from __future__ import annotations

import customtkinter as ctk

from easyfeet.services import EasyFeetService

DASHBOARD_ULTIMOS_PACIENTES = 3


def render_dashboard(parent: ctk.CTkFrame, service: EasyFeetService, *, font_pt: int = 15) -> None:
    parent.grid_columnconfigure((0, 1), weight=1)

    total_clientes = len(service.clientes.listar())
    ultimos = service.clientes.listar_ultimos_por_cadastro(DASHBOARD_ULTIMOS_PACIENTES)

    cards = [
        ("Total de pacientes", f"{total_clientes}", "Pacientes cadastrados"),
        ("Pendencias", "0", "Laudos pendentes (MVP)"),
        ("Atalhos", "4", "Novo paciente, avaliacao, imagens"),
    ]

    for i, (title, value, subtitle) in enumerate(cards):
        card = ctk.CTkFrame(parent, fg_color="#ffffff", corner_radius=12, border_width=1, border_color="#ececec")
        card.grid(row=i // 2, column=i % 2, sticky="nsew", padx=8, pady=8)
        ctk.CTkLabel(card, text=title, font=ctk.CTkFont(size=font_pt, weight="bold")).pack(
            anchor="w", padx=14, pady=(12, 2)
        )
        ctk.CTkLabel(
            card, text=value, font=ctk.CTkFont(size=font_pt, weight="bold"), text_color="#7c1229"
        ).pack(anchor="w", padx=14)
        ctk.CTkLabel(card, text=subtitle, font=ctk.CTkFont(size=font_pt), text_color="#666666").pack(
            anchor="w", padx=14, pady=(0, 12)
        )

    recent_box = ctk.CTkFrame(parent, fg_color="#ffffff", corner_radius=12, border_width=1, border_color="#ececec")
    recent_box.grid(row=2, column=0, columnspan=2, sticky="nsew", padx=8, pady=(16, 8))
    ctk.CTkLabel(recent_box, text="Ultimos pacientes cadastrados", font=ctk.CTkFont(size=font_pt, weight="bold")).pack(
        anchor="w", padx=14, pady=(12, 8)
    )
    if not ultimos:
        ctk.CTkLabel(
            recent_box,
            text="Sem pacientes cadastrados ainda.",
            font=ctk.CTkFont(size=font_pt),
            text_color="#666666",
        ).pack(anchor="w", padx=14, pady=(0, 12))
    for cliente in ultimos:
        ctk.CTkLabel(
            recent_box,
            text=f"#{cliente.id} - {cliente.nome}",
            font=ctk.CTkFont(size=font_pt),
            text_color="#333333",
        ).pack(anchor="w", padx=14, pady=2)
