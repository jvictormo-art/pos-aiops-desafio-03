# ADR-006 — Garantia de somente leitura visível no projeto

| Campo | Valor |
|---|---|
| Status | aceito (ampliado em 2026-10-27, revisão 2) |
| Data | 2026-09-17 (origem: `spec/spec-decisoes.md`, "Como a garantia de leitura fica visível no projeto") |
| Exigência do enunciado | "Essa garantia precisa estar visível no projeto (código, configuração ou permissões), não só na intenção de quem escreveu" |

## Contexto

A aplicação fala com clusters de produção usando o kubeconfig de quem opera, que muitas vezes tem permissão de escrita. Na versão 1.0, a garantia era estrutural no código (a única classe que fala com a API, `ClusterReader`, só chama `list_*`/`read_*`) e verificada por um `grep` descrito numa tarefa, que ninguém roda automaticamente.

## Decisão

A garantia fica em **três camadas**, cada uma verificável por quem não escreveu o código:

1. **Código:** só `ClusterReader` fala com a API, e só com verbos de leitura.
2. **Teste automático** (`dashboard/test_somente_leitura.py`): percorre a árvore sintática de todos os `.py` do dashboard e falha se encontrar chamada a qualquer método de escrita do cliente (`create_*`, `patch_*`, `replace_*`, `delete_*`, `connect_*`). Também confere que a ClusterRole versionada só concede `get`, `list` e `watch`.
3. **Permissão:** `rbac/dashboard-leitura.yaml`, uma ClusterRole só com `get`/`list`/`watch` nos recursos que a tela usa, para quem quiser rodar o dashboard com uma identidade que **não consegue** escrever, mesmo que o código mudasse.

## Alternativas consideradas

### A. Só a convenção no código (versão 1.0)

- **Ganha:** nada a manter além do próprio código.
- **Perde:** a garantia depende de alguém rodar o `grep` e de ninguém escrever um verbo de escrita "só desta vez". É "a intenção de quem escreveu", que o enunciado descarta.

### B. Só RBAC (identidade sem permissão de escrita)

- **Ganha:** a garantia mais forte possível: o apiserver recusa a escrita.
- **Perde:** depende de cada operador configurar uma identidade separada; na prática, o dashboard roda com o kubeconfig do dia a dia, que escreve. Sozinha, a camada de permissão não protege o caso comum.

### C. Wrapper que intercepta o cliente e bloqueia métodos de escrita em tempo de execução

- **Ganha:** protege mesmo contra código novo que esqueça a regra.
- **Perde:** é um monkeypatch do cliente oficial, que quebra a cada versão e falha em produção, não no CI. O teste estático pega o mesmo erro antes de chegar ao operador.

### D. Código + teste + ClusterRole (escolhida)

- **Ganha:** o erro é pego no teste antes de chegar à tela; quem quer a garantia máxima usa a ClusterRole; as três camadas estão no repositório, visíveis.
- **Perde:** o teste é estático: pega chamadas diretas, não uma chamada montada dinamicamente (`getattr(api, "delete_" + x)`). O teste também falha nesse padrão, proibindo `getattr` com nome montado em `k8s_reader.py`.

## Consequências

- O cenário `platform-ro` dos testes de falha usa uma Role ainda mais restrita (sem `deployments` nem `services`), derivada desta ClusterRole, versionada em `laboratorio/cenarios-de-falha.sh`.
