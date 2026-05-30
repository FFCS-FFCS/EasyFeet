from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import json
from pathlib import Path
import shutil
from typing import Any
from uuid import uuid4

from PIL import Image


DATA_DIR = Path("data")
RULES_FILE = DATA_DIR / "marker_rules.json"
IMAGES_DIR = DATA_DIR / "marker_rule_images"

BUILTIN_PLACEHOLDER_NAME = "_builtin_placeholder.png"

PROTOCOLO_VERSAO_ATUAL = 1

# Regras criadas no seed inicial: referência imutável na exclusão; cópia editável + restaurável.
SEED_ROLE_ABCD_REFERENCE = "abcd_reference"
SEED_ROLE_ABCD_USER_COPY = "abcd_user_copy"
SEED_ROLE_POINTS_REFERENCE = "points_af_reference"
SEED_ROLE_POINTS_USER_COPY = "points_af_user_copy"

ROTULOS_LINHAS: tuple[str, ...] = ("A", "B", "C", "D")
ROTULOS_PONTOS: tuple[str, ...] = ("A", "B", "C", "D", "E", "F")

_LEGACY_DEF_FIELDS = ("definicao_a", "definicao_b", "definicao_c", "definicao_d", "definicao_e", "definicao_f")

def required_item_count(tipo_marcador: str) -> int:
    t = (tipo_marcador or "").strip().lower()
    if t == "pontos":
        return 6
    return 4


def default_rotulos(tipo_marcador: str) -> tuple[str, ...]:
    t = (tipo_marcador or "").strip().lower()
    return ROTULOS_PONTOS if t == "pontos" else ROTULOS_LINHAS


@dataclass(frozen=True)
class ProtocoloItem:
    ordem: int
    rotulo: str
    texto: str


@dataclass
class MarkerRule:
    id: int
    nome_regra: str
    tipo_marcador: str
    ativo: bool
    descricao_geral: str
    itens: tuple[ProtocoloItem, ...]
    imagem_exemplo_path: str
    imagem_exemplo_nome: str
    criado_em: str
    atualizado_em: str
    seed_role: str | None = None


def _legacy_texts_by_letter(raw: dict[str, Any]) -> dict[str, str]:
    return {
        "A": str(raw.get("definicao_a", "")).strip(),
        "B": str(raw.get("definicao_b", "")).strip(),
        "C": str(raw.get("definicao_c", "")).strip(),
        "D": str(raw.get("definicao_d", "")).strip(),
        "E": str(raw.get("definicao_e", "")).strip(),
        "F": str(raw.get("definicao_f", "")).strip(),
    }


def itens_from_legacy_row(raw: dict[str, Any], tipo_marcador: str) -> tuple[ProtocoloItem, ...]:
    """Constroi itens a partir de definicao_a..f (formato antigo)."""
    rotulos = default_rotulos(tipo_marcador)
    by_letter = _legacy_texts_by_letter(raw)
    out: list[ProtocoloItem] = []
    for i, rot in enumerate(rotulos, start=1):
        out.append(ProtocoloItem(ordem=i, rotulo=rot, texto=by_letter.get(rot, "")))
    return tuple(out)


def parse_itens_from_raw(raw: dict[str, Any]) -> tuple[ProtocoloItem, ...]:
    """Le protocolo.itens ou migra definicao_*."""
    tipo = str(raw.get("tipo_marcador", "linhas")).strip().lower() or "linhas"
    need = required_item_count(tipo)
    proto = raw.get("protocolo")
    if isinstance(proto, dict):
        arr = proto.get("itens")
        if isinstance(arr, list) and arr:
            parsed: list[ProtocoloItem] = []
            for entry in arr:
                if not isinstance(entry, dict):
                    continue
                try:
                    ordem = int(entry.get("ordem", 0))
                except (TypeError, ValueError):
                    ordem = 0
                rotulo = str(entry.get("rotulo", "")).strip()
                texto = str(entry.get("texto", "")).strip()
                if ordem <= 0 or not rotulo:
                    continue
                parsed.append(ProtocoloItem(ordem=ordem, rotulo=rotulo, texto=texto))
            parsed.sort(key=lambda x: x.ordem)
            if len(parsed) == need:
                return tuple(parsed[:need])
    return itens_from_legacy_row(raw, tipo)


