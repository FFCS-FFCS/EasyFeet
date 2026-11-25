# EasyFeet — Instruções para geração de régua para folha de plantígrafo com borda

Este documento descreve como gerar um PDF vetorial para imprimir **réguas diretamente na folha do plantígrafo**, usando a variação **com borda**.

Nesta variação, a contagem das réguas **não começa na borda física da folha**.  
Os zeros dos eixos devem ficar dentro de uma área imprimível segura, criando uma borda interna.

---

## 1. Nome do arquivo final de instruções

Este arquivo deve se chamar:

`EasyFeet_Regua_PLANTIGRAFO_somente_reguas_com_Borda.md`

---

## 2. Objetivo

Gerar um PDF com réguas para uma folha de plantígrafo, para permitir conferência manual de medidas da impressão plantar.

O PDF deve ser usado para imprimir diretamente na folha física do plantígrafo, respeitando o tamanho real da folha.

---

## 3. Medidas iniciais da folha do plantígrafo

Medidas informadas pelo usuário:

- largura aproximada: `18,3 cm`;
- comprimento aproximado: `36,8 cm`.

Em milímetros:

- largura aproximada: `183 mm`;
- comprimento aproximado: `368 mm`.

Essas medidas devem ser tratadas como **estimativa inicial**.

---

## 4. Tamanho de página recomendado para o PDF

### Tamanho ideal

Se a impressora e o driver aceitarem tamanho personalizado, gerar o PDF com:

- largura: `183 mm`;
- altura: `368 mm`;
- orientação: retrato.

Nome técnico sugerido para o tamanho personalizado:

`Plantigrafo_183x368mm`

### Tamanho alternativo por limitação da impressora

Se a impressora não aceitar `368 mm` de comprimento, usar:

- largura: `183 mm`;
- altura: `355 mm`.

Nome técnico sugerido:

`Plantigrafo_183x355mm`

---

## 5. Configuração de impressora

Ao imprimir, usar sempre:

- escala `100%`;
- tamanho real;
- sem ajustar à página;
- sem preencher página;
- sem reduzir para área imprimível.

Não usar opções como:

- ajustar à página;
- reduzir para caber;
- preencher página;
- centralização automática que altere a escala.

---

## 6. Observação sobre a HP Ink Tank Wireless 410 series

A impressora pode não aceitar oficialmente uma folha de `183 x 368 mm`, pois alguns modelos da série HP Ink Tank Wireless 410 informam tamanho personalizado máximo de aproximadamente `215 x 355 mm`.

Neste caso:

- `183 mm` de largura está dentro do limite;
- `368 mm` de comprimento pode ficar acima do limite;
- a impressão pode cortar a parte final da folha ou nem permitir selecionar esse tamanho.

Se o driver não aceitar `183 x 368 mm`, testar primeiro:

`183 x 355 mm`

---

## 7. Tamanhos prontos do driver

Se o driver só mostrar tamanhos prontos como A4, A5, Carta, Ofício, Executivo ou JIS, normalmente nenhum deles corresponde exatamente a `183 x 368 mm`.

Comparação aproximada:

- A4: `210 x 297 mm` — curto demais no comprimento;
- Carta: `216 x 279 mm` — curto demais no comprimento;
- Ofício/Legal: aproximadamente `216 x 355/356 mm` — mais próximo no comprimento, mas ainda diferente da folha real e mais largo que a folha;
- JIS Chou #2: `119 x 277 mm` — menor demais.

Portanto, para precisão, o ideal é usar **tamanho personalizado**.

> Se você acabou imprimindo em **Ofício/Legal**, isso pode explicar parte da diferença observada, porque o driver pode impor limites próprios ou cortar a área final do papel.

---

## 8. Tipo de régua

Gerar somente as réguas, sem quadrado de calibração e sem barra de conferência.

O PDF deve conter:

- régua horizontal superior;
- régua vertical direita;
- sem textos extras na parte inferior;
- sem elementos decorativos.

---

## 9. Régua horizontal superior

A régua horizontal deve:

- começar dentro da área imprimível, com margem interna segura;
- medir de `0` até, no máximo, a largura útil da folha;
- para folha de `183 mm`, recomenda-se medir até `17 cm` com folga segura;
- ter marcações a cada `0,5 cm`;
- destacar marcações intermediárias a cada `2,5 cm`;
- destacar marcações principais a cada `5 cm`.

### Regra importante dos números superiores

