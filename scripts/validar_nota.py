#!/usr/bin/env python3
"""Validador estrutural para notas portable, obsidian e OKF."""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")


def frontmatter(text: str) -> tuple[str | None, str | None]:
    if not text.startswith("---\n") and not text.startswith("---\r\n"):
        return None, None
    lines = text.splitlines()
    for index, line in enumerate(lines[1:], 1):
        if line == "---":
            return "\n".join(lines[1:index]), "\n".join(lines[index + 1:])
    return None, "UNTERMINATED"


def validate(path: Path, profile: str, vault_root: Path | None) -> tuple[list[str], list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    infos: list[str] = []
    try:
        raw = path.read_bytes()
    except FileNotFoundError:
        return [f"arquivo nao encontrado: {path}"], warnings, infos
    if raw.startswith(b"\xef\xbb\xbf"):
        errors.append("UTF-8 BOM nao permitido")
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        return ["arquivo nao e legivel em UTF-8"], warnings, infos
    if re.search(r"^# .+", text, re.MULTILINE):
        infos.append("H1 presente")
    else:
        errors.append("sem H1")
    fences = len(re.findall(r"^```", text, re.MULTILINE))
    if fences % 2:
        errors.append("fences desbalanceados")
    else:
        infos.append(f"fences balanceados ({fences})")
    if re.search(r"[\u0400-\u04ff\u0370-\u03ff]", text):
        errors.append("caractere cirilico ou grego acidental")
    mojibake = re.search(r"(?:\u00c3[\x80-\xbf]|\u00c2[\x80-\xbf]|\u00e2[\x80-\xbf]{2}|\u00f0\u0178)", text)
    broken_question = any(re.search(r"(?<=[A-Za-z\u00c0-\u00ff])\?(?=[A-Za-z\u00c0-\u00ff])", line) for line in text.splitlines() if "://" not in line)
    if "\ufffd" in text or mojibake or "??" in text or broken_question:
        errors.append("possivel corrupcao de UTF-8")
    blocks = re.findall(r"^```mermaid\s*\n(.*?)^```", text, re.MULTILINE | re.DOTALL)
    if any(entity in block for block in blocks for entity in ("&quot;", "&amp;", "&lt;", "&gt;", "&#")):
        errors.append("entidade HTML dentro de Mermaid")
    if any(block.lstrip().startswith("mindmap") and any(line.strip().startswith('"') and line.strip().endswith('"') for line in block.splitlines()) for block in blocks):
        errors.append("rotulo entre aspas no mindmap")
    fm, body = frontmatter(text)
    if profile == "okf":
        if body == "UNTERMINATED":
            errors.append("frontmatter sem fechamento")
        elif fm is None:
            errors.append("frontmatter YAML obrigatorio no perfil okf")
        else:
            type_match = re.search(r"^type:\s*(.*?)\s*$", fm, re.MULTILINE)
            type_value = type_match.group(1).strip() if type_match else ""
            if (
                len(type_value) >= 2
                and type_value[0] == type_value[-1]
                and type_value[0] in {"\"", "'"}
            ):
                type_value = type_value[1:-1].strip()
            if not type_value:
                errors.append("campo type obrigatorio e nao vazio")
        if "[[" in text:
            errors.append("wikilinks nao permitidos no perfil okf")
        for target in re.findall(r"\[[^\]]*\]\(([^)]+)\)", text):
            target = target.strip()
            if target.startswith("/") or target.lower().startswith("file://") or re.match(r"^[A-Za-z]:[\\/]", target):
                errors.append("link local absoluto nao permitido no perfil okf")
                break
        if vault_root:
            try:
                if path.resolve().parent == vault_root.resolve() and path.name.lower() in {"index.md", "log.md"}:
                    errors.append("index.md e log.md sao reservados na raiz do bundle")
            except OSError:
                errors.append("nao foi possivel resolver o caminho do bundle")
    else:
        if fm is None:
            warnings.append("sem frontmatter no topo")
        if not blocks:
            warnings.append("nenhum diagrama Mermaid")
        if not re.search(r"^>\s*\[!", text, re.MULTILINE):
            warnings.append("nenhum callout")
    return errors, warnings, infos


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", choices=("portable", "obsidian", "okf"), default="portable")
    parser.add_argument("--vault-root", type=Path)
    parser.add_argument("arquivo", type=Path)
    args = parser.parse_args()
    errors, warnings, infos = validate(args.arquivo, args.profile, args.vault_root)
    print(f"Validando: {args.arquivo} (perfil {args.profile})")
    for item in infos:
        print(f"  OK {item}")
    for item in warnings:
        print(f"  AVISO {item}")
    for item in errors:
        print(f"  ERRO {item}")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())