# ADR-002 — Dado que não pôde ser coletado vira `nao_verificado`

| Campo | Valor |
|---|---|
| Status | aceito (revisado em 2026-10-08 e 2026-10-27) |
| Data | 2026-09-17 (registrado como ADR em 2026-10-27; origem: `spec/spec-decisoes.md`, seção "O que acontece quando um dado não pode ser coletado") |
| Decisão exigida pelo enunciado | "O que acontece quando um dado não pode ser coletado" |

## Contexto

A coleta roda com usuário comum. Alguns dados exigem privilégio (`sshd -T`), outros dependem de componentes que podem não existir no host (systemd em execução, `ss`, `timedatectl`). O enunciado diz que reportar isso como conforme seria falso e que abortar a execução inteira não ajudaria ninguém.

## Decisão

1. **Todo comando tem o código de saída conferido.** Comando que falha ou não existe faz o coletor devolver `None`, nunca um valor vazio que possa ser lido como "nada encontrado".
2. **`None` vira `nao_verificado` com `motivo`**, em todas as regras que dependem daquele dado. Nunca `conforme`, nunca `desvio`.
3. **Uma falha inesperada num item não aborta a execução** (revisão 2): o coletor é isolado; a exceção vira `nao_verificado` com motivo `falha inesperada na coleta (<tipo>)` e os outros itens seguem.
4. **Falha de conexão é outra coisa:** sem conexão não há o que auditar; a execução termina com código 2 e nenhuma saída em stdout ([ADR-004](./ADR-004-codigos-de-saida.md)).
5. Detectar o systemd por `test -d /run/systemd/system` (o mesmo teste do `sd_booted()`), não pelo código de saída de `systemctl is-system-running`.

## Alternativas consideradas

### A. Abortar a execução quando um dado falta

- **Ganha:** simplicidade; nenhum relatório parcial.
- **Perde:** um único `sshd -T` sem privilégio derrubaria todo inventário com usuário comum, que é o modo normal de operar. É o que o enunciado descarta explicitamente.

### B. Tratar dado ausente como vazio e seguir a comparação — *o comportamento real da versão 1.0*

- **Ganha:** nenhum caso especial no código.
- **Perde:** é exatamente o defeito que a revisão 1 encontrou: numa VM sem systemd e sem `ss`, lista vazia de serviços virou "nenhum serviço proibido" e lista vazia de portas virou "nenhuma porta exposta", ou seja, `conforme` sem nada ter sido verificado.

### C. Elevar privilégio (`sudo -n`) para não ter `nao_verificado` — *avaliada na revisão 2 (2026-10-27)*

- **Ganha:** relatório mais completo onde houver sudo sem senha.
- **Perde:** o usuário de auditoria passa a precisar de privilégio, o que contraria o PRD; e onde não houver sudo, o problema volta igual.

### D. `nao_verificado` com motivo (escolhida)

- **Ganha:** o relatório separa o que foi verificado do que não foi, diz por quê, e continua útil para todo o resto.
- **Perde:** o consumidor (Roster, pipeline) precisa tratar um terceiro estado; código 0 passa a significar "nenhum desvio confirmado", não "tudo verificado".

## Consequências

- O código 0 convive com `nao_verificado`. Quem precisar de cobertura total deve olhar `resumo.nao_verificado`.
- Arquivo `authorized_keys` **inexistente** é dado coletado (não há chaves) e leva a desvio; arquivo **existente e ilegível** é `nao_verificado`.
