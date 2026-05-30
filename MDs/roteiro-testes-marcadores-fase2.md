# EasyFeet — Roteiro de testes: marcações Fase 2

**Status:** pendente de execução manual pelo utilizador  
**Criado:** 2026-05-28 (UTC-3)  
**Escopo:** selector de paciente no EFM, momentos clínicos, Salvar no paciente, histórico em Pacientes, reabertura contextual  
**Pasta oficial:** `C:\Users\flavi\OneDrive\Documentos\Ideias_Projetos\Cursor_Projetos\EasyFeet`  
**Especificação de referência:** `especificacao-marcacoes-vinculo-paciente.md`

---

## Como usar este documento

1. Marque cada linha com **OK** ou **Falhou** na coluna correspondente.
2. Em **Notas**, descreva o que viu (mensagem de erro, ficheiro em falta, comportamento estranho).
3. Quando terminar (ou se travar num passo), peça ao assistente no Cursor: *«Quero executar o roteiro de testes da Fase 2 dos marcadores»* — ele deve orientar passo a passo com base neste ficheiro.

---

## Quando faz sentido executar estes testes

Faça este roteiro quando puder dedicar **cerca de 45–60 minutos** sem interrupções, com o ambiente abaixo preparado.

| Condição | Porquê |
|----------|--------|
| Abrir o projeto pela pasta **OneDrive** (não `C:\Cursor_Projetos\EasyFeet`) | Garante `data/`, `EF.bat` e ficheiros gravados no sítio certo |
| Executar via **`EF.bat`** (duplo clique na raiz do projeto) | É o fluxo real do utilizador; não usar instalador/ZIP para esta validação |
| Ter **1–2 fotos plantares** de teste (PNG/JPG) à mão | Necessário para carregar imagem e salvar marcação |
| Ter ou criar **pelo menos um paciente** de teste no cadastro | Fluxo exige paciente selecionado |
| **Fechar** qualquer janela EFM já aberta antes de começar | Evita confusão com o aviso de “EFM já aberto” |
| (Opcional) Copiar `data/` e `data/easyfeet.db` para backup | Permite repetir testes sem medo de estragar dados reais |

**Não é obrigatório** ter `pytest` instalado para estes testes manuais. Os testes automáticos abaixo são opcionais (revalidação rápida).

---

## O que já foi verificado automaticamente (2026-05-28)

Estes pontos foram validados em ambiente de desenvolvimento **sem** abrir a interface gráfica:

| Verificação | Resultado |
|-------------|-----------|
| Import de `easyfeet.gui`, `easyfeet_markers.app`, modelos e repositórios | OK |
| Tabelas SQLite `momentos_clinicos`, `imagens_plantares`, `marcacoes_plantares` | OK (existem após `init_db`) |
| Inserção e leitura via `MarcacaoPlantarRepository.listar_marcacoes_por_cliente` | OK |
| Parser CLI `--cliente-id`, `--momento-id`, `--imagem-id` | OK |
| Linter nos ficheiros alterados da Fase 2 | OK (sem erros reportados) |
| Suíte `pytest` no ambiente atual | **Não executada** (`pytest` não instalado) |

### Comandos opcionais para repetir a validação automática

Na raiz OneDrive do projeto:

```powershell
cd "C:\Users\flavi\OneDrive\Documentos\Ideias_Projetos\Cursor_Projetos\EasyFeet"
py -3 -c "from easyfeet.db import init_db; init_db(); from easyfeet.gui import EasyFeetApp; from easyfeet_markers.app import _parse_int_arg; print('imports OK')"
py -3 -c "import sqlite3; from easyfeet.db import DB_PATH; c=sqlite3.connect(str(DB_PATH)); print(c.execute(\"SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%plantar%' OR name LIKE '%clinico%'\").fetchall()); c.close()"
```

Para instalar e correr testes unitários existentes (se/quando quiser):

```powershell
py -3 -m pip install pytest
py -3 -m pytest -q
```

---

## Onde os dados devem aparecer após Salvar

