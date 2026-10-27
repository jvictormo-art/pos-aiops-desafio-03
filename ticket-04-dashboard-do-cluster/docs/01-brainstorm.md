# Brainstorm de escopo — metacortex-dashboard

> **Origem deste documento.** O brainstorm aconteceu em 2026-09-17, na sessão do Claude Code em que o projeto foi concebido, e o resultado foi registrado direto em `spec/proposta.md` e `spec/spec-decisoes.md` (commit "Add metacortex-dashboard e entregas do Ticket 04"). Este arquivo **reconstitui** em 2026-10-27, como documento próprio, as perguntas e alternativas que levaram àquela proposta, porque a revisão pediu cada etapa do arco como um documento separado. O que foi acrescentado na reconstituição está marcado.

---

## O problema

Toda triagem começa com a mesma sequência de seis a dez comandos (`kubectl get pods`, `get deploy`, `get svc`, `get endpoints`, `get events`, repetidos por namespace) só para montar o retrato do namespace. Isso consome os primeiros minutos de cada chamado antes de a investigação começar.

## Restrições que vieram prontas

- Roda na máquina de quem opera, com o kubeconfig dela, lendo **só o contexto corrente**, no momento em que sobe.
- Multicluster fora do escopo: sem seletor de cluster, sem trocar de contexto por dentro.
- **Só leitura**, com a garantia visível no projeto (código, configuração ou permissões), não só na intenção.
- Tem de se comportar quando o ambiente falha: cluster que não responde, credencial expirada, permissão negada para um tipo de recurso.
- Não substitui o terminal: encurta os primeiros minutos.

## Perguntas levantadas

| # | Pergunta | Para onde foi |
|---|---|---|
| 1 | TUI, web local ou outra coisa? Em que linguagem? | [ADR-001](./adr/ADR-001-linguagem-e-stack.md) |
| 2 | Cliente oficial, `kubectl` como subprocesso ou HTTP direto? | [ADR-002](./adr/ADR-002-acesso-a-api-do-kubernetes.md) |
| 3 | Sob demanda, intervalo fixo ou watch? | [ADR-003](./adr/ADR-003-atualizacao-da-tela.md) |
| 4 | `Endpoints` ou `EndpointSlice`? | [ADR-004](./adr/ADR-004-fonte-dos-endpoints.md) |
| 5 | O que entra na primeira fatia? | [ADR-005](./adr/ADR-005-recorte-da-primeira-fatia.md) |
| 6 | Como tornar "só leitura" verificável, e não só prometido? | [ADR-006](./adr/ADR-006-garantia-de-somente-leitura.md) |
| 7 | Campo ausente é diferente de campo vazio: como a tela mostra cada caso? | TRD, seção "Ausência de campo" |
| 8 | Um painel sem permissão derruba a tela? | Não: cada painel trata o próprio erro (TRD, "Falhas") |
| 9 | O quanto a tela pode afirmar sobre saúde? *(pergunta do enunciado respondida só na revisão 2)* | [ADR-007](./adr/ADR-007-o-que-a-tela-afirma-sobre-saude.md) |

## Ideias descartadas

Registradas em 2026-09-17:

| Ideia | Por que saiu |
|---|---|
| Seletor de cluster na tela | Fora do escopo pelo enunciado; troca de contexto é feita por fora |
| Métricas de CPU/memória (metrics-server) | O componente não é garantido no cluster (e não está no `kind-metacortex-lab`) |
| Ações a partir da tela (reiniciar pod, escalar) | Viola o invariante de leitura |
| Busca global através de todos os painéis | Tipos de objeto diferentes em espaços de nome diferentes; resultado confuso |

Acrescentada na reconstituição de 2026-10-27:

| Ideia | Por que não serve |
|---|---|
| Usar `k9s` ou o Kubernetes Dashboard oficial | O `k9s` faz escrita (delete, scale) por padrão; o modo `--readonly` é uma flag de quem roda, não uma propriedade verificável do projeto; o Dashboard oficial roda dentro do cluster, não na estação de quem opera |

## O que saiu do brainstorm

Uma TUI em Python que lê o contexto corrente com o cliente oficial, atualiza a cada 5 segundos, mostra os cinco objetos mínimos do enunciado com filtro e busca, e trata cada painel de forma independente para continuar útil quando parte do acesso falha. Escopo no [PRD](./02-PRD.md); "como" no [TRD](./03-TRD.md) e nos ADRs.
