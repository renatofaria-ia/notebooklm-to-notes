# Perfil OKF 0.1

Use este perfil somente quando o chamador selecionar `okf`. Ele preserva a nota visual, sem impor vault, pasta, tag, hub ou indice.

## Nucleo obrigatorio

- O arquivo e Markdown UTF-8 sem BOM.
- O frontmatter YAML abre o arquivo, fecha corretamente e possui `type` nao vazio.
- O arquivo possui H1.
- A proveniencia explicita notebook, fonte ou fontes conhecidas e data de geracao. Nunca invente identificadores ou datas ausentes.
- Links para outras notas usam Markdown relativo, por exemplo `[Titulo](../caminho/nota.md)`.
- Nao use `[[wikilinks]]`.
- Nunca crie ou sobrescreva `index.md` ou `log.md` na raiz do bundle.
- Campos extras no frontmatter sao permitidos e nao removem `type`.

```yaml
---
type: research-note
date: 2026-07-16
source: NotebookLM - <titulo ou identificador conhecido>
---

# <Titulo>
```

Nomes e campos extras podem ser ajustados pelo consumidor.

## Extensoes visuais permitidas

Mermaid, callouts `> [!tipo]`, tabelas, emojis, blockquotes e fences Markdown sao permitidos. Eles nao alteram o nucleo OKF. O conteudo essencial deve continuar compreensivel sem Mermaid, callouts ou wikilinks.

## Estrutura visual

Mantenha TL;DR, contexto/fonte, desenvolvimento, aplicacao, mapa e cola rapida. Adapte as secoes ao conteudo; nao adicione diagramas decorativos nem fatos fora das fontes.