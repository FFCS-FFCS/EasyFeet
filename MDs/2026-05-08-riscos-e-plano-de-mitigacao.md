# EasyFeet - Riscos e Plano de Mitigacao

Data do registro: 2026-05-08

## 1) Objetivo

Mapear riscos atuais do produto/projeto e definir acoes objetivas de mitigacao para reduzir impacto em demos, operacao e evolucao.

## 2) Matriz resumida de riscos

| ID | Risco | Probabilidade | Impacto | Nivel |
|----|-------|---------------|---------|-------|
| R1 | Perda/corrupcao de `easyfeet.db` local | Media | Alto | Alto |
| R2 | Falha de execucao em maquinas externas (dependencias/permissao) | Media | Alto | Alto |
| R3 | Divergencia entre principal e modulo EFM em releases | Media | Medio/Alto | Alto |
| R4 | Limites do SQLite em cenarios multiusuario | Media | Medio | Medio |
| R5 | Qualidade de sugestao automatica em imagens fora do padrao | Alta | Medio | Alto |
| R6 | Escopo crescer sem priorizacao (atrasos) | Alta | Medio | Alto |
| R7 | Falta de rastreabilidade de mudancas | Media | Medio | Medio |
| R8 | Dependencia de conhecimento concentrado em poucas pessoas | Media | Medio/Alto | Alto |

## 3) Plano de mitigacao por risco

### R1 - Perda/corrupcao de banco local

**Mitigacoes:**
- criar rotina simples de backup com timestamp;
- orientar fechamento do app antes de copiar banco;
- documentar restauracao rapida.

**Responsavel:** equipe tecnica  
**Prazo recomendado:** curto prazo

### R2 - Falha em maquina externa

**Mitigacoes:**
- checklist de teste em maquina limpa (instalador e zip);
- validar permissao de escrita no diretorio de execucao;
- manter fallback de mensagens de erro claras.

**Responsavel:** equipe tecnica  
**Prazo recomendado:** imediato/curto prazo

### R3 - Principal e EFM fora de sincronia

**Mitigacoes:**
- build unificado e versionado;
- checklist de regressao principal + EFM;
- padrao de release unico por versao.

**Responsavel:** release manager tecnico  
**Prazo recomendado:** curto prazo

### R4 - Limites de SQLite

**Mitigacoes:**
- monitorar sinais de saturacao (concorrencia, volume);
- preparar plano de migracao para PostgreSQL;
- introduzir migracoes estruturadas de schema.

**Responsavel:** arquitetura  
**Prazo recomendado:** medio prazo

### R5 - Heuristicas de marcacao insuficientes

**Mitigacoes:**
- manter ajuste manual simples e rapido;
- coletar exemplos de imagens problematicas;
- evoluir algoritmo com base em dataset real.

**Responsavel:** produto + tecnico  
**Prazo recomendado:** curto/medio prazo

### R6 - Crescimento de escopo

**Mitigacoes:**
- definir backlog priorizado por valor;
- congelar escopo por release;
- separar "must-have" de "nice-to-have".

**Responsavel:** produto  
**Prazo recomendado:** continuo

### R7 - Falta de rastreabilidade

**Mitigacoes:**
- manter atualizacao disciplinada dos arquivos `.md`;
- padronizar nomes com data;
- registrar decisao e impacto de cada release.

**Responsavel:** equipe toda  
**Prazo recomendado:** continuo

### R8 - Conhecimento concentrado

**Mitigacoes:**
- documentar rotinas de build, install e operacao;
- criar mini runbook tecnico;
- revisar conhecimento em pares quando possivel.

**Responsavel:** lider tecnico  
**Prazo recomendado:** curto prazo

## 4) Checklist pratico de mitigacao (proximas semanas)

- [ ] Criar backup automatizado simples do banco local.
- [ ] Executar teste completo em maquina limpa.
- [ ] Consolidar checklist de release em um unico documento.
- [ ] Definir criterios de entrada para migracao PostgreSQL.
- [ ] Coletar pacote de imagens reais para calibrar heuristicas de pontos.
- [ ] Atualizar historico `.md` a cada marco relevante.

## 5) Reavaliacao de riscos

Revisar este documento quando houver:

- nova release para demo externa;
- inicio da POC web;
- mudanca de banco;
- onboarding de novo colaborador tecnico.

