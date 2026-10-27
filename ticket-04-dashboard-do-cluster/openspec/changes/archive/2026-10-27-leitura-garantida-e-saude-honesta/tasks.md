# Tasks

## 1. Testes primeiro

- [x] 1.1 Escrever `dashboard/test_somente_leitura.py` (AST + verbos da ClusterRole) — verificação: falha enquanto `rbac/dashboard-leitura.yaml` não existe
- [x] 1.2 Escrever `dashboard/test_k8s_reader.py` com objetos falsos: pod pronto sem probe marcado, pod com probe sem marca, EndpointSlice com 403 vira "endpoint não verificado", `readyReplicas` ausente vira 0 — verificação: os testes novos falham contra o código atual

## 2. Implementação

- [x] 2.1 `_resumir_pod` devolve `sem_readiness`; `app.py` marca `*` e mostra a legenda — verificação: testes de pod passam
- [x] 2.2 `_contar_endpoints_prontos` devolve `None` + motivo em falha; texto "endpoint não verificado (<motivo>)" — verificação: teste de 403 passa
- [x] 2.3 Criar `rbac/dashboard-leitura.yaml` — verificação: teste de somente leitura passa; `kubectl auth can-i` com a SA confirma leitura sim, escrita não

## 3. Cenários e evidência

- [x] 3.1 `laboratorio/cenarios-de-falha.sh` gera os três kubeconfigs — verificação: cada um produz o erro esperado no `kubectl`
- [x] 3.2 `evidencia/capturar.py` gera os oito SVGs (nyx-dev, nyx-prod, orion-stg, nyx-stg, orion-prod, inalcançável, credencial inválida, platform-ro) — verificação: SVGs mostram kube-news e fake-shop de pé, a marca `*` no Postgres sem probe e os três cenários de falha sem stack trace

## 4. Documentação

- [x] 4.1 Atualizar curadoria, registro das skills e README do ticket — verificação: README aponta cada item do Entregue
