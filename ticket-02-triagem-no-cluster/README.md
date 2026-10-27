# Ticket 02 — Triagem no cluster

Skill `metacortex-triage`: método único de triagem de workloads Kubernetes, que acessa o cluster só pelo `mcp-server-kubernetes` em modo não destrutivo e nunca escreve.

## Onde está cada item do Entregue

| Item do enunciado | Onde |
|---|---|
| **A skill completa** | [`skill/SKILL.md`](./skill/SKILL.md), instalada em [`../.claude/skills/metacortex-triage`](../.claude/skills/) |
| **Configuração do servidor MCP em modo não destrutivo** | [`.mcp.json`](./.mcp.json) (`mcp-server-kubernetes@4.1.9`, `ALLOW_ONLY_NON_DESTRUCTIVE_TOOLS=true`, contexto fixado) e [`.claude/settings.json`](./.claude/settings.json) (só `get`/`describe`/`logs` liberados); verificação em [`saida/evidencia-mcp-nao-destrutivo.txt`](./saida/evidencia-mcp-nao-destrutivo.txt) |
| **Origem da skill** (fluxo, como foi produzida, ferramenta) | [`origem-e-curadoria.md`](./origem-e-curadoria.md), seção "De qual fluxo a skill nasceu" |
| **Saída real da triagem dos três chamados, com a causa** | Execução da skill pelo agente, com o cluster acessado **só pelas ferramentas do MCP** (cada chamada `mcp__kubernetes__kubectl_*` e o que o cluster respondeu): [`triagem-chamado-01-nyx-prod.md`](./saida/triagem-chamado-01-nyx-prod.md) (OOMKilled, limite de 24Mi) · [`triagem-chamado-02-orion-stg.md`](./saida/triagem-chamado-02-orion-stg.md) (tag `v1.14.2` inexistente) · [`triagem-chamado-03-nyx-stg.md`](./saida/triagem-chamado-03-nyx-stg.md) (seletor `nyx-api` × label `nyxapi`). Registro bruto em [`saida/triagens/logs/`](./saida/triagens/logs/) |
| **Matriz de roteamento** (o que disparou, o que errou, o que mudou) | [`saida/matriz-roteamento.md`](./saida/matriz-roteamento.md): as duas skills instaladas, 10 frases × 3 sessões limpas, antes e depois dos ajustes, mais frases reformuladas; logs em [`saida/roteamento/logs/`](./saida/roteamento/logs/) |
| **Comparação com e sem skill** (saída, custo e tempo) | [`saida/comparacao-com-sem-skill.md`](./saida/comparacao-com-sem-skill.md): 12 sessões medidas, tokens, custo, tool calls e duração; logs em [`saida/medicao-tokens/runs/`](./saida/medicao-tokens/runs/) |
| **Curadoria** (o que o método fixou e o que ficou com o agente; como foi garantido que não escreve) | [`origem-e-curadoria.md`](./origem-e-curadoria.md) |
| **Manifests dos três chamados** | [`manifests/`](./manifests/), aplicados no cluster `kind-metacortex-lab` |

## Como reproduzir

```bash
kubectl --context kind-metacortex-lab apply -f manifests/      # os três chamados
saida/triagens/rodar-triagens.sh                                # triagem dos três chamados pelo MCP
saida/roteamento/rodar-matriz.sh 3 <rotulo>                     # matriz de roteamento
saida/medicao-tokens/medir.sh 3                                 # com × sem skill
```

Todos os scripts abrem sessões do Claude Code (`claude -p`) com o servidor MCP de [`.mcp.json`](./.mcp.json) e Bash bloqueado.

- **Agente:** Claude Code · **Modelos:** Claude Opus 4.8 / Sonnet 4.6 (produção da skill) e Sonnet 5.5 (execuções gravadas)
