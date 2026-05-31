from __future__ import annotations

from datetime import date, datetime

from sqlalchemy.orm import Session

from easyfeet.cliente_dados_corporais import validar_altura_metros, validar_lateralidade, validar_peso_kg
from easyfeet.models import FichaPodoscopio, MomentoClinico

MOMENTO_ROTULO_MAX = 120
MOMENTO_OBSERVACOES_MAX = 2000
from easyfeet.repositories import (
    AvaliacaoRepository,
    ClienteRepository,
    FichaPodoscopioRepository,
    LaudoRepository,
    MarcacaoPlantarRepository,
    PalmilhaRepository,
)


class EasyFeetService:
    def __init__(self, session: Session) -> None:
        self.clientes = ClienteRepository(session)
        self.avaliacoes = AvaliacaoRepository(session)
        self.laudos = LaudoRepository(session)
        self.palmilhas = PalmilhaRepository(session)
        self.marcacoes = MarcacaoPlantarRepository(session)
        self.fichas_podoscopio = FichaPodoscopioRepository(session)

    def cadastrar_cliente(
        self,
        nome: str,
        telefone: str = "",
        email: str = "",
        data_nascimento: str = "",
        sexo: str = "",
        observacoes: str = "",
        altura_m: str = "",
        peso_kg: str = "",
        lateralidade: str = "",
        *,
        exigir_dados_corporais: bool = False,
    ):
        dados = self._validar_dados_cliente(
            nome,
            data_nascimento,
            sexo,
            altura_m,
            peso_kg,
            lateralidade,
            exigir_dados_corporais=exigir_dados_corporais,
        )
        return self.clientes.criar(
            dados["nome"],
            telefone,
            email,
            dados["nascimento"],
            dados["sexo"],
            observacoes,
            altura_m=dados["altura_m"],
            peso_kg=dados["peso_kg"],
            lateralidade=dados["lateralidade"],
        )

    def atualizar_cliente(
        self,
        cliente_id: int,
        nome: str,
        telefone: str = "",
        email: str = "",
        data_nascimento: str = "",
        sexo: str = "",
        observacoes: str = "",
        altura_m: str = "",
        peso_kg: str = "",
        lateralidade: str = "",
        *,
        exigir_dados_corporais: bool = False,
    ):
        dados = self._validar_dados_cliente(
            nome,
            data_nascimento,
            sexo,
            altura_m,
            peso_kg,
            lateralidade,
            exigir_dados_corporais=exigir_dados_corporais,
        )
        return self.clientes.atualizar(
            cliente_id,
            dados["nome"],
            telefone,
            email,
            dados["nascimento"],
            dados["sexo"],
            observacoes,
            altura_m=dados["altura_m"],
            peso_kg=dados["peso_kg"],
            lateralidade=dados["lateralidade"],
        )

    def _validar_dados_cliente(
        self,
        nome: str,
        data_nascimento: str,
        sexo: str,
        altura_m: str,
        peso_kg: str,
        lateralidade: str,
        *,
        exigir_dados_corporais: bool,
    ) -> dict:
        if not nome.strip():
            raise ValueError("Nome do cliente e obrigatorio.")
        nascimento = self._parse_and_validate_nascimento(data_nascimento)
        if sexo not in {"Masculino", "Feminino"}:
            raise ValueError("Para salvar, selecione Masculino ou Feminino.")

        altura_txt = (altura_m or "").strip()
        peso_txt = (peso_kg or "").strip()
        lat_txt = (lateralidade or "").strip()
        if exigir_dados_corporais or altura_txt or peso_txt or lat_txt:
            if not altura_txt:
                raise ValueError("Altura (m) e obrigatoria (ex.: 1,75).")
            if not peso_txt:
                raise ValueError("Peso (kg) e obrigatorio (ex.: 68,5).")
            if not lat_txt:
                raise ValueError("Selecione Destro, Canhoto ou Ambidestro.")
            return {
                "nome": nome.strip(),
                "nascimento": nascimento,
                "sexo": sexo,
                "altura_m": validar_altura_metros(altura_txt),
                "peso_kg": validar_peso_kg(peso_txt),
                "lateralidade": validar_lateralidade(lat_txt),
            }
        return {
            "nome": nome.strip(),
            "nascimento": nascimento,
            "sexo": sexo,
            "altura_m": None,
            "peso_kg": None,
            "lateralidade": "",
        }

    def _parse_and_validate_nascimento(self, data_nascimento: str) -> str:
        if not data_nascimento.strip():
            raise ValueError("Data de nascimento e obrigatoria (DD/MM/AAAA).")
        try:
            nascimento = datetime.strptime(data_nascimento.strip(), "%d/%m/%Y").date()
        except ValueError:
            raise ValueError("Data de nascimento invalida. Use DD/MM/AAAA.") from None
        hoje = date.today()
        idade_anos = hoje.year - nascimento.year - ((hoje.month, hoje.day) < (nascimento.month, nascimento.day))
        if idade_anos < 3:
            raise ValueError("Paciente precisa ter completado 3 anos de idade (cadastro alinhado à orientação por idade).")
        return nascimento.strftime("%d/%m/%Y")

    def registrar_avaliacao(
        self, cliente_id: int, postura_estatica: str, marcha_dinamica: str, dor_relato: str, observacoes: str = ""
    ):
        if not self.clientes.obter_por_id(cliente_id):
            raise ValueError("Cliente nao encontrado.")
        return self.avaliacoes.criar(cliente_id, postura_estatica, marcha_dinamica, dor_relato, observacoes)

    def gerar_laudo(self, avaliacao_id: int, resumo_clinico: str, recomendacoes: str = ""):
        avaliacao = self.avaliacoes.obter_por_id(avaliacao_id)
        if not avaliacao:
            raise ValueError("Avaliacao nao encontrada.")
        if avaliacao.laudo:
            raise ValueError("Esta avaliacao ja possui laudo.")
        return self.laudos.criar(avaliacao_id, resumo_clinico, recomendacoes)

    def parse_data_avaliacao_podoscopio(self, texto: str) -> datetime:
        raw = (texto or "").strip()
        for fmt in ("%d/%m/%Y %H:%M", "%d/%m/%Y"):
            try:
                return datetime.strptime(raw, fmt)
            except ValueError:
                continue
        raise ValueError("Data da avaliacao invalida. Use DD/MM/AAAA HH:MM ou DD/MM/AAAA.")

    def salvar_ficha_podoscopio(
        self,
        cliente_id: int,
        data_avaliacao_texto: str,
        rotulo_atendimento: str,
        queixa_objetivo: str,
        arco_pe_direito: str,
        arco_pe_esquerdo: str,
        apoio_pe_direito: str,
        apoio_pe_esquerdo: str,
        simetria_carga: str,
        hiperpressao_zonas: list[str],
        observacoes: str,
        *,
        ficha_id: int | None = None,
    ) -> FichaPodoscopio:
        if not self.clientes.obter_por_id(cliente_id):
            raise ValueError("Cliente nao encontrado.")
        data_avaliacao = self.parse_data_avaliacao_podoscopio(data_avaliacao_texto)
        zonas_txt = ";".join(z.strip() for z in hiperpressao_zonas if z.strip())
        payload = dict(
            data_avaliacao=data_avaliacao,
            rotulo_atendimento=(rotulo_atendimento or "").strip(),
            queixa_objetivo=(queixa_objetivo or "").strip(),
            arco_pe_direito=arco_pe_direito.strip(),
            arco_pe_esquerdo=arco_pe_esquerdo.strip(),
            apoio_pe_direito=apoio_pe_direito.strip(),
            apoio_pe_esquerdo=apoio_pe_esquerdo.strip(),
            simetria_carga=simetria_carga.strip(),
            hiperpressao_zonas=zonas_txt,
            observacoes=(observacoes or "").strip(),
        )
        if ficha_id is not None:
            return self.fichas_podoscopio.atualizar(ficha_id, **payload)
        return self.fichas_podoscopio.criar(cliente_id, **payload)

    def criar_momento_clinico(
        self,
        cliente_id: int,
        rotulo: str,
        data_referencia: datetime | None = None,
        observacoes: str = "",
    ) -> MomentoClinico:
        if not self.clientes.obter_por_id(cliente_id):
            raise ValueError("Paciente nao encontrado.")
        rotulo_txt = (rotulo or "").strip()
        if not rotulo_txt:
            raise ValueError("Informe um rotulo para o momento clinico.")
        when = data_referencia or datetime.now()
        return self.marcacoes.criar_momento(
            cliente_id,
            self._validar_momento_rotulo(rotulo_txt),
            when,
            self._validar_momento_observacoes(observacoes),
        )

    def atualizar_momento_clinico(
        self,
        momento_id: int,
        rotulo: str,
        observacoes: str = "",
    ) -> MomentoClinico:
        momento = self.marcacoes.obter_momento(momento_id)
        if momento is None:
            raise ValueError("Momento clinico nao encontrado.")
        if not self.clientes.obter_por_id(momento.cliente_id):
            raise ValueError("Paciente nao encontrado.")
        return self.marcacoes.atualizar_momento(
            momento_id,
            self._validar_momento_rotulo((rotulo or "").strip()),
            self._validar_momento_observacoes(observacoes),
        )

    @staticmethod
    def _validar_momento_rotulo(rotulo: str) -> str:
        if not rotulo:
            raise ValueError("Informe um rotulo para o momento clinico.")
        if len(rotulo) > MOMENTO_ROTULO_MAX:
            raise ValueError(f"Rotulo do momento: maximo {MOMENTO_ROTULO_MAX} caracteres.")
        return rotulo

    @staticmethod
    def _validar_momento_observacoes(observacoes: str) -> str:
        txt = (observacoes or "").strip()
        if len(txt) > MOMENTO_OBSERVACOES_MAX:
            raise ValueError(f"Observacoes do momento: maximo {MOMENTO_OBSERVACOES_MAX} caracteres.")
        return txt

    def solicitar_palmilha(
        self,
        avaliacao_id: int,
        tipo: str,
        material: str = "",
        status: str = "solicitada",
        previsao_entrega: str = "",
        observacoes: str = "",
    ):
        if not self.avaliacoes.obter_por_id(avaliacao_id):
            raise ValueError("Avaliacao nao encontrada.")
        if not tipo.strip():
            raise ValueError("Tipo de palmilha e obrigatorio.")
        return self.palmilhas.criar(avaliacao_id, tipo, material, status, previsao_entrega, observacoes)
