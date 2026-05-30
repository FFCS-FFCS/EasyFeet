# EasyFeet - Gerenciador de MDs (Indice e Guia)

Ultima atualizacao: 2026-05-30 UTC-3 (retomada: execucao roteiro Fase 2 marcadores)

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

Excecao de leitura na regeneracao: **nao** usar o proprio conteudo deste arquivo como fonte de verdade sobre o produto; reler os demais MDs e recompor o indice.

### Regeneracao deste arquivo  circularidade ou nao?

- **Sim**, ele carrega instrucoes para **ser gerado de novo** e **substituido** (`sobrescrito`). Isso e util: qualquer um (ou um assistente) sabe qual protocolo seguir sem procurar outro documento.
- **Nao**, isso **nao e um loop problematico**. O fluxo correto na regeneracao e:
  1. Ler **todos** os outros `*.md` na pasta `MDs` **e subpastas** (**exceto** este `gerenciador-de-mds-indice-e-guia.md`).
  2. A partir deles, atualizar catalogo por tema, baseline/deltas, guia rapido, ordem de leitura, etc. (conteudo de produto e governanca vem dos MDs tematicos e do `MD_MESTRE`; snapshots e copias locais entram na **listagem** e no guia, mas **nao** substituem os temas.)
  3. **Gravar por cima** deste arquivo com o texto novo, **mantendo de proposito** de novo estas secoes fixas (objetivo, convencoes, protocolo, template) para a proxima rodada.

A versao anterior do gerenciador **nao** e a fonte da lista de documentos nem dos fatos do produto  so pode ser consultada opcionalmente para copiar redacao estrutural (por exemplo titulos), nunca como substituto de reler cada MD tema a tema.

## Inventario desta regeneracao (arquivos .md)

Encontrados **19** arquivos `*.md` alem do presente gerenciador (varredura recursiva em `MDs`):

| Arquivo |
|----------|
| `cadastro-pacientes-prototipo-e-testes.md` |
| `especificacao-marcacoes-vinculo-paciente.md` |
| `roteiro-testes-marcadores-fase2.md` |
| `caminho-do-projeto.md` |
| `2026-05-07-visao-geral-e-registro-evolutivo.md` |
| `2026-05-07-status-tecnico-e-pendencias.md` |
| `2026-05-08-stack-tecnologica-e-direcionadores-de-evolucao.md` |
| `2026-05-08-arquitetura-e-decisoes-tecnicas.md` |
| `2026-05-08-riscos-e-plano-de-mitigacao.md` |
| `2026-05-08-plano-de-release-e-validacao.md` |
| `2026-05-08-roadmap-fases-e-marcos.md` |
| `2026-05-08-timesheet-horas-trabalhadas.md` |
| `2026-05-09-timesheet-horas-trabalhadas.md` |
| `2026-05-25-timesheet-horas-trabalhadas.md` |
| `2026-05-28-timesheet-horas-trabalhadas.md` |
| `timesheet-indice-e-consolidado.md` |
| `MD_MESTRE-indice-e-governanca.md` |
| `OLD/2026-05-08-gerenciador-de-mds-indice-e-guia.md` |
| `OLD/gerenciador-de-mds-indice-e-guia - Copia.md` |

## Regra operacional  pasta única (obrigatório)

| O quê | Onde |
|-------|------|
| **Workspace / código / `data/`** | `C:\Users\flavi\OneDrive\Documentos\Ideias_Projetos\Cursor_Projetos\EasyFeet` |
| **Proibido** desenvolver, abrir Cursor, build, ZIP, `dist/`, `release/` | `C:\Cursor_Projetos\EasyFeet` |

Qualquer assistente ou script deve tratar a pasta OneDrive como **única** raiz viva. Detalhe: `caminho-do-projeto.md`. O build (`build_windows_installer.ps1`) **falha** se for executado na pasta antiga.

## Nota desta regeneracao (continuidade da sessao)

**Workspace oficial (definitivo):** `C:\Users\flavi\OneDrive\Documentos\Ideias_Projetos\Cursor_Projetos\EasyFeet`  ver `caminho-do-projeto.md`. A pasta `C:\Cursor_Projetos\EasyFeet` está **descontinuada**.

