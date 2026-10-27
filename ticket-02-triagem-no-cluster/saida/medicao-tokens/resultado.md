## Medição real de tokens

Números extraídos do `claude -p --output-format stream-json` de cada sessão (gerados por [`medicao-tokens/medir.sh`](./medir.sh) e [`medicao-tokens/consolidar.py`](./consolidar.py); o JSON bruto de cada execução está em `medicao-tokens/runs/`). Cada execução é uma sessão limpa, com o mesmo servidor MCP, as mesmas permissões e o mesmo prompt; a única diferença entre as variantes é a skill instalada em `.claude/skills/`.

Modelo(s): claude-sonnet-5-5.

### Caso A — Chamado 1 (nyx-prod, OOMKilled)

Média de 3 execução(ões) sem skill e 3 com skill.

| Métrica | Sem skill | Com skill | Variação |
|---|---:|---:|---:|
| Tokens de entrada (sem cache) | 8 | 10 | +25% |
| Tokens de escrita em cache | 10.628 | 11.093 | +4% |
| Tokens de leitura de cache | 47.551 | 66.085 | +39% |
| Tokens de saída | 1.382 | 1.414 | +2% |
| **Tokens totais** | 59.569 | 78.602 | +32% |
| Custo (USD) | 0.0659 | 0.0718 | +9% |
| Tool calls no cluster | 3.3 | 2.0 | -40% |
| Turnos | 5.3 | 6.0 | +13% |
| Duração (s) | 13 | 15 | +15% |
| Skill acionada | 0/3 | 3/3 | |

### Caso B — Chamado 3 (nyx-stg, 503 com pods Running)

Média de 3 execução(ões) sem skill e 3 com skill.

| Métrica | Sem skill | Com skill | Variação |
|---|---:|---:|---:|
| Tokens de entrada (sem cache) | 8 | 10 | +25% |
| Tokens de escrita em cache | 10.791 | 17.232 | +60% |
| Tokens de leitura de cache | 48.004 | 66.479 | +38% |
| Tokens de saída | 1.464 | 1.715 | +17% |
| **Tokens totais** | 60.267 | 85.436 | +42% |
| Custo (USD) | 0.0674 | 0.0994 | +47% |
| Tool calls no cluster | 4.7 | 5.0 | +7% |
| Turnos | 6.7 | 9.0 | +35% |
| Duração (s) | 13 | 16 | +20% |
| Skill acionada | 0/3 | 3/3 | |

<details><summary>Execuções individuais</summary>

| Execução | Tokens totais | Saída | Custo (USD) | Tool calls | Skill | Erro |
|---|---:|---:|---:|---:|:-:|:-:|
| `A-nyx-prod-com-1` | 78.539 | 1.369 | 0.0712 | 2 | sim |  |
| `A-nyx-prod-com-2` | 78.650 | 1.466 | 0.0723 | 2 | sim |  |
| `A-nyx-prod-com-3` | 78.616 | 1.408 | 0.0718 | 2 | sim |  |
| `A-nyx-prod-sem-1` | 56.605 | 1.227 | 0.0574 | 3 | não |  |
| `A-nyx-prod-sem-2` | 59.911 | 1.346 | 0.0654 | 3 | não |  |
| `A-nyx-prod-sem-3` | 62.192 | 1.573 | 0.0748 | 4 | não |  |
| `B-nyx-stg-com-1` | 86.709 | 1.732 | 0.1012 | 5 | sim |  |
| `B-nyx-stg-com-2` | 84.727 | 1.687 | 0.0983 | 5 | sim |  |
| `B-nyx-stg-com-3` | 84.871 | 1.725 | 0.0987 | 5 | sim |  |
| `B-nyx-stg-sem-1` | 60.357 | 1.564 | 0.0674 | 5 | não |  |
| `B-nyx-stg-sem-2` | 60.074 | 1.366 | 0.0679 | 4 | não |  |
| `B-nyx-stg-sem-3` | 60.371 | 1.462 | 0.0669 | 5 | não |  |

