# Triagem — Chamado 02-orion-stg

Saída real da skill `metacortex-triage`, executada pelo agente numa sessão limpa do Claude Code (`claude -p`, modelo `claude-sonnet-5-5`). O acesso ao cluster foi **só** pelo `mcp-server-kubernetes` em modo não destrutivo ([`.mcp.json`](../.mcp.json)); Bash ficou bloqueado na sessão, então não havia como rodar `kubectl` direto. Registro bruto: [`triagens/logs/chamado-02-orion-stg.jsonl`](./triagens/logs/chamado-02-orion-stg.jsonl).

| Item | Valor |
|---|---|
| Servidor MCP | `kubernetes` (connected) |
| Ferramentas do servidor disponíveis na sessão | 17 (nenhuma de escrita destrutiva: o modo não destrutivo remove `kubectl_delete`, `exec_in_pod` e afins) |
| Skills instaladas | metacortex-manifest, metacortex-triage |
| Turnos / duração / custo | 8 / 16 s / US$ 0.1379 |

**Skill carregada:** `metacortex-triage`

## Chamada 1: `mcp__kubernetes__kubectl_get`

```json
{"resourceType": "pods", "namespace": "orion-stg", "output": "wide"}
```

Resposta do cluster:

```
NAME                              READY   STATUS             RESTARTS      AGE   IP            NODE                           NOMINATED NODE   READINESS GATES
orion-postgres-6775c9f896-8f7w2   1/1     Running            2 (15m ago)   39d   10.244.0.14   metacortex-lab-control-plane   <none>           <none>
orion-web-67cd86ffd5-54v6l        0/1     ImagePullBackOff   0             39d   10.244.0.13   metacortex-lab-control-plane   <none>           <none>
orion-web-67cd86ffd5-ls7zv        0/1     ImagePullBackOff   0             39d   10.244.0.17   metacortex-lab-control-plane   <none>           <none>
orion-web-67cd86ffd5-tg7cb        0/1     ImagePullBackOff   0             39d   10.244.0.12   metacortex-lab-control-plane   <none>           <none>
```

## Chamada 2: `mcp__kubernetes__kubectl_get`

```json
{"resourceType": "deployments", "namespace": "orion-stg", "output": "yaml"}
```

Resposta do cluster:

```
apiVersion: v1
items:
- apiVersion: apps/v1
  kind: Deployment
  metadata:
    annotations:
      deployment.kubernetes.io/revision: "1"
      kubectl.kubernetes.io/last-applied-configuration: |
        {"apiVersion":"apps/v1","kind":"Deployment","metadata":{"annotations":{},"name":"orion-postgres","namespace":"orion-stg"},"spec":{"replicas":1,"selector":{"matchLabels":{"app":"orion-postgres"}},"template":{"metadata":{"labels":{"app":"orion-postgres"}},"spec":{"containers":[{"env":[{"name":"POSTGRES_DB","value":"ecommerce"},{"name":"POSTGRES_USER","value":"ecommerce"},{"name":"POSTGRES_PASSWORD","value":"Pg1234"}],"image":"postgres:16-alpine","name":"postgres","ports":[{"containerPort":5432}]}]}}}}
    creationTimestamp: "2026-09-17T18:01:54Z"
    generation: 1
    name: orion-postgres
    namespace: orion-stg
    resourceVersion: "852"
    uid: bdda64f7-93cd-4214-983a-324867dc3b7c
  spec:
    progressDeadlineSeconds: 600
    replicas: 1
    revisionHistoryLimit: 10
    selector:
      matchLabels:
        app: orion-postgres
    strategy:
      rollingUpdate:
        maxSurge: 25%
        maxUnavailable: 25%
      type: RollingUpdate
    template:
      metadata:
        labels:
          app: orion-postgres
      spec:
        containers:
        - env:
          - name: POSTGRES_DB
            value: ecommerce
          - name: POSTGRES_USER
            value: ecommerce
          - name: POSTGRES_PASSWORD
            value: Pg1234
          image: postgres:16-alpine
          imagePullPolicy: IfNotPresent
          name: postgres
          ports:
          - containerPort: 5432
… (109 linhas omitidas; resposta completa no log .jsonl)
```

## Chamada 3: `mcp__kubernetes__kubectl_get`

```json
{"resourceType": "events", "namespace": "orion-stg"}
```

Resposta do cluster:

```
{
  "events": [
    {
      "type": "Normal",
      "reason": "Pulling",
      "message": "Pulling image \"fabricioveronez/fake-shop:v1.14.2\"",
      "involvedObject": {
        "kind": "Pod",
        "name": "orion-web-67cd86ffd5-ls7zv",
        "namespace": "orion-stg"
      },
      "firstTimestamp": "2026-09-17T18:01:55Z",
      "lastTimestamp": "2026-09-30T09:21:01Z",
      "count": 457
    },
    {
      "type": "Warning",
      "reason": "Failed",
      "message": "Failed to pull image \"fabricioveronez/fake-shop:v1.14.2\": rpc error: code = NotFound desc = failed to pull and unpack image \"docker.io/fabricioveronez/fake-shop:v1.14.2\": failed to resolve reference \"docker.io/fabricioveronez/fake-shop:v1.14.2\": docker.io/fabricioveronez/fake-shop:v1.14.2: not found",
      "involvedObject": {
        "kind": "Pod",
        "name": "orion-web-67cd86ffd5-ls7zv",
        "namespace": "orion-stg"
      },
      "firstTimestamp": "2026-09-17T18:02:09Z",
      "lastTimestamp": "2026-09-30T10:35:02Z",
      "count": 420
    },
    {
      "type": "Normal",
      "reason": "Pulling",
      "message": "Pulling image \"fabricioveronez/fake-shop:v1.14.2\"",
      "involvedObject": {
        "kind": "Pod",
        "name": "orion-web-67cd86ffd5-54v6l",
        "namespace": "orion-stg"
      },
      "firstTimestamp": "2026-09-17T18:01:55Z",
      "lastTimestamp": "2026-09-30T13:45:27Z",
      "count": 462
    },
    {
      "type": "Warning",
      "reason": "Failed",
      "message": "Failed to pull image \"fabricioveronez/fake-shop:v1.14.2\": rpc error: code = NotFound desc = failed to pull and unpack image \"docker.io/fabricioveronez/fake-shop:v1.14.2\": failed to resolve reference \"docker.io/fabricioveronez/fake-shop:v1.14.2\": docker.io/fabricioveronez/fake-shop:v1.14.2: not found",
… (687 linhas omitidas; resposta completa no log .jsonl)
```

