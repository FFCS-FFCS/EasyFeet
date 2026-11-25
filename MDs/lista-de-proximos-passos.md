# EasyFeet — Lista de próximos passos

**Última atualização:** 2026-06-12 UTC-3  
**Documento vivo:** registrar aqui trabalho pendente; marcar concluído quando entregar.

---

## Prioridade activa (demanda actual)

| ID | Item | Estado | Notas |
|----|------|--------|-------|
| **PEND-NAV-001** | **Novo tipo de marcação / registo clínico: Teste do Navicular** | Pendente — **prioridade do utilizador** | Pesquisa clínica feita (aguarda instruções); ver secção abaixo. Não confundir com «navicular acessório» (patologia distinta). |

### Teste do Navicular — escopo e classificação

**Documentos de apoio:**  
- `Documentos de Apoio/EF - Navicular mm x percentual.md` + PDF limiares  
- `Documentos de Apoio/EF - Navicular plano de implantacao.md`  
- `Documentos de Apoio/EF - Navicular laudo - textos modelo.md` — **PEND-NAV-LAUDO-001** (textos clínicos para laudo; implementar na NAV-4)

**Menu (NAV-0):** `Teste Navicular` acima de Palmilhas — Ficha / Laudos / Configurações (`menu-config-v2.json`)

| Modo | Descrição | Estado |
|------|-----------|--------|
| **A** | Limiar fixo: **até 10 mm = normal** (Brody); acima = alterado | **Implementado (NAV-1)** |
| **B** | Queda relativa: `(queda / altura_sentado) × 100` — limiar % a validar | Futuro |
| **C** | Ajuste por comprimento do pé (+ sexo), Nielsen / Mølgaard Pedersen | Futuro |

- [x] Menu lateral (NAV-0): módulo `navicular` + subitens espelho Podoscópio.
- [x] Plano de fases NAV-0…NAV-5 e mapeamento ficha Podoscópio → Navicular.
- [x] **NAV-1:** ficha funcional + BD + Modo A (≤ 10 mm, Brody) + combo «Ficha salva» + excluir ficha.
- [x] **NAV-2:** PDF ficha (branco + preenchida) — layout EasyFeet + logotipo.
- [ ] **NAV-3:** fotos sentado/em pé + Hub/timeline.
- [x] **NAV-4:** ecrã **Laudos** — gerar, salvar, listar e baixar PDF **por paciente**; integrar textos de `EF - Navicular laudo - textos modelo.md`.
- [x] **PEND-NAV-LAUDO-001:** conteúdo clínico do laudo (§4–§6) — `navicular_laudo.py`, `navicular_laudo_pdf.py`, `laudos_navicular` BD, `gui.py` (`navicular_laudos`).
- [ ] **NAV-5:** Modos B/C (futuro).

**Retomar nesta ordem:** NAV-3 (fotos/Hub) → NAV-5 (Modos B/C, futuro).

---

## Hub v2 — M5 (pausado; retomar depois)

| ID | Item | Estado | Ficheiros prováveis |
|----|------|--------|---------------------|
| **M5-1** | Botão **«Momentos»** na ficha (Linha do tempo ou cabeçalho Hub) → modal com lista | Pendente | `easyfeet/gui.py` |
| **M5-2** | Busca / filtros: texto (rótulo), intervalo de datas, «com Plantígrafo / sem exames» | Pendente | `gui.py`, eventualmente `services.py` / `repositories.py` |
| **M5-3** | Ao seleccionar momento: ir ao card na timeline ou abrir EFM com `momento_id` | Pendente | reutilizar `_open_efm_marcadores` |
| **M5-4** | Atalho **Podoscópio** na ficha (substituir stub `_hub_atalho_modulo`) | Pendente | `gui.py` |
| **M5-5** | Testes: estender `scripts/test_hub_smoke.py` ou smoke via `EF.bat` | Pendente | `scripts/` |

**Spec:** `rascunho-menu-hub-paciente-v2.md` §6.2. A timeline agrupada por dia **mantém-se**; o modal é complemento para muitos momentos.

**Commit de referência (M1–M4 feitos):** `e28c34d`.

---

## Marcadores / produto (backlog registado)

| ID | Item | Prioridade | Estado |
|----|------|------------|--------|
| **PEND-MARC-001** | Comparar evolução entre momentos (lado a lado; palmilhas) | Alta | Pendente |
| **PEND-MARC-002** | Filtros por intervalo de datas no histórico (parcialmente coberto por M5) | Média | Pendente |
| **PEND-MARC-003** | Exportação relatório PDF/Word com vários momentos | Média | Pendente |
| **PEND-MARC-004** | Vincular `momento_clinico.avaliacao_id` quando CRUD Avaliações existir | Média | Pendente |
| **PEND-MARC-005** | Migração legado `Imagens/Pacientes/{nome}/` → `data/pacientes/{id}/` | Baixa | Pendente |
| **PEND-MARC-006** | Duplicar momento / «Salvar como nova versão» | Baixa | Pendente |

Detalhe: `especificacao-marcacoes-vinculo-paciente.md` §10.

---

## Opcional / operação

| Item | Estado |
|------|--------|
| Tag `v2.0.0-m4` ou snapshot (`CriarSnapshot.bat`) | Opcional |
| Release instalador (`build_instalador.bat`) | Só se pedido |
| Atualizar `2026-05-07-status-tecnico-e-pendencias.md` com estado pós-v2 | Baixa |

---

## Histórico de conclusões recentes (referência)

- **M1–M4** (menu v2, Hub, timeline, EFM B+): concluído — commit `e28c34d` (2026-05-30).
- **Fase 2 marcadores** (vínculo paciente, Salvar, reabertura CLI): concluído — roteiro manual 2026-05-30.
- **NAV-1** (ficha Navicular + BD + Modo A + combo/excluir): concluído — 2026-06-01; smoke `scripts/test_ficha_salva_combo_smoke.py`.
- **NAV-2** (PDF ficha branco + preenchida): concluído — 2026-06-12; `easyfeet/navicular_pdf.py`, smoke `scripts/test_navicular_pdf.py`.
- **Refino PDFs** (Navicular + Podoscópio): layout rotulo/valor dinâmico, campos em branco sem traços, destaque Alterado — 2026-06-12; `pdf_brand.col_widths_rotulo_valor`.
- **NAV-4** (Laudos + PEND-NAV-LAUDO-001): ecrã `navicular_laudos`, BD `laudos_navicular`, textos §4, PDF laudo — 2026-06-12; smoke `scripts/test_navicular_laudo.py`.
- **Instalador DEMO** (BD + pacientes atuais): `release/EasyFeet-Setup-DEMO-2.0.0.exe`, `build_instalador_demo.bat` — 2026-06-12.
