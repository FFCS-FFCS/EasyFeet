# EasyFeet — Especificação: marcações vinculadas ao paciente

**Status:** rascunho para decisão (sem implementação comprometida)  
**Data:** 2026-05-26  
**Versão do documento:** 1.0  
**Pasta do projeto:** `C:\Users\flavi\OneDrive\Documentos\Ideias_Projetos\Cursor_Projetos\EasyFeet`

---

## 1. Objetivo

Permitir que o trabalho feito no **módulo de marcações (EFM)** — imagem original, geometria (JSON) e imagem marcada (PNG) — fique **registrado e recuperável** no **mesmo paciente** do EasyFeet, para:

- reabrir e continuar a edição;
- consultar original vs. marcada no histórico do paciente;
- no futuro, acompanhar **evolução em momentos diferentes** (ex.: confecção de palmilhas) e **comparar** imagens entre datas.

Este documento **não autoriza implementação**; serve como referência quando o produto avançar.

---

## 2. Princípios de produto (decisões fechadas)

| # | Decisão |
|---|---------|
| P1 | Existe **um único sistema: EasyFeet** — uma base de dados, um cadastro de pacientes (`clientes`). |
| P2 | O módulo de marcações pode ser **vendido/licenciado à parte**, mas **não é um produto independente**: não há sincronização nem cadastro duplicado de pacientes. |
| P3 | Sem licença do módulo: rotas/menu de marcações **indisponíveis**; o resto do EasyFeet funciona. |
| P4 | Com licença: marcações gravam sempre com `cliente_id` do cadastro central. |
| P5 | **Sem auto-save**; persistência explícita pelo botão **Salvar** (com confirmação ao sair se houver alterações não salvas — recomendado). |
| P6 | Por **momento** clínico, a **mesma imagem original** pode ter marcações **separadas por tipo** (`plantar_linhas` vs `plantar_pontos`). |
| P7 | Para evolução no tempo: **novos momentos** = novas imagens originais (não reutilizar o mesmo `momento_id` para fotos de datas diferentes). |

---

## 3. O que não é escopo desta especificação

- Comparar lado a lado duas datas (funcionalidade **futura** — ver §10).
- Módulo **Avaliação Postural** (placeholder no menu; integração posterior).
- Sincronização cloud ou multi-dispositivo.
- Auto-save ou histórico de versões automático por cada clique.

---

## 4. Modelo conceitual de dados

```
Cliente (já existe: tabela clientes)
  └── Momento clínico (novo)
        └── Imagem original (novo; 1..N por momento — ex. pé D e pé E)
              └── Marcação (novo; 0..1 por tipo_marcador por imagem)
                    ├── anotacao.json  (geometria editável)
                    └── marcado.png    (render exportado; opcional até 1º Salvar com PNG)
```

### 4.1 Entidades (proposta)

#### `momento_clinico`

| Campo | Tipo | Notas |
|-------|------|--------|
| `id` | PK | |
| `cliente_id` | FK → `clientes.id` | Obrigatório |
| `avaliacao_id` | FK → `avaliacoes.id` | **Opcional** até o módulo Avaliações estar integrado |
| `data_referencia` | date/datetime | Data do atendimento / da foto |
| `rotulo` | string | Ex.: "Avaliação inicial", "Retorno 3 meses" |
| `observacoes` | text | Opcional |
| `criado_em` / `atualizado_em` | datetime | |

#### `imagem_plantar`

| Campo | Tipo | Notas |
|-------|------|--------|
| `id` | PK | |
| `momento_id` | FK | |
| `lado` | enum | `direito` \| `esquerdo` \| `nao_informado` (recomendado exigir em UI futura) |
| `nome_arquivo` | string | Nome legível original |
| `path_original` | string | Caminho **relativo** ao projeto (`stored_path_for_write`) |
| `largura` / `altura` | int | Opcional, cache |
| `criado_em` | datetime | |

#### `marcacao_plantar`

| Campo | Tipo | Notas |
|-------|------|--------|
| `id` | PK | |
| `imagem_id` | FK → `imagem_plantar.id` | |
| `tipo_marcador` | enum | `plantar_linhas` \| `plantar_pontos` |
| `path_json` | string | Formato atual dos exportadores EFM |
| `path_png_marcado` | string | Nullable até gerar PNG |
| `regra_marcador_id` | int | Opcional; liga a `marker_rules` se aplicável |
| `criado_em` / `atualizado_em` | datetime | **Salvar** atualiza o mesmo registo (`atualizado_em`) |

**Regra de unicidade sugerida:** `(imagem_id, tipo_marcador)` único — uma marcação de linhas e uma de pontos por imagem.

**Regra de “Salvar”:** atualiza JSON sempre; gera/atualiza PNG conforme política (ver §6.3).

### 4.2 Relação com JSON existente

