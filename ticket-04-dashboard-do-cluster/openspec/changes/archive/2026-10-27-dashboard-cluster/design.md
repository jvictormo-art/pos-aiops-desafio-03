# Design

> Change reconstituída de `spec/spec-decisoes.md` (2026-09-17). Cada decisão está em detalhe, com as alternativas descartadas, nos ADRs de `docs/adr/`.

## Context

Ferramenta local, contexto corrente apenas, cluster de produção acessado com a credencial de quem opera (ver proposal.md).

## Goals / Non-Goals

**Goals:**
- Os cinco objetos mínimos do enunciado, com filtro e busca.
- Cada painel independente: falha num tipo de recurso não derruba os outros.

**Non-Goals:**
- Multicluster, watch, métricas, ações a partir da tela.

## Decisions

- **Python + Textual (TUI)** em vez de Go ou web local (ADR-001).
- **Cliente oficial `kubernetes`** em vez de `kubectl` por subprocesso ou HTTP direto (ADR-002).
- **Polling de 5 s** em vez de sob demanda ou watch (ADR-003).
- **EndpointSlice** em vez de Endpoints (ADR-004).
- **Primeira fatia = os cinco objetos mínimos**, sem métricas nem PDB (ADR-005).
- **Só leitura estrutural**: só `ClusterReader` fala com a API, só com `list_*` (ADR-006, versão 1.0).

## Risks / Trade-offs

- [Polling repete o estado completo a cada ciclo] → carga baixa para um operador por vez; watch fica para a segunda fatia.
- [Cliente tipado pode falhar ao desserializar dados reais] → confirmado na implementação com `EndpointSlice.endpoints: null`; contornado com leitura crua só nesse ponto.
