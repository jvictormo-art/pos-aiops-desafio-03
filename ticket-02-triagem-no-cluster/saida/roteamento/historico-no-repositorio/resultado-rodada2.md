# Matriz de roteamento — resultado `rodada2`

Skills instaladas nas sessões (evento `init`): metacortex-manifest, metacortex-triage.

| # | Frase | Esperado | Disparou (por execução) | Confere? |
|---|---|---|---|---|
| 1 | o pod do nyx-prod não sobe | triage | triage · triage · triage | sim |
| 2 | por que esse deployment está 0/3 | triage | triage · triage · triage | sim |
| 3 | o service do nyx-stg não tem endpoint | triage | triage · triage · triage | sim |
| 4 | revisa esse deployment antes de eu subir | manifest | nenhuma · manifest · manifest | **não** (2/3) |
| 5 | esse manifesto está no padrão da casa? | manifest | manifest · manifest · manifest | sim |
| 6 | cria um Deployment novo do zero pra mim | manifest | manifest · manifest · manifest | sim |
| 7 | esse manifesto não sobe no cluster | ambígua | triage · triage · nenhuma | ambígua — ver análise |
| 8 | o Service do nyx não está entregando tráfego | triage | triage · triage · triage | sim |
| 9 | o que é um DaemonSet? | nenhuma | nenhuma · nenhuma · nenhuma | sim |
| 10 | provisiona uma VM nova no Construct pro cliente orion | nenhuma | nenhuma · nenhuma · nenhuma | sim |

## Resposta de cada sessão

### 1. "o pod do nyx-prod não sobe"

- `logs/rodada2/01-1.jsonl` — skill: **metacortex-triage** — ferramentas: Skill → ToolSearch → k8s:kubectl_get → k8s:kubectl_describe
  > 
- `logs/rodada2/01-2.jsonl` — skill: **metacortex-triage** — ferramentas: Skill → ToolSearch → k8s:kubectl_get → k8s:kubectl_describe
  > 
- `logs/rodada2/01-3.jsonl` — skill: **metacortex-triage** — ferramentas: Skill → ToolSearch → k8s:kubectl_get → k8s:kubectl_describe
  > 

### 2. "por que esse deployment está 0/3"

- `logs/rodada2/02-1.jsonl` — skill: **metacortex-triage** — ferramentas: Skill
  > Preciso de duas informações antes de começar a triagem:  1. **Em qual namespace está o deployment?** 2. **Qual é o nome do deployment?** Se você não souber, eu listo os deployments do namespace.  Se você já tiver o sintoma, como pods em `Pending`, `CrashLoopBackOff`, erro de imagem ou 503 no serviço
- `logs/rodada2/02-2.jsonl` — skill: **metacortex-triage** — ferramentas: Skill
  > Qual é o namespace do deployment? Se você também souber o nome dele, me passe. Preciso do namespace para começar a triagem, e vou só ler o estado do cluster, sem aplicar nada.  Também me diga o que o cliente está vendo, por exemplo pods que não sobem, 503 ou deploy travado. Isso ajuda a escolher a c
- `logs/rodada2/02-3.jsonl` — skill: **metacortex-triage** — ferramentas: Skill
  > Qual é o namespace e o nome do deployment que está 0/3? A triagem precisa do namespace antes de começar, e o nome me poupa de listar tudo.  Se o chamado tem mais detalhes, me passe também. Por exemplo, se há queixa de tráfego (503 ou timeout) ou só os pods sem ficar prontos.  Vou só ler o estado do 

### 3. "o service do nyx-stg não tem endpoint"

- `logs/rodada2/03-1.jsonl` — skill: **metacortex-triage** — ferramentas: Skill → ToolSearch → k8s:kubectl_get → k8s:kubectl_get → k8s:kubectl_get → k8s:kubectl_get → k8s:kubectl_get
  > 
- `logs/rodada2/03-2.jsonl` — skill: **metacortex-triage** — ferramentas: Skill → ToolSearch → k8s:kubectl_get → k8s:kubectl_get → k8s:kubectl_get → k8s:kubectl_get → k8s:kubectl_get
  > 
- `logs/rodada2/03-3.jsonl` — skill: **metacortex-triage** — ferramentas: Skill → ToolSearch → k8s:kubectl_get → k8s:kubectl_get → k8s:kubectl_get → k8s:kubectl_get → k8s:kubectl_describe
  > 

### 4. "revisa esse deployment antes de eu subir"

