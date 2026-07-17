import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "scripts" / "validar_nota.py"
FIXTURE_BUNDLE = ROOT / "tests" / "fixtures" / "bundle-valido"
DECK_FIXTURE = ROOT / "tests" / "fixtures" / "deck-valido"
LEGACY = ROOT / "tests" / "nota-valida.md"
MINDMAP = ROOT / "tests" / "nota-mindmap-com-aspas.md"
FIDELITY_FIXTURE = ROOT / "tests" / "fixtures" / "deck-fidelidade-valido"


def run(*args):
    return subprocess.run(
        [sys.executable, str(VALIDATOR), *map(str, args)],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )


class ValidatorTests(unittest.TestCase):
    def write(self, folder, name, content):
        path = Path(folder) / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path

    def concept(self, extra="", body="# Conceito\n\n# Citations\n\n[1] [Origem](https://example.com)\n"):
        return (
            "---\n"
            "type: NotebookLM Summary\n"
            "title: Conceito\n"
            "description: Uma descrição de teste.\n"
            "tags: [teste]\n"
            "timestamp: 2026-07-16T12:00:00-03:00\n"
            f"{extra}"
            "---\n\n"
            f"{body}"
        )

    def test_valid_bundle_is_conformant(self):
        result = run("--bundle", FIXTURE_BUNDLE)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_pt_br_bundle_fixture_is_valid(self):
        result = run("--bundle", FIXTURE_BUNDLE, "--pt-br")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_default_profile_validates_okf_concept(self):
        with tempfile.TemporaryDirectory() as folder:
            note = self.write(folder, "conceito.md", self.concept())
            self.assertEqual(run(note).returncode, 0)

    def test_portable_legacy_remains_explicitly_available(self):
        self.assertEqual(run("--profile", "portable", LEGACY).returncode, 0)

    def test_missing_type_fails(self):
        with tempfile.TemporaryDirectory() as folder:
            note = self.write(folder, "conceito.md", "---\ntitle: Sem tipo\n---\n# Nota\n")
            self.assertEqual(run(note).returncode, 1)

    def test_empty_type_fails(self):
        with tempfile.TemporaryDirectory() as folder:
            note = self.write(folder, "conceito.md", "---\ntype: \"\"\n---\n# Nota\n")
            self.assertEqual(run(note).returncode, 1)

    def test_invalid_yaml_fails(self):
        with tempfile.TemporaryDirectory() as folder:
            note = self.write(folder, "conceito.md", "---\ntype: [\n---\n# Nota\n")
            self.assertEqual(run(note).returncode, 1)

    def test_bundle_relative_absolute_link_is_accepted(self):
        with tempfile.TemporaryDirectory() as folder:
            body = "# Nota\n\nLeia [fonte](/sources/fonte.md).\n\n# Citations\n\n[1] [Fonte](/sources/fonte.md)\n"
            note = self.write(folder, "conceito.md", self.concept(body=body))
            self.assertEqual(run(note).returncode, 0)

    def test_quoted_yaml_title_with_colon_is_valid(self):
        with tempfile.TemporaryDirectory() as folder:
            content = self.concept().replace("title: Conceito", 'title: "Conceito: com dois-pontos"')
            note = self.write(folder, "conceito.md", content)
            self.assertEqual(run(note).returncode, 0)

    def test_relative_link_is_accepted(self):
        with tempfile.TemporaryDirectory() as folder:
            body = "# Nota\n\nLeia [fonte](./fonte.md).\n\n# Citations\n\n[1] [Fonte](./fonte.md)\n"
            note = self.write(folder, "conceito.md", self.concept(body=body))
            self.assertEqual(run(note).returncode, 0)

    def test_file_uri_is_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            note = self.write(folder, "conceito.md", self.concept(body="# Nota\n\n[x](file:///tmp/a.md)\n"))
            self.assertEqual(run(note).returncode, 1)

    def test_extra_frontmatter_is_accepted(self):
        with tempfile.TemporaryDirectory() as folder:
            note = self.write(folder, "conceito.md", self.concept("notebook_id: conhecido\nsource_status: ready\n"))
            self.assertEqual(run(note).returncode, 0)

    def test_broken_link_is_accepted(self):
        with tempfile.TemporaryDirectory() as folder:
            body = "# Nota\n\n[Em breve](/sources/ainda-nao-existe.md)\n\n# Citations\n\n[1] [Em breve](/sources/ainda-nao-existe.md)\n"
            note = self.write(folder, "conceito.md", self.concept(body=body))
            self.assertEqual(run(note).returncode, 0)

    def test_reserved_index_cannot_be_concept(self):
        with tempfile.TemporaryDirectory() as folder:
            bundle = Path(folder)
            self.write(bundle, "index.md", "---\ntype: Conceito\n---\n# Índice\n")
            result = run("--bundle", bundle)
            self.assertEqual(result.returncode, 1)
            self.assertIn("somente okf_version", result.stdout)

    def test_log_requires_iso_dates(self):
        with tempfile.TemporaryDirectory() as folder:
            bundle = Path(folder)
            self.write(bundle, "log.md", "# Histórico do diretório\n\n## ontem\n\n* **Criação**: teste\n")
            result = run("--bundle", bundle)
            self.assertEqual(result.returncode, 1)
            self.assertIn("YYYY-MM-DD", result.stdout)

    def test_wikilink_is_warning_not_error(self):
        with tempfile.TemporaryDirectory() as folder:
            body = "# Nota\n\n[[legado]]\n\n# Citations\n\n[1] [Origem](https://example.com)\n"
            note = self.write(folder, "conceito.md", self.concept(body=body))
            result = run(note)
            self.assertEqual(result.returncode, 0)
            self.assertIn("AVISO wikilink", result.stdout)

    def test_existing_mindmap_fixture_fails_in_portable_mode(self):
        self.assertEqual(run("--profile", "portable", MINDMAP).returncode, 1)

    def test_pt_br_mode_rejects_unaccented_narrative(self):
        with tempfile.TemporaryDirectory() as folder:
            body = "# Sintese\n\nA sintese orienta a automacao.\n\n# Citations\n"
            note = self.write(folder, "conceito.md", self.concept(body=body))
            result = run(note, "--pt-br")
            self.assertEqual(result.returncode, 1)
            self.assertIn("síntese", result.stdout)
            self.assertIn("automação", result.stdout)

    def test_pt_br_mode_allows_valid_demonstrative_esta(self):
        with tempfile.TemporaryDirectory() as folder:
            body = "# Nota\n\nEsta s\u00edntese est\u00e1 pronta.\n\n# Citations\n"
            note = self.write(folder, "conceito.md", self.concept(body=body))
            self.assertEqual(run(note, "--pt-br").returncode, 0)

    def test_pt_br_mode_ignores_tags_code_and_link_targets(self):
        with tempfile.TemporaryDirectory() as folder:
            body = (
                "# Síntese\n\nA automação está pronta. Veja [a síntese](/sintese.md).\n\n"
                "```python\nslug = 'automacao'\n```\n\n# Citations\n"
            )
            note = self.write(folder, "conceito.md", self.concept("tags: [automacao]\n", body))
            self.assertEqual(run(note, "--pt-br").returncode, 0)


    def test_valid_progressive_deck_is_conformant(self):
        result = run("--deck", DECK_FIXTURE, "--pt-br")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_deck_requires_notebook_provenance(self):
        with tempfile.TemporaryDirectory() as folder:
            deck = Path(folder) / "deck"
            shutil.copytree(DECK_FIXTURE, deck)
            summary = deck / "notebooks" / "curso-teste" / "curso-teste.md"
            summary.write_text(summary.read_text(encoding="utf-8").replace("notebook_id: notebook-de-teste\n", ""), encoding="utf-8")
            result = run("--deck", deck)
            self.assertEqual(result.returncode, 1)
            self.assertIn("exige notebook_id", result.stdout)

    def test_deck_rejects_broken_generated_link(self):
        with tempfile.TemporaryDirectory() as folder:
            deck = Path(folder) / "deck"
            shutil.copytree(DECK_FIXTURE, deck)
            index = deck / "notebooks" / "curso-teste" / "index.md"
            index.write_text(index.read_text(encoding="utf-8").replace("curso-teste.md", "ausente.md"), encoding="utf-8")
            result = run("--deck", deck)
            self.assertEqual(result.returncode, 1)
            self.assertIn("link interno gerado não encontrado", result.stdout)


    def test_deck_allows_summary_without_source_concepts(self):
        with tempfile.TemporaryDirectory() as folder:
            deck = Path(folder) / "deck"
            shutil.copytree(DECK_FIXTURE, deck)
            shutil.rmtree(deck / "notebooks" / "curso-teste" / "sources")
            index = deck / "notebooks" / "curso-teste" / "index.md"
            index.write_text("# Curso de teste\n\n* [Sintese](/notebooks/curso-teste/curso-teste.md) - Visao geral.\n", encoding="utf-8")
            summary = deck / "notebooks" / "curso-teste" / "curso-teste.md"
            summary.write_text(
                (summary.read_text(encoding="utf-8")
                .replace("Leia a [fonte de teste](/notebooks/curso-teste/sources/fonte-teste.md).", "Fonte identificada: source-de-teste.")
                .replace("[1] [Fonte de teste](/notebooks/curso-teste/sources/fonte-teste.md)", "[1] Fonte identificada: source-de-teste")),
                encoding="utf-8",
            )
            self.assertEqual(run("--deck", deck).returncode, 0)

    def copy_fidelity_deck(self, folder):
        deck = Path(folder) / "deck"
        shutil.copytree(FIDELITY_FIXTURE, deck)
        return deck

    def test_valid_evidence_first_deck_is_conformant(self):
        result = run("--deck", FIDELITY_FIXTURE, "--fidelity", "--pt-br")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_fidelity_rejects_invalid_raw_json(self):
        with tempfile.TemporaryDirectory() as folder:
            deck = self.copy_fidelity_deck(folder)
            raw = deck / "notebooks" / "curso-fidelidade" / "evidence" / "raw-response.json"
            raw.write_text("{", encoding="utf-8")
            result = run("--deck", deck, "--fidelity")
            self.assertEqual(result.returncode, 1)
            self.assertIn("JSON inválido", result.stdout)

    def test_fidelity_rejects_raw_response_hash_mismatch(self):
        with tempfile.TemporaryDirectory() as folder:
            deck = self.copy_fidelity_deck(folder)
            raw = deck / "notebooks" / "curso-fidelidade" / "evidence" / "raw-response.json"
            raw.write_text(raw.read_text(encoding="utf-8") + "\n", encoding="utf-8")
            result = run("--deck", deck, "--fidelity")
            self.assertEqual(result.returncode, 1)
            self.assertIn("hash de raw-response.json", result.stdout)

    def test_fidelity_rejects_missing_source_concept(self):
        with tempfile.TemporaryDirectory() as folder:
            deck = self.copy_fidelity_deck(folder)
            source = deck / "notebooks" / "curso-fidelidade" / "sources" / "fonte-fidelidade.md"
            source.unlink()
            result = run("--deck", deck, "--fidelity")
            self.assertEqual(result.returncode, 1)
            self.assertIn("fontes sem conceito", result.stdout)

    def test_fidelity_rejects_missing_evidence_category(self):
        with tempfile.TemporaryDirectory() as folder:
            deck = self.copy_fidelity_deck(folder)
            coverage = deck / "notebooks" / "curso-fidelidade" / "evidence" / "coverage.md"
            coverage.write_text(coverage.read_text(encoding="utf-8").replace("category: example", "category: invalid", 1), encoding="utf-8")
            result = run("--deck", deck, "--fidelity")
            self.assertEqual(result.returncode, 1)
            self.assertIn("categoria example", result.stdout)

    def test_fidelity_rejects_broken_evidence_destination(self):
        with tempfile.TemporaryDirectory() as folder:
            deck = self.copy_fidelity_deck(folder)
            coverage = deck / "notebooks" / "curso-fidelidade" / "evidence" / "coverage.md"
            coverage.write_text(coverage.read_text(encoding="utf-8").replace("/notebooks/curso-fidelidade/evidence/coverage.md#c1", "/notebooks/curso-fidelidade/evidence/ausente.md#c1", 1), encoding="utf-8")
            result = run("--deck", deck, "--fidelity")
            self.assertEqual(result.returncode, 1)
            self.assertIn("destination inexistente", result.stdout)

    def test_fidelity_blocks_incomplete_source_gap(self):
        with tempfile.TemporaryDirectory() as folder:
            deck = self.copy_fidelity_deck(folder)
            inventory = deck / "notebooks" / "curso-fidelidade" / "evidence" / "source-inventory.json"
            inventory.write_text(inventory.read_text(encoding="utf-8").replace('"status": "ready"', '"status": "error"'), encoding="utf-8")
            source = deck / "notebooks" / "curso-fidelidade" / "sources" / "fonte-fidelidade.md"
            source.write_text(source.read_text(encoding="utf-8").replace("type: NotebookLM Source", "type: NotebookLM Source Gap").replace("source_status: ready", "source_status: error"), encoding="utf-8")
            summary = deck / "notebooks" / "curso-fidelidade" / "curso-fidelidade.md"
            summary.write_text(summary.read_text(encoding="utf-8").replace("source_ready_count: 1", "source_ready_count: 0").replace("source_error_count: 0", "source_error_count: 1"), encoding="utf-8")
            coverage = deck / "notebooks" / "curso-fidelidade" / "evidence" / "coverage.md"
            coverage.write_text(coverage.read_text(encoding="utf-8").replace("extraction_status: complete", "extraction_status: incomplete"), encoding="utf-8")
            result = run("--deck", deck, "--fidelity")
            self.assertEqual(result.returncode, 1)
            self.assertIn("bundle incomplete", result.stdout)

    def test_pt_br_checks_mermaid_labels(self):
        with tempfile.TemporaryDirectory() as folder:
            fence = chr(96) * 3
            body = "# Síntese\n\n" + fence + "mermaid\nmindmap\n  root((Sintese))\n" + fence + "\n\n# Citations\n"
            note = self.write(folder, "conceito.md", self.concept(body=body))
            result = run(note, "--pt-br")
            self.assertEqual(result.returncode, 1)
            self.assertIn("síntese", result.stdout)


if __name__ == "__main__":
    unittest.main()