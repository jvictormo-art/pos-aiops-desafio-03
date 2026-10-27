# ADR-003 — Estratégia de atualização da tela

| Campo | Valor |
|---|---|
| Status | aceito |
| Data | 2026-09-17 (registrado como ADR próprio em 2026-10-27; origem: `spec/spec-decisoes.md`, Decisão 3) |
| Decisão em aberto do enunciado | "Como manter a tela atualizada: consulta sob demanda, consulta em intervalo fixo, ou observação de mudanças (watch)" |

## Decisão

**Escolhido**: consulta em intervalo fixo (polling, a cada 5 segundos) na primeira fatia.


**Por quê**: é o ponto de equilíbrio entre "a tela precisa estar razoavelmente atual" e "o código precisa ser simples o suficiente para validar rápido contra um cluster real". Um poll que falha simplesmente tenta de novo no próximo ciclo — não há estado de conexão para recuperar.

## Alternativas descartadas

### Alternativa descartada A — consulta sob demanda (só busca quando o operador pede)

- **O que se ganha**: carga mínima possível sobre o apiserver — só uma requisição por ação explícita do operador. Implementação mais simples ainda que o polling.

- **O que se perde**: isso contraria a própria motivação do ticket. Se o operador precisa apertar "atualizar" para ver cada mudança, a ferramenta não é mais rápida que rodar os mesmos 6-10 `kubectl get` um por um — só troca o lugar onde os comandos são digitados. O valor de "assistir o estado se assentar" (por exemplo, ver os pods saindo de `CrashLoopBackOff` depois de uma correção) se perde.

### Alternativa descartada B — watch/informer (observar mudanças e receber eventos conforme acontecem)

- **O que se ganha**: atualização quase em tempo real, menor volume total de dados trafegados ao longo do tempo (só deltas, não o estado completo repetido), e é a arquitetura "correta" para ferramentas de observação de longa duração — é o que `k9s` e o próprio `kubectl get -w` fazem.

- **O que se perde**: é, de longe, a peça de maior complexidade e maior risco da primeira fatia. Um watch exige rastrear `resourceVersion` por tipo de recurso, tratar o erro `410 Gone` (quando a versão observada expirou e é preciso re-sincronizar do zero), reconectar com backoff quando a conexão cai, e multiplexar cinco streams independentes (pods, deployments, services, endpointslices, eventos) simultaneamente. Um loop de reconexão de watch malfeito, rodando contra um apiserver de produção, é uma versão auto-inflingida do próprio problema que o ticket quer resolver — silenciosamente parar de atualizar e ninguém notar. Fica registrado como a evolução natural da segunda fatia, depois que a versão com polling for validada em uso real.

## O que a implementação confirmou ou contestou

**Polling em vez de watch**: confirmada sem ressalvas — nenhum dos cinco cenários de falha testados exigiu lógica de reconexão de watch, e a simplicidade do polling permitiu isolar e corrigir os cinco problemas reais (lista acima) rápido, um por vez.
