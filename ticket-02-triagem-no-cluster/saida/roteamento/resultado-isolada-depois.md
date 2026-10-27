# Matriz de roteamento — resultado `isolada-depois`

Skills instaladas nas sessões (evento `init`): metacortex-manifest, metacortex-triage.

| # | Frase | Esperado | Disparou (por execução) | Confere? |
|---|---|---|---|---|
| 1 | o pod do nyx-prod não sobe | triage | triage · triage · triage | sim |
| 2 | por que esse deployment está 0/3 | triage | triage · triage · triage | sim |
| 3 | o service do nyx-stg não tem endpoint | triage | triage · triage · triage | sim |
| 4 | revisa esse deployment antes de eu subir | manifest | manifest · manifest · manifest | sim |
| 5 | esse manifesto está no padrão da casa? | manifest | manifest · manifest · manifest | sim |
| 6 | cria um Deployment novo do zero pra mim | manifest | manifest · manifest · manifest | sim |
| 7 | esse manifesto não sobe no cluster | ambígua | triage · triage · triage | ambígua — ver análise |
| 8 | o Service do nyx não está entregando tráfego | triage | triage · triage · triage | sim |
| 9 | o que é um DaemonSet? | nenhuma | nenhuma · nenhuma · nenhuma | sim |
| 10 | provisiona uma VM nova no Construct pro cliente orion | nenhuma | nenhuma · nenhuma · nenhuma | sim |

## Resposta de cada sessão

### 1. "o pod do nyx-prod não sobe"

- `logs/isolada-depois/01-1.jsonl` — skill: **metacortex-triage** — ferramentas: Skill → ToolSearch → k8s:kubectl_get → k8s:kubectl_describe
  > 
- `logs/isolada-depois/01-2.jsonl` — skill: **metacortex-triage** — ferramentas: Skill → ToolSearch → k8s:kubectl_get → k8s:kubectl_describe
  > 
- `logs/isolada-depois/01-3.jsonl` — skill: **metacortex-triage** — ferramentas: Skill → ToolSearch → k8s:kubectl_get → k8s:kubectl_describe
  > 

### 2. "por que esse deployment está 0/3"

- `logs/isolada-depois/02-1.jsonl` — skill: **metacortex-triage** — ferramentas: Skill
  > Para investigar, preciso saber em qual **namespace** está o deployment. Qual é o namespace, e qual é o nome do deployment, se houver mais de um?  Se você tiver o sintoma exato, como pods em `Pending`, `CrashLoopBackOff` ou `ImagePullBackOff`, ou o Service retornando 503, diga também. Isso acelera a 
