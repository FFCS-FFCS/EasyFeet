# EasyFeet — Rascunho: menu v2 + Hub do paciente

**Status:** parcialmente validado (2026-05-30) — sem implementação em código  
**Data:** 2026-05-30 (UTC-3)  
**Versão alvo do produto:** evolução pós v1.0.0  
**Pasta oficial:** `C:\Users\flavi\OneDrive\Documentos\Ideias_Projetos\Cursor_Projetos\EasyFeet`  
**JSON activo:** `menu-config-v2.json` (M1 — v2.0.0). Arquivo `menu-config-v1.json` mantido como referencia da v1.

### Decisões fechadas nesta revisão

| Decisão | Estado |
|---------|--------|
| Plantígrafo → subitem **Análise** (não "Captura"; id técnico `efm_marcadores`) | **OK** |
| Laudos **global** + secção Laudos no **Hub** | **OK** |
| **Baropodômetro** fora do menu até existir módulo | **OK** |
| **Análise de marcha** fora do menu v2 | **OK** (2026-05-30) |
| **Palmilhas** transversal (não dentro de módulo) + secção no Hub | **OK** — ordem física no menu **tarda** (depende de laudos; ver § CRM) |
| **Podoscópio** → Ficha / Avaliação · Laudos · Configurações | **OK** |
| **Config** — Regras Marcadores → Plantígrafo → Configurações | **OK** |
| Modelo **CRM** — paciente no centro; avaliações/laudos/palmilhas derivam dele | **OK** (princípio orientador) |
| **Hub** — lista/cadastro vs ficha clínica (dois ecrãs) | **OK** — implementar **Hub v0** básico (§ 6) |
| **B+ Hub-first** — aceder/rever paciente antes das acções clínicas | **OK** |

---

## Objetivo deste documento

Consolidar decisões de produto discutidas na sessão e propor:

1. Resposta **A vs B** (contexto paciente/momento no Hub vs no módulo).
2. **Menu v2** (equipamentos em primeiro nível, palmilha transversal, laudos consolidados).
3. **Wireframe do Hub do paciente** (rotas futuras, secções, fluxos).
4. Checklist **item a item** para você validar antes de codar.

---

## 1. A vs B — paciente/momento no Hub ou no módulo?

### Pergunta

Ao abrir **Plantígrafo → Análise** sem paciente:

| Opção | Comportamento |
|-------|----------------|
| **A** | Combo paciente + momento dentro do EFM (como hoje) |
| **B** | Obrigar contexto vindo do Hub (“Selecione paciente na ficha clínica”) |

### Resposta directa: **B deixa os módulos menos poluídos**

Sim. Com **B** (ou variante **B+** abaixo), a tela do módulo **não precisa** repetir:

- combo Paciente  
- combo Momento  
- botão Novo momento  
- (eventualmente) escolha de “qual imagem reabrir”

Isso fica **uma vez** no Hub. O módulo recebe `cliente_id`, `momento_id` (e opcionalmente `imagem_id`) e foca só na **tarefa clínica** (marcar, medir, preencher ficha).

### EFM hoje — por que parece complexo

Header actual (1.ª linha + barra Ações):

```
Paciente [combo] | Momento [combo] | [Novo momento] | Tipo marcador [combo] | [Carregar imagem] [Ajuda]
[Ações] Exportar | Gerar | Sugerir | Limpar… | Limpar todos | Salvar no paciente
+ canvas + painel lateral do módulo
```

**~6 controlos de contexto** + **~6 acções** antes do trabalho clínico. Muito para uma ferramenta de captura.

### EFM futuro (com B+) — alvo de simplicidade

**Contexto** (paciente, momento, imagem) → definido no **Hub** ou passado ao abrir.

**Análise (EFM)** — header reduzido:

```
Plantígrafo — Análise          Maria Silva · Momento 30/05/2026 14:30  [Trocar contexto → Hub]
Linhas | Pontos                [Carregar imagem] [Ajuda]              [Salvar]
+ canvas + ferramentas essenciais (zoom; limpar; sugerir — possivelmente menu ou barra compacta)
```

