# EasyFeet - Timesheet de Horas Trabalhadas

Data do registro: 2026-06-01
Regra de calculo ativa: pausas > 20 min nao contam (criterio desde 2026-05-30)
Fuso horario de referencia: UTC-3

## 1) Sessao registrada

- Periodo: 2026-06-01 10:00 ate 2026-06-01 23:30 (UTC-3) — **estimativa** para encerramento do dia (ajustar com log de mensagens se precisar).
- Janela total (decorrido): 13.50 h
- Tempo ativo estimado: 7.00 h
- Fonte: sessoes Cursor (Teste Navicular NAV-0/NAV-1, PDF limiares 10 mm, UX ficha, combo ficha salva, laudo MD); gatilho **Encerrar o dia: atualizar timesheet e o gerenciador de MDs**

### Atividades principais (resumo)

- **NAV-0:** menu `navicular` acima de Palmilhas (Ficha / Laudos / Configuracoes); hub e subitens.
- **NAV-1:** ficha funcional + BD + Modo A (Brody, limiar **10 mm**); combo «Ficha salva»; salvar/carregar; `NAVICULAR_LIMIAR_MM = 10`.
- **Documentos de apoio:** `EF - Navicular mm x percentual.md` + PDF limiares (10 mm); plano NAV-0…NAV-5; **`EF - Navicular laudo - textos modelo.md`** (PEND-NAV-LAUDO-001).
- **UX ficha:** campos mm com `tk.Entry` (multiplos digitos); layout queda/classificacao alinhado a esquerda; sanfonas da sidebar fechadas no arranque.
- **Ficha:** removidos botoes «Abrir limiares/plano (MD)»; mantidos Nova ficha + Salvar.
- **Excluir ficha salva:** Navicular e Podoscopio.
- **Combo ficha salva:** correcao handler (`choice` do callback + sync combo/var) — Podoscopio e Navicular.
- **Testes:** `scripts/test_navicular_ficha_salvar.py`, `scripts/test_ficha_salva_combo_smoke.py`.
- **Lista viva:** `lista-de-proximos-passos.md` — NAV-1 concluido; retomar **NAV-2** (PDF ficha) → **NAV-4** (laudos).

## 2) Lancamentos tabulares (base para graficos)

| data       | inicio | fim   | criterio_pausa_min | horas_ativas | horas_decorridas | sessoes |
|------------|--------|-------|--------------------|--------------|------------------|---------|
| 2026-06-01 | 10:00  | 23:30 | 20                 | 7.00         | 13.50            | 1       |

## 3) Totais acumulados (neste arquivo diario)

- Total horas ativas (esta folha): 7.00
- Total horas decorridas (esta folha): 13.50
- Registros na folha: 1

## 4) Observacoes

- Horas ativas sao estimadas; refinar se houver pausas > 20 min sem troca de mensagens no intervalo.
- O consolidado (`timesheet-indice-e-consolidado.md` + `Documentos de Apoio/TimeSheet/timesheet-consolidado.csv`) foi atualizado neste encerramento.
