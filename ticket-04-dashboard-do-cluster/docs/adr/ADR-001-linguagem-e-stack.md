# ADR-001 — Linguagem e stack

| Campo | Valor |
|---|---|
| Status | aceito |
| Data | 2026-09-17 (registrado como ADR próprio em 2026-10-27; origem: `spec/spec-decisoes.md`, Decisão 1) |
| Decisão em aberto do enunciado | "Linguagem e stack, considerando que quem vai manter é um time de infraestrutura" |

## Decisão

**Escolhido**: Python 3.10+ com [Textual](https://textual.textualize.io/) (TUI — interface de terminal).


**Por quê**: quem mantém isso é um time de infraestrutura que, ao longo deste mesmo desafio, já demonstrou fluência em Python (a skill `metacortex-manifest`, o `check-manifest.py`, a ferramenta `inventario.py` do Ticket 03 são todos Python). Uma TUI abre instantaneamente no mesmo terminal onde o operador já roda `kubectl` — sem trocar de janela, sem esperar um servidor subir, sem abrir navegador. Isso combina diretamente com o objetivo do ticket: encurtar os primeiros dez minutos de reconhecimento, não adicionar uma etapa.

## Alternativas descartadas

### Alternativa descartada A — Go + client-go + TUI (bubbletea/tview)

- **O que se ganha**: binário único, estático, sem dependência de interpretador ou pacotes instalados na estação do operador — `go build` e distribui um arquivo. Performance superior e tipagem mais forte contra a API do Kubernetes. `client-go` é a mesma biblioteca que o próprio `kubectl` usa internamente, o que dá confiança de que o comportamento de autenticação/contexto está alinhado com a ferramenta que todos já usam.

- **O que se perde**: o time que mantém isso hoje não escreve Go — mantém Python em todos os outros artefatos deste desafio. Trocar de stack aqui significa um segundo conjunto de convenções, um segundo pipeline de build, uma segunda curva de aprendizado para quem for dar manutenção. Para uma ferramenta interna de baixo tráfego (um operador por vez, algumas centenas de objetos), o ganho de performance do Go não paga o custo de fragmentar a stack do time.

### Alternativa descartada B — aplicação web (backend Python + frontend HTML/JS, aberta no navegador local)

- **O que se ganha**: mais liberdade visual (tabelas ricas, cores, potencial de adicionar links e drill-down mais tarde), paradigma mais familiar para desenvolvedores web, caminho natural se algum dia o dashboard precisar ser compartilhado entre múltiplos operadores.

- **O que se perde**: o ticket descreve a ferramenta como algo que "roda na máquina de quem opera" — uma aplicação web precisa de um processo servidor rodando e um navegador aberto apontando para `localhost`, dois processos coordenados em vez de um. Isso adiciona uma etapa (abrir o navegador, confiar que a porta local não está em conflito) exatamente onde o ticket pede menos etapas. Backend e frontend como projetos separados também dobra a superfície de manutenção para um time que hoje escreve scripts e ferramentas de linha de comando, não aplicações full-stack.

## O que a implementação confirmou ou contestou

**Linguagem/stack (Python + Textual)**: confirmada. A TUI rodou dentro do mesmo terminal sem fricção; o único atrito real foi a versão do Python (item 1 das correções), não a escolha da stack em si.
