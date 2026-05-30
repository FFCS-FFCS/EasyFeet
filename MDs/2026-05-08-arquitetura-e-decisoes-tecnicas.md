# EasyFeet - Arquitetura e Decisoes Tecnicas

Data do registro: 2026-05-08

## 1) Objetivo deste documento

Registrar as decisoes tecnicas principais tomadas ate o momento, com o racional por tras de cada uma. Este arquivo deve ser atualizado quando houver mudancas de arquitetura ou de direcao tecnica.

## 2) Visao de arquitetura atual

- Aplicacao desktop principal (EasyFeet) com interface em Python.
- Modulo de marcadores (EFM) separado em janela propria, integrado ao menu do principal.
- Persistencia local em SQLite.
- Configuracao de menu orientada por JSON.
- Distribuicao por executavel Windows + instalador.

## 3) Decisoes tecnicas e racional

### 3.1 Python como base

**Decisao:** usar Python para acelerar prototipacao e evolucao do MVP.  
**Racional:** menor tempo para validar fluxo clinico e iterar com feedback real.

### 3.2 Interface desktop (Tkinter + CustomTkinter)

**Decisao:** manter app desktop nativo no MVP.  
**Racional:** instalacao simples, operacao offline e menor complexidade inicial que uma arquitetura web completa.

### 3.3 SQLite como banco inicial

**Decisao:** iniciar com SQLite (`data/easyfeet.db`).  
**Racional:** baixa friccao operacional para demo e uso local, sem infraestrutura externa.

### 3.4 SQLAlchemy como camada de acesso

**Decisao:** usar SQLAlchemy desde o inicio.  
**Racional:** reduzir acoplamento ao banco especifico e facilitar migracao futura para PostgreSQL.

### 3.5 Modulo EFM desacoplado do principal

**Decisao:** EFM em componente separado (`EFM_Marcadores`) com integracao por menu.  
**Racional:** modularidade para evolucao independente e base para futura comercializacao por modulos.

### 3.6 Distribuicao em duas modalidades

**Decisao:** fornecer instalador e pacote portatil ZIP.  
**Racional:** cobrir uso padrao instalado e cenarios de demonstracao em pendrive/ambiente temporario.

## 4) Alternativas consideradas

- App web desde o inicio:
  - **Nao adotada agora** por aumento de escopo (infra, auth, deploy, operacao).
- Banco servidor no MVP:
  - **Nao adotado agora** para manter simplicidade e velocidade de entrega.
- Integrar EFM dentro da mesma tela do principal:
  - **Postergado**; janela separada atende melhor o curto prazo com baixo risco.

## 5) Consequencias tecnicas conhecidas

- Vantagens:
  - velocidade de entrega;
  - baixo custo de entrada;
  - boa base para evoluir.
- Limites atuais:
  - SQLite e desktop local nao escalam bem para multiusuario simultaneo;
  - necessidade de maior governanca de dados ao crescer.

## 6) Gatihos para revisao de arquitetura

Reavaliar arquitetura quando houver:

- necessidade de uso multiusuario em tempo real;
- demanda por acesso remoto em larga escala;
- crescimento de volume de dados e integrações externas;
- formalizacao da POC web em dominio.

## 7) Proxima revisao prevista

Atualizar este documento apos:

- primeira rodada de uso externo com instalador/zip;
- definicao do escopo da POC web;
- decisao sobre estrategia de migracao para PostgreSQL.

