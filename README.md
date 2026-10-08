# Desafio 3 — Engenharia de Prompt e Contexto

> Cada pasta de ticket possui um `README.md` próprio que aponta onde está cada item solicitado no **Entregue** daquele ticket.

## Tickets do Desafio

1. **Ticket 01: Padrão de Manifests**
   - **Pasta:** [ticket-01-padrao-de-manifests](./ticket-01-padrao-de-manifests/)
   - **Agente:** Claude Code
   - **Modelos:** Claude Opus 4.8 e Claude Sonnet 4.6

2. **Ticket 02: Triagem no Cluster**
   - **Pasta:** [ticket-02-triagem-no-cluster](./ticket-02-triagem-no-cluster/)
   - **Agente:** Claude Code
   - **Modelos:** Claude Opus 4.8 e Claude Sonnet 4.6

3. **Ticket 03: Inventário de VM**
   - **Pasta:** [ticket-03-inventario-de-vm](./ticket-03-inventario-de-vm/)
   - **Agente:** Claude Code
   - **Modelos:** Claude Opus 4.8 e Claude Sonnet 4.6

4. **Ticket 04: Dashboard do Cluster**
   - **Pasta:** [ticket-04-dashboard-do-cluster](./ticket-04-dashboard-do-cluster/)
   - **Agente:** Claude Code
   - **Modelos:** Claude Opus 4.8 e Claude Sonnet 4.6

---

## Ajustes após a revisão

| Ponto da revisão | O que mudou | Onde |
|---|---|---|
| `inventario.py` devolvia `conforme` para dado não coletado (VM sem systemd e sem `ss`) | O systemd passa a ser detectado por `/run/systemd/system`; todo coletor confere o código de saída e o que não foi coletado vira `nao_verificado` com motivo. 13 testes, dos quais 10 falham na versão anterior, e uma VM de teste sem systemd e sem `ss` | [`ticket-03-inventario-de-vm/ferramenta/`](./ticket-03-inventario-de-vm/ferramenta/) · [`spec/arquivo-final.md` §6](./ticket-03-inventario-de-vm/spec/arquivo-final.md) |
| Comparação com e sem skill sem número de tokens | 12 sessões medidas (3 por caso e variante) com tokens, custo e tool calls; a conclusão foi reescrita a partir dos números | [`ticket-02-triagem-no-cluster/saida/comparacao-com-sem-skill.md`](./ticket-02-triagem-no-cluster/saida/comparacao-com-sem-skill.md) · [`saida/medicao-tokens/`](./ticket-02-triagem-no-cluster/saida/medicao-tokens/) |
| Configuração do `mcp-server-kubernetes` em modo não destrutivo não versionada | `.mcp.json` com `ALLOW_ONLY_NON_DESTRUCTIVE_TOOLS=true` e contexto fixado, mais `.claude/settings.json` liberando só leitura | [`ticket-02-triagem-no-cluster/.mcp.json`](./ticket-02-triagem-no-cluster/.mcp.json) · [`.claude/settings.json`](./ticket-02-triagem-no-cluster/.claude/settings.json) |
| Repositório misturava os Desafios 1 e 2 | Este repositório contém só os quatro tickets do Desafio 3, com o histórico de commits preservado | — |

---

## Agentes e Modelos Utilizados

- **Agente de Execução dos Tickets:** Claude Code (Anthropic)
- **Modelos nos Tickets:** Claude Opus 4.8 (concepção, especificações e skills) e Claude Sonnet 4.6 (implementação das ferramentas e testes)
- **Agente de Consolidação/README:** Antigravity
- **Modelo na Consolidação/README:** Gemini 3.8 Flash (High)