| O quê | Onde conferir |
|-------|----------------|
| Base de dados | `data/easyfeet.db` (tabelas acima) |
| Ficheiros do paciente | `data/pacientes/{cliente_id}/momentos/{momento_id}/imagens/{imagem_id}/` (original, JSON, PNG) |
| Histórico na UI | Módulo **Pacientes** → bloco **Histórico de marcações do paciente selecionado** |
| EFM com contexto | Menu **Módulos → Marcadores** ou botões **Abrir marcadores** / **Reabrir no EFM** |

---

## Checklist manual (marcar OK / Falhou)

### A — Fluxo principal Fase 2 (core)

| # | Passo | Ação | Resultado esperado | OK | Falhou | Notas |
|---|-------|------|-------------------|----|--------|-------|
| A1 | Abrir app | Duplo clique em `EF.bat` | EasyFeet abre sem erro | | | |
| A2 | Paciente | Ir em **Pacientes**, selecionar um paciente na tabela | Formulário e histórico reagem à seleção | | | |
| A3 | Abrir EFM | Clicar **Abrir marcadores** | EFM abre; paciente já vem no combo superior | | | |
| A4 | Momento | Ver combo de momento | Existe momento atual ou opção de novo momento | | | |
| A5 | Imagem | Carregar uma imagem plantar | Imagem aparece no painel; registo de imagem criado | | | |
| A6 | Marcar | Desenhar linhas ou pontos (conforme tipo ativo) | Marcação visível no canvas | | | |
| A7 | Salvar | Clicar **Salvar no paciente** | Mensagem de sucesso ou feedback claro; sem crash | | | |
| A8 | Histórico | Fechar EFM; voltar a **Pacientes** com o mesmo paciente | Histórico lista a nova marcação (momento, tipo, datas) | | | |
| A9 | Ficheiros | (Opcional) Abrir pasta `data/pacientes/...` | Existem `original`, JSON e PNG da marcação | | | |

### B — Histórico em Pacientes

| # | Passo | Ação | Resultado esperado | OK | Falhou | Notas |
|---|-------|------|-------------------|----|--------|-------|
| B1 | Ver original | Selecionar linha no histórico → **Ver original** | Abre a foto original correta (visualizador do Windows) | | | |
| B2 | Ver marcada | **Ver marcada** na mesma linha | Abre o PNG com marcação correspondente | | | |
| B3 | Reabrir | **Reabrir no EFM** (com EFM fechado) | EFM abre com paciente, momento, imagem e tipo corretos; marcação carregada | | | |
| B4 | Paciente errado | Repetir B1–B3 com outro paciente selecionado | Só vê/abre dados do paciente selecionado | | | |
| B5 | Sem marcações | Selecionar paciente sem histórico | Mensagem do tipo “sem marcações salvas” | | | |

### C — EFM já aberto (UX)

| # | Passo | Ação | Resultado esperado | OK | Falhou | Notas |
|---|-------|------|-------------------|----|--------|-------|
| C1 | EFM aberto | Deixar uma janela EFM aberta | — | | | |
| C2 | Reabrir com contexto | No histórico, **Reabrir no EFM** noutra linha | Aviso: fechar o EFM atual para abrir no contexto selecionado | | | |
| C3 | Após fechar | Fechar EFM; clicar **Reabrir no EFM** de novo | Abre no contexto da linha escolhida | | | |

### D — Tipos Linhas vs Pontos (mesma imagem)

| # | Passo | Ação | Resultado esperado | OK | Falhou | Notas |
|---|-------|------|-------------------|----|--------|-------|
| D1 | Linhas | Tipo **Linhas**, marcar, **Salvar no paciente** | Entrada “Linhas” no histórico | | | |
| D2 | Pontos | Trocar para **Pontos**, marcar diferente, salvar | Segunda entrada (Pontos) no histórico; mesma imagem original | | | |
| D3 | Alternar | Voltar a Linhas, depois Pontos | Cada tipo mantém a sua geometria (não mistura) | | | |
| D4 | Reabrir linhas | **Reabrir no EFM** numa linha “Linhas” | Abre em Linhas com dados de linhas | | | |
| D5 | Reabrir pontos | **Reabrir no EFM** numa linha “Pontos” | Abre em Pontos com dados de pontos | | | |

