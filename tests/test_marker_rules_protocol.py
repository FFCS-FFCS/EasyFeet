"""Testes do modelo protocolo.itens (regras de marcador)."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

from easyfeet.marker_rules_store import (
    MarkerRuleStore,
    ProtocoloItem,
    finalize_rule_dict_for_write,
    normalize_rule_from_raw,
    parse_itens_from_form_data,
    parse_itens_from_raw,
    validate_itens_obrigatorios,
)


class TestProtocolParsing(unittest.TestCase):
    def test_legacy_linhas_to_four_items(self) -> None:
        raw = {
            "id": 1,
            "tipo_marcador": "linhas",
            "definicao_a": "ta",
            "definicao_b": "tb",
            "definicao_c": "tc",
            "definicao_d": "td",
            "definicao_e": "ignored",
            "definicao_f": "ignored",
        }
        itens = parse_itens_from_raw(raw)
        self.assertEqual(len(itens), 4)
        self.assertEqual([x.rotulo for x in itens], ["A", "B", "C", "D"])
        self.assertEqual([x.texto for x in itens], ["ta", "tb", "tc", "td"])

    def test_legacy_pontos_six_items(self) -> None:
        raw = {
            "tipo_marcador": "pontos",
            "definicao_a": "a",
            "definicao_b": "b",
            "definicao_c": "c",
            "definicao_d": "d",
            "definicao_e": "e",
            "definicao_f": "f",
        }
        itens = parse_itens_from_raw(raw)
        self.assertEqual(len(itens), 6)
        self.assertEqual(itens[5].rotulo, "F")
        self.assertEqual(itens[5].texto, "f")

    def test_new_protocolo_preferred_over_legacy(self) -> None:
        raw = {
            "tipo_marcador": "linhas",
            "definicao_a": "old",
            "protocolo": {
                "versao": 1,
                "itens": [
                    {"ordem": 1, "rotulo": "A", "texto": "na"},
                    {"ordem": 2, "rotulo": "B", "texto": "nb"},
                    {"ordem": 3, "rotulo": "C", "texto": "nc"},
                    {"ordem": 4, "rotulo": "D", "texto": "nd"},
                ],
            },
        }
        itens = parse_itens_from_raw(raw)
        self.assertEqual([x.texto for x in itens], ["na", "nb", "nc", "nd"])


class TestValidation(unittest.TestCase):
    def test_validate_rejects_empty_texto(self) -> None:
        it = (
            ProtocoloItem(1, "A", "x"),
            ProtocoloItem(2, "B", ""),
            ProtocoloItem(3, "C", "z"),
            ProtocoloItem(4, "D", "w"),
        )
        with self.assertRaises(ValueError) as ctx:
            validate_itens_obrigatorios("linhas", it)
        self.assertIn("obrigatorio", str(ctx.exception).lower())

    def test_validate_rejects_wrong_rotulo(self) -> None:
        it = (
            ProtocoloItem(1, "A", "a"),
            ProtocoloItem(2, "X", "b"),
            ProtocoloItem(3, "C", "c"),
            ProtocoloItem(4, "D", "d"),
        )
        with self.assertRaises(ValueError):
            validate_itens_obrigatorios("linhas", it)

    def test_validate_accepts_full_line_rule(self) -> None:
        it = tuple(
            ProtocoloItem(i + 1, r, r.lower())
            for i, r in enumerate(("A", "B", "C", "D"))
        )
        validate_itens_obrigatorios("linhas", it)


class TestFinalizeStorage(unittest.TestCase):
    def test_finalize_removes_legacy_keys(self) -> None:
        raw = {
            "id": 9,
            "nome_regra": "t",
            "tipo_marcador": "linhas",
            "ativo": True,
            "descricao_geral": "d",
            "definicao_a": "a",
            "definicao_b": "b",
            "definicao_c": "c",
            "definicao_d": "dd",
            "imagem_exemplo_path": "/x",
            "imagem_exemplo_nome": "p.png",
            "criado_em": "t0",
            "atualizado_em": "t1",
            "seed_role": None,
        }
        out = finalize_rule_dict_for_write(raw)
        for k in ("definicao_a", "definicao_b", "definicao_c", "definicao_d"):
            self.assertNotIn(k, out)
        self.assertIn("protocolo", out)
        self.assertEqual(len(out["protocolo"]["itens"]), 4)


class TestFormParsing(unittest.TestCase):
    def test_parse_itens_from_form_data(self) -> None:
        data = {
            "tipo_marcador": "linhas",
            "protocolo": {
                "itens": [
                    {"ordem": 1, "rotulo": "A", "texto": "1"},
                    {"ordem": 2, "rotulo": "B", "texto": "2"},
                    {"ordem": 3, "rotulo": "C", "texto": "3"},
                    {"ordem": 4, "rotulo": "D", "texto": "4"},
                ]
            },
        }
        itens = parse_itens_from_form_data(data)
        self.assertEqual(len(itens), 4)


class TestMarkerRuleStoreMigration(unittest.TestCase):
    def test_init_migrates_legacy_json(self) -> None:
        import shutil

        tmp = Path(self.__class__.__name__ + "_data")
        tmp.mkdir(exist_ok=True)
        self.addCleanup(lambda: shutil.rmtree(tmp, ignore_errors=True))
        rules_path = tmp / "marker_rules.json"
        images_dir = tmp / "marker_rule_images"
        from PIL import Image

        Image.new("RGB", (2, 2), (0, 0, 0)).save(tmp / "p.png")
        img_path = str((tmp / "p.png").resolve())
        # Duas seeds minimas para nao disparar `ensure_initial_*` que acrescenta linhas/pontos.
        legacy = {
            "next_id": 3,
            "rules": [
                {
                    "id": 1,
                    "nome_regra": "R",
                    "tipo_marcador": "linhas",
                    "ativo": True,
                    "descricao_geral": "dg",
                    "definicao_a": "da",
                    "definicao_b": "db",
                    "definicao_c": "dc",
                    "definicao_d": "dd",
                    "imagem_exemplo_path": img_path,
                    "imagem_exemplo_nome": "p.png",
                    "criado_em": "c",
                    "atualizado_em": "u",
                    "seed_role": "abcd_reference",
                },
                {
                    "id": 2,
                    "nome_regra": "P ref",
                    "tipo_marcador": "pontos",
                    "ativo": False,
                    "descricao_geral": "dgp",
                    "definicao_a": "pa",
                    "definicao_b": "pb",
                    "definicao_c": "pc",
                    "definicao_d": "pd",
                    "definicao_e": "pe",
                    "definicao_f": "pf",
                    "imagem_exemplo_path": img_path,
                    "imagem_exemplo_nome": "p.png",
                    "criado_em": "c",
                    "atualizado_em": "u",
                    "seed_role": "points_af_reference",
                },
            ],
        }
        rules_path.write_text(json.dumps(legacy), encoding="utf-8")

        MarkerRuleStore(rules_path=rules_path, images_dir=images_dir)

        payload = json.loads(rules_path.read_text(encoding="utf-8"))
        self.assertEqual(len(payload["rules"]), 2)
        r0 = payload["rules"][0]
        self.assertIn("protocolo", r0)
        self.assertNotIn("definicao_a", r0)
        rule = normalize_rule_from_raw(r0)
        self.assertEqual(len(rule.itens), 4)
        self.assertEqual(rule.itens[0].texto, "da")
        r1 = payload["rules"][1]
        self.assertEqual(len(r1["protocolo"]["itens"]), 6)


if __name__ == "__main__":
    unittest.main()
