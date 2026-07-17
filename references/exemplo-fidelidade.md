# Exemplo de cobertura verificável

A síntese de um notebook aponta cada alegação para o ledger:

```markdown
## Números e limites

- O limite informado é de 50 itens por lote. [Evidência N1](/notebooks/curso/evidence/coverage.md#N1)
- A fonte registra uma exceção para contas de teste. [Evidência L1](/notebooks/curso/evidence/coverage.md#L1)
```

O ledger preserva a classificação e o suporte:

```yaml
- id: N1
  category: number
  extracted_text: "O máximo por lote é 50."
  source_ids: [fonte-01]
  destination: /notebooks/curso/evidence/coverage.md#N1
  status: represented
- id: L1
  category: limit
  extracted_text: "Contas de teste não seguem esse máximo."
  source_ids: [fonte-01]
  destination: /notebooks/curso/evidence/coverage.md#L1
  status: represented
```

Se o NotebookLM informar uma fonte indisponível, crie ```NotebookLM Source Gap``` e marque o notebook como ```incomplete```. Não resuma por inferência.
