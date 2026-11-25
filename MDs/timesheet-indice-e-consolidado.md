# EasyFeet - Timesheet (Indice e Consolidado)

Data da consolidacao: 2026-06-12 (folha diaria 2026-06-12 atualizada — 2 sessoes, UTC-3)
Regra de calculo **ativa (novas folhas a partir de 2026-05-30):** pausas **> 20 min** nao contam
Regra **legado (folhas ate 2026-05-28 inclusive):** pausas **> 30 min** nao contam — **nao recalcular** horas ja registradas
Fuso horario de referencia: UTC-3

## 1) Janela consolidada do projeto

- Periodo consolidado: 2026-05-07 10:32 ate 2026-06-12 14:00 (UTC-3) — extremos a partir dos timesheets diarios.
- Janela total (decorrido, soma dos dias na tabela): 88.11 h
- Tempo total ativo estimado: 43.33 h
- Dias com atividade: 8
- Arquivos diarios consolidados: 8

## 2) Lancamentos tabulares consolidados (base para graficos)

| data       | inicio | fim   | criterio_pausa_min | horas_ativas | horas_decorridas | sessoes | origem_md                                   |
|------------|--------|-------|--------------------|--------------|------------------|---------|---------------------------------------------|
| 2026-05-07 | 10:32  | 23:59 | 30                 | 4.68         | 13.45            | 1       | 2026-05-08-timesheet-horas-trabalhadas.md |
| 2026-05-08 | 00:00  | 20:08 | 30                 | 7.65         | 20.13            | 1       | 2026-05-08-timesheet-horas-trabalhadas.md |
| 2026-05-09 | 10:00  | 20:30 | 30                 | 3.25         | 10.50            | 1       | 2026-05-09-timesheet-horas-trabalhadas.md |
| 2026-05-25 | 14:00  | 23:45 | 30                 | 5.50         | 9.75             | 1       | 2026-05-25-timesheet-horas-trabalhadas.md |
| 2026-05-28 | 00:45  | 02:42 | 30                 | 1.75         | 1.95             | 1       | 2026-05-28-timesheet-horas-trabalhadas.md |
| 2026-05-30 | 11:00  | 23:30 | 20                 | 7.75         | 12.50            | 1       | 2026-05-30-timesheet-horas-trabalhadas.md |
| 2026-06-01 | 10:00  | 23:30 | 20                 | 7.00         | 13.50            | 1       | 2026-06-01-timesheet-horas-trabalhadas.md |
| 2026-06-12 | 06:30  | 14:00 | 20                 | 5.75         | 6.33             | 2       | 2026-06-12-timesheet-horas-trabalhadas.md |

## 3) Totais acumulados (dia, semana, mes, geral)

### Diario

| data       | horas_ativas | horas_decorridas |
|------------|--------------|------------------|
| 2026-05-07 | 4.68         | 13.45            |
| 2026-05-08 | 7.65         | 20.13            |
| 2026-05-09 | 3.25         | 10.50            |
| 2026-05-25 | 5.50         | 9.75             |
| 2026-05-28 | 1.75         | 1.95             |
| 2026-05-30 | 7.75         | 12.50            |
| 2026-06-01 | 7.00         | 13.50            |
| 2026-06-12 | 5.75         | 6.33             |

### Semanal (ISO week)

| ano_semana | horas_ativas | horas_decorridas |
|------------|--------------|------------------|
| 2026-W19   | 12.33        | 33.58            |
| 2026-W21   | 5.50         | 9.75             |
| 2026-W22   | 9.50         | 14.45            |
| 2026-W23   | 7.00         | 13.50            |
| 2026-W24   | 5.75         | 6.33             |

Nota: 2026-05-08 cruza meia-noite; a folha `2026-05-08-timesheet` atribui 7,65 h ativas ao dia 08 e 4,68 ao dia 07 — semana ISO pode sobrepor dias; usar secao 2 para graficos por data.

### Mensal

| ano_mes | horas_ativas | horas_decorridas |
|---------|--------------|------------------|
| 2026-05 | 30.58        | 68.28            |
| 2026-06 | 12.75        | 19.83            |

### Geral

- Total horas ativas no projeto: 43.33
- Total horas decorridas no periodo consolidado: 88.11
- Registros diarios acumulados: 8

## 4) Observacoes e protocolo de atualizacao

- Este arquivo deve ser sobrescrito sempre que houver novo timesheet diario.
- **Criterio de pausa (desde 2026-05-30):** intervalos **> 20 min** sem troca de mensagens **nao** entram nas horas ativas. Folhas antigas mantêm `criterio_pausa_min = 30` na tabela (secao 2); **nao** alterar retroativamente salvo pedido explicito.
- **Novas folhas diarias:** usar `criterio_pausa_min = 20` na tabela e no cabecalho do `AAAA-MM-DD-timesheet-horas-trabalhadas.md`.
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
- `2026-05-30-timesheet-horas-trabalhadas.md`
- `2026-06-01-timesheet-horas-trabalhadas.md`
- `2026-06-12-timesheet-horas-trabalhadas.md`
