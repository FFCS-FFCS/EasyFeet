# EasyFeet - Timesheet (Indice e Consolidado)

Data da consolidacao: 2026-05-28 (encerramento do dia, UTC-3)
Regra de calculo ativa: pausas > 30 min nao contam (criterio intermediario)
Fuso horario de referencia: UTC-3

## 1) Janela consolidada do projeto

- Periodo consolidado: 2026-05-07 10:32 ate 2026-05-28 02:42 (UTC-3) — extremos a partir dos timesheets diarios.
- Janela total (decorrido, soma dos dias na tabela): 55.78 h
- Tempo total ativo estimado: 22.83 h
- Dias com atividade: 5
- Arquivos diarios consolidados: 4 (+ folha 2026-05-28)

## 2) Lancamentos tabulares consolidados (base para graficos)

| data       | inicio | fim   | criterio_pausa_min | horas_ativas | horas_decorridas | sessoes | origem_md                                   |
|------------|--------|-------|--------------------|--------------|------------------|---------|---------------------------------------------|
| 2026-05-07 | 10:32  | 23:59 | 30                 | 4.68         | 13.45            | 1       | 2026-05-08-timesheet-horas-trabalhadas.md |
| 2026-05-08 | 00:00  | 20:08 | 30                 | 7.65         | 20.13            | 1       | 2026-05-08-timesheet-horas-trabalhadas.md |
| 2026-05-09 | 10:00  | 20:30 | 30                 | 3.25         | 10.50            | 1       | 2026-05-09-timesheet-horas-trabalhadas.md |
| 2026-05-25 | 14:00  | 23:45 | 30                 | 5.50         | 9.75             | 1       | 2026-05-25-timesheet-horas-trabalhadas.md |
| 2026-05-28 | 00:45  | 02:42 | 30                 | 1.75         | 1.95             | 1       | 2026-05-28-timesheet-horas-trabalhadas.md |

## 3) Totais acumulados (dia, semana, mes, geral)

### Diario

| data       | horas_ativas | horas_decorridas |
|------------|--------------|------------------|
| 2026-05-07 | 4.68         | 13.45            |
| 2026-05-08 | 7.65         | 20.13            |
| 2026-05-09 | 3.25         | 10.50            |
| 2026-05-25 | 5.50         | 9.75             |
| 2026-05-28 | 1.75         | 1.95             |

### Semanal (ISO week)

| ano_semana | horas_ativas | horas_decorridas |
|------------|--------------|------------------|
| 2026-W19   | 12.33        | 33.58            |
| 2026-W21   | 5.50         | 9.75             |
| 2026-W22   | 5.00         | 12.45            |

Nota: 2026-05-08 cruza meia-noite; a folha `2026-05-08-timesheet` atribui 7,65 h ativas ao dia 08 e 4,68 ao dia 07 — semana ISO pode sobrepor dias; usar secao 2 para graficos por data.

### Mensal

| ano_mes | horas_ativas | horas_decorridas |
|---------|--------------|------------------|
| 2026-05 | 22.83        | 55.78            |

### Geral

- Total horas ativas no projeto: 22.83
- Total horas decorridas no periodo consolidado: 55.78
- Registros diarios acumulados: 5

## 4) Observacoes e protocolo de atualizacao

- Este arquivo deve ser sobrescrito sempre que houver novo timesheet diario.
- Para gerar grafico (dia/semana/mes), use preferencialmente a tabela da secao 2.
- Os campos da secao 2 foram padronizados para facilitar exportacao para CSV/Excel/Power BI.
- O arquivo `Documentos de Apoio/TimeSheet/timesheet-consolidado.csv` deve ser atualizado junto com este consolidado.
- Gatilhos validos: "atualizar timesheet", "sincronizar horas trabalhadas", "encerrar o dia: atualizar timesheet e o gerenciador de MDs".
- Ao atualizar: ler todos os `*-timesheet-horas-trabalhadas.md`, recalcular tabelas, atualizar `Documentos de Apoio/TimeSheet/timesheet-consolidado.csv` e manter o total geral ao final desta secao.
- Formato CSV Brasil: separador `;` e casas decimais com `,` (vírgula).

## Indice de arquivos de timesheet diario

- `2026-05-08-timesheet-horas-trabalhadas.md`
- `2026-05-09-timesheet-horas-trabalhadas.md`
- `2026-05-25-timesheet-horas-trabalhadas.md`
- `2026-05-28-timesheet-horas-trabalhadas.md`
