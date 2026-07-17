---
name: notebooklm-to-notes
description: Extraia notebooks do NotebookLM em decks Open Knowledge Format (OKF) 0.1 evidence-first, preservando material bruto, fontes, cobertura verificável e uma síntese visual em PT-BR. Use para transformar notebooks em conhecimento rastreável no Obsidian, Markdown ou Notion.
---

# notebooklm-to-notes

Gere um deck OKF 0.1 em PT-BR, visual e rastreável. O bundle local é a fonte de verdade; o espelho no Notion é opcional. Toda nova extração usa o contrato **evidence-first** e só é declarada completa após passar em validação de fidelidade.

## Referências obrigatórias

Leia antes de gerar: ```references/formato-okf.md```, ```references/formato-visual.md```, ```references/deck-progressivo.md``` e ```references/contrato-fidelidade.md```.

## Fluxo obrigatório

1. Confirme a sessão com ```notebooklm auth check --test --json``` e liste o notebook e as fontes, mantendo IDs, títulos, URLs conhecidas e status originais.
2. Crie o inventário original em ```evidence/source-inventory.json```.
3. Solicite o pacote estruturado definido em ```contrato-fidelidade.md``` por ```notebooklm ask --json```. Preserve cada retorno em ```evidence/raw-response.json```, mesmo quando inválido.
4. Se o pacote estruturado for inválido, faça **uma única** nova solicitação corretiva. Nunca descarte a primeira resposta bruta.
5. Gere ```evidence/raw-response.md``` com prompt, resposta literal e SHA-256 do JSON; gere ```evidence/coverage.md``` com cada item atômico.
6. Para **cada fonte pronta**, gere automaticamente um conceito em ```sources/```. Fonte não pronta recebe ```type: NotebookLM Source Gap```, com status e impacto; não invente conteúdo.
7. Gere a síntese visual. Cada alegação derivada deve apontar para seu item em ```coverage.md```. As instruções da própria skill ficam em seção editorial marcada e não contam como alegações extraídas.
8. Execute ```python scripts/validar_nota.py --deck <diretório> --fidelity --pt-br```. Se falhar, mantenha os artefatos e marque o notebook como ```incomplete```; não declare entrega integral.

## Estrutura padrão

```text
<deck>/
  index.md
  log.md
  notebooks/
    index.md
    <notebook-slug>/
      index.md
      <notebook-slug>.md
      evidence/
        index.md
        raw-response.json
        raw-response.md
        source-inventory.json
        coverage.md
      sources/
        index.md
        <fonte-slug>.md
```

A síntese deve conter obrigatoriamente: ```TL;DR```, ```Conceitos```, ```Exemplos```, ```Números e limites```, ```Divergências e lacunas``` e ```Citations```.

## Regras de apresentação e proveniência

- Escreva em UTF-8 sem BOM, PT-BR natural e acentuado.
- Em Mermaid, preserve acentos nos rótulos; nunca use entidades HTML como ```&quot;```. Em mindmap, use rótulos simples sem aspas.
- Use links Markdown absolutos relativos à raiz do deck, como ```/notebooks/<slug>/evidence/coverage.md#C1```. Nunca use ```file://```, caminho local do sistema ou wikilink.
- Toda síntese e fonte termina em ```# Citations```.
- Mantenha no máximo três cross-links didáticos na seção ```Conhecimento relacionado```. O vínculo precisa ter suporte explícito ou duas tags normalizadas em comum.

## Compatibilidade

```--bundle``` e ```--deck``` permanecem permissivos para bundles históricos. ```--fidelity``` é obrigatório para novas gerações desta skill. ```--profile portable``` continua exclusivo para validações legadas.
