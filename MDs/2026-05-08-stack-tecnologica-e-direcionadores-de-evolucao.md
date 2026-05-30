# EasyFeet - Stack Tecnologica e Direcionadores de Evolucao

Data do registro: 2026-05-08

## Nome sugerido para este documento

O nome adotado para este arquivo foi:

- `2026-05-08-stack-tecnologica-e-direcionadores-de-evolucao.md`

Racional:

- Mantem o padrao cronologico `AAAA-MM-DD`.
- Identifica claramente que o foco e tecnologia + rumo do produto.
- Facilita montagem futura de timeline evolutiva.

## 1) Tecnologias utilizadas no estado atual

### Linguagem e runtime

- **Python 3.x**
  - Linguagem principal da aplicacao.
  - Boa produtividade para MVP e iteracoes rapidas.

### Interface desktop

- **Tkinter** (base nativa)
- **CustomTkinter** (camada visual moderna)
  - Usado para construir interface do sistema principal.
  - Permite interface desktop leve, sem dependencias de browser.

### Banco de dados

- **SQLite**
  - Banco local em arquivo (`data/easyfeet.db`).
  - Excelente para MVP, instalacao simples e operacao offline.

### Persistencia / ORM

- **SQLAlchemy**
  - Mapeamento objeto-relacional e acesso ao banco.
  - Abstracao que facilita futura migracao para banco servidor.

### Processamento de imagem

- **Pillow (PIL)**
  - Carregamento de imagens.
  - Conversao para tons de cinza.
  - Renderizacao de marcadores e exportacao de PNG.

### Configuracao e navegacao

- **JSON**
  - `menu-config-v1.json` para estrutura de menu e visibilidade por perfil.

### Empacotamento e distribuicao

- **PyInstaller**
  - Gera executaveis para Windows.
- **Inno Setup**
  - Gera instalador `.exe` para distribuicao do sistema principal.

## 2) Arquitetura atual (resumo)

- Aplicacao principal desktop (EasyFeet).
- Modulo de marcadores (EFM) separado e integrado via menu.
- Banco local SQLite compartilhado pelo principal.
- Fluxo de build para:
  - instalador (`release/EasyFeet-Setup-1.0.0.exe`)
  - pacote portatil (`release/EasyFeet_Portatil.zip`)

## 3) Decisoes de engenharia relevantes neste momento

- Prioridade em **MVP funcional** com baixo atrito de instalacao.
- Manter **modularidade** para evolucao e possivel comercializacao por modulos.
- Escolha de SQLite por simplicidade operacional inicial.
- Escolha de SQLAlchemy para evitar acoplamento excessivo ao SQLite.

## 4) Migracao futura de banco (SQLite -> PostgreSQL)

### Viabilidade

A migracao e **tecnicamente viavel e provavel** no futuro, especialmente para cenarios multiusuario, web e crescimento de volume.

### Motivos para migrar

- Melhor concorrencia de acesso.
- Escalabilidade superior.
- Recursos avancados de banco servidor (usuarios, backup centralizado, auditoria).

### Caminho recomendado

1. Manter camada de repositorio/servicos desacoplada.
2. Adotar migracoes de schema (ex.: Alembic) quando iniciar transicao.
3. Parametrizar `DATABASE_URL` por ambiente (dev, demo, producao).
4. Planejar etapa de migracao de dados do `.db` local para PostgreSQL.

## 5) Direcao de produto: POC web em dominio

Existe perspectiva de criar uma **POC web** em dominio proprio para validar:

- acesso remoto;
- fluxo de trabalho centralizado;
- experiencia multiusuario;
- potencial de produto SaaS.

### Implicacoes tecnicas esperadas

- Backend/API (possivel reaproveitamento da logica atual).
- Banco PostgreSQL em ambiente de servidor.
- Autenticacao, perfis e seguranca web.
- Camada de front-end web (a definir em fase de POC).

## 6) Distribuicao para outras maquinas (estado atual)

O produto ja possui duas formas praticas:

- **Instalador**
  - Instala em pasta escolhida pelo usuario.
  - Inclui principal e modulo de marcadores.
- **Pacote portatil (ZIP)**
  - Permite executar direto de pendrive/descompactado.
  - Adequado para demos e testes em campo.

## 7) Informacoes perifericas importantes para registro

- O projeto ja conta com scripts `.bat` para facilitar operacao sem comandos longos.
- O banco principal em producao atual e um arquivo local (`easyfeet.db`), portanto:
  - backup e copia sao simples;
  - deve-se fechar o app antes de copiar o banco.
- A documentacao em `.md` foi adotada como base para historico evolutivo.
- Ja existe mecanismo para converter `.md` em `.docx` para comunicacao executiva.

## 8) Marco historico

Este registro reconhece o inicio da evolucao estruturada do produto no periodo de:

- **07/05/2026** (inicio dos registros e consolidacao do MVP)
- **08/05/2026** (formalizacao da stack, distribuicao e direcao de evolucao)

Objetivo futuro: usar esses arquivos para construir uma **timeline do produto**, conectando decisao tecnica, entregas e maturidade comercial.

