# EasyFeet - MVP Local (Python + SQLite)

Aplicacao local para avaliacao postural, geracao de laudos e acompanhamento de confeccao de palmilhas personalizadas.

## Objetivo desta primeira versao

- Rodar localmente no Windows
- Armazenar dados em SQLite (arquivo local, sem servidor)
- Permitir migracao futura para PostgreSQL com minimo retrabalho

## Funcionalidades atuais (MVP)

- Cadastro de clientes
- Registro de avaliacao postural
- Registro de laudo por avaliacao
- Registro de pedido de palmilha
- Listagem basica de clientes e historico

## Requisitos

- Python 3.11+

## Como executar

1. Criar e ativar ambiente virtual:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Instalar dependencias:

```powershell
pip install -r requirements.txt
```

3. Executar:

```powershell
python main.py
```

O banco local sera criado automaticamente em `data/easyfeet.db`.

### Interface grafica (nova)

```powershell
python easyfeet_main.py
```

A GUI possui:
- Dashboard com cards
- Sidebar por modulo com permissao por perfil
- Modulo de Pacientes com cadastro + listagem

## Gerar executavel (Windows)

```powershell
pip install pyinstaller
pyinstaller --onefile --name easyfeet main.py
```

Executavel gerado em `dist/easyfeet.exe`.

## Estrutura

- `easyfeet/db.py`: conexao e schema SQLite
- `easyfeet/repositories.py`: acesso a dados (camada pronta para trocar backend depois)
- `easyfeet/services.py`: regras de negocio
- `easyfeet/navigation.py`: menu escalavel por JSON + rotas CRUD padrao
- `easyfeet/cli.py`: interface de uso local em terminal
- `main.py`: ponto de entrada

## Preview do menu escalavel (JSON)

Arquivo de configuracao:

- `menu-config-v1.json`

Script para validar menu por perfil e mostrar rotas CRUD:

```powershell
python scripts/preview_menu.py
```

## Proximos passos sugeridos

- Adicionar exportacao de laudo em PDF
- Adicionar campos clinicos detalhados para fisioterapia
- Evoluir para interface desktop (Tkinter/PySide) mantendo mesma camada de dados
- Preparar deploy web (FastAPI + PostgreSQL)