| Elemento | Onde fica |
|----------|-----------|
| Paciente / Momento / Novo momento | **Hub → Linha do tempo** |
| Reabrir marcação antiga | **Hub → Linha do tempo** ou atalho “Continuar” no card do momento |
| Tipo Linhas vs Pontos | **Dentro** do módulo (é da ferramenta) |
| Carregar imagem | **Dentro** do módulo |
| Salvar | **Dentro** do módulo |
| Exportar avulso (sem paciente) | Config avançada ou modo técnico — não no fluxo normal |

### Recomendação: **B+ (Hub-first com atalho controlado)**

| Fluxo | Comportamento |
|-------|----------------|
| **Principal (B)** | Menu Plantígrafo → Análise **sem** paciente → ecrã leve: “Selecione um paciente na ficha clínica” + botão **Ir para Pacientes** |
| **Com contexto (Hub)** | Hub → card do momento → **Plantígrafo / Análise** → EFM abre **sem combos** |
| **Atalho recepção (A lite)** | Lista Pacientes → **Abrir análise** (1 clique) com paciente já definido; momento = “Novo momento de hoje” criado no Hub automaticamente |

Assim: módulo **limpo** no fluxo clínico; **A** só como atalho, não como layout permanente.

**Decisão:** adoptar **B+** como padrão — **OK** (2026-05-30).

| OK | Ajuste | Notas |
|----|--------|-------|
| OK | | CRM: paciente primeiro, depois módulos |

---

## 2b. Modelo CRM — paciente no centro

O EasyFeet comporta-se como um **CRM clínico**: o **paciente** (`cliente`) é o registo mestre; tudo o resto **deriva** dele.

```
                    ┌─────────────┐
                    │  PACIENTE   │  ← cadastro + avaliação inicial
                    └──────┬──────┘
           ┌───────────────┼───────────────┐
           ▼               ▼               ▼
    Momentos clínicos   Laudos          Palmilhas / acções
           │
           ├── Plantígrafo (análise, imagens, marcações)
           ├── Podoscópio (ficha + avaliação)
           └── (outros módulos licenciados)
```

| Analogia CRM | EasyFeet |
|--------------|----------|
| Lista de contactos | **Pacientes** (lista + cadastro básico) |
| Ficha do contacto / deal | **Hub** = ficha clínica do paciente |
| Actividades / histórico | **Linha do tempo** (momentos + módulos) |
| Documentos | **Laudos** (por módulo + consolidado) |
| Encomenda / entrega | **Palmilhas** (workflow transversal) |

**Fluxo do dia a dia (B+):** quase sempre **localizar ou abrir o paciente** → rever contexto no Hub → só depois Plantígrafo, Podoscópio, laudo, palmilha.

**Palmilhas “no topo” (conceito vs menu):**

| Significado | Decisão |
|-------------|---------|
| **Transversal** — não é filho de Plantígrafo/Podoscópio | **Sim** |
| **Secção no Hub** do paciente | **Sim** |
| **Ordem física alta no menu lateral** (acima dos módulos) | **Não necessário** — palmilha é uma das **últimas** funcionalidades (depende de laudos/módulos). No `menu-config-v2.json`, `order: 75` (após equipamentos, antes de Relatórios). Pode ficar placeholder até existir lógica. |

---

| # | Princípio |
|---|-----------|
| M1 | **Equipamento/recurso** em primeiro nível (Plantígrafo, Podoscópio…), não “Marcadores”. |
| M2 | **Palmilha** transversal (item raiz + Hub); **ordem no menu** pode ser tardia (não “topo” físico). |
| M3 | **Laudos** consolidados no topo + laudo por módulo como subitem. |
| M4 | **Config por módulo**; Config global só clínica/licenças/templates. |
| M5 | Remover ou fundir placeholders MVP: Avaliações, Imagens (topo). |
| M6 | **Pacientes** = lista + cadastro básico; **Hub** = rota `/pacientes/{id}` (ficha clínica). |
| M7 | IDs técnicos estáveis (`efm_marcadores`…) mesmo que labels mudem (compatibilidade). |

---

## 3. Menu v2 — árvore proposta (revisão item a item)

Legenda: `[PLACEHOLDER]` = ecrã stub; `[EXISTE]` = já implementado; `[MOVER]` = hoje noutro sítio.

