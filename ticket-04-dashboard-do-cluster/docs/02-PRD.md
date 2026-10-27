# PRD — metacortex-dashboard

| Campo | Valor |
|---|---|
| Versão | 1.1 |
| Status | aprovado |
| Histórico | 1.0 (2026-09-17, origem: `spec/proposta.md`, commit "Add metacortex-dashboard e entregas do Ticket 04") · 1.1 (2026-10-27, revisão 2: garantia de leitura por permissão e teste, cenários reproduzíveis, o que a tela afirma sobre saúde) |

> A versão 1.0 foi escrita como `spec/proposta.md`. Em 2026-10-27 o conteúdo foi movido para este documento próprio; as mudanças da 1.1 vêm da change do OpenSpec `leitura-garantida-e-saude-honesta`.

---

## Problema

Toda triagem começa com seis a dez comandos no terminal para montar o retrato de um namespace. Isso consome os primeiros minutos de cada chamado antes de a investigação começar.

## Usuários

Plantonistas e SREs da Metacortex, na própria estação, com o kubeconfig que já usam no `kubectl`.

## O que a aplicação faz

Lê o **contexto corrente** do kubeconfig no momento em que sobe e mostra:

- namespaces do cluster (seletor);
- pods com estado, reinícios e motivo quando em falha;
- deployments com réplicas prontas sobre desejadas;
- services e se têm endpoint;
- eventos recentes do namespace selecionado;
- filtro por namespace e busca por nome.

Não substitui o terminal; encurta o reconhecimento.

## Requisitos não funcionais

- **Só leitura, verificável.** Nenhuma operação de escrita (`apply`, `delete`, `scale`, `patch`). A garantia está no código (só verbos de leitura), num teste automático que falha se aparecer um verbo de escrita, e numa ClusterRole versionada só com `get`/`list`/`watch` ([ADR-006](./adr/ADR-006-garantia-de-somente-leitura.md)).
- **Contexto corrente, e só ele.** Sem seletor de cluster; o nome do contexto fica visível na tela.
- **Sem tela em branco nem stack trace** quando o ambiente falha.
- **Honestidade sobre saúde.** A tela mostra o que a API diz ("pronto", "disponível"), nunca "saudável", e marca quando "pronto" não passou por nenhuma probe ([ADR-007](./adr/ADR-007-o-que-a-tela-afirma-sobre-saude.md)).

## Pré-requisitos do enunciado

| Pré-requisito | Como foi cumprido |
|---|---|
| Pelo menos dois projetos de pé, em namespaces separados, com os manifests da skill do Ticket 01 | kube-news em `nyx-dev` (manifests gerados numa sessão em que a `metacortex-manifest` disparou sozinha) e fake-shop em `orion-prod` (manifests do Ticket 01). Os dois respondem HTTP 200. Reproduzível com [`../laboratorio/subir-workloads.sh`](../laboratorio/subir-workloads.sh) |
| Skills dos Tickets 01 e 02 instaladas no agente | `.claude/skills/metacortex-manifest` e `.claude/skills/metacortex-triage` na raiz do desafio; registro do comportamento em [`../saida/skills-neste-projeto.md`](../saida/skills-neste-projeto.md) |

## Critérios de aceite

| # | Critério | Evidência |
|---|---|---|
| CA1 | Roda contra o contexto corrente, sem flag de cluster | `evidencia/01`–`05` |
| CA2 | Mostra os cinco objetos, com filtro por namespace e busca por nome | `evidencia/01`–`05` |
| CA3 | Distingue campo ausente de campo vazio (nada de `None` na tela) | `evidencia/03` (`readyReplicas` ausente → `0/3`), `evidencia/04` (Service sem endpoint) |
| CA4 | Cluster que não responde: mensagem, sem tela em branco nem stack trace | `evidencia/06` |
| CA5 | Credencial expirada ou inválida: idem | `evidencia/07` |
| CA6 | Permissão negada para um tipo de recurso, os outros continuam | `evidencia/08` (contexto `platform-ro`) |
| CA7 | Nenhuma chamada de escrita, verificável | `dashboard/test_somente_leitura.py` + `rbac/dashboard-leitura.yaml` + `evidencia/10` (`kubectl auth can-i`) |
| CA8 | "Pronto" sem probe é sinalizado | `evidencia/01` (Postgres de apoio sem probe) |

## Fora do escopo

| Item | Motivo |
|---|---|
| Multicluster / seletor de contexto | Corte explícito do enunciado |
| Watch / streaming | [ADR-003](./adr/ADR-003-atualizacao-da-tela.md): polling na primeira fatia |
| Ações a partir da tela | Viola o invariante de leitura |
| Métricas de CPU/memória | `metrics-server` não é garantido ([ADR-005](./adr/ADR-005-recorte-da-primeira-fatia.md)) |
| Verificação de saúde da aplicação (chamar `/health`) | Exigiria acesso de rede aos pods; a tela fica no que a API diz ([ADR-007](./adr/ADR-007-o-que-a-tela-afirma-sobre-saude.md)) |