</details>

## Diagnóstico final de cada execução

### `A-nyx-prod-com-1`

**CAUSA:** O container `api` do nyx-prod é morto por falta de memória (OOMKilled) em loop. O limite de memória, 24Mi, é baixo demais para a aplicação.

**EVIDÊNCIA:**
- Em `pod/nyx-api-656789474b-vm2jh`, o estado do container `api` é `Terminated`, motivo `OOMKilled`, exit code 137.
- O último ciclo durou cerca de 1 segundo (19:14:42 → 19:14:43).
- O ciclo anterior durou cerca de 5 segundos.
- `Limits.memory` é **24Mi** e `Requests.memory` é 16Mi (`Limits.cpu` 200m).
- O pod tem **1131 restarts** em 21 dias. O outro, `nyx-api-656789474b-znchx`, tem 1124 e o mesmo status.
- O pod `znchx` não foi descrito. Ele tem o mesmo ReplicaSet e o mesmo status, então presumo o mesmo limite.

**CAMADA:** container

**O que funciona:**
- `nyx-postgres-f6fdc6dbf-x7wvv` está 1/1 Running, com 1 restart recente. Esse restart coincide com o evento `SandboxChanged` de 74s atrás no pod da API, então o nó ou o runtime provavelmente reiniciou os sandboxes. Não investiguei a causa.
- A imagem `fabricioveronez/kube-news:v1` já está presente no nó, então o registry não é o problema.
- O container sobe e é morto logo em seguida, então a readinessProbe (`/ready`) nem chega a ser avaliada.

**AÇÃO SUGERIDA (não aplicada):**
- Aumentar o `resources.limits.memory` do Deployment `nyx-api`. Um ponto de partida razoável é 256Mi, com request em torno de 128Mi. Para dimensionar melhor, vale medir o consumo real de uma app Node.
- Pergunte ao time por que o limite está tão baixo. Se foi mudança recente, vale conferir o histórico do manifesto.

**Fora do escopo da triagem:** o `DB_PASSWORD` aparece em texto puro nas variáveis de ambiente do Deployment (`Pg#123`). O ideal é movê-lo para um Secret.

### `A-nyx-prod-com-2`

**CAUSA:** o container `api` do nyx-prod é morto por OOM em loop porque o limite de memória é de só 24Mi.

**EVIDÊNCIA:**
- Pods `nyx-api-656789474b-vm2jh` e `nyx-api-656789474b-znchx`: STATUS `OOMKilled`, com 1131 e 1125 restarts em 21 dias.
- `vm2jh`, container `api`: `Last State.Reason: OOMKilled`, `Exit Code: 137`, `Limits.memory: 24Mi` (requests de 16Mi).
- O container vive só 1 a 5 segundos por ciclo. Ele inicia em 19:14:08 e termina em 19:14:13, e o ciclo seguinte inicia em 19:14:42 e termina em 19:14:43. Isso é a aplicação estourando a memória logo na subida, sem chegar a atender tráfego.
- Só descrevi o pod `vm2jh`. O `znchx` também está em OOMKilled, com 1125 restarts, e deve ter o mesmo limite, já que os dois vêm do mesmo ReplicaSet.

**CAMADA:** container

**O que está funcionando:**
- O `nyx-postgres-f6fdc6dbf-x7wvv` está `1/1 Running`. Ele teve 1 restart recente (há cerca de 95s), mas o banco não é a causa.
- A imagem `fabricioveronez/kube-news:v1` está presente no nó, então não há problema de registry.
- O pod está agendado normalmente (`PodScheduled: True`).

