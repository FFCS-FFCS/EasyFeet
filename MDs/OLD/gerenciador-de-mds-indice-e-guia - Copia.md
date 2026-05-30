# EasyFeet - Gerenciador de MDs (Indice e Guia)

Ultima atualizacao: 2026-05-08 (revisao: conteudo consolidado com o snapshot `2026-05-08-gerenciador-de-mds-indice-e-guia.md`)

## Objetivo deste arquivo

Este documento funciona como:

- indice da documentacao em `MDs`;
- dicionario/guia de leitura de cada MD;
- ponto unico para entender o estado documental do produto;
- base para atualizacao evolutiva (timeline de produto).

## Como usar este documento

Este e o **arquivo mestre fixo** da pasta `MDs` (nome **sem data**).  
Ele deve ser **sempre sobrescrito/atualizado** a partir da leitura de todos os `.md` existentes, mantendo:

- catalogo completo por tema;
- linha do tempo por tema (primeiro ao ultimo);
- baseline + deltas (o que mudou a partir da segunda versao);
- ordem recomendada de leitura.

Excecao de leitura na regeneracao: **nao** usar o proprio conteudo deste arquivo como fonte de verdade sobre o produto; reler os demais MDs e recompor o indice. O arquivo `2026-05-08-gerenciador-de-mds-indice-e-guia.md` e **snapshot historico** (nao e o alvo de sobrescrita do protocolo).

### Regeneracao deste arquivo — circularidade ou nao?

- **Sim**, ele carrega instrucoes para **ser gerado de novo** e **substituido** (`sobrescrito`). Isso e util: qualquer um (ou um assistente) sabe qual protocolo seguir sem procurar outro documento.
- **Nao**, isso **nao e um loop problematico**. O fluxo correto na regeneracao e:
  1. Ler **todos** os outros `*.md` da pasta `MDs` (**exceto** este `gerenciador-de-mds-indice-e-guia.md`).
  2. A partir deles, atualizar catalogo por tema, baseline/deltas, guia rapido, ordem de leitura, etc.
  3. **Gravar por cima** deste arquivo com o texto novo, **mantendo de propósito** de novo estas seções fixas (objetivo, convencoes, protocolo, template) para a proxima rodada.

A versao anterior do gerenciador **nao** e a fonte da lista de documentos nem dos fatos do produto — so pode ser consultada opcionalmente para copiar redacao estrutural (por exemplo titulos), nunca como substituto de reler cada MD tema a tema.

## Ordem recomendada para entendimento completo

Ordem base (ajustavel sempre que aparecer MD novo mais prioritario ao contexto atual; ao pedir atualizacao do gerenciador, reavaliar esta sequencia contra o conjunto atual de `.md`).

Fluxo esperado nesta revisao:

- **Por que Visao geral em primeiro lugar:** responde "o que e o projeto e para que serve"; e o primeiro recado para um leitor desconhecido.
- **`MD_MESTRE-indice-e-governanca.md` logo em seguida (segundo lugar):** nao compete com a historia do produto; explica nomenclatura, governanca e transicao dos MDs. Quem quer so contexto pode parar na Visao geral; quem vai manter documentacao le Visao geral + MESTRE cedo para nao ler o restante "no escuro".

1. Visao geral (`2026-05-07-visao-geral-e-registro-evolutivo.md`)
2. Governanca documental — transicao (`MD_MESTRE-indice-e-governanca.md`)
3. Stack tecnologica (`2026-05-08-stack-tecnologica-e-direcionadores-de-evolucao.md`)
4. Arquitetura e decisoes (`2026-05-08-arquitetura-e-decisoes-tecnicas.md`)
5. Status tecnico e pendencias (`2026-05-07-status-tecnico-e-pendencias.md`)
6. Riscos e mitigacao (`2026-05-08-riscos-e-plano-de-mitigacao.md`)
7. Plano de release e validacao (`2026-05-08-plano-de-release-e-validacao.md`)
8. Roadmap de fases e marcos (`2026-05-08-roadmap-fases-e-marcos.md`)

## Convencao geral dos arquivos MD

- Padrao de nome: `AAAA-MM-DD-assunto.md` (com excecoes intencionais **sem data**: este gerenciador e `MD_MESTRE-indice-e-governanca.md`).
- Idioma: portugues (com foco tecnico e pratico).
- Estilo: objetivo, com secoes curtas e reutilizaveis.
- Regra: toda mudanca relevante no produto deve refletir em pelo menos um MD.

## Guia rapido por arquivo (finalidade e perguntas)

### `gerenciador-de-mds-indice-e-guia.md` (este arquivo)

**Finalidade:** indice vivo, catalogo por tema, baseline/deltas, ordem de leitura, protocolo de regeneracao e criterios de consistencia.  
**Quando ler:** para navegar a pasta `MDs` e orientar atualizacoes do acervo.  
**Perguntas que responde:** Quais temas existem? Qual a ordem de leitura? Como pedir regeneracao? O que checar na consistencia?