## Chamada 4: `mcp__kubernetes__kubectl_describe`

```json
{"resourceType": "pod", "name": "orion-web-67cd86ffd5-54v6l", "namespace": "orion-stg"}
```

Resposta do cluster:

```
Name:             orion-web-67cd86ffd5-54v6l
Namespace:        orion-stg
Priority:         0
Service Account:  default
Node:             metacortex-lab-control-plane/172.18.0.2
Start Time:       Thu, 17 Sep 2026 15:01:54 -0300
Labels:           app=orion-web
                  pod-template-hash=67cd86ffd5
Annotations:      <none>
Status:           Pending
IP:               10.244.0.13
IPs:
  IP:           10.244.0.13
Controlled By:  ReplicaSet/orion-web-67cd86ffd5
Containers:
  web:
    Container ID:   
    Image:          fabricioveronez/fake-shop:v1.14.2
    Image ID:       
    Port:           5000/TCP
    Host Port:      0/TCP
    State:          Waiting
      Reason:       ImagePullBackOff
    Ready:          False
    Restart Count:  0
    Environment:
      DB_HOST:                   orion-postgres
      DB_NAME:                   ecommerce
      DB_USER:                   ecommerce
      DB_PASSWORD:               Pg1234
      FLASK_APP:                 index.py
      PROMETHEUS_MULTIPROC_DIR:  /tmp/metrics
    Mounts:
      /var/run/secrets/kubernetes.io/serviceaccount from kube-api-access-54xxm (ro)
Conditions:
  Type                        Status
  PodReadyToStartContainers   True 
  Initialized                 True 
  Ready                       False 
  ContainersReady             False 
  PodScheduled                True 
Volumes:
  kube-api-access-54xxm:
    Type:                    Projected (a volume that contains injected data from multiple sources)
    TokenExpirationSeconds:  3607
… (26 linhas omitidas; resposta completa no log .jsonl)
```

## Diagnóstico do agente

**CAUSA:** O Deployment `orion-web` pede a imagem `fabricioveronez/fake-shop:v1.14.2`, e essa tag não existe no registry. Os 3 pods nunca subiram. A tag "nova" do release nunca chegou ao cluster.

**EVIDÊNCIA:**
- `deployment/orion-web` está na revisão 1 e `generation: 1`. O deploy nunca foi atualizado desde a criação, em 2026-09-17.
- `spec.template.spec.containers[web].image` é `fabricioveronez/fake-shop:v1.14.2`. A anotação `last-applied-configuration` mostra a mesma tag.
- Os 3 pods (`orion-web-67cd86ffd5-*`) estão em `0/1 ImagePullBackOff`, com 0 restarts, porque o container nunca iniciou.
- O evento de erro é: `failed to resolve reference "docker.io/fabricioveronez/fake-shop:v1.14.2": ... not found`.
- A condição `Progressing=False` tem o motivo `ProgressDeadlineExceeded`. `Available=False` tem o motivo `MinimumReplicasUnavailable`.

**CAMADA:** registry.

**Sobre "o pod nunca foi substituído":** não houve rollout que falhou. O objeto no cluster não tem nenhuma revisão além da primeira. Ou o `apply` com a tag nova não chegou neste cluster/namespace, ou foi aplicado em outro lugar. Não consigo ver isso daqui. Os pods atuais têm 39 dias e usam a ReplicaSet original, `67cd86ffd5`.

**O que está funcionando:**
- `orion-postgres` está `1/1 Running` e o deployment está Available. Teve 2 restarts, o último 15 minutos atrás, junto com o `SandboxChanged` do nó em 2026-10-27. Está de pé agora.
- Não é problema de credencial nem de rede, porque o erro é `not found` e não `unauthorized` ou `timeout`.
- Não olhei Service ou endpoints. Sem pod Ready, a loja fica sem backend de qualquer forma.

**AÇÃO SUGERIDA (não aplicada):**
1. Confirmar no Docker Hub se a tag `v1.14.2` existe. Ela pode ter sido anunciada mas nunca publicada, ou ter um erro de digitação.
2. Descobrir qual tag o Loom publicou de fato, e se o `apply` foi feito neste contexto/cluster. O manifesto versionado pode estar com a tag antiga.
3. Corrigir a tag para uma que exista e reaplicar. Depois disso, `kubectl rollout status deployment/orion-web -n orion-stg` deve mostrar a nova ReplicaSet substituindo as atuais.

**Pontos que não consegui confirmar:**
- Se `v1.14.2` é a tag anunciada no release ou uma tag antiga.
- Se `orion-stg` é o único cluster/contexto onde o deploy foi tentado.
