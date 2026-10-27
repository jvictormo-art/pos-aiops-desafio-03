# Proposal

> **Change reconstituída.** A correção foi feita em 2026-10-08 (commit "fix(ticket-03): marcar como nao_verificado todo dado que nao foi coletado") a partir da revisão 1, sem passar pela CLI do OpenSpec. Em 2026-10-27 foi transcrita para esta change e arquivada para manter a spec principal fiel ao comportamento entregue.

## Why

A revisão 1 rodou a ferramenta numa VM sem systemd em execução e sem o comando `ss`, e recebeu `servicos.proibidos` e as duas regras de porta como `conforme`. A detecção do systemd aceitava o exit 1 de `systemctl is-system-running` (que é o `offline` de um host sem systemd) e nenhum coletor conferia o código de saída: saída vazia virava "nada encontrado".

## What Changes

- Todo comando de coleta tem o código de saída conferido; comando que falha ou não existe produz "dado não coletado", nunca lista vazia.
- A regra "dado não coletado vira `nao_verificado`" deixa de valer só para falta de privilégio e passa a valer para qualquer dado não coletado: serviços, portas, swap, chaves SSH, SO e kernel.
- O systemd passa a ser detectado por `/run/systemd/system`.

## Capabilities

### New Capabilities

### Modified Capabilities
- `inventario-vm`: o requisito "Dado não coletado" passa a cobrir qualquer falha de coleta, não só a de privilégio.

## Impact

- `ferramenta/inventario.py` (coletores e auditoria), `ferramenta/test_inventario.py` (13 testes novos), `ferramenta/Dockerfile.test-vm-minima` (VM sem systemd e sem `ss`).
