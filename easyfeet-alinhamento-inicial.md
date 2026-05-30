# EasyFeet - Alinhamento Inicial do Projeto

Documento de referencia para uso no GPT e backup historico do inicio do projeto.

## 1) Contexto

- Projeto criado para uso profissional da fisioterapeuta responsavel (usuaria principal e detentora do conhecimento).
- Objetivo inicial: atender clientes com avaliacao postural, gerar laudos e apoiar a confeccao de palmilhas personalizadas.
- Nome escolhido e validado: **EasyFeet**.

## 2) Visao de produto

### Fase inicial (MVP local)

- Cadastro de clientes
- Registro de avaliacao postural
- Geracao de laudo
- Registro e acompanhamento de pedido de palmilha
- Consulta de historico por cliente

### Evolucao futura (expansao)

- Biomecanica
- Escaneamento
- Acessorios
- Fisioterapia
- IA / analise da pisada
- Franquias

## 3) Decisoes tecnicas combinadas

- Linguagem principal: **Python**
- Primeira entrega: **aplicacao local**
- Armazenamento inicial: **SQLite**
  - sem servidor de banco
  - arquivo local simples
  - adequado para poucos clientes e fase de testes
- Meta futura: migrar para **PostgreSQL** quando houver crescimento

## 4) Motivo de usar SQLite no inicio

- Nao exige instalacao de servidor de banco no computador da usuaria
- Facil distribuicao em outro computador local
- Bom para POC e validacao de processo
- Menor complexidade operacional no comeco

## 5) Distribuicao para outro computador

- Opcao recomendada: empacotar em executavel (`.exe`) no futuro
- Com SQLite, o banco pode ser apenas um arquivo local (`.db`)
- Em geral, nao exige instalacao separada de banco de dados

## 6) Estrategia de migracao futura para PostgreSQL

Para evitar retrabalho, o sistema deve nascer com separacao de camadas:

- Camada de dominio/regra de negocio
- Camada de acesso a dados (repositorios)
- Interface (CLI agora, web depois)

Quando migrar:

1. manter regras de negocio
2. trocar implementacao de persistencia para PostgreSQL
3. migrar dados de SQLite para PostgreSQL via script
4. validar rotinas e relatorios

## 7) Estrategia de web POC futura

- Primeiro foco: validar fluxo local com usuaria principal
- Depois: subir POC web
- Observacao: Wix nao e a melhor opcao para backend Python; plataformas de deploy Python costumam ser mais adequadas

## 8) Principios de conducao do projeto

- Comecar simples e funcional
- Priorizar uso real no atendimento
- Evoluir por ciclos curtos de melhoria
- Preservar historico clinico com consistencia
- Preparar base tecnica para escalar sem reescrever tudo

## 9) Proximos passos sugeridos

1. Fechar campos obrigatorios da ficha de avaliacao postural
2. Definir formato minimo do laudo (template)
3. Testar fluxo completo com casos reais da usuaria
4. Ajustar linguagem e usabilidade
5. Planejar interface visual (desktop/web) apos validacao do fluxo

---

Ultima atualizacao: 2026-05-07