def validate_itens_obrigatorios(tipo_marcador: str, itens: tuple[ProtocoloItem, ...]) -> None:
    n = required_item_count(tipo_marcador)
    if len(itens) != n:
        raise ValueError(f"Protocolo: sao obrigatorios {n} itens para tipo '{tipo_marcador}' (recebido {len(itens)}).")
    rotulos = default_rotulos(tipo_marcador)
    for i, (item, esperado) in enumerate(zip(itens, rotulos, strict=True), start=1):
        if item.ordem != i:
            raise ValueError(f"Item {i}: ordem deve ser {i} (recebido {item.ordem}).")
        if item.rotulo != esperado:
            raise ValueError(f"Item {i}: rotulo deve ser '{esperado}' (recebido '{item.rotulo}').")
        if not item.texto.strip():
            raise ValueError(f"Item {i} ({item.rotulo}): texto e obrigatorio.")


def protocolo_dict_from_itens(itens: tuple[ProtocoloItem, ...]) -> dict[str, Any]:
    return {
        "versao": PROTOCOLO_VERSAO_ATUAL,
        "itens": [{"ordem": x.ordem, "rotulo": x.rotulo, "texto": x.texto} for x in itens],
    }


def rule_to_storage_dict(rule: MarkerRule) -> dict[str, Any]:
    """Dicionario persistivel (sem campos legacy definicao_*)."""
    return {
        "id": rule.id,
        "nome_regra": rule.nome_regra,
        "tipo_marcador": rule.tipo_marcador,
        "ativo": rule.ativo,
        "descricao_geral": rule.descricao_geral,
        "protocolo": protocolo_dict_from_itens(rule.itens),
        "imagem_exemplo_path": rule.imagem_exemplo_path,
        "imagem_exemplo_nome": rule.imagem_exemplo_nome,
        "criado_em": rule.criado_em,
        "atualizado_em": rule.atualizado_em,
        "seed_role": rule.seed_role,
    }


def normalize_rule_from_raw(raw: dict[str, Any]) -> MarkerRule:
    itens = parse_itens_from_raw(raw)
    return MarkerRule(
        id=int(raw.get("id", 0)),
        nome_regra=str(raw.get("nome_regra", "")).strip(),
        tipo_marcador=str(raw.get("tipo_marcador", "linhas")).strip() or "linhas",
        ativo=bool(raw.get("ativo", True)),
        descricao_geral=str(raw.get("descricao_geral", "")).strip(),
        itens=itens,
        imagem_exemplo_path=str(raw.get("imagem_exemplo_path", "")).strip(),
        imagem_exemplo_nome=str(raw.get("imagem_exemplo_nome", "")).strip(),
        criado_em=str(raw.get("criado_em", "")).strip(),
        atualizado_em=str(raw.get("atualizado_em", "")).strip(),
        seed_role=(
            str(sr).strip()
            if (sr := raw.get("seed_role")) is not None and str(sr).strip()
            else None
        ),
    )


def finalize_rule_dict_for_write(rule_dict: dict[str, Any]) -> dict[str, Any]:
    """Garante protocolo.itens e remove definicao_* antes de gravar."""
    rule = normalize_rule_from_raw(rule_dict)
    out = rule_to_storage_dict(rule)
    return out


def itens_from_default_texts_line() -> tuple[ProtocoloItem, ...]:
    t = default_abcd_line_rule_texts()
    rotulos = ROTULOS_LINHAS
    keys = ("definicao_a", "definicao_b", "definicao_c", "definicao_d")
    return tuple(
        ProtocoloItem(ordem=i + 1, rotulo=rotulos[i], texto=str(t.get(keys[i], "")).strip())
        for i in range(4)
    )


