---
name: notebooklm-to-notes
description: Extraia conhecimento de notebooks do NotebookLM e entregue bundles Open Knowledge Format (OKF) 0.1 visuais, com sintese, conceitos por fonte, citacoes, indice, log, Mermaid e callouts. Use quando o usuario quiser transformar, exportar ou persistir um notebook do NotebookLM no Obsidian, em Markdown ou no Notion.
---

# notebooklm-to-notes

Gere sempre um **bundle OKF 0.1** como fonte de verdade. Preserve a experiencia editorial: PT-BR claro, TL;DR, contexto, diagramas Mermaid, callouts, tabelas, emojis, mapa mental e cola rapida.

## Referencias obrigatorias

Antes de escrever, leia:

- `references/formato-okf.md` para contrato, estrutura e citacoes OKF.
- `references/formato-visual.md` para a camada editorial e Mermaid.
- `references/exemplo-bundle-okf.md` para o bundle completo esperado.

## 1. Extrair com fidelidade

1. Confirme a sessao com `notebooklm auth check --test --json`.
2. Liste notebooks e fontes; use o ID completo do notebook.
3. Leia `source fulltext` de cada fonte pronta. Registre fontes com erro sem inventar conteudo.
4. Inventarie conceitos, exemplos, numeros, limites e divergencias antes de redigir.

## 2. Definir o bundle

- Se o usuario indicar uma pasta, crie nela um diretorio com slug do notebook.
- Se indicar um arquivo `.md`, crie uma pasta irma com o mesmo nome sem extensao; nao entregue Markdown solto fora do bundle.
- Nao imponha pasta de vault, tags proprietarias, hubs ou wikilinks.

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

Todo `.md` que nao seja `index.md` ou `log.md` precisa de YAML UTF-8 sem BOM com:



Use as chaves reais abaixo, em minusculas:

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
- Em cada fonte, use `type: NotebookLM Source`, `source_id`, `source_status` e `resource` somente quando a URL for conhecida. Termine com `# Citations`; nao invente URL, ID ou data.
- Use links Markdown padrao. Prefira links absolutos relativos a raiz do bundle, como `/sources/video.md`; links relativos tambem sao validos. Nunca use `file://`, caminhos de disco ou wikilinks na geracao.
- `index.md` raiz deve ter somente `okf_version: "0.1"` no frontmatter e listar itens com descricao. `sources/index.md` nao tem frontmatter. `log.md` nao tem frontmatter e registra a criacao em data ISO, mais recente primeiro.

## 4. Camada visual

A sintese mantem esta sequencia quando aplicavel: H1, TL;DR, proveniencia, mecanismo, desenvolvimento, aplicacao, mapa, cola rapida e citacoes.

Mermaid e callouts sao extensoes visuais: o conteudo essencial deve permanecer claro em Markdown puro. Nunca use entidades HTML dentro de Mermaid. Em `mindmap`, use rotulos simples sem aspas.

## 5. Entregar

1. Instale dependencias: `python -m pip install -r requirements.txt`.
2. Valide o bundle: `python scripts/validar_nota.py --bundle <bundle>`.
3. Corrija todos os erros antes da entrega; avisos OKF sao orientacoes de qualidade e nao bloqueiam o bundle.
4. Para Notion, crie primeiro o bundle local. Se houver conector, publique um espelho em blocos nativos e informe o caminho da fonte de verdade. Sem conector, entregue o bundle local.
5. Reporte caminho, fontes prontas e com erro, conceitos criados, validacao e extensoes visuais usadas.

## Compatibilidade

`python scripts/validar_nota.py --profile portable <arquivo>` continua disponivel apenas para validar artefatos antigos. Nao o use para novas entregas.