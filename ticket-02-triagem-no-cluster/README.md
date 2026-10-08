# Ticket 02 — Triagem no Cluster

Este documento mapeia e aponta onde está cada item solicitado no **Entregue** do Ticket 02:

| Item do Entregue | Arquivo / Diretório | Descrição |
|---|---|---|
| **Skill de Triagem** | [`skill/SKILL.md`](./skill/SKILL.md) | Skill `metacortex-triage` (método de 5 camadas, estritamente read-only) |
| **Triagem Chamado 01** | [`saida/triagem-chamado-01-nyx-prod.md`](./saida/triagem-chamado-01-nyx-prod.md) | Diagnóstico completo: OOMKilled (Exit Code 137, limits.memory baixo) |
| **Triagem Chamado 02** | [`saida/triagem-chamado-02-orion-stg.md`](./saida/triagem-chamado-02-orion-stg.md) | Diagnóstico completo: ImagePullBackOff (tag inexistente no registry) |
| **Triagem Chamado 03** | [`saida/triagem-chamado-03-nyx-stg.md`](./saida/triagem-chamado-03-nyx-stg.md) | Diagnóstico completo: 503 com pods Running (discrepância Service × labels) |
| **Matriz de Roteamento** | [`saida/matriz-roteamento.md`](./saida/matriz-roteamento.md) | Desambiguação de disparo entre `metacortex-manifest` e `metacortex-triage` |
| **Comparação Com/Sem Skill** | [`saida/comparacao-com-sem-skill.md`](./saida/comparacao-com-sem-skill.md) | Benchmarking de tool calls, hipóteses e tempo em dois incidentes |
| **Medição de Tokens** | [`saida/medicao-tokens/`](./saida/medicao-tokens/) | `medir.sh` roda cada caso com e sem skill em sessões limpas (`claude -p`); `consolidar.py` gera as tabelas de tokens e custo em `comparacao-com-sem-skill.md` |
| **Origem e Curadoria** | [`origem-e-curadoria.md`](./origem-e-curadoria.md) | Gênese do método, garantia estrutural de não-escrita e limites |
| **Configuração do Servidor MCP** | [`.mcp.json`](./.mcp.json) | `mcp-server-kubernetes@4.1.9` em modo não destrutivo (`ALLOW_ONLY_NON_DESTRUCTIVE_TOOLS=true`), fixado no contexto `kind-metacortex-lab` |
| **Permissões do Agente** | [`.claude/settings.json`](./.claude/settings.json) | Libera só `kubectl_get`/`describe`/`logs`; nega as ferramentas de escrita e a troca de contexto que o modo não destrutivo ainda expõe |
| **Evidência do Modo Não Destrutivo** | [`saida/evidencia-mcp-nao-destrutivo.txt`](./saida/evidencia-mcp-nao-destrutivo.txt) | `tools/list` do servidor iniciado com a configuração versionada: ferramentas destrutivas ausentes |
| **Manifests dos Laboratórios** | [`manifests/`](./manifests/) | Manifests aplicados no cluster `kind-metacortex-lab` para os 3 chamados |

## Como reproduzir o ambiente

Abra o Claude Code **a partir desta pasta** para que `.mcp.json` e `.claude/settings.json` sejam carregados:

```bash
cd ticket-02-triagem-no-cluster
claude
# /mcp  → deve listar o servidor "kubernetes" conectado
```

---
- **Agente:** Claude Code
- **Modelos:** Claude Opus 4.8 / Claude Sonnet 4.6
