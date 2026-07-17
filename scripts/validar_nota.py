#!/usr/bin/env python3
"""Valida conceitos e bundles Open Knowledge Format (OKF) 0.1."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError as error:
    raise SystemExit("PyYAML é obrigatório. Instale com: pip install -r requirements.txt") from error

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

RESERVED = {"index.md", "log.md"}
DRIVE_PATH = re.compile(r"^[A-Za-z]:[\\/]")
MARKDOWN_LINK = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
MARKDOWN_LINK_LABEL = re.compile(r"\[([^\]]*)\]\([^)]+\)")
FENCED_BLOCK = re.compile(r"^```.*?^```", re.MULTILINE | re.DOTALL)
INLINE_CODE = re.compile(r"`[^`]*`")
ISO_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

# O modo --pt-br protege a escrita humana da skill. Identificadores, tags,
# URLs e blocos de código ficam fora da verificação.
PT_BR_REQUIRED_ACCENTS = {
    "acao": "ação", "acoes": "ações", "alegacao": "alegação", "alegacoes": "alegações",
    "analise": "análise", "automacao": "automação", "autenticacao": "autenticação",
    "citacao": "citação", "citacoes": "citações", "conteudo": "conteúdo", "conteudos": "conteúdos",
    "conversao": "conversão", "criacao": "criação", "demonstracao": "demonstração",
    "descricao": "descrição", "diretorio": "diretório", "extracao": "extração", "facil": "fácil",
    "geracao": "geração", "indexacao": "indexação", "informacao": "informação", "ingestao": "ingestão",
    "integracao": "integração", "memoria": "memória", "nao": "não", "operacao": "operação",
    "operacoes": "operações", "orquestracao": "orquestração", "padrao": "padrão",
    "proveniencia": "proveniência", "publicacao": "publicação", "relacao": "relação",
    "relacoes": "relações", "revisao": "revisão", "selecao": "seleção", "sessao": "sessão",
    "sintese": "síntese", "tambem": "também", "usuario": "usuário", "usuarios": "usuários",
    "util": "útil", "validacao": "validação", "video": "vídeo", "videos": "vídeos",
    "visao": "visão", "voce": "você",
}


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
                return None, "", f"frontmatter YAML inválido: {error.problem or 'erro de sintaxe'}"
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
        report.errors.append("arquivo não encontrado")
        return None, report
    if raw.startswith(b"\xef\xbb\xbf"):
        report.errors.append("UTF-8 BOM não permitido")
    try:
        return raw.decode("utf-8"), report
    except UnicodeDecodeError:
        report.errors.append("arquivo não é legível em UTF-8")
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
        report.errors.append("possível corrupção de UTF-8")
    blocks = re.findall(r"^```mermaid\s*\n(.*?)^```", text, re.MULTILINE | re.DOTALL)
    if any(entity in block for block in blocks for entity in ("&quot;", "&amp;", "&lt;", "&gt;", "&#")):
        report.errors.append("entidade HTML dentro de Mermaid")
    if any(
        block.lstrip().startswith("mindmap")
        and any(line.strip().startswith('"') and line.strip().endswith('"') for line in block.splitlines())
        for block in blocks
    ):
        report.errors.append("rótulo entre aspas no mindmap")


def validate_links(text: str, report: Report) -> None:
    for target in MARKDOWN_LINK.findall(text):
        target = target.strip()
        if target.lower().startswith("file://") or DRIVE_PATH.match(target):
            report.errors.append("caminho local do sistema não permitido em links OKF")
            break
    if "[[" in text:
        report.warnings.append("wikilink encontrado; prefira link Markdown padrão do OKF")


def narrative_for_ptbr(text: str) -> str:
    """Extrai a escrita humana, ignorando citações, links, código e URLs."""
    text = re.split(r"^# Citations\s*$", text, maxsplit=1, flags=re.MULTILINE)[0]
    text = FENCED_BLOCK.sub("", text)
    text = INLINE_CODE.sub("", text)
    text = MARKDOWN_LINK_LABEL.sub(r"\1", text)
    return re.sub(r"https?://\S+", "", text)


def validate_ptbr(text: str, report: Report) -> None:
    narrative = narrative_for_ptbr(text)
    for ascii_form, accented_form in PT_BR_REQUIRED_ACCENTS.items():
        pattern = rf"(?<![A-Za-zÀ-ÿ]){re.escape(ascii_form)}(?![A-Za-zÀ-ÿ])"
        if re.search(pattern, narrative, re.IGNORECASE):
            report.errors.append(f"pt-BR: use '{accented_form}' em vez de '{ascii_form}'")


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


def validate_concept(path: Path, enforce_ptbr: bool = False) -> Report:
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
        report.errors.append("conceito OKF exige type não vazio")
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
    if enforce_ptbr:
        validate_mermaid_ptbr(body, report)
        human_metadata = "\n".join(str(metadata.get(key, "")) for key in ("title", "description"))
        validate_ptbr(f"{human_metadata}\n{body}", report)
    if "# Citations" not in body:
        report.warnings.append("sem # Citations; inclua fontes para alegações externas")
    return report


def validate_index(path: Path, bundle_root: Path, enforce_ptbr: bool = False) -> Report:
    text, report = read_utf8(path)
    if text is None:
        return report
    metadata, body, frontmatter_error = split_frontmatter(text)
    if frontmatter_error:
        report.errors.append(frontmatter_error)
        return report
    if metadata is not None:
        if path.parent != bundle_root:
            report.errors.append("index.md fora da raiz não pode ter frontmatter")
        elif set(metadata) != {"okf_version"} or str(metadata.get("okf_version")) != "0.1":
            report.errors.append("frontmatter do index raiz deve conter somente okf_version: '0.1'")
    elif path.parent == bundle_root:
        report.warnings.append("index raiz sem okf_version: '0.1'")
    if not re.search(r"^# .+", body, re.MULTILINE):
        report.errors.append("index.md exige pelo menos uma seção H1")
    if not re.search(r"^\s*[*-] \[[^\]]+\]\([^)]+\)\s*-\s+.+", body, re.MULTILINE):
        report.errors.append("index.md exige itens Markdown com descrição")
    validate_links(body, report)
    if enforce_ptbr:
        validate_ptbr(body, report)
    return report


def validate_log(path: Path, enforce_ptbr: bool = False) -> Report:
    text, report = read_utf8(path)
    if text is None:
        return report
    metadata, body, frontmatter_error = split_frontmatter(text)
    if frontmatter_error:
        report.errors.append(frontmatter_error)
        return report
    if metadata is not None:
        report.errors.append("log.md não pode ter frontmatter")
    if not re.search(r"^# .+", body, re.MULTILINE):
        report.errors.append("log.md exige título H1")
    dates = re.findall(r"^## (.+)$", body, re.MULTILINE)
    if not dates:
        report.errors.append("log.md exige ao menos uma data ISO 8601")
    elif any(not ISO_DATE.fullmatch(date) for date in dates):
        report.errors.append("datas de log.md devem usar YYYY-MM-DD")
    elif dates != sorted(dates, reverse=True):
        report.errors.append("datas de log.md devem estar da mais recente para a mais antiga")
    if dates and not re.search(r"^\* \*\*.+?\*\*:", body, re.MULTILINE):
        report.errors.append("log.md exige entradas em lista com rótulo em negrito")
    validate_links(body, report)
    if enforce_ptbr:
        validate_ptbr(body, report)
    return report


def validate_path(path: Path, bundle_root: Path | None, profile: str, enforce_ptbr: bool = False) -> Report:
    if profile == "portable":
        text, report = read_utf8(path)
        if text is not None:
            validate_editorial(text, report)
            if enforce_ptbr:
                validate_ptbr(text, report)
        return report
    if path.name.lower() == "index.md":
        return validate_index(path, bundle_root or path.parent, enforce_ptbr)
    if path.name.lower() == "log.md":
        return validate_log(path, enforce_ptbr)
    return validate_concept(path, enforce_ptbr)


def validate_bundle(bundle_root: Path, enforce_ptbr: bool = False) -> Report:
    report = Report()
    if not bundle_root.is_dir():
        report.errors.append("bundle não encontrado ou não é diretório")
        return report
    markdown_files = sorted(bundle_root.rglob("*.md"))
    if not markdown_files:
        report.errors.append("bundle não contém arquivos Markdown")
        return report
    for path in markdown_files:
        report.extend(validate_path(path, bundle_root, "okf", enforce_ptbr), f"{path.relative_to(bundle_root)}: ")
    root_names = {path.name.lower() for path in markdown_files if path.parent == bundle_root}
    for reserved in RESERVED:
        if reserved not in root_names:
            report.warnings.append(f"arquivo recomendado ausente na raiz: {reserved}")
    return report


def validate_deck_link_targets(path: Path, deck_root: Path, report: Report) -> None:
    """Garante que os links internos produzidos pelo modo deck existem.

    O OKF aceita links quebrados. Esta checagem mais rigorosa só vale para a
    estrutura que a própria skill cria, evitando índices ou cross-links
    desatualizados sem restringir a compatibilidade do validador OKF genérico.
    """
    text, read_report = read_utf8(path)
    report.extend(read_report, f"{path.relative_to(deck_root)}: ")
    if text is None:
        return
    _, body, frontmatter_error = split_frontmatter(text)
    if frontmatter_error:
        return
    for raw_target in MARKDOWN_LINK.findall(body):
        target = raw_target.strip().split("#", 1)[0].strip()
        if not target or "://" in target or target.startswith(("mailto:", "#")):
            continue
        destination = deck_root / target.lstrip("/") if target.startswith("/") else path.parent / target
        if not destination.exists():
            report.errors.append(
                f"{path.relative_to(deck_root)}: link interno gerado não encontrado: {raw_target}"
            )


def validate_deck(deck_root: Path, enforce_ptbr: bool = False) -> Report:
    """Valida o perfil opinativo de deck progressivo da notebooklm-to-notes."""
    report = validate_bundle(deck_root, enforce_ptbr)
    if not deck_root.is_dir():
        return report
    for required in ("index.md", "log.md", "notebooks/index.md"):
        if not (deck_root / required).is_file():
            report.errors.append(f"deck exige {required}")
    notebooks_dir = deck_root / "notebooks"
    if not notebooks_dir.is_dir():
        report.errors.append("deck exige o diretório notebooks/")
        return report
    for notebook_dir in sorted(path for path in notebooks_dir.iterdir() if path.is_dir()):
        slug = notebook_dir.name
        index_path = notebook_dir / "index.md"
        summary_path = notebook_dir / f"{slug}.md"
        if not index_path.is_file():
            report.errors.append(f"notebook {slug}: exige index.md")
        if not summary_path.is_file():
            report.errors.append(f"notebook {slug}: exige o conceito {slug}.md")
        else:
            summary_text, summary_report = read_utf8(summary_path)
            report.extend(summary_report, f"notebooks/{slug}/{slug}.md: ")
            if summary_text is not None:
                metadata, _, frontmatter_error = split_frontmatter(summary_text)
                if frontmatter_error or metadata is None:
                    report.errors.append(f"notebook {slug}: conceito principal exige frontmatter YAML")
                else:
                    if metadata.get("type") != "NotebookLM Summary":
                        report.errors.append(f"notebook {slug}: conceito principal exige type NotebookLM Summary")
                    if not isinstance(metadata.get("notebook_id"), str) or not metadata["notebook_id"].strip():
                        report.errors.append(f"notebook {slug}: conceito principal exige notebook_id")
        sources_dir = notebook_dir / "sources"
        if sources_dir.exists():
            if not sources_dir.is_dir():
                report.errors.append(f"notebook {slug}: sources deve ser diretório")
            elif not (sources_dir / "index.md").is_file():
                report.errors.append(f"notebook {slug}: sources/ exige index.md")
            else:
                source_files = sorted(path for path in sources_dir.glob("*.md") if path.name.lower() not in RESERVED)
                if not source_files:
                    report.warnings.append(f"notebook {slug}: sources/ sem conceitos de fonte")
                for source_path in source_files:
                    source_text, source_report = read_utf8(source_path)
                    report.extend(source_report, f"{source_path.relative_to(deck_root)}: ")
                    if source_text is None:
                        continue
                    metadata, _, frontmatter_error = split_frontmatter(source_text)
                    if frontmatter_error or metadata is None:
                        report.errors.append(f"{source_path.relative_to(deck_root)}: fonte exige frontmatter YAML")
                        continue
                    if metadata.get("type") != "NotebookLM Source":
                        report.errors.append(f"{source_path.relative_to(deck_root)}: fonte exige type NotebookLM Source")
                    for key in ("source_id", "source_status"):
                        if not isinstance(metadata.get(key), str) or not metadata[key].strip():
                            report.errors.append(f"{source_path.relative_to(deck_root)}: fonte exige {key}")
    link_paths = [deck_root / "index.md", deck_root / "notebooks" / "index.md"]
    for notebook_dir in sorted(path for path in notebooks_dir.iterdir() if path.is_dir()):
        link_paths.extend((notebook_dir / "index.md", notebook_dir / f"{notebook_dir.name}.md"))
        sources_index = notebook_dir / "sources" / "index.md"
        if sources_index.is_file():
            link_paths.append(sources_index)
    for link_path in link_paths:
        if link_path.is_file():
            validate_deck_link_targets(link_path, deck_root, report)
    return report


FIDELITY_CATEGORIES = ("concept", "example", "number", "limit", "divergence", "gap")
FIDELITY_STATUSES = {"represented", "gap"}
FENCE_MERMAID = re.compile(r"^\`\`\`mermaid\s*\n(.*?)^\`\`\`", re.MULTILINE | re.DOTALL)


def validate_mermaid_ptbr(text: str, report: Report) -> None:
    """Aplica a revisão pt-BR aos rótulos exibidos por Mermaid."""
    for block in FENCE_MERMAID.findall(text):
        validate_ptbr(block, report)


def read_json_document(path: Path, report: Report, label: str) -> Any | None:
    text, read_report = read_utf8(path)
    report.extend(read_report, f"{label}: ")
    if text is None:
        return None
    try:
        return json.loads(text)
    except json.JSONDecodeError as error:
        report.errors.append(f"{label}: JSON inválido: {error.msg}")
        return None


def concept_metadata(path: Path, report: Report, label: str) -> tuple[dict[str, Any] | None, str]:
    text, read_report = read_utf8(path)
    report.extend(read_report, f"{label}: ")
    if text is None:
        return None, ""
    metadata, body, frontmatter_error = split_frontmatter(text)
    if frontmatter_error:
        report.errors.append(f"{label}: {frontmatter_error}")
        return None, ""
    if metadata is None:
        report.errors.append(f"{label}: conceito exige frontmatter YAML")
        return None, ""
    return metadata, body


def resolve_bundle_target(deck_root: Path, origin: Path, target: str) -> Path | None:
    target = target.split("#", 1)[0].strip()
    if not target or "://" in target or target.startswith(("mailto:", "#")):
        return None
    return deck_root / target.lstrip("/") if target.startswith("/") else origin.parent / target


def validate_fidelity_notebook(deck_root: Path, notebook_dir: Path, report: Report) -> None:
    slug = notebook_dir.name
    summary_path = notebook_dir / f"{slug}.md"
    evidence_dir = notebook_dir / "evidence"
    sources_dir = notebook_dir / "sources"
    label = f"notebook {slug}"

    for relative in ("raw-response.json", "raw-response.md", "source-inventory.json", "coverage.md"):
        if not (evidence_dir / relative).is_file():
            report.errors.append(f"{label}: fidelity exige evidence/{relative}")
    if not sources_dir.is_dir() or not (sources_dir / "index.md").is_file():
        report.errors.append(f"{label}: fidelity exige sources/index.md")
    if not summary_path.is_file() or not evidence_dir.is_dir():
        return

    summary_metadata, summary_body = concept_metadata(summary_path, report, f"{label}: síntese")
    if summary_metadata is not None:
        for section in ("## Conceitos", "## Exemplos", "## Números e limites", "## Divergências e lacunas", "# Citations"):
            if section not in summary_body:
                report.errors.append(f"{label}: síntese exige seção {section}")

    raw_json_path = evidence_dir / "raw-response.json"
    raw_md_path = evidence_dir / "raw-response.md"
    inventory_path = evidence_dir / "source-inventory.json"
    coverage_path = evidence_dir / "coverage.md"
    if not all(path.is_file() for path in (raw_json_path, raw_md_path, inventory_path, coverage_path)):
        return

    raw_payload = read_json_document(raw_json_path, report, f"{label}: raw-response.json")
    inventory = read_json_document(inventory_path, report, f"{label}: source-inventory.json")
    raw_metadata, raw_body = concept_metadata(raw_md_path, report, f"{label}: raw-response.md")
    coverage_metadata, coverage_body = concept_metadata(coverage_path, report, f"{label}: coverage.md")
    if not isinstance(raw_payload, dict) or not isinstance(inventory, dict):
        return
    if not isinstance(raw_payload.get("answer"), str):
        report.errors.append(f"{label}: raw-response.json exige answer textual")
    if not isinstance(raw_payload.get("references"), list):
        report.errors.append(f"{label}: raw-response.json exige references como lista")
    if raw_metadata is not None:
        if raw_metadata.get("type") != "NotebookLM Raw Response":
            report.errors.append(f"{label}: raw-response.md exige type NotebookLM Raw Response")
        expected_hash = raw_metadata.get("raw_response_sha256")
        actual_hash = hashlib.sha256(raw_json_path.read_bytes()).hexdigest()
        if expected_hash != actual_hash:
            report.errors.append(f"{label}: hash de raw-response.json não confere")
        if not isinstance(raw_metadata.get("query_prompt"), str) or not raw_metadata["query_prompt"].strip():
            report.errors.append(f"{label}: raw-response.md exige query_prompt")
        if isinstance(raw_payload.get("answer"), str) and raw_payload["answer"] not in raw_body:
            report.errors.append(f"{label}: raw-response.md não preserva a resposta literal")

    sources = inventory.get("sources")
    if not isinstance(sources, list):
        report.errors.append(f"{label}: source-inventory.json exige sources como lista")
        return
    inventory_ids = {
        source.get("id") for source in sources
        if isinstance(source, dict) and isinstance(source.get("id"), str) and source["id"].strip()
    }
    if len(inventory_ids) != len(sources):
        report.errors.append(f"{label}: source-inventory.json contém fonte sem id")
    source_concepts: dict[str, dict[str, Any]] = {}
    if sources_dir.is_dir():
        for source_path in sources_dir.glob("*.md"):
            if source_path.name.lower() in RESERVED:
                continue
            metadata, _ = concept_metadata(source_path, report, f"{label}: {source_path.relative_to(deck_root)}")
            if metadata is not None and isinstance(metadata.get("source_id"), str):
                source_concepts[metadata["source_id"]] = metadata
    missing_sources = inventory_ids.difference(source_concepts)
    if missing_sources:
        report.errors.append(f"{label}: fontes sem conceito: {', '.join(sorted(missing_sources))}")
    for source in sources:
        if not isinstance(source, dict) or not isinstance(source.get("id"), str):
            continue
        metadata = source_concepts.get(source["id"])
        if metadata is None:
            continue
        status = str(source.get("status", "")).lower()
        expected_type = "NotebookLM Source" if status == "ready" else "NotebookLM Source Gap"
        if metadata.get("type") != expected_type:
            report.errors.append(f"{label}: fonte {source['id']} exige type {expected_type}")
        if metadata.get("source_status") != source.get("status"):
            report.errors.append(f"{label}: fonte {source['id']} possui source_status divergente")

    if summary_metadata is not None:
        ready_count = sum(1 for source in sources if isinstance(source, dict) and str(source.get("status", "")).lower() == "ready")
        error_count = len(sources) - ready_count
        if summary_metadata.get("source_ready_count") != ready_count:
            report.errors.append(f"{label}: source_ready_count não confere com o inventário")
        if summary_metadata.get("source_error_count") != error_count:
            report.errors.append(f"{label}: source_error_count não confere com o inventário")

    if coverage_metadata is None:
        return
    if coverage_metadata.get("type") != "NotebookLM Coverage Ledger":
        report.errors.append(f"{label}: coverage.md exige type NotebookLM Coverage Ledger")
    extraction_status = coverage_metadata.get("extraction_status")
    if extraction_status not in {"complete", "incomplete"}:
        report.errors.append(f"{label}: coverage.md exige extraction_status complete ou incomplete")
    items = coverage_metadata.get("coverage_items")
    empty_categories = coverage_metadata.get("empty_categories", {})
    if not isinstance(items, list):
        report.errors.append(f"{label}: coverage.md exige coverage_items como lista YAML")
        return
    if not isinstance(empty_categories, dict):
        report.errors.append(f"{label}: empty_categories deve ser mapa YAML")
        empty_categories = {}
    categories_present: set[str] = set()
    has_gap = False
    for item in items:
        if not isinstance(item, dict):
            report.errors.append(f"{label}: item de cobertura inválido")
            continue
        item_id = item.get("id")
        category = item.get("category")
        status = item.get("status")
        source_ids = item.get("source_ids")
        destination = item.get("destination")
        if not isinstance(item_id, str) or not item_id.strip():
            report.errors.append(f"{label}: item de cobertura exige id")
            continue
        if category not in FIDELITY_CATEGORIES:
            report.errors.append(f"{label}: item {item_id} tem categoria inválida")
        else:
            categories_present.add(category)
        if status not in FIDELITY_STATUSES:
            report.errors.append(f"{label}: item {item_id} tem status inválido")
        if not isinstance(source_ids, list) or not source_ids or not all(source_id in inventory_ids for source_id in source_ids):
            report.errors.append(f"{label}: item {item_id} exige source_ids existentes")
        if not isinstance(destination, str) or not destination.strip():
            report.errors.append(f"{label}: item {item_id} exige destination")
        else:
            destination_path = resolve_bundle_target(deck_root, coverage_path, destination)
            if destination_path is None or not destination_path.exists():
                report.errors.append(f"{label}: item {item_id} aponta para destination inexistente")
            if summary_body and f"({destination})" not in summary_body:
                report.errors.append(f"{label}: síntese não referencia o item {item_id}")
        if f"## {item_id}" not in coverage_body:
            report.errors.append(f"{label}: coverage.md exige seção ## {item_id}")
        if status == "gap":
            has_gap = True
            if not isinstance(item.get("gap_reason"), str) or not item["gap_reason"].strip():
                report.errors.append(f"{label}: item em lacuna exige gap_reason")
    for category in FIDELITY_CATEGORIES:
        if category not in categories_present:
            reason = empty_categories.get(category)
            if not isinstance(reason, str) or not reason.strip():
                report.errors.append(f"{label}: categoria {category} sem item ou justificativa")
    if extraction_status == "complete" and has_gap:
        report.errors.append(f"{label}: extraction_status complete não aceita lacunas")
    if extraction_status == "incomplete":
        report.errors.append(f"{label}: fidelity bloqueia bundle incomplete")


def validate_fidelity(deck_root: Path, report: Report) -> None:
    notebooks_dir = deck_root / "notebooks"
    if not notebooks_dir.is_dir():
        report.errors.append("fidelity exige notebooks/")
        return
    for notebook_dir in sorted(path for path in notebooks_dir.iterdir() if path.is_dir()):
        validate_fidelity_notebook(deck_root, notebook_dir, report)


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
    parser.add_argument("--deck", type=Path, help="valida a estrutura progressiva de um deck notebooklm-to-notes")
    parser.add_argument("--fidelity", action="store_true", help="exige evidências completas em um deck")
    parser.add_argument("--profile", choices=("okf", "portable"), default="okf")
    parser.add_argument("--pt-br", action="store_true", help="bloqueia palavras pt-BR sem acentos na escrita humana")
    parser.add_argument("--vault-root", type=Path, help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args.fidelity and not args.deck:
        parser.error("--fidelity exige --deck <diretório>")
    selected = sum(value is not None for value in (args.arquivo, args.bundle, args.deck))
    if selected != 1:
        parser.error("informe um arquivo, --bundle <diretório> ou --deck <diretório>")
    if args.bundle:
        print(f"Validando bundle: {args.bundle} (OKF 0.1)")
        report = validate_bundle(args.bundle, args.pt_br)
    elif args.deck:
        print(f"Validando deck: {args.deck} (notebooklm-to-notes)")
        report = validate_deck(args.deck, args.pt_br)
        if args.fidelity:
            validate_fidelity(args.deck, report)
    else:
        print(f"Validando: {args.arquivo} (perfil {args.profile})")
        report = validate_path(args.arquivo, args.vault_root, args.profile, args.pt_br)
    print_report(report)
    return 1 if report.errors else 0


if __name__ == "__main__":
    raise SystemExit(main())