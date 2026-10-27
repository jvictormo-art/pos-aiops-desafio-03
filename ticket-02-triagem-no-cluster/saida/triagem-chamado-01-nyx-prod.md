# Triagem — Chamado 01-nyx-prod

Saída real da skill `metacortex-triage`, executada pelo agente numa sessão limpa do Claude Code (`claude -p`, modelo `claude-sonnet-5-5`). O acesso ao cluster foi **só** pelo `mcp-server-kubernetes` em modo não destrutivo ([`.mcp.json`](../.mcp.json)); Bash ficou bloqueado na sessão, então não havia como rodar `kubectl` direto. Registro bruto: [`triagens/logs/chamado-01-nyx-prod.jsonl`](./triagens/logs/chamado-01-nyx-prod.jsonl).

| Item | Valor |
|---|---|
| Servidor MCP | `kubernetes` (connected) |
| Ferramentas do servidor disponíveis na sessão | 17 (nenhuma de escrita destrutiva: o modo não destrutivo remove `kubectl_delete`, `exec_in_pod` e afins) |
| Skills instaladas | metacortex-manifest, metacortex-triage |
| Turnos / duração / custo | 7 / 18 s / US$ 0.0910 |

**Skill carregada:** `metacortex-triage`

## Chamada 1: `mcp__kubernetes__kubectl_get`

```json
{"resourceType": "pods", "namespace": "nyx-prod", "output": "wide"}
```

Resposta do cluster:

```
NAME                           READY   STATUS             RESTARTS           AGE   IP            NODE                           NOMINATED NODE   READINESS GATES
nyx-api-656789474b-vm2jh       0/1     CrashLoopBackOff   1142 (4m24s ago)   39d   10.244.0.16   metacortex-lab-control-plane   <none>           <none>
nyx-api-656789474b-znchx       0/1     CrashLoopBackOff   1135 (4m45s ago)   39d   10.244.0.19   metacortex-lab-control-plane   <none>           <none>
nyx-postgres-f6fdc6dbf-x7wvv   1/1     Running            2 (15m ago)        39d   10.244.0.15   metacortex-lab-control-plane   <none>           <none>
```

## Chamada 2: `mcp__kubernetes__kubectl_describe`

```json
{"resourceType": "pod", "name": "nyx-api-656789474b-vm2jh", "namespace": "nyx-prod"}
```

Resposta do cluster:

```
Name:             nyx-api-656789474b-vm2jh
Namespace:        nyx-prod
Priority:         0
Service Account:  default
Node:             metacortex-lab-control-plane/172.18.0.2
Start Time:       Thu, 17 Sep 2026 15:01:54 -0300
Labels:           app=nyx-api
                  pod-template-hash=656789474b
Annotations:      <none>
Status:           Running
IP:               10.244.0.16
IPs:
  IP:           10.244.0.16
Controlled By:  ReplicaSet/nyx-api-656789474b
Containers:
  api:
    Container ID:   containerd://0957b6a4a5a6b93ff89dcbdb77633b5f4dfe3a4474da904e738a3a861b20f308
    Image:          fabricioveronez/kube-news:v1
    Image ID:       docker.io/fabricioveronez/kube-news@sha256:f86b40ce1bcbdf297b6236a8212f3e66c8412113aaa8855ba2747c79182734e5
    Port:           8080/TCP
    Host Port:      0/TCP
    State:          Waiting
      Reason:       CrashLoopBackOff
    Last State:     Terminated
      Reason:       OOMKilled
      Exit Code:    137
      Started:      Tue, 27 Oct 2026 14:04:25 -0300
      Finished:     Tue, 27 Oct 2026 14:04:27 -0300
    Ready:          False
    Restart Count:  1142
    Limits:
      cpu:     200m
      memory:  24Mi
    Requests:
      cpu:      50m
      memory:   16Mi
    Readiness:  http-get http://:8080/ready delay=10s timeout=1s period=10s #success=1 #failure=3
    Environment:
      DB_HOST:      nyx-postgres
      DB_DATABASE:  kubedevnews
      DB_USERNAME:  kubedevnews
      DB_PASSWORD:  Pg#123
    Mounts:
      /var/run/secrets/kubernetes.io/serviceaccount from kube-api-access-kkv8f (ro)
Conditions:
… (33 linhas omitidas; resposta completa no log .jsonl)
```

## Chamada 3: `mcp__kubernetes__kubectl_describe`

