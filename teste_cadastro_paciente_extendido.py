"""
Protótipo de cadastro de paciente com altura (m), peso (kg), IMC e lateralidade.

Uso: duplo clique em EF_teste_cadastro.bat (pasta oficial OneDrive).
"""

from __future__ import annotations

import tkinter as tk
from datetime import date, datetime
from tkinter import messagebox, ttk

import customtkinter as ctk

from easyfeet.cliente_dados_corporais import (
    LATERALIDADE_OPCOES,
    FAIXAS_IMC_ADULTO,
    calcular_imc,
    classificar_imc,
    formatar_altura,
    formatar_imc,
    formatar_peso,
    imc_preview,
    imc_valor_numerico,
)
from easyfeet.db import SessionLocal, init_db
from easyfeet.services import EasyFeetService

# Tamanho único em toda a janela (rótulos, campos, botões e tabela).
UI_FONT_PT = 16
IMC_MODAL_FONT_PT = 13
TREE_ROW_HEIGHT = 34


def _idade_de_nascimento(data_nascimento: str) -> str:
    if not data_nascimento.strip():
        return "-"
    try:
        nasc = datetime.strptime(data_nascimento.strip(), "%d/%m/%Y").date()
    except ValueError:
        return "-"
    hoje = date.today()
    anos = hoje.year - nasc.year - ((hoje.month, hoje.day) < (nasc.month, nasc.day))
    return f"{anos} anos"


