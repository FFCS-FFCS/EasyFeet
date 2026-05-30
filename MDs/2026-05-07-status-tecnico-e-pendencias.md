# EasyFeet - Status Tecnico e Pendencias

Data do registro: 2026-05-07

## 1) Status tecnico atual

### 1.1 Base da aplicacao

- Stack principal: Python + SQLAlchemy + SQLite + CustomTkinter/Tkinter.
- Entrada principal: `easyfeet_main.py`.
- Configuracao de menu por arquivo JSON: `menu-config-v1.json`.
- Banco local: `data/easyfeet.db`.

### 1.2 Funcionalidades ja implementadas no MVP

- Dashboard basico.
- Cadastro/listagem/edicao de pacientes (modulo principal).
- Busca simples de pacientes por nome.
- Janela com observacao de paciente.
- Estrutura de placeholders para demais modulos do menu.

### 1.3 Modulo EFM (marcadores)

- Entrada do modulo: `EFM_Marcadores.py`.
- Tipos atuais:
  - Linhas (vista plantar): A/B/C/D.
  - Pontos (articulacoes/referencias): A-F.
- Exportacoes:
  - PNG em P&B.
  - JSON tecnico com coordenadas.
- Ajuda por tipo com texto externo editavel:
  - `marcador_plantar/help_plantar_pt.txt`
  - `marcador_pontos/help_pontos_pt.txt`
- Persistencia da imagem ao alternar entre tipos dentro do EFM.
- Botao de abrir imagem centralizado no topo do EFM.

### 1.4 Integracao principal -> modulo

- Menu principal contem item de marcadores (`efm_marcadores`).
- Abertura do EFM em processo separado (nao bloqueante).
- Tratamento para modo empacotado (`sys.frozen`) procurando `EFM_Marcadores.exe` ao lado do principal.

### 1.5 Distribuicao e entrega

- Build com PyInstaller (principal e modulo).
- Instalador Windows (Inno Setup): `release/EasyFeet-Setup-1.0.0.exe`.
- Pacote portatil ZIP: `release/EasyFeet_Portatil.zip`.
- Scripts de build:
  - `build_instalador.bat`
  - `scripts/build_windows_installer.ps1`
  - `scripts/easyfeet_installer.iss`
- Utilitarios de limpeza:
  - `limpar_build.bat`

### 1.6 Documentacao e conversao para Word

- Registros em Markdown na pasta `MDs`.
- Conversores para DOCX:
  - `MDs/converter_md_para_docx.bat`
  - `MDs/converter_todos_md_para_docx.bat`

## 2) Pendencias tecnicas (priorizadas)

## Alta prioridade

- [ ] Integrar de forma nativa os resultados dos marcadores ao fluxo de paciente/avaliacao (vinculo de arquivo e metadados).
- [ ] Definir estrategia de versao do banco (`easyfeet.db`) e migracoes futuras.
- [ ] Revisar tratamento de erros do launcher de modulo em cenarios de permissao/caminho.
- [ ] Validar fluxo completo em PC limpo (sem ambiente de desenvolvimento) com instalador e com ZIP portatil.

## Media prioridade

- [ ] Unificar estilo visual entre tela principal e modulo EFM.
- [ ] Revisar heuristica automatica de pontos para casos de baixa qualidade de imagem e orientacao variavel.
- [ ] Adicionar logs basicos de diagnostico para falhas de abertura/exportacao.
- [ ] Criar rotina de backup simples do banco (`data/easyfeet.db`) com data no nome.

## Baixa prioridade

- [ ] Melhorar internacionalizacao/acentuacao em mensagens de UI.
- [ ] Refinar icones, metadados e detalhes de instalacao (atalhos, desinstalacao com nome amigavel, etc.).
- [ ] Estruturar roadmap de modulos opcionais para comercializacao futura.

## 3) Checklist de validacao rapida (release demo)

- [ ] Abrir `EasyFeet.exe` (instalado) sem erro.
- [ ] Acessar menu "Marcadores" e abrir `EFM_Marcadores`.
- [ ] Carregar imagem e desenhar linhas (A-D).
- [ ] Trocar para pontos (A-F) mantendo a mesma imagem.
- [ ] Exportar PNG/JSON em ambos os tipos.
- [ ] Fechar/reabrir aplicativo e confirmar consistencia do banco.
- [ ] Testar pacote portatil (ZIP) executando direto da pendrive.

## 4) Riscos conhecidos

- Dependencia de escrita local para SQLite (`data/easyfeet.db`).
- Em pendrive/rede, desempenho e permissao podem variar.
- Heuristicas automaticas de pontos/linhas dependem da qualidade da imagem.
- Crescimento de escopo sem modularizacao pode gerar acoplamento entre principal e EFM.

## 5) Proximos passos sugeridos (curto prazo)

1. Fechar padrao de dados para salvar resultados de marcadores por paciente/avaliacao.
2. Implementar uma tela simples de historico de marcacoes por paciente.
3. Preparar release `1.0.1` com ajustes de robustez e testes de instalacao.

