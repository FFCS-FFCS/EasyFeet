# Situação do projeto — EasyFeet

**Atualizado em:** 25/11/2026 19:20 · **Ramo:** main · **Repositório:** https://github.com/FFCS-FFCS/EasyFeet

## Objetivo

Aplicação desktop (Windows) para apoio ao atendimento em podologia e fisioterapia: cadastro de pacientes, análise da planta do pé (plantígrafo e podoscópio), marcadores visuais, teste do navicular, laudos em PDF e acompanhamento de palmilhas. Dados ficam num SQLite local (`data/easyfeet.db`), fora do Git.

## Inventário de arquivos

| Arquivo | O que é |
|---------|---------|
| `easyfeet_main.py`, `EF.bat` | Entrada da aplicação |
| `easyfeet/` | Núcleo: interface, banco, modelos, PDFs, navegação, navicular |
| `easyfeet_markers/`, `marcador_plantar/`, `marcador_pontos/`, `EFM_Marcadores.py` | Módulo de marcadores (linhas e pontos) |
| `menu-config-v1.json`, `menu-config-v2.json` | Menus por configuração (v2 é o menu atual) |
| `scripts/` | Instalador Windows, testes de fumaça, utilitários |
| `build_instalador.bat`, `build_instalador_demo.bat` | Geração do instalador e da variante DEMO |
| `MDs/` | Documentação do produto, timesheet e pendências |
| `Imagens/EasyFeet/` | Logotipo e capturas de tela |
| `Imagens/Pacientes/` | Exemplos de demonstração (Zero1, Zero2, Zé Pé Chato, Complicada) |
| `Imagens/Plantigrafo/`, `Imagens/TesteNavicular/` | Réguas, moldes e fotos de referência do teste |
| `requirements.txt`, `README.md` | Dependências e como executar |
| `.gitignore` | Ignora `data/`, builds, executáveis e os ZIPs grandes |
| `snapshots/` | Versionamento local (os ZIPs gerados ficam de fora do Git) |

## O que mudou desde o último Suba

Este é o primeiro Suba do EasyFeet. O Git local já tinha quatro commits, o último `e28c34d` (Hub M2–M4 e EFM B+, 30/05/2026). O que entra agora, ainda não commitado até este registro:

- Teste do Navicular: ficha, banco, PDF da ficha, tela de laudos e PDF do laudo (`easyfeet/navicular.py`, `navicular_pdf.py`, `navicular_laudo.py`, `navicular_laudo_pdf.py`).
- Ajustes de layout nos PDFs do Navicular e do Podoscópio (`pdf_brand.py`, `podoscopio_pdf.py`).
- Menu v2 com o item Teste Navicular e integração na interface (`menu-config-v2.json`, `gui.py`).
- Instalador DEMO (`build_instalador_demo.bat` e scripts de build).
- Documentação: timesheets de 01/06 e 12/06/2026, lista de próximos passos, índice de MDs.
- Imagens novas: telas do sistema, plantígrafo, teste navicular e paciente de exemplo Complicada.

## Situação atual

Versão da aplicação: **2.0.0** (`easyfeet/version.py`).

Pelo `MDs/lista-de-proximos-passos.md` (atualizado em 12/06/2026):

- Feitos: menu Navicular (NAV-0), ficha e Modo A (NAV-1), PDF da ficha (NAV-2), laudos (NAV-4).
- Abertos: fotos sentado/em pé e Hub (NAV-3); Modos B e C (NAV-5).
- Hub v2 M5 (Momentos, filtros, atalhos) está pausado.
- O banco de pacientes e os instaladores gerados não vão para o Git (`data/`, `release/`, `*.exe`).

O repositório no GitHub foi criado **público**, a pedido explícito neste Suba. O comando Suba, por regra, cria repositório privado; esta foi a exceção pedida.

O ramo local chamava-se `master` e não tinha remoto. Passou a chamar-se `main`, que é o ramo principal.

## Decisões tomadas

- Primeiro envio ao GitHub na conta `FFCS-FFCS`, visibilidade pública.
- `EasyFeet_DEMO_Com_Dados.zip` (~109 MB) ficou de fora: o GitHub recusa arquivo acima de 100 MB. Entrou no `.gitignore`, ao lado de `EasyFeet_Com_Dados.zip`, que já estava ignorado.
- Imagens de pés em `Imagens/Pacientes/` são exemplos de demonstração e ficam visíveis no repositório público.
- A ficha de exemplo do Zero1 foi gerada de novo a partir do cadastro atual. O commit anterior, que ainda tinha a ficha antiga, saiu do histórico do Git.
- Nenhum `.env`, chave ou credencial apareceu no que seria commitado.

## Pendências

- NAV-3: fotos do teste (sentado e em pé) ligadas ao Hub / linha do tempo.
- NAV-5: Modos B e C do navicular (queda relativa e ajuste por comprimento do pé).
- Hub M5: botão Momentos, busca/filtros, abrir momento no EFM, atalho do Podoscópio.
- Comparar evolução entre momentos, filtros de data e relatório com vários momentos (PEND-MARC-001 a 003).
- Migração das imagens legadas `Imagens/Pacientes/{nome}/` para `data/pacientes/{id}/` (PEND-MARC-005).
- O status técnico em `MDs/2026-05-07-status-tecnico-e-pendencias.md` ainda descreve o MVP de maio e não o estado pós-v2.

## Próximos passos

1. Retomar o Navicular em NAV-3 (fotos e Hub).
2. Deixar NAV-5 (Modos B/C) para quando os limiares forem validados.
3. Retomar o Hub M5 depois do Navicular.
4. Atualizar o status técnico de 07/05/2026 para refletir a v2.
