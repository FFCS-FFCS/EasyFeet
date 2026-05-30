# EasyFeet — Versionamento local (sem GitHub)

**Versão atual do produto:** v1.0.0 (`easyfeet/version.py`)  
**Pasta oficial:** `C:\Users\flavi\OneDrive\Documentos\Ideias_Projetos\Cursor_Projetos\EasyFeet`

Este guia explica como **guardar**, **listar**, **comparar**, **voltar** e **executar** versões anteriores **sem GitHub** — só no seu PC / OneDrive.

---

## Duas formas de backup (use as duas)

| Método | O que guarda | Onde fica | Melhor para |
|--------|--------------|-----------|-------------|
| **Git local** | Histórico de commits + **tags** (`v1.0.0`) | Pasta oculta `.git` | Comparar código, voltar ficheiros, ver o que mudou |
| **Snapshot ZIP** | Cópia do projeto (código + docs) | `snapshots/EasyFeet_v1.0.0_YYYY-MM-DD.zip` | Executar versão antiga noutra pasta, backup “foto” |

**Importante:** `data/` (pacientes, `easyfeet.db`) **não entra** no Git nem no ZIP — são dados do seu dia a dia. O código evolui; os dados ficam na pasta `data/` actual.

---

## Atalhos na raiz do projeto

| Ficheiro | O que faz |
|----------|-----------|
| **`ListarVersoes.bat`** | Mostra tags Git e ZIPs em `snapshots/` |
| **`CriarSnapshot.bat`** | Gera ZIP em `snapshots/` (só código, sem `data/`) |
| **`MarcarVersao.bat`** | Commit + tag Git + ZIP (use ao fechar uma versão, ex. v1.1.0) |

---

## Rotina recomendada

### Ao fechar uma versão (ex.: v1.0.0 → v1.1.0)

1. Actualize `easyfeet/version.py` se quiser mudar o número no rodapé do app.
2. Duplo clique em **`MarcarVersao.bat`**.
3. Indique a versão (ex. `v1.1.0`) e confirme o commit.
4. Opcional: copie o ZIP gerado para outro sítio no OneDrive (backup extra).

### Entre versões (trabalho normal)

- O Git regista commits quando pedir ou quando usar `MarcarVersao.bat`.
- Antes de mudanças grandes, pode usar só **`CriarSnapshot.bat`** (ZIP rápido, sem tag).

---

## Como executar a versão 1.0 (ou outra)

### Opção A — Pasta separada (mais simples, mais segura)

1. Abra `snapshots/` e descompacte `EasyFeet_v1.0.0_*.zip` para uma pasta **irmã**, por exemplo:  
   `...\Cursor_Projetos\EasyFeet_v1.0.0\`
2. Nessa pasta: `pip install -r requirements.txt` (uma vez).
3. Duplo clique em **`EF.bat`** nessa pasta.
4. A pasta **`data/`** pode ser a mesma da versão actual (copie de `EasyFeet\data\` se quiser os mesmos pacientes de teste) ou deixe vazia para começar do zero.

Assim a versão **actual** em `EasyFeet\` continua a evoluir e a v1.0 fica intacta noutra pasta.

### Opção B — Git (mesma pasta, troca de código)

No PowerShell, na raiz do projeto:

```powershell
cd "C:\Users\flavi\OneDrive\Documentos\Ideias_Projetos\Cursor_Projetos\EasyFeet"
git checkout v1.0.0
# Executar EF.bat normalmente
```

Para **voltar ao trabalho actual**:

```powershell
git checkout master
```

**Atenção:** `data/` não muda com o checkout — só o código. Isso é normalmente o que se quer.

---

## Como comparar versões

### No PowerShell (Git)

```powershell
# Resumo do que mudou desde v1.0.0
git log v1.0.0..HEAD --oneline

# Diferenças de um ficheiro
git diff v1.0.0 -- easyfeet/gui.py

# Diferenças de todo o projecto
git diff v1.0.0
```

### Ver um ficheiro como era na v1.0.0 (sem mudar a pasta)

```powershell
git show v1.0.0:easyfeet/gui.py
```

---

## O que pedir ao Cursor (copiar e colar)

Use estes textos no chat do Cursor, na pasta **EasyFeet** (OneDrive):

| Objetivo | Pedido sugerido |
|----------|-----------------|
| **Executar / abrir v1.0** | *«Quero trabalhar na versão v1.0.0 do EasyFeet. Usa a tag Git `v1.0.0` ou o ZIP em `snapshots/` e diz-me como correr o EF.bat nessa versão.»* |
| **Comparar com v1.0** | *«Compara o código actual com a tag `v1.0.0` e resume o que mudou nos módulos X e Y.»* |
| **Ver diff de um ficheiro** | *«Mostra o diff de `easyfeet/gui.py` entre v1.0.0 e o código actual.»* |
| **Restaurar um ficheiro** | *«Restaura `easyfeet/gui.py` como estava na tag v1.0.0.»* |
| **Voltar tudo à v1.0** | *«Quero voltar o projecto inteiro à tag v1.0.0 (git checkout). Confirma os passos e avisa sobre data/.»* |
| **Criar nova versão** | *«Prepare a versão v1.1.0: actualize version.py se fizer sentido, e oriente-me a correr MarcarVersao.bat.»* |
| **Listar versões** | *«Lista as tags Git e os ZIPs em snapshots/ deste projecto.»* |

O assistente pode usar `git tag`, `git diff`, `git checkout` e a pasta `snapshots/` — **não precisa de GitHub**.

---

## Quando tiver GitHub (futuro)

O histórico local continua válido. Bastará:

```powershell
git remote add origin https://github.com/SEU_USER/EasyFeet.git
git push -u origin master
git push origin --tags
```

Até lá, **Git local + ZIP + OneDrive** chegam para backup e rollback.

---

## Versões registadas neste projecto

| Versão | Tag Git | Snapshot ZIP | Notas |
|--------|---------|--------------|-------|
| v1.0.0 | `v1.0.0` | `snapshots/EasyFeet_v1.0.0_*.zip` | Fase 2 marcadores validada; baseline local |

*(Actualize esta tabela ao marcar v1.1.0, v1.2.0, etc.)*

---

## Perguntas frequentes

**Perdi o `.git`?**  
Use o ZIP em `snapshots/` — é o plano B.

**O ZIP inclui pacientes?**  
Não, de propósito. Copie `data/` manualmente se precisar na versão antiga.

**OneDrive apaga versões?**  
OneDrive guarda histórico de ficheiros; manter ZIPs em `snapshots/` ou noutra pasta OneDrive dá redundância.

**Preciso instalar Git?**  
Sim, para tags e diff: [Git for Windows](https://git-scm.com/download/win). Os `.bat` avisam se o Git não estiver no PATH.

---

*Documento criado em 2026-05-30. Referência rápida: **versionamento-local-easyfeet.md**.*