```
Dashboard                                    [EXISTE]

Pacientes                                    [EXISTE — evoluir]
  (lista + cadastro básico; botão "Abrir ficha clínica")

Laudos                                       [PLACEHOLDER — consolidado global]

── Recursos clínicos (equipamentos) ──

Plantígrafo                                  [MOVER de Módulos → Marcadores]
  ├── Análise                                [EXISTE — EFM / efm_marcadores]
  ├── Laudos                                 [PLACEHOLDER]
  └── Configurações                          [MOVER — Regras Marcadores]

Podoscópio                                   [EXISTE parcial]
  ├── Ficha / Avaliação                      [EXISTE — ficha + avaliação]
  ├── Laudos                                 [PLACEHOLDER]
  └── Configurações                          [PLACEHOLDER]

Avaliação postural                           [PLACEHOLDER]
  ├── Avaliação · Laudos · Configurações

Palmilhas                                    [PLACEHOLDER — transversal; order ~75; implementação tardia]
  (item raiz + secção Hub; depende de laudos)

Análise de marcha                            [FORA do v2]

Relatórios                                   [PLACEHOLDER]

Configurações                                [EXISTE — reduzir escopo]
  ├── Clínica / identidade                   [PLACEHOLDER]
  ├── Utilizadores e perfis                  [PLACEHOLDER]
  ├── Licenças de módulos                    [PLACEHOLDER futuro]
  └── Templates PDF (cabeçalho/rodapé)       [PLACEHOLDER — parcial em pdf_brand]
```

### Itens removidos ou absorvidos

| Item actual (v1) | Destino v2 |
|------------------|------------|
| Módulos (hub genérico) | **Dissolvido** — filhos passam a raiz |
| Avaliações (topo) | **Hub → Linha do tempo** + cadastro (avaliação inicial) |
| Imagens (topo) | **Dentro de cada módulo / momento** |
| Laudos (topo CRUD MVP) | **Laudos consolidado** + laudos por módulo |
| Config → Regras Marcadores | **Plantígrafo → Configurações** |

---

## 4. Menu v2 — JSON (`menu-config-v2.json`)

Ficheiro draft na **raiz do projeto** (não activo; `menu-config-v1.json` continua em uso).

Alterações face ao rascunho anterior:

| Campo | Valor validado |
|-------|----------------|
| Plantígrafo → filho | **label:** `Análise` · **route:** `/plantigrafo/analise` · **id:** `efm_marcadores` |
| Laudos topo | `laudos_consolidado` em `/laudos` |
| Baropodômetro | **Removido** até existir módulo |
| Análise de marcha | **Fora do v2** (decidido 2026-05-30) |

Trecho principal (Plantígrafo + Laudos):

```json
{
  "id": "laudos_consolidado",
  "label": "Laudos",
  "route": "/laudos",
  "order": 40
},
{
  "id": "plantigrafo",
  "label": "Plantígrafo",
  "children": [
    {
      "id": "efm_marcadores",
      "label": "Análise",
      "route": "/plantigrafo/analise"
    },
    { "id": "plantigrafo_laudos", "label": "Laudos", "route": "/plantigrafo/laudos" },
    { "id": "plantigrafo_config", "label": "Configurações", "route": "/plantigrafo/configuracoes" }
  ]
}
```

Ver ficheiro completo: `menu-config-v2.json`.

**Nota:** `hiddenInSidebar` e `licenseModule` são extensões propostas ao validador/menu — implementar quando adoptar v2.

### Checklist menu — validar com OK / Ajuste

| Item | OK | Ajuste | Notas |
|------|----|--------|-------|
| Palmilhas (transversal) | OK | | **order 75** no menu; Hub secção v3 |
| Laudos consolidado (40) | OK | | + Hub → Laudos |
| Plantígrafo > **Análise** (id `efm_marcadores`) | OK | | route `/plantigrafo/analise` |
| Plantígrafo > Laudos | | | |
| Plantígrafo > Config (ex-Regras Marcadores) | OK | | |
| Podoscópio > Ficha / Avaliação / Laudos / Config | OK | | ficha + avaliação |
| Placeholders: postural | | | |
| Baropodômetro no menu | — | OK | **Removido** até existir |
| Análise de marcha no menu | — | OK | **Fora do v2** (2026-05-30) |
| Remover Avaliações / Imagens / hub Módulos | | | |
| Config global (clínica, licenças…) | | | |

