# Matriz de roteamento — resultado `isolada-antes`

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

- `logs/isolada-antes/01-1.jsonl` — skill: **metacortex-triage** — ferramentas: Skill → ToolSearch → k8s:kubectl_get → k8s:kubectl_describe
  > 
- `logs/isolada-antes/01-2.jsonl` — skill: **metacortex-triage** — ferramentas: Skill → ToolSearch → k8s:kubectl_get → k8s:kubectl_describe
  > 
- `logs/isolada-antes/01-3.jsonl` — skill: **metacortex-triage** — ferramentas: Skill → ToolSearch → k8s:kubectl_get → k8s:kubectl_describe
  > 

### 2. "por que esse deployment está 0/3"

- `logs/isolada-antes/02-1.jsonl` — skill: **metacortex-triage** — ferramentas: Skill
  > Qual é o namespace do deployment? Se souber, me diga também o nome do deployment e o que o cliente está vendo, por exemplo pods que não sobem ou 503.  Sem o namespace eu não consigo começar a triagem. Com ele, eu só leio o estado do cluster (pods, eventos, describe e logs) e não aplico nenhuma corre
- `logs/isolada-antes/02-2.jsonl` — skill: **metacortex-triage** — ferramentas: Skill
  > Qual é o namespace do deployment (e o nome dele, se souber)? Preciso disso para começar a triagem.  Se você tiver o sintoma que o cliente relatou, como "pods não sobem" ou "serviço retorna 503", me passe também. Isso me diz por onde começar.
- `logs/isolada-antes/02-3.jsonl` — skill: **metacortex-triage** — ferramentas: Skill
  > Em qual namespace está esse deployment? Se souber o nome do deployment, me passe também. Preciso do namespace para começar a triagem.  Vou só ler o estado do cluster (pods, eventos, logs). Não aplico nenhuma correção.

### 3. "o service do nyx-stg não tem endpoint"

- `logs/isolada-antes/03-1.jsonl` — skill: **metacortex-triage** — ferramentas: Skill → ToolSearch → k8s:kubectl_get → k8s:kubectl_get → k8s:kubectl_get → k8s:kubectl_get → k8s:kubectl_get
  > 
- `logs/isolada-antes/03-2.jsonl` — skill: **metacortex-triage** — ferramentas: Skill → ToolSearch → k8s:kubectl_get → k8s:kubectl_get → k8s:kubectl_get → k8s:kubectl_get
  > 
- `logs/isolada-antes/03-3.jsonl` — skill: **metacortex-triage** — ferramentas: Skill → ToolSearch → k8s:kubectl_get → k8s:kubectl_get → k8s:kubectl_get → k8s:kubectl_get → k8s:kubectl_get
  > 

### 4. "revisa esse deployment antes de eu subir"

- `logs/isolada-antes/04-1.jsonl` — skill: **metacortex-manifest** — ferramentas: Skill → Glob → Glob → Read → Read → Bash
  > Não consegui rodar o `trivy` nem o `check-manifest.py`, porque o Bash está desabilitado nesta sessão. Também não tenho o repositório do workload `nyx/api`. Por isso fiz a revisão só lendo o YAML (`nyx-barrado.yaml`) contra `regras-buckets.md`. Não valide a conclusão como se as ferramentas tivessem p
- `logs/isolada-antes/04-2.jsonl` — skill: **metacortex-manifest** — ferramentas: Skill → Glob → Glob → Read → Read → Bash
  > Não consegui rodar o `trivy` nem o `check-manifest.py`, porque o Bash está desabilitado nesta sessão. Esta revisão é só leitura manual de `ticket-01-padrao-de-manifests/saida/nyx-barrado.yaml` contra `regras-buckets.md`. O repositório do workload também não está aqui. Por isso não confirmei a porta 
- `logs/isolada-antes/04-3.jsonl` — skill: **metacortex-manifest** — ferramentas: Skill → Glob → Glob → Read → Read → Bash
  > Não consegui rodar o `trivy` nem o `check-manifest.py`, porque o Bash está desabilitado nesta sessão. Fiz a revisão manual do `nyx-barrado.yaml` contra as regras de `regras-buckets.md`. Também não tenho o repositório do workload, então a regra 2.2 (probes apontando para endpoints reais) ficou sem ve

### 5. "esse manifesto está no padrão da casa?"

- `logs/isolada-antes/05-1.jsonl` — skill: **metacortex-manifest** — ferramentas: Skill → Glob → Read → Glob → Glob → Read → Read
  > **Não, o `nyx-barrado.yaml` não está no padrão da casa.** Ele falha em quase todas as regras.  Não tenho shell nesta sessão, então não rodei `trivy` nem `check-manifest.py`. Li o manifesto contra o script e a tabela `regras-buckets.md` e conferi cada regra à mão. Os achados de Trivy abaixo vêm dessa
- `logs/isolada-antes/05-2.jsonl` — skill: **metacortex-manifest** — ferramentas: Skill → Glob → Read → Read → Bash
  > 
- `logs/isolada-antes/05-3.jsonl` — skill: **metacortex-manifest** — ferramentas: Skill → Glob → Glob → Read → Read → Bash
  > **Não, o manifesto não está no padrão.** O arquivo é `ticket-01-padrao-de-manifests/saida/nyx-barrado.yaml`. Não consegui rodar `trivy` nem `check-manifest.py`, porque o Bash está desativado nesta sessão. Fiz a conferência lendo o YAML contra `regras-buckets.md`. Também não abri o repositório do wor

### 6. "cria um Deployment novo do zero pra mim"