```json
{"resourceType": "pod", "name": "nyx-api-656789474b-znchx", "namespace": "nyx-prod"}
```

Resposta do cluster:

```
Name:             nyx-api-656789474b-znchx
Namespace:        nyx-prod
Priority:         0
Service Account:  default
Node:             metacortex-lab-control-plane/172.18.0.2
Start Time:       Thu, 17 Sep 2026 15:01:54 -0300
Labels:           app=nyx-api
                  pod-template-hash=656789474b
Annotations:      <none>
Status:           Running
IP:               10.244.0.19
IPs:
  IP:           10.244.0.19
Controlled By:  ReplicaSet/nyx-api-656789474b
Containers:
  api:
    Container ID:   containerd://66bc3fe381494841eebdfbcff603c662c98d52e5dd7e453be5f619988394c828
    Image:          fabricioveronez/kube-news:v1
    Image ID:       docker.io/fabricioveronez/kube-news@sha256:f86b40ce1bcbdf297b6236a8212f3e66c8412113aaa8855ba2747c79182734e5
    Port:           8080/TCP
    Host Port:      0/TCP
    State:          Waiting
      Reason:       CrashLoopBackOff
    Last State:     Terminated
      Reason:       OOMKilled
      Exit Code:    137
      Started:      Tue, 27 Oct 2026 14:04:05 -0300
      Finished:     Tue, 27 Oct 2026 14:04:06 -0300
    Ready:          False
    Restart Count:  1135
    Limits:
      cpu:     200m
      memory:  24Mi
    Requests:
      cpu:      50m
      memory:   16Mi
    Readiness:  http-get http://:8080/ready delay=10s timeout=1s period=10s #success=1 #failure=3
    Environment:
      DB_HOST:      nyx-postgres
      DB_DATABASE:  kubedevnews
      DB_USERNAME:  kubedevnews
      DB_PASSWORD:  Pg#123
    Mounts:
      /var/run/secrets/kubernetes.io/serviceaccount from kube-api-access-s2qs4 (ro)
Conditions:
… (34 linhas omitidas; resposta completa no log .jsonl)
```

## Diagnóstico do agente

**CAUSA:** As duas réplicas da `nyx-api` são mortas por falta de memória (OOMKilled, exit 137) porque o limite de memória do container está em 24Mi, baixo demais para a aplicação.

**EVIDÊNCIA:**
- `pod/nyx-api-656789474b-vm2jh` e `pod/nyx-api-656789474b-znchx`, container `api`:
  - `Last State: Terminated, Reason: OOMKilled, Exit Code: 137`.
  - `Limits.memory: 24Mi`, com `Requests.memory: 16Mi` e `Limits.cpu: 200m`.
  - O container vive cerca de 2 segundos (14:04:25 → 14:04:27 e 14:04:05 → 14:04:06), ou seja, morre logo na subida.
- Restart count: 1142 e 1135, ambos em `CrashLoopBackOff`.
- Os eventos mostram `BackOff` em loop e `Started`/`Created` repetidos, sem erro de pull. A imagem `fabricioveronez/kube-news:v1` já está no nó.

**CAMADA:** container

**AÇÃO SUGERIDA (não aplicada):**
- Subir `resources.limits.memory` (e o `requests.memory` correspondente) do deployment `nyx-api` para um valor que comporte uma app Node. Como ponto de partida, algo na faixa de 256Mi–512Mi, ajustado depois pela medição real de uso.
- Como o corte de custos mexeu nos limites do namespace inteiro, vale revisar os outros workloads e qualquer `LimitRange` ou `ResourceQuota` do `nyx-prod` que tenha sido alterado junto.

**O que está funcionando:**
- O `nyx-postgres` está `1/1 Running`, com 2 restarts, o último há 15 minutos (coincide com o `SandboxChanged` dos pods da API). O banco não é a causa.
- Não há problema de imagem, de agendamento nem de rede. Os pods estão agendados e os eventos não mostram falha de pull.

**Ressalvas:**
- Não confirmei que o limite de 24Mi veio do corte de custos. Os pods têm 39 dias e os restarts começam bem antes, então o limite pode estar baixo desde o início. O histórico do deployment ou do Git diria quando mudou, mas isso fica fora da triagem.
- Não li os logs, porque o `describe` já fechou a causa.
- Fora do escopo do chamado: o `DB_PASSWORD` está em texto puro nas variáveis de ambiente do deployment. Vale mover para um Secret.
