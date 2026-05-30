# EasyFeet — Caminho canónico do projeto

**Atualizado:** 2026-05-25 (UTC-3, cadastro protótipo)

## Pasta de trabalho oficial

```
C:\Users\flavi\OneDrive\Documentos\Ideias_Projetos\Cursor_Projetos\EasyFeet
```

## Pasta anterior (descontinuada)

```
C:\Cursor_Projetos\EasyFeet
```

**Não usar** esta localização para desenvolvimento, Cursor, build nem cópia para pen drive. Os dados (`data/`, `Imagens/`, regras de marcadores) vivem apenas na pasta OneDrive acima.

**Regra para assistentes e scripts:** não gerar `dist/`, `release/`, `build/`, `EasyFeet_Com_Dados.zip` nem instalador em `C:\Cursor_Projetos\EasyFeet`. O script `scripts/build_windows_installer.ps1` **bloqueia** build se a raiz for a pasta antiga.

## O que o código faz após a mudança

- `easyfeet/paths.py` define `PROJECT_ROOT` a partir do código (não depende do `cd` no terminal).
- `data/easyfeet.db` e `data/marker_rules.json` resolvem-se sempre relativamente à raiz do repositório.
- Caminhos antigos `C:\Cursor_Projetos\EasyFeet\...` em JSON são migrados automaticamente ao gravar regras; imagens novas são guardadas como caminhos relativos (ex.: `data\marker_rule_images\...`).

## Cadastro de pacientes (protótipo — processo repetível)

Enquanto o cadastro evolui, usar o protótipo e o atalho:

- `teste_cadastro_paciente_extendido.py`
- `EF_teste_cadastro.bat` (duplo clique)

Este ciclo pode repetir-se a cada mudança de campos/layout. Detalhes e **regra para o assistente** (perguntar se basta atualizar o `.bat`): ver **`cadastro-pacientes-prototipo-e-testes.md`**.

## Build e release (só na pasta OneDrive)

Executar **sempre** a partir da raiz oficial:

- `limpar_build.bat` (opcional, limpa artefactos antigos)
- `build_instalador.bat` → chama `scripts/build_windows_installer.ps1`

**Saídas para pen drive / outro PC** (todas **nesta** raiz, não em `C:\Cursor_Projetos\EasyFeet`):

| Artefacto | Caminho relativo à raiz OneDrive |
|-----------|----------------------------------|
| Instalador | `release\EasyFeet-Setup-1.0.0.exe` |
| ZIP portátil | `EasyFeet_Com_Dados.zip` |
| Pasta descompactada | `dist\EasyFeet\` (equivalente ao ZIP) |

O build copia a pasta `data\` completa (base SQLite, `marker_rules.json`, imagens das regras). Não é necessário recadastrar pacientes após instalar, desde que o `data\` desta raiz esteja atualizado antes de gerar o instalador.

**Nota:** um build feito por engano em `C:\Cursor_Projetos\EasyFeet` (2026-05-25) **não** é o pacote canónico — ignorar ou apagar; regenerar só a partir desta pasta quando precisar de novo EXE/ZIP.

## Cursor / IDE

Abrir o projeto **somente** em:

`C:\Users\flavi\OneDrive\Documentos\Ideias_Projetos\Cursor_Projetos\EasyFeet`

### Chats e histórico do agente

O Cursor guarda conversas **por pasta do workspace**, não dentro do repositório:

| Workspace | Pasta de metadados do Cursor |
|-----------|------------------------------|
| Antigo (`C:\Cursor_Projetos\EasyFeet`) | `%USERPROFILE%\.cursor\projects\c-Cursor-Projetos-EasyFeet` |
| Novo (OneDrive) | `%USERPROFILE%\.cursor\projects\c-Users-flavi-OneDrive-Documentos-Ideias-Projetos-Cursor-Projetos-EasyFeet` |

Foi feita cópia de `agent-transcripts`, `agent-tools`, `assets` e `terminals` do projeto antigo para o novo (sem sobrescrever o chat atual). Para repetir ou completar: feche o Cursor e execute `scripts\migrar_pasta_antiga.ps1`.

**Recuperar o chat «EasyFeet» na UI (sem pasta antiga):** feche o Cursor e execute `python scripts\relink_chat_easyfeet.py`. Depois reabra só a pasta OneDrive e abra o chat **EasyFeet** no histórico.

**Nota:** cópia só de `agent-transcripts` não basta para o histórico aparecer na interface; o Cursor usa `state.vscdb` em `%APPDATA%\Cursor\User\`.

### Erro "sharing violation" ao renomear a pasta antiga

Algum processo ainda usa ficheiros em `C:\Cursor_Projetos\EasyFeet` (Cursor com workspace antigo, `EasyFeet.exe`, terminal com `cd` na pasta antiga, antivirus/OneDrive). Passos:

1. Fechar Cursor e EasyFeet.
2. Abrir só o workspace na pasta OneDrive.
3. Reiniciar o PC se o erro persistir.
4. Só então renomear ou apagar `C:\Cursor_Projetos\EasyFeet` (ou deixar como backup com outro nome, ex. `_EasyFeet_OLD`).
