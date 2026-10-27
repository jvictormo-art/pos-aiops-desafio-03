# Proposal

> **Change reconstituída.** O ciclo original (2026-09-17) foi feito com documentos próprios em `spec/` (proposta, decisões, comportamento, tarefas, arquivo final; commit "Add ferramenta metacortex-inventario e entregas do Ticket 03"), sem a CLI do OpenSpec. Em 2026-10-27 o conteúdo foi transcrito para esta change e arquivado com `openspec archive`, para que a spec principal em `openspec/specs/` reflita a versão 1.0 e as changes seguintes possam ser deltas sobre ela. Nenhum requisito foi acrescentado na transcrição.

## Why

O Roster é mantido à mão e acumula drift: hosts que mudaram de papel, agentes nunca registrados, chaves SSH esquecidas. Ninguém sabe quantas VMs estão fora do padrão, e as VMs não têm agente; o único acesso comum é SSH com chave.

## What Changes

- Nova CLI `inventario.py` que audita **uma** VM por SSH, da máquina de quem opera, só com comandos de leitura.
- Coleta de identificação, SO, kernel, serviços (`service` e `socket`), swap, portas em escuta, chaves SSH autorizadas, login de root efetivo e NTP.
- Comparação com `baseline.yaml` em três vereditos: `conforme`, `desvio` (com severidade do baseline) e `nao_verificado` (com motivo).
- Saída em JSON e Markdown a partir do mesmo dado; códigos de saída 0/1/2/3 para pipeline.

## Capabilities

### New Capabilities
- `inventario-vm`: auditoria de uma VM por SSH contra o baseline do parque, com inventário, conformidade e relatório.

### Modified Capabilities

## Impact

- Código novo em `ferramenta/` (`inventario.py`, `baseline.yaml`, `requirements.txt`).
- Dependências: `paramiko`, `PyYAML`.
- Nenhum sistema existente é alterado; o Roster consumirá o JSON quando existir.
