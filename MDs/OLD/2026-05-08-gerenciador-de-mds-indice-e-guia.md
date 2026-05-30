# EasyFeet - Gerenciador de MDs (Indice e Guia)

Data do registro: 2026-05-08

## Nome sugerido para este "MD mestre"

Nome adotado:

- `2026-05-08-gerenciador-de-mds-indice-e-guia.md`

Racional:

- Mantem o padrao cronologico `AAAA-MM-DD`.
- Identifica claramente que e o documento central dos demais MDs.
- Facilita consulta, onboarding e atualizacoes futuras.

## Objetivo deste arquivo

Este documento funciona como:

- indice da documentacao em `MDs`;
- dicionario/guia de leitura de cada MD;
- ponto unico para entender o estado documental do produto;
- base para atualizacao evolutiva (timeline de produto).

## Convencao geral dos arquivos MD

- Padrao de nome: `AAAA-MM-DD-assunto.md`
- Idioma: portugues (com foco tecnico e pratico).
- Estilo: objetivo, com secoes curtas e reutilizaveis.
- Regra: toda mudanca relevante no produto deve refletir em pelo menos um MD.

## Mapa dos MDs atuais (o que cada um cobre)

## 1) `2026-05-07-visao-geral-e-registro-evolutivo.md`

**Finalidade:** documento de contexto de produto para publico tecnico/negocio.  
**Quando ler:** primeiro contato com o projeto.  
**Perguntas que responde:**
- O que e o EasyFeet?
- Que problema resolve?
- O que ja funciona?
- Quais proximos passos de alto nivel?

## 2) `2026-05-07-status-tecnico-e-pendencias.md`

**Finalidade:** fotografia tecnica do momento + backlog de pendencias.  
**Quando ler:** planejamento tecnico de curto prazo.  
**Perguntas que responde:**
- Qual status atual por area?
- Quais pendencias priorizadas?
- Qual checklist rapido de validacao?

## 3) `2026-05-08-stack-tecnologica-e-direcionadores-de-evolucao.md`

**Finalidade:** registrar stack usada e direcao tecnica estrategica.  
**Quando ler:** discussoes de tecnologia, migracao, POC web.  
**Perguntas que responde:**
- Quais tecnologias estao em uso?
- O que e migravel (ex.: SQLite -> PostgreSQL)?
- Como distribuimos hoje (instalador/zip)?
- Qual visao de evolucao para web?

## 4) `2026-05-08-arquitetura-e-decisoes-tecnicas.md`

**Finalidade:** historico de decisoes de arquitetura e racional.  
**Quando ler:** antes de mudar arquitetura ou adotar nova abordagem.  
**Perguntas que responde:**
- Quais decisoes foram tomadas?
- Quais alternativas foram consideradas?
- Quais gatilhos exigem revisao arquitetural?

## 5) `2026-05-08-riscos-e-plano-de-mitigacao.md`

**Finalidade:** mapa de risco com acoes praticas de mitigacao.  
**Quando ler:** antes de release/demo e em planejamento de estabilidade.  
**Perguntas que responde:**
- Quais riscos sao altos agora?
- O que fazer para reduzir impacto?
- Quem e responsavel e qual prazo recomendado?

## 6) `2026-05-08-plano-de-release-e-validacao.md`

**Finalidade:** padrao operacional para gerar e validar release.  
**Quando ler:** toda vez que for gerar instalador/zip para entrega.  
**Perguntas que responde:**
- Qual passo a passo de release?
- Quais criterios de aceite?
- Como agir em rollback?

## 7) `2026-05-08-roadmap-fases-e-marcos.md`

**Finalidade:** visao de fases e marcos do produto.  
**Quando ler:** alinhamento de prioridade, escopo e timeline.  
**Perguntas que responde:**
- Em que fase estamos?
- O que entra nas proximas fases?
- Quais dependencias existem entre fases?

## Relacao entre os documentos (leitura recomendada)

Ordem recomendada para entendimento completo:

1. Visao geral
2. Stack tecnologica
3. Arquitetura e decisoes
4. Status tecnico e pendencias
5. Riscos e mitigacao
6. Plano de release e validacao
7. Roadmap de fases e marcos

## Protocolo de atualizacao deste gerenciador (quando voce pedir)

Quando voce pedir algo como:

- "atualizar o gerenciador de MDs"
- "regenerar o indice dos MDs"
- "sincronizar o dicionario dos MDs"

o procedimento deve ser:

1. Ler todos os arquivos `*.md` em `MDs` (exceto este, se necessario para evitar duplicidade de resumo).
2. Identificar novos arquivos, arquivos removidos e mudancas de escopo.
3. Atualizar:
   - lista de MDs;
   - finalidade de cada um;
   - relacoes e ordem de leitura;
   - observacoes de consistencia.
4. Manter este arquivo como referencia central do estado documental.

## Criticos de consistencia documental

Ao atualizar este gerenciador, verificar:

- se ha arquivos sem data no nome;
- se ha sobreposicao excessiva de conteudo entre MDs;
- se existe pendencia tecnica sem documento correspondente;
- se os nomes continuam claros para consulta futura.

## Proposta de timeline evolutiva (meta futura)

Usar os MDs como base para uma timeline de produto:

- marco tecnico (arquitetura, stack, release);
- marco funcional (novos modulos/fluxos);
- marco operacional (instalacao, distribuicao, validacao);
- marco estrategico (POC web, migracoes, comercializacao modular).

Com isso, a evolucao desde 07/05/2026 fica documentada de forma cronologica e auditavel.

