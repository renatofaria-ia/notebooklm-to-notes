# notebooklm-to-notes

Skill para transformar conhecimento de notebooks do NotebookLM em notas Markdown visuais, fieis e faceis de consultar.

## Perfis de saida

- `portable` (padrao): Markdown visual generico e portatil. Mantem a compatibilidade atual.
- `obsidian`: Markdown visual para Obsidian. Callouts e Mermaid sao permitidos. Use wikilinks somente quando o usuario pedir e o vault os utilizar.
- `okf`: Markdown visual compativel com o nucleo OKF 0.1. Mermaid e callouts seguem permitidos como extensoes visuais documentadas; o contrato persistido exige YAML valido, `type`, H1, proveniencia explicita e links Markdown relativos.

O perfil `okf` e uma escolha explicita. Ele nao altera o comportamento padrao dos perfis `portable` e `obsidian`.

## Como usar

```text
Use $notebooklm-to-notes para transformar o notebook "Curso X" em uma nota portable em C:\Notas\curso-x.md.
Use $notebooklm-to-notes com perfil okf para entregar uma nota no caminho informado pelo bundle.
```

## Validacao

```powershell
python .\scripts\validar_nota.py C:\caminho\para\nota.md
python .\scripts\validar_nota.py --profile okf C:\caminho\para\nota.md
python .\scripts\validar_nota.py --profile okf --vault-root C:\caminho\do\bundle C:\caminho\do\bundle\nota.md
python -m unittest discover -s tests
```

## Estrutura

- `SKILL.md`: fluxo principal e perfis de saida.
- `references/formato-visual.md`: formato visual comum.
- `references/formato-okf.md`: contrato persistido OKF 0.1.
- `references/exemplo-gold.md`: exemplo visual existente.
- `references/exemplo-okf.md`: exemplo visual compativel com OKF.
- `scripts/validar_nota.py`: validador sem dependencias externas.

## Licenca

Este projeto e licenciado sob a [MIT License](LICENSE).