# Formato visual sobre o nucleo OKF

O OKF define a estrutura persistida; esta referencia define a camada editorial da `sintese.md` sem alterar a conformidade.

## Ordem recomendada

1. `# Titulo` claro, com emoji se ajudar.
2. Callout `abstract` para TL;DR.
3. Callout `info` para proveniencia e limites da extracao.
4. Mecanismo ou ideia central, com tabela ou fluxo quando util.
5. Desenvolvimento e exemplos fieis as fontes.
6. `## Como aplicar` com acoes praticas.
7. `## Mapa` com mindmap Mermaid quando fizer sentido.
8. `## Cola rapida` em tabela.
9. `# Citations` com links para conceitos de fonte e referencias externas.

## Portabilidade

- O conteudo essencial deve sobreviver sem Mermaid e sem callouts.
- Use links Markdown padrao; a geracao nao usa wikilinks.
- Callouts degradam para blockquotes em leitores genericos.
- No Notion, use blocos nativos apenas como espelho do bundle local.

## Mermaid seguro

- Nunca use `&quot;`, `&amp;`, `&lt;`, `&gt;` ou entidades HTML.
- Use `<br/>`, nao `\n`, dentro de nos.
- Em `mindmap`, nao use aspas nos rotulos e evite caracteres estruturais.
- Prefira diagramas pequenos que expliquem uma relacao real.

## Voz

Escreva em PT-BR, com paragrafos curtos, termos-chave em negrito e sem floreio. Fidelidade vem antes de compressao: preserve conceitos, limites, exemplos e discordancias das fontes.