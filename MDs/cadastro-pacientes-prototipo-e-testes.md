# EasyFeet — Cadastro de pacientes (protótipo e testes)

**Atualizado:** 2026-05-25 (UTC-3)  
**Pasta oficial:** `C:\Users\flavi\OneDrive\Documentos\Ideias_Projetos\Cursor_Projetos\EasyFeet`

## Situação

O cadastro de pacientes **ainda está em evolução** (novos campos, layout, possíveis abas no futuro). Enquanto isso, o fluxo abaixo pode ser **repetido quantas vezes forem necessárias** — não é um passo único de release.

O app principal (`easyfeet_main.py` / `gui.py`) pode ficar atrás do protótipo até a integração ser pedida explicitamente.

## Ficheiros do protótipo

| Ficheiro | Função |
|----------|--------|
| `teste_cadastro_paciente_extendido.py` | Janela de teste (CustomTkinter), grava em `data/easyfeet.db` |
| `EF_teste_cadastro.bat` | Atalho rápido: duplo clique para abrir o protótipo |
| `easyfeet/cliente_dados_corporais.py` | Validação altura, peso, IMC, lateralidade |
| `easyfeet/models.py`, `db.py`, `repositories.py`, `services.py` | Modelo e persistência (migração SQLite leve em `init_db`) |

**Campos já no protótipo (2026-05-25):** altura (m), peso (kg), IMC (calculado), lateralidade (Destro / Canhoto / Ambidestro), mais os campos já existentes (nome, telefone, e-mail, nascimento, sexo, observações).

## Processo repetível (cada alteração de cadastro)

1. Ajustar modelo/serviço/validação em `easyfeet/` conforme o novo requisito.
2. Atualizar `teste_cadastro_paciente_extendido.py` (formulário + tabela de teste).
3. Se o `.bat` precisar de mensagens ou checagens novas, atualizar `EF_teste_cadastro.bat`.
4. Testar com **duplo clique** em `EF_teste_cadastro.bat` (ou `python teste_cadastro_paciente_extendido.py` na raiz OneDrive).
5. Quando o cadastro estiver estável, integrar em `easyfeet/gui.py` (módulo Pacientes) — passo separado, sob pedido.

**Não** gerar instalador (`build_instalador.bat`) só por mudança de cadastro em protótipo.

## Regra para o assistente (Cursor)

Na **próxima** (e nas seguintes) alterações pedidas ao **cadastro de pacientes**:

1. **Perguntar ao utilizador** se deseja gerar/atualizar **apenas** `EF_teste_cadastro.bat` para testes rápidos, ou se quer também mudanças no app principal (`gui.py`) / instalador.
2. Se a resposta for só teste rápido: focar em `teste_cadastro_paciente_extendido.py` + `EF_teste_cadastro.bat` (e camada `easyfeet/` necessária), **sem** rebuild de EXE/ZIP salvo pedido explícito.
3. Trabalhar **somente** na pasta OneDrive oficial; **nunca** criar artefactos em `C:\Cursor_Projetos\EasyFeet`.

Registo do pedido do utilizador (2026-05-25): *«na próxima alteração em cadastro, pergunte se desejo que gere apenas o EF_teste_cadastro.bat para os testes»*.

## Módulo de marcadores (protótipo separado)

| Ficheiro | Função |
|----------|--------|
| `teste_modulo_marcadores.py` | EFM com **Exportar / Gerar / Sugerir / Limpar** no topo (fora dos painéis) |
| `EF_teste_modulo.bat` | Atalho para abrir o protótipo |

Painéis aceitam `show_action_toolbar=False`; métodos `toolbar_*` para a barra central. O `EFM_Marcadores.py` principal mantém botões nos painéis até integração.

## Referências

- Caminho do projeto: `caminho-do-projeto.md`
- Índice geral: `gerenciador-de-mds-indice-e-guia.md`
