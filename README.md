# notebooklm-to-notes

Skill para transformar notebooks do NotebookLM em **bundles Open Knowledge Format (OKF) 0.1** visuais, rastreaveis e prontos para leitura humana ou por agentes.

Cada entrega cria uma síntese e um conceito por fonte, com citações, `index.md`, `log.md`, Mermaid, callouts, tabelas e Markdown em UTF-8 sem BOM. O bundle local e a fonte de verdade; Obsidian e Notion são destinos de leitura ou espelho.

## Contrato de saida

```text
<bundle>/
  index.md                 # navegacao progressiva + okf_version: "0.1"
  log.md                   # historico datado
  sintese.md               # NotebookLM Summary visual
  sources/
    index.md
    <fonte>.md             # NotebookLM Source por fonte
```

Conceitos usam frontmatter YAML com `type` obrigatorio e os campos recomendados `title`, `description`, `resource` quando conhecido, `tags` e `timestamp`. citações ficam em `# Citations`. Links internos usam Markdown padrão e preferem caminhos absolutos relativos a raiz, como `/sources/video.md`.

## Uso

```text
Use $notebooklm-to-notes para transformar o notebook "Curso X" em um bundle OKF em C:\Notas.
Use $notebooklm-to-notes para extrair o notebook "Curso X" para C:\Notas\curso-x.md.
```

No segundo caso, a skill cria `C:\Notas\curso-x\` como bundle irmao; não produz arquivo solto fora do OKF.

## validação

```powershell
python -m pip install -r requirements.txt
python .\scripts\validar_nota.py .\caminho\para\conceito.md
python .\scripts\validar_nota.py --bundle .\caminho\para\bundle --pt-br
```

O modo padrão valida OKF. Em entregas da skill, `--pt-br` é obrigatório: ele bloqueia formas pt-BR comuns sem acentuação no texto humano, sem inspecionar URLs, tags, caminhos ou blocos de código. `--profile portable` existe somente para artefatos legados.

## Destinos

- **Obsidian:** abre diretamente o bundle; Mermaid e callouts renderizam onde houver suporte.
- **Markdown:** o bundle e a entrega canonica e portatil.
- **Notion:** o bundle local e criado primeiro; com conector, a skill publica um espelho em blocos nativos.

## referências

- [Especificacao OKF 0.1](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md)
- `references/formato-okf.md`
- `references/formato-visual.md`
- `references/exemplo-bundle-okf.md`

## Licenca

[MIT](LICENSE).