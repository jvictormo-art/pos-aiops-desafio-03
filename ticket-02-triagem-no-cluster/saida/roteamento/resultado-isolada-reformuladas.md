# Matriz de roteamento — resultado `isolada-reformuladas`

Skills instaladas nas sessões (evento `init`): metacortex-manifest, metacortex-triage.

| # | Frase | Esperado | Disparou (por execução) | Confere? |
|---|---|---|---|---|
| 1 | o ticket-01-padrao-de-manifests/saida/nyx-barrado.yaml está no padrão da casa? | manifest | manifest · manifest · manifest | sim |
| 2 | o kubectl apply desse manifesto deu erro de validação, o que tem de errado no YAML? | manifest | manifest · manifest · manifest | sim |
| 3 | apliquei o manifesto no nyx-stg e os pods não ficam de pé | triage | triage · triage · triage | sim |

## Resposta de cada sessão

### 1. "o ticket-01-padrao-de-manifests/saida/nyx-barrado.yaml está no padrão da casa?"

- `logs/isolada-reformuladas/01-1.jsonl` — skill: **metacortex-manifest** — ferramentas: Skill → Read → Glob → Read → Bash
  > Não tenho como rodar `trivy` nem `check-manifest.py` aqui, porque o Bash está desabilitado nesta sessão. Fiz a revisão lendo o YAML contra as regras em `regras-buckets.md`. Isso cobre as regras mecânicas, mas não a saída real das ferramentas.  **Não, o `nyx-barrado.yaml` não está no padrão da casa.*
- `logs/isolada-reformuladas/01-2.jsonl` — skill: **metacortex-manifest** — ferramentas: Skill → Read → Glob → Read → ToolSearch
  > Não, não está no padrão. Fiz a revisão lendo o YAML, porque não tenho Bash nesta sessão e não consegui rodar `trivy` nem `check-manifest.py`. Também não tenho o repositório do workload nyx, então a regra 2.2 (probes apontando para endpoints reais) ficou sem conferência.  **Falhas**  - **1.1 Nome em 
- `logs/isolada-reformuladas/01-3.jsonl` — skill: **metacortex-manifest** — ferramentas: Skill → Read → Glob → Read → Bash
  > Não tenho o Bash nesta sessão, então não rodei `trivy` nem `check-manifest.py`. Também não há repositório do workload para confirmar as probes. Comparei o YAML com as regras da skill e com `regras-buckets.md`.  **Não, não está no padrão.** O arquivo se chama `nyx-barrado` e está barrado de propósito

### 2. "o kubectl apply desse manifesto deu erro de validação, o que tem de errado no YAML?"

- `logs/isolada-reformuladas/02-1.jsonl` — skill: **metacortex-manifest** — ferramentas: Skill → Glob → Read → Bash
  > O erro de validação vem da linha 4: `metadata.name: NyxAPI`. Nomes de recurso no Kubernetes precisam seguir RFC 1123, ou seja, só minúsculas, números, `-` e `.`. Letra maiúscula faz o `apply` rejeitar o manifesto. Troque por `nyx-api`, que segue o padrão `<cliente>-<componente>`.  Não consegui rodar
- `logs/isolada-reformuladas/02-2.jsonl` — skill: **metacortex-manifest** — ferramentas: Skill → Glob → Read → Glob → Bash
  > Não consegui rodar o `trivy` nem o `check-manifest.py`, porque o Bash está desabilitado nesta sessão. Esta análise vem só da leitura de `ticket-01-padrao-de-manifests/saida/nyx-barrado.yaml`. Também não há repositório do workload aqui, então não verifiquei se as probes e a porta batem com o código. 
- `logs/isolada-reformuladas/02-3.jsonl` — skill: **metacortex-manifest** — ferramentas: Skill → Glob → Read → Glob
  > O erro de validação vem da linha 4: `name: NyxAPI`. Nomes de recurso no Kubernetes precisam ser RFC 1123, ou seja, minúsculas, números e `-`. Maiúsculas são rejeitadas. Troque para `nyx-api`, que é o nome que o Service já usa.  Também há um problema que o `apply` não acusa. O Service tem `selector: 

### 3. "apliquei o manifesto no nyx-stg e os pods não ficam de pé"

- `logs/isolada-reformuladas/03-1.jsonl` — skill: **metacortex-triage** — ferramentas: Skill → ToolSearch → k8s:kubectl_get → k8s:kubectl_get → k8s:kubectl_get
  > 
- `logs/isolada-reformuladas/03-2.jsonl` — skill: **metacortex-triage** — ferramentas: Skill → ToolSearch → k8s:kubectl_get → k8s:kubectl_get → k8s:kubectl_get
  > 
- `logs/isolada-reformuladas/03-3.jsonl` — skill: **metacortex-triage** — ferramentas: Skill → ToolSearch → k8s:kubectl_get → k8s:kubectl_get → k8s:kubectl_get
  > 

