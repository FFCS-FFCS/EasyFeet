# EasyFeet — Instruções para geração das réguas A4 com borda

Este documento descreve como gerar dois PDFs vetoriais A4 para o projeto EasyFeet, na variação **com borda**.

Nesta variação, a contagem:
- da régua horizontal **não começa na borda física da folha**;
- da régua vertical **não começa na borda física da folha**.

Em vez disso, os zeros dos eixos devem ficar **dentro de uma área imprimível segura**, criando uma borda interna útil.

## Arquivos finais obrigatórios

1. `EasyFeet_Regua_A4_somente_reguas_com_Borda.pdf`
2. `EasyFeet_Regua_A4_conferencia_calibracao_com_Borda.pdf`

## Tamanho da página

Usar folha A4 em orientação retrato:
- largura: 21,0 cm
- altura: 29,7 cm

O PDF deve ser vetorial.

## Configuração de impressão esperada

Imprimir com:
- escala 100%
- tamanho real
- sem ajustar à página
- sem preencher página
- sem reduzir para área imprimível

## Régua horizontal superior

A régua horizontal deve:
- começar dentro da área imprimível, com uma borda interna à esquerda;
- medir de `0` até `20 cm`;
- ter marcações a cada `0,5 cm`;
- destacar `2,5 cm` e `5 cm`;
- exibir os rótulos: `0`, `2,5`, `5`, `7,5`, `10`, `12,5`, `15`, `17,5`, `20`;
- ter a linha da régua um pouco abaixo do topo da folha, para não cortar na impressão;
- ter os números mais para dentro da página;
- manter o `20` levemente afastado do canto direito.

## Régua vertical direita

A régua vertical deve:
- começar dentro da área imprimível, com uma borda interna superior;
- medir até `27,5 cm`;
- ficar deslocada um pouco para a esquerda em relação à borda direita para evitar corte;
- ter marcações a cada `0,5 cm`;
- destacar `2,5 cm` e `5 cm`;
- exibir os rótulos:
  `2,5`, `5`, `7,5`, `10`, `12,5`, `15`, `17,5`, `20`, `22,5`, `25`, `27,5`.

## Regra do canto superior direito

Para manter o canto limpo:
- manter o `20` da régua horizontal;
- manter o `cm` da régua horizontal;
- **não exibir** o `0` da régua vertical;
- **não exibir** o `cm` vertical no canto superior.

## Versão somente réguas

Arquivo:
`EasyFeet_Regua_A4_somente_reguas_com_Borda.pdf`

Conteúdo:
- régua horizontal superior;
- régua vertical direita;
- sem quadrado de calibração;
- sem barra de conferência;
- sem textos extras.

## Versão conferência/calibração

Arquivo:
`EasyFeet_Regua_A4_conferencia_calibracao_com_Borda.pdf`

Conteúdo:
- mesma régua horizontal;
- mesma régua vertical;
- quadrado de calibração `5 x 5 cm`;
- barra de conferência de `10 cm`;
- nota de impressão.

## Quadrado de calibração

O quadrado deve:
- ter exatamente `5 cm x 5 cm`;
- ficar deslocado um pouco para a direita;
- conter cotas `5 cm` na parte superior e na lateral;
- conter o texto interno:
  - `Quadrado de`
  - `calibracao 5 x 5 cm`

## Barra de conferência

A barra deve:
- ter exatamente `10 cm`;
- ficar acima da área de corte da impressora;
- conter a legenda `Barra de conferencia: 10 cm`.

## Rodapé

Na versão de conferência, incluir:
- `Folha A4: 21,0 x 29,7 cm`
- `Imprimir em escala 100% / tamanho real / sem ajustar`

## Critérios de aceitação

A saída estará correta se:
1. os arquivos tiverem os nomes exatos;
2. a folha for A4 real;
3. os zeros dos eixos ficarem dentro de uma área imprimível segura;
4. a linha horizontal não ficar cortada na impressão;
5. os números superiores não ficarem cortados;
6. a régua vertical não ficar cortada;
7. o canto superior direito não ficar embolado;
8. a versão de calibração tiver quadrado 5 x 5 cm e barra 10 cm;
9. o quadrado e seus rótulos não forem cortados.

## Observação

Esta versão é diferente da `sem_Borda`.

Na `com_Borda`, a medição começa a partir de uma borda interna criada no PDF.

Na `sem_Borda`, a medição começa a partir da borda física da folha.