### `MD_MESTRE-indice-e-governanca.md`

**Finalidade:** governanca documental, baseline/delta e visao consolidada do acervo (documento vivo sem data no nome).  
**Quando ler:** em segundo na ordem recomendada, ou ao definir/comparar regras de documentacao com o gerenciador.  
**Perguntas que responde:** Qual o modelo baseline/delta? Qual o papel do mestre frente aos MDs datados?

### `2026-05-08-gerenciador-de-mds-indice-e-guia.md` (snapshot)

**Finalidade:** preservar a **primeira versao publicada** do texto do gerenciador com nome datado (inclui gatilhos de pedido, mapa original e criterios).  
**Quando ler:** auditoria, comparacao historica ou recuperacao de redacao.  
**Perguntas que responde:** O que foi proposto na primeira versao do gerenciador com `AAAA-MM-DD` no nome?

### `2026-05-07-visao-geral-e-registro-evolutivo.md`

**Finalidade:** contexto de produto para publico tecnico/negocio.  
**Quando ler:** primeiro contato com o projeto.  
**Perguntas que responde:** O que e o EasyFeet? Que problema resolve? O que ja funciona? Quais proximos passos de alto nivel?

### `2026-05-07-status-tecnico-e-pendencias.md`

**Finalidade:** fotografia tecnica do momento + backlog de pendencias.  
**Quando ler:** planejamento tecnico de curto prazo.  
**Perguntas que responde:** Qual status atual por area? Quais pendencias priorizadas? Qual checklist rapido de validacao?

### `2026-05-08-stack-tecnologica-e-direcionadores-de-evolucao.md`

**Finalidade:** registrar stack usada e direcao tecnica estrategica.  
**Quando ler:** discussoes de tecnologia, migracao, POC web.  
**Perguntas que responde:** Quais tecnologias estao em uso? O que e migravel (ex.: SQLite para PostgreSQL)? Como distribuimos hoje? Qual visao de evolucao para web?

### `2026-05-08-arquitetura-e-decisoes-tecnicas.md`

**Finalidade:** historico de decisoes de arquitetura e racional.  
**Quando ler:** antes de mudar arquitetura ou adotar nova abordagem.  
**Perguntas que responde:** Quais decisoes foram tomadas? Quais alternativas foram consideradas? Quais gatilhos exigem revisao arquitetural?

### `2026-05-08-riscos-e-plano-de-mitigacao.md`

**Finalidade:** mapa de risco com acoes praticas de mitigacao.  
**Quando ler:** antes de release/demo e em planejamento de estabilidade.  
**Perguntas que responde:** Quais riscos sao altos agora? O que fazer para reduzir impacto?

### `2026-05-08-plano-de-release-e-validacao.md`

**Finalidade:** padrao operacional para gerar e validar release.  
**Quando ler:** toda vez que for gerar instalador/zip para entrega.  
**Perguntas que responde:** Qual passo a passo de release? Quais criterios de aceite? Como agir em rollback?

### `2026-05-08-roadmap-fases-e-marcos.md`

**Finalidade:** visao de fases e marcos do produto.  
**Quando ler:** alinhamento de prioridade, escopo e timeline.  
**Perguntas que responde:** Em que fase estamos? O que entra nas proximas fases? Quais dependencias existem entre fases?

## Regra de historico (baseline + delta)

- Primeiro arquivo cronologico de um tema = **Baseline** (versao completa).
- Arquivos seguintes do mesmo tema = **Delta** (somente mudancas).
- A partir do segundo arquivo, relatar:
  - adicionado;
  - alterado;
  - removido;
  - impacto.

Exemplo:

- `2026-05-08-roadmap-fases-e-marcos.md` = baseline
- `2026-05-10-roadmap-fases-e-marcos.md` = delta (comparado ao baseline/anterior)

## Catalogo por tema (estado atual)

## Tema: gerenciador de MDs (snapshot datado)

- Arquivos:
  - `2026-05-08-gerenciador-de-mds-indice-e-guia.md`
- Baseline: `2026-05-08-gerenciador-de-mds-indice-e-guia.md`
- Ultima versao: `2026-05-08-gerenciador-de-mds-indice-e-guia.md`
- Mudancas desde baseline: arquivo de referencia estatica (nao substitui o gerenciador sem data)
- Observacao: contem a redacao original com gatilhos de pedido e mapa; o indice vivo e `gerenciador-de-mds-indice-e-guia.md`.

## Tema: governanca documental (legado de transicao)

- Arquivos:
  - `MD_MESTRE-indice-e-governanca.md`
- Baseline: `MD_MESTRE-indice-e-governanca.md`
- Ultima versao: `MD_MESTRE-indice-e-governanca.md`
- Mudancas desde baseline: nao aplicavel (arquivo fixo sem data)
- Observacao: este arquivo foi o primeiro "mestre fixo" da governanca e permanece como referencia de transicao.

## Tema: visao geral e registro evolutivo

- Arquivos:
  - `2026-05-07-visao-geral-e-registro-evolutivo.md`