Os exportadores atuais (`marcador_plantar`, `marcador_pontos`) já produzem JSON com:

- `version`, `protocol`, `source_image`, `image_size`, `markers[]`

Ao salvar no paciente:

- Gravar esse payload em `path_json` (relativo).
- Incluir metadados EasyFeet no JSON ou em colunas da BD: `cliente_id`, `momento_id`, `imagem_id`, `marcacao_id`, `tipo_marcador` (recomendado: **colunas na BD** + JSON focado na geometria).

**Reabrir edição:** ler JSON → repor linhas/pontos no canvas (funcionalidade a desenvolver no EFM).

---

## 5. Armazenamento de ficheiros

Raiz sugerida (portável, alinhada a `easyfeet/paths.py`):

```
data/pacientes/{cliente_id}/
  momentos/{momento_id}/
    imagens/{imagem_id}/
      original.{ext}      # cópia imutável da foto carregada
      anotacao_linhas.json   # ou nome único por marcacao_id
      marcado_linhas.png
      anotacao_pontos.json
      marcado_pontos.png
```

Alternativa equivalente: ficheiros nomeados por `marcacao_id` dentro de `marcacoes/{marcacao_id}/`.

**Não usar** apenas `Imagens/Pacientes/{nome}/` como fonte de verdade (legado manual; migrável pontualmente).

**Backup:** pasta `data/` + `easyfeet.db` continuam a ser o pacote de cópia para pen drive / instalador.

---

## 6. Interface — módulo de marcações (EFM)

### 6.1 Barra superior (ordem)

```
[Paciente ▼]   [Tipo de marcador ▼]   [Abrir imagem…]   [Ajuda]
────────────────────────────────────────────────────────────────
[Ações: Exportar | Gerar | Sugerir | Limpar …]   [Salvar no paciente]
```

- **Paciente** acima de **Tipo de marcador** (decisão de UX).
- Lista de pacientes: **mesma** origem que o módulo Pacientes (`clientes`).
- Paciente **obrigatório** antes de carregar imagem (ou antes do primeiro Salvar).

### 6.2 Integração com EasyFeet principal

| Origem | Comportamento |
|--------|----------------|
| Menu **Módulos → Marcadores** | EFM abre; utilizador escolhe paciente no combo |
| **Pacientes** (futuro) | Com linha selecionada → "Abrir marcadores" passa `cliente_id` pré-preenchido |
| Sem licença | Item de menu oculto ou mensagem "Módulo não disponível no seu plano" |

### 6.3 Fluxo: nova imagem

1. Selecionar paciente.
2. Selecionar tipo (linhas ou pontos).
3. **Abrir imagem** → diálogo de ficheiro.
4. Sistema cria (ou associa) **momento** (novo ou "momento atual" — ver §6.5).
5. Copia ficheiro para `data/pacientes/.../original.*`.
6. Cria `imagem_plantar` + `marcacao_plantar` em rascunho (sem ficheiros até 1º Salvar, ou JSON vazio).
7. Utilizador marca no canvas.
8. **Salvar no paciente** → persiste JSON (+ opcionalmente PNG via mesma lógica de Exportar).

### 6.4 Fluxo: retomar trabalho

1. Selecionar paciente.
2. Painel/lista: **momentos** → **imagens** → marcações existentes.
3. Escolher marcação (linhas ou pontos) → carregar JSON no painel correto.
4. Editar → **Salvar** (atualiza mesmo `marcacao_id`).

### 6.5 Momento clínico na UI (MVP)

Opções (escolher uma na implementação):

- **A — Simplificado:** cada "Abrir imagem" cria **automaticamente** um novo `momento_clinico` com `data_referencia = hoje` e rotulo editável depois.
- **B — Explícito:** combo "Momento" entre Paciente e Tipo (lista + botão "Novo momento").

Recomendação para facilitar evolução: **B** já no MVP, mesmo que "Novo momento" pré-preencha a data de hoje.

### 6.6 Exportar vs Salvar

| Ação | Comportamento proposto |
|------|-------------------------|
| **Salvar no paciente** | Grava JSON no path do paciente; gera PNG marcado no path do paciente; atualiza BD |
| **Exportar PNG + JSON…** | Pode manter-se como cópia **adicional** para pasta à escolha do utilizador (relatório, email) |

---

## 7. Interface — módulo Pacientes (EasyFeet)

Secção (ou aba) **Marcações plantares** quando o paciente estiver selecionado:

- Lista cronológica de **momentos** (data, rótulo).
- Por momento: imagens (lado, miniatura) e estado linhas/pontos (salvo / não salvo).
- Ações: **Ver original** | **Ver marcada** | **Continuar no EFM**.

Requisito de licença: secção visível só se módulo marcadores ativo.

---

## 8. Licenciamento / feature gate

