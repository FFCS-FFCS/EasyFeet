# EasyFeet — Geração de PDF em tamanho real a partir de imagem de pé

Este arquivo descreve o procedimento para gerar um **PDF em tamanho real** a partir de uma imagem de pé.

O objetivo é receber:
- **1 imagem** contendo a impressão / silhueta / marca plantar de um pé;
- **1 comprimento-alvo em cm**;
- **1 largura esperada em cm**.

A saída deve ser:
- **1 PDF em tamanho real**, pronto para impressão em **100% / tamanho real / sem ajustar**;
- **1 análise curta**, informando a largura proporcional resultante e se ela ficou **abaixo**, **igual** ou **acima** da largura esperada.

---

## 1. Regra principal

A regra principal é:

1. Detectar **somente a área útil do pé** na imagem.
2. Considerar como área útil:
   - o ponto escuro mais alto até o ponto escuro mais baixo = **comprimento útil**;
   - o ponto escuro mais à esquerda até o ponto escuro mais à direita = **largura útil**.
3. **Não distorcer a imagem**.
4. Usar o **comprimento informado** como referência principal para a escala.
5. Escalar a imagem de forma proporcional, de modo que o comprimento útil do pé fique exatamente com o valor solicitado.
6. Calcular a largura proporcional resultante após a escala.
7. Comparar a largura resultante com a **largura esperada** informada pelo usuário.

---

## 2. Entradas esperadas

Sempre devem ser fornecidos:

- **arquivo de imagem** do pé (normalmente `.png`, mas a extensão deve ser desconsiderada no nome final);
- **comprimento-alvo em cm**, por exemplo: `27,0`;
- **largura esperada em cm**, por exemplo: `11,0`.

### Exemplo de entrada

Arquivo:
`pe esquerdo zezinho.png`

Parâmetros:
- comprimento-alvo = `27,0 cm`
- largura esperada = `11,0 cm`

---

## 3. Regra de medição

### 3.1 Comprimento
O comprimento do pé deve ser medido **somente na área útil do pé**:
- do **ponto escuro superior**
- até o **ponto escuro inferior**.

### 3.2 Largura
A largura do pé deve ser medida **somente na área útil do pé**:
- do **ponto escuro mais à esquerda**
- até o **ponto escuro mais à direita**.

### 3.3 Proporção
A imagem deve ser escalada usando o **comprimento** como referência, **sem alargar nem estreitar artificialmente o pé**.

Isto significa:
- o comprimento final será exatamente o valor solicitado;
- a largura final será a largura proporcional resultante.

---

## 4. Regra de escala

Se o usuário informar:
- comprimento-alvo = `27,0 cm`
- largura esperada = `11,0 cm`

então o processo deve ser:

1. detectar a área útil do pé;
2. medir largura e altura em pixels da área útil;
3. fixar a **altura final** em `27,0 cm`;
4. calcular a **largura final proporcional**, sem distorção;
5. informar a diferença entre a largura final proporcional e a largura esperada (`11,0 cm`).

---

## 5. Regras de saída

### 5.1 PDF
Gerar um PDF em folha A4, com a imagem do pé em **tamanho real**, respeitando a escala calculada.

A imagem do pé deve ser inserida no PDF usando:
- o **comprimento final exato** solicitado;
- a **largura proporcional resultante**;
- sem distorção.

### 5.2 Nome do PDF
O nome do PDF deve seguir exatamente este padrão:

`EasyFeet_[nome do arquivo sem extensão]_[comprimento]_x_[largura].pdf`

#### Regra para o nome
- usar o **nome original do arquivo**, sem a extensão;
- manter o nome do arquivo como referência principal;
- o comprimento e a largura no nome devem estar em **décimos de milímetro**, **sem separador decimal**.

### Conversão para o nome
- `27,0 cm` = `270,0 mm` = `2700` em décimos de milímetro;
- `10,73 cm` = `107,3 mm` = `1073` em décimos de milímetro.

### Exemplo de saída
Se o arquivo de entrada for:
`pe esquerdo zezinho.png`

e a largura proporcional final calculada for `10,73 cm`, então o PDF final deve se chamar:

`EasyFeet_pe esquerdo zezinho_2700_x_1073.pdf`

---

## 6. Análise textual obrigatória

Além do PDF, a resposta deve informar claramente:

1. qual foi a área útil detectada do pé;
2. qual foi o comprimento final aplicado;
3. qual foi a largura proporcional resultante;
4. qual foi a largura esperada informada pelo usuário;
5. se a largura resultante ficou:
   - **abaixo** da esperada;
   - **igual** à esperada;
   - **acima** da esperada.

### Exemplo de análise
- comprimento final aplicado: `27,00 cm`
- largura proporcional resultante: `10,73 cm`
- largura esperada: `11,00 cm`
- conclusão: a largura ficou **0,27 cm abaixo** da esperada.

---

## 7. Configuração de impressão esperada

O PDF deve ser pensado para impressão com:
- **escala 100%**;
- **tamanho real**;
- **sem ajustar à página**;
- **sem preencher página**;
- **sem reduzir para área imprimível**.

---

## 8. Critérios de aceitação

A saída só será considerada correta se:

1. a área útil do pé for usada, e não a imagem inteira;
2. o comprimento final do pé no PDF corresponder exatamente ao valor solicitado;
3. a imagem não for distorcida;
4. a largura final for calculada proporcionalmente;
5. a largura final for comparada com a largura esperada;
6. o PDF for gerado em tamanho real;
7. o nome do PDF seguir o padrão exigido;
8. o nome usar comprimento e largura em **décimos de milímetro**;
9. a resposta incluir a análise textual.

---

## 9. Comando recomendado para uso

Quando este MD existir, o pedido recomendado será algo como:

**Leia o arquivo `EasyFeet_gera_pdf_tamanho_real.md` e gere um PDF em tamanho real para a imagem anexa `pe esquerdo zezinho.png`, usando comprimento-alvo de `27,0 cm` e largura esperada de `11,0 cm`. Use o comprimento como referência, não distorça a imagem, calcule a largura proporcional final, faça a análise da largura obtida e gere o arquivo de saída no formato `EasyFeet_[nome do arquivo sem extensão]_[comprimento em décimos de milímetro]_x_[largura final em décimos de milímetro].pdf`.**

### Versão curta do comando

**Leia o `EasyFeet_gera_pdf_tamanho_real.md` para o arquivo anexo `pe esquerdo zezinho.png`, com comprimento `27,0 cm` e largura esperada `11,0 cm`.**

---

## 10. Observação final

Este processo prioriza a **precisão do comprimento**, pois ele é a referência principal.

A largura **não deve ser forçada**. Ela deve ser apenas:
- calculada proporcionalmente;
- analisada em relação à largura esperada.

Isso evita distorção e mantém a fidelidade do pé original.