**Observações:**
- Não vi os logs, porque a causa já fechou no `describe`.
- Os eventos mostram `SandboxChanged` e `services have not yet been read at least once` há cerca de 92s. Isso indica que o nó ou o kubelet reiniciou há pouco tempo (o postgres também reiniciou). É ruído sobre o problema principal: o OOM já vem acontecendo há 21 dias.
- O `DB_PASSWORD` (`Pg#123`) está em texto puro no manifesto do Deployment, e o `describe` o expõe. Vale mover para um Secret.

**AÇÃO SUGERIDA (não aplicada):** o time deve aumentar `resources.limits.memory` do deployment `nyx-api`. Um Node.js costuma precisar de pelo menos 128Mi a 256Mi, e o valor ideal deve vir da medição do consumo real. O `requests.memory` também deve subir para algo coerente com o limite. A triagem não alterou nada no cluster.

### `A-nyx-prod-com-3`

Causa fechada; o skill manda parar aqui. Não apliquei nada no cluster.

```
CAUSA: O container da API é morto por OOMKilled em loop porque o limite de memória (24Mi) é baixo demais para a aplicação.
EVIDÊNCIA: pod nyx-api-656789474b-vm2jh (e o -znchx, mesmo ReplicaSet), container "api":
           Limits.memory = 24Mi (Requests.memory = 16Mi), Last State.Reason = OOMKilled,
           Exit Code = 137, Restart Count = 1132 (1125 no outro pod, ~21 dias de loop).
           Cada execução dura 1–2 segundos (19:14:42→19:14:43, 19:15:40→19:15:42), ou seja,
           o processo estoura a memória logo na subida.
CAMADA: container
AÇÃO SUGERIDA: Aumentar resources.limits.memory do Deployment nyx-api. Como a aplicação (kube-news, Node.js) morre
               já na inicialização, 24Mi não basta. Um ponto de partida razoável é 256Mi de limit e
               128Mi de request, ajustando depois pelo consumo real. O time deve fazer a mudança.
```

**O que está funcionando e o que não está**
- **nyx-postgres:** `1/1 Running`, com 1 restart (há 2m24s). O banco não é a causa.
- **nyx-api, as duas réplicas:** ambas em `0/1 OOMKilled`, então a API está fora do ar. O Deployment não tem nenhuma réplica saudável.
- **Imagem:** `fabricioveronez/kube-news:v1` baixa normalmente. O evento `Pulled` diz que ela já está no nó.
- **Evento de sandbox:** há um `SandboxChanged` e um `Failed: services have not yet been read at least once` de 2 minutos atrás. Isso indica que o kubelet ou nó reiniciou há pouco tempo, o que bate com o restart recente do postgres. É ruído de reinício do nó, não a causa do loop. O loop já existia havia 21 dias.

**Segurança**
- O `describe` mostra `DB_PASSWORD` em texto puro nas variáveis de ambiente do Deployment (`Pg#123`). Vale mover para um Secret e trocar essa senha, já que ela agora aparece nesta conversa.

### `A-nyx-prod-sem-1`

A causa é falta de memória. Os dois pods da `nyx-api` estão em **OOMKilled** (exit 137), com mais de 1.100 restarts em 21 dias.

**Causa:** o container `api` tem limite de memória de **24Mi** (request de 16Mi). Isso é muito pouco para uma app Node, que é o que a imagem `kube-news:v1` parece ser. O container sobe, estoura a memória em poucos segundos (ele roda por 1 a 5s) e o kernel mata o processo. Depois cai em CrashLoopBackOff e o ciclo se repete.

**Não consegui ver os logs:** o `previous` retornou "unable to retrieve container logs". Então não confirmei pelo log o que consome a memória. Pelo tamanho do limite, ele é o principal suspeito.

**Outras observações:**
- O Postgres teve 1 restart, 62s atrás. O evento `SandboxChanged` de 58s atrás sugere que o nó ou o runtime reiniciou, e isso pode ter afetado todos os pods.
- `DB_PASSWORD` está em texto puro no manifesto do Deployment (`Pg#123`). O ideal é movê-la para um Secret.