---

## 5. Wireframe — Pacientes (lista + cadastro)

Rota: `/pacientes`

```
┌─────────────────────────────────────────────────────────────────────────┐
│  Pacientes                    [Buscar…]  [Filtros ▼]     [+ Novo]       │
├─────────────────────────────────────────────────────────────────────────┤
│  Tabela: Nome | Idade | Último atendimento | …                          │
│  (duplo clique ou botão "Abrir ficha clínica")                          │
├─────────────────────────────────────────────────────────────────────────┤
│  Painel lateral / modal — CADASTRO BÁSICO (quando criar/editar)         │
│  • Identificação, contactos, dados corporais, IMC                       │
│  • Avaliação inicial (texto; futuro: rascunho IA + editar)              │
│  • [Gravar cadastro]  [Abrir ficha clínica → Hub]                       │
└─────────────────────────────────────────────────────────────────────────┘
```

**O que NÃO fica aqui (v2):** histórico de marcadores, laudos de módulos, linha do tempo.

| OK | Ajuste | Notas |
|----|--------|-------|
| | | |

---

## 6. Wireframe — Hub do paciente (ficha clínica)

Rota: `/pacientes/{id}` — **não aparece no menu lateral**; entra pela lista.  
**Metáfora:** ficha do contacto no CRM — tudo do paciente converge aqui.

### Hub v0 (primeira implementação — básico, extensível)

Objectivo: **não redesenhar tudo depois** — mesma rota e secções, conteúdo cresce por fases.

| Fase | Secções activas | Conteúdo mínimo |
|------|-----------------|-----------------|
| **v0 (M2)** | **Resumo** + **Linha do tempo** | Nome, dados-chave; lista momentos; **Novo momento**; atalhos módulos |
| **v1 (M3)** | + timeline rica | Cards Plantígrafo (histórico marcadores migrado) |
| **v2** | tab **Laudos** | Tabela laudos do paciente |
| **v3** | tab **Palmilhas** | Workflow palmilha |

**Dois ecrãs (CRM):** **Pacientes** = lista/cadastro · **Hub** = ficha clínica. Duplo clique → Hub.

```
┌─────────────────────────────────────────────────────────────────────────┐
│  ← Pacientes    Maria Silva (#12)    32 anos    [Editar cadastro]       │
├──────────────┬──────────────────────────────────────────────────────────┤
│  Resumo      │  (conteúdo da secção activa)                             │
│  Linha do    │                                                          │
│    tempo     │                                                          │
│  Laudos      │                                                          │
│  Palmilhas   │                                                          │
│  ─────────   │                                                          │
│  Atalhos     │  Plantígrafo · Podoscópio · … (só módulos licenciados)   │
└──────────────┴──────────────────────────────────────────────────────────┘
```

### 6.1 Secção — Resumo

```
• Dados-chave (nome, idade, IMC, alertas)
• Avaliação inicial (versão actual; editar; histórico de versões futuro)
• Últimos laudos (3) + link "Ver todos"
• Palmilhas em andamento (se houver)
• [+ Novo momento clínico]
```

### 6.2 Secção — Linha do tempo (núcleo do Hub)

Momentos **globais**, ordenados do mais recente:

```
┌─ Momento: 30/05/2026 14:30 — Retorno 3 meses ─────────────────────────┐
│  Plantígrafo:  2 imagens · linhas salvas · pontos salvos               │
│               [Análise] [Ver laudo] [Ver original / marcada]          │
│  Podoscópio:  ficha preenchida                                        │
│               [Abrir ficha] [Ver laudo PDF]                           │
│  Laudo profissional: rascunho                                         │
│               [Editar]                                                │
└───────────────────────────────────────────────────────────────────────┘

┌─ Momento: 15/03/2026 — Avaliação inicial ─────────────────────────────┐
│  …                                                                    │
└───────────────────────────────────────────────────────────────────────┘
```

**Histórico de marcadores** (hoje em Pacientes) → cards **Plantígrafo** dentro de cada momento.

Se módulo **não licenciado:** card não aparece (não bloco vazio).

### 6.3 Secção — Laudos