- `logs/isolada-antes/06-1.jsonl` — skill: **metacortex-manifest** — ferramentas: Skill → Glob → Glob → Read
  > Não achei o repositório do workload aqui. O único arquivo é `ticket-01-padrao-de-manifests/saida/nyx-barrado.yaml`, um manifest antigo (`NyxAPI`, `:latest`, senha em `value`, sem probes) que parece ter sido reprovado. A skill pede para ler o projeto antes de escrever e não supor nada, então preciso 
- `logs/isolada-antes/06-2.jsonl` — skill: **metacortex-manifest** — ferramentas: Skill → Glob → Read → Read
  > Antes de escrever o YAML, preciso de alguns dados. O padrão da Metacortex pede que eu não suponha nada sobre o workload.  1. **Qual workload?** Informe cliente e componente (por exemplo `nyx` / `api`), e o repositório, se houver, para eu ler porta, endpoints de saúde e entrypoint. 2. **Ambiente:** `
- `logs/isolada-antes/06-3.jsonl` — skill: **metacortex-manifest** — ferramentas: Skill → Glob → Read
  > Não dá pra escrever o Deployment sem inventar valores, e o padrão da Metacortex pede que eu leia o projeto do workload antes. Achei só o `ticket-01-padrao-de-manifests/saida/nyx-barrado.yaml`, que é um manifest existente com problemas e não o workload novo. Não sei se é dele que você quer partir.  P

### 7. "esse manifesto não sobe no cluster"

- `logs/isolada-antes/07-1.jsonl` — skill: **metacortex-triage** — ferramentas: Skill
  > Qual é o namespace do workload? A triagem começa pelo estado dos pods nesse namespace, então preciso dele antes de rodar qualquer coisa.  Se puder, diga também o sintoma que você vê, por exemplo pods que não sobem, 503 ou deploy travado. Isso ajuda a escolher a camada certa para investigar.  Esta tr
- `logs/isolada-antes/07-2.jsonl` — skill: **metacortex-triage** — ferramentas: Skill → Glob → Read → ToolSearch → k8s:kubectl_get → k8s:kubectl_get
  > 
- `logs/isolada-antes/07-3.jsonl` — skill: **metacortex-triage** — ferramentas: Skill → Glob → Read → ToolSearch → k8s:kubectl_get → k8s:kubectl_describe
  > 

### 8. "o Service do nyx não está entregando tráfego"

- `logs/isolada-antes/08-1.jsonl` — skill: **metacortex-triage** — ferramentas: Skill → ToolSearch → k8s:kubectl_get → k8s:kubectl_get → k8s:kubectl_get → k8s:kubectl_get
  > 
- `logs/isolada-antes/08-2.jsonl` — skill: **metacortex-triage** — ferramentas: Skill → ToolSearch → k8s:kubectl_get → k8s:kubectl_get
  > 
- `logs/isolada-antes/08-3.jsonl` — skill: **metacortex-triage** — ferramentas: Skill → ToolSearch → k8s:kubectl_get → k8s:kubectl_get → k8s:kubectl_get → k8s:kubectl_get
  > 

### 9. "o que é um DaemonSet?"

- `logs/isolada-antes/09-1.jsonl` — skill: **nenhuma** — ferramentas: (nenhuma ferramenta)
  > Um **DaemonSet** é um recurso do Kubernetes que garante que **uma cópia de um Pod rode em cada nó** do cluster (ou em um subconjunto deles).  ## Como funciona  - Quando um novo nó entra no cluster, o DaemonSet cria automaticamente um Pod nele. - Quando um nó é removido, o Pod correspondente é descar
- `logs/isolada-antes/09-2.jsonl` — skill: **nenhuma** — ferramentas: (nenhuma ferramenta)
  > Um **DaemonSet** é um objeto do Kubernetes que garante que **uma cópia de um Pod rode em cada nó** do cluster (ou em um subconjunto deles).  ## Como funciona - Quando um novo nó entra no cluster, o DaemonSet cria automaticamente o Pod nele. - Quando um nó é removido, o Pod correspondente é descartad
- `logs/isolada-antes/09-3.jsonl` — skill: **nenhuma** — ferramentas: (nenhuma ferramenta)
  > Um **DaemonSet** é um recurso do Kubernetes que garante que **uma cópia de um Pod rode em cada nó** do cluster (ou em um subconjunto deles, filtrado por `nodeSelector`, affinity ou tolerations).  **Comportamento principal** - Quando um novo nó entra no cluster, o Pod é criado nele automaticamente. -

### 10. "provisiona uma VM nova no Construct pro cliente orion"

- `logs/isolada-antes/10-1.jsonl` — skill: **nenhuma** — ferramentas: Grep → Glob
  > Não consigo provisionar essa VM. Não tenho nenhuma ferramenta nem integração com o Construct nesta sessão, e também não achei nada sobre ele no workspace. Não existe referência a "construct" nos arquivos, e as únicas skills do projeto são `metacortex-manifest` e `metacortex-triage`, que cuidam de ma
- `logs/isolada-antes/10-2.jsonl` — skill: **nenhuma** — ferramentas: Grep → Glob
  > Não consigo provisionar essa VM. Não tenho nenhuma ferramenta ou integração do Construct nesta sessão, e o repositório não menciona o Construct. As únicas ferramentas de infraestrutura que tenho são as do Kubernetes e as skills de manifest e triage da Metacortex. Nenhuma delas cria VMs.  Para eu cri
- `logs/isolada-antes/10-3.jsonl` — skill: **nenhuma** — ferramentas: Grep → Glob
  > Não consigo provisionar essa VM. Não tenho nenhuma ferramenta, integração ou CLI do Construct nesta sessão. As únicas ferramentas de infraestrutura que tenho são as de Kubernetes, e o repositório não menciona o Construct em nenhum arquivo.  Para eu seguir, preciso de uma destas opções: - **Acesso ao

