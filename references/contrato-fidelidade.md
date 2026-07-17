# Contrato de fidelidade evidence-first

Este contrato se aplica a toda nova geração da skill. Ele é uma extensão de proveniência do OKF 0.1: usa conceitos Markdown e frontmatter YAML, sem alterar a estrutura aberta do padrão.

## Artefatos obrigatórios

Para cada ```<notebook-slug>```, crie:

```text
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

```raw-response.json``` é imutável e contém o payload completo de ```notebooklm ask --json```. ```raw-response.md``` é um conceito ```NotebookLM Raw Response``` com ```query_prompt```, ```raw_response_sha256``` e a resposta literal. ```source-inventory.json``` conserva o inventário original, inclusive IDs, título, URL quando conhecida e status.

```coverage.md``` é um conceito ```NotebookLM Coverage Ledger```. Seu frontmatter contém ```extraction_status```, ```coverage_items``` e ```empty_categories```.

Cada item em ```coverage_items``` possui:

```yaml
- id: C1
  category: concept
  extracted_text: "Texto preservado da extração."
  source_ids: [source-id]
  destination: /notebooks/<slug>/evidence/coverage.md#C1
  status: represented
```

As categorias são ```concept```, ```example```, ```number```, ```limit```, ```divergence``` e ```gap```. Uma categoria vazia exige justificativa em ```empty_categories```. Item ```gap``` exige ```gap_reason```.

## Solicitação estruturada ao NotebookLM

Use este pedido, substituindo o contexto necessário:

```text
Com base somente nas fontes deste notebook, responda com JSON válido.
Extraia itens atômicos, sem omitir detalhes relevantes, nas categorias:
concept, example, number, limit, divergence e gap.
Para cada item, forneça id único, category, extracted_text literal ou fiel,
source_ids conhecidos e uma explicação curta se category for gap.
Inclua também um resumo em texto e informe explicitamente categorias sem itens.
Não use Markdown fora do JSON. Não invente fonte, URL, número, limite ou consenso.
```

Se o JSON não puder ser analisado, faça uma única solicitação corretiva. Preserve ambos os retornos brutos. Após a segunda falha, o bundle é ```incomplete```.

## Síntese e fontes

A síntese ```NotebookLM Summary``` deve ter ```notebook_id```, ```source_ready_count``` e ```source_error_count```. Organize as alegações em:

1. Conceitos
2. Exemplos
3. Números e limites
4. Divergências e lacunas
5. Citations

Cada alegação tem link para o item no ledger. Cada fonte pronta é ```NotebookLM Source``` com ```source_id``` e ```source_status```. Fontes indisponíveis usam ```NotebookLM Source Gap```, mantendo ID, status e impacto.

## Conclusão e falha

```extraction_status: complete``` exige que todos os itens tenham destino existente, fonte correspondente, âncora no ledger e referência na síntese. Um erro de fonte, divergência não resolvida, item sem destino ou falha do pacote estruturado marca ```incomplete```. O material bruto é preservado, mas a skill não declara entrega integral.
