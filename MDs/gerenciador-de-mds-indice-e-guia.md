# EasyFeet - Gerenciador de MDs (Indice e Guia)

Ultima atualizacao: 2026-06-12 UTC-3 (encerramento do dia: timesheet + gerenciador; NAV-4 + instalador DEMO)

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

Encontrados **25** arquivos `*.md` alem do presente gerenciador (varredura recursiva em `MDs`):

| Arquivo |
|----------|
| `cadastro-pacientes-prototipo-e-testes.md` |
| `especificacao-marcacoes-vinculo-paciente.md` |
| `roteiro-testes-marcadores-fase2.md` |
| `rascunho-menu-hub-paciente-v2.md` |
| `versionamento-local-easyfeet.md` |
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
| `2026-05-30-timesheet-horas-trabalhadas.md` |
| `2026-06-01-timesheet-horas-trabalhadas.md` |
| `2026-06-12-timesheet-horas-trabalhadas.md` |
| `lista-de-proximos-passos.md` |
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

**Pedido que motivou esta regeneracao:** *"Encerrar o dia: atualizar timesheet e o gerenciador de MDs. Depois vamos continuar de onde paramos."*

**Commit de referencia (codigo M2–M4):** `e28c34d` — `feat(v2): Hub M2-M4, EFM B+ e encerramento 2026-05-30` (branch `master`). Codigo Navicular (NAV-0/NAV-1) **apos** este commit — ainda sem tag dedicada.

**Estado do repositorio:** M2–M4 no commit acima; Navicular implementado localmente (NAV-1); ficheiros locais nao versionados (ex.: `Imagens/Pacientes/`, `Documentos de Apoio/`, PDFs de teste) — nao entram no Git.

**Sessao 2026-05-28 (resumo):** refinamento completo da ficha tecnica do Podoscopio (`gui.py` + `podoscopio_pdf.py`): correcoes de UX/formulario, carga de ficha salva, exportacao PDF branco/preenchido, logo/rodape com pagina, quebra de pagina, campo paciente (branco/preenchido) e alinhamento com cadastro do paciente.

**Sessao 2026-05-30 (continuacao):** roteiro Fase 2 marcadores **concluido** (A–G); **M1** menu v2 implementado (`menu-config-v2.json`, app **v2.0.0**); rascunho CRM/Hub validado (`rascunho-menu-hub-paciente-v2.md`); versionamento local Git + snapshots (`versionamento-local-easyfeet.md`, tag `v1.0.0`); criterio timesheet **20 min** para novos apontamentos (legado 30 min preservado).

**Sessao 2026-05-30 (tarde/noite):** **M2** Hub v0 (ficha clinica, Resumo + Linha do tempo); **M3** timeline agrupada por dia, edicao de momentos, historico migrou do modulo Pacientes; **M4** EFM B+ (contexto Hub, lado D/E, seletor/exclusao de imagens, Plantigrafo Hub-first); UX Pacientes («Novo paciente», colunas tabela) e EFM (2 linhas header, faixa Acoes, zoom 50 em 50, alinhamento); `scripts/test_hub_smoke.py`.

**Sessao 2026-06-01 (Teste Navicular):** **NAV-0** menu + hub; **NAV-1** ficha funcional + BD + Modo A (Brody, **10 mm**); PDF limiares regenerado; UX ficha (mm multiplos digitos, layout); sanfonas fechadas no arranque; excluir ficha (Navicular + Podoscopio); combo «Ficha salva» corrigido; textos laudo registados (**PEND-NAV-LAUDO-001**); testes `test_navicular_ficha_salvar.py`, `test_ficha_salva_combo_smoke.py`. Docs em `Documentos de Apoio/EF - Navicular *.md` (fora de `MDs/`).

**Sessao 2026-06-12 (manha):** **NAV-2** PDF Navicular (`navicular_pdf.py`, botoes, `test_navicular_pdf.py`); refinamento PDFs Navicular + Podoscopio (sem tracos/canetas em branco, destaque Alterado, fotos so preenchida); `pdf_brand.col_widths_rotulo_valor` (largura minima rotulos nos 4 PDFs).

