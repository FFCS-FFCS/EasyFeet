# EasyFeet - Visao Geral e Registro Evolutivo

Data do registro: 2026-05-07

## O que e o EasyFeet

O EasyFeet e um sistema para apoio ao atendimento clinico em podologia/fisioterapia, com foco em organizacao de dados de pacientes e avaliacao plantar. O projeto combina:

- Gestao clinica basica (cadastros e consulta de informacoes).
- Analise por imagem da planta do pe com marcadores visuais.
- Estrutura preparada para evolucao modular e comercializacao por pacotes.

## Qual problema resolve

Na pratica, o sistema resolve a dificuldade de centralizar, padronizar e reaproveitar informacoes de atendimento. Em vez de processos dispersos (anotacoes separadas, imagens sem padrao, laudos desconectados), o EasyFeet cria um fluxo unico com:

- Registro de pacientes e historico.
- Dados de avaliacao organizados.
- Marcacao visual em imagem plantar com exportacao tecnica (PNG + JSON).
- Base pronta para evoluir para relatorios e protocolos mais completos.

## Ideia do projeto

A ideia central e ter um sistema principal leve, com menu orientado por configuracao, e modulos especializados que podem ser ativados e evoluidos separadamente.

Isso permite:

- Entrega rapida de um MVP funcional.
- Evolucao gradual sem reescrever o sistema inteiro.
- Possibilidade futura de licenciamento por modulos.

## O que ja funciona hoje

### Sistema principal

- Aplicacao desktop em Python com interface (CustomTkinter/Tkinter).
- Banco SQLite local (`data/easyfeet.db`).
- Menu por configuracao (`menu-config-v1.json`).
- Modulos principais ja visiveis no menu (Dashboard, Pacientes e placeholders para demais areas).
- Cadastro/edicao/listagem de pacientes funcional no MVP.

### Modulo de marcadores (EFM)

- Modulo unificado `EFM_Marcadores.py`.
- Selecao de tipo de marcador:
  - Linhas (vista plantar).
  - Pontos (articulacoes/referencias).
- Ajuda por tipo de marcador (texto editavel por arquivo `.txt`).
- Persistencia da imagem ao alternar entre tipos.
- Exportacao em preto e branco (PNG + JSON).
- Integracao com o sistema principal por menu (abre em janela separada, nao bloqueante).

### Distribuicao

- Build para Windows com executaveis.
- Instalador do sistema principal com modulo junto.
- Pacote portatil em ZIP para uso direto (inclusive em pendrive).

## O que esta previsto para evolucao

### Curto prazo

- Refinar layout e usabilidade do modulo de marcadores.
- Melhorar heuristicas de sugestao automatica de pontos/linhas.
- Ajustes de textos de ajuda e padrao clinico por protocolo.

### Medio prazo

- Integrar melhor os resultados dos marcadores ao fluxo clinico (vinculo direto com pacientes/avaliacoes).
- Expandir modulo de imagens, avaliacoes e laudos com fluxo completo.
- Melhorar empacotamento e versionamento de releases.

### Longo prazo

- Modelo de licenciamento por modulo (instalacao seletiva).
- Relatorios clinicos mais completos.
- Estrutura para integracoes futuras e melhorias de produtividade.

## Observacoes de registro evolutivo

- Este documento e um marco de estado do projeto em 2026-05-07.
- A proposta e manter novos arquivos no formato:
  - `AAAA-MM-DD-assunto.md`
- Assim, o historico evolutivo fica claro, cronologico e facil de consultar.

