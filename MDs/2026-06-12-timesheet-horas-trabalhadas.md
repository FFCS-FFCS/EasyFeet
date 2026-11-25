# EasyFeet - Timesheet de Horas Trabalhadas



Data do registro: 2026-06-12

Regra de calculo ativa: pausas > 20 min nao contam (criterio desde 2026-05-30)

Fuso horario de referencia: UTC-3



## 1) Sessoes registradas



### Sessao 1 (manha)



- Periodo: 2026-06-12 06:30 ate 2026-06-12 08:20 (UTC-3)

- Janela total (decorrido): 1.83 h

- Tempo ativo estimado: 1.75 h

- **NAV-2** + refinamento PDFs Navicular/Podoscopio; `pdf_brand.col_widths_rotulo_valor`.



### Sessao 2 (tarde)



- Periodo: 2026-06-12 09:30 ate 2026-06-12 14:00 (UTC-3) — **estimativa** para encerramento do dia (ajustar com log de mensagens se precisar).

- Janela total (decorrido): 4.50 h

- Tempo ativo estimado: 4.00 h

- Fonte: sessao Cursor (NAV-4, instalador DEMO); gatilho **Encerrar o dia: atualizar timesheet e o gerenciador de MDs**



#### Atividades principais (sessao 2)



- **NAV-4:** ecrã `navicular_laudos` — gerar textos, salvar, listar, PDF por paciente (`gui.py`).

- **PEND-NAV-LAUDO-001:** `navicular_laudo.py` (textos §4.1–4.4), `navicular_laudo_pdf.py`, BD `laudos_navicular`; smoke `scripts/test_navicular_laudo.py`.

- **Instalador DEMO:** `build_instalador_demo.bat`, `scripts/build_windows_installer.ps1 -Demo`; saida `release/EasyFeet-Setup-DEMO-2.0.0.exe` + `EasyFeet_DEMO_Com_Dados.zip` (inclui `data/` atual com BD e pacientes).

- **Docs:** gerenciador + `lista-de-proximos-passos.md` — NAV-4 concluido; retomar **NAV-3**.



## 2) Lancamentos tabulares (base para graficos)



| data       | inicio | fim   | criterio_pausa_min | horas_ativas | horas_decorridas | sessoes |

|------------|--------|-------|--------------------|--------------|------------------|---------|

| 2026-06-12 | 06:30  | 08:20 | 20                 | 1.75         | 1.83             | 1       |

| 2026-06-12 | 09:30  | 14:00 | 20                 | 4.00         | 4.50             | 1       |



**Total do dia 2026-06-12:** 5.75 h ativas / 6.33 h decorridas (2 sessoes).



## 3) Totais acumulados (neste arquivo diario)



- Total horas ativas (esta folha): 5.75

- Total horas decorridas (esta folha): 6.33

- Registros na folha: 2



## 4) Observacoes



- Horas ativas sao estimadas; refinar se houver pausas > 20 min sem troca de mensagens no intervalo.

- O consolidado (`timesheet-indice-e-consolidado.md` + `Documentos de Apoio/TimeSheet/timesheet-consolidado.csv`) foi atualizado neste encerramento.