**Sessao 2026-06-12 (tarde):** **NAV-4** + **PEND-NAV-LAUDO-001** — ecrã `navicular_laudos`, BD `laudos_navicular`, `navicular_laudo.py`, `navicular_laudo_pdf.py`, smoke `test_navicular_laudo.py`. **Instalador DEMO** com `data/` atual: `release/EasyFeet-Setup-DEMO-2.0.0.exe`, `EasyFeet_DEMO_Com_Dados.zip` (`build_instalador_demo.bat`).

**Proximo passo ativo:** ver **`lista-de-proximos-passos.md`** — **NAV-3** (fotos/Hub); M5 Hub **pausado**.

### Retomada imediata (Navicular — o que implementar)

| Item | Detalhe | Ficheiros provaveis |
|------|---------|---------------------|
| **NAV-3** | Fotos sentado/em pe + Hub/timeline | `gui.py`, `data/pacientes/{id}/navicular/` |
| Teste | Smoke laudos + PDF ficha | `scripts/test_navicular_laudo.py`, `test_navicular_pdf.py` |

**Spec:** `Documentos de Apoio/EF - Navicular plano de implantacao.md`; checklist em **`lista-de-proximos-passos.md`**.

### Retomada pausada (M5 Hub)

| Item | Detalhe | Ficheiros provaveis |
|------|---------|---------------------|
| Botao **Momentos** | Modal lista filtravel na ficha clinica | `easyfeet/gui.py` |
| Busca / filtros | Texto, datas, «com Plantigrafo / sem exames» | `gui.py`, eventualmente `services.py` |
| Atalho Podoscopio | Substituir stub `_hub_atalho_modulo` | `gui.py` |

**Spec:** `rascunho-menu-hub-paciente-v2.md` §6.2; **`lista-de-proximos-passos.md`** (M5-1…M5-5).

### Pen drive / instalador (entrega DEMO — 2026-06-12)

Só copiar ficheiros gerados **na raiz OneDrive**:

- **Instalar noutro PC (com dados atuais):** `release\EasyFeet-Setup-DEMO-2.0.0.exe` — nome **EasyFeet (DEMO)** no assistente; inclui `data\` (BD, pacientes, regras).
- **Portátil (sem instalar):** `EasyFeet_DEMO_Com_Dados.zip` (ou pasta `dist\EasyFeet\`)
- **Regenerar:** `build_instalador_demo.bat` (feche EasyFeet antes)

Build legado `EasyFeet-Setup-1.0.0.exe` / `EasyFeet_Com_Dados.zip` — substituido pelo DEMO v2.0.0 para demonstracao. EXE/ZIP em `C:\Cursor_Projetos\EasyFeet` **nao** conta como entrega oficial.

### O que já está feito (código + operação)

| Área | Entregue |
|------|----------|
| Regras CRUD | `protocolo.itens`, migração JSON, filtro linhas/pontos, testes `tests/test_marker_rules_protocol.py` |
| EFM | Regra, sugestao AD/pontos; **integrado** em `easyfeet_markers/app.py` (header 2 linhas, faixa Acoes alinhada, combo Imagem/Lado, excluir imagem, zoom 100–400%) |
| App principal `EF.bat` | Cadastro com altura, peso, IMC (?), lateralidade; modal IMC; tabela pacientes com scroll H/V |
| Dashboard | Total de pacientes; últimos 3 cadastros; `easyfeet/dashboard_ui.py`; `EF_teste_dashboard.bat` |
| Menu / versão | **Menu v2** (`menu-config-v2.json`): Plantigrafo, Podoscopio, Laudos, Palmilhas…; **v2.0.0** no rodapé (`easyfeet/version.py`); v1.0.0 congelada (tag Git + snapshot) |
| Versionamento | Git local, `MarcarVersao.bat`, `CriarSnapshot.bat`, guia `versionamento-local-easyfeet.md` |
| UX cabeçalho | Buscar e Filtro **apenas** no módulo Pacientes |
| Dados | `easyfeet/paths.py`, `cliente_dados_corporais.py`, migração `criado_em`; `EF.bat` com `%~dp0` |
| Release | Build OneDrive (`dist_new` / `release/` em 2026-05-25); teste diário preferir **`EF.bat`**, não instalador |
| Protótipos teste | `EF_teste_cadastro.bat`, `EF_teste_modulo.bat`, `EF_teste_dashboard.bat` |
| Especificação | `especificacao-marcacoes-vinculo-paciente.md` — vínculo paciente, momentos clínicos, licença de módulo |
| Marcadores Fase 2 (codigo) | Selector paciente/momento no EFM; Salvar no paciente; **historico na ficha (Hub → Linha do tempo)**; reabertura contextual CLI |
| Hub paciente (M2–M3) | Ficha clinica (`paciente_hub`): Resumo, Linha do tempo agrupada por dia, edicao momento, bloco Plantigrafo por imagem; botao «Abrir ficha clinica»; historico marcacoes **saiu** de Pacientes |
| EFM M4 (B+) | Contexto Hub (`cliente_id` + `momento_id`); Plantigrafo → Analise Hub-first; lado D/E/Ambos; combo Imagem + Excluir imagem; header 2 linhas; faixa Acoes; zoom 100–400% |
| UX Pacientes | Botao «Novo paciente»; colunas Lateralidade/Email alargadas |
| Testes Hub | `scripts/test_hub_smoke.py` |
| UX v2 (doc) | `rascunho-menu-hub-paciente-v2.md` — CRM, Hub, B+; **M1–M4 codigo OK**, **M5 pausado** |
| Validação Fase 2 | `roteiro-testes-marcadores-fase2.md` — **concluido** manualmente (A–G, 2026-05-30) |
| Podoscopio / PDFs | Ficha tecnica + PDF branco/preenchido; layout rotulo/valor dinamico (`col_widths_rotulo_valor`); campos em branco sem tracos (2026-06-12) |
| **Teste Navicular (NAV-0…NAV-4)** | Ficha + BD + Modo A (≤ **10 mm**); PDF ficha (`navicular_pdf.py`); **Laudos** (`navicular_laudos`, `laudos_navicular`, `navicular_laudo_pdf.py`); testes smoke |

### Ponto de retomada  próximo trabalho sugerido (produto)

Lista viva: **`lista-de-proximos-passos.md`**.

Ordem pratica para **continuar de onde paramos** (pos NAV-1):

1. **Agora (prioridade utilizador):** **NAV-3** — fotos sentado/em pe + Hub/timeline.
2. **Feito (NAV-4):** ecrã Laudos + textos §4 + PDF laudo por paciente.
3. **Pausado (M5):** botao «Momentos» + modal busca/filtros na ficha clinica.
4. Atalho **Podoscopio** na ficha — abrir ficha tecnica com `cliente_id`.
5. **Pendencia futura:** PEND-MARC-001 comparar imagens entre momentos (palmilhas).
6. **Opcional:** tag ou snapshot se quiser congelar marco Navicular pos-NAV-2.
7. **Release:** so se pedido — `build_instalador.bat` na raiz OneDrive.

### Timesheet

Ultimo consolidado: `timesheet-indice-e-consolidado.md` / `Documentos de Apoio/TimeSheet/timesheet-consolidado.csv` — inclui **`2026-06-12-timesheet-horas-trabalhadas.md`** (2 sessoes no dia). Totais gerais: **43,33 h** ativas / **88,11 h** decorridas.

**Regra activa (novas folhas a partir de 2026-05-30):** pausas **> 20 min** não contam. Folhas até 2026-05-28 mantêm critério **30 min** (legado; não recalcular). Novas folhas diárias: `criterio_pausa_min = 20`.

### Inventário documental

Cópias não canónicas em `OLD/`; documento vivo de caminho: `caminho-do-projeto.md`.

**Fora de `MDs/` (referencia operacional):** pasta `Documentos de Apoio/` — specs Navicular (`EF - Navicular mm x percentual.md`, plano NAV-0…NAV-5, laudo textos modelo), PDF limiares, TimeSheet CSV; **nao** entra na varredura recursiva de `MDs/` mas deve constar neste gerenciador quando relevante ao produto.

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
12. **Roteiro de testes Fase 2 (marcadores)** (`roteiro-testes-marcadores-fase2.md`) — concluido 2026-05-30
13. **Menu v2 / Hub paciente (rascunho CRM)** (`rascunho-menu-hub-paciente-v2.md`) — M1–M4 implementados; M5 em seguida
14. **Versionamento local** (`versionamento-local-easyfeet.md`) — tags, snapshots, scripts `.bat`

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
**Quando ler:** auditoria ou regressao; Fase 2 **concluida** em 2026-05-30.  
**Perguntas que responde:** O que conferir passo a passo? O que ja passou em smoke/DB? Onde ficam os ficheiros gravados?

### `lista-de-proximos-passos.md`

**Finalidade:** lista viva de trabalho pendente (prioridades, M5, PEND-NAV, backlog MARC).  
**Quando ler:** ao retomar desenvolvimento ou mudar prioridade entre demandas.  
**Perguntas que responde:** O que fazer a seguir? O que esta pausado? Qual o ID da pendencia?

### `rascunho-menu-hub-paciente-v2.md`

**Finalidade:** spec validada do menu v2, Hub paciente-centrado, laudos consolidados, palmilhas transversal, roteiro M1–M5.  
**Quando ler:** antes de implementar M5 (modal Momentos) ou evolucoes do Hub.  
**Perguntas que responde:** Como fica a navegacao v2? O que entra no Hub? Qual ordem de implementacao?

### `versionamento-local-easyfeet.md`

**Finalidade:** Git local, tags, snapshots ZIP, scripts `MarcarVersao.bat` / `CriarSnapshot.bat` / `ListarVersoes.bat`.  
**Quando ler:** ao marcar versao, criar snapshot ou retomar baseline congelada (ex.: v1.0.0).  
**Perguntas que responde:** Como versionar sem release? Onde ficam os snapshots?

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

### `2026-05-30-timesheet-horas-trabalhadas.md`

**Finalidade:** folha diaria **2026-05-30** — M2 Hub, M3 timeline, M4 EFM B+, UX Pacientes/EFM.  
**Quando ler:** reconciliar horas do dia 30.  
**Perguntas que responde:** Quanto tempo na sessao Hub/EFM?

### `2026-06-01-timesheet-horas-trabalhadas.md`

**Finalidade:** folha diaria **2026-06-01** — Teste Navicular NAV-0/NAV-1, PDF limiares 10 mm, UX ficha, combo/excluir ficha, laudo MD pendente.  
**Quando ler:** reconciliar horas do dia 01/06 e retomar contexto Navicular.  
**Perguntas que responde:** O que foi entregue na sessao Navicular e quanto tempo foi dedicado?

### `2026-06-12-timesheet-horas-trabalhadas.md`

**Finalidade:** folha diaria **2026-06-12** (2 sessoes) — manha: NAV-2 + refino PDFs; tarde: NAV-4 laudos + instalador DEMO.  
**Quando ler:** reconciliar horas do dia 12/06.  
**Perguntas que responde:** O que foi entregue nas sessoes NAV-2/NAV-4/DEMO e quanto tempo foi dedicado?

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

## Tema: marcacoes vinculadas ao paciente (especificacao + Fase 2)

- Arquivos: `especificacao-marcacoes-vinculo-paciente.md`; `roteiro-testes-marcadores-fase2.md`
- Baseline: `especificacao-marcacoes-vinculo-paciente.md` v1.0 (2026-05-26)
- Estado codigo: **implementado (Fase 2)** — selector paciente/momento, Salvar, historico, reabertura CLI; roteiro manual **concluido** 2026-05-30.
- Pendencias: PEND-MARC-001 (comparar evolucao entre momentos), etc.  ver especificacao §10.

## Tema: menu v2 e Hub paciente (CRM)

- Arquivos: `rascunho-menu-hub-paciente-v2.md`; codigo `menu-config-v2.json`, `easyfeet/gui.py`, `easyfeet/navigation.py`
- Baseline doc: `rascunho-menu-hub-paciente-v2.md`
- Estado: **M1–M4 concluidos** (commit `e28c34d`); **M5 pausado** (modal Momentos + filtros; atalho Podoscopio).
- Observacao: timeline agrupada por dia permanece; M5 adiciona busca quando ha muitos momentos. EFM B+ e Plantigrafo Hub-first estaveis.

## Tema: Teste do Navicular (NAV-0…NAV-5)

- Arquivos MDs: `lista-de-proximos-passos.md` (checklist vivo); `especificacao-marcacoes-vinculo-paciente.md` (PEND-NAV-001)
- Docs de apoio (fora de `MDs/`): `Documentos de Apoio/EF - Navicular mm x percentual.md` + PDF limiares; `EF - Navicular plano de implantacao.md`; `EF - Navicular laudo - textos modelo.md`
- Codigo: `easyfeet/navicular.py`, `easyfeet/gui.py`, `easyfeet/models.py`, `repositories.py`, `services.py`, `db.py`, `menu-config-v2.json`
- Baseline doc: plano de implantacao (NAV-0…NAV-5)
- Estado: **NAV-0 + NAV-1 + NAV-2 concluidos** (ate 2026-06-12) — Modo A ≤ 10 mm (Brody); ficha + BD + combo/excluir; PDF branco/preenchida (`navicular_pdf.py`).
- **Pendente:** NAV-3 fotos/Hub; NAV-5 Modos B/C.
- **Concluido:** NAV-4 laudos + **PEND-NAV-LAUDO-001** (2026-05-30).
- Testes: `scripts/test_navicular_ficha_salvar.py`, `scripts/test_ficha_salva_combo_smoke.py`, `scripts/test_navicular_pdf.py`

## Tema: versionamento local

- Arquivos: `versionamento-local-easyfeet.md`; scripts `MarcarVersao.bat`, `CriarSnapshot.bat`, `ListarVersoes.bat`
- Baseline: `versionamento-local-easyfeet.md`
- Estado: Git local activo; tag `v1.0.0`; snapshot em `snapshots/`.

## Tema: cadastro de pacientes  idade minima e modal de orientacao (legado deste bloco)

- Estado: **implementado** em `gui.py` / `services.py`.
- Observacao: fundido no tema cadastro acima; manter idade minima 3 anos e modal Nascimento.

## Tema: marcadores e regras (EFM)

- Estado: **implementado** (regras CRUD + EFM UI integrada; Fase 2 vinculo paciente 2026-05-25/30).
- Referencias: `easyfeet_markers/app.py`, `marcador_plantar/`, `marcador_pontos/`, `marker_rules_store.py`, `menu-config-v2.json` (Plantigrafo → Analise / Config).
- **Alterado (2026-05-30):** menu v2; persistencia por paciente **implementada** (Fase 2); **M4** EFM B+ (contexto Hub, lado D/E, seletor/exclusao imagem, UX header 2 linhas + faixa Acoes).
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
  - `2026-05-30-timesheet-horas-trabalhadas.md`
  - `2026-06-01-timesheet-horas-trabalhadas.md`
  - `2026-06-12-timesheet-horas-trabalhadas.md`
- Baseline: `2026-05-08-timesheet-horas-trabalhadas.md`
- Ultima versao: `2026-06-12-timesheet-horas-trabalhadas.md`
- Mudancas desde baseline: folhas 09, 25, 28, 30, 01/06 e 12/06 (2 sessoes); consolidado atualizado 2026-06-12; totais **43,33 h** ativas / **88,11 h** decorridas; **criterio de pausa 20 min** para novas folhas a partir de 2026-05-30 (legado 30 min preservado).
- Observacao: atualizacao incremental no mesmo dia pode sobrescrever a folha desse dia; ao virar data, novo `AAAA-MM-DD-timesheet-horas-trabalhadas.md` com `criterio_pausa_min = 20`.

## Tema: timesheet consolidado (indice e totais)

- Arquivos:
  - `timesheet-indice-e-consolidado.md`
- Baseline: `timesheet-indice-e-consolidado.md`
- Ultima versao: `timesheet-indice-e-consolidado.md`
- Mudancas desde baseline: regra de pausa **20 min** activa desde 2026-05-30; legado 30 min nas linhas ate 2026-05-28.
- Observacao: deve manter sincronia com `Documentos de Apoio/TimeSheet/timesheet-consolidado.csv`. Novas folhas: `criterio_pausa_min = 20`.

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
11. **Timesheet (consolidado + CSV):** se existirem `*-timesheet-horas-trabalhadas.md` **e** o pedido for de **timesheet/horas** ou de **encerramento combinado** (ver lista acima), atualizar `timesheet-indice-e-consolidado.md` e `Documentos de Apoio/TimeSheet/timesheet-consolidado.csv` com totais diarios, semanais, mensais e total acumulado (CSV Brasil: separador `;` e decimal `,`). **Novas folhas (desde 2026-05-30):** `criterio_pausa_min = 20` (pausas > 20 min nao contam); folhas ate 2026-05-28 mantem 30 min — **nao recalcular** legado salvo pedido explicito. Se o pedido for **apenas** regeneracao do indice do gerenciador (sem mencionar horas/timesheet/encerrar o dia), **nao** alterar timesheet/CSV salvo o usuario pedir o contrario na mesma mensagem.

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