**Pedido que motivou esta regeneracao:** *"atualizar o gerenciador de MDs e depois vamos continuar de onde paramos."*

**Sessao 2026-05-28 (resumo):** refinamento completo da ficha tecnica do Podoscopio (`gui.py` + `podoscopio_pdf.py`): correcoes de UX/formulario, carga de ficha salva, exportacao PDF branco/preenchido, logo/rodape com pagina, quebra de pagina, campo paciente (branco/preenchido) e alinhamento com cadastro do paciente.

**Sessao 2026-05-30 (retomada):** proximo passo ativo = **executar manualmente** `roteiro-testes-marcadores-fase2.md` via `EF.bat` (secoes A–G). Validacao automatica de imports/tabelas reexecutada antes dos testes manuais.

### Pen drive / instalador (quando build for feito de novo)

Só copiar ficheiros gerados **na raiz OneDrive**:

- **Instalar noutro PC:** `release\EasyFeet-Setup-1.0.0.exe`
- **Portátil (sem instalar):** `EasyFeet_Com_Dados.zip` (ou pasta `dist\EasyFeet\`)

Um EXE/ZIP gerado em `C:\Cursor_Projetos\EasyFeet` (ex.: sessão 2026-05-25) **não** conta como entrega oficial  pode ignorar; o próximo build deve correr só na pasta OneDrive.

### O que já está feito (código + operação)

| Área | Entregue |
|------|----------|
| Regras CRUD | `protocolo.itens`, migração JSON, filtro linhas/pontos, testes `tests/test_marker_rules_protocol.py` |
| EFM | Regra, sugestão AD/pontos; **integrado** em `easyfeet_markers/app.py` (barra Ações centralizada, painéis compactos, rodapé recolhível nos painéis) |
| App principal `EF.bat` | Cadastro com altura, peso, IMC (?), lateralidade; modal IMC; tabela pacientes com scroll H/V |
| Dashboard | Total de pacientes; últimos 3 cadastros; `easyfeet/dashboard_ui.py`; `EF_teste_dashboard.bat` |
| Menu / versão | Grupo **Módulos** (Marcadores, Avaliação Postural); **v1.0.0** no rodapé da sidebar (`easyfeet/version.py`) |
| UX cabeçalho | Buscar e Filtro **apenas** no módulo Pacientes |
| Dados | `easyfeet/paths.py`, `cliente_dados_corporais.py`, migração `criado_em`; `EF.bat` com `%~dp0` |
| Release | Build OneDrive (`dist_new` / `release/` em 2026-05-25); teste diário preferir **`EF.bat`**, não instalador |
| Protótipos teste | `EF_teste_cadastro.bat`, `EF_teste_modulo.bat`, `EF_teste_dashboard.bat` |
| Especificação (sem código) | `especificacao-marcacoes-vinculo-paciente.md`  vínculo paciente, momentos clínicos, licença de módulo |
| Marcadores Fase 2 (código) | Selector paciente/momento no EFM; Salvar no paciente; histórico em Pacientes; reabertura contextual CLI |
| Validação Fase 2 (em execucao) | `roteiro-testes-marcadores-fase2.md`  checklist manual A–G; automáticos OK (2026-05-28 e revalidacao 2026-05-30) |
| Podoscopio / PDFs | Ficha tecnica: UX, persistencia, PDF branco/preenchido, logo, paginacao, campo paciente (2026-05-28) |

### Ponto de retomada  próximo trabalho sugerido (produto)

Ordem prática para **continuar de onde paramos** (2026-05-30):

1. **Agora:** executar `roteiro-testes-marcadores-fase2.md` com `EF.bat` (~45–60 min), secao A primeiro (fluxo core), depois B–G.
2. Marcar OK/Falhou no roteiro; reportar falhas ao assistente para correcao imediata.
3. Corrigir bloqueadores antes de avancar para release ou novas features.
3. **Pendência futura registada:** PEND-MARC-001 comparar imagens entre momentos (palmilhas).
4. **Documentar delta** em `2026-05-07-status-tecnico-e-pendencias.md` / arquitetura (opcional).
5. **Release:** só se pedido explicitamente  `build_instalador.bat` na raiz OneDrive; fechar ficheiros em `dist/` antes do build.

### Timesheet

Ultimo consolidado: `timesheet-indice-e-consolidado.md` / `Documentos de Apoio/TimeSheet/timesheet-consolidado.csv`  inclui **`2026-05-28-timesheet-horas-trabalhadas.md`**. Totais gerais: **22,83 h** ativas / **55,78 h** decorridas.

### Inventário documental

Cópias não canónicas em `OLD/`; documento vivo de caminho: `caminho-do-projeto.md`.

## Ordem recomendada para entendimento completo

Ordem base (ajustavel sempre que aparecer MD novo mais prioritario ao contexto atual; ao pedir atualizacao do gerenciador, reavaliar esta sequencia contra o conjunto atual de `.md`).

Fluxo esperado nesta revisao:

- **Por que Visao geral em primeiro lugar:** responde "o que e o projeto e para que serve"; e o primeiro recado para um leitor desconhecido.
- **`MD_MESTRE-indice-e-governanca.md` logo em seguida (segundo lugar):** nao compete com a historia do produto; explica nomenclatura, governanca e transicao dos MDs. Quem quer so contexto pode parar na Visao geral; quem vai manter documentacao le Visao geral + MESTRE cedo para nao ler o restante "no escuro".

1. Visao geral (`2026-05-07-visao-geral-e-registro-evolutivo.md`)
2. Governanca documental (`MD_MESTRE-indice-e-governanca.md`)
3. Caminho do projeto e Cursor (`caminho-do-projeto.md`)  **obrigatorio** apos mudanca de pasta ou retomada de chat
4. Stack tecnologica (`2026-05-08-stack-tecnologica-e-direcionadores-de-evolucao.md`)
5. Arquitetura e decisoes (`2026-05-08-arquitetura-e-decisoes-tecnicas.md`)
6. Status tecnico e pendencias (`2026-05-07-status-tecnico-e-pendencias.md`)
7. Riscos e mitigacao (`2026-05-08-riscos-e-plano-de-mitigacao.md`)
8. Plano de release e validacao (`2026-05-08-plano-de-release-e-validacao.md`)
9. Roadmap de fases e marcos (`2026-05-08-roadmap-fases-e-marcos.md`)
10. Cadastro  protótipo e testes (`cadastro-pacientes-prototipo-e-testes.md`)
11. **Marcacoes vinculadas ao paciente  especificacao** (`especificacao-marcacoes-vinculo-paciente.md`)
12. **Roteiro de testes Fase 2 (marcadores)** (`roteiro-testes-marcadores-fase2.md`)  apos implementacao; validacao manual pendente

Opcional (nao faz parte do fluxo minimo do produto): snapshots e copias (`OLD/`, arquivos com nome "Copia") para auditoria ou comparacao.

## Convencao geral dos arquivos MD

- Padrao de nome: `AAAA-MM-DD-assunto.md` (com excecoes intencionais **sem data**: este gerenciador e `MD_MESTRE-indice-e-governanca.md`).
- Idioma: portugues (com foco tecnico e pratico).
- Estilo: objetivo, com secoes curtas e reutilizaveis.
- Regra: toda mudanca relevante no produto deve refletir em pelo menos um MD tematico.
- Preferir guardar snapshots datados historicos em subpastas (ex.: `OLD/`) para nao misturar com o indice vivo.

## Guia rapido por arquivo (finalidade e perguntas)

### `gerenciador-de-mds-indice-e-guia.md` (este arquivo)

**Finalidade:** indice vivo, catalogo por tema, baseline/deltas, ordem de leitura, protocolo de regeneracao e criterios de consistencia.  
**Quando ler:** para navegar a pasta `MDs` e orientar atualizacoes do acervo.  
**Perguntas que responde:** Quais temas existem? Qual a ordem de leitura? Como pedir regeneracao? O que checar na consistencia?

### `cadastro-pacientes-prototipo-e-testes.md`

**Finalidade:** fluxo **repetível** de teste do cadastro (`teste_cadastro_paciente_extendido.py`, `EF_teste_cadastro.bat`); regra para o assistente perguntar se na próxima mudança basta atualizar o `.bat`. Campos corporais **já integrados** no `gui.py`  protótipo ainda útil para testes isolados.  
**Quando ler:** antes de alterar campos de paciente ou pedir teste rápido.  
**Perguntas que responde:** Como testar cadastro? O processo pode repetir? O assistente deve gerar só o `.bat`?

### `especificacao-marcacoes-vinculo-paciente.md`

**Finalidade:** especificação (rascunho aprovado para discussão) de vínculo imagens/marcações ao paciente no EasyFeet único; módulo por licença; momentos clínicos; Salvar sem autosave; pendências PEND-MARC-001+.  
**Quando ler:** antes de implementar persistência de marcações ou UI Salvar no paciente.  
**Perguntas que responde:** Onde gravar ficheiros? Qual modelo de dados? O EFM fica independente? Como evoluir para comparar datas?

### `roteiro-testes-marcadores-fase2.md`

**Finalidade:** checklist manual (tabelas OK/Falhou) para validar Fase 2 dos marcadores; inclui o que ja foi testado automaticamente e quando executar.  
**Quando ler:** quando for testar no desktop; pedir ao assistente *«Quero executar o roteiro de testes da Fase 2 dos marcadores»*.  
**Perguntas que responde:** O que conferir passo a passo? O que ja passou em smoke/DB? Onde ficam os ficheiros gravados?

### `caminho-do-projeto.md`

**Finalidade:** pasta canónica do repositório, migração desde `C:\Cursor_Projetos\EasyFeet`, chats Cursor, build/release, sharing violation.  
**Quando ler:** ao abrir o workspace na pasta nova ou retomar conversa com o agente.  
**Perguntas que responde:** Onde trabalhar? Como migrar dados/chats? Como reabrir o histórico no Cursor?

### `MD_MESTRE-indice-e-governanca.md`

**Finalidade:** governanca documental, baseline/delta e visao consolidada do acervo (documento vivo sem data no nome).  
**Quando ler:** em segundo na ordem recomendada, ou ao definir/comparar regras de documentacao com o gerenciador.  
**Perguntas que responde:** Qual o modelo baseline/delta? Qual o papel do mestre frente aos MDs datados?

### `OLD/2026-05-08-gerenciador-de-mds-indice-e-guia.md` (snapshot arquivado)

**Finalidade:** preservar a **primeira versao publicada** do texto do gerenciador com nome datado (inclui gatilhos de pedido, mapa original e criterios).  
**Quando ler:** auditoria ou comparacao historica.  
**Perguntas que responde:** O que foi proposto na primeira versao do gerenciador com `AAAA-MM-DD` no nome?

### `OLD/gerenciador-de-mds-indice-e-guia - Copia.md`

**Finalidade:** copia local/manual do gerenciador; **nao canonica** (arquivada em `OLD/`).  
**Quando ler:** apenas se precisar de um ramo paralelo antes de fusao ou para recuperacao acidental.  
**Perguntas que responde:** Nenhuma como fonte de produto; evitar edicoes permanentes aqui em vez do arquivo sem "Copia" no nome.  
**Recomendacao:** eliminar quando deixar de ser necessaria, para evitar drift.

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

### `2026-05-08-timesheet-horas-trabalhadas.md`

**Finalidade:** registro diario de horas trabalhadas (modelo em 4 secoes: sessao, tabela, totais, observacoes).  
**Quando ler:** no fechamento do dia/sessao para registrar janela total e tempo ativo estimado.  
**Perguntas que responde:** Quanto tempo foi dedicado no periodo? Qual o recorte diario para graficos?

### `2026-05-09-timesheet-horas-trabalhadas.md`

**Finalidade:** folha diaria **2026-05-09** (mesmo modelo que a de 2026-05-08); encerramento com atualizacao do consolidado.  
**Quando ler:** ao fechar o dia 09 ou ao reconciliar horas dessa data.  
**Perguntas que responde:** Qual o bloco tabular do dia 09? (Estimativa sujeita a ajuste manual.)

### `2026-05-25-timesheet-horas-trabalhadas.md`

**Finalidade:** folha diaria **2026-05-25**  integracao app principal, dashboard, menu Modulos, especificacao marcacoes.  
**Quando ler:** reconciliar horas do dia 25.  
**Perguntas que responde:** Qual o bloco tabular do dia 25?

### `2026-05-28-timesheet-horas-trabalhadas.md`

**Finalidade:** folha diaria **2026-05-28**  ajustes de UX da ficha do Podoscopio, persistencia/carga de ficha salva e refinamento dos PDFs (quebra, pagina, campo paciente).  
**Quando ler:** reconciliar horas do dia 28 e retomar contexto tecnico exato da ultima sessao.  
**Perguntas que responde:** O que foi finalizado no fechamento do dia 28 e quanto tempo foi dedicado?

### `timesheet-indice-e-consolidado.md`

**Finalidade:** consolidar todos os timesheets diarios em uma visao unica por dia/semana/mes e total geral.  
**Quando ler:** ao atualizar o projeto, revisar dedicacao de tempo e preparar dados de acompanhamento.  
**Perguntas que responde:** Qual o total acumulado? Como esta a distribuicao por dia/semana/mes?

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

## Tema: caminho do projeto e migracao de workspace

- Arquivos:
  - `caminho-do-projeto.md`
- Baseline: `caminho-do-projeto.md`
- Ultima versao: `caminho-do-projeto.md`
- Mudancas desde baseline: documento evoluido com scripts `migrar_pasta_antiga.ps1`, `relink_chat_easyfeet.py` (mencionados no MD)
- Observacao: codigo em `easyfeet/paths.py`; repositorio ativo apenas em OneDrive.

## Tema: cadastro de pacientes

- Arquivos:
  - `cadastro-pacientes-prototipo-e-testes.md` (processo de teste)
  - `2026-05-07-status-tecnico-e-pendencias.md` (parcial)
- Baseline documental tematico: **pendente** (MD datado dedicado)
- Ultima versao codigo: `easyfeet/gui.py` + `easyfeet/cliente_dados_corporais.py` (2026-05-25)
- **Alterado (delta operacional):** altura, peso, IMC com modal e scroll, lateralidade, tabela com colunas corporais e scroll H/V; dados em `clientes` + migracao `criado_em`.
- Observacao: protótipos `EF_teste_cadastro.bat` mantidos para teste isolado.

## Tema: dashboard

- Arquivos: `easyfeet/dashboard_ui.py`; teste `EF_teste_dashboard.bat` / `teste_dashboard.py`
- Baseline documental: **pendente**
- **Adicionado (2026-05-25):** card Total de pacientes; removido card contagem recentes; lista fixa dos 3 últimos cadastros por `criado_em`.

## Tema: marcacoes vinculadas ao paciente (especificacao)

- Arquivos: `especificacao-marcacoes-vinculo-paciente.md`; referencia em `2026-05-08-roadmap-fases-e-marcos.md` (Fase 2)
- Baseline: `especificacao-marcacoes-vinculo-paciente.md` v1.0 (2026-05-26 no doc / sessao 25-26)
- Estado codigo: **nao implementado**  apenas especificacao e alinhamento de produto (EasyFeet unico, licenca de modulo, selector paciente no EFM, momentos, Salvar manual).
- Pendencias: PEND-MARC-001 (comparar evolucao entre momentos), etc.  ver especificacao §10.

## Tema: cadastro de pacientes  idade minima e modal de orientacao (legado deste bloco)

- Estado: **implementado** em `gui.py` / `services.py`.
- Observacao: fundido no tema cadastro acima; manter idade minima 3 anos e modal Nascimento.

## Tema: marcadores e regras (EFM)

- Estado: **implementado** (regras CRUD + EFM UI integrada 2026-05-25).
- Referencias: `easyfeet_markers/app.py`, `marcador_plantar/`, `marcador_pontos/`, `marker_rules_store.py`, `menu-config-v1.json` (grupo `modulos`).
- **Alterado:** barra Ações centralizada; `show_action_toolbar=False` nos painéis; fontes compactas; persistencia por paciente **pendente** (ver especificacao).
- MD tematico de regras: ainda **pendente**; especificacao de vinculo paciente em arquivo proprio.

## Tema: gerenciador de MDs  copia local (nao canonica)

- Arquivos:
  - `OLD/gerenciador-de-mds-indice-e-guia - Copia.md`
- Baseline: `OLD/gerenciador-de-mds-indice-e-guia - Copia.md`
- Ultima versao: `OLD/gerenciador-de-mds-indice-e-guia - Copia.md`
- Mudancas desde baseline: nao aplicavel (arquivo auxiliar; risco de divergencia em relacao ao gerenciador vivo)
- Observacao: nao usar como fonte de indice; preferir apagar ou fundir alteracoes no `gerenciador-de-mds-indice-e-guia.md`. Localizacao atual: subpasta `OLD/` (antes havia copia homonima na raiz de `MDs`).

## Tema: gerenciador de MDs (snapshot datado, arquivado)

- Arquivos:
  - `OLD/2026-05-08-gerenciador-de-mds-indice-e-guia.md`
- Baseline: `OLD/2026-05-08-gerenciador-de-mds-indice-e-guia.md`
- Ultima versao: `OLD/2026-05-08-gerenciador-de-mds-indice-e-guia.md`
- Mudancas desde baseline: arquivo de referencia estatica (localizacao atual: subpasta `OLD/`)
- Observacao: indice vivo e `gerenciador-de-mds-indice-e-guia.md`.

## Tema: governanca documental (MD Mestre)

- Arquivos:
  - `MD_MESTRE-indice-e-governanca.md`
- Baseline: `MD_MESTRE-indice-e-governanca.md`
- Ultima versao: `MD_MESTRE-indice-e-governanca.md`
- Mudancas desde baseline: sem deltas ate o momento
- Observacao: documento vivo sem data no nome; complementa este gerenciador.

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
- Ultima versao: `2026-05-08-roadmap-fases-e-marcos.md` (+ nota Fase 2  `especificacao-marcacoes-vinculo-paciente.md`)
- Mudancas desde baseline: link para especificacao de marcacoes (2026-05-25/26)

## Tema: timesheet diario de horas trabalhadas

- Arquivos:
  - `2026-05-08-timesheet-horas-trabalhadas.md`
  - `2026-05-09-timesheet-horas-trabalhadas.md`
  - `2026-05-25-timesheet-horas-trabalhadas.md`
  - `2026-05-28-timesheet-horas-trabalhadas.md`
- Baseline: `2026-05-08-timesheet-horas-trabalhadas.md`
- Ultima versao: `2026-05-28-timesheet-horas-trabalhadas.md`
- Mudancas desde baseline: folhas 09, 25 e 28; consolidado atualizado 2026-05-28.
- Observacao: atualizacao incremental no mesmo dia pode sobrescrever a folha desse dia; ao virar data, novo `AAAA-MM-DD-timesheet-horas-trabalhadas.md`.

## Tema: timesheet consolidado (indice e totais)

- Arquivos:
  - `timesheet-indice-e-consolidado.md`
- Baseline: `timesheet-indice-e-consolidado.md`
- Ultima versao: `timesheet-indice-e-consolidado.md`
- Mudancas desde baseline: nao aplicavel (arquivo consolidado vivo, sobrescrito a cada atualizacao)
- Observacao: deve manter sincronia com `Documentos de Apoio/TimeSheet/timesheet-consolidado.csv`.

## Protocolo de atualizacao deste gerenciador (quando voce pedir)

Quando pedir algo como:

- "atualizar o gerenciador de MDs"
- "regenerar o indice dos MDs"
- "sincronizar o dicionario dos MDs"
- "atualizar o gerenciador de MDs e continuar de onde paramos"
- "atualizar o gerenciador de MDs e depois vamos continuar de onde paramos" (equivalente ao item anterior para retomada)

(isso equivale a **regenerar** o arquivo `gerenciador-de-mds-indice-e-guia.md` com base nos demais MDs.)

**Clareza para encerrar o dia ou pausar com tudo alinhado**

- Pedir **só** "atualizar o gerenciador de MDs" **nao** deixa implicito que o assistente deve **recalcular horas**; em muitas sessoes isso foi tratado como **indice/guia apenas** (passos 110).
- Para **sempre** incluir horas no mesmo pedido, use uma formula **explicita**, por exemplo:
  - **"Encerrar o dia: atualizar timesheet e o gerenciador de MDs"** (recomendado)
  - **"Atualizar timesheet e regenerar o gerenciador"**
  - **"Parar agora: sincronizar horas trabalhadas e atualizar o gerenciador"**
- Se quiser **apenas** horas, sem mexer no gerenciador: **"atualizar timesheet"** ou **"sincronizar horas trabalhadas"**.
- Se quiser **apenas** o indice, sem recalcular horas: **"atualizar o gerenciador de MDs so o indice"** ou **"regenerar o gerenciador sem timesheet"**.

Procedimento:

1. Enumerar e ler todos os arquivos `*.md` em `MDs` **e subpastas**, **exceto** `gerenciador-de-mds-indice-e-guia.md` (evita circularidade). Opcional: consultar o snapshot em `OLD/` ou copias **apenas** para texto fixo, nunca como substituto dos MDs tematicos para fatos de produto.
2. Identificar arquivos novos, removidos e mudancas de escopo/tema.
3. Agrupar por tema (ignorando a data no inicio do nome, quando houver).
4. Ordenar cronologicamente cada tema.
5. Definir baseline (primeiro) e ultima versao (ultimo) por tema.
6. A partir do segundo arquivo de cada tema, gerar resumo de mudancas (delta).
7. Atualizar a **lista de MDs**, **finalidades** (secao Guia rapido), **relacoes** e **ordem de leitura**.
8. Reavaliar a **Ordem recomendada para entendimento completo** (inserir, promover ou rebaixar itens quando um MD novo mudar prioridade de leitura).
9. Aplicar os **criterios de consistencia documental** (secao abaixo).
10. Sobrescrever **este** arquivo com o estado atualizado.
11. **Timesheet (consolidado + CSV):** se existirem `*-timesheet-horas-trabalhadas.md` **e** o pedido for de **timesheet/horas** ou de **encerramento combinado** (ver lista acima), atualizar `timesheet-indice-e-consolidado.md` e `Documentos de Apoio/TimeSheet/timesheet-consolidado.csv` com totais diarios, semanais, mensais e total acumulado (CSV Brasil: separador `;` e decimal `,`). Se o pedido for **apenas** regeneracao do indice do gerenciador (sem mencionar horas/timesheet/encerrar o dia), **nao** alterar timesheet/CSV salvo o usuario pedir o contrario na mesma mensagem.

## Criterios de consistencia documental

Ao atualizar este gerenciador, verificar:

- se ha arquivos sem data no nome e se o motivo esta claro (excecoes intencionais);
- se ha sobreposicao excessiva de conteudo entre MDs;
- se existe pendencia tecnica sem documento correspondente (marcadores/regras, EFM, `paths.py`, filtro CRUD, sugestao de pontos vs textos do protocolo, cadastro idade+modal  ver nota de retomada);
- se o workspace aberto no Cursor e a pasta OneDrive canónica (nao `C:\Cursor_Projetos\EasyFeet`);
- se nenhum build/ZIP/instalador foi gerado ou documentado como entrega na pasta antiga;
- se `caminho-do-projeto.md` descreve corretamente os caminhos de `release/`, ZIP e pen drive na raiz OneDrive;
- em mudanças de **cadastro**, se foi seguida `cadastro-pacientes-prototipo-e-testes.md` (perguntar ao utilizador se deseja só `EF_teste_cadastro.bat` para teste);
- se os nomes continuam claros para consulta futura;
- se existem copias (`Copia`) ou snapshots em `OLD/` que devam ser arquivadas, renomeadas ou removidas para reduzir ambiguidade.

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



