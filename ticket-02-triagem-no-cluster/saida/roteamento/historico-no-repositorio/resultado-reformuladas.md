# Matriz de roteamento — resultado `reformuladas`

Skills instaladas nas sessões (evento `init`): metacortex-manifest, metacortex-triage.

| # | Frase | Esperado | Disparou (por execução) | Confere? |
|---|---|---|---|---|
| 1 | o ticket-01-padrao-de-manifests/saida/nyx-barrado.yaml está no padrão da casa? | manifest | manifest · manifest · manifest | sim |
| 2 | o kubectl apply desse manifesto deu erro de validação, o que tem de errado no YAML? | manifest | nenhuma · nenhuma · nenhuma | **não** (0/3) |
| 3 | apliquei o manifesto no nyx-stg e os pods não ficam de pé | triage | triage · triage · triage | sim |

## Resposta de cada sessão

### 1. "o ticket-01-padrao-de-manifests/saida/nyx-barrado.yaml está no padrão da casa?"

- `logs/reformuladas/01-1.jsonl` — skill: **metacortex-manifest** — ferramentas: Skill → Read → Glob
  > **Não, o `nyx-barrado.yaml` não está no padrão da casa.** Fiz a revisão só lendo o YAML. Não tenho Bash nesta sessão, então não rodei o `trivy` nem o `check-manifest.py`. Também não abri o repositório do workload, então a regra 2.2 (probes) fica sem checagem de código.  **Falhas** - **[FALHA] Segred
- `logs/reformuladas/01-2.jsonl` — skill: **metacortex-manifest** — ferramentas: Skill → Read → Read → Glob
  > **Não, o `nyx-barrado.yaml` não está no padrão da casa.** O nome do arquivo já diz isso: é o manifest "barrado" de propósito. Não consegui rodar `trivy` nem `check-manifest.py`, porque não tenho Bash nesta sessão. A revisão abaixo é manual, contra as regras de `regras-buckets.md`. Também não abri o 
- `logs/reformuladas/01-3.jsonl` — skill: **metacortex-manifest** — ferramentas: Skill → Read → Bash → Glob
  > **Não, o `nyx-barrado.yaml` não está no padrão da casa.** Não consegui rodar o Trivy nem o `check-manifest.py` porque o Bash está desativado nesta sessão. Também não achei Dockerfile nem código do workload no repositório. A revisão abaixo vem só da leitura do YAML, comparada com o template da skill.

### 2. "o kubectl apply desse manifesto deu erro de validação, o que tem de errado no YAML?"

- `logs/reformuladas/02-1.jsonl` — skill: **nenhuma** — ferramentas: (nenhuma ferramenta)
  > Não recebi o manifesto nem a mensagem de erro, então não dá para apontar o problema ainda. Me envie uma destas opções:  - o YAML colado aqui, ou o caminho do arquivo no repositório - a saída completa do `kubectl apply`, incluindo a linha com o campo que falhou  Com o caminho do arquivo, eu leio o ma
- `logs/reformuladas/02-2.jsonl` — skill: **nenhuma** — ferramentas: (nenhuma ferramenta)
  > Não consegui ver o manifesto nem a mensagem de erro. Nada veio anexado à sua mensagem e não sei a qual arquivo você se refere.  Pode me mandar uma destas opções? - O caminho do arquivo no repositório (por exemplo, algo em `ticket-01-padrao-de-manifests/`). - O YAML colado aqui. - A saída completa do
- `logs/reformuladas/02-3.jsonl` — skill: **nenhuma** — ferramentas: (nenhuma ferramenta)
  > Não consigo ver o manifesto nem a mensagem de erro, porque nenhum dos dois veio na sua mensagem. Pode colar aqui:  1. O YAML do manifesto, ou o caminho do arquivo no repositório. 2. A saída completa do `kubectl apply`, com a linha do erro de validação.  Com isso consigo apontar o campo errado. Os er

### 3. "apliquei o manifesto no nyx-stg e os pods não ficam de pé"

- `logs/reformuladas/03-1.jsonl` — skill: **metacortex-triage** — ferramentas: Skill → ToolSearch → k8s:kubectl_get → k8s:kubectl_get → k8s:kubectl_get
  > 
- `logs/reformuladas/03-2.jsonl` — skill: **metacortex-triage** — ferramentas: Skill → ToolSearch → k8s:kubectl_get → k8s:kubectl_get → k8s:kubectl_get
  > 
- `logs/reformuladas/03-3.jsonl` — skill: **metacortex-triage** — ferramentas: Skill → ToolSearch → k8s:kubectl_get → k8s:kubectl_get → k8s:kubectl_get
  > 