### E — Momentos clínicos (evolução no tempo)

| # | Passo | Ação | Resultado esperado | OK | Falhou | Notas |
|---|-------|------|-------------------|----|--------|-------|
| E1 | Novo momento | No EFM, criar **Novo momento** para o paciente | Momento aparece no combo | | | |
| E2 | Salvar no momento 1 | Carregar imagem, marcar, salvar | Histórico mostra registo com data/rótulo do momento 1 | | | |
| E3 | Segundo momento | Criar outro momento; nova imagem e marcação | Histórico com **dois** momentos distintos | | | |
| E4 | Ordenação | Ver ordem no histórico | Mais recente primeiro (data do momento) | | | |

### F — Robustez e mensagens de erro

| # | Passo | Ação | Resultado esperado | OK | Falhou | Notas |
|---|-------|------|-------------------|----|--------|-------|
| F1 | Salvar sem imagem | **Salvar no paciente** sem carregar foto | Aviso claro; não grava lixo na BD | | | |
| F2 | Salvar sem paciente | (Se possível) tentar fluxo sem paciente no combo | Bloqueio ou aviso antes de gravar | | | |
| F3 | Ficheiro em falta | Renomear/apagar um PNG ou original no disco; **Ver original** ou **Ver marcada** | Mensagem “não encontrado”; app não fecha | | | |
| F4 | Atualizar mesma marcação | Editar marcação existente e salvar de novo | Mesma linha no histórico com **Atualizado em** mais recente | | | |

### G — Regressão rápida (não quebrar o resto)

| # | Passo | Ação | Resultado esperado | OK | Falhou | Notas |
|---|-------|------|-------------------|----|--------|-------|
| G1 | Cadastro | Criar/editar paciente (nome, altura, peso, IMC) | Grava e aparece na tabela | | | |
| G2 | Dashboard | Abrir **Dashboard** | Total de pacientes e últimos 3 nomes corretos | | | |
| G3 | Buscar/Filtro | Dashboard vs Pacientes | Buscar/Filtro **só** visíveis em Pacientes | | | |
| G4 | Versão | Rodapé da sidebar | Mostra **v1.0.0** (ou versão atual) | | | |
| G5 | Menu Módulos | **Módulos → Marcadores** e **Avaliação Postural** | Marcadores abre EFM; Avaliação Postural comporta-se como placeholder | | | |
| G6 | Modal IMC | Botão **?** ao lado do IMC no paciente | Modal com tabela e scroll funciona | | | |

---

## Resumo da sessão de teste (preencher no fim)

| Campo | Valor |
|-------|--------|
| Data da execução | |
| Versão testada (rodapé do app) | |
| SO / máquina | |
| Total OK | / |
| Total Falhou | / |
| Bloqueadores (impedem uso) | |
| Melhorias desejadas (não bloqueiam) | |

---

## Pendências futuras (fora deste roteiro)

Registadas na especificação; **não** fazem parte desta validação:

- **PEND-MARC-001:** comparar imagens entre momentos (lado a lado, evolução para palmilhas).
- Licenciamento do módulo (desativar menu sem licença).
- Auto-save (decisão de produto: **não** implementar por agora).

---

## Ficheiros relacionados ao desenvolvimento

| Ficheiro | Papel |
|----------|--------|
| `easyfeet_markers/app.py` | EFM: paciente, momento, salvar, CLI |
| `easyfeet/gui.py` | Histórico, botões, abrir EFM |
| `easyfeet/models.py` | `MomentoClinico`, `ImagemPlantar`, `MarcacaoPlantar` |
| `easyfeet/repositories.py` | `MarcacaoPlantarRepository` |
| `marcador_plantar/app_tk.py`, `marcador_pontos/app_tk.py` | `get_*_data`, `set_*_data`, `export_to` |
| `EFM_Marcadores.py` | Entrada do módulo de marcadores |

---

*Documento gerado para execução posterior. Ao pedir orientação no Cursor, referencie: **roteiro-testes-marcadores-fase2.md**.*