Tabela unificada do **paciente**:

| Data | Momento | Origem | Tipo | PDF | Acções |
|------|---------|--------|------|-----|--------|
| … | … | Plantígrafo | Laudo módulo | Sim | Ver / Reabrir |
| … | … | Podoscópio | Laudo módulo | Sim | Ver |
| … | … | Profissional | Laudo clínico | — | Editar |
| … | — | Cadastro | Avaliação inicial | — | Editar |

### 6.4 Secção — Palmilhas

Pedidos deste paciente + **insumos escolhidos** (laudos/momentos/módulos).

```
[+ Novo pedido de palmilha]
  → wizard: finalidade → seleccionar insumos (checkbox por laudo/módulo) → gravar
```

### 6.5 Atalhos laterais (módulos)

Abre ferramenta **com contexto** (B+):

- Se **momento seleccionado** na timeline → passa `momento_id`
- Se nenhum → Hub pede “Seleccione ou crie um momento” **antes** de abrir

| OK | Ajuste | Notas |
|----|--------|-------|
| Hub com sub-nav (Resumo / Timeline / Laudos / Palmilhas) | OK | | v0: só Resumo + Timeline; resto fases v1–v3 |
| Timeline como eixo central | OK | | CRM |
| Histórico marcadores dentro de Timeline | OK | | M3 |
| Atalhos de módulos no Hub | OK | | B+ |
| Secção Laudos no Hub | OK | | tab v2 |
| Dois ecrãs (lista vs Hub) | OK | | padrão CRM |

---

## 7. Wireframe — Plantígrafo

### 7.1 Análise (EFM simplificado — B+)

**Sem contexto** (abriu pelo menu):

```
┌─────────────────────────────────────────────────────────────────────────┐
│  Plantígrafo — Análise                                                  │
│                                                                         │
│     Selecione um paciente e momento na ficha clínica.                   │
│     [Ir para Pacientes]  [Abrir ficha de paciente recente ▼]            │
└─────────────────────────────────────────────────────────────────────────┘
```

**Com contexto** (vindo do Hub):

```
┌─────────────────────────────────────────────────────────────────────────┐
│  Análise — Maria Silva · Momento 30/05/2026 14:30    [Alterar contexto] │
│  Linhas | Pontos     [Carregar imagem]  [Ajuda]           [Salvar]      │
├─────────────────────────────────────────────────────────────────────────┤
│  [Ferramentas compactas: zoom | sugerir | limpar ▼]                     │
├─────────────────────────────────────────────────────────────────────────┤
│                         CANVAS                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

Exportar PNG+JSON → **modo avançado** ou automático no Salvar (não botão prominente).

### 7.2 Laudos (plantígrafo)

Lista filtrada (paciente opcional); gerar PDF a partir de momento + marcações + texto clínico.

### 7.3 Configurações

Conteúdo actual **Regras Marcadores** (`configuracoes_regras_marcadores`).

| Item Plantígrafo | OK | Ajuste | Notas |
|------------------|----|--------|-------|
| Label raiz "Plantígrafo" | | | |
| Sub **"Análise"** (não "Marcadores" / "Captura") | OK | | validado 2026-05-30 |
| EFM sem combos paciente/momento | | | B+ |
| Laudos subitem | | | |
| Config aqui (não global) | | | |

---

## 8. Wireframe — Podoscópio

| Subitem | Actual | v2 |
|---------|--------|-----|
| Ficha / Avaliação | `podoscopio_ficha_tecnica` | Igual; abre **com paciente+momento** do Hub |
| Laudos | PDF ficha (parcial) | Laudo formal do módulo na lista consolidada |
| Configurações | — | Campos default, textos PDF, etc. |

Fluxo Hub: card Podoscópio no momento → **Abrir ficha** (preenche `cliente_id`, `momento_id`).

| Item Podoscópio | OK | Ajuste | Notas |
|-----------------|----|--------|-------|
| 3 subitens (Ficha / Laudos / Config) | OK | | label Ficha / Avaliação |
| Ficha ligada ao momento global | OK | | B+ |

---

## 9. Wireframe — Laudos (consolidado)

Rota: `/laudos` — visão **clínica global** (todos pacientes):

```
Filtros: Paciente [   ]  Módulo [todos ▼]  Período [   ]  Tipo [todos ▼]

