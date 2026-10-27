# Ticket 03 — Inventário e drift de VM por SSH

`metacortex-inventario`: CLI que audita uma VM por SSH, sem agente e sem alterar o host, e compara o que encontra com o `baseline.yaml` do parque.

## Onde está cada item do Entregue

| Item do enunciado | Onde |
|---|---|
| **Arco de spec: brainstorm** | [`docs/01-brainstorm.md`](./docs/01-brainstorm.md) |
| **PRD** | [`docs/02-PRD.md`](./docs/02-PRD.md) |
| **TRD** | [`docs/03-TRD.md`](./docs/03-TRD.md) |
| **ADRs** | [`docs/adr/`](./docs/adr/) |
| ↳ Como a ferramenta se comunica com o host | [ADR-001 — SSH via paramiko](./docs/adr/ADR-001-comunicacao-ssh-com-paramiko.md) |
| ↳ O que acontece quando um dado não pode ser coletado | [ADR-002 — `nao_verificado` com motivo](./docs/adr/ADR-002-dado-nao-coletado-vira-nao-verificado.md) |
| ↳ Em que linguagem, e por quê | [ADR-003 — Python 3](./docs/adr/ADR-003-linguagem-python.md) |
| ↳ Código de saída para pipeline | [ADR-004](./docs/adr/ADR-004-codigos-de-saida.md) |
| ↳ Uma entrada por regra do baseline | [ADR-005](./docs/adr/ADR-005-uma-entrada-por-regra.md) |
| **OpenSpec: proposta, tarefas, specs e o que foi arquivado** | [`openspec/`](./openspec/): spec vigente em [`openspec/specs/inventario-vm/spec.md`](./openspec/specs/inventario-vm/spec.md); changes arquivadas em [`openspec/changes/archive/`](./openspec/changes/archive/), cada uma com `proposal.md`, `design.md`, `tasks.md` e `specs/` |
| **Código** | [`ferramenta/inventario.py`](./ferramenta/inventario.py), [`ferramenta/baseline.yaml`](./ferramenta/baseline.yaml), [`ferramenta/requirements.txt`](./ferramenta/requirements.txt) |
| **Testes** | [`ferramenta/test_inventario.py`](./ferramenta/test_inventario.py): 27 testes (`python3 -m unittest test_inventario.py`) |
| **Evidência de execução real** | [`saida/evidencia/`](./saida/evidencia/), gerada por [`gerar-evidencias.sh`](./saida/evidencia/gerar-evidencias.sh); cada arquivo registra comando, código de retorno, stdout e stderr |
| ↳ Saída nos dois formatos | `01` (JSON) e `02` (Markdown) do host conforme; `04`/`05` do host com desvios |
| ↳ Código de retorno | Em todos os arquivos: conforme → 0, com desvios → 1, inalcançável → 2, erro de uso → 3 |
| ↳ Host inalcançável | `08` endereço que não resolve · `09` IP sem resposta · `10` chave recusada · `11` SSH fora do ar |
| ↳ Segunda execução com o mesmo resultado | `01` e `03`, comparados em `14-segunda-execucao-mesmo-resultado.txt` |
| **Curadoria** | [`saida/curadoria.md`](./saida/curadoria.md): onde a spec foi corrigida e o que o agente entendeu diferente |

## Critérios de pronto × evidência

| Critério do enunciado | Evidência | Resultado |
|---|---|---|
| Um host conforme sai sem nenhum desvio | `01`, `02` (VM Ubuntu 24.04 real) | 0 desvio, código 0 |
| Host com desvios sai com cada desvio classificado pela severidade | `04`, `05` | 4 desvios (2 crítico, 1 alto, 1 médio), código 1 |
| Regra não verificável aparece como `nao_verificado`, separada de `conforme` | `02` (`ssh.login_de_root`), `06`/`07` (sem systemd, sem `ss`) | motivo em cada regra |
| Host inalcançável falha com mensagem que explica o que houve, sem stack trace | `08` a `11` | código 2, stdout vazio, uma linha em stderr |
| A segunda execução devolve o mesmo resultado | `14` | conformidade e resumo idênticos |
| A chave privada não aparece | `15` | conteúdo ausente de todas as evidências |

## Hosts usados na evidência

| Host | O que é | Como reproduzir |
|---|---|---|
| `192.168.64.2` | VM Ubuntu 24.04 (Lima, kernel 6.8), preparada conforme o baseline | `limactl start --name=metacortex-vm --network=vzNAT template:ubuntu-24.04` + [`ferramenta/preparar-vm-conforme.sh`](./ferramenta/preparar-vm-conforme.sh) |
| `127.0.0.1:2222` | Ubuntu 22.04 com systemd e desvios propositais | [`ferramenta/Dockerfile.test-vm`](./ferramenta/Dockerfile.test-vm) |
| `127.0.0.1:2223` | Ubuntu 22.04 sem systemd em execução e sem `ss` | [`ferramenta/Dockerfile.test-vm-minima`](./ferramenta/Dockerfile.test-vm-minima) |

## Como rodar

```bash
cd ferramenta
pip3 install -r requirements.txt
python3 inventario.py --host <ip> --user <usuario> --key <chave_privada> [--format json|md|both]
```

## Histórico

Os documentos de spec da versão 1.0 foram escritos em `spec/` (proposta, decisões, comportamento, tarefas, arquivo final; commit "Add ferramenta metacortex-inventario e entregas do Ticket 03"). A revisão 2 pediu cada etapa do arco como documento próprio e o ciclo do OpenSpec: o conteúdo de `spec/` foi migrado para `docs/` e para as changes reconstituídas do OpenSpec, que o declaram no cabeçalho. A change da revisão 2 foi feita com a CLI do OpenSpec (`openspec` 1.15.0), com spec e tarefas escritas antes do código.

- **Agente:** Claude Code · **Modelos:** Claude Opus 4.8 / Sonnet 4.6 (v1.0) e Claude Opus 5.5 (revisões)
