# Matriz de roteamento — resultado `rodada1`

Skills instaladas nas sessões (evento `init`): metacortex-manifest, metacortex-triage.

| # | Frase | Esperado | Disparou (por execução) | Confere? |
|---|---|---|---|---|
| 1 | o pod do nyx-prod não sobe | triage | triage · triage · triage | sim |
| 2 | por que esse deployment está 0/3 | triage | triage · triage · triage | sim |
| 3 | o service do nyx-stg não tem endpoint | triage | triage · triage · triage | sim |
| 4 | revisa esse deployment antes de eu subir | manifest | manifest · manifest · manifest | sim |
| 5 | esse manifesto está no padrão da casa? | manifest | nenhuma · manifest · manifest | **não** (2/3) |
| 6 | cria um Deployment novo do zero pra mim | manifest | manifest · manifest · manifest | sim |
| 7 | esse manifesto não sobe no cluster | ambígua | triage · triage · triage | ambígua — ver análise |
| 8 | o Service do nyx não está entregando tráfego | triage | triage · triage · triage | sim |
| 9 | o que é um DaemonSet? | nenhuma | nenhuma · nenhuma · nenhuma | sim |
| 10 | provisiona uma VM nova no Construct pro cliente orion | nenhuma | nenhuma · nenhuma · nenhuma | sim |

## Resposta de cada sessão

### 1. "o pod do nyx-prod não sobe"

- `logs/rodada1/01-1.jsonl` — skill: **metacortex-triage** — ferramentas: Skill → ToolSearch → k8s:kubectl_get → k8s:kubectl_describe
  > 
- `logs/rodada1/01-2.jsonl` — skill: **metacortex-triage** — ferramentas: Skill → ToolSearch → k8s:kubectl_get → k8s:kubectl_describe
  > 
- `logs/rodada1/01-3.jsonl` — skill: **metacortex-triage** — ferramentas: Skill → ToolSearch → k8s:kubectl_get → k8s:kubectl_describe
  > 

### 2. "por que esse deployment está 0/3"

- `logs/rodada1/02-1.jsonl` — skill: **metacortex-triage** — ferramentas: Skill
  > Preciso do namespace antes de começar. Qual é o namespace e o nome do deployment que mostra 0/3?  Se você também tiver o sintoma que o cliente relatou (por exemplo "serviço retorna 503" ou "pods não sobem"), me passe junto. Com isso eu sigo direto para a camada certa da triagem. Vou só ler o cluster
- `logs/rodada1/02-2.jsonl` — skill: **metacortex-triage** — ferramentas: Skill
  > Qual é o namespace e o nome do deployment? Preciso do namespace para começar a triagem, e o nome do deployment ajuda a filtrar os pods.  Se você tiver mais sintomas, como o serviço retornar 503 ou o deploy ter travado depois de um rollout, me passe também. Eles me ajudam a escolher a camada certa pa
- `logs/rodada1/02-3.jsonl` — skill: **metacortex-triage** — ferramentas: Skill
  > Qual é o namespace do deployment? Se você souber, me diga também o nome dele e o sintoma, por exemplo se o serviço retorna 503 ou se os pods nem sobem.  Com o namespace eu começo pelo estado dos pods, só com leitura e sem aplicar nada no cluster.

### 3. "o service do nyx-stg não tem endpoint"

- `logs/rodada1/03-1.jsonl` — skill: **metacortex-triage** — ferramentas: Skill → ToolSearch → k8s:kubectl_get → k8s:kubectl_get → k8s:kubectl_get → k8s:kubectl_get
  > 
- `logs/rodada1/03-2.jsonl` — skill: **metacortex-triage** — ferramentas: Skill → ToolSearch → k8s:kubectl_get → k8s:kubectl_get → k8s:kubectl_get → k8s:kubectl_get → k8s:kubectl_get
  > 
- `logs/rodada1/03-3.jsonl` — skill: **metacortex-triage** — ferramentas: Skill → ToolSearch → k8s:kubectl_get → k8s:kubectl_get → k8s:kubectl_get → k8s:kubectl_get → k8s:kubectl_get
  > 

### 4. "revisa esse deployment antes de eu subir"