- Baseline: `2026-05-07-visao-geral-e-registro-evolutivo.md`
- Ultima versao: `2026-05-07-visao-geral-e-registro-evolutivo.md`
- Mudancas desde baseline: sem deltas ate o momento

## Tema: status tecnico e pendencias

- Arquivos:
  - `2026-05-07-status-tecnico-e-pendencias.md`
- Baseline: `2026-05-07-status-tecnico-e-pendencias.md`
- Ultima versao: `2026-05-07-status-tecnico-e-pendencias.md`
- Mudancas desde baseline: sem deltas ate o momento

## Tema: stack tecnologica e direcionadores de evolucao

- Arquivos:
  - `2026-05-08-stack-tecnologica-e-direcionadores-de-evolucao.md`
- Baseline: `2026-05-08-stack-tecnologica-e-direcionadores-de-evolucao.md`
- Ultima versao: `2026-05-08-stack-tecnologica-e-direcionadores-de-evolucao.md`
- Mudancas desde baseline: sem deltas ate o momento

## Tema: arquitetura e decisoes tecnicas

- Arquivos:
  - `2026-05-08-arquitetura-e-decisoes-tecnicas.md`
- Baseline: `2026-05-08-arquitetura-e-decisoes-tecnicas.md`
- Ultima versao: `2026-05-08-arquitetura-e-decisoes-tecnicas.md`
- Mudancas desde baseline: sem deltas ate o momento

## Tema: riscos e plano de mitigacao

- Arquivos:
  - `2026-05-08-riscos-e-plano-de-mitigacao.md`
- Baseline: `2026-05-08-riscos-e-plano-de-mitigacao.md`
- Ultima versao: `2026-05-08-riscos-e-plano-de-mitigacao.md`
- Mudancas desde baseline: sem deltas ate o momento

## Tema: plano de release e validacao

- Arquivos:
  - `2026-05-08-plano-de-release-e-validacao.md`
- Baseline: `2026-05-08-plano-de-release-e-validacao.md`
- Ultima versao: `2026-05-08-plano-de-release-e-validacao.md`
- Mudancas desde baseline: sem deltas ate o momento

## Tema: roadmap de fases e marcos

- Arquivos:
  - `2026-05-08-roadmap-fases-e-marcos.md`
- Baseline: `2026-05-08-roadmap-fases-e-marcos.md`
- Ultima versao: `2026-05-08-roadmap-fases-e-marcos.md`
- Mudancas desde baseline: sem deltas ate o momento

## Protocolo de atualizacao deste gerenciador (quando voce pedir)

Quando pedir algo como:

- "atualizar o gerenciador de MDs"
- "regenerar o indice dos MDs"
- "sincronizar o dicionario dos MDs"

(isso equivale a **regenerar** o arquivo `gerenciador-de-mds-indice-e-guia.md` com base nos demais MDs.)

Procedimento:

1. Ler todos os arquivos `*.md` em `MDs`, **exceto** `gerenciador-de-mds-indice-e-guia.md` (evita circularidade; opcionalmente ler o snapshot datado apenas como referencia de redacao, nao como fonte de fatos do produto).
2. Identificar arquivos novos, removidos e mudancas de escopo/tema.
3. Agrupar por tema (ignorando a data no inicio do nome, quando houver).
4. Ordenar cronologicamente cada tema.
5. Definir baseline (primeiro) e ultima versao (ultimo) por tema.
6. A partir do segundo arquivo de cada tema, gerar resumo de mudancas (delta).
7. Atualizar a **lista de MDs**, **finalidades** (secao Guia rapido), **relacoes** e **ordem de leitura**.
8. Reavaliar a **Ordem recomendada para entendimento completo** (inserir, promover ou rebaixar itens quando um MD novo mudar prioridade de leitura).
9. Aplicar os **criterios de consistencia documental** (secao abaixo).
10. Sobrescrever **este** arquivo com o estado atualizado.

## Criterios de consistencia documental

Ao atualizar este gerenciador, verificar:

- se ha arquivos sem data no nome e se o motivo esta claro (excecoes intencionais);
- se ha sobreposicao excessiva de conteudo entre MDs;
- se existe pendencia tecnica sem documento correspondente;
- se os nomes continuam claros para consulta futura.

## Meta: timeline evolutiva (produto)

Usar os MDs como base para uma timeline de produto:

- marco tecnico (arquitetura, stack, release);
- marco funcional (novos modulos/fluxos);
- marco operacional (instalacao, distribuicao, validacao);
- marco estrategico (POC web, migracoes, comercializacao modular).

Com isso, a evolucao documentada fica cronologica e auditavel (combinar com baseline + delta por tema).

## Template para novos arquivos de delta

No inicio de cada novo delta, usar:

- Tema:
- Tipo: Delta
- Baseline do tema:
- Versao anterior:
- Data:

### Mudancas desde a versao anterior

- Adicionado:
- Alterado:
- Removido:
- Impacto:
- Proximas acoes:
