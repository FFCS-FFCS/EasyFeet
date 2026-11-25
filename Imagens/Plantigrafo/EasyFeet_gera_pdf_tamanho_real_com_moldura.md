# EasyFeet — Geração de PDF em tamanho real com moldura

Este arquivo descreve o procedimento para gerar um **PDF em tamanho real** a partir de uma imagem de pé, incluindo uma **moldura da área útil** para facilitar a conferência manual do comprimento e da largura após a impressão.

O objetivo é receber:
- **1 imagem** contendo a impressão / silhueta / marca plantar de um pé;
- **1 nome-base** para o arquivo de saída;
- **1 comprimento-alvo em cm**;
- **1 largura esperada em cm**;
- **opcionalmente 1 fator de correção de impressão**.

A saída deve ser:
- **1 PDF em tamanho real com moldura**, pronto para impressão em **100% / tamanho real / sem ajustar**;
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
8. Desenhar uma **moldura visível e imprimível** em volta da área útil do pé.

---

## 2. Entradas esperadas

Sempre devem ser fornecidos:

- **arquivo de imagem** do pé (normalmente `.png`);
- **nome-base para o PDF**, sem extensão;
- **comprimento-alvo em cm**, por exemplo: `26,5`;
- **largura esperada em cm**, por exemplo: `10,5`.

Opcionalmente, pode ser fornecido:

- **fator de correção de impressão**, por exemplo: `1,006456513482719`.

---

## 3. Regra de medição

### 3.1 Comprimento

O comprimento do pé deve ser medido **somente na área útil do pé**:

- do **ponto escuro superior**;
- até o **ponto escuro inferior**.

### 3.2 Largura

A largura do pé deve ser medida **somente na área útil do pé**:

- do **ponto escuro mais à esquerda**;
- até o **ponto escuro mais à direita**.

### 3.3 Proporção

A imagem deve ser escalada usando o **comprimento** como referência, **sem alargar nem estreitar artificialmente o pé**.

Isto significa:

- o comprimento final será exatamente o valor solicitado;
- a largura final será a largura proporcional resultante.

---

## 4. Regra de escala

Se o usuário informar:

- comprimento-alvo = `26,0 cm`;
- largura esperada = `10,5 cm`;

então o processo deve ser:

1. detectar a área útil do pé;
2. medir largura e altura em pixels da área útil;
3. fixar a **altura final** em `26,0 cm`;
4. calcular a **largura final proporcional**, sem distorção;
5. informar a diferença entre a largura final proporcional e a largura esperada (`10,5 cm`).

---

## 5. Fator de correção de impressão (opcional)

Este parâmetro existe para compensar pequenas diferenças sistemáticas observadas na impressão física.

### 5.1 Quando usar

Use o fator quando você já tiver medido a impressão anterior com régua e identificado que o tamanho físico saiu ligeiramente menor ou maior do que o esperado.

Exemplo:

- comprimento desejado = `26,5 cm`;
- comprimento medido na impressão = `26,33 cm`.

Fator calculado:

`26,5 / 26,33 = 1,006456513482719`

### 5.2 Como aplicar

Se o usuário fornecer o fator, ele deve ser aplicado **ao tamanho final já calculado**, **sem distorcer a imagem**.

Ou seja:

- primeiro calcular a imagem proporcional usando o comprimento-alvo como referência;
- depois multiplicar **comprimento e largura finais** pelo fator;
- aplicar o mesmo fator à moldura.

### 5.3 Regra importante

O fator deve ser aplicado **uniformemente nos dois eixos**.

Isso significa:

- se aumentar o comprimento, a largura também deve aumentar proporcionalmente;
- a imagem **não pode ser distorcida**.

### 5.4 Se o fator não for fornecido

Se o usuário não informar fator, assumir:

`fator = 1,0`

---

## 6. Regras de saída

### 6.1 PDF

Gerar um PDF em folha A4, com a imagem do pé em **tamanho real**, respeitando a escala calculada.

A imagem do pé deve ser inserida no PDF usando:

- o **comprimento final exato** solicitado, ou corrigido pelo fator, se houver;
- a **largura proporcional resultante**, também corrigida pelo fator, se houver;
- sem distorção.

### 6.2 Moldura

Desenhar uma moldura retangular em volta da área útil do pé.

