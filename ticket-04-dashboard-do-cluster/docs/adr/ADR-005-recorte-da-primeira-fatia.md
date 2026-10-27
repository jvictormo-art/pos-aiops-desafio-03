# ADR-005 — Quanto do escopo entra na primeira fatia

| Campo | Valor |
|---|---|
| Status | aceito |
| Data | 2026-09-17 (registrado como ADR próprio em 2026-10-27; origem: `spec/spec-decisoes.md`, Decisão 5) |
| Decisão em aberto do enunciado | "Recorte da primeira fatia: o que entra na primeira spec e o que fica para depois" |

## Decisão

**Escolhido**: exatamente os 5 objetos citados como mínimo no ticket (namespaces, pods, deployments, services+endpoints, eventos), com filtro por namespace e busca por nome. Nada de métricas de CPU/memória, nada de PodDisruptionBudget, nada de ação a partir da tela.

## Alternativas descartadas

### Alternativa descartada A — fatia mais fina ainda: só pods

- **O que se ganha**: caminho mais rápido para validar "conecta no contexto corrente e desenha algo real na tela" antes de investir nos outros quatro tipos de objeto.

- **O que se perde**: um dashboard só de pods não consegue mostrar o cenário do Chamado 3 (Service sem endpoint por seletor divergente) nem o do `orion-web` (Deployment com `unavailableReplicas` e `readyReplicas` ausente) — que são os próprios exemplos que o ticket usa para justificar a ferramenta. Entregar só pods falharia os critérios de aceite, que listam os 5 objetos como "no mínimo", não como aspiração.

### Alternativa descartada B — fatia mais larga: incluir métricas (CPU/memória via metrics-server) e PDB

- **O que se ganha**: resposta mais completa, inclusive um começo de resposta para a pergunta da Niobe sobre quanto o parque custa a mais por estar fora do padrão.

- **O que se perde**: `metrics-server` é um componente opcional do cluster, não garantido — e de fato **não está instalado** no cluster `kind-metacortex-lab` usado como evidência deste ticket. Construir uma feature que quebra silenciosamente quando metrics-server está ausente contradiz o próprio requisito de "comportar-se quando o ambiente não colabora" — e o jeito mais simples de não violar esse requisito é não depender de um componente que pode não existir. Fica registrado como escopo futuro, não como promessa desta versão.

## O que a implementação confirmou ou contestou

**Escopo da primeira fatia (sem métricas)**: confirmada — o cluster de evidência não tem `metrics-server` instalado, validando na prática o argumento de que depender dele seria construir algo que quebra no ambiente real disponível.
