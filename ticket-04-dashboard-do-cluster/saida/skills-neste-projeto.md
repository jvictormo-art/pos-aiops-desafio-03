# O que aconteceu com as skills durante o projeto

## Instalação

As duas skills estão instaladas na raiz do desafio, onde o agente trabalha:

```
.claude/skills/metacortex-manifest -> ticket-01-padrao-de-manifests/skill
.claude/skills/metacortex-triage   -> ticket-02-triagem-no-cluster/skill
```

São symlinks, para existir uma cópia só de cada skill (a entregue no ticket é a mesma que o agente carrega). O evento `init` de cada sessão registrada confirma que o agente as enxerga (`"skills": [..., "metacortex-manifest", "metacortex-triage"]`).

> **Versão anterior deste registro.** Na primeira entrega, as skills existiam só nas pastas dos tickets e nunca tinham sido instaladas em `.claude/skills/`; o registro dizia isso e descrevia uma invocação manual. A revisão apontou o pré-requisito não cumprido. Tudo abaixo vem de sessões feitas **com as skills instaladas**.

## Como foi observado

As tarefas do projeto que envolviam o cluster ou os manifests foram feitas em sessões gravadas do Claude Code (`claude -p`, Sonnet 5.5), abertas na raiz do desafio, com o servidor MCP do Ticket 02 em modo não destrutivo. **Nenhum pedido cita uma skill**: o objetivo é ver o que o agente escolhe só pela descrição. Script: [`sessoes-skills/sessao.sh`](./sessoes-skills/sessao.sh); registro bruto de cada sessão em [`sessoes-skills/logs/`](./sessoes-skills/logs/).

| # | Tarefa do projeto (pedido enviado) | Skill esperada | O que disparou | Resultado |
|---|---|---|---|---|
| 01 | "o fake-shop do cliente orion, no namespace orion-prod, não sobe: os pods ficam reiniciando ainda no init" | triagem | **`metacortex-triage`, sozinha** | Causa certa: o Secret aplicado tinha o placeholder `CHANGE_ME` e a migração não autenticava no Postgres. Só leitura pelo MCP |
| 02 | "Gere os manifests de Kubernetes do kube-news [...] na pasta `manifests-kube-news/`" | manifests | **`metacortex-manifest`, sozinha** | Leu o código do kube-news no GitHub (porta, `/ready`, variáveis do banco), gerou os cinco manifests, rodou o script da skill (20 OK) e o Trivy, deixou o Secret com `CHANGE_ME` |
| 03 | "acabei de subir o kube-news [...] e o deployment não fica disponível. Por quê?" | triagem | **`metacortex-triage`, sozinha** | Localizou o erro de pull da imagem pelos eventos (camada registry), sem escrever no cluster |
| 04 | "No dashboard [...], como o k8s_reader decide se um Service tem endpoint [...]? Só explique" | nenhuma | nenhuma | Explicou o código sem carregar a triagem, apesar de "Service" e "endpoint" estarem no pedido |
| 05 | "Escreva [...] um rascunho de ADR [...] comparando Endpoints ou EndpointSlice" | nenhuma | nenhuma | Escreveu o ADR; nenhuma skill de Kubernetes apareceu numa tarefa de documentação |

Além dessas, as três triagens dos chamados e as 69 sessões da matriz de roteamento do Ticket 02 rodaram com as mesmas skills instaladas ([`../../ticket-02-triagem-no-cluster/saida/roteamento/`](../../ticket-02-triagem-no-cluster/saida/roteamento/)).

## O que disparou sozinho

- **`metacortex-triage`** nas duas vezes em que um workload do projeto quebrou (01 e 03). As duas sessões começaram pelo estado dos pods, desceram para eventos ou logs e pararam ao achar a causa, sem nenhuma escrita.
- **`metacortex-manifest`** ao pedir os manifests do kube-news (02), sem o pedido dizer "padrão" nem "skill".

## O que precisou ser chamado manualmente

Nada, nas sessões gravadas. A diferença em relação à primeira entrega é só a instalação: com as skills em `.claude/skills/`, as duas disparam pela descrição.

## O que apareceu onde não devia

- **Nas tarefas de código e documentação (04, 05), nada**, o que era o risco principal, já que "Service", "endpoint" e "EndpointSlice" são palavras do território da triagem.
- **A triagem sugeriu uma ação fora do padrão da casa (03).** Diante do pull que falhava, a ação sugerida incluiu "ajustar o campo `image` do Deployment". Trocar a imagem por uma pública viola a regra 3.7 da `metacortex-manifest`. Cada skill só conhece o próprio território: a triagem não sabe que existe um padrão de imagens. A sessão também atribuiu a causa ao DNS do registry, que é o sintoma. A causa de fundo era outra (o kubelet tinha registro de um pull anterior da mesma imagem, ver curadoria), e a triagem, corretamente, não foi além da camada. **Mudança aplicada na skill de triagem por causa disso:** quando a correção for no manifesto, a AÇÃO SUGERIDA remete à `metacortex-manifest` e não propõe atalhos que o padrão proíbe (imagem de registry público, `:latest`).

## O que precisou ser reexplicado

- **O nome da imagem no registry interno e o banco de apoio (02).** A skill de manifests sabe que a imagem tem de vir de `registry.metacortex.io`, mas não tem como saber o nome que o Loom publicou nem onde está o Postgres do laboratório. Isso foi dito no pedido. Sem essa informação, a skill pergunta ou deixa um placeholder.
- **Credenciais.** Nas duas gerações de manifests (fake-shop no Ticket 01, kube-news aqui), o Secret sai com `CHANGE_ME`, e é preciso lembrar que o segredo é criado fora do Git (`laboratorio/subir-workloads.sh`). É o comportamento certo pela regra 3.3, mas é um passo que todo mundo esquece.
- **Comandos compostos.** Na sessão 02, dois comandos Bash com `cd ... && ...` foram negados, porque as permissões liberavam comandos simples (`git clone`, `python3`) e não encadeamentos. O agente contornou com leitura direta pelo GitHub (WebFetch) e caminhos absolutos. Não é falha da skill, mas mostra que o `SKILL.md` de manifests assume liberdade de shell que um ambiente restrito não dá.

## O conhecimento das skills no desenho do dashboard

Independentemente de disparo, a tabela de decisão da triagem (`OOMKilled` → container, `ImagePullBackOff` → registry, `Running` sem endpoint → roteamento) definiu **quais campos a tela mostra**: a coluna MOTIVO dos pods, a coluna ENDPOINT dos services e a ordem dos painéis. A correção feita na triagem durante a matriz de roteamento (pod `1/1 Ready` com Service sem endpoint é problema de roteamento) é exatamente o caso que a tela mostra na evidência `04-nyx-stg-sem-endpoint.svg`.
