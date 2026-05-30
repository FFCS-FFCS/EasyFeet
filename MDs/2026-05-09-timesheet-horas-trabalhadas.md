# EasyFeet - Timesheet de Horas Trabalhadas

Data do registro: 2026-05-09
Regra de calculo ativa: pausas > 30 min nao contam (criterio intermediario)
Fuso horario de referencia: UTC-3

## 1) Sessao registrada

- Periodo: 2026-05-09 10:00 ate 2026-05-09 20:30 (UTC-3) — **estimativa** para encerramento do dia (ajustar com log de mensagens se precisar).
- Janela total (decorrido): 10.50 h
- Tempo ativo estimado: 3.25 h
- Fonte: sessao de desenvolvimento/documentacao (Cursor); gatilho **Encerrar o dia: atualizar timesheet e o gerenciador de MDs**

## 2) Lancamentos tabulares (base para graficos)

| data       | inicio | fim   | criterio_pausa_min | horas_ativas | horas_decorridas | sessoes |
|------------|--------|-------|--------------------|--------------|------------------|---------|
| 2026-05-09 | 10:00  | 20:30 | 30                 | 3.25         | 10.50            | 1       |

## 3) Totais acumulados (neste arquivo diario)

- Total horas ativas (esta folha): 3.25
- Total horas decorridas (esta folha): 10.50
- Registros na folha: 1

## 4) Observacoes

- Horas ativas sao estimadas; refinar se houver pausas > 30 min sem troca de mensagens no intervalo.
- O consolidado (`timesheet-indice-e-consolidado.md` + `Documentos de Apoio/TimeSheet/timesheet-consolidado.csv`) soma esta folha com `2026-05-08-timesheet-horas-trabalhadas.md`.
