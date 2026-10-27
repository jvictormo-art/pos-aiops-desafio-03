# PRD — metacortex-inventario

| Campo | Valor |
|---|---|
| Versão | 1.2 |
| Status | aprovado |
| Histórico | 1.0 (2026-09-17, origem: `spec/proposta.md`, commit "Add ferramenta metacortex-inventario e entregas do Ticket 03") · 1.1 (2026-10-08, revisão 1: dado não coletado) · 1.2 (2026-10-27, revisão 2: aderência ao formato do enunciado) |

> A versão 1.0 deste PRD foi escrita como `spec/proposta.md`. Em 2026-10-27 o conteúdo foi movido para este documento próprio, sem mudar requisitos; as mudanças das versões 1.1 e 1.2 vêm dos ciclos de revisão e estão nas changes do OpenSpec em [`../openspec/changes/archive/`](../openspec/changes/archive/).

---

## Problema

O Roster manual acumula drift silencioso: host que mudou de papel e não teve o registro atualizado, chave SSH inserida durante incidente e nunca catalogada, serviço proibido que sobreviveu a uma migração. Quando Segurança pergunta quantas VMs estão fora do padrão, a resposta honesta é "não sei".

O parque não tem agente nas VMs. O que existe em toda VM é acesso por chave SSH, e é com ele que a ferramenta trabalha.

## Usuários

| Quem | Para quê |
|---|---|
| Plantão (operação) | Ler no terminal, às 3h, o que está fora do padrão num host |
| Roster (sistema) | Consumir o JSON e manter o inventário atualizado |
| Pipeline (CI/cron) | Decidir pelo código de saída se houve desvio |

## O que a ferramenta faz

1. Recebe o endereço de uma VM, o usuário e a chave privada.
2. Conecta por SSH, da máquina de quem opera.
3. Coleta o estado real do host: identificação, SO, kernel, serviços (distinguindo `service` de `socket`), swap, portas em escuta (porta, bind, processo), chaves SSH autorizadas, login de root efetivo e sincronização de tempo.
4. Compara com o `baseline.yaml`: **uma entrada por regra do baseline**, com regra, esperado, encontrado e veredito (`conforme`, `desvio` com severidade, ou `nao_verificado` com motivo).
5. Produz JSON e Markdown a partir do mesmo dado.

## Requisitos não funcionais

- **Só leitura.** Nada é instalado, escrito ou corrigido no host auditado.
- **Credencial protegida.** A chave privada não aparece na saída, no log nem em mensagem de erro.
- **Determinismo.** Duas execuções seguidas devolvem o mesmo veredito para cada regra; só o instante da coleta muda.
- **Pipeline.** O código de saída distingue conforme, desvio, falha de conexão e erro de uso.
- **Sem stack trace.** Toda falha prevista vira uma mensagem de uma linha que explica o que houve.

## Critérios de pronto

| # | Critério | Como é verificado |
|---|---|---|
| CP1 | Um host conforme sai sem nenhum desvio (exit 0) | Execução contra a VM Ubuntu 24.04 conforme |
| CP2 | Um host com desvios sai com cada desvio classificado pela severidade do baseline (exit 1) | Execução contra a VM de teste com desvios propositais |
| CP3 | Regra não verificável aparece como `nao_verificado`, separada de `conforme` | Usuário sem privilégio (`ssh.login_de_root`) e VM sem systemd e sem `ss` |
| CP4 | Host inalcançável falha com mensagem que explica o que houve, sem stack trace e sem ser confundido com host conforme (exit 2) | Endereço errado, chave recusada e SSH fora do ar |
| CP5 | A segunda execução devolve o mesmo resultado | Duas execuções seguidas, conformidade e resumo comparados |
| CP6 | A chave privada não aparece em nenhuma saída | Busca do conteúdo da chave em stdout e stderr de todas as execuções |

As evidências de cada critério estão em [`../saida/evidencia/`](../saida/evidencia/).

## Fora do escopo

| Item | Motivo |
|---|---|
| Vários hosts em paralelo | Complexidade de saída fora do MVP; um laço no shell resolve enquanto isso |
| Integração direta com o Roster | O Roster ainda não existe; o JSON é o contrato |
| Remediação de desvios | A ferramenta só lê |
| Firewall e regras de rede | Exige olhar o host de fora |
| Coleta como root ou com `sudo` | A coleta roda com usuário comum; o que exige privilégio é reportado como `nao_verificado` |
