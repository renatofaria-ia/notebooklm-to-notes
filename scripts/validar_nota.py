#!/usr/bin/env python3
"""Valida conceitos e bundles Open Knowledge Format (OKF) 0.1."""
from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError as error:
    raise SystemExit("PyYAML e obrigatorio. Instale com: pip install -r requirements.txt") from error

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

RESERVED = {"index.md", "log.md"}
DRIVE_PATH = re.compile(r"^[A-Za-z]:[\\/]")
MARKDOWN_LINK = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
ISO_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


@dataclass
class Report:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    infos: list[str] = field(default_factory=list)

    def extend(self, other: "Report", prefix: str = "") -> None:
        self.errors.extend(f"{prefix}{item}" for item in other.errors)
        self.warnings.extend(f"{prefix}{item}" for item in other.warnings)
        self.infos.extend(f"{prefix}{item}" for item in other.infos)


def split_frontmatter(text: str) -> tuple[dict[str, Any] | None, str, str | None]:
    if not text.startswith("---\n") and not text.startswith("---\r\n"):
        return None, text, None
    lines = text.splitlines()
    for index, line in enumerate(lines[1:], 1):
        if line == "---":
            raw_yaml = "\n".join(lines[1:index])
            try:
                value = yaml.safe_load(raw_yaml)
            except yaml.YAMLError as error:
                return None, "", f"frontmatter YAML invalido: {error.problem or 'erro de sintaxe'}"
            if value is None:
                value = {}
            if not isinstance(value, dict):
                return None, "", "frontmatter YAML deve ser um mapa de chaves e valores"
            return value, "\n".join(lines[index + 1:]), None
    return None, "", "frontmatter sem fechamento"


def read_utf8(path: Path) -> tuple[str | None, Report]:
    report = Report()
    try:
        raw = path.read_bytes()
    except FileNotFoundError:
        report.errors.append("arquivo nao encontrado")
        return None, report
    if raw.startswith(b"\xef\xbb\xbf"):
        report.errors.append("UTF-8 BOM nao permitido")
    try:
        return raw.decode("utf-8"), report
    except UnicodeDecodeError:
        report.errors.append("arquivo nao e legivel em UTF-8")
        return None, report


def validate_editorial(text: str, report: Report) -> None:
    if re.search(r"^# .+", text, re.MULTILINE):
        report.infos.append("H1 presente")
    else:
        report.warnings.append("conceito sem H1; OKF permite, mas a skill gera H1")
    fences = len(re.findall(r"^```", text, re.MULTILINE))
    if fences % 2:
        report.errors.append("fences desbalanceados")
    else:
        report.infos.append(f"fences balanceados ({fences})")
    mojibake = re.search(r"(?:\u00c3[\x80-\xbf]|\u00c2[\x80-\xbf]|\u00e2[\x80-\xbf]{2}|\u00f0\u0178)", text)
    broken_question = any(
        re.search(r"(?<=[A-Za-z\u00c0-\u00ff])\?(?=[A-Za-z\u00c0-\u00ff])", line)
        for line in text.splitlines()
        if "://" not in line
    )
    if "\ufffd" in text or mojibake or "??" in text or broken_question:
        report.errors.append("possivel corrupcao de UTF-8")
    blocks = re.findall(r"^```mermaid\s*\n(.*?)^```", text, re.MULTILINE | re.DOTALL)
    if any(entity in block for block in blocks for entity in ("&quot;", "&amp;", "&lt;", "&gt;", "&#")):
        report.errors.append("entidade HTML dentro de Mermaid")
    if any(
        block.lstrip().startswith("mindmap")
        and any(line.strip().startswith('"') and line.strip().endswith('"') for line in block.splitlines())
        for block in blocks
    ):
        report.errors.append("rotulo entre aspas no mindmap")


def validate_links(text: str, report: Report) -> None:
    for target in MARKDOWN_LINK.findall(text):
        target = target.strip()
        if target.lower().startswith("file://") or DRIVE_PATH.match(target):
            report.errors.append("caminho local do sistema nao permitido em links OKF")
            break
    if "[[" in text:
        report.warnings.append("wikilink encontrado; prefira link Markdown padrao do OKF")


def valid_timestamp(value: Any) -> bool:
    if isinstance(value, datetime):
        return True
    if not isinstance(value, str):
        return False
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
        return True
    except ValueError:
        return False


def validate_concept(path: Path) -> Report:
    text, report = read_utf8(path)
    if text is None:
        return report
    metadata, body, frontmatter_error = split_frontmatter(text)
    if frontmatter_error:
        report.errors.append(frontmatter_error)
        return report
    if metadata is None:
        report.errors.append("conceito OKF exige frontmatter YAML")
        return report
    type_value = metadata.get("type")
    if not isinstance(type_value, str) or not type_value.strip():
        report.errors.append("conceito OKF exige type nao vazio")
    for key in ("title", "description"):
        if key not in metadata:
            report.warnings.append(f"campo recomendado ausente: {key}")
    if "tags" in metadata and (
        not isinstance(metadata["tags"], list) or not all(isinstance(tag, str) for tag in metadata["tags"])
    ):
        report.warnings.append("tags deveria ser uma lista YAML de strings")
    if "timestamp" in metadata and not valid_timestamp(metadata["timestamp"]):
        report.warnings.append("timestamp deveria usar ISO 8601")
    validate_editorial(body, report)
    validate_links(body, report)
    if "# Citations" not in body:
        report.warnings.append("sem # Citations; inclua fontes para alegacoes externas")
    return report


