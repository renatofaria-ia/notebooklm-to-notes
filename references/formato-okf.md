# OKF 0.1 para notebooklm-to-notes

está skill implementa o [Open Knowledge Format 0.1](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md) como contrato de persistencia.

## Regras de conformidade

- Um bundle e uma arvore de arquivos Markdown UTF-8 sem BOM.
- Todo conceito, isto e, todo `.md` exceto `index.md` e `log.md`, possui frontmatter YAML parseavel e `type` não vazio.
- `type` não e catalogado centralmente. Use `NotebookLM Summary` e `NotebookLM Source` nesta skill.
- Preserve chaves desconhecidas; extensoes de proveniência são permitidas.
- Links internos usam Markdown. Prefira `/caminho/conceito.md`, relativo a raiz do bundle; links relativos também são aceitos.
- Links quebrados são permitidos. Nunca invente um destino para corrigi-los.
- `index.md` e `log.md` são reservados e não podem representar conceitos.

## Estrutura produzida

```text
<bundle>/
  index.md
  log.md
  sintese.md
  sources/
    index.md
    fonte-a.md
```

O `index.md` raiz usa somente:

```yaml
---
okf_version: "0.1"
---
```

O corpo de cada indice lista itens Markdown com descrição. O `log.md` não tem frontmatter, usa H1 e agrupa entradas por `## AAAA-MM-DD`, da mais recente para a mais antiga.

## Frontmatter de conceitos

```yaml
---
type: NotebookLM Summary
title: <titulo>
description: <uma frase>
resource: <URI canonica quando houver>
tags: [notebooklm, pesquisa]
timestamp: 2026-07-16T12:00:00-03:00
notebook_id: <id conhecido>
---
```

Use `source_id` e `source_status` nos conceitos de fonte. não invente `resource`, identificadores ou datas ausentes.

Coloque entre aspas valores YAML que tenham :, #, {}, [] ou outros caracteres estruturais. O frontmatter deve passar por yaml.safe_load, não apenas por verificacao textual.

## citações e visual

Conceitos baseados em fontes externas terminam com `# Citations`. A síntese cita conceitos em `/sources/`; cada fonte cita sua URL externa quando conhecida.

Mermaid, callouts, emojis e tabelas são extensoes visuais permitidas. Eles não substituem texto, titulos e listas estruturadas.