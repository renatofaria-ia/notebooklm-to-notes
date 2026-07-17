# Deck progressivo

O deck é a representação didática do segundo cérebro. A raiz oferece descoberta progressiva; cada notebook é um conceito principal; suas fontes e evidências permanecem próximas ao conteúdo.

## Organização

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
      sources/
```

Use ```index.md``` para navegação e ```log.md``` para histórico cronológico ISO. Não mova nem migre bundles históricos sem pedido explícito.

## Cross-linking didático

A síntese pode conter até três links em ```Conhecimento relacionado```. Cada link deve explicar a relação e ter suporte explícito no NotebookLM ou compartilhar duas tags normalizadas. Não crie arquivo de arestas, banco de grafo ou hub de tags.

## Regra de fidelidade

Novas extrações incluem evidência bruta, inventário, ledger de cobertura e conceitos de todas as fontes prontas. Consulte [o contrato de fidelidade](contrato-fidelidade.md). Use a validação abaixo antes de declarar a extração completa:

```powershell
python scripts/validar_nota.py --deck <diretório> --fidelity --pt-br
```
