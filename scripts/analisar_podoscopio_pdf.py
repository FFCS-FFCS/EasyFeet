# -*- coding: utf-8 -*-
"""
Gera PDFs do Podoscopio (branco + preenchido) e analisa layout (sobreposicao de texto).

Uso: py -3 scripts/analisar_podoscopio_pdf.py
Saida: data/test_pdfs/analise/branco.pdf, preenchida.pdf, relatorio.txt
"""

from __future__ import annotations

import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

OUT = ROOT / "data" / "test_pdfs" / "analise"


def _gerar_pdfs() -> Path:
    from easyfeet.db import SessionLocal, init_db
    from easyfeet.podoscopio_pdf import export_ficha_podoscopio_pdf_branco, export_ficha_podoscopio_pdf_preenchida
    from easyfeet.services import EasyFeetService

    OUT.mkdir(parents=True, exist_ok=True)
    init_db()
    session = SessionLocal()
    service = EasyFeetService(session)

    branco = OUT / "branco.pdf"
    preenchida = OUT / "preenchida.pdf"
    export_ficha_podoscopio_pdf_branco(branco)

    clientes = service.clientes.listar()
    if not clientes:
        session.close()
        raise RuntimeError("Nenhum paciente no banco para gerar PDF preenchido.")

    c = clientes[0]
    fichas = service.fichas_podoscopio.listar_por_cliente(c.id)
    if fichas:
        ficha = fichas[0]
        ficha = service.salvar_ficha_podoscopio(
            c.id,
            ficha.data_avaliacao.strftime("%d/%m/%Y %H:%M"),
            ficha.rotulo_atendimento or "Analise layout",
            "Dor nas costas",
            "Nao avaliado",
            "Nao avaliado",
            "Nao avaliado",
            "Nao avaliado",
            "Nao avaliado",
            [],
            ficha.observacoes or "Observacao de teste",
            ficha_id=ficha.id,
        )
    else:
        ficha = service.salvar_ficha_podoscopio(
            c.id,
            datetime.now().strftime("%d/%m/%Y %H:%M"),
            "Analise layout",
            "Dor nas costas",
            "Nao avaliado",
            "Nao avaliado",
            "Nao avaliado",
            "Nao avaliado",
            "Nao avaliado",
            [],
            "Observacao de teste",
        )

    export_ficha_podoscopio_pdf_preenchida(preenchida, ficha=ficha)
    session.close()
    return OUT


def _extrair_texto(pdf_path: Path) -> str:
    from pypdf import PdfReader

    return "\n".join(page.extract_text() or "" for page in PdfReader(str(pdf_path)).pages)


def _analisar_sobreposicao_pdfplumber(pdf_path: Path) -> list[str]:
    try:
        import pdfplumber
    except ImportError:
        return ["SKIP: pdfplumber nao instalado"]

    problemas: list[str] = []
    limite_coluna = 280

    with pdfplumber.open(str(pdf_path)) as pdf:
        for num, page in enumerate(pdf.pages, start=1):
            words = page.extract_words() or []
            por_linha: dict[int, list[dict]] = defaultdict(list)
            for w in words:
                chave = round(w["top"] / 4) * 4
                por_linha[chave].append(w)

            for top, linha in sorted(por_linha.items()):
                linha.sort(key=lambda x: x["x0"])
                if len(linha) < 2:
                    continue
                texto = " ".join(w["text"] for w in linha)
                if "Apoio predominante" not in texto and "Arco plantar" not in texto:
                    continue
                esq = [w for w in linha if w["x0"] < limite_coluna]
                dir_ = [w for w in linha if w["x0"] >= limite_coluna]
                if not esq or not dir_:
                    continue
                fim_esq = max(w["x1"] for w in esq)
                inicio_dir = min(w["x0"] for w in dir_)
                if fim_esq > inicio_dir + 2:
                    problemas.append(
                        f"p.{num} y~{top}: sobreposicao '{texto[:70]}' "
                        f"(fim rotulo {fim_esq:.0f} > inicio valor {inicio_dir:.0f})"
                    )
    return problemas


def _checagens_texto(nome: str, texto: str) -> list[str]:
    erros: list[str] = []
    if "Apoio predominante" not in texto:
        erros.append(f"{nome}: secao plantar ausente")
    if nome == "branco.pdf":
        if "( ) Normal" not in texto:
            erros.append(f"{nome}: opcoes de marcacao ausentes")
        if texto.count("Arco plantar") < 2:
            erros.append(f"{nome}: faltam linhas de arco plantar")
    if nome == "preenchida.pdf":
        if "Nao avaliado" not in texto and "Normal" not in texto:
            erros.append(f"{nome}: valores plantares ausentes")
        if "Dor nas costas" not in texto:
            erros.append(f"{nome}: queixa de teste ausente")
    return erros


def main() -> int:
    pasta = _gerar_pdfs()
    linhas = ["Relatorio de analise - Podoscopio PDF", f"Gerado em: {datetime.now()}", ""]

    falhas: list[str] = []
    for nome in ("branco.pdf", "preenchida.pdf"):
        path = pasta / nome
        linhas.append(f"=== {nome} ({path.stat().st_size} bytes) ===")
        texto = _extrair_texto(path)
        linhas.append("--- texto extraido (trecho plantar) ---")
        idx = texto.find("Leitura plantar")
        trecho = texto[idx : idx + 900] if idx >= 0 else texto[:500]
        linhas.append(trecho)
        linhas.append("")

        falhas.extend(_checagens_texto(nome, texto))
        sob = _analisar_sobreposicao_pdfplumber(path)
        if sob and sob[0].startswith("SKIP"):
            linhas.append(sob[0])
        elif sob:
            linhas.extend(sob)
            falhas.extend(sob)
        else:
            linhas.append("Coordenadas: sem sobreposicao detectada na tabela plantar.")

        linhas.append("")

    rel = pasta / "relatorio.txt"
    rel.write_text("\n".join(linhas), encoding="utf-8")

    print(f"PDFs em: {pasta}")
    print(f"Relatorio: {rel}")
    if falhas:
        print("FALHOU:")
        for f in falhas:
            print(f"  - {f}")
        return 1
    print("OK: branco e preenchido gerados e analisados sem problemas.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
