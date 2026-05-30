# EasyFeet - MD Mestre (Indice, Governanca e Baseline/Delta)

Ultima atualizacao: 2026-05-08

## Decisao de formato

Este arquivo **nao usa data no nome** por ser um documento vivo e central.

- Nome fixo: `MD_MESTRE-indice-e-governanca.md`
- Funcao: consolidar visao de toda a pasta `MDs`
- Atualizacao: sempre que houver novo MD ou alteracao relevante

## Objetivo

Este MD mestre serve para:

- mapear todos os MDs existentes;
- explicar o papel de cada tema;
- indicar baseline e deltas por tema;
- evitar duplicacao de conteudo;
- sustentar uma timeline evolutiva do produto.

## Convencao recomendada para os demais MDs

- Padrao de nome: `AAAA-MM-DD-<tema>.md`
- Primeiro arquivo de um tema: **baseline** (completo)
- Proximos arquivos do mesmo tema: **delta** (somente mudancas)

## Modelo baseline + delta (regra oficial)

Para cada tema documental:

1. O primeiro arquivo cronologico e o **Baseline**.
2. Arquivos seguintes do mesmo tema devem registrar apenas:
   - adicoes;
   - alteracoes;
   - remocoes;
   - impacto esperado.
3. Se houver mudanca estrutural grande, criar novo baseline e registrar o motivo.

Exemplo do seu ponto:

- `2026-05-08-roadmap-fases-e-marcos.md` = baseline
- `2026-05-10-roadmap-fases-e-marcos.md` = delta (explica apenas o que mudou)

## Catalogo atual por tema

## Tema: visao geral do produto

- Baseline: `2026-05-07-visao-geral-e-registro-evolutivo.md`
- Ultima versao: `2026-05-07-visao-geral-e-registro-evolutivo.md`
- Tipo atual: baseline unico
- Uso: contextualizacao geral para tecnico e negocio

## Tema: status tecnico e pendencias

- Baseline: `2026-05-07-status-tecnico-e-pendencias.md`
- Ultima versao: `2026-05-07-status-tecnico-e-pendencias.md`
- Tipo atual: baseline unico
- Uso: fotografia tecnica + backlog imediato

## Tema: stack tecnologica e direcao de evolucao

- Baseline: `2026-05-08-stack-tecnologica-e-direcionadores-de-evolucao.md`
- Ultima versao: `2026-05-08-stack-tecnologica-e-direcionadores-de-evolucao.md`
- Tipo atual: baseline unico
- Uso: tecnologias adotadas, migrabilidade e visao web/POC

## Tema: arquitetura e decisoes tecnicas

- Baseline: `2026-05-08-arquitetura-e-decisoes-tecnicas.md`
- Ultima versao: `2026-05-08-arquitetura-e-decisoes-tecnicas.md`
- Tipo atual: baseline unico
- Uso: decisoes, racional e gatilhos de revisao arquitetural

## Tema: riscos e mitigacao

- Baseline: `2026-05-08-riscos-e-plano-de-mitigacao.md`
- Ultima versao: `2026-05-08-riscos-e-plano-de-mitigacao.md`
- Tipo atual: baseline unico
- Uso: matriz de risco e plano de acao

## Tema: release e validacao

- Baseline: `2026-05-08-plano-de-release-e-validacao.md`
- Ultima versao: `2026-05-08-plano-de-release-e-validacao.md`
- Tipo atual: baseline unico
- Uso: processo padrao de empacotamento, teste e entrega

## Tema: roadmap de fases e marcos

- Baseline: `2026-05-08-roadmap-fases-e-marcos.md`
- Ultima versao: `2026-05-08-roadmap-fases-e-marcos.md`
- Tipo atual: baseline unico
- Uso: direcionamento por fases e marcos de produto

## Protocolo para "atualizar o gerenciador de MDs"

Quando solicitado para atualizar este MD mestre, o procedimento deve ser:

1. Ler todos os `*.md` em `MDs` (exceto este arquivo mestre, quando apropriado).
2. Agrupar arquivos por tema (ignorando a data inicial).
3. Determinar para cada tema:
   - baseline (mais antigo);
   - ultimo delta (mais novo).
4. Atualizar este arquivo com:
   - catalogo por tema;
   - resumo das mudancas novas;
   - ajustes de consistencia.
5. Atualizar o campo "Ultima atualizacao".

## Template recomendado para arquivos delta

Para um novo arquivo delta, iniciar com:

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

## Regras de consistencia documental

- Evitar duplicar texto completo de baseline em deltas.
- Se um delta ficar grande demais, avaliar criar novo baseline.
- Manter nomes consistentes e cronologicos.
- Registrar mudancas relevantes de produto em pelo menos um MD tematico.