**Correção sugerida:** aumentar o limite de memória, por exemplo `requests: 128Mi` e `limits: 256Mi`, e depois ver o consumo real para ajustar. Posso aplicar essa mudança no Deployment? Essa ferramenta só lê, então eu precisaria do `kubectl` pelo Bash, ou você roda o comando abaixo:

```
kubectl -n nyx-prod set resources deploy/nyx-api --requests=memory=128Mi --limits=memory=256Mi
```

Isso faz um rollout dos pods em produção. Quer que eu aplique?

### `A-nyx-prod-sem-2`

Achei a causa: o container da API está sendo morto por falta de memória (OOMKilled, exit 137). Eu não mudei nada no cluster.

**O que está acontecendo (namespace `nyx-prod`, deployment `nyx-api`)**
- Os dois pods (`nyx-api-656789474b-vm2jh` e `-znchx`) estão em `OOMKilled`, com mais de 1.125 restarts cada em 21 dias.
- O limite de memória é de **24Mi** (request de 16Mi). Uma aplicação Node (a imagem é `kube-news:v1`) não cabe nisso. O container sobe, estoura a memória em 1 a 2 segundos e é morto. Depois disso entra em CrashLoopBackOff.
- Os pods nunca ficam `Ready`, então a API está praticamente fora do ar.
- O `nyx-stg` usa a mesma imagem e está rodando, com poucos restarts. Dá para comparar o limite de memória do stg com o do prod.
- O `nyx-postgres` do prod está saudável.

**O que eu não consegui confirmar**
- Não consegui os logs da instância anterior (`unable to retrieve container logs`). Por isso não sei o consumo real de memória da aplicação. Isso me deixa seguro sobre o limite estar baixo demais, mas não sobre qual valor é suficiente. Se houver também um leak, só aumentar o limite vai adiar o problema.

**Outros pontos**
- O `DB_PASSWORD` está em texto puro no manifesto do deployment. O ideal seria mover para um Secret.
- Os `orion-prod` e `orion-stg` estão com `ImagePullBackOff`. Não tem relação com este problema.

**Sugestão de correção**
Aumentar o limite para algo como 256Mi (request de 128Mi) no deployment `nyx-api`. Antes disso, vale ver o limite do stg, que está funcionando, para usar como referência.

Quer que eu veja o deployment do stg e aplique o ajuste no prod? Como é produção, só mexo depois da sua confirmação.

### `A-nyx-prod-sem-3`

## Diagnóstico

A API do nyx-prod não está só reiniciando, está **fora do ar**. Os dois pods (`nyx-api-656789474b-vm2jh` e `-znchx`) estão em crash loop por **OOMKilled** (exit code 137), com cerca de 1130 restarts cada.

**Causa:** o limite de memória do container é **24Mi** (request 16Mi). É um valor muito baixo pra um app Node. O container sobe, estoura a memória em 1 a 2 segundos e o kernel o mata. Ele nunca chega a ficar Ready.

- O deployment está com `Available=False` (`MinimumReplicasUnavailable`) e `Progressing=False` (`ProgressDeadlineExceeded`).
- Isso acontece desde a criação, há 21 dias (revision 1, nunca houve um rollout bom).
- Os logs do container anterior não estão disponíveis (`unable to retrieve container logs`), então a causa vem do status e dos limites, não do log do app.

## Correção sugerida

Subir o limite de memória do deployment, por exemplo para request `128Mi` e limit `256Mi`. Antes de escolher o valor, eu compararia com o `nyx-api` do `nyx-stg`, que está rodando (5 restarts). Posso olhar os limites dele pra usar de referência.

Não alterei nada. Quer que eu aplique a mudança no `nyx-prod`? Não tenho uma ferramenta de escrita no Kubernetes carregada aqui, então o mais provável é eu te passar o comando:

```
kubectl -n nyx-prod set resources deploy/nyx-api --requests=memory=128Mi --limits=memory=256Mi
```

**Outros pontos que vi no deployment:**
- `DB_PASSWORD` está em texto puro no manifest (`Pg#123`). O ideal é mover pra um Secret.
- Houve um restart do cluster há cerca de 2 minutos (`SandboxChanged`, todos os pods com 1 restart recente). Isso é um evento separado do OOM.

### `B-nyx-stg-com-1`

**CAUSA:** O Service `nyx-api` não casa com nenhum pod: o seletor dele não bate com os rótulos dos pods. Por isso o Endpoints `nyx-api` está vazio e nenhum tráfego é entregue.

**EVIDÊNCIA:**
- `Service/nyx-api` → `spec.selector: app: nyx-api`
- Pods `nyx-api-7f4487c6ff-bl899` e `nyx-api-7f4487c6ff-dv9z8` → `metadata.labels: app: nyxapi`
- `Endpoints/nyx-api` não tem nenhum `subsets`, ou seja, nenhum endereço.

**CAMADA:** roteamento

**AÇÃO SUGERIDA:** O time deve alinhar os dois valores, em um destes lugares:
- Corrigir o `spec.selector` do Service para `app: nyxapi`.
- Corrigir o label em `spec.template.metadata.labels` do Deployment para `app: nyx-api`. Neste caso o `spec.selector.matchLabels` do Deployment também precisa mudar. Esse campo é imutável, então o Deployment teria de ser recriado.

O mais simples é a primeira opção. Não apliquei nada no cluster.

**O que está funcionando:**
- Os dois pods `nyx-api` estão `Running` e `1/1 Ready`, nos IPs 10.244.0.2 e 10.244.0.4.
- O Postgres está `Running` e Ready. O Service `nyx-postgres` usa `app: nyx-postgres`, que bate com o rótulo do pod.
- Imagem, agendamento e probes não são o problema.

**Pontos de atenção, fora da causa principal:**
- Os pods da API reiniciaram 4 e 5 vezes. O último término foi com exit code 1, às 22:14:18Z, uns 5 segundos depois de iniciar. Isso coincide com o restart do Postgres às 22:14:02Z (exit 255), e a API provavelmente subiu antes de o banco estar pronto. Não li os logs, porque a causa do tráfego já estava fechada. Hoje os pods estão estáveis.
- As credenciais do banco (`DB_PASSWORD`, `POSTGRES_PASSWORD`) estão em texto puro nos manifests dos pods. Vale mover para um Secret.

### `B-nyx-stg-com-2`

**CAUSA:** O Service `nyx-api` não casa com nenhum pod, porque o seletor dele não bate com o rótulo dos pods. O Service procura `app: nyx-api`, mas os pods têm `app: nyxapi`, sem o hífen. Por isso o Endpoints está vazio e nenhum tráfego chega.

**EVIDÊNCIA:**
- `service/nyx-api` → `spec.selector: {app: nyx-api}`. Esse valor também está no `last-applied-configuration`, então foi aplicado assim.
- `pods nyx-api-7f4487c6ff-bl899` e `-dv9z8` → `metadata.labels.app: nyxapi`.
- `endpoints/nyx-api` → não tem nenhum `subsets`, ou seja, zero endereços.

**CAMADA:** roteamento

**AÇÃO SUGERIDA:** O time deve alinhar os dois valores. O Service ou o template de labels do Deployment `nyx-api` precisa usar o mesmo valor (`nyx-api` ou `nyxapi`). Se mudar o label no Deployment, o `spec.selector.matchLabels` também precisa ser ajustado. Esse campo é imutável, então o Deployment teria que ser recriado. Alterar o selector do Service é mais simples. Não apliquei nada, pela regra de triagem.

**O que está funcionando:**
- Os 2 pods `nyx-api` estão `Running`, `1/1 Ready`. A readinessProbe (`/ready`:8080) passa.
- O `nyx-postgres` está `Running` e Ready.
- O `targetPort` 8080 do Service bate com o `containerPort` 8080.