def itens_from_default_texts_points() -> tuple[ProtocoloItem, ...]:
    t = default_points_af_rule_texts()
    keys = ("definicao_a", "definicao_b", "definicao_c", "definicao_d", "definicao_e", "definicao_f")
    return tuple(
        ProtocoloItem(ordem=i + 1, rotulo=ROTULOS_PONTOS[i], texto=str(t.get(keys[i], "")).strip())
        for i in range(6)
    )


def default_abcd_line_rule_texts() -> dict[str, str]:
    """Textos iniciais da regra ABCD (marcador de linhas)."""
    return {
        "nome_regra": "Regra ABCD (linhas) — sugestão inicial",
        "descricao_geral": (
            "Como transformar isso em pontos \"de onde até onde\":\n\n"
            "Extrair contorno da planta (máscara binária da pegada).\n"
            "Definir o eixo A como direção principal da máscara.\n"
            "Para B/C/D, gerar linhas perpendiculares ao eixo A em diferentes alturas do pé.\n"
            "Cada linha começa e termina nas interseções com o contorno (isso já dá início/fim automaticamente).\n"
            "Selecionar:\n"
            "B: maior largura no terço anterior,\n"
            "C: menor largura no terço médio,\n"
            "D: largura no terço posterior (calcanhar)."
        ),
        "definicao_a": (
            "Calcular o eixo principal da pegada (PCA na silhueta) e traçar do antepé ao retropé."
        ),
        "definicao_b": (
            "Procurar, na faixa do antepé, a secção transversal de maior largura (medial-lateral)."
        ),
        "definicao_c": (
            "Procurar, entre antepé e retropé, a secção de menor largura (região do arco)."
        ),
        "definicao_d": (
            "Procurar, na faixa do calcanhar, a largura posterior representativa."
        ),
    }


def default_reference_rule_display_name() -> str:
    return f'{default_abcd_line_rule_texts()["nome_regra"]} — referência do sistema'


def default_user_copy_rule_display_name() -> str:
    return "Versão usuário (cópia editável)"


def default_points_af_rule_texts() -> dict[str, str]:
    """Alinhado a `marcador_pontos/help_pontos_pt.txt` e `definitions.POINT_MARKERS`."""
    return {
        "nome_regra": "Referências A–F (pontos) — sugestão inicial",
        "descricao_geral": (
            "Marcador de pontos — articulações e referências (vista plantar).\n\n"
            "Cada letra (A–F) corresponde a um ponto marcado com um único clique sobre a imagem. "
            "Todos os pontos assinalados permanecem visíveis ao mesmo tempo; escolha o tipo na lista antes de clicar.\n\n"
            "«Sugerir pontos» tenta detetar a pegada (área mais escura que o fundo claro) e coloca marcas dentro dessa zona. "
            "Imagens sem contraste ou pé no sentido oposto podem precisar de ajuste manual."
        ),
        "definicao_a": (
            "A — Hálux — articulação MTP.\n"
            "Referência na base do hálux, ao nível aproximado da articulação metatarso-falangiana.\n\n"
            "Complemento (planta P&B, dedos para cima): o hálux é o dedão; em pé direito a face "
            "medial costuma ficar à esquerda da imagem. No antepé (faixa superior da pegada), "
            "procurar mancha escura arredondada do lado medial; em tons, útil considerar a coluna "
            "mais escura nessa faixa e um pequeno deslocamento proximal para aproximar a MTP. "
            "Pé esquerdo: espelhar (medial à direita). «Sugerir pontos» no EFM usa posições fixas "
            "na caixa da pegada, não este raciocínio literal."
        ),
        "definicao_b": (
            "B — 5.º metatarso — cabeça.\nCabeça do osso do quinto raio, zona lateral do antepé."
        ),
        "definicao_c": (
            "C — médio-pé — referência medial.\nPonto de apoio ou proeminência na margem medial do arco "
            "(conforme a convenção clínica da equipa)."
        ),
        "definicao_d": (
            "D — calcâneo — face medial.\nReferência na região medial do calcâneo / retropé."
        ),
        "definicao_e": (
            "E — calcâneo — face lateral.\nReferência na região lateral do calcâneo."
        ),
        "definicao_f": (
            "F — retropé — referência central.\nPonto central ou posterior do segmento do calcâneo, "
            "conforme protocolo da equipa."
        ),
    }


