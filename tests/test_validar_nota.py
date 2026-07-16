import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "scripts" / "validar_nota.py"
FIXTURE_BUNDLE = ROOT / "tests" / "fixtures" / "bundle-valido"
LEGACY = ROOT / "tests" / "nota-valida.md"
MINDMAP = ROOT / "tests" / "nota-mindmap-com-aspas.md"


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
            "description: Uma descricao de teste.\n"
            "tags: [teste]\n"
            "timestamp: 2026-07-16T12:00:00-03:00\n"
            f"{extra}"
            "---\n\n"
            f"{body}"
        )

    def test_valid_bundle_is_conformant(self):
        result = run("--bundle", FIXTURE_BUNDLE)
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
            note = self.write(folder, "conceito.md", self.concept(body="# Nota\n\nLeia [fonte](/sources/fonte.md).\n\n# Citations\n\n[1] [Fonte](/sources/fonte.md)\n"))
            self.assertEqual(run(note).returncode, 0)

    def test_relative_link_is_accepted(self):
        with tempfile.TemporaryDirectory() as folder:
            note = self.write(folder, "conceito.md", self.concept(body="# Nota\n\nLeia [fonte](./fonte.md).\n\n# Citations\n\n[1] [Fonte](./fonte.md)\n"))
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
            note = self.write(folder, "conceito.md", self.concept(body="# Nota\n\n[Em breve](/sources/ainda-nao-existe.md)\n\n# Citations\n\n[1] [Em breve](/sources/ainda-nao-existe.md)\n"))
            self.assertEqual(run(note).returncode, 0)

    def test_reserved_index_cannot_be_concept(self):
        with tempfile.TemporaryDirectory() as folder:
            bundle = Path(folder)
            self.write(bundle, "index.md", "---\ntype: Conceito\n---\n# Indice\n")
            result = run("--bundle", bundle)
            self.assertEqual(result.returncode, 1)
            self.assertIn("somente okf_version", result.stdout)

    def test_log_requires_iso_dates(self):
        with tempfile.TemporaryDirectory() as folder:
            bundle = Path(folder)
            self.write(bundle, "log.md", "# Directory Update Log\n\n## ontem\n\n* **Creation**: teste\n")
            result = run("--bundle", bundle)
            self.assertEqual(result.returncode, 1)
            self.assertIn("YYYY-MM-DD", result.stdout)

    def test_wikilink_is_warning_not_error(self):
        with tempfile.TemporaryDirectory() as folder:
            note = self.write(folder, "conceito.md", self.concept(body="# Nota\n\n[[legado]]\n\n# Citations\n\n[1] [Origem](https://example.com)\n"))
            result = run(note)
            self.assertEqual(result.returncode, 0)
            self.assertIn("AVISO wikilink", result.stdout)

    def test_existing_mindmap_fixture_fails_in_portable_mode(self):
        self.assertEqual(run("--profile", "portable", MINDMAP).returncode, 1)


if __name__ == "__main__":
    unittest.main()