Os **números da régua superior devem ficar abaixo da linha da régua**, e não acima.

Motivo:
- evitar corte na impressão;
- manter legibilidade;
- repetir o padrão que já funcionou nas versões A4.

Rótulos sugeridos:

`0`, `2,5`, `5`, `7,5`, `10`, `12,5`, `15`, `17`

O texto `cm` também deve ficar **abaixo da linha**, próximo ao canto direito, mas sem embolar com a régua vertical.

---

## 10. Régua vertical direita

A régua vertical deve:

- começar dentro da área imprimível, com margem interna superior;
- ficar deslocada para a esquerda em relação à borda direita, evitando corte;
- medir até a maior medida útil segura;
- para folha de `355 mm` com borda interna, a área útil real da régua pode ficar em torno de `34,5 cm` a `34,7 cm`, e não `35 cm` completos;
- para folha de `368 mm`, a área útil será maior.

### Regra prática

- se a página for `183 x 355 mm`, não prometer `35 cm` completos na régua com borda;
- nesse cenário, o mais realista é chegar em torno de `34,5 cm`.

A régua deve:

- ter marcações a cada `0,5 cm`;
- destacar marcações intermediárias a cada `2,5 cm`;
- destacar marcações principais a cada `5 cm`.

Rótulos sugeridos para a versão `183 x 355 mm`:

`2,5`, `5`, `7,5`, `10`, `12,5`, `15`, `17,5`, `20`, `22,5`, `25`, `27,5`, `30`, `32,5`, `34,5`

Não exibir o `0` da régua vertical no canto superior, para evitar conflito visual com a régua horizontal.

---

## 11. Regra do canto superior direito

Para manter o canto limpo:

- manter o último número útil da régua horizontal, se houver espaço;
- colocar o `cm` da régua horizontal abaixo da linha, sem embolar;
- não exibir o `0` da régua vertical;
- não exibir o `cm` vertical no canto superior;
- evitar qualquer sobreposição entre rótulos.

---

## 12. Margens internas sugeridas

Como o objetivo é imprimir em uma folha física não padrão, usar margens internas seguras.

Sugestão ajustada:

- margem esquerda da régua horizontal: `4 mm`;
- margem superior da régua horizontal: `5 mm`;
- deslocamento da régua vertical em relação à borda direita: `6 mm`;
- margem inferior de segurança: `3 mm`.

Esses valores podem ser ajustados após o primeiro teste de impressão.

---

## 13. Nome do PDF gerado

O PDF final deve se chamar:

`EasyFeet_Regua_PLANTIGRAFO_somente_reguas_com_Borda.pdf`

Se forem geradas variações de tamanho, usar nomes complementares, por exemplo:

- `EasyFeet_Regua_PLANTIGRAFO_183x368_somente_reguas_com_Borda.pdf`
- `EasyFeet_Regua_PLANTIGRAFO_183x355_somente_reguas_com_Borda.pdf`

---

## 14. Critérios de aceitação

A saída estará correta se:

1. o PDF for vetorial;
2. o tamanho da página corresponder ao tamanho definido da folha do plantígrafo;
3. a régua horizontal começar dentro da área imprimível;
4. os **números da régua horizontal ficarem abaixo da linha** e não forem cortados;
5. a régua vertical começar dentro da área imprimível;
6. os números não forem cortados;
7. o canto superior direito não ficar embolado;
8. as marcas de `5 cm` e `10 cm` conferirem com uma régua física;
9. a impressão for feita em escala `100%`, sem ajuste automático;
10. o arquivo gerado tiver o nome correto.

---

## 15. Comando recomendado para uso

### Para folha medida em 18,3 x 36,8 cm

Use:

`Leia o EasyFeet_Regua_PLANTIGRAFO_somente_reguas_com_Borda.md e gere o PDF para folha de plantígrafo com largura 18,3 cm e comprimento 36,8 cm.`

### Para folha limitada pela impressora a 35,5 cm de comprimento

Use:

`Leia o EasyFeet_Regua_PLANTIGRAFO_somente_reguas_com_Borda.md e gere o PDF para folha de plantígrafo com largura 18,3 cm e comprimento 35,5 cm.`

---

## 16. Observação final

A folha do plantígrafo pode variar conforme o fabricante.

Não assumir que existe um tamanho universal.  
Sempre que possível, medir a folha real antes de gerar o PDF final.

Se a impressora não aceitar `183 x 368 mm`, o problema não está no PDF, e sim no limite físico/driver da impressora.