Requisitos da moldura:

- linha fina, porém imprimível;
- suficientemente visível para medição manual;
- deve acompanhar exatamente a área útil escalada do pé;
- se houver fator, a moldura também deve receber a mesma correção.

### 6.3 Nome do PDF

O nome do PDF deve seguir exatamente este padrão:

`EasyFeet_[nome-base]_[comprimento]_x_[largura]_Com_Moldura.pdf`

#### Regra para o nome

- usar o **nome-base informado pelo usuário**;
- o comprimento e a largura no nome devem estar em **décimos de milímetro**, **sem separador decimal**;
- por ser um PDF com moldura, o nome deve terminar obrigatoriamente com o sufixo **`_Com_Moldura.pdf`**.

### Conversão para o nome

- `26,0 cm` = `260,0 mm` = `2600` em décimos de milímetro;
- `10,03 cm` = `100,3 mm` = `1003` em décimos de milímetro.

### Exemplo de saída

Se o nome-base for:

`2-Pé_direito_20260507`

e a largura proporcional final calculada for `10,03 cm`, então o PDF final deve se chamar:

`EasyFeet_2-Pé_direito_20260507_2600_x_1003_Com_Moldura.pdf`

> Observação: se houver fator e ele alterar o tamanho final, o nome do PDF deve refletir as **dimensões finais efetivamente usadas no PDF**, sempre mantendo o sufixo `_Com_Moldura`.

---

## 7. Análise textual obrigatória

Além do PDF, a resposta deve informar claramente:

1. qual foi a área útil detectada do pé;
2. qual foi o comprimento final aplicado;
3. qual foi a largura proporcional resultante;
4. qual foi a largura esperada informada pelo usuário;
5. se foi usado fator de correção;
6. qual foi o fator usado;
7. se a largura resultante ficou:
   - **abaixo** da esperada;
   - **igual** à esperada;
   - **acima** da esperada.

### Exemplo de análise

- comprimento final aplicado: `26,00 cm`;
- largura proporcional resultante: `10,03 cm`;
- largura esperada: `10,50 cm`;
- fator usado: `1,0`;
- conclusão: a largura ficou **0,47 cm abaixo** da esperada.

---

## 8. Configuração de impressão esperada

O PDF deve ser pensado para impressão com:

- **escala 100%**;
- **tamanho real**;
- **sem ajustar à página**;
- **sem preencher página**;
- **sem reduzir para área imprimível**.

---

## 9. Critérios de aceitação

A saída só será considerada correta se:

1. a área útil do pé for usada, e não a imagem inteira;
2. o comprimento final do pé no PDF corresponder exatamente ao valor solicitado, ou ao valor corrigido pelo fator;
3. a imagem não for distorcida;
4. a largura final for calculada proporcionalmente;
5. a largura final for comparada com a largura esperada;
6. a moldura acompanhar exatamente a área útil escalada;
7. o PDF for gerado em tamanho real;
8. o nome do PDF seguir o padrão exigido;
9. o nome usar comprimento e largura em **décimos de milímetro**;
10. o nome do PDF terminar com **`_Com_Moldura.pdf`**;
11. a resposta incluir a análise textual.

---

## 10. Comando recomendado para uso

### Versão curta

**Leia o `EasyFeet_gera_pdf_tamanho_real_com_moldura.md` para o arquivo anexo, nome `2-Pé_direito_20260507`, com comprimento `26,5 cm`, largura esperada `10,5 cm` e use o fator `1,006456513482719`.**

### Versão sem fator

**Leia o `EasyFeet_gera_pdf_tamanho_real_com_moldura.md` para o arquivo anexo, nome `2-Pé_direito_20260507`, com comprimento `26,0 cm` e largura esperada `10,5 cm`.**

---

## 11. Observação final

Este processo prioriza a **precisão do comprimento**.

A largura **não deve ser forçada**. Ela deve ser apenas:

- calculada proporcionalmente;
- analisada em relação à largura esperada.

O fator de correção existe apenas para compensar diferenças físicas sistemáticas observadas na impressão, mantendo a proporção original e sem distorção.

Por se tratar da versão com moldura, todo PDF gerado por este protocolo deve terminar com o sufixo **`_Com_Moldura.pdf`**.