- `logs/rodada1/04-1.jsonl` — skill: **metacortex-manifest** — ferramentas: Glob → Skill
  > Tem mais de um deployment no repositório e não sei qual você vai subir:  - `ticket-01-padrao-de-manifests/saida/manifests-orion/deployment.yaml` (orion) - `ticket-04-dashboard-do-cluster/manifests-kube-news/deployment.yaml` (kube-news) - `ticket-02-triagem-no-cluster/manifests/chamado-0*.yaml` (nyx 
- `logs/rodada1/04-2.jsonl` — skill: **metacortex-manifest** — ferramentas: Glob → Skill → Read → Read → Glob
  > Não sei qual dos dois você vai subir, então revisei os dois só pela leitura dos YAMLs. Não tenho shell nesta sessão, então **não rodei `trivy` nem o `check-manifest.py`**. Também não abri o código dos workloads, então as probes, portas e variáveis de ambiente abaixo não estão confirmadas contra o có
- `logs/rodada1/04-3.jsonl` — skill: **metacortex-manifest** — ferramentas: Skill → Glob
  > Não sei qual deployment você quer dizer. Há vários no repositório:  - `ticket-01-padrao-de-manifests/saida/manifests-orion/deployment.yaml` - `ticket-04-dashboard-do-cluster/manifests-kube-news/deployment.yaml` - `ticket-02-triagem-no-cluster/manifests/chamado-01-nyx-prod.yaml`, `chamado-02-orion-st

### 5. "esse manifesto está no padrão da casa?"

- `logs/rodada1/05-1.jsonl` — skill: **nenhuma** — ferramentas: Glob
  > Encontrei vários manifestos e não sei de qual você fala. Qual deles você quer que eu confira?  - `ticket-01-padrao-de-manifests/saida/manifests-orion/` (deployment, service, configmap, secret e serviceaccount) - `ticket-01-padrao-de-manifests/saida/nyx-barrado.yaml` - outro arquivo, ou um YAML que v
- `logs/rodada1/05-2.jsonl` — skill: **metacortex-manifest** — ferramentas: Skill → Glob → Bash → Read → Read
  > 
- `logs/rodada1/05-3.jsonl` — skill: **metacortex-manifest** — ferramentas: Skill → Glob
  > Há vários manifestos no repositório e você não disse qual. Não quero validar o errado.  Qual deles você quer conferir? Os candidatos são:  - `ticket-01-padrao-de-manifests/saida/manifests-orion/` (secret, configmap, serviceaccount, service e deployment) - `ticket-01-padrao-de-manifests/saida/nyx-bar

### 6. "cria um Deployment novo do zero pra mim"

- `logs/rodada1/06-1.jsonl` — skill: **metacortex-manifest** — ferramentas: Skill
  > Antes de escrever o YAML, o padrão da Metacortex exige umas decisões que eu não devo chutar. Preciso destas informações:  1. **Workload:** qual é o repositório ou componente? Preciso dele para ler a porta, os endpoints de saúde, as variáveis de ambiente e se o entrypoint roda migração. 2. **Cliente 
- `logs/rodada1/06-2.jsonl` — skill: **metacortex-manifest** — ferramentas: Skill
  > Antes de escrever o YAML, o padrão da Metacortex pede decisões que eu não consigo inferir do que você mandou. Preciso destas respostas:  1. **Workload**: qual é o componente e o cliente? Se houver repositório, me passe o caminho ou a URL para eu ler a porta, os endpoints de saúde e o `entrypoint`. 2
- `logs/rodada1/06-3.jsonl` — skill: **metacortex-manifest** — ferramentas: Skill
  > Antes de escrever o YAML, preciso de alguns dados. O padrão da Metacortex exige que eu leia o workload em vez de supor:  1. **Cliente, componente e ambiente**: define o namespace `<cliente>-<env>` e o nome `<cliente>-<componente>`. O ambiente também decide as réplicas (prod precisa de 2 ou mais). 2.

### 7. "esse manifesto não sobe no cluster"

- `logs/rodada1/07-1.jsonl` — skill: **metacortex-triage** — ferramentas: Glob → Skill
  > Não sei de qual manifesto você está falando, e a triagem precisa do namespace, então preciso de dois dados:  1. **Qual manifesto?** O repositório tem vários candidatos:    - `ticket-02-triagem-no-cluster/manifests/chamado-01-nyx-prod.yaml`    - `ticket-02-triagem-no-cluster/manifests/chamado-02-orio
- `logs/rodada1/07-2.jsonl` — skill: **metacortex-triage** — ferramentas: Skill
  > Falta informação para começar a triagem. Preciso de duas coisas:  1. **Namespace** onde você aplicou o manifest. 2. **Qual manifest** você quer dizer. Não vi nenhum arquivo anexado ou aberto. Se for um arquivo do repositório, me passe o caminho.  Também ajuda saber o que você vê: o `kubectl apply` d
- `logs/rodada1/07-3.jsonl` — skill: **metacortex-triage** — ferramentas: Glob → Skill
  > Preciso de duas informações antes de investigar:  1. **Qual manifesto?** Há vários no repositório, por exemplo:    - `ticket-02-triagem-no-cluster/manifests/chamado-01-nyx-prod.yaml`, `chamado-02-orion-stg.yaml` e `chamado-03-nyx-stg.yaml`    - `ticket-01-padrao-de-manifests/saida/manifests-orion/` 

### 8. "o Service do nyx não está entregando tráfego"

- `logs/rodada1/08-1.jsonl` — skill: **metacortex-triage** — ferramentas: Skill → ToolSearch → k8s:kubectl_get → k8s:kubectl_get → k8s:kubectl_get → k8s:kubectl_get
  > 
- `logs/rodada1/08-2.jsonl` — skill: **metacortex-triage** — ferramentas: Skill → ToolSearch → k8s:kubectl_get → k8s:kubectl_get → k8s:kubectl_get
  > 
- `logs/rodada1/08-3.jsonl` — skill: **metacortex-triage** — ferramentas: Skill → ToolSearch → k8s:kubectl_get → k8s:kubectl_get → k8s:kubectl_get
  > 

### 9. "o que é um DaemonSet?"

- `logs/rodada1/09-1.jsonl` — skill: **nenhuma** — ferramentas: (nenhuma ferramenta)
  > Um **DaemonSet** é um recurso do Kubernetes que garante que **um Pod rode em cada nó** do cluster (ou em um subconjunto deles).  **Como funciona** - Quando um nó novo entra no cluster, o DaemonSet cria um Pod nele automaticamente. - Quando um nó é removido, o Pod dele é descartado. - Ao apagar o Dae
- `logs/rodada1/09-2.jsonl` — skill: **nenhuma** — ferramentas: (nenhuma ferramenta)
  > Um **DaemonSet** é um recurso do Kubernetes que garante que **uma cópia de um Pod rode em cada nó** do cluster (ou em um subconjunto de nós, selecionado por `nodeSelector`, afinidade ou tolerations).  **Comportamento principal** - Quando um novo nó entra no cluster, o Pod do DaemonSet é criado nele 
- `logs/rodada1/09-3.jsonl` — skill: **nenhuma** — ferramentas: (nenhuma ferramenta)
  > Um **DaemonSet** é um recurso do Kubernetes que garante que **uma cópia de um Pod rode em cada nó** do cluster (ou em um subconjunto deles, selecionado por `nodeSelector`, afinidade ou tolerations).  **Comportamento** - Quando um nó novo entra no cluster, o DaemonSet cria automaticamente o Pod nele.

### 10. "provisiona uma VM nova no Construct pro cliente orion"

- `logs/rodada1/10-1.jsonl` — skill: **nenhuma** — ferramentas: Grep → Grep
  > Não consigo provisionar essa VM. Não tenho ferramenta, API nem CLI do Construct. Procurei no repositório e não achei nenhum script ou documentação de provisionamento de VM. O Construct só aparece como o componente que cria namespaces, no padrão de manifests.  A frase "provisiona uma VM nova no Const
- `logs/rodada1/10-2.jsonl` — skill: **nenhuma** — ferramentas: Grep → Grep → Grep
  > Não consigo provisionar essa VM. Esse pedido é um dos casos de teste da matriz de roteamento do ticket 02 (`ticket-02-triagem-no-cluster/saida/matriz-roteamento.md:20`), em que o resultado esperado é "nenhuma skill". Ele está fora do escopo de `metacortex-manifest` e `metacortex-triage`.  - **O Cons
- `logs/rodada1/10-3.jsonl` — skill: **nenhuma** — ferramentas: Grep → Grep → Grep
  > Não consigo provisionar essa VM. Não tenho nenhuma ferramenta de acesso ao Construct (API, CLI ou MCP). As únicas integrações disponíveis são as do Kubernetes e do sistema de arquivos local.  O próprio repositório trata esse pedido como fora de escopo. Ele aparece como um caso de teste em `ticket-02

