# EasyFeet - Timesheet de Horas Trabalhadas

Data do registro: 2026-05-30
Regra de calculo ativa: pausas > 20 min nao contam (criterio desde 2026-05-30)
Fuso horario de referencia: UTC-3

## 1) Sessao registrada

- Periodo: 2026-05-30 11:00 ate 2026-05-30 23:30 (UTC-3) — **estimativa** para encerramento do dia (ajustar com log de mensagens se precisar).
- Janela total (decorrido): 12.50 h
- Tempo ativo estimado: 7.75 h
- Fonte: sessoes Cursor (M2 Hub, M3 timeline, M4 EFM B+, UX Pacientes/EFM); gatilho **Encerrar o dia: atualizar timesheet e o gerenciador de MDs**

### Atividades principais (resumo)

- **M2:** Hub v0 do paciente (Resumo + Linha do tempo), botao «Abrir ficha clinica», sidebar scrollavel.
- **M3:** Timeline agrupada por dia/subcards; edicao rotulo/observacoes do momento; historico de marcacoes saiu de Pacientes.
- **M4:** EFM B+ (contexto Hub, Plantigrafo sem auto-abrir), lado D/E/Ambos, timeline por imagem, atalho Plantigrafo na ficha.
- **UX Pacientes:** botao «Novo paciente»; colunas Lateralidade/Email mais largas.
- **UX EFM:** seletor Imagem (D/E), alterar lado, excluir imagem, header em 2 linhas, faixa Acoes alinhada, zoom 100–400% (passo 50), alinhamento gutter 6 px.
- **Testes:** `scripts/test_hub_smoke.py`.

## 2) Lancamentos tabulares (base para graficos)

| data       | inicio | fim   | criterio_pausa_min | horas_ativas | horas_decorridas | sessoes |
|------------|--------|-------|--------------------|--------------|------------------|---------|
| 2026-05-30 | 11:00  | 23:30 | 20                 | 7.75         | 12.50            | 1       |

## 3) Totais acumulados (neste arquivo diario)

- Total horas ativas (esta folha): 7.75
- Total horas decorridas (esta folha): 12.50
- Registros na folha: 1

## 4) Observacoes

- Horas ativas sao estimadas; refinar se houver pausas > 20 min sem troca de mensagens no intervalo.
- O consolidado (`timesheet-indice-e-consolidado.md` + `Documentos de Apoio/TimeSheet/timesheet-consolidado.csv`) foi atualizado neste encerramento.
