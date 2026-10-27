# Matriz de roteamento — metacortex-manifest × metacortex-triage

As duas skills disputam o mesmo território (Kubernetes, YAML, coisa quebrada) e o agente escolhe qual carregar só pela descrição. Esta matriz foi **medida**: as duas skills instaladas, cada frase numa sessão limpa do Claude Code (`claude -p`, Sonnet 5.5, sem histórico, sem settings ou plugins do usuário), **três vezes por frase**, registrando a primeira chamada à ferramenta `Skill`.

- Script: [`roteamento/rodar-matriz.sh`](./roteamento/rodar-matriz.sh) e [`roteamento/consolidar-matriz.py`](./roteamento/consolidar-matriz.py); frases em [`frases-enunciado.txt`](./roteamento/frases-enunciado.txt) e [`frases-reformuladas.txt`](./roteamento/frases-reformuladas.txt)
- Resultado com a resposta de cada sessão: [`resultado-isolada-antes.md`](./roteamento/resultado-isolada-antes.md), [`resultado-isolada-depois.md`](./roteamento/resultado-isolada-depois.md), [`resultado-isolada-reformuladas.md`](./roteamento/resultado-isolada-reformuladas.md)
- Logs de cada sessão: [`roteamento/logs/`](./roteamento/logs/)

## Ambiente do teste: por que isolado

A primeira medição rodou **dentro do repositório do desafio**. A conferência dos logs mostrou que 7 de 69 sessões leram arquivos do próprio roteamento (inclusive esta matriz, com o disparo esperado de cada frase) antes de escolher a skill, e que as falhas daquela medição vinham do repositório: diante de "esse manifesto" ou "esse deployment", o agente achava vários manifestos e perguntava qual era **antes** de carregar a skill.

A medição oficial roda num **diretório isolado** que contém só as duas skills, o manifesto citado numa das frases reformuladas e o servidor MCP. "Antes" usa as skills como estavam antes dos ajustes (recuperadas do git); "depois" usa as atuais. A única diferença entre as duas rodadas é o texto das skills. A medição dentro do repositório fica como histórico em [`roteamento/historico-no-repositorio/`](./roteamento/historico-no-repositorio/) e [`roteamento/logs/no-repositorio/`](./roteamento/logs/no-repositorio/).

---

## Resultado: que skill disparou

| # | Frase | Esperado | Antes dos ajustes | Depois dos ajustes |
|---|---|---|---|---|
| 1 | o pod do nyx-prod não sobe | triage | triage ×3 | triage ×3 |
| 2 | por que esse deployment está 0/3 | triage | triage ×3 | triage ×3 |
| 3 | o service do nyx-stg não tem endpoint | triage | triage ×3 | triage ×3 |
| 4 | revisa esse deployment antes de eu subir | manifest | manifest ×3 | manifest ×3 |
| 5 | esse manifesto está no padrão da casa? | manifest | manifest ×3 | manifest ×3 |
| 6 | cria um Deployment novo do zero pra mim | manifest | manifest ×3 | manifest ×3 |
| 7 | esse manifesto não sobe no cluster | ambígua | triage ×3 | triage ×3 |
| 8 | o Service do nyx não está entregando tráfego | triage | triage ×3 | triage ×3 |
| 9 | o que é um DaemonSet? | nenhuma | nenhuma ×3 | nenhuma ×3 |
| 10 | provisiona uma VM nova no Construct pro cliente orion | nenhuma | nenhuma ×3 | nenhuma ×3 |

**60 de 60 sessões dispararam a skill esperada**, antes e depois. Nenhuma frase de triagem carregou a skill de manifests, nem o contrário, e as duas fora de escopo não carregaram nenhuma. As descrições das duas skills já separavam bem o território: "antes de aplicar", trabalho no YAML × "já aplicados", trabalho no cluster.

---

## O que errou e o que mudou por causa disso

O erro não estava em **qual** skill disparava, e sim no que a skill fazia depois.

### Frase 7 — "esse manifesto não sobe no cluster" (ambígua)

A frase serve para dois casos: `apply` rejeitado (o YAML é o problema, trabalho da `metacortex-manifest`) ou objetos aplicados que não ficam de pé (trabalho da triagem). A triagem dispara nas duas rodadas, porque "no cluster" pesa para o lado do cluster, e essa escolha foi mantida. O que mudou foi o comportamento:

| | O que a triagem fez em cada sessão |
|---|---|
| **Antes** | 1ª: pediu o namespace. 2ª e 3ª: **foram direto ao cluster** (acharam um manifesto, leram e começaram a consultar pods) sem saber se o `apply` tinha sido aceito, até esbarrar no limite de turnos do teste |
| **Depois** | As três perguntaram primeiro: *"o `apply` foi aceito e os pods não ficam de pé, ou o `apply` deu erro?"*, e explicaram que, se deu erro, não há nada no cluster para ler e o caso é da `metacortex-manifest` |

**Mudança na skill de triagem** que produziu isso: a seção "Quando não é triagem" do `SKILL.md`.

### Frase 5 — "esse manifesto está no padrão da casa?"

Na medição dentro do repositório, a frase falhou uma vez. A descrição da `metacortex-manifest` foi ajustada para citar o "padrão da casa" e "perguntar se um manifesto está no padrão". A medição isolada mostra que **a frase já roteava certo antes do ajuste (3/3)**: a falha vinha do repositório, não da descrição. O ajuste foi mantido porque não piorou nada (3/3 depois) e deixa o gatilho explícito, mas o registro honesto é que ele **não era necessário**.

### Outros ajustes na triagem que vieram da execução, não da matriz

A tabela do Passo 1 (pod `1/1 Ready` com Service sem endpoint é problema de roteamento) e a ação sugerida que remete à `metacortex-manifest` vieram das triagens e do Ticket 04 (ver [`../origem-e-curadoria.md`](../origem-e-curadoria.md)).

---

## Casos fora do escopo e frases mal formuladas

**Fora do escopo (9 e 10).** "O que é um DaemonSet?" é conceitual: o agente responde com conhecimento geral, e o bloco de vocabulário do padrão ficou de fora da skill de propósito (curadoria do Ticket 01). "Provisiona uma VM no Construct" é outro sistema: nenhuma skill dispara, e o agente diz que não tem acesso ao Construct em vez de improvisar.

**Frase mal formulada.** O enunciado avisa que às vezes a frase é que está errada, não a skill. A frase 7 é o caso: ela não diz se o `apply` foi aceito. As versões reformuladas, com o estado explícito, roteiam sem ambiguidade:

| Frase reformulada | Esperado | Disparou |
|---|---|---|
| "o `ticket-01-padrao-de-manifests/saida/nyx-barrado.yaml` está no padrão da casa?" | manifest | manifest ×3 |
| "o kubectl apply desse manifesto deu erro de validação, o que tem de errado no YAML?" | manifest | manifest ×3 |
| "apliquei o manifesto no nyx-stg e os pods não ficam de pé" | triage | triage ×3 |

**Orientação para o plantão:** diga *em que ponto* falhou (o `apply` deu erro, ou aplicou e não sobe) e, se possível, *qual* objeto. Com isso cada frase vai direto para a skill certa, sem a pergunta extra da triagem.