def validate_index(path: Path, bundle_root: Path) -> Report:
    text, report = read_utf8(path)
    if text is None:
        return report
    metadata, body, frontmatter_error = split_frontmatter(text)
    if frontmatter_error:
        report.errors.append(frontmatter_error)
        return report
    if metadata is not None:
        if path.parent != bundle_root:
            report.errors.append("index.md fora da raiz nao pode ter frontmatter")
        elif set(metadata) != {"okf_version"} or str(metadata.get("okf_version")) != "0.1":
            report.errors.append("frontmatter do index raiz deve conter somente okf_version: '0.1'")
    elif path.parent == bundle_root:
        report.warnings.append("index raiz sem okf_version: '0.1'")
    if not re.search(r"^# .+", body, re.MULTILINE):
        report.errors.append("index.md exige pelo menos uma secao H1")
    if not re.search(r"^\s*[*-] \[[^\]]+\]\([^)]+\)\s*-\s+.+", body, re.MULTILINE):
        report.errors.append("index.md exige itens Markdown com descricao")
    validate_links(body, report)
    return report


def validate_log(path: Path) -> Report:
    text, report = read_utf8(path)
    if text is None:
        return report
    metadata, body, frontmatter_error = split_frontmatter(text)
    if frontmatter_error:
        report.errors.append(frontmatter_error)
        return report
    if metadata is not None:
        report.errors.append("log.md nao pode ter frontmatter")
    if not re.search(r"^# .+", body, re.MULTILINE):
        report.errors.append("log.md exige titulo H1")
    dates = re.findall(r"^## (.+)$", body, re.MULTILINE)
    if not dates:
        report.errors.append("log.md exige ao menos uma data ISO 8601")
    elif any(not ISO_DATE.fullmatch(date) for date in dates):
        report.errors.append("datas de log.md devem usar YYYY-MM-DD")
    elif dates != sorted(dates, reverse=True):
        report.errors.append("datas de log.md devem estar da mais recente para a mais antiga")
    if dates and not re.search(r"^\* \*\*.+?\*\*:", body, re.MULTILINE):
        report.errors.append("log.md exige entradas em lista com rotulo em negrito")
    validate_links(body, report)
    return report


def validate_path(path: Path, bundle_root: Path | None, profile: str) -> Report:
    if profile == "portable":
        text, report = read_utf8(path)
        if text is not None:
            validate_editorial(text, report)
        return report
    if path.name.lower() == "index.md":
        return validate_index(path, bundle_root or path.parent)
    if path.name.lower() == "log.md":
        return validate_log(path)
    return validate_concept(path)


def validate_bundle(bundle_root: Path) -> Report:
    report = Report()
    if not bundle_root.is_dir():
        report.errors.append("bundle nao encontrado ou nao e diretorio")
        return report
    markdown_files = sorted(bundle_root.rglob("*.md"))
    if not markdown_files:
        report.errors.append("bundle nao contem arquivos Markdown")
        return report
    for path in markdown_files:
        report.extend(validate_path(path, bundle_root, "okf"), f"{path.relative_to(bundle_root)}: ")
    root_names = {path.name.lower() for path in markdown_files if path.parent == bundle_root}
    for reserved in RESERVED:
        if reserved not in root_names:
            report.warnings.append(f"arquivo recomendado ausente na raiz: {reserved}")
    return report


def print_report(report: Report) -> None:
    for item in report.infos:
        print(f"  OK {item}")
    for item in report.warnings:
        print(f"  AVISO {item}")
    for item in report.errors:
        print(f"  ERRO {item}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("arquivo", nargs="?", type=Path, help="conceito ou arquivo reservado")
    parser.add_argument("--bundle", type=Path, help="valida todos os Markdown de um bundle OKF")
    parser.add_argument("--profile", choices=("okf", "portable"), default="okf")
    parser.add_argument("--vault-root", type=Path, help=argparse.SUPPRESS)
    args = parser.parse_args()
    if bool(args.arquivo) == bool(args.bundle):
        parser.error("informe um arquivo ou --bundle <diretorio>")
    if args.bundle:
        print(f"Validando bundle: {args.bundle} (OKF 0.1)")
        report = validate_bundle(args.bundle)
    else:
        print(f"Validando: {args.arquivo} (perfil {args.profile})")
        report = validate_path(args.arquivo, args.vault_root, args.profile)
    print_report(report)
    return 1 if report.errors else 0


if __name__ == "__main__":
    raise SystemExit(main())