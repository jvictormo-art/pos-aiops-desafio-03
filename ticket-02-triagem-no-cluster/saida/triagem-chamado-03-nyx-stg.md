# Triagem — Chamado 03-nyx-stg

Saída real da skill `metacortex-triage`, executada pelo agente numa sessão limpa do Claude Code (`claude -p`, modelo `claude-sonnet-5-5`). O acesso ao cluster foi **só** pelo `mcp-server-kubernetes` em modo não destrutivo ([`.mcp.json`](../.mcp.json)); Bash ficou bloqueado na sessão, então não havia como rodar `kubectl` direto. Registro bruto: [`triagens/logs/chamado-03-nyx-stg.jsonl`](./triagens/logs/chamado-03-nyx-stg.jsonl).

| Item | Valor |
|---|---|
| Servidor MCP | `kubernetes` (connected) |
| Ferramentas do servidor disponíveis na sessão | 17 (nenhuma de escrita destrutiva: o modo não destrutivo remove `kubectl_delete`, `exec_in_pod` e afins) |
| Skills instaladas | metacortex-manifest, metacortex-triage |
| Turnos / duração / custo | 8 / 19 s / US$ 0.1017 |

**Skill carregada:** `metacortex-triage`

## Chamada 1: `mcp__kubernetes__kubectl_get`

```json
{"resourceType": "pods", "namespace": "nyx-stg", "output": "wide"}
```

Resposta do cluster:

```
NAME                           READY   STATUS    RESTARTS      AGE   IP            NODE                           NOMINATED NODE   READINESS GATES
nyx-api-7f4487c6ff-bl899       1/1     Running   8 (15m ago)   39d   10.244.0.2    metacortex-lab-control-plane   <none>           <none>
nyx-api-7f4487c6ff-dv9z8       1/1     Running   7 (15m ago)   39d   10.244.0.18   metacortex-lab-control-plane   <none>           <none>
nyx-postgres-f6fdc6dbf-224xn   1/1     Running   2 (16m ago)   39d   10.244.0.20   metacortex-lab-control-plane   <none>           <none>
```

## Chamada 2: `mcp__kubernetes__kubectl_get`

```json
{"resourceType": "services", "namespace": "nyx-stg", "output": "yaml"}
```

Resposta do cluster:

```
apiVersion: v1
items:
- apiVersion: v1
  kind: Service
  metadata:
    annotations:
      kubectl.kubernetes.io/last-applied-configuration: |
        {"apiVersion":"v1","kind":"Service","metadata":{"annotations":{},"name":"nyx-api","namespace":"nyx-stg"},"spec":{"ports":[{"port":80,"targetPort":8080}],"selector":{"app":"nyx-api"}}}
    creationTimestamp: "2026-09-17T18:01:55Z"
    name: nyx-api
    namespace: nyx-stg
    resourceVersion: "759"
    uid: 86048363-e4ff-43b5-a5a9-c34cd078f073
  spec:
    clusterIP: 10.96.94.79
    clusterIPs:
    - 10.96.94.79
    internalTrafficPolicy: Cluster
    ipFamilies:
    - IPv4
    ipFamilyPolicy: SingleStack
    ports:
    - port: 80
      protocol: TCP
      targetPort: 8080
    selector:
      app: nyx-api
    sessionAffinity: None
    type: ClusterIP
  status:
    loadBalancer: {}
- apiVersion: v1
  kind: Service
  metadata:
    annotations:
      kubectl.kubernetes.io/last-applied-configuration: |
        {"apiVersion":"v1","kind":"Service","metadata":{"annotations":{},"name":"nyx-postgres","namespace":"nyx-stg"},"spec":{"ports":[{"port":5432,"targetPort":5432}],"selector":{"app":"nyx-postgres"}}}
    creationTimestamp: "2026-09-17T18:01:55Z"
    name: nyx-postgres
    namespace: nyx-stg
    resourceVersion: "750"
    uid: 6e93efe2-c11a-47e5-90fa-b23420eb9ec6
  spec:
    clusterIP: 10.96.134.210
    clusterIPs:
… (18 linhas omitidas; resposta completa no log .jsonl)
```

## Chamada 3: `mcp__kubernetes__kubectl_get`

```json
{"resourceType": "endpoints", "namespace": "nyx-stg", "output": "yaml"}
```

Resposta do cluster:

