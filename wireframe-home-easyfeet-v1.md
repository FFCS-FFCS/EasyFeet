# EasyFeet - Wireframe Textual da Home (v1)

## Objetivo

Definir uma tela principal simples, clara para uso clinico diario e preparada para crescer sem retrabalho.

---

## Estrutura geral da tela

```
+--------------------------------------------------------------------------------------+
| Header fixo: [Logo] [Busca rapida]                         [Usuario] [Perfil] [Sair] |
+-----------------------------+--------------------------------------------------------+
| Sidebar (modulos)           | Area central (conteudo dinamico)                      |
| - Dashboard                 | +--------------------------+-------------------------+ |
| - Pacientes                 | | Card: Hoje              | Card: Pendencias       | |
| - Avaliacoes                | | - atendimentos dia      | - laudos pendentes     | |
| - Laudos                    | | - novos pacientes       | - palmilhas em atraso  | |
| - Palmilhas                 | +--------------------------+-------------------------+ |
| - Imagens                   | +--------------------------+-------------------------+ |
| - Relatorios                | | Card: Pacientes recentes | Card: Atalhos rapidos  | |
| - Configuracoes             | | - ultimos atendimentos   | - Novo paciente        | |
|                             | | - status resumido        | - Nova avaliacao       | |
|                             | +--------------------------+ - Anexar imagens       | |
|                             |                              - Gerar analise prelim.  | |
+-----------------------------+--------------------------------------------------------+
```

---

## Header fixo (sempre visivel)

- Logo EasyFeet (clicar volta ao Dashboard)
- Busca rapida global (nome do paciente, telefone, id)
- Dados do usuario logado
- Acoes de conta (perfil/sair)

### Comportamento esperado

- Busca abre resultado rapido com atalho para prontuario
- Header permanece fixo durante rolagem

---

## Sidebar por modulos (navegacao principal)

1. Dashboard
2. Pacientes
3. Avaliacoes
4. Laudos
5. Palmilhas
6. Imagens
7. Relatorios
8. Configuracoes

### Boas praticas para escalar

- Nao hardcode de rotas no frontend
- Carregar menu de arquivo JSON/config
- Exibir itens conforme permissao do perfil

---

## Area central em cards (home)

### Card 1 - Hoje

- Total de atendimentos do dia
- Avaliacoes realizadas
- Laudos emitidos hoje

### Card 2 - Pendencias

- Avaliacoes sem laudo
- Palmilhas sem status final
- Revisoes pendentes

### Card 3 - Pacientes recentes

- Lista curta com ultimos pacientes atendidos
- Nome, data, status rapido

### Card 4 - Atalhos rapidos

- Novo paciente
- Nova avaliacao
- Gerar analise preliminar
- Anexar imagens

---

## Painel direito opcional (fase 2)

- Alertas clinicos
- Lembretes de retorno
- Tarefas pessoais do avaliador(a)

---

## Fluxo base de CRUD (padrao por modulo)

Cada modulo segue o mesmo ciclo para reduzir esforco:

- `list` -> listagem + filtros + ordenacao
- `create` -> formulario novo registro
- `detail` -> visualizacao completa
- `edit` -> atualizacao controlada
- `archive` (opcional) -> desativar sem apagar historico

---

## Regras de usabilidade para equipe clinica

- Priorizar leitura em ate 2 cliques para informacao critica
- Evitar telas longas sem secoes
- Padronizar botoes:
  - Primario: Salvar
  - Secundario: Cancelar
  - Perigo: Excluir/Arquivar
- Mostrar confirmacao clara apos salvar

---

## Evolucao sem retrabalho

- Novos modulos entram no JSON de menu
- Cada modulo novo reaproveita template CRUD padrao
- Permissoes por perfil resolvem visibilidade sem mexer na estrutura da tela
