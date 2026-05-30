# EasyFeet - Plano de Release e Validacao

Data do registro: 2026-05-08

## 1) Objetivo

Padronizar o processo de empacotamento, validacao e entrega de cada release para reduzir erros e aumentar previsibilidade.

## 2) Artefatos de release esperados

Para cada versao, gerar:

- Instalador:
  - `release/EasyFeet-Setup-<versao>.exe`
- Pacote portatil:
  - `release/EasyFeet_Portatil.zip`

## 3) Processo recomendado (passo a passo)

### Etapa A - Preparacao

- [ ] Validar que o sistema abre e executa o fluxo principal.
- [ ] Validar modulo EFM (linhas e pontos).
- [ ] Atualizar documentos de status se houver mudanca relevante.
- [ ] Definir numero da versao.

### Etapa B - Build

- [ ] (Opcional) executar `limpar_build.bat`.
- [ ] Executar `build_instalador.bat`.
- [ ] Confirmar geracao de instalador e zip em `release`.

### Etapa C - Validacao funcional minima

- [ ] Abrir executavel principal.
- [ ] Navegar em dashboard e pacientes.
- [ ] Abrir menu de marcadores.
- [ ] Confirmar abertura do `EFM_Marcadores`.
- [ ] Testar exportacao PNG/JSON de linhas.
- [ ] Testar exportacao PNG/JSON de pontos.
- [ ] Fechar e reabrir aplicativo sem erro.

### Etapa D - Validacao de distribuicao

- [ ] Testar instalador em maquina limpa.
- [ ] Testar pacote ZIP portatil (incluindo pendrive).
- [ ] Confirmar gravacao/leitura de `data/easyfeet.db`.

### Etapa E - Entrega

- [ ] Publicar artefatos finais para uso interno/cliente.
- [ ] Registrar observacoes da release em `.md`.

## 4) Criterios de aceite da release

A release e considerada valida quando:

- principal abre sem erro;
- modulo de marcadores abre a partir do principal;
- exportacoes funcionam;
- instalador instala e executa;
- zip portatil executa direto da pasta/pendrive.

## 5) Estrategia de rollback

Se a release falhar:

- manter release anterior disponivel;
- voltar para instalador/zip da versao anterior;
- registrar incidente e causa raiz no historico tecnico.

## 6) Itens que nao devem ser esquecidos

- Nome de versao consistente entre artefatos.
- Verificacao de caminho do banco e permissao de escrita.
- Teste rapido de abertura em contexto empacotado.
- Revisao visual basica de mensagens e layout.

## 7) Melhorias futuras no processo de release

- automatizar pipeline de build/validação;
- adicionar assinatura digital de instalador;
- publicar changelog por versao;
- anexar checklist preenchido como evidência de release.