```
apiVersion: v1
items:
- apiVersion: v1
  kind: Endpoints
  metadata:
    annotations:
      endpoints.kubernetes.io/last-change-trigger-time: "2026-09-17T18:01:55Z"
    creationTimestamp: "2026-09-17T18:01:55Z"
    labels:
      endpoints.kubernetes.io/managed-by: endpoint-controller
    name: nyx-api
    namespace: nyx-stg
    resourceVersion: "760"
    uid: 88f4d17f-368c-4f0b-a287-48f7b08bf074
- apiVersion: v1
  kind: Endpoints
  metadata:
    annotations:
      endpoints.kubernetes.io/last-change-trigger-time: "2026-09-17T18:01:55Z"
    creationTimestamp: "2026-09-17T18:01:55Z"
    labels:
      endpoints.kubernetes.io/managed-by: endpoint-controller
    name: nyx-postgres
    namespace: nyx-stg
    resourceVersion: "216799"
    uid: 86c61cb3-6d02-406a-995f-7da6c5dfbb8a
  subsets:
  - addresses:
    - ip: 10.244.0.20
      nodeName: metacortex-lab-control-plane
      targetRef:
        kind: Pod
        name: nyx-postgres-f6fdc6dbf-224xn
        namespace: nyx-stg
        uid: d882144d-2069-4b8c-9304-228c6caa0d9a
    ports:
    - port: 5432
      protocol: TCP
kind: List
metadata:
  resourceVersion: ""
```

## Chamada 4: `mcp__kubernetes__kubectl_get`

```json
{"resourceType": "pods", "namespace": "nyx-stg", "output": "yaml"}
```

Resposta do cluster:

```
apiVersion: v1
items:
- apiVersion: v1
  kind: Pod
  metadata:
    creationTimestamp: "2026-09-17T18:01:55Z"
    generateName: nyx-api-7f4487c6ff-
    generation: 1
    labels:
      app: nyxapi
      pod-template-hash: 7f4487c6ff
    name: nyx-api-7f4487c6ff-bl899
    namespace: nyx-stg
    ownerReferences:
    - apiVersion: apps/v1
      blockOwnerDeletion: true
      controller: true
      kind: ReplicaSet
      name: nyx-api-7f4487c6ff
      uid: 9493d129-a63d-4882-b3cf-e29ea60e3632
    resourceVersion: "216976"
    uid: 7dc0e034-bcc8-4df0-9ed3-49faadfcc340
  spec:
    containers:
    - env:
      - name: DB_HOST
        value: nyx-postgres
      - name: DB_DATABASE
        value: kubedevnews
      - name: DB_USERNAME
        value: kubedevnews
      - name: DB_PASSWORD
        value: Pg#123
      image: fabricioveronez/kube-news:v1
      imagePullPolicy: IfNotPresent
      livenessProbe:
        failureThreshold: 3
        httpGet:
          path: /health
          port: 8080
          scheme: HTTP
        initialDelaySeconds: 20
        periodSeconds: 10
        successThreshold: 1
        timeoutSeconds: 1
… (461 linhas omitidas; resposta completa no log .jsonl)
```

## Diagnóstico do agente

CAUSA: o selector do Service `nyx-api` não casa com os rótulos dos pods da API. O Service não tem nenhum endpoint, e é daí que vem o 503.

EVIDÊNCIA:
- `Service/nyx-api`, campo `spec.selector`, tem `app: nyx-api`.
- Os pods `nyx-api-7f4487c6ff-bl899` e `nyx-api-7f4487c6ff-dv9z8`, em `metadata.labels`, têm `app: nyxapi`, sem o hífen.
- `Endpoints/nyx-api` não tem `subsets`, ou seja, a lista de endereços está vazia.
- O objeto `Endpoints/nyx-postgres` aponta para `10.244.0.20:5432`. O Service do banco tem o selector correto (`app: nyx-postgres`).

CAMADA: roteamento

AÇÃO SUGERIDA: o time deve alinhar o rótulo e o selector. Isso fica a cargo do time, porque a triagem não aplica nada. Há duas opções.
- **Corrigir o rótulo (preferível):** mudar o rótulo `app` do template do Deployment `nyx-api` para `nyx-api`, que é o padrão do `nyx-postgres`. O `selector.matchLabels` do Deployment é imutável, então talvez seja preciso recriar o Deployment.
- **Corrigir o selector:** mudar `spec.selector` do Service para `app: nyxapi`.

O que está funcionando:
- **Postgres:** o pod do banco está `1/1 Ready` e tem endpoint.
- **Pods da API:** as duas réplicas estão `Running` e `1/1 Ready`, com as probes `/health` e `/ready` passando.
- **Imagem e agendamento:** não há problema de imagem nem de agendamento.

O que não investiguei, porque a causa já fechou:
- **Reinícios:** a API tem 7 e 8 reinícios, com último estado `exit code 1` às 16:53:40Z. O Postgres também reiniciou (saiu com 255 às 16:53:14Z). Os horários batem com uma reinicialização do nó, e a API provavelmente caiu por não alcançar o banco antes de ele voltar. Não li os logs, então isso é hipótese. Não explica o 503 e hoje a API está estável.
- **Ingress:** não olhei se existe um Ingress ou rota externa, nem se ele aponta para o Service certo. Se o 503 persistir depois de corrigir o selector, é o próximo ponto a checar.

Dois pontos fora do escopo do chamado:
- **Senha em claro:** `DB_PASSWORD` e `POSTGRES_PASSWORD` estão em texto puro nos manifests. Vale mover para um Secret.
- **Sem limites de recursos:** `resources: {}` deixa os pods como BestEffort.
