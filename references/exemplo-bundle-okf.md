# Exemplo de bundle OKF visual

```text
pesquisa-claude-notebooklm/
  index.md
  log.md
  sintese.md
  sources/
    index.md
    video-principal.md
```

## `index.md`

```markdown
---
okf_version: "0.1"
---

# Conteudos

* [Sintese](/sintese.md) - Visao geral visual do notebook.
* [Fontes](/sources/) - Conceitos de proveniencia e texto extraido.
```

## `sintese.md`

```markdown
---
type: NotebookLM Summary
title: Pesquisa com Claude Code e NotebookLM
description: Sintese visual de um fluxo de pesquisa baseado em fontes.
tags: [notebooklm, pesquisa]
timestamp: 2026-07-16T12:00:00-03:00
notebook_id: id-conhecido
---

# Pesquisa com Claude Code e NotebookLM

> [!abstract] TL;DR
> O agente orquestra; o NotebookLM analisa as fontes; o bundle preserva o conhecimento.

Leia a [fonte principal](/sources/video-principal.md).

# Citations

[1] [Fonte principal](/sources/video-principal.md)
```

## `log.md`

```markdown
# Directory Update Log

## 2026-07-16

* **Creation**: Criado bundle a partir de um notebook do NotebookLM.
```