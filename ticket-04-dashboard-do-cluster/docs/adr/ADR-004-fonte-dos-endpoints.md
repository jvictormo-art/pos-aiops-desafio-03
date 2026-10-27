# ADR-004 — Endpoints (`v1`) ou EndpointSlice (`discovery.k8s.io/v1`)

| Campo | Valor |
|---|---|
| Status | aceito |
| Data | 2026-09-17 (registrado como ADR próprio em 2026-10-27; origem: `spec/spec-decisoes.md`, Decisão 4) |
| Decisão em aberto do enunciado | "Fonte dos endpoints: Endpoints ou EndpointSlice, considerando por quanto tempo o código vai continuar funcionando" |

## Decisão

**Escolhido**: `EndpointSlice`.


**Por quê**: `v1/Endpoints` está em rota de aposentadoria — a evidência disso apareceu sem ser buscada: `kubectl get endpoints -n nyx-dev` durante a coleta de evidência deste próprio ticket imprimiu `Warning: v1 Endpoints is deprecated in v1.33+; use discovery.k8s.io/v1 EndpointSlice`. Construir uma ferramenta nova sobre uma API que o próprio Kubernetes já avisa para não usar é comprar dívida técnica no primeiro dia.

## Alternativas descartadas

### Alternativa descartada A — manter `v1/Endpoints`

- **O que se ganha**: um objeto por Service (mapeamento 1:1 simples), API mais antiga e mais estável em termos de forma (não sofreu mudanças de schema recentes), e é o objeto que o próprio exemplo do ticket usa para ilustrar o problema do Chamado 3.

- **O que se perde**: durabilidade. `Endpoints` já está marcado como deprecated a partir do Kubernetes v1.33 nos avisos do próprio `kubectl`; construir a leitura do dashboard sobre ele significa que a próxima major version pode remover o suporte, obrigando uma reescrita não planejada.

### Alternativa descartada B — consultar ambos e escolher o que responder primeiro

- **O que se ganha**: comportamento correto em clusters antigos (sem EndpointSlice habilitado) e novos ao mesmo tempo.

- **O que se perde**: complexidade dobrada para um cenário que não existe no parque da Metacortex — `EndpointSlice` é GA desde o Kubernetes 1.21 e está habilitado por padrão em qualquer cluster suportado hoje. Cobrir os dois formatos é engenharia para um problema hipotético, não para o cluster real. `EndpointSlice` sozinho basta.

**Nuance registrada**: um Service pode ter múltiplos objetos `EndpointSlice` (o Kubernetes particiona endereços em fatias de até 100 por padrão). O dashboard soma os endereços prontos (`endpoints[].conditions.ready`) através de todas as fatias do mesmo Service antes de decidir "tem endpoint" ou "não tem" — não basta olhar a primeira fatia.

## O que a implementação confirmou ou contestou

**EndpointSlice em vez de Endpoints**: confirmada, e a durabilidade do argumento apareceu de forma extra: o próprio `kubectl` emitiu o aviso de depreciação durante a coleta de evidência deste ticket, sem eu precisar procurar por ele.