- `logs/rodada2/04-1.jsonl` — skill: **nenhuma** — ferramentas: Glob → Grep
  > Achei mais de um deployment no repositório e não sei qual você vai subir:  - `ticket-01-padrao-de-manifests/saida/manifests-orion/deployment.yaml` (Orion) - `ticket-01-padrao-de-manifests/saida/nyx-barrado.yaml` (Nyx) - `ticket-04-dashboard-do-cluster/manifests-kube-news/deployment.yaml` (kube-news,
- `logs/rodada2/04-2.jsonl` — skill: **metacortex-manifest** — ferramentas: Glob → Skill → Read → Bash → Read → Read → Read → Read → Read
  > Revisei o `deployment.yaml` do kube-news em `ticket-04-dashboard-do-cluster/manifests-kube-news/`. Não consegui rodar o `trivy` nem o `check-manifest.py` porque o Bash está desativado nesta sessão. A revisão é manual e não teve a checagem mecânica.  Pelo que li, o deployment segue o padrão da casa e
- `logs/rodada2/04-3.jsonl` — skill: **metacortex-manifest** — ferramentas: Skill → Glob → Read → Read
  > Não sei qual deployment você vai subir. Há dois candidatos no repo, então revisei os dois só pela leitura dos YAMLs. Não consegui rodar `trivy` nem o `check-manifest.py`, porque nesta sessão não tenho shell. Também não abri o código dos workloads. Esta revisão não substitui essas ferramentas.  ## `t

### 5. "esse manifesto está no padrão da casa?"

- `logs/rodada2/05-1.jsonl` — skill: **metacortex-manifest** — ferramentas: Skill → Glob → Glob
  > Há vários manifestos no repositório e você não indicou qual. Não vou chutar.  Candidatos: - `ticket-01-padrao-de-manifests/saida/manifests-orion/` (5 arquivos) - `ticket-01-padrao-de-manifests/saida/nyx-barrado.yaml` - `ticket-02-triagem-no-cluster/manifests/` (chamados 01 a 03) - `ticket-04-dashboa
- `logs/rodada2/05-2.jsonl` — skill: **metacortex-manifest** — ferramentas: Skill → Glob
  > Você não indicou qual manifesto, e não consigo inferir pelo contexto. No ticket-01 há dois candidatos:  - `ticket-01-padrao-de-manifests/saida/nyx-barrado.yaml` - `ticket-01-padrao-de-manifests/saida/manifests-orion/` (secret, configmap, serviceaccount, service e deployment)  Qual deles você quer qu
- `logs/rodada2/05-3.jsonl` — skill: **metacortex-manifest** — ferramentas: Skill → Glob
  > Você não disse qual manifesto, e o repositório tem mais de um candidato. Em `ticket-01-padrao-de-manifests/saida/` há:  - `nyx-barrado.yaml`, um arquivo único que parece ser o manifesto a conferir - `manifests-orion/`, com `secret`, `configmap`, `serviceaccount`, `deployment` e `service`  Qual deles

### 6. "cria um Deployment novo do zero pra mim"

- `logs/rodada2/06-1.jsonl` — skill: **metacortex-manifest** — ferramentas: Skill
  > Pela skill, preciso de alguns dados antes de escrever o YAML, porque ela não deixa inferir porta, probes e segredos. Me diga:  1. **Cliente e componente**, que viram o nome `<cliente>-<componente>` e o namespace. 2. **Ambiente**: `dev`, `stg` ou `prod`. Isso define réplicas e strategy. 3. **Imagem e
- `logs/rodada2/06-2.jsonl` — skill: **metacortex-manifest** — ferramentas: Skill
  > Antes de escrever o YAML, preciso de alguns dados do workload. O padrão da Metacortex pede que eu não suponha nada sobre eles.  1. **Cliente e componente**: por exemplo `acme` e `billing`. Com eles o nome fica `acme-billing`. 2. **Ambiente**: `dev`, `stg` ou `prod`. Isso define o namespace (`<client
- `logs/rodada2/06-3.jsonl` — skill: **metacortex-manifest** — ferramentas: Skill
  > Antes de escrever o YAML, o padrão da casa pede decisões que não dá para inventar. Preciso destas respostas:  1. **Workload**: qual é o cliente e o componente? Isso define o nome (`<cliente>-<componente>`) e a imagem. Se houver um repositório do workload, me passe o caminho ou a URL para eu ler a po

### 7. "esse manifesto não sobe no cluster"

- `logs/rodada2/07-1.jsonl` — skill: **metacortex-triage** — ferramentas: Skill
  > Antes de investigar, preciso saber qual dos dois casos é o seu:  1. **O `apply` foi aceito, mas os pods não ficam de pé.** Os objetos existem no cluster e dá para investigar. Nesse caso me diga o **namespace** e o sintoma (por exemplo `CrashLoopBackOff`, `ImagePullBackOff`, `Pending` ou 503). 2. **O
- `logs/rodada2/07-2.jsonl` — skill: **metacortex-triage** — ferramentas: Skill
  > Antes de investigar, preciso saber qual é o caso. Pela skill de triagem, essa pergunta decide o caminho:  **O `kubectl apply` foi aceito e os pods não ficam de pé, ou o `apply` deu erro?**  - **O `apply` deu erro** (validação ou rejeição, nenhum objeto criado): não há nada no cluster para ler. Nesse
- `logs/rodada2/07-3.jsonl` — skill: **nenhuma** — ferramentas: Glob
  > Há vários manifests e não sei qual deles você quer dizer. Qual é?  - `ticket-01-padrao-de-manifests/saida/manifests-orion/` (secret, configmap, serviceaccount, service, deployment) - `ticket-01-padrao-de-manifests/saida/nyx-barrado.yaml` - `ticket-02-triagem-no-cluster/manifests/chamado-01-nyx-prod.

### 8. "o Service do nyx não está entregando tráfego"

- `logs/rodada2/08-1.jsonl` — skill: **metacortex-triage** — ferramentas: Skill → ToolSearch → k8s:kubectl_get → k8s:kubectl_get → k8s:kubectl_get → k8s:kubectl_get
  > 
- `logs/rodada2/08-2.jsonl` — skill: **metacortex-triage** — ferramentas: Skill → ToolSearch → k8s:kubectl_get → k8s:kubectl_get → k8s:kubectl_get
  > 
- `logs/rodada2/08-3.jsonl` — skill: **metacortex-triage** — ferramentas: Skill
  > Qual é o namespace do Service do nyx? O chamado só diz o sintoma ("não entrega tráfego"), e a triagem exige o namespace antes de começar.  Se "nyx" já for o namespace, me avise e informe o nome do Service. Se você não souber o namespace, posso listar os namespaces do cluster (só leitura) e procurar 

### 9. "o que é um DaemonSet?"

- `logs/rodada2/09-1.jsonl` — skill: **nenhuma** — ferramentas: (nenhuma ferramenta)
  > Um **DaemonSet** é um recurso do Kubernetes que garante que **uma cópia de um Pod rode em cada nó** do cluster (ou em um subconjunto de nós, se você filtrar).  **Comportamento** - Quando um nó novo entra no cluster, o Pod é criado nele automaticamente. - Quando um nó é removido, o Pod correspondente
- `logs/rodada2/09-2.jsonl` — skill: **nenhuma** — ferramentas: (nenhuma ferramenta)
  > Um **DaemonSet** é um recurso do Kubernetes que garante que **uma cópia de um pod rode em cada nó** do cluster (ou em um subconjunto deles, filtrado por `nodeSelector`, affinity ou tolerations).  **Comportamento** - Quando um novo nó entra no cluster, o pod é criado nele automaticamente. - Quando um
- `logs/rodada2/09-3.jsonl` — skill: **nenhuma** — ferramentas: (nenhuma ferramenta)
  > Um **DaemonSet** é um recurso do Kubernetes que garante que **um Pod rode em cada nó** do cluster (ou em um subconjunto deles, selecionado por `nodeSelector`, affinity ou tolerations).  **Comportamento principal** - Quando um novo nó entra no cluster, o Pod é criado nele automaticamente. - Quando um

### 10. "provisiona uma VM nova no Construct pro cliente orion"

- `logs/rodada2/10-1.jsonl` — skill: **nenhuma** — ferramentas: Grep → Grep
  > Não consigo provisionar essa VM. Não tenho ferramenta, API, CLI nem MCP do Construct. As únicas integrações que tenho são as do Kubernetes e as do sistema de arquivos local.  No repositório, o Construct só aparece como o componente que cria namespaces (no padrão de manifests do ticket-01) e como que
- `logs/rodada2/10-2.jsonl` — skill: **nenhuma** — ferramentas: Grep → Grep
  > Não consigo provisionar essa VM. Não tenho nenhuma ferramenta de acesso ao Construct (API, CLI ou MCP). As únicas integrações disponíveis aqui são o MCP do Kubernetes e o sistema de arquivos local, e o repositório não tem script nem documentação de provisionamento de VM.  Ele só cita o Construct com
- `logs/rodada2/10-3.jsonl` — skill: **nenhuma** — ferramentas: Grep → Grep
  > Não consigo provisionar essa VM. Não tenho ferramenta, API nem CLI do Construct. Também procurei no repositório e não achei script nem documentação de provisionamento de VM.  O Construct só aparece em `ticket-01-padrao-de-manifests/Padrao de Manifests da Metacortex.md`. Lá ele é o componente que cri

