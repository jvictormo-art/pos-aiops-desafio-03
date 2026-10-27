# Brainstorm de escopo — metacortex-inventario

> **Origem deste documento.** O brainstorm aconteceu em 2026-09-17, na sessão do Claude Code em que o projeto foi concebido, e o resultado foi registrado direto em `spec/proposta.md` e `spec/spec-decisoes.md` (commit "Add ferramenta metacortex-inventario e entregas do Ticket 03"). Este arquivo **reconstitui** em 2026-10-27, como documento próprio, as perguntas e alternativas que levaram àquela proposta, porque a revisão pediu cada etapa do arco como um documento separado. O conteúdo vem daqueles dois arquivos; o pouco que foi acrescentado na reconstituição está marcado como tal, e nada aqui é decisão nova.

---

## O problema, nas palavras de quem sofre com ele

- O Roster é mantido à mão e está desatualizado.
- Há hosts que mudaram de papel, agentes instalados e nunca registrados, chaves SSH que ficaram para trás.
- Ninguém consegue dizer quantas VMs estão fora do padrão.

## Restrições que vieram prontas

- As VMs **não têm agente** e nenhum será instalado. O único acesso comum a todas é SSH com chave.
- A ferramenta roda na máquina de quem opera.
- Só leitura: nada é instalado, escrito ou corrigido no host.
- A chave privada é credencial: não pode vazar em saída, log ou erro.
- Duas saídas do mesmo dado: JSON (Roster) e Markdown (plantão).

## Perguntas levantadas

| # | Pergunta | Para onde foi |
|---|---|---|
| 1 | Auditar um host por vez ou o parque inteiro? | PRD: um host por execução; paralelismo fica fora do MVP |
| 2 | Como falar com o host: binário `ssh` do sistema ou biblioteca? | [ADR-001](./adr/ADR-001-comunicacao-ssh-com-paramiko.md) |
| 3 | Em que linguagem? | [ADR-003](./adr/ADR-003-linguagem-python.md) |
| 4 | O que fazer quando um dado não pode ser coletado (falta de privilégio, comando ausente)? | [ADR-002](./adr/ADR-002-dado-nao-coletado-vira-nao-verificado.md) |
| 5 | Como o resultado entra num pipeline? | [ADR-004](./adr/ADR-004-codigos-de-saida.md) |
| 6 | O que é "porta pública"? | TRD: wildcard (`0.0.0.0`, `::`, `*`) é público; qualquer endereço específico é interno |
| 7 | Como saber se uma chave foi "emitida pela plataforma"? | TRD: o comentário da linha em `authorized_keys` contém `metacortex-platform` |
| 8 | Login de root: ler `sshd_config` ou a configuração efetiva? | TRD: `sshd -T` (efetiva); sem privilégio vira `nao_verificado` |
| 9 | Usuário root para coletar tudo? | Descartado: a coleta roda com usuário comum, e o que exigir privilégio é reportado como tal |
| 10 | Integrar direto com o Roster? | Fora do escopo: o Roster ainda não existe; o JSON é o contrato |
| 11 | Corrigir os desvios encontrados? | Fora do escopo por definição: a ferramenta só lê |

## Ideias descartadas

Registradas em 2026-09-17 (`spec/proposta.md` e `spec/spec-decisoes.md`):

| Ideia | Por que saiu |
|---|---|
| Shell puro com o binário `ssh` | Parsear saídas e comparar versões em shell é frágil e difícil de testar isolado |
| Go com `x/crypto/ssh` | Binário portável, mas mais verboso para os comandos compostos; o time mantém Python |
| Coletar como root | A operação padrão usa usuário comum; o que exigir privilégio é reportado |
| Verificar firewall/regras de rede | Exige olhar o host de fora; SSH só vê o lado de dentro |
| Vários hosts em paralelo | Complexidade de saída fora do MVP |

Acrescentadas na reconstituição de 2026-10-27, para deixar explícito o que o enunciado já excluía:

| Ideia | Por que não serve |
|---|---|
| Agente leve (osquery, textfile do node_exporter) | O enunciado proíbe agente nas VMs |
| Ansible com `gather_facts` | Exige Python no host remoto e um inventário; é uma dependência inteira para nove comandos de leitura |
| `sudo` para não ter `nao_verificado` | O enunciado trata a falta de privilégio como o caso típico a reportar, não a contornar |

## O que saiu do brainstorm

Um escopo pequeno e fechado: **um host por execução, nove itens coletados, comparação regra a regra com o baseline, dois formatos de saída e quatro códigos de saída**. Esse escopo está no [PRD](./02-PRD.md); o "como" está no [TRD](./03-TRD.md) e nos ADRs.
