# EasyFeet — Instruções para geração de régua em papel Ofício com borda (V2)

Este documento descreve como gerar um PDF vetorial para imprimir **somente réguas** usando o tamanho de papel **Ofício** e a variação **com borda**.

Nesta variação, a contagem das réguas **não começa na borda física da folha**.  
Os zeros dos eixos ficam dentro de uma área imprimível segura.

---

## 1. Nome do arquivo de instruções

Este arquivo deve se chamar:

`EasyFeet_Regua_Oficio_somente_reguas_com_Borda_v2.md`

---

## 2. Objetivo

Gerar um PDF com:

- régua horizontal superior;
- régua vertical à direita;
- sem quadrado de calibração;
- sem barra de conferência;
- sem elementos extras.

O objetivo é testar a impressão em papel **Ofício**, considerando que a impressora interpreta o tamanho como:

- largura: `215,9 mm`;
- altura: `355,6 mm`.

---

## 3. Tamanho do papel

Usar página com:

- largura: `215,9 mm`;
- altura: `355,6 mm`;
- orientação: retrato.

Esse tamanho corresponde ao papel que a impressora está reconhecendo como **Ofício**.

---

## 4. Regra especial deste teste

A régua vertical da direita **não deve passar do 17,0 cm da régua horizontal**.

Isso significa:

- a régua horizontal começa no zero;
- a régua vertical deve cruzar a régua horizontal **exatamente na marca de 17,0 cm**;
- portanto, a linha-base da régua vertical deve ficar posicionada a **170 mm do zero da régua horizontal**.

Em outras palavras:

- a régua horizontal útil deve ir de `0` até `17,0 cm`;
- a régua vertical deve começar nesse ponto de cruzamento.

---

## 5. Configuração de impressão

Ao imprimir, usar sempre:

- escala `100%`;
- tamanho real;
- sem ajustar à página;
- sem preencher página;
- sem reduzir para área imprimível.

Não usar:

- ajustar à página;
- reduzir para caber;
- preencher página;
- centralização automática que altere a escala.

---

## 6. Margens internas sugeridas

Usar as seguintes margens:

- margem esquerda da régua horizontal: `4 mm`;
- margem superior da régua horizontal: `5 mm`;
- margem inferior: `3 mm`.

A posição da régua vertical deve ser determinada pela regra do item 4, isto é:

- `x da régua vertical = x do zero + 170 mm`.

---

## 7. Régua horizontal superior

A régua horizontal deve:

- começar dentro da área imprimível;
- ter a linha principal próxima ao topo, mas sem cortar;
- terminar exatamente em `17,0 cm`;
- ter marcações a cada `0,5 cm`;
- destacar marcações intermediárias a cada `2,5 cm`;
- destacar marcações principais a cada `5 cm`.

### Regra importante dos números superiores

Os **números da régua superior devem ficar abaixo da linha da régua**.

Motivo:
- evitar corte na impressão;
- repetir a solução que já funcionou nos testes anteriores.

Rótulos sugeridos:

`0`, `2,5`, `5`, `7,5`, `10`, `12,5`, `15`, `17`

O texto `cm` também deve ficar **abaixo da linha**, perto do lado direito, mas sem embolar com a régua vertical.

---

## 8. Régua vertical direita

A régua vertical deve:

- começar no ponto em que cruza a régua horizontal no `17,0 cm`;
- seguir para baixo;
- ter marcações a cada `0,5 cm`;
- destacar marcações intermediárias a cada `2,5 cm`;
- destacar marcações principais a cada `5 cm`;
- não exibir o `0` no canto superior.

Rótulos sugeridos:

`2,5`, `5`, `7,5`, `10`, `12,5`, `15`, `17,5`, `20`, `22,5`, `25`, `27,5`, `30`, `32,5`

Dependendo da área útil, a régua pode passar um pouco disso.

---

## 9. Regra do canto superior direito

Para manter o canto limpo:

- manter os números da régua superior abaixo da linha;
- manter o `cm` da régua horizontal abaixo da linha;
- não exibir o `0` da régua vertical;
- não exibir o `cm` vertical;
- evitar sobreposição entre textos.

---

## 10. Nome do PDF gerado

O PDF final deve se chamar exatamente:

`EasyFeet_Regua_OFICIO_somente_reguas_com_Borda_v2.pdf`

---

## 11. Critérios de aceitação

A saída estará correta se:

1. o PDF for vetorial;
2. o tamanho da página for `215,9 x 355,6 mm`;
3. a régua horizontal começar dentro da área imprimível;
4. os números da régua horizontal ficarem abaixo da linha e não forem cortados;
5. a régua vertical cruzar a régua horizontal exatamente no `17,0 cm`;
6. os números da régua vertical não forem cortados;
7. o canto superior direito não ficar embolado;
8. a impressão for feita em escala `100%`;
9. o PDF tiver o nome correto.

---

## 12. Comando recomendado para uso

Use:

`Leia o EasyFeet_Regua_Oficio_somente_reguas_com_Borda_v2.md e gere o PDF com as réguas em papel Ofício, fazendo a régua vertical cruzar a régua horizontal no 17,0 cm.`

---

## 13. Observação final

Este teste existe porque a impressora reconhece **Ofício = 215,9 x 355,6 mm**, mas a folha física usada pode ser mais estreita.

Nesta V2, a prioridade é garantir que a régua vertical cruze a horizontal exatamente no **17,0 cm**.
