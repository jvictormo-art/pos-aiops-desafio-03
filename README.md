# Desafio 3 — Engenharia de Prompt e Contexto

Quatro tickets do parque da Metacortex: duas skills (Tickets 01 e 02) e dois projetos completos com código rodando (Tickets 03 e 04). Cada pasta tem um `README.md` que aponta onde está **cada item do Entregue** daquele ticket.

| Ticket | Pasta | O que é |
|---|---|---|
| 01 — Skill do padrão de manifests | [`ticket-01-padrao-de-manifests/`](./ticket-01-padrao-de-manifests/) | `metacortex-manifest`: escreve e confere manifests no padrão da casa (script + instrução, sem reimplementar o Trivy) |
| 02 — Skill de triagem de cluster | [`ticket-02-triagem-no-cluster/`](./ticket-02-triagem-no-cluster/) | `metacortex-triage`: método único de triagem pelo `mcp-server-kubernetes` em modo não destrutivo; matriz de roteamento e medição com × sem skill |
| 03 — Inventário e drift de VM por SSH | [`ticket-03-inventario-de-vm/`](./ticket-03-inventario-de-vm/) | `metacortex-inventario`: CLI agentless que compara a VM com o baseline (arco de spec + OpenSpec) |
| 04 — Dashboard do cluster | [`ticket-04-dashboard-do-cluster/`](./ticket-04-dashboard-do-cluster/) | `metacortex-dashboard`: TUI de leitura do contexto corrente (arco de spec + OpenSpec + um ADR por decisão em aberto) |

## Skills instaladas

As duas skills estão instaladas onde o agente as descobre, na raiz do desafio:

```
.claude/skills/metacortex-manifest -> ticket-01-padrao-de-manifests/skill
.claude/skills/metacortex-triage   -> ticket-02-triagem-no-cluster/skill
```

Foram usadas instaladas na matriz de roteamento (Ticket 02), nas triagens dos chamados (Ticket 02) e durante o projeto do dashboard (Ticket 04), sempre em sessões gravadas.

## Ambiente de laboratório

| Peça | Para quê |
|---|---|
| Cluster `kind-metacortex-lab` (Kubernetes 1.36) | Chamados do Ticket 02 e workloads do Ticket 04 (kube-news em `nyx-dev`, fake-shop em `orion-prod`) |
| `mcp-server-kubernetes` 4.1.9 em modo não destrutivo | Acesso do agente ao cluster ([`ticket-02-triagem-no-cluster/.mcp.json`](./ticket-02-triagem-no-cluster/.mcp.json)) |
| VM Ubuntu 24.04 (Lima) | Host conforme do Ticket 03 |
| Containers Ubuntu 22.04 | Hosts com desvios e sem systemd/`ss` do Ticket 03 |
| OpenSpec 1.15.0 | Ciclo de spec dos Tickets 03 e 04 (`openspec/` em cada um) |

## Revisões

### Revisão 1 (2026-10-08)

| Ponto | O que mudou | Onde |
|---|---|---|
| `inventario.py` devolvia `conforme` para dado não coletado | Todo coletor confere o código de saída; o que não foi coletado vira `nao_verificado` com motivo | Ticket 03 · change `coleta-nao-verificada` |
| Comparação com × sem skill sem tokens | 12 sessões medidas | [`comparacao-com-sem-skill.md`](./ticket-02-triagem-no-cluster/saida/comparacao-com-sem-skill.md) |
| Configuração do MCP não versionada | `.mcp.json` em modo não destrutivo + permissões | [`ticket-02-triagem-no-cluster/.mcp.json`](./ticket-02-triagem-no-cluster/.mcp.json) |
| Desafios 1 e 2 no mesmo repositório | Repositório só com o Desafio 3 | — |

### Revisão 2 (2026-10-27)

| Ponto | O que mudou | Onde |
|---|---|---|
| Tickets 03 e 04 sem arco de spec (brainstorm, PRD, TRD, ADRs) nem OpenSpec; no 04, cada decisão em aberto como ADR separado | `docs/` com brainstorm, PRD, TRD e ADRs (5 no Ticket 03, 7 no Ticket 04, um por decisão em aberto); `openspec/` com as changes arquivadas. Os documentos da versão 1.0 foram reconstituídos de `spec/` e dizem isso no cabeçalho; as correções desta revisão passaram por um ciclo real da CLI (proposal → specs → design → tasks → código → archive) | [`ticket-03-.../docs/`](./ticket-03-inventario-de-vm/docs/) · [`ticket-03-.../openspec/`](./ticket-03-inventario-de-vm/openspec/) · [`ticket-04-.../docs/`](./ticket-04-dashboard-do-cluster/docs/) · [`ticket-04-.../openspec/`](./ticket-04-dashboard-do-cluster/openspec/) |
| Ticket 03 sem código de retorno, sem host inalcançável, sem host conforme | 15 evidências reais, cada uma com comando e código de retorno: VM Ubuntu 24.04 conforme (0 desvio), host com desvios, sem systemd/`ss`, endereço que não resolve, IP sem resposta, chave recusada, SSH fora do ar, segunda execução idêntica | [`ticket-03-.../saida/evidencia/`](./ticket-03-inventario-de-vm/saida/evidencia/) |
| Ticket 02: matriz de roteamento sem teste real | Skills instaladas; 10 frases × 3 sessões limpas em diretório isolado, antes e depois dos ajustes, mais frases reformuladas; logs versionados | [`matriz-roteamento.md`](./ticket-02-triagem-no-cluster/saida/matriz-roteamento.md) |
| Ticket 02: triagens com `kubectl` manual | Skill executada pelo agente nos três chamados, só com as ferramentas do `mcp-server-kubernetes`; cada chamada MCP registrada | [`triagem-chamado-0*.md`](./ticket-02-triagem-no-cluster/saida/) |
| Ticket 04: skills não instaladas e só um projeto de pé | Skills em `.claude/skills/`; kube-news e fake-shop rodando com os manifests da skill (HTTP 200); comportamento das skills registrado em sessões gravadas | [`ticket-04-.../README.md`](./ticket-04-dashboard-do-cluster/README.md) |

Além dos pontos citados, a conferência do enunciado item a item encontrou e corrigiu: formato da saída do Ticket 03 diferente do exemplo do enunciado (uma entrada por regra, Markdown), resposta ausente sobre "o quanto o dashboard pode afirmar sobre saúde" (ADR-007 do Ticket 04), garantia de só leitura do dashboard dependente de intenção (agora teste + ClusterRole), defeito no manifest do fake-shop do Ticket 01 que só aparecia ao rodar, senha versionada no Secret do kube-news e um erro na tabela de decisão da skill de triagem. Os detalhes estão na curadoria de cada ticket.

## Agentes e modelos

- **Execução dos tickets:** Claude Code. Claude Opus 4.8 (concepção, especificações e skills) e Claude Sonnet 4.6 (implementação) na versão 1.0; Claude Opus 5.5 nas revisões.
- **Sessões gravadas** (medição de tokens, matriz de roteamento, triagens, observação das skills): Claude Code em modo não interativo (`claude -p`), Claude Sonnet 5.5.
- **Consolidação do README da versão 1.0:** Antigravity com Gemini 3.8 Flash (High).
