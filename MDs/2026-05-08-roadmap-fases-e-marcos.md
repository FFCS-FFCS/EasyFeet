# EasyFeet - Roadmap de Fases e Marcos

Data do registro: 2026-05-08

## 1) Objetivo

Definir uma visao evolutiva por fases para orientar prioridades, comunicar expectativa e manter foco no valor entregue.

## 2) Linha do tempo base (marco inicial)

- **2026-05-07 / 2026-05-08**: consolidacao do MVP desktop com modulo de marcadores e distribuicao (instalador + zip).

## 3) Roadmap por fases

## Fase 1 - MVP operacional (concluida em grande parte)

**Meta:** entregar fluxo principal funcional para demonstracao e uso inicial.

**Marcos principais:**
- sistema principal desktop funcionando;
- cadastro e gestao basica de pacientes;
- modulo EFM integrado por menu;
- exportacoes de marcadores;
- build de instalador e pacote portatil.

**Status:** em consolidacao final.

## Fase 2 - Integracao clinica dos marcadores

**Meta:** ligar resultado de marcadores ao historico clinico de forma estruturada.

**Marcos desejados:**
- vinculo de marcacao com paciente/avaliacao;
- historico de marcacoes por atendimento;
- recuperacao e comparacao de marcacoes anteriores;
- padronizacao de metadados de exportacao.

**Status:** planejada (proxima prioridade funcional).

**Especificacao detalhada (rascunho, 2026-05-26):** `especificacao-marcacoes-vinculo-paciente.md` — sistema unico EasyFeet, modulo por licenca (sem cadastro duplicado), paciente no topo do EFM, momentos clinicos para evolucao, pendencia PEND-MARC-001 (comparar imagens entre datas).

## Fase 3 - Robustez e operacao

**Meta:** aumentar confiabilidade para uso recorrente.

**Marcos desejados:**
- rotina de backup e restauracao simplificada;
- melhoria de logs e mensagens de erro;
- checklist de release consolidado;
- validacoes em maquinas limpas recorrentes.

**Status:** parcialmente iniciado.

## Fase 4 - POC Web em dominio

**Meta:** validar hipotese de produto web e acesso remoto.

**Marcos desejados:**
- definicao de arquitetura POC (backend + frontend);
- deploy inicial em dominio;
- auth/perfis basicos;
- banco servidor (candidato: PostgreSQL).

**Status:** visao estrategica, ainda sem inicio tecnico completo.

## Fase 5 - Produto modular comercial

**Meta:** estruturar ofertas por modulos e evolucao escalavel do produto.

**Marcos desejados:**
- politicas de habilitacao/licenciamento modular;
- trilha de instalacao com selecao de modulos;
- observabilidade e suporte de operacao;
- narrativa comercial e tecnica madura.

**Status:** visao de medio/longo prazo.

## 4) Dependencias entre fases

- Fase 2 depende da maturidade do modelo de dados clinicos.
- Fase 3 reduz risco para ampliar uso externo.
- Fase 4 depende de decisao arquitetural e recursos de infraestrutura.
- Fase 5 depende de padronizacao funcional e operacional das fases anteriores.

## 5) Indicadores de progresso sugeridos

- percentual de funcionalidades MVP estabilizadas;
- taxa de sucesso de instalacao/execucao em ambientes externos;
- tempo medio para gerar e validar release;
- quantidade de retrabalho por falha de processo;
- cobertura dos fluxos clinicos prioritarios.

## 6) Revisao do roadmap

Recomendacao:

- revisao quinzenal curta (status e bloqueios);
- revisao mensal mais estrategica (priorizacao e marcos);
- registro das mudancas neste arquivo para manter historico evolutivo.

