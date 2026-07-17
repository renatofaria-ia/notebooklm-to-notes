# notebooklm-to-notes

Skill para converter notebooks do NotebookLM em um deck de conhecimento progressivo, visual e rastreável, usando **Open Knowledge Format (OKF) 0.1**. A versão **v1.2.0** adota geração **evidence-first**.

## O que a versão 1.2 entrega

- Preserva a resposta bruta do NotebookLM em JSON e Markdown, com hash SHA-256.
- Inventaria todas as fontes e cria automaticamente um conceito para cada fonte pronta.
- Registra fontes indisponíveis como lacunas explícitas, sem preenchimento inventado.
- Mantém um ledger de cobertura com conceitos, exemplos, números, limites, divergências e lacunas.
- Liga cada afirmação da síntese ao item de evidência correspondente.
- Produz síntese visual em PT-BR: TL;DR, callouts, tabelas, Mermaid, mapa mental e cola rápida quando úteis.
- Mantém bundles históricos compatíveis, sem migração automática.

## Estrutura de uma nova extração

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
        <fonte>.md
```

A entrega é completa somente se o deck passar:

```powershell
python .\scripts\validar_nota.py --deck .\caminho\para\deck --fidelity --pt-br
```

Em falha, a resposta bruta e as lacunas permanecem no deck, que é marcado como ```incomplete```.

## Validação

```powershell
python -m pip install -r requirements.txt
python .\scripts\validar_nota.py .\caminho\para\conceito.md
python .\scripts\validar_nota.py --bundle .\caminho\para\bundle --pt-br
python .\scripts\validar_nota.py --deck .\caminho\para\deck --pt-br
python .\scripts\validar_nota.py --deck .\caminho\para\deck --fidelity --pt-br
```

```--bundle``` e @@--deck``` preservam o comportamento permissivo para acervos existentes. Consulte [o contrato de fidelidade](references/contrato-fidelidade.md) para o esquema, o prompt e os critérios de conclusão.

## Referências

- [Especificação OKF 0.1](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md)
- [Contrato de fidelidade](references/contrato-fidelidade.md)
- [Deck progressivo](references/deck-progressivo.md)
- [Formato visual](references/formato-visual.md)

## Licença

[MIT](LICENSE).
