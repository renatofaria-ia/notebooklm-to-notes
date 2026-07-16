# notebooklm-to-notes

Skill para transformar o conteúdo de notebooks do NotebookLM em notas visuais, fiéis e fáceis de consultar.

O resultado combina uma estrutura editorial clara com frontmatter mínimo, TL;DR, diagramas Mermaid, callouts, tabelas, emojis, mindmap e uma cola rápida. O destino é escolha do usuário: uma pasta do Obsidian, um arquivo Markdown ou uma página do Notion quando houver conector disponível.

## O que ela faz

1. Localiza o notebook e lê integralmente suas fontes pelo NotebookLM CLI.
2. Inventaria conceitos, exemplos, números e metáforas para preservar a fidelidade.
3. Reescreve o material em PT-BR no formato visual canônico.
4. Adapta a entrega ao destino e valida arquivos Markdown antes da entrega.

## Instalação

Instale a skill no Codex a partir deste repositório:

```powershell
python C:\Users\konok\.codex\skills\.system\skill-installer\scripts\install-skill-from-github.py --url https://github.com/renatofaria-ia/notebooklm-to-notes --path . --name notebooklm-to-notes
```

Reinicie o Codex após a instalação para que a skill seja descoberta em uma nova sessão.

## Como usar

Use pedidos naturais, por exemplo:

```text
Use $notebooklm-to-notes para transformar o notebook "Aprendizados de vendas" em uma nota na pasta C:\Obsidian\Conhecimento.
```

Ou:

```text
Pegue o conteúdo do notebook "Curso X" no NotebookLM e entregue como Markdown em C:\Notas\curso-x.md.
```

Se o destino não for informado, a skill pergunta se a entrega deve ir para Obsidian, arquivo Markdown ou Notion.

## Estrutura

```text
.
├── SKILL.md                       # fluxo principal da skill
├── agents/openai.yaml             # metadados da interface do Codex
├── references/
│   ├── formato-visual.md          # especificação do formato
│   └── exemplo-gold.md            # referência completa de qualidade
├── scripts/
│   └── validar_nota.py            # validador estrutural de Markdown
└── tests/
    └── nota-valida.md             # fixture para o validador
```

## Validação

Para validar uma nota Markdown produzida pela skill:

```powershell
python .\scripts\validar_nota.py C:\caminho\para\nota.md
```

O validador verifica H1, fences, caracteres não latinos acidentais, Mermaid, callouts e frontmatter. Avisos não impedem a entrega; erros estruturais retornam código 1.

## Limites e integrações

- É necessária uma sessão autenticada na CLI do NotebookLM para extrair conteúdo.
- O Notion só recebe blocos nativos quando houver um conector Notion/MCP disponível na sessão. Sem conector, a skill entrega Markdown portátil para colagem manual.
- Mermaid é preservado como bloco de código para que o destino o renderize quando suportado.

## Licença

Este repositório ainda não declara uma licença. Antes de reutilizá-lo ou distribuí-lo fora do seu contexto, defina uma licença apropriada.