**Ponto de atenção, fora da causa principal:**
- Os pods `nyx-api` têm 4 e 5 restarts. O último término foi `exit 1` às 22:14:18Z, uns 5 segundos depois de iniciar.
- O Postgres reiniciou uma vez (`exit 255`) às 22:14:02Z. A hipótese mais provável é que a API subiu antes do banco voltar e caiu na conexão. Não li os logs para confirmar.
- Os pods estabilizaram e estão Ready, então isso não explica a falta de tráfego.
- As credenciais do banco (`DB_PASSWORD`) estão em texto puro no spec do pod. Vale mover para um Secret.

### `B-nyx-stg-com-3`

**CAUSA:** O Service `nyx-api` não tem endpoints porque o seletor dele não casa com os rótulos dos pods. O Service procura `app: nyx-api`, mas os pods têm `app: nyxapi`, sem o hífen.

**EVIDÊNCIA:**
- `Service/nyx-api`: `spec.selector` é `{app: nyx-api}`. Esse valor também está no `last-applied-configuration`.
- `Pod/nyx-api-7f4487c6ff-bl899` e `Pod/nyx-api-7f4487c6ff-dv9z8`: `metadata.labels.app` é `nyxapi`.
- `Endpoints/nyx-api`: não tem `subsets`, ou seja, não há nenhum endereço. Ele existe desde a criação, em 2026-09-17T18:01:55Z.

**CAMADA:** roteamento

**AÇÃO SUGERIDA:** O time deve alinhar os dois valores. A opção mais provável é mudar `spec.selector.app` do Service para `nyxapi`. A outra é corrigir o label no pod template do Deployment para `nyx-api`, o que recria os pods. Não apliquei nada no cluster.

**O que está funcionando:**
- Os dois pods `nyx-api` estão `Running`, 1/1 Ready e com a condição `Ready=True`.
- O `nyx-postgres` está 1/1 Ready.
- O Service tem `port 80 → targetPort 8080`, e os pods expõem a 8080. A porta não é o problema.

**Observações fora da causa principal:**
- **Reinício recente:** todos os pods reiniciaram por volta de 2026-10-08 22:14Z. O `nyx-postgres` saiu com exit 255 e os `nyx-api` com exit 1 (4 e 5 restarts). Estão estáveis agora. É provável que o Postgres tenha voltado depois da API, que falhou ao conectar. Não olhei os logs porque a causa já estava fechada.
- **Credenciais:** o `DB_PASSWORD` e o `POSTGRES_PASSWORD` estão em texto puro nos manifestos. Vale mover para um Secret.
- **Possível outro 503:** o Service do `nyx-postgres` também não apareceu nesta triagem. Se a API acessa o banco por `nyx-postgres`, confirme que o seletor dele casa com o label `app: nyx-postgres`. Não verifiquei.

### `B-nyx-stg-sem-1`

## Causa

O selector do Service não bate com os labels dos pods:

- Service `nyx-api` → `selector: app=nyx-api`
- Pods `nyx-api-7f4487c6ff-*` → label `app=nyxapi` (sem hífen)

Por isso o Endpoints `nyx-api` está vazio, sem `subsets`, e o Service não entrega tráfego. Os pods estão saudáveis (Running, Ready). O `selector` com `app=nyx-api` não retorna nenhum pod.

Eu só verifiquei o pod `bl899`. O outro pod (`dv9z8`) vem do mesmo ReplicaSet, então deve ter o mesmo label.

## Correção

Há duas opções. A primeira é mais simples e menos arriscada:

1. **Corrigir o selector do Service** para `app: nyxapi`. Não reinicia pods.
2. **Corrigir o label no template do Deployment** para `app: nyx-api`. Isso também exige ajustar o `selector.matchLabels` do Deployment, que é imutável, então teria que recriar o Deployment.

