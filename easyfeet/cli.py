from __future__ import annotations

from sqlalchemy.orm import Session

from easyfeet.services import EasyFeetService


def _input_int(label: str) -> int:
    while True:
        raw = input(label).strip()
        try:
            return int(raw)
        except ValueError:
            print("Valor invalido. Digite um numero.")


def executar_cli(session: Session) -> None:
    service = EasyFeetService(session)

    while True:
        print("\n=== EasyFeet - Menu Principal ===")
        print("1) Cadastrar cliente")
        print("2) Listar clientes")
        print("3) Registrar avaliacao postural")
        print("4) Gerar laudo")
        print("5) Solicitar palmilha")
        print("6) Ver historico de cliente")
        print("0) Sair")

        opcao = input("Escolha uma opcao: ").strip()

        try:
            if opcao == "1":
                nome = input("Nome: ").strip()
                telefone = input("Telefone (opcional): ").strip()
                email = input("Email (opcional): ").strip()
                data_nascimento = input("Data nascimento (DD/MM/AAAA, obrigatorio): ").strip()
                sexo_in = input("Sexo [M/F] (obrigatorio): ").strip().lower()
                mapa = {"m": "Masculino", "f": "Feminino"}
                sexo = mapa.get(sexo_in, "")
                observacoes = input("Observacoes (opcional): ").strip()
                cliente = service.cadastrar_cliente(nome, telefone, email, data_nascimento, sexo, observacoes)
                print(f"Cliente cadastrado com sucesso. ID: {cliente.id}")

            elif opcao == "2":
                clientes = service.clientes.listar()
                if not clientes:
                    print("Nenhum cliente cadastrado.")
                    continue
                print("\n--- Clientes ---")
                for c in clientes:
                    print(f"[{c.id}] {c.nome} | Tel: {c.telefone or '-'} | Email: {c.email or '-'}")

            elif opcao == "3":
                cliente_id = _input_int("ID do cliente: ")
                postura_estatica = input("Postura estatica: ").strip()
                marcha_dinamica = input("Marcha dinamica: ").strip()
                dor_relato = input("Relato de dor: ").strip()
                observacoes = input("Observacoes (opcional): ").strip()
                avaliacao = service.registrar_avaliacao(
                    cliente_id, postura_estatica, marcha_dinamica, dor_relato, observacoes
                )
                print(f"Avaliacao registrada. ID: {avaliacao.id}")

            elif opcao == "4":
                avaliacao_id = _input_int("ID da avaliacao: ")
                resumo_clinico = input("Resumo clinico: ").strip()
                recomendacoes = input("Recomendacoes (opcional): ").strip()
                laudo = service.gerar_laudo(avaliacao_id, resumo_clinico, recomendacoes)
                print(f"Laudo criado com sucesso. ID: {laudo.id}")

            elif opcao == "5":
                avaliacao_id = _input_int("ID da avaliacao: ")
                tipo = input("Tipo de palmilha: ").strip()
                material = input("Material (opcional): ").strip()
                status = input("Status (default: solicitada): ").strip() or "solicitada"
                previsao_entrega = input("Previsao entrega (YYYY-MM-DD, opcional): ").strip()
                observacoes = input("Observacoes (opcional): ").strip()
                pedido = service.solicitar_palmilha(
                    avaliacao_id, tipo, material, status, previsao_entrega, observacoes
                )
                print(f"Pedido de palmilha registrado. ID: {pedido.id}")

            elif opcao == "6":
                cliente_id = _input_int("ID do cliente: ")
                cliente = service.clientes.obter_por_id(cliente_id)
                if not cliente:
                    print("Cliente nao encontrado.")
                    continue

                print(f"\nCliente: {cliente.nome}")
                print(f"Telefone: {cliente.telefone or '-'}")
                print(f"Email: {cliente.email or '-'}")
                print(f"Nascimento: {cliente.data_nascimento or '-'}")
                print(f"Observacoes: {cliente.observacoes or '-'}")

                avaliacoes = service.avaliacoes.listar_por_cliente(cliente_id)
                if not avaliacoes:
                    print("Sem avaliacoes registradas.")
                    continue

                print("\n--- Avaliacoes ---")
                for a in avaliacoes:
                    print(f"Avaliacao [{a.id}] em {a.data_avaliacao.strftime('%Y-%m-%d %H:%M')}")
                    print(f"  Postura estatica: {a.postura_estatica or '-'}")
                    print(f"  Marcha dinamica: {a.marcha_dinamica or '-'}")
                    print(f"  Relato dor: {a.dor_relato or '-'}")
                    if a.laudo:
                        print(f"  Laudo [{a.laudo.id}]: {a.laudo.resumo_clinico}")
                    pedidos = service.palmilhas.listar_por_avaliacao(a.id)
                    for p in pedidos:
                        print(f"  Palmilha [{p.id}] tipo={p.tipo} status={p.status} previsao={p.previsao_entrega or '-'}")

            elif opcao == "0":
                print("Encerrando EasyFeet.")
                break
            else:
                print("Opcao invalida.")
        except ValueError as exc:
            print(f"Erro: {exc}")