def default_points_reference_rule_display_name() -> str:
    return f'{default_points_af_rule_texts()["nome_regra"]} — referência do sistema'


def default_points_user_copy_rule_display_name() -> str:
    return "Versão usuário — pontos A–F (cópia editável)"


def parse_itens_from_form_data(data: dict[str, Any]) -> tuple[ProtocoloItem, ...]:
    """Aceita protocolo.itens ou lista plana 'itens' com dicts ordem/rotulo/texto."""
    tipo = str(data.get("tipo_marcador", "linhas")).strip().lower() or "linhas"
    proto = data.get("protocolo")
    if isinstance(proto, dict):
        arr = proto.get("itens")
        if isinstance(arr, list):
            tmp: dict[str, Any] = {**data, "tipo_marcador": tipo, "protocolo": {"itens": arr}}
            return parse_itens_from_raw(tmp)
    arr2 = data.get("itens")
    if isinstance(arr2, list):
        tmp2: dict[str, Any] = {**data, "tipo_marcador": tipo, "protocolo": {"itens": arr2}}
        return parse_itens_from_raw(tmp2)
    return itens_from_legacy_row(data, tipo)


class MarkerRuleStore:
    def __init__(self, rules_path: Path = RULES_FILE, images_dir: Path = IMAGES_DIR) -> None:
        self.rules_path = rules_path
        self.images_dir = images_dir
        self.rules_path.parent.mkdir(parents=True, exist_ok=True)
        self.images_dir.mkdir(parents=True, exist_ok=True)
        if not self.rules_path.exists():
            self._write({"next_id": 1, "rules": []})
        self.ensure_initial_marker_rule_pair()
        self.ensure_initial_points_marker_rule_pair()
        self._migrate_file_to_protocolo_if_needed()

    def _migrate_file_to_protocolo_if_needed(self) -> None:
        """Uma gravacao com formato novo quando o ficheiro ainda tem definicao_* ou falta protocolo."""
        payload = self._read()
        rules = payload.get("rules", [])
        needs = False
        for r in rules:
            if not isinstance(r, dict):
                continue
            if "protocolo" not in r:
                needs = True
                break
            if any(k in r for k in _LEGACY_DEF_FIELDS):
                needs = True
                break
        if needs:
            self._write(payload)

    def ensure_initial_marker_rule_pair(self) -> None:
        """Base vazia: cria duas regras (referência do sistema + cópia editável do usuário)."""
        payload = self._read()
        rules: list[dict[str, Any]] = list(payload.get("rules", []))
        if not rules:
            self._write_seed_pair(payload)
            return
        if any(r.get("seed_role") for r in rules):
            return
        if len(rules) != 1:
            return
        texts = default_abcd_line_rule_texts()
        r0 = dict(rules[0])
        nome = str(r0.get("nome_regra", "")).strip()
        img = str(r0.get("imagem_exemplo_nome", "")).strip()
        if nome != texts["nome_regra"] or img != BUILTIN_PLACEHOLDER_NAME:
            return
        now = datetime.now().isoformat(timespec="seconds")
        next_id = max(int(payload.get("next_id", 1)), int(r0.get("id", 1)) + 1)
        ph = self._ensure_builtin_placeholder_image()
        itens = itens_from_default_texts_line()
        r0["seed_role"] = SEED_ROLE_ABCD_REFERENCE
        r0["nome_regra"] = default_reference_rule_display_name()
        r0["atualizado_em"] = now
        r0["tipo_marcador"] = "linhas"
        r0["descricao_geral"] = texts["descricao_geral"]
        r0["protocolo"] = protocolo_dict_from_itens(itens)
        user = finalize_rule_dict_for_write(
            {
                "id": next_id,
                "nome_regra": default_user_copy_rule_display_name(),
                "tipo_marcador": "linhas",
                "ativo": True,
                "descricao_geral": texts["descricao_geral"],
                "protocolo": protocolo_dict_from_itens(itens),
                "imagem_exemplo_path": str(ph.resolve()),
                "imagem_exemplo_nome": BUILTIN_PLACEHOLDER_NAME,
                "criado_em": now,
                "atualizado_em": now,
                "seed_role": SEED_ROLE_ABCD_USER_COPY,
            }
        )
        payload["rules"] = [finalize_rule_dict_for_write(r0), user]
        payload["next_id"] = next_id + 1
        self._write(payload)

    def ensure_initial_points_marker_rule_pair(self) -> None:
        """Garante par referência do sistema + cópia editável para regras tipo `pontos` (A–F)."""
        payload = self._read()
        rules: list[dict[str, Any]] = list(payload.get("rules", []))
        if any(r.get("seed_role") == SEED_ROLE_POINTS_REFERENCE for r in rules):
            return
        texts = default_points_af_rule_texts()
        ph = self._ensure_builtin_placeholder_image()
        now = datetime.now().isoformat(timespec="seconds")
        next_id = max(int(payload.get("next_id", 1)), max((int(r.get("id", 0)) for r in rules), default=0) + 1)
        rid_ref = next_id
        rid_user = next_id + 1
        itens = itens_from_default_texts_points()
        base = {
            "tipo_marcador": "pontos",
            "ativo": True,
            "descricao_geral": texts["descricao_geral"],
            "protocolo": protocolo_dict_from_itens(itens),
            "imagem_exemplo_path": str(ph.resolve()),
            "imagem_exemplo_nome": BUILTIN_PLACEHOLDER_NAME,
            "criado_em": now,
            "atualizado_em": now,
        }
        ref = finalize_rule_dict_for_write(
            {
                **base,
                "id": rid_ref,
                "nome_regra": default_points_reference_rule_display_name(),
                "ativo": False,
                "seed_role": SEED_ROLE_POINTS_REFERENCE,
            }
        )
        user = finalize_rule_dict_for_write(
            {
                **base,
                "id": rid_user,
                "nome_regra": default_points_user_copy_rule_display_name(),
                "seed_role": SEED_ROLE_POINTS_USER_COPY,
            }
        )
        rules.append(ref)
        rules.append(user)
        payload["rules"] = rules
        payload["next_id"] = rid_user + 1
        self._write(payload)

    def _write_seed_pair(self, payload: dict[str, Any]) -> None:
        now = datetime.now().isoformat(timespec="seconds")
        ph = self._ensure_builtin_placeholder_image()
        texts = default_abcd_line_rule_texts()
        itens = itens_from_default_texts_line()
        base = {
            "tipo_marcador": "linhas",
            "ativo": True,
            "descricao_geral": texts["descricao_geral"],
            "protocolo": protocolo_dict_from_itens(itens),
            "imagem_exemplo_path": str(ph.resolve()),
            "imagem_exemplo_nome": BUILTIN_PLACEHOLDER_NAME,
            "criado_em": now,
            "atualizado_em": now,
        }
        ref = finalize_rule_dict_for_write(
            {
                **base,
                "id": 1,
                "nome_regra": default_reference_rule_display_name(),
                "seed_role": SEED_ROLE_ABCD_REFERENCE,
            }
        )
        user = finalize_rule_dict_for_write(
            {
                **base,
                "id": 2,
                "nome_regra": default_user_copy_rule_display_name(),
                "seed_role": SEED_ROLE_ABCD_USER_COPY,
            }
        )
        payload["rules"] = [ref, user]
        payload["next_id"] = 3
        self._write(payload)

    def restore_abcd_user_copy_to_defaults(self, reset_image: bool = True) -> MarkerRule:
        payload = self._read()
        now = datetime.now().isoformat(timespec="seconds")
        texts = default_abcd_line_rule_texts()
        ph = self._ensure_builtin_placeholder_image()
        itens = itens_from_default_texts_line()
        for idx, raw in enumerate(payload.get("rules", [])):
            if raw.get("seed_role") != SEED_ROLE_ABCD_USER_COPY:
                continue
            rid = int(raw.get("id", 0))
            image_name = str(raw.get("imagem_exemplo_nome", ""))
            image_path = str(raw.get("imagem_exemplo_path", ""))
            if reset_image:
                image_name, image_path = self._copy_image(str(ph), rid)
                image_path = str(image_path)
            updated = finalize_rule_dict_for_write(
                {
                    **raw,
                    "nome_regra": default_user_copy_rule_display_name(),
                    "tipo_marcador": "linhas",
                    "ativo": True,
                    "descricao_geral": texts["descricao_geral"],
                    "protocolo": protocolo_dict_from_itens(itens),
                    "imagem_exemplo_nome": image_name,
                    "imagem_exemplo_path": image_path,
                    "atualizado_em": now,
                    "seed_role": SEED_ROLE_ABCD_USER_COPY,
                }
            )
            payload["rules"][idx] = updated
            self._write(payload)
            return self._normalize(updated)
        raise ValueError("Nao encontrei a regra de versao usuario (cópia editavel) para restaurar.")

    def restore_points_user_copy_to_defaults(self, reset_image: bool = True) -> MarkerRule:
        payload = self._read()
        now = datetime.now().isoformat(timespec="seconds")
        texts = default_points_af_rule_texts()
        ph = self._ensure_builtin_placeholder_image()
        itens = itens_from_default_texts_points()
        for idx, raw in enumerate(payload.get("rules", [])):
            if raw.get("seed_role") != SEED_ROLE_POINTS_USER_COPY:
                continue
            rid = int(raw.get("id", 0))
            image_name = str(raw.get("imagem_exemplo_nome", ""))
            image_path = str(raw.get("imagem_exemplo_path", ""))
            if reset_image:
                image_name, image_path = self._copy_image(str(ph), rid)
                image_path = str(image_path)
            updated = finalize_rule_dict_for_write(
                {
                    **raw,
                    "nome_regra": default_points_user_copy_rule_display_name(),
                    "tipo_marcador": "pontos",
                    "ativo": True,
                    "descricao_geral": texts["descricao_geral"],
                    "protocolo": protocolo_dict_from_itens(itens),
                    "imagem_exemplo_nome": image_name,
                    "imagem_exemplo_path": image_path,
                    "atualizado_em": now,
                    "seed_role": SEED_ROLE_POINTS_USER_COPY,
                }
            )
            payload["rules"][idx] = updated
            self._write(payload)
            return self._normalize(updated)
        raise ValueError("Nao encontrei a regra de versao usuario (pontos A-F) para restaurar.")

    def _ensure_builtin_placeholder_image(self) -> Path:
        path = self.images_dir / BUILTIN_PLACEHOLDER_NAME
        if not path.exists():
            Image.new("RGB", (8, 8), color=(245, 245, 245)).save(path, format="PNG")
        return path

    def list_rules(self) -> list[MarkerRule]:
        payload = self._read()
        return [self._normalize(item) for item in payload.get("rules", [])]

    def get_rule(self, rule_id: int) -> MarkerRule | None:
        for rule in self.list_rules():
            if rule.id == rule_id:
                return rule
        return None

    def create_rule(self, data: dict[str, Any], image_source_path: str) -> MarkerRule:
        itens = parse_itens_from_form_data(data)
        tipo = str(data.get("tipo_marcador", "linhas")).strip().lower() or "linhas"
        validate_itens_obrigatorios(tipo, itens)
        payload = self._read()
        now = datetime.now().isoformat(timespec="seconds")
        next_id = int(payload.get("next_id", 1))
        image_name, image_path = self._copy_image(image_source_path, next_id)
        record = finalize_rule_dict_for_write(
            {
                "id": next_id,
                "nome_regra": str(data.get("nome_regra", "")).strip(),
                "tipo_marcador": tipo,
                "ativo": bool(data.get("ativo", True)),
                "descricao_geral": str(data.get("descricao_geral", "")).strip(),
                "protocolo": protocolo_dict_from_itens(itens),
                "imagem_exemplo_path": str(image_path),
                "imagem_exemplo_nome": image_name,
                "criado_em": now,
                "atualizado_em": now,
                "seed_role": None,
            }
        )
        payload["rules"].append(record)
        payload["next_id"] = next_id + 1
        self._write(payload)
        return self._normalize(record)

    def update_rule(
        self,
        rule_id: int,
        data: dict[str, Any],
        image_source_path: str | None = None,
    ) -> MarkerRule:
        payload = self._read()
        now = datetime.now().isoformat(timespec="seconds")
        for idx, raw in enumerate(payload.get("rules", [])):
            if int(raw.get("id", 0)) != rule_id:
                continue
            row = self._normalize(raw)
            image_name = row.imagem_exemplo_nome
            image_path = row.imagem_exemplo_path
            if image_source_path:
                image_name, copied = self._copy_image(image_source_path, rule_id)
                image_path = str(copied)
            itens = parse_itens_from_form_data({**data, "tipo_marcador": data.get("tipo_marcador", row.tipo_marcador)})
            tipo = str(data.get("tipo_marcador", row.tipo_marcador)).strip().lower() or "linhas"
            validate_itens_obrigatorios(tipo, itens)
            merged = {
                "id": row.id,
                "nome_regra": str(data.get("nome_regra", row.nome_regra)).strip(),
                "tipo_marcador": tipo,
                "ativo": bool(data.get("ativo", row.ativo)),
                "descricao_geral": str(data.get("descricao_geral", row.descricao_geral)).strip(),
                "protocolo": protocolo_dict_from_itens(itens),
                "imagem_exemplo_nome": image_name,
                "imagem_exemplo_path": image_path,
                "criado_em": row.criado_em,
                "atualizado_em": now,
                "seed_role": row.seed_role,
            }
            updated = finalize_rule_dict_for_write(merged)
            payload["rules"][idx] = updated
            self._write(payload)
            return self._normalize(updated)
        raise ValueError("Regra nao encontrada.")

    def delete_rule(self, rule_id: int) -> None:
        payload = self._read()
        current = payload.get("rules", [])
        for r in current:
            if int(r.get("id", 0)) != rule_id:
                continue
            if r.get("seed_role") in (SEED_ROLE_ABCD_REFERENCE, SEED_ROLE_POINTS_REFERENCE):
                raise ValueError("A regra de referência do sistema não pode ser excluída.")
        payload["rules"] = [r for r in current if int(r.get("id", 0)) != rule_id]
        self._write(payload)

    def _copy_image(self, source: str, rule_id: int) -> tuple[str, Path]:
        src = Path(source)
        if not src.exists():
            raise ValueError("Imagem de exemplo nao encontrada.")
        suffix = src.suffix.lower() or ".png"
        safe_name = f"rule_{rule_id}_{uuid4().hex[:8]}{suffix}"
        dst = self.images_dir / safe_name
        shutil.copy2(src, dst)
        return src.name, dst.resolve()

    def _normalize(self, raw: dict[str, Any]) -> MarkerRule:
        return normalize_rule_from_raw(raw)

    def _read(self) -> dict[str, Any]:
        try:
            return json.loads(self.rules_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, FileNotFoundError):
            return {"next_id": 1, "rules": []}

    @staticmethod
    def _strip_legacy_racional_keys(payload: dict[str, Any]) -> None:
        for r in payload.get("rules", []):
            if isinstance(r, dict):
                for k in ("racional_a", "racional_b", "racional_c", "racional_d"):
                    r.pop(k, None)

    def _write(self, payload: dict[str, Any]) -> None:
        self._strip_legacy_racional_keys(payload)
        new_rules: list[dict[str, Any]] = []
        for r in payload.get("rules", []):
            if isinstance(r, dict):
                new_rules.append(finalize_rule_dict_for_write(dict(r)))
            else:
                new_rules.append(r)
        payload["rules"] = new_rules
        self.rules_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