- **Um** `menu-config` (ou ficheiro de licença local) define módulos ativos.
- Itens `modulos` → `efm_marcadores`, `avaliacao_postural` respeitam flag.
- Não criar segundo executável nem segunda base de pacientes.
- Build/installer pode incluir código EFM sempre; runtime bloqueia sem licença.

*(Detalhe comercial — chaves, trial — fora desta especificação técnica.)*

---

## 9. Fases de implementação sugeridas

| Fase | Entregável | Protótipo de teste (opcional) |
|------|------------|-------------------------------|
| **1** | Migração BD + repositórios + paths + Salvar/Carregar JSON | `EF_teste_marcadores_paciente.bat` |
| **2** | EFM: combo Paciente + Momento; Salvar; lista no paciente | Integração `EF.bat` |
| **3** | Reabrir marcação no editor; PNG sempre no Salvar | — |
| **4** | Atalho Pacientes → EFM com `cliente_id` | — |
| **5** | Licença / ocultar menu | — |

Ordem pode ser ajustada; fases 1–2 entregam valor mínimo utilizável.

---

## 10. Pendências futuras (registo explícito)

| ID | Descrição | Prioridade |
|----|-----------|------------|
| **PEND-MARC-001** | **Comparar evolução:** visualização lado a lado (ou sobreposição alinhada) de dois `momento_clinico` do mesmo paciente, mesmo `tipo_marcador` e preferencialmente mesmo `lado`. | Alta (palmilhas) |
| **PEND-MARC-002** | Linha do tempo / filtros por intervalo de datas no histórico do paciente. | Média |
| **PEND-MARC-003** | Exportação de relatório (PDF/Word) com pares original/marcado de vários momentos. | Média |
| **PEND-MARC-004** | Vincular `momento_clinico.avaliacao_id` quando o CRUD de Avaliações estiver ativo. | Média |
| **PEND-MARC-005** | Migração pontual de ficheiros legados em `Imagens/Pacientes/{nome}/` para `data/pacientes/{id}/`. | Baixa |
| **PEND-MARC-006** | Duplicar momento ou marcação ("Salvar como nova versão") — só se surgir necessidade além de "novo momento". | Baixa |
| **PEND-NAV-001** | **Teste do Navicular** — ficha de medição (sentado + em pé); **Modo A:** até 10 mm = normal (Brody); Modos B/C futuros. Doc: `Documentos de Apoio/EF - Navicular mm x percentual.md`. | **Alta (prioridade utilizador)** |

Estas pendências devem ser refletidas em `2026-05-08-roadmap-fases-e-marcos.md` (Fase 2+) quando o produto retomar desenvolvimento.

---

## 11. Riscos e mitigações

| Risco | Mitigação |
|-------|-----------|
| Ficheiros órfãos se apagar registo na BD | Transação: criar registo BD antes de mover ficheiro; job de limpeza opcional |
| Caminhos absolutos legados | `resolve_project_file` / `stored_path_for_write` (já existentes) |
| Utilizador fecha EFM sem Salvar | Diálogo "Alterações não salvas" |
| Imagem muito grande | Limites opcionais de tamanho; mensagem clara |
| Confusão linhas vs pontos | Um registo `marcacao_plantar` por tipo; UI deixa tipo explícito |

---

## 12. Critérios de aceitação (quando implementar)

1. Com módulo licenciado, consigo selecionar paciente no EFM, carregar imagem, marcar, **Salvar**, fechar e reabrir a **mesma** marcação com geometria intacta.
2. No paciente, consigo ver **original** e **marcada** da mesma sessão.
3. Num **novo momento** (nova data), consigo guardar **nova** original sem sobrescrever a anterior.
4. Na mesma imagem do mesmo momento, consigo ter marcação de **linhas** e de **pontos** independentes.
5. Sem licença, não acedo ao fluxo de marcações no menu.
6. Não existe segundo cadastro de pacientes só para o EFM.

---

## 13. Referências no código atual

| Área | Ficheiros |
|------|-----------|
| EFM UI | `easyfeet_markers/app.py`, `EFM_Marcadores.py` |
| Painéis | `marcador_plantar/app_tk.py`, `marcador_pontos/app_tk.py` |
| Export JSON/PNG | `marcador_plantar/exporter.py`, `marcador_pontos/exporter.py` |
| Pacientes | `easyfeet/gui.py`, `easyfeet/models.py` (`Cliente`) |
| Caminhos | `easyfeet/paths.py` |
| Menu | `menu-config-v1.json` |
| Roadmap | `MDs/2026-05-08-roadmap-fases-e-marcos.md` (Fase 2) |

---

## 14. Histórico do documento

| Data | Versão | Notas |
|------|--------|--------|
| 2026-05-26 | 1.0 | Especificação inicial após alinhamento: sistema único EasyFeet, módulo opcional por licença, selector de paciente no EFM, momentos para evolução, Salvar sem autosave. |
