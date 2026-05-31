from __future__ import annotations

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from easyfeet.models import (
    Avaliacao,
    Cliente,
    FichaPodoscopio,
    ImagemPlantar,
    Laudo,
    MarcacaoPlantar,
    MomentoClinico,
    PalmilhaPedido,
)


class ClienteRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def criar(
        self,
        nome: str,
        telefone: str = "",
        email: str = "",
        data_nascimento: str = "",
        sexo: str = "",
        observacoes: str = "",
        altura_m: float | None = None,
        peso_kg: float | None = None,
        lateralidade: str = "",
    ) -> Cliente:
        cliente = Cliente(
            nome=nome,
            telefone=telefone,
            email=email,
            data_nascimento=data_nascimento,
            sexo=sexo,
            observacoes=observacoes,
            altura_m=altura_m,
            peso_kg=peso_kg,
            lateralidade=lateralidade,
        )
        self.session.add(cliente)
        self.session.commit()
        self.session.refresh(cliente)
        return cliente

    def listar(self) -> list[Cliente]:
        return list(self.session.scalars(select(Cliente).order_by(Cliente.nome)))

    def listar_ultimos_por_cadastro(self, limit: int = 3) -> list[Cliente]:
        stmt = (
            select(Cliente)
            .order_by(Cliente.criado_em.desc(), Cliente.id.desc())
            .limit(max(1, limit))
        )
        return list(self.session.scalars(stmt))

    def obter_por_id(self, cliente_id: int) -> Cliente | None:
        return self.session.get(Cliente, cliente_id)

    def atualizar(
        self,
        cliente_id: int,
        nome: str,
        telefone: str = "",
        email: str = "",
        data_nascimento: str = "",
        sexo: str = "",
        observacoes: str = "",
        altura_m: float | None = None,
        peso_kg: float | None = None,
        lateralidade: str = "",
    ) -> Cliente:
        cliente = self.session.get(Cliente, cliente_id)
        if not cliente:
            raise ValueError("Cliente nao encontrado.")
        cliente.nome = nome
        cliente.telefone = telefone
        cliente.email = email
        cliente.data_nascimento = data_nascimento
        cliente.sexo = sexo
        cliente.observacoes = observacoes
        cliente.altura_m = altura_m
        cliente.peso_kg = peso_kg
        cliente.lateralidade = lateralidade
        self.session.commit()
        self.session.refresh(cliente)
        return cliente


class AvaliacaoRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def criar(
        self,
        cliente_id: int,
        postura_estatica: str,
        marcha_dinamica: str,
        dor_relato: str,
        observacoes: str = "",
    ) -> Avaliacao:
        avaliacao = Avaliacao(
            cliente_id=cliente_id,
            postura_estatica=postura_estatica,
            marcha_dinamica=marcha_dinamica,
            dor_relato=dor_relato,
            observacoes=observacoes,
        )
        self.session.add(avaliacao)
        self.session.commit()
        self.session.refresh(avaliacao)
        return avaliacao

    def listar_por_cliente(self, cliente_id: int) -> list[Avaliacao]:
        stmt = select(Avaliacao).where(Avaliacao.cliente_id == cliente_id).order_by(Avaliacao.data_avaliacao.desc())
        return list(self.session.scalars(stmt))

    def obter_por_id(self, avaliacao_id: int) -> Avaliacao | None:
        return self.session.get(Avaliacao, avaliacao_id)


class LaudoRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def criar(self, avaliacao_id: int, resumo_clinico: str, recomendacoes: str = "") -> Laudo:
        laudo = Laudo(avaliacao_id=avaliacao_id, resumo_clinico=resumo_clinico, recomendacoes=recomendacoes)
        self.session.add(laudo)
        self.session.commit()
        self.session.refresh(laudo)
        return laudo


class PalmilhaRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def criar(
        self,
        avaliacao_id: int,
        tipo: str,
        material: str = "",
        status: str = "solicitada",
        previsao_entrega: str = "",
        observacoes: str = "",
    ) -> PalmilhaPedido:
        pedido = PalmilhaPedido(
            avaliacao_id=avaliacao_id,
            tipo=tipo,
            material=material,
            status=status,
            previsao_entrega=previsao_entrega,
            observacoes=observacoes,
        )
        self.session.add(pedido)
        self.session.commit()
        self.session.refresh(pedido)
        return pedido

    def listar_por_avaliacao(self, avaliacao_id: int) -> list[PalmilhaPedido]:
        stmt = (
            select(PalmilhaPedido)
            .where(PalmilhaPedido.avaliacao_id == avaliacao_id)
            .order_by(PalmilhaPedido.criado_em.desc())
        )
        return list(self.session.scalars(stmt))


class MarcacaoPlantarRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def listar_momentos_por_cliente(self, cliente_id: int) -> list[MomentoClinico]:
        stmt = (
            select(MomentoClinico)
            .where(MomentoClinico.cliente_id == cliente_id)
            .order_by(MomentoClinico.data_referencia.desc(), MomentoClinico.id.desc())
        )
        return list(self.session.scalars(stmt))

    def criar_momento(
        self,
        cliente_id: int,
        rotulo: str,
        data_referencia: datetime,
        observacoes: str = "",
    ) -> MomentoClinico:
        momento = MomentoClinico(
            cliente_id=cliente_id,
            data_referencia=data_referencia,
            rotulo=rotulo,
            observacoes=observacoes,
        )
        self.session.add(momento)
        self.session.commit()
        self.session.refresh(momento)
        return momento

    def obter_momento(self, momento_id: int) -> MomentoClinico | None:
        return self.session.get(MomentoClinico, momento_id)

    def atualizar_momento(self, momento_id: int, rotulo: str, observacoes: str = "") -> MomentoClinico:
        momento = self.session.get(MomentoClinico, momento_id)
        if momento is None:
            raise ValueError("Momento clinico nao encontrado.")
        momento.rotulo = rotulo
        momento.observacoes = observacoes
        momento.atualizado_em = datetime.utcnow()
        self.session.commit()
        self.session.refresh(momento)
        return momento

    def listar_imagens_por_momento(self, momento_id: int) -> list[ImagemPlantar]:
        stmt = (
            select(ImagemPlantar)
            .where(ImagemPlantar.momento_id == momento_id)
            .order_by(ImagemPlantar.id.desc())
        )
        return list(self.session.scalars(stmt))

    def listar_marcacoes_por_cliente(self, cliente_id: int) -> list[tuple[MarcacaoPlantar, ImagemPlantar, MomentoClinico]]:
        stmt = (
            select(MarcacaoPlantar, ImagemPlantar, MomentoClinico)
            .join(ImagemPlantar, MarcacaoPlantar.imagem_id == ImagemPlantar.id)
            .join(MomentoClinico, ImagemPlantar.momento_id == MomentoClinico.id)
            .where(MomentoClinico.cliente_id == cliente_id)
            .order_by(MomentoClinico.data_referencia.desc(), MarcacaoPlantar.atualizado_em.desc())
        )
        return list(self.session.execute(stmt).all())


class FichaPodoscopioRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def criar(
        self,
        cliente_id: int,
        data_avaliacao: datetime,
        rotulo_atendimento: str,
        queixa_objetivo: str,
        arco_pe_direito: str,
        arco_pe_esquerdo: str,
        apoio_pe_direito: str,
        apoio_pe_esquerdo: str,
        simetria_carga: str,
        hiperpressao_zonas: str,
        observacoes: str,
    ) -> FichaPodoscopio:
        ficha = FichaPodoscopio(
            cliente_id=cliente_id,
            data_avaliacao=data_avaliacao,
            rotulo_atendimento=rotulo_atendimento,
            queixa_objetivo=queixa_objetivo,
            arco_pe_direito=arco_pe_direito,
            arco_pe_esquerdo=arco_pe_esquerdo,
            apoio_pe_direito=apoio_pe_direito,
            apoio_pe_esquerdo=apoio_pe_esquerdo,
            simetria_carga=simetria_carga,
            hiperpressao_zonas=hiperpressao_zonas,
            observacoes=observacoes,
        )
        self.session.add(ficha)
        self.session.commit()
        self.session.refresh(ficha)
        return ficha

    def atualizar(
        self,
        ficha_id: int,
        data_avaliacao: datetime,
        rotulo_atendimento: str,
        queixa_objetivo: str,
        arco_pe_direito: str,
        arco_pe_esquerdo: str,
        apoio_pe_direito: str,
        apoio_pe_esquerdo: str,
        simetria_carga: str,
        hiperpressao_zonas: str,
        observacoes: str,
    ) -> FichaPodoscopio:
        ficha = self.session.get(FichaPodoscopio, ficha_id)
        if not ficha:
            raise ValueError("Ficha podoscopica nao encontrada.")
        ficha.data_avaliacao = data_avaliacao
        ficha.rotulo_atendimento = rotulo_atendimento
        ficha.queixa_objetivo = queixa_objetivo
        ficha.arco_pe_direito = arco_pe_direito
        ficha.arco_pe_esquerdo = arco_pe_esquerdo
        ficha.apoio_pe_direito = apoio_pe_direito
        ficha.apoio_pe_esquerdo = apoio_pe_esquerdo
        ficha.simetria_carga = simetria_carga
        ficha.hiperpressao_zonas = hiperpressao_zonas
        ficha.observacoes = observacoes
        ficha.atualizado_em = datetime.utcnow()
        self.session.commit()
        self.session.refresh(ficha)
        return ficha

    def obter_por_id(self, ficha_id: int) -> FichaPodoscopio | None:
        return self.session.get(FichaPodoscopio, ficha_id)

    def listar_por_cliente(self, cliente_id: int) -> list[FichaPodoscopio]:
        stmt = (
            select(FichaPodoscopio)
            .where(FichaPodoscopio.cliente_id == cliente_id)
            .order_by(FichaPodoscopio.data_avaliacao.desc(), FichaPodoscopio.id.desc())
        )
        return list(self.session.scalars(stmt))