Recomendo a 1, a menos que o nome `nyxapi` tenha sido um erro no manifesto do Deployment e você queira padronizar. Posso aplicar um patch no Service, se você confirmar:

```
kubectl -n nyx-stg patch svc nyx-api -p '{"spec":{"selector":{"app":"nyxapi"}}}'
```

## Outros pontos

- Os pods reiniciaram há cerca de 2 minutos (`SandboxChanged`, e o erro `services have not yet been read at least once`). Isso parece ser um restart do nó ou do kubelet e já se resolveu: os pods estão Ready. A API também reiniciou 4 a 5 vezes, provavelmente por tentar conectar no Postgres antes de ele subir.
- `DB_PASSWORD` está em texto puro no manifesto do Deployment. Vale mover para um Secret.

### `B-nyx-stg-sem-2`

**Causa:** o selector do Service não bate com os labels dos pods.

- Service `nyx-api` (nyx-stg): selector `app=nyx-api`
- Pods do Deployment `nyx-api`: label `app=nyxapi` (sem hífen)

Por isso o Service está com `Endpoints: <none>`, mesmo com os 2 pods `1/1 Running` e Ready.

**Correção:** tem duas opções, e as duas dão o mesmo resultado.

1. Ajustar o Service para o label dos pods (menos invasivo, não reinicia nada):
   ```
   kubectl -n nyx-stg patch svc nyx-api -p '{"spec":{"selector":{"app":"nyxapi"}}}'
   ```
2. Corrigir o label no Deployment para `app: nyx-api`. Isso exige mudar o `selector.matchLabels`, que é imutável. Você teria que recriar o Deployment.

Recomendo a opção 1 agora e corrigir o manifesto no repositório, para o próximo `apply` não reintroduzir o erro. Também confira se o Service no repositório usa `nyx-api` ou `nyxapi`, para saber qual dos dois manifestos está errado.

**Outras observações:**
- Os pods tiveram 4 a 5 restarts, os últimos há cerca de 3 minutos, junto com o restart do postgres. Isso parece ser reinício do nó ou do cluster e não causa o problema de tráfego. Se os restarts continuarem, vale olhar os logs.
- As senhas do banco (`DB_PASSWORD`) estão em texto puro nos Deployments. O ideal é movê-las para um Secret.

Quer que eu aplique o patch da opção 1? Não alterei nada no cluster até agora.

### `B-nyx-stg-sem-3`

## Causa raiz

O selector do Service não bate com os labels dos pods:

- Service `nyx-api` tem `selector: app: nyx-api`.
- Os pods do Deployment têm o label `app: nyxapi`, sem hífen.

Por isso `kubectl get pods -l app=nyx-api` volta vazio e o Endpoints `nyx-api` não tem nenhum subset. Os pods estão saudáveis, com 2/2 Ready, mas o Service não os encontra e não entrega tráfego.

## Correção

O jeito mais simples é ajustar o Service, porque o `selector` do Deployment é imutável. Mudar o label no Deployment obrigaria a recriá-lo.

```bash
kubectl -n nyx-stg patch svc nyx-api -p '{"spec":{"selector":{"app":"nyxapi"}}}'
```

No manifesto de origem, o certo é padronizar para `nyx-api` ou `nyxapi` no Service e no Deployment. Se o Deployment for recriado, o certo é `nyx-api`, que é o nome usado nos outros recursos.

Não apliquei a correção, porque altera o ambiente. Posso aplicar o patch se você quiser.

## Observações

- Os pods `nyx-api` têm 4 e 5 restarts, e o `nyx-postgres` tem 1, todos há cerca de 3 minutos. Isso não explica o problema de tráfego, mas vale investigar depois, com `kubectl logs --previous`.
- O Deployment tem `DB_PASSWORD` em texto puro. O ideal é movê-lo para um Secret.

