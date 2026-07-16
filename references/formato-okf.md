# OKF 0.1 para notebooklm-to-notes

Esta skill implementa o [Open Knowledge Format 0.1](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md) como contrato de persistencia.

## Regras de conformidade

- Um bundle e uma arvore de arquivos Markdown UTF-8 sem BOM.
- Todo conceito, isto e, todo `.md` exceto `index.md` e `log.md`, possui frontmatter YAML parseavel e `type` nao vazio.
- `type` nao e catalogado centralmente. Use `NotebookLM Summary` e `NotebookLM Source` nesta skill.
- Preserve chaves desconhecidas; extensoes de proveniencia sao permitidas.
- Links internos usam Markdown. Prefira `/caminho/conceito.md`, relativo a raiz do bundle; links relativos tambem sao aceitos.
- Links quebrados sao permitidos. Nunca invente um destino para corrigi-los.
- `index.md` e `log.md` sao reservados e nao podem representar conceitos.

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

O corpo de cada indice lista itens Markdown com descricao. O `log.md` nao tem frontmatter, usa H1 e agrupa entradas por `## AAAA-MM-DD`, da mais recente para a mais antiga.

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

Use `source_id` e `source_status` nos conceitos de fonte. Nao invente `resource`, identificadores ou datas ausentes.

## Citacoes e visual

Conceitos baseados em fontes externas terminam com `# Citations`. A sintese cita conceitos em `/sources/`; cada fonte cita sua URL externa quando conhecida.

Mermaid, callouts, emojis e tabelas sao extensoes visuais permitidas. Eles nao substituem texto, titulos e listas estruturadas.