class TesteCadastroPacienteApp(ctk.CTk):
    def __init__(self, service: EasyFeetService) -> None:
        super().__init__()
        self.service = service
        self._editing_id: int | None = None
        self._ui_font = ctk.CTkFont(size=UI_FONT_PT)
        self._ui_font_bold = ctk.CTkFont(size=UI_FONT_PT, weight="bold")

        self.title("EasyFeet — Teste cadastro paciente")
        self.geometry("1150x740")
        self.minsize(920, 620)
        ctk.set_appearance_mode("light")

        root = ctk.CTkFrame(self, fg_color="#f5f5f5")
        root.pack(fill="both", expand=True, padx=16, pady=16)
        root.grid_columnconfigure(0, weight=1)
        root.grid_rowconfigure(1, weight=1)

        form = ctk.CTkFrame(root, fg_color="#ffffff", corner_radius=12, border_width=1, border_color="#ececec")
        form.grid(row=0, column=0, sticky="ew")
        for c in range(6):
            form.grid_columnconfigure(c, weight=1 if c == 0 else 0)

        self._title = ctk.CTkLabel(form, text="Novo paciente (protótipo)", font=self._ui_font_bold)
        self._title.grid(row=0, column=0, columnspan=6, sticky="w", padx=14, pady=(12, 6))

        entry_h = 38

        def lbl(row: int, col: int, text: str) -> None:
            ctk.CTkLabel(form, text=text, font=self._ui_font).grid(
                row=row, column=col, padx=8, pady=(2, 0), sticky="w"
            )

        lbl(1, 0, "Nome *")
        lbl(1, 1, "Telefone")
        lbl(1, 2, "Email")
        lbl(1, 3, "Nascimento *")
        lbl(1, 4, "Sexo *")
        lbl(1, 5, "Lateralidade *")

        self._nome = ctk.CTkEntry(form, placeholder_text="Nome completo", font=self._ui_font, height=entry_h)
        self._telefone = ctk.CTkEntry(form, placeholder_text="Telefone", font=self._ui_font, height=entry_h, width=140)
        self._email = ctk.CTkEntry(form, placeholder_text="Email", font=self._ui_font, height=entry_h, width=180)
        self._nascimento = ctk.CTkEntry(form, placeholder_text="DD/MM/AAAA", font=self._ui_font, height=entry_h, width=120)
        self._sexo = ctk.CTkOptionMenu(
            form,
            values=["Selecione... *", "Masculino", "Feminino"],
            font=self._ui_font,
            height=entry_h,
            width=120,
        )
        self._sexo.set("Selecione... *")
        self._lateralidade = ctk.CTkOptionMenu(
            form,
            values=["Selecione... *", *LATERALIDADE_OPCOES],
            font=self._ui_font,
            height=entry_h,
            width=130,
        )
        self._lateralidade.set("Selecione... *")

        self._nome.grid(row=2, column=0, padx=8, pady=(0, 6), sticky="ew")
        self._telefone.grid(row=2, column=1, padx=8, pady=(0, 6), sticky="w")
        self._email.grid(row=2, column=2, padx=8, pady=(0, 6), sticky="w")
        self._nascimento.grid(row=2, column=3, padx=8, pady=(0, 6), sticky="w")
        self._sexo.grid(row=2, column=4, padx=8, pady=(0, 6), sticky="w")
        self._lateralidade.grid(row=2, column=5, padx=8, pady=(0, 6), sticky="w")

        corp = ctk.CTkFrame(form, fg_color="#f8f8f8", corner_radius=8, border_width=1, border_color="#e0e0e0")
        corp.grid(row=3, column=0, columnspan=3, padx=8, pady=(4, 6), sticky="w")
        for i in range(3):
            corp.grid_columnconfigure(i, weight=0)

        ctk.CTkLabel(corp, text="Altura (m) *", font=self._ui_font).grid(row=0, column=0, padx=(10, 6), pady=(8, 0), sticky="w")
        ctk.CTkLabel(corp, text="Peso (kg) *", font=self._ui_font).grid(row=0, column=1, padx=6, pady=(8, 0), sticky="w")

        imc_hdr = ctk.CTkFrame(corp, fg_color="transparent")
        imc_hdr.grid(row=0, column=2, padx=(6, 10), pady=(8, 0), sticky="w")
        ctk.CTkLabel(imc_hdr, text="IMC", font=self._ui_font).pack(side="left")

        self._altura = ctk.CTkEntry(corp, placeholder_text="1,75", font=self._ui_font, height=entry_h, width=88)
        self._peso = ctk.CTkEntry(corp, placeholder_text="68,5", font=self._ui_font, height=entry_h, width=88)

        imc_row = ctk.CTkFrame(corp, fg_color="transparent")
        imc_row.grid(row=1, column=2, padx=(6, 10), pady=(4, 10), sticky="w")
        self._imc = ctk.CTkEntry(
            imc_row,
            font=self._ui_font,
            height=entry_h,
            width=72,
            placeholder_text="-",
            state="disabled",
            text_color="#333333",
        )
        self._imc.pack(side="left")
        ctk.CTkButton(
            imc_row,
            text="?",
            width=28,
            height=entry_h - 4,
            font=self._ui_font,
            fg_color="#ececec",
            text_color="#333333",
            hover_color="#dbe8ff",
            corner_radius=6,
            command=self._show_imc_help,
        ).pack(side="left", padx=(6, 0))

        self._altura.grid(row=1, column=0, padx=(10, 6), pady=(4, 10), sticky="w")
        self._peso.grid(row=1, column=1, padx=6, pady=(4, 10), sticky="w")

        self._altura.bind("<KeyRelease>", self._on_corporal_change)
        self._peso.bind("<KeyRelease>", self._on_corporal_change)

        ctk.CTkLabel(form, text="Observações", font=self._ui_font).grid(
            row=4, column=0, columnspan=6, padx=8, pady=(4, 0), sticky="w"
        )
        self._obs = ctk.CTkTextbox(form, font=self._ui_font, height=64)
        self._obs.grid(row=5, column=0, columnspan=6, padx=8, pady=(0, 8), sticky="ew")

        btn_row = ctk.CTkFrame(form, fg_color="transparent")
        btn_row.grid(row=6, column=0, columnspan=6, padx=8, pady=(0, 12), sticky="ew")

        ctk.CTkButton(
            btn_row,
            text="Editar selecionado",
            font=self._ui_font,
            fg_color="#ffffff",
            text_color="#7c1229",
            hover_color="#f0dbe1",
            border_width=1,
            border_color="#7c1229",
            command=self._carregar_edicao,
        ).pack(side="left")

        ctk.CTkButton(
            btn_row,
            text="Limpar formulário",
            font=self._ui_font,
            fg_color="#ececec",
            text_color="#333333",
            command=self._limpar_form,
        ).pack(side="left", padx=(8, 0))

        self._salvar_btn = ctk.CTkButton(
            btn_row,
            text="Salvar paciente",
            font=self._ui_font,
            fg_color="#7c1229",
            hover_color="#5b0717",
            command=self._salvar,
        )
        self._salvar_btn.pack(side="right")

        self._nascimento.bind("<KeyRelease>", self._mascara_data)

        table_box = ctk.CTkFrame(root, fg_color="#ffffff", corner_radius=12, border_width=1, border_color="#ececec")
        table_box.grid(row=1, column=0, sticky="nsew", pady=(14, 0))
        table_box.grid_columnconfigure(0, weight=1)
        table_box.grid_rowconfigure(0, weight=1)

        style = ttk.Style()
        style.configure(
            "TesteCadastro.Treeview",
            font=("Segoe UI", UI_FONT_PT),
            rowheight=TREE_ROW_HEIGHT,
        )
        style.configure("TesteCadastro.Treeview.Heading", font=("Segoe UI", UI_FONT_PT))

        cols = ("id", "nome", "idade", "sexo", "altura", "peso", "imc", "lat", "telefone")
        self._tree = ttk.Treeview(table_box, columns=cols, show="headings", height=14, style="TesteCadastro.Treeview")
        for cid, title, w in (
            ("id", "ID", 48),
            ("nome", "Nome", 190),
            ("idade", "Idade", 76),
            ("sexo", "Sexo", 96),
            ("altura", "Alt. (m)", 80),
            ("peso", "Peso (kg)", 84),
            ("imc", "IMC", 64),
            ("lat", "Lateral.", 96),
            ("telefone", "Telefone", 120),
        ):
            self._tree.heading(cid, text=title)
            anchor = "w" if cid == "nome" else "center"
            self._tree.column(cid, width=w, anchor=anchor)
        self._tree.grid(row=0, column=0, sticky="nsew", padx=12, pady=12)
        sb = ttk.Scrollbar(table_box, orient="vertical", command=self._tree.yview)
        self._tree.configure(yscrollcommand=sb.set)
        sb.grid(row=0, column=1, sticky="ns", pady=12)
        self._tree.bind("<Double-1>", lambda _e: self._carregar_edicao())

        self._atualizar_imc_preview()
        self._refresh_table()

    def _set_imc_display(self, texto: str) -> None:
        self._imc.configure(state="normal")
        self._imc.delete(0, tk.END)
        self._imc.insert(0, texto)
        self._imc.configure(state="disabled")

    def _on_corporal_change(self, _event: object | None = None) -> None:
        self._atualizar_imc_preview()

    def _atualizar_imc_preview(self) -> None:
        self._set_imc_display(imc_preview(self._altura.get(), self._peso.get()))

    def _show_imc_help(self) -> None:
        modal = ctk.CTkToplevel(self)
        modal.title("IMC — tabela de referência (adultos)")
        modal.geometry("920x520")
        modal.minsize(820, 440)
        modal.transient(self)
        modal.grab_set()

        modal_font = ctk.CTkFont(size=IMC_MODAL_FONT_PT)
        modal_font_bold = ctk.CTkFont(size=IMC_MODAL_FONT_PT, weight="bold")

        frame = ctk.CTkFrame(modal, fg_color="#ffffff")
        frame.pack(fill="both", expand=True, padx=16, pady=16)
        frame.grid_rowconfigure(3, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            frame,
            text="Classificação do IMC (referência clínica)",
            font=modal_font_bold,
            text_color="#333333",
        ).grid(row=0, column=0, sticky="w", padx=8, pady=(4, 6))

        info = ctk.CTkLabel(
            frame,
            text="Tabela para adultos (18+). Em crianças/adolescentes, use curvas pediátricas por idade/sexo.",
            font=modal_font,
            text_color="#555555",
            wraplength=860,
            justify="left",
        )
        info.grid(row=1, column=0, sticky="w", padx=8, pady=(0, 8))

        atual = imc_valor_numerico(self._altura.get(), self._peso.get())
        resumo_txt = "Preencha altura e peso para ver a classificação do paciente."
        if atual is not None:
            faixa = classificar_imc(atual)
            resumo_txt = f"IMC atual: {formatar_imc(atual)}  →  {faixa.nome}  ({faixa.intervalo})"

        resumo = ctk.CTkLabel(frame, text=resumo_txt, font=modal_font_bold, text_color="#333333")
        resumo.grid(row=2, column=0, sticky="w", padx=8, pady=(0, 8))

        table_host = ttk.Frame(frame)
        table_host.grid(row=3, column=0, sticky="nsew", padx=8, pady=(0, 10))
        table_host.grid_rowconfigure(0, weight=1)
        table_host.grid_columnconfigure(0, weight=1)

        style = ttk.Style()
        style.configure("IMC.Treeview", font=("Segoe UI", IMC_MODAL_FONT_PT), rowheight=26)
        style.configure("IMC.Treeview.Heading", font=("Segoe UI", IMC_MODAL_FONT_PT, "bold"))

        cols = ("imc", "classificacao", "interpretacao")
        tree = ttk.Treeview(
            table_host,
            columns=cols,
            show="headings",
            style="IMC.Treeview",
            height=6,
            selectmode="browse",
        )
        tree.heading("imc", text="Faixa IMC (adulto)")
        tree.heading("classificacao", text="Classificação")
        tree.heading("interpretacao", text="Interpretação resumida")
        tree.column("imc", width=155, minwidth=130, anchor="w", stretch=False)
        tree.column("classificacao", width=220, minwidth=170, anchor="w", stretch=False)
        tree.column("interpretacao", width=420, minwidth=280, anchor="w", stretch=True)
        tree.grid(row=0, column=0, sticky="nsew")

        vsb = ttk.Scrollbar(table_host, orient="vertical", command=tree.yview)
        hsb = ttk.Scrollbar(table_host, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")

        tree.tag_configure("current", background="#dbe8ff", foreground="#111111")

        current_name = classificar_imc(atual).nome if atual is not None else None
        current_iid: str | None = None
        for f in FAIXAS_IMC_ADULTO:
            tag = ("current",) if current_name == f.nome else ()
            iid = tree.insert("", "end", values=(f.intervalo, f.nome, f.texto_tabela), tags=tag)
            if current_name == f.nome:
                current_iid = iid

        if current_iid is not None:
            tree.selection_set(current_iid)
            tree.focus(current_iid)
            tree.see(current_iid)

        note = ctk.CTkLabel(
            frame,
            text="Nota: IMC é um indicador populacional; não substitui exame clínico nem avaliação postural/plantar.",
            font=modal_font,
            text_color="#555555",
            wraplength=860,
            justify="left",
        )
        note.grid(row=4, column=0, sticky="w", padx=8, pady=(0, 10))

        ctk.CTkButton(frame, text="Fechar", font=modal_font, command=modal.destroy).grid(
            row=5, column=0, sticky="e", padx=8, pady=(0, 4)
        )

    def _mascara_data(self, _event: object | None = None) -> None:
        raw = "".join(ch for ch in self._nascimento.get() if ch.isdigit())[:8]
        parts: list[str] = []
        if raw:
            parts.append(raw[:2])
        if len(raw) > 2:
            parts.append(raw[2:4])
        if len(raw) > 4:
            parts.append(raw[4:8])
        masked = "/".join(parts)
        if masked != self._nascimento.get():
            self._nascimento.delete(0, tk.END)
            self._nascimento.insert(0, masked)

    def _limpar_form(self) -> None:
        self._editing_id = None
        self._title.configure(text="Novo paciente (protótipo)")
        self._salvar_btn.configure(text="Salvar paciente")
        for entry in (self._nome, self._telefone, self._email, self._nascimento, self._altura, self._peso):
            entry.delete(0, tk.END)
        self._obs.delete("1.0", "end")
        self._sexo.set("Selecione... *")
        self._lateralidade.set("Selecione... *")
        self._atualizar_imc_preview()

    def _salvar(self) -> None:
        lateralidade = self._lateralidade.get()
        if lateralidade.startswith("Selecione"):
            lateralidade = ""
        try:
            if self._editing_id is None:
                self.service.cadastrar_cliente(
                    self._nome.get(),
                    self._telefone.get(),
                    self._email.get(),
                    self._nascimento.get(),
                    self._sexo.get(),
                    self._obs.get("1.0", "end-1c"),
                    self._altura.get(),
                    self._peso.get(),
                    lateralidade,
                    exigir_dados_corporais=True,
                )
                messagebox.showinfo("Teste cadastro", "Paciente cadastrado.")
            else:
                self.service.atualizar_cliente(
                    self._editing_id,
                    self._nome.get(),
                    self._telefone.get(),
                    self._email.get(),
                    self._nascimento.get(),
                    self._sexo.get(),
                    self._obs.get("1.0", "end-1c"),
                    self._altura.get(),
                    self._peso.get(),
                    lateralidade,
                    exigir_dados_corporais=True,
                )
                messagebox.showinfo("Teste cadastro", "Paciente atualizado.")
        except ValueError as exc:
            messagebox.showerror("Validação", str(exc))
            return
        self._limpar_form()
        self._refresh_table()

    def _carregar_edicao(self) -> None:
        sel = self._tree.focus()
        if not sel:
            messagebox.showinfo("Edição", "Selecione um paciente na tabela.")
            return
        valores = self._tree.item(sel, "values")
        if not valores:
            return
        cliente = self.service.clientes.obter_por_id(int(valores[0]))
        if not cliente:
            return
        self._editing_id = cliente.id
        self._title.configure(text=f"Editar paciente #{cliente.id}")
        self._salvar_btn.configure(text="Atualizar paciente")
        self._nome.delete(0, tk.END)
        self._nome.insert(0, cliente.nome)
        self._telefone.delete(0, tk.END)
        self._telefone.insert(0, cliente.telefone or "")
        self._email.delete(0, tk.END)
        self._email.insert(0, cliente.email or "")
        self._nascimento.delete(0, tk.END)
        self._nascimento.insert(0, cliente.data_nascimento or "")
        sexo = (cliente.sexo or "").strip()
        self._sexo.set(sexo if sexo in {"Masculino", "Feminino"} else "Selecione... *")
        lat = (cliente.lateralidade or "").strip()
        self._lateralidade.set(lat if lat in LATERALIDADE_OPCOES else "Selecione... *")
        self._altura.delete(0, tk.END)
        self._altura.insert(0, formatar_altura(cliente.altura_m))
        self._peso.delete(0, tk.END)
        self._peso.insert(0, formatar_peso(cliente.peso_kg))
        self._obs.delete("1.0", "end")
        self._obs.insert("1.0", cliente.observacoes or "")
        self._atualizar_imc_preview()

    def _refresh_table(self) -> None:
        for item in self._tree.get_children():
            self._tree.delete(item)
        for c in self.service.clientes.listar():
            self._tree.insert(
                "",
                "end",
                values=(
                    c.id,
                    c.nome,
                    _idade_de_nascimento(c.data_nascimento or ""),
                    c.sexo or "-",
                    formatar_altura(c.altura_m) or "-",
                    formatar_peso(c.peso_kg) or "-",
                    formatar_imc(calcular_imc(c.altura_m, c.peso_kg)),
                    c.lateralidade or "-",
                    c.telefone or "",
                ),
            )


def main() -> None:
    init_db()
    with SessionLocal() as session:
        app = TesteCadastroPacienteApp(EasyFeetService(session))
        app.mainloop()


if __name__ == "__main__":
    main()
