# Ticket 04 — Dashboard do cluster

`metacortex-dashboard`: aplicação de terminal que mostra o retrato de um namespace do cluster do **contexto corrente** do kubeconfig, só lendo.

## Onde está cada item do Entregue

| Item do enunciado | Onde |
|---|---|
| **Arco de spec: brainstorm** | [`docs/01-brainstorm.md`](./docs/01-brainstorm.md) |
| **PRD** | [`docs/02-PRD.md`](./docs/02-PRD.md) |
| **TRD** | [`docs/03-TRD.md`](./docs/03-TRD.md) |
| **ADRs, um por decisão em aberto** | [`docs/adr/`](./docs/adr/) |
| ↳ Linguagem e stack | [ADR-001](./docs/adr/ADR-001-linguagem-e-stack.md) |
| ↳ Como falar com a API do Kubernetes | [ADR-002](./docs/adr/ADR-002-acesso-a-api-do-kubernetes.md) |
| ↳ Como manter a tela atualizada | [ADR-003](./docs/adr/ADR-003-atualizacao-da-tela.md) |
| ↳ Endpoints ou EndpointSlice | [ADR-004](./docs/adr/ADR-004-fonte-dos-endpoints.md) |
| ↳ Recorte da primeira fatia | [ADR-005](./docs/adr/ADR-005-recorte-da-primeira-fatia.md) |
| ↳ Garantia de só leitura visível no projeto | [ADR-006](./docs/adr/ADR-006-garantia-de-somente-leitura.md) |
| ↳ O que a tela pode afirmar sobre saúde | [ADR-007](./docs/adr/ADR-007-o-que-a-tela-afirma-sobre-saude.md) |
| **Artefatos do ciclo do OpenSpec** | [`openspec/`](./openspec/): spec vigente em [`openspec/specs/dashboard-cluster/spec.md`](./openspec/specs/dashboard-cluster/spec.md); changes em [`openspec/changes/`](./openspec/changes/), cada uma com `proposal.md`, `design.md`, `tasks.md` e `specs/` |
| **Código** | [`dashboard/app.py`](./dashboard/app.py) (interface), [`dashboard/k8s_reader.py`](./dashboard/k8s_reader.py) (única camada que fala com a API) |
| **Garantia de só leitura** | código + [`dashboard/test_somente_leitura.py`](./dashboard/test_somente_leitura.py) + [`rbac/dashboard-leitura.yaml`](./rbac/dashboard-leitura.yaml), aplicada no cluster e conferida com `kubectl auth can-i` em [`evidencia/10-identidade-somente-leitura.txt`](./evidencia/10-identidade-somente-leitura.txt) (lê os seis recursos da tela; não apaga, altera, cria nem executa) |
| **Testes** | `cd dashboard && python3 -m unittest test_somente_leitura test_k8s_reader` (13 testes) |
| **Evidência de execução contra o cluster** | [`evidencia/`](./evidencia/), gerada por [`evidencia/capturar.py`](./evidencia/capturar.py) |
| ↳ Aplicação rodando | `01` kube-news (nyx-dev) · `05` fake-shop (orion-prod) · `02`–`04` chamados do Ticket 02 · `09` busca por nome |
| ↳ Cluster que não responde | `06-cluster-inalcancavel.svg` |
| ↳ Credencial expirada/inválida | `07-credencial-invalida.svg` |
| ↳ Permissão negada para um tipo de recurso | `08-rbac-restrito-platform-ro.svg` |
| **Registro das skills durante o projeto** | [`saida/skills-neste-projeto.md`](./saida/skills-neste-projeto.md), com as sessões gravadas em [`saida/sessoes-skills/`](./saida/sessoes-skills/) |
| **Curadoria** | [`saida/curadoria.md`](./saida/curadoria.md): correções da spec, o que o agente entendeu diferente e a justificativa estendida de cada decisão |

## Pré-requisitos do enunciado

| Pré-requisito | Como foi cumprido |
|---|---|
| Pelo menos dois projetos de pé, em namespaces separados, com os manifests da skill do Ticket 01 | **kube-news** em `nyx-dev` ([`manifests-kube-news/`](./manifests-kube-news/), gerados numa sessão em que a `metacortex-manifest` disparou sozinha) e **fake-shop** em `orion-prod` ([manifests do Ticket 01](../ticket-01-padrao-de-manifests/saida/manifests-orion/)). Os dois respondem HTTP 200 |
| Skills dos Tickets 01 e 02 instaladas no agente | `.claude/skills/` na raiz do desafio ([registro](./saida/skills-neste-projeto.md)) |

## Como reproduzir

```bash
# 1. Workloads (imagens espelhadas como registry.metacortex.io, Secrets fora do Git)
laboratorio/subir-workloads.sh
# 2. Kubeconfigs dos cenários de falha (o segundo comando cria RBAC no cluster)
laboratorio/cenarios-de-falha.sh
laboratorio/cenarios-de-falha.sh platform-ro
# 3. Testes e evidências
cd dashboard && pip3 install -r requirements.txt && python3 -m unittest test_somente_leitura test_k8s_reader
python3 ../evidencia/capturar.py
# 4. Usar
python3 app.py [--namespace nyx-dev]
```

## Histórico

Os documentos da versão 1.0 foram escritos em `spec/` (proposta, decisões, comportamento, tarefas, arquivo final; commit "Add metacortex-dashboard e entregas do Ticket 04"). A revisão 2 pediu cada etapa do arco como documento próprio, um ADR por decisão e o ciclo do OpenSpec: o conteúdo foi migrado para `docs/` e para a change reconstituída do OpenSpec, que declara isso no cabeçalho. A change da revisão 2 foi feita com a CLI do OpenSpec (1.15.0), com spec e tarefas escritas antes do código.

- **Agente:** Claude Code · **Modelos:** Claude Opus 4.8 / Sonnet 4.6 (v1.0) e Claude Opus 5.5 (revisão 2); sessões gravadas com Sonnet 5.5
