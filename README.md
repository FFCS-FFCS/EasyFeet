<p align="center">
  <img src="Imagens/EasyFeet/easyfeet_logo_header_1200x300.png" alt="EasyFeet" width="480">
</p>

# EasyFeet

**Sistema desktop de apoio ao atendimento em podologia e fisioterapia:** cadastro de pacientes, análise da planta do pé por imagem, teste do navicular e laudos em PDF.

Versão atual: **2.0.0** · Python · SQLite · Windows

> Todos os pacientes, fotos e laudos deste repositório são **fictícios**, criados só para demonstração e testes.

---

## O problema

No consultório, as informações do atendimento ficavam espalhadas: anotações em papel, fotos do pé sem padrão, laudos escritos à mão e desconectados do histórico do paciente. Comparar a evolução entre consultas era difícil e demorado.

## A solução

O EasyFeet reúne tudo em um fluxo único:

1. **Cadastro do paciente** com dados corporais (altura, peso, IMC, lateralidade).
2. **Análise plantar por imagem:** a profissional carrega a foto do plantígrafo ou do podoscópio e marca linhas e pontos de referência. O sistema sugere as linhas automaticamente (heurística ou regra configurável), e ela ajusta.
3. **Teste do navicular** com ficha, classificação automática (limiar de Brody, até 10 mm = normal) e laudo.
4. **Laudos em PDF** com a identidade visual da clínica, salvos por paciente.
5. **Momentos clínicos:** cada avaliação fica registrada com data, formando a linha do tempo do paciente.

## Telas

**Cadastro de pacientes**

![Ficha do paciente](Imagens/EasyFeet/Telas%20do%20Sistema/Ficha_Paciente.png)

**Módulo de marcadores (EFM): análise da planta do pé**

![Análise do plantígrafo](Imagens/EasyFeet/Telas%20do%20Sistema/An%C3%A1lise_Plant%C3%ADgrafo.png)

Linhas A–D: eixo longitudinal, largura do antepé, do médio-pé e do retropé. A marcação é exportada em PNG + JSON e salva no histórico do paciente.

## Funcionalidades

| Área | O que faz |
|---|---|
| Pacientes | Cadastro, edição, busca, observações, PDF da ficha (em branco ou preenchida) |
| Plantígrafo | Análise por imagem com marcadores de linhas, regras editáveis, laudos |
| Podoscópio | Ficha de avaliação, laudos e PDF |
| Teste do navicular | Ficha, classificação (Modo A), laudos com textos clínicos e PDF |
| Ficha clínica | Linha do tempo com os momentos de cada paciente |
| Menu e perfis | Menu montado por configuração JSON, com permissões por perfil (admin, fisioterapeuta, recepção) |
| Distribuição | Instalador Windows (Inno Setup), versão DEMO e pacote portátil em ZIP |

## Como foi construído

- **Python 3.11+** com interface em **CustomTkinter/Tkinter**
- **SQLite** com **SQLAlchemy**, para permitir a migração futura para PostgreSQL sem reescrever o acesso a dados
- **Pillow** e **NumPy** para o tratamento das imagens; **ReportLab** para os PDFs
- Menu orientado por configuração (`menu-config-v2.json`), pensado para licenciamento por módulos
- Módulo de marcadores (EFM) desacoplado do sistema principal
- Testes automatizados e testes de fumaça em `tests/` e `scripts/`
- Desenvolvido com apoio de IA (Cursor), a partir de requisitos, regras de negócio e validação feitos por mim junto à profissional usuária

## Documentação do produto

A pasta [`MDs/`](MDs/) registra o projeto como produto, não só como código:

- [Visão geral e registro evolutivo](MDs/2026-05-07-visao-geral-e-registro-evolutivo.md)
- [Arquitetura e decisões técnicas](MDs/2026-05-08-arquitetura-e-decisoes-tecnicas.md), com o racional de cada escolha e as alternativas descartadas
- [Roadmap por fases e marcos](MDs/2026-05-08-roadmap-fases-e-marcos.md)
- [Riscos e plano de mitigação](MDs/2026-05-08-riscos-e-plano-de-mitigacao.md)
- [Plano de release e validação](MDs/2026-05-08-plano-de-release-e-validacao.md)
- [Especificação: marcações vinculadas ao paciente](MDs/especificacao-marcacoes-vinculo-paciente.md)
- [Lista de próximos passos](MDs/lista-de-proximos-passos.md)

## Como executar

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python easyfeet_main.py
```

O banco local é criado automaticamente em `data/easyfeet.db` (fora do Git).

Para gerar o instalador Windows: `build_instalador.bat` (requer PyInstaller e Inno Setup).

## Estrutura

| Pasta / arquivo | Conteúdo |
|---|---|
| `easyfeet_main.py` | Entrada da aplicação |
| `easyfeet/` | Núcleo: interface, banco, modelos, regras, PDFs, navicular |
| `easyfeet_markers/`, `marcador_plantar/`, `marcador_pontos/` | Módulo de marcadores (linhas e pontos) |
| `menu-config-v2.json` | Menu e permissões por perfil |
| `scripts/`, `tests/` | Instalador, testes e utilitários |
| `MDs/` | Documentação do produto |
| `Imagens/` | Logotipo, telas, réguas de calibração e exemplos fictícios |

## Próximos passos

- Fotos do teste do navicular (sentado e em pé) ligadas à linha do tempo
- Modos B e C do navicular (queda relativa e ajuste pelo comprimento do pé)
- Comparação da evolução entre momentos clínicos
- Prova de conceito web (backend + PostgreSQL)

---

Autor: **Flávio Ferro** · [LinkedIn](https://www.linkedin.com/in/ffcsffcs)
