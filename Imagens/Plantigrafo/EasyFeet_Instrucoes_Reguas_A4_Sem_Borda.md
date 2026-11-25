# EasyFeet — Instruções para geração das réguas A4 sem borda

Este documento descreve como gerar dois PDFs vetoriais A4 para o projeto EasyFeet, na variação **sem borda**.

Nesta variação, a contagem:
- da régua horizontal começa na **borda esquerda física da folha**;
- da régua vertical começa no **topo físico da folha**.

Assim, ao encostar o zero de uma régua real na borda do papel, a marca de 5 cm deve coincidir com a marca impressa de 5 cm, desde que o PDF seja impresso em escala real.

## Arquivos finais obrigatórios

1. `EasyFeet_Regua_A4_somente_reguas_sem_Borda.pdf`
2. `EasyFeet_Regua_A4_conferencia_calibracao_sem_Borda.pdf`

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
- começar em `x = 0`, isto é, na borda esquerda da folha;
- medir de `0` até `20 cm`;
- ter marcações a cada `0,5 cm`;
- destacar `2,5 cm` e `5 cm`;
- exibir os rótulos: `0`, `2,5`, `5`, `7,5`, `10`, `12,5`, `15`, `17,5`, `20`;
- ter a **linha da régua um pouco mais abaixo do topo da folha**, para não cortar na impressão;
- ter os números mais para dentro da página;
- manter o `20` levemente afastado do canto direito.

## Régua vertical direita

A régua vertical deve:
- começar a contagem no topo físico da folha;
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
`EasyFeet_Regua_A4_somente_reguas_sem_Borda.pdf`

Conteúdo:
- régua horizontal superior;
- régua vertical direita;
- sem quadrado de calibração;
- sem barra de conferência;
- sem textos extras.

## Versão conferência/calibração

Arquivo:
`EasyFeet_Regua_A4_conferencia_calibracao_sem_Borda.pdf`

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
3. a régua horizontal começar na borda esquerda da folha;
4. a marca de 5 cm horizontal coincidir com régua física desde a borda do papel;
5. a marca de 5 cm vertical coincidir com régua física desde o topo do papel;
6. a linha horizontal não ficar cortada na impressão;
7. os números superiores não ficarem cortados;
8. o canto superior direito não ficar embolado;
9. a versão de calibração tiver quadrado 5 x 5 cm e barra 10 cm;
10. o quadrado e seus rótulos não forem cortados.

## Observação

Esta versão é diferente da `com_Borda`.

Na `com_Borda`, a medição começa a partir de uma borda interna criada no PDF.

Na `sem_Borda`, a medição começa a partir da borda física da folha.