Tabela: Paciente | Data | Momento | Módulo | Tipo laudo | PDF | Acções
```

Duplicata intencional: mesma informação filtrada no **Hub → Laudos** (só aquele paciente).

| Item Laudos | OK | Ajuste | Notas |
|-------------|----|--------|-------|
| Menu topo "Laudos" (global) | OK | | validado 2026-05-30 |
| Laudos também no Hub | OK | | |
| Laudo por módulo (submenu) | | | |

---

## 10. Wireframe — Palmilhas

Rota: `/palmilhas`

```
[Lista pedidos — todos pacientes ou filtro]
[+ Novo pedido]

Wizard novo pedido:
  1. Paciente (se não veio do Hub)
  2. Finalidade (correção / estímulo / esportiva / …)
  3. Insumos: ☑ Laudo plantígrafo 30/05  ☑ Ficha podoscópio  ☐ Laudo postural
  4. Material, previsão, observações
  5. Gravar
```

| Item Palmilhas | OK | Ajuste | Notas |
|----------------|----|--------|-------|
| Topo transversal | OK | | order menu 75 |
| Profissional escolhe insumos | OK | | |
| Secção Palmilhas no Hub | OK | | implementação tardia (v3) |

---

## 11. Wireframe — Configurações

### Global (`/configuracoes`)

| Subitem | Conteúdo |
|---------|----------|
| Clínica | Nome, logo, contactos |
| Utilizadores | admin / fisio / recepção |
| Licenças | módulos activos (futuro) |
| Templates PDF | cabeçalho/rodapé partilhados |

### Por módulo

| Módulo | Exemplo |
|--------|---------|
| Plantígrafo | Regras A–D, defaults marcadores |
| Podoscópio | Campos da ficha, opções PDF |
| … | específico do equipamento |

| Item Config | OK | Ajuste | Notas |
|-------------|----|--------|-------|
| Regras Marcadores → Plantígrafo | OK | | |
| Config global reduzida | OK | | |

---

## 12. Rotas futuras (mapa para web)

| Rota | Ecrã |
|------|------|
| `/dashboard` | Dashboard |
| `/pacientes` | Lista + cadastro básico |
| `/pacientes/{id}` | Hub (sub: resumo, timeline, laudos, palmilhas) |
| `/pacientes/{id}/momentos/{mid}` | Detalhe momento (opcional fase 2) |
| `/plantigrafo/analise` | EFM (Plantígrafo → Análise) |
| `/plantigrafo/laudos` | Laudos plantígrafo |
| `/podoscopio/ficha` | Ficha podoscópio |
| `/laudos` | Consolidado global |
| `/palmilhas` | Pedidos palmilha |

IDs de menu = chaves de módulo para licenciamento e deep links.

---

## 13. Ordem de implementação sugerida (após validar este MD)

| Etapa | Entrega | Teste |
|-------|---------|-------|
| **M1** | Activar menu v2 (JSON + placeholders; sem Hub) | Navegação sidebar |
| **M2** | Hub vazio + rota a partir de Pacientes | Abrir ficha |
| **M3** | Timeline placeholder + mover histórico marcadores | Regressão Fase 2 B |
| **M4** | EFM B+ (contexto do Hub; header simples) | Análise + salvar |
| **M5** | Config plantígrafo movida | Regras marcadores |
| **M6+** | Laudos, palmilha insumos, IA avaliação inicial | Por entrega |

---

## 14. Como revisar este documento

1. Percorra as tabelas **OK / Ajuste / Notas** (secções 1, 3, 5–11).
2. Responda no Cursor com OK / Ajuste por secção (ex.: Podoscópio, Palmilhas, B+).
3. Após consenso, próximo passo = **M1** (só menu + placeholders).

---

## 15. Referências

| Documento | Relação |
|-----------|---------|
| `especificacao-marcacoes-vinculo-paciente.md` | Momentos, imagens, marcações (Plantígrafo) |
| `menu-config-v1.json` | Menu actual |
| `versionamento-local-easyfeet.md` | Tags / snapshots antes de M1 |

---

*Rascunho gerado para revisão conjunta. Não altera código até validação.*