- `logs/isolada-depois/02-2.jsonl` — skill: **metacortex-triage** — ferramentas: Skill
  > Para começar a triagem, preciso saber o namespace. Qual é o namespace e o nome do deployment que está 0/3?  Se você já souber o que aparece nos pods (STATUS como `Pending`, `ImagePullBackOff` ou `CrashLoopBackOff`), me diga também, mas não é obrigatório. Eu só vou ler o cluster (get, describe e logs
- `logs/isolada-depois/02-3.jsonl` — skill: **metacortex-triage** — ferramentas: Skill
  > Para começar a triagem, preciso saber o **namespace** e o **nome do deployment** que está em 0/3. Você pode me passar os dois?  Se o sintoma for diferente de "pods não ficam Ready", como 503 ou timeout, me diga também.  Outra pergunta: o `kubectl apply` foi aceito e os pods não ficam de pé, ou o `ap

### 3. "o service do nyx-stg não tem endpoint"

- `logs/isolada-depois/03-1.jsonl` — skill: **metacortex-triage** — ferramentas: Skill → ToolSearch → k8s:kubectl_get → k8s:kubectl_get → k8s:kubectl_get → k8s:kubectl_get → k8s:kubectl_get
  > 
- `logs/isolada-depois/03-2.jsonl` — skill: **metacortex-triage** — ferramentas: Skill → ToolSearch → k8s:kubectl_get → k8s:kubectl_get → k8s:kubectl_get
  > **CAUSA:** O seletor do Service `nyx-api` não casa com os rótulos dos pods da API. Por isso o Service não tem endpoint.  **EVIDÊNCIA:** - `Service/nyx-api` (nyx-stg): `spec.selector` é `app: nyx-api`. - Pods `nyx-api-7f4487c6ff-bl899` e `nyx-api-7f4487c6ff-dv9z8`: `metadata.labels` é `app: nyxapi`, 
- `logs/isolada-depois/03-3.jsonl` — skill: **metacortex-triage** — ferramentas: Skill → ToolSearch → k8s:kubectl_get → k8s:kubectl_get → k8s:kubectl_get → k8s:kubectl_get → k8s:kubectl_get
  > 

### 4. "revisa esse deployment antes de eu subir"

- `logs/isolada-depois/04-1.jsonl` — skill: **metacortex-manifest** — ferramentas: Skill → Glob → Glob → Read → Bash → Read → Read
  > 
- `logs/isolada-depois/04-2.jsonl` — skill: **metacortex-manifest** — ferramentas: Skill → Glob → Glob → Read → Read → ToolSearch
  > 
- `logs/isolada-depois/04-3.jsonl` — skill: **metacortex-manifest** — ferramentas: Skill → Glob → Glob → Read → Bash → Read
  > **Não suba ainda.** Revisei `ticket-01-padrao-de-manifests/saida/nyx-barrado.yaml` e ele falha em quase todo o padrão. Alguns achados quebram o deploy, não são só estilo.  **Limitações da revisão** - O Bash está desabilitado nesta sessão, então **não rodei `trivy` nem o `check-manifest.py`**. Confer

### 5. "esse manifesto está no padrão da casa?"

- `logs/isolada-depois/05-1.jsonl` — skill: **metacortex-manifest** — ferramentas: Skill → Glob → Glob → Glob → Read → Read → Bash
  > **Não, o manifesto `ticket-01-padrao-de-manifests/saida/nyx-barrado.yaml` não está no padrão da casa.** Não consegui rodar `trivy` nem `check-manifest.py` porque o Bash está desabilitado nesta sessão. A revisão abaixo é só leitura manual do YAML. Também não tenho o repositório do workload, então não
- `logs/isolada-depois/05-2.jsonl` — skill: **metacortex-manifest** — ferramentas: Skill → Glob → Glob → Read → Read → Bash
  > **Não, o manifesto não está no padrão da casa.** Ele quebra a maioria das regras.  Não consegui rodar `trivy` nem `check-manifest.py` porque o Bash está desabilitado nesta sessão. Também não há o repositório do workload aqui. A revisão abaixo é só leitura do YAML em `ticket-01-padrao-de-manifests/sa
- `logs/isolada-depois/05-3.jsonl` — skill: **metacortex-manifest** — ferramentas: Skill → Glob → Glob → Read → Bash → Read → Grep
  > 

### 6. "cria um Deployment novo do zero pra mim"

- `logs/isolada-depois/06-1.jsonl` — skill: **metacortex-manifest** — ferramentas: Skill → Glob → Glob → Read
  > Não dá pra escrever esse Deployment sem inventar dados, e o padrão da Metacortex pede que eu leia o projeto antes de escrever, sem suposições. Não achei aqui nenhum repositório de workload. Só encontrei `ticket-01-padrao-de-manifests/saida/nyx-barrado.yaml`, que é um manifest existente e fora do pad
- `logs/isolada-depois/06-2.jsonl` — skill: **metacortex-manifest** — ferramentas: Skill → Glob → Glob
  > Pra escrever esse Deployment do jeito certo, preciso de algumas informações. O padrão da Metacortex exige que eu leia o projeto em vez de supor.  1. **Qual workload é esse?** Preciso do repositório ou do caminho do código, e do nome do cliente e do componente. Com isso eu leio:    - a porta que o pr
- `logs/isolada-depois/06-3.jsonl` — skill: **metacortex-manifest** — ferramentas: Skill → Glob → Glob → Glob → Read
  > Não tenho o que preciso pra escrever esse Deployment sem chutar. O skill de manifests da Metacortex exige ler o projeto do workload antes, e aqui não há código nem Dockerfile. O único arquivo no repo é `ticket-01-padrao-de-manifests/saida/nyx-barrado.yaml`, que é um manifest antigo do Nyx que viola 

### 7. "esse manifesto não sobe no cluster"

- `logs/isolada-depois/07-1.jsonl` — skill: **metacortex-triage** — ferramentas: Skill
  > Antes de investigar, preciso saber qual é o caso. A triagem só lê o que já está no cluster.  **O `apply` foi aceito e os pods não ficam de pé, ou o `apply` deu erro?**  - **Deu erro e nenhum objeto foi criado.** Não há nada no cluster para investigar. Nesse caso, o caminho é conferir o YAML com a sk
- `logs/isolada-depois/07-2.jsonl` — skill: **metacortex-triage** — ferramentas: Skill
  > Antes de investigar, preciso saber qual dos dois casos é o seu:  1. **O `apply` foi aceito, mas os pods não ficam de pé?** Nesse caso eu faço a triagem no cluster. Para isso preciso do **namespace** e do sintoma, por exemplo `Pending`, `CrashLoopBackOff`, `ImagePullBackOff` ou 503. 2. **O `apply` de
- `logs/isolada-depois/07-3.jsonl` — skill: **metacortex-triage** — ferramentas: Skill
  > Antes de investigar, preciso saber qual é o caso, porque a abordagem muda:  **O `kubectl apply` foi aceito e os pods não ficam de pé, ou o `apply` deu erro?**  - **O `apply` deu erro (rejeitado, nenhum objeto criado):** não há nada no cluster para investigar. Posso conferir o YAML contra o padrão da

### 8. "o Service do nyx não está entregando tráfego"

- `logs/isolada-depois/08-1.jsonl` — skill: **metacortex-triage** — ferramentas: Skill
  > Para começar a triagem, preciso saber em qual namespace o nyx está. Você disse "o Service do nyx", mas não deu o namespace, então não sei se `nyx` é o nome do namespace ou só o nome do Service.  Também ajuda saber o sintoma exato: 503, timeout ou "sem endpoint".  Com o namespace, começo pelo estado 
- `logs/isolada-depois/08-2.jsonl` — skill: **metacortex-triage** — ferramentas: Skill → ToolSearch → k8s:kubectl_get → k8s:kubectl_get → k8s:kubectl_get
  > 
- `logs/isolada-depois/08-3.jsonl` — skill: **metacortex-triage** — ferramentas: Skill → ToolSearch → k8s:kubectl_get
  > Existem três namespaces do nyx: `nyx-dev`, `nyx-stg` e `nyx-prod`. Em qual deles está o problema? Não vou chutar, porque a triagem depende do ambiente certo.  Se souber, me diga também o nome do Service e o sintoma que aparece (503, timeout, conexão recusada). Isso ajuda a ir direto à camada de rote

### 9. "o que é um DaemonSet?"

- `logs/isolada-depois/09-1.jsonl` — skill: **nenhuma** — ferramentas: (nenhuma ferramenta)
  > Um **DaemonSet** é um tipo de workload do Kubernetes que garante que **uma cópia de um Pod rode em cada nó** do cluster (ou em um subconjunto deles).  **Como funciona** - Quando um novo nó entra no cluster, o DaemonSet cria automaticamente um Pod nele. - Quando um nó é removido, o Pod correspondente
- `logs/isolada-depois/09-2.jsonl` — skill: **nenhuma** — ferramentas: (nenhuma ferramenta)
  > Um **DaemonSet** é um tipo de workload do Kubernetes que garante que **uma cópia de um Pod rode em cada nó** do cluster (ou em um subconjunto deles).  ## Como funciona  - Quando um novo nó entra no cluster, o DaemonSet cria automaticamente um Pod nele. - Quando um nó é removido, o Pod correspondente
- `logs/isolada-depois/09-3.jsonl` — skill: **nenhuma** — ferramentas: (nenhuma ferramenta)
  > Um **DaemonSet** é um tipo de recurso do Kubernetes que garante que **uma cópia de um Pod rode em cada node** do cluster (ou em um subconjunto deles).  ## Como funciona - Quando um node novo entra no cluster, o DaemonSet automaticamente cria um Pod nele. - Quando um node é removido, o Pod correspond

### 10. "provisiona uma VM nova no Construct pro cliente orion"

- `logs/isolada-depois/10-1.jsonl` — skill: **nenhuma** — ferramentas: Grep → Glob
  > Não consegui provisionar a VM. Não achei nada sobre o Construct neste ambiente:  - O repositório não menciona "construct" em nenhum arquivo. - Não tenho ferramenta nem integração para o Construct. As únicas coisas de infraestrutura disponíveis são as ferramentas de Kubernetes (kubectl/helm) e duas s
- `logs/isolada-depois/10-2.jsonl` — skill: **nenhuma** — ferramentas: Grep → Glob
  > Não consegui provisionar a VM. Não achei nada sobre o Construct aqui.  - O repositório não menciona "Construct" em nenhum arquivo. - Não tenho ferramenta de provisionamento de VM nem acesso a uma API ou CLI do Construct. - As únicas ferramentas de infraestrutura que tenho são as do Kubernetes e as s
- `logs/isolada-depois/10-3.jsonl` — skill: **nenhuma** — ferramentas: Grep → Glob
  > Não consigo provisionar essa VM. Não achei nada sobre "Construct" no repositório, e as únicas ferramentas de infraestrutura que tenho são as do Kubernetes. Não tenho acesso a uma API, CLI ou MCP de VMs.  Para eu continuar, preciso saber:  1. **O que é o Construct?** É uma plataforma própria, um clus

