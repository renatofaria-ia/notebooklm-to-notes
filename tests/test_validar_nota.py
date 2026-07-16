import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "scripts" / "validar_nota.py"
EXAMPLE = ROOT / "references" / "exemplo-okf.md"
VALID = ROOT / "tests" / "nota-valida.md"
MINDMAP = ROOT / "tests" / "nota-mindmap-com-aspas.md"


def run(*args):
    return subprocess.run([sys.executable, str(VALIDATOR), *map(str, args)], capture_output=True, text=True, encoding="utf-8")


class ValidatorTests(unittest.TestCase):
    def write(self, folder, name, content):
        path = Path(folder) / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path

    def test_portable_fixture_stays_valid(self):
        self.assertEqual(run(VALID).returncode, 0)

    def test_okf_example_is_valid(self):
        self.assertEqual(run("--profile", "okf", EXAMPLE).returncode, 0)

    def test_okf_requires_type(self):
        with tempfile.TemporaryDirectory() as folder:
            note = self.write(folder, "note.md", "---\nsource: teste\n---\n# Nota\n")
            self.assertEqual(run("--profile", "okf", note).returncode, 1)

    def test_okf_rejects_empty_type(self):
        with tempfile.TemporaryDirectory() as folder:
            note = self.write(folder, "note.md", "---\ntype: \"\"\n---\n# Nota\n")
            self.assertEqual(run("--profile", "okf", note).returncode, 1)

    def test_okf_rejects_wikilink(self):
        with tempfile.TemporaryDirectory() as folder:
            note = self.write(folder, "note.md", "---\ntype: note\n---\n# Nota\n[[outra]]\n")
            self.assertEqual(run("--profile", "okf", note).returncode, 1)

    def test_okf_rejects_unclosed_frontmatter(self):
        with tempfile.TemporaryDirectory() as folder:
            note = self.write(folder, "note.md", "---\ntype: note\n# Nota\n")
            self.assertEqual(run("--profile", "okf", note).returncode, 1)

    def test_okf_rejects_absolute_link(self):
        with tempfile.TemporaryDirectory() as folder:
            note = self.write(folder, "note.md", "---\ntype: note\n---\n# Nota\n[x](/tmp/a.md)\n")
            self.assertEqual(run("--profile", "okf", note).returncode, 1)

    def test_root_index_is_reserved(self):
        with tempfile.TemporaryDirectory() as folder:
            note = self.write(folder, "index.md", "---\ntype: note\n---\n# Nota\n")
            self.assertEqual(run("--profile", "okf", "--vault-root", folder, note).returncode, 1)

    def test_nested_index_is_not_reserved(self):
        with tempfile.TemporaryDirectory() as folder:
            note = self.write(folder, "sub/index.md", "---\ntype: note\n---\n# Nota\n")
            self.assertEqual(run("--profile", "okf", "--vault-root", folder, note).returncode, 0)

    def test_utf8_portuguese_and_emoji_are_valid(self):
        with tempfile.TemporaryDirectory() as folder:
            note = self.write(folder, "nota.md", "---\ntype: pesquisa\nsource: fonte conhecida\n---\n# 🧠 Coração e ação\n")
            self.assertEqual(run("--profile", "okf", note).returncode, 0)

    def test_existing_mindmap_fixture_fails(self):
        self.assertEqual(run(MINDMAP).returncode, 1)


if __name__ == "__main__":
    unittest.main()