from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from easyfeet.db import Base


class Cliente(Base):
    __tablename__ = "clientes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    nome: Mapped[str] = mapped_column(String(120), nullable=False)
    telefone: Mapped[str] = mapped_column(String(30), nullable=True, default="")
    email: Mapped[str] = mapped_column(String(120), nullable=True, default="")
    data_nascimento: Mapped[str] = mapped_column(String(10), nullable=True, default="")
    sexo: Mapped[str] = mapped_column(String(20), nullable=True, default="")
    altura_m: Mapped[float | None] = mapped_column(Float, nullable=True)
    peso_kg: Mapped[float | None] = mapped_column(Float, nullable=True)
    lateralidade: Mapped[str] = mapped_column(String(20), nullable=True, default="")
    observacoes: Mapped[str] = mapped_column(Text, nullable=True, default="")
    criado_em: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    avaliacoes: Mapped[list["Avaliacao"]] = relationship(back_populates="cliente")
    momentos_clinicos: Mapped[list["MomentoClinico"]] = relationship(back_populates="cliente")
    fichas_podoscopio: Mapped[list["FichaPodoscopio"]] = relationship(back_populates="cliente")


class Avaliacao(Base):
    __tablename__ = "avaliacoes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    cliente_id: Mapped[int] = mapped_column(ForeignKey("clientes.id"), nullable=False, index=True)
    data_avaliacao: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    postura_estatica: Mapped[str] = mapped_column(Text, nullable=True, default="")
    marcha_dinamica: Mapped[str] = mapped_column(Text, nullable=True, default="")
    dor_relato: Mapped[str] = mapped_column(Text, nullable=True, default="")
    observacoes: Mapped[str] = mapped_column(Text, nullable=True, default="")

    cliente: Mapped["Cliente"] = relationship(back_populates="avaliacoes")
    laudo: Mapped["Laudo"] = relationship(back_populates="avaliacao", uselist=False)
    pedidos_palmilha: Mapped[list["PalmilhaPedido"]] = relationship(back_populates="avaliacao")
    momentos_clinicos: Mapped[list["MomentoClinico"]] = relationship(back_populates="avaliacao")


class Laudo(Base):
    __tablename__ = "laudos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    avaliacao_id: Mapped[int] = mapped_column(
        ForeignKey("avaliacoes.id"), nullable=False, unique=True, index=True
    )
    resumo_clinico: Mapped[str] = mapped_column(Text, nullable=False)
    recomendacoes: Mapped[str] = mapped_column(Text, nullable=True, default="")
    criado_em: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    avaliacao: Mapped["Avaliacao"] = relationship(back_populates="laudo")


class PalmilhaPedido(Base):
    __tablename__ = "palmilhas_pedidos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    avaliacao_id: Mapped[int] = mapped_column(ForeignKey("avaliacoes.id"), nullable=False, index=True)
    tipo: Mapped[str] = mapped_column(String(80), nullable=False)
    material: Mapped[str] = mapped_column(String(80), nullable=True, default="")
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="solicitada")
    previsao_entrega: Mapped[str] = mapped_column(String(10), nullable=True, default="")
    observacoes: Mapped[str] = mapped_column(Text, nullable=True, default="")
    criado_em: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    avaliacao: Mapped["Avaliacao"] = relationship(back_populates="pedidos_palmilha")


class MomentoClinico(Base):
    __tablename__ = "momentos_clinicos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    cliente_id: Mapped[int] = mapped_column(ForeignKey("clientes.id"), nullable=False, index=True)
    avaliacao_id: Mapped[int | None] = mapped_column(ForeignKey("avaliacoes.id"), nullable=True, index=True)
    data_referencia: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    rotulo: Mapped[str] = mapped_column(String(120), nullable=True, default="")
    observacoes: Mapped[str] = mapped_column(Text, nullable=True, default="")
    criado_em: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    atualizado_em: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    cliente: Mapped["Cliente"] = relationship(back_populates="momentos_clinicos")
    avaliacao: Mapped["Avaliacao"] = relationship(back_populates="momentos_clinicos")
    imagens_plantares: Mapped[list["ImagemPlantar"]] = relationship(back_populates="momento")


class ImagemPlantar(Base):
    __tablename__ = "imagens_plantares"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    momento_id: Mapped[int] = mapped_column(ForeignKey("momentos_clinicos.id"), nullable=False, index=True)
    lado: Mapped[str] = mapped_column(String(30), nullable=False, default="nao_informado")
    nome_arquivo: Mapped[str] = mapped_column(String(240), nullable=False)
    path_original: Mapped[str] = mapped_column(String(500), nullable=False)
    largura: Mapped[int] = mapped_column(Integer, nullable=True, default=0)
    altura: Mapped[int] = mapped_column(Integer, nullable=True, default=0)
    criado_em: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    momento: Mapped["MomentoClinico"] = relationship(back_populates="imagens_plantares")
    marcacoes: Mapped[list["MarcacaoPlantar"]] = relationship(back_populates="imagem")


class MarcacaoPlantar(Base):
    __tablename__ = "marcacoes_plantares"
    __table_args__ = (UniqueConstraint("imagem_id", "tipo_marcador", name="uq_marcacao_imagem_tipo"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    imagem_id: Mapped[int] = mapped_column(ForeignKey("imagens_plantares.id"), nullable=False, index=True)
    tipo_marcador: Mapped[str] = mapped_column(String(40), nullable=False)
    path_json: Mapped[str] = mapped_column(String(500), nullable=False)
    path_png_marcado: Mapped[str] = mapped_column(String(500), nullable=False)
    regra_marcador_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    criado_em: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    atualizado_em: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    imagem: Mapped["ImagemPlantar"] = relationship(back_populates="marcacoes")


class FichaPodoscopio(Base):
    __tablename__ = "fichas_podoscopio"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    cliente_id: Mapped[int] = mapped_column(ForeignKey("clientes.id"), nullable=False, index=True)
    data_avaliacao: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    rotulo_atendimento: Mapped[str] = mapped_column(String(120), nullable=True, default="")
    queixa_objetivo: Mapped[str] = mapped_column(Text, nullable=True, default="")
    arco_pe_direito: Mapped[str] = mapped_column(String(40), nullable=False, default="Nao avaliado")
    arco_pe_esquerdo: Mapped[str] = mapped_column(String(40), nullable=False, default="Nao avaliado")
    apoio_pe_direito: Mapped[str] = mapped_column(String(40), nullable=False, default="Nao avaliado")
    apoio_pe_esquerdo: Mapped[str] = mapped_column(String(40), nullable=False, default="Nao avaliado")
    simetria_carga: Mapped[str] = mapped_column(String(40), nullable=False, default="Nao avaliado")
    hiperpressao_zonas: Mapped[str] = mapped_column(Text, nullable=True, default="")
    observacoes: Mapped[str] = mapped_column(Text, nullable=True, default="")
    criado_em: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    atualizado_em: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    cliente: Mapped["Cliente"] = relationship(back_populates="fichas_podoscopio")
