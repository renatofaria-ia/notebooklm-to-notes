---
name: notebooklm-to-notes
description: Extraia conhecimento de notebooks do NotebookLM e entregue bundles Open Knowledge Format (OKF) 0.1 visuais, com síntese, conceitos por fonte, citações, indice, log, Mermaid e callouts. Use quando o usuário quiser transformar, exportar ou persistir um notebook do NotebookLM no Obsidian, em Markdown ou no Notion.
---

# notebooklm-to-notes

Gere sempre um **bundle OKF 0.1** como fonte de verdade. Preserve a experiência editorial: PT-BR claro, TL;DR, contexto, diagramas Mermaid, callouts, tabelas, emojis, mapa mental e cola rápida.

## referências obrigatorias

Antes de escrever, leia:

- `references/formato-okf.md` para contrato, estrutura e citações OKF.
- `references/formato-visual.md` para a camada editorial e Mermaid.
- `references/exemplo-bundle-okf.md` para o bundle completo esperado.

## 1. Extrair com fidelidade

1. Confirme a sessão com `notebooklm auth check --test --json`.
2. Liste notebooks e fontes; use o ID completo do notebook.
3. Leia `source fulltext` de cada fonte pronta. Registre fontes com erro sem inventar conteúdo.
4. Inventarie conceitos, exemplos, números, limites e divergências antes de redigir.

## 2. Definir o bundle

- Se o usuário indicar uma pasta, crie nela um diretório com slug do notebook.
- Se indicar um arquivo `.md`, crie uma pasta irmã com o mesmo nome sem extensão; não entregue Markdown solto fora do bundle.
- não imponha pasta de vault, tags proprietarias, hubs ou wikilinks.

Crie esta estrutura minima:

```text
<bundle>/
  index.md
  log.md
  sintese.md
  sources/
    index.md
    <fonte>.md
```

## 3. Escrever conceitos OKF

Todo `.md` que não seja `index.md` ou `log.md` precisa de YAML UTF-8 sem BOM com:



Use as chaves reais abaixo, em minúsculas:

```yaml
---
type: NotebookLM Summary
title: <titulo humano>
description: <resumo em uma frase>
tags: [notebooklm, <tema>]
timestamp: <ISO 8601>
notebook_id: <id conhecido>
source_status: ready
---
```

- Em `sintese.md`, use `type: NotebookLM Summary`, links `/sources/<arquivo>.md` e `# Citations` apontando para os conceitos de fonte.
- Escreva todo texto humano em pt-BR natural, com acentuação correta. UTF-8 sem BOM não substitui a revisão linguística: use `síntese`, `automação`, `memória`, `não` e demais formas acentuadas. Identificadores, tags, URLs, caminhos e blocos de código podem permanecer em ASCII.
- Coloque entre aspas valores YAML que contenham :, #, {}, [] ou outros caracteres estruturais; valide sempre o bundle com PyYAML antes da entrega.
- Em cada fonte, use `type: NotebookLM Source`, `source_id`, `source_status` e `resource` somente quando a URL for conhecida. Termine com `# Citations`; não invente URL, ID ou data.
- Use links Markdown padrão. Prefira links absolutos relativos a raiz do bundle, como `/sources/video.md`; links relativos também são válidos. Nunca use `file://`, caminhos de disco ou wikilinks na geração.
- `index.md` raiz deve ter somente `okf_version: "0.1"` no frontmatter e listar itens com descrição. `sources/index.md` não tem frontmatter. `log.md` não tem frontmatter e registra a criação em data ISO, mais recente primeiro.

## 4. Camada visual

A síntese mantém esta sequência quando aplicavel: H1, TL;DR, proveniência, mecanismo, desenvolvimento, aplicação, mapa, cola rápida e citações.

Mermaid e callouts são extensoes visuais: o conteúdo essencial deve permanecer claro em Markdown puro. Nunca use entidades HTML dentro de Mermaid. Em `mindmap`, use rótulos simples sem aspas.

## 5. Entregar

1. Instale dependências: `python -m pip install -r requirements.txt`.
2. Valide o bundle: `python scripts/validar_nota.py --bundle <bundle> --pt-br`. Esta validação é obrigatória e bloqueia formas pt-BR comuns sem acentuação na escrita humana.
3. Corrija todos os erros antes da entrega; avisos OKF são orientações de qualidade e não bloqueiam o bundle.
4. Para Notion, crie primeiro o bundle local. Se houver conector, publique um espelho em blocos nativos e informe o caminho da fonte de verdade. Sem conector, entregue o bundle local.
5. Reporte caminho, fontes prontas e com erro, conceitos criados, validação e extensoes visuais usadas.

## Compatibilidade

`python scripts/validar_nota.py --profile portable <arquivo>` continua disponível apenas para validar artefatos antigos. não o use para novas entregas.