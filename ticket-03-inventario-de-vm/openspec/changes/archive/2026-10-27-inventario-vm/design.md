# Design

> Change reconstituída de `spec/spec-decisoes.md` (2026-09-17). As decisões estão registradas em detalhe nos ADRs de `docs/adr/`.

## Context

VMs sem agente, acesso só por SSH com chave, ferramenta rodando na estação de quem opera, coleta com usuário comum (ver proposal.md).

## Goals / Non-Goals

**Goals:**
- Um comando de leitura por item coletado, com fallback onde existir.
- Comparação determinística: o mesmo estado do host produz o mesmo veredito.

**Non-Goals:**
- Paralelismo entre hosts, integração com o Roster, remediação, firewall.

## Decisions

- **SSH via paramiko** em vez do binário `ssh` por subprocess: exceções tipadas por tipo de falha e código de saída por comando. (ADR-001)
- **Python 3** em vez de Go ou shell: mesma linguagem do time, testes simples. (ADR-003)
- **Falta de privilégio vira `nao_verificado`** em vez de abortar: o caso típico é `sshd -T` com usuário comum. (ADR-002)
- **Códigos 0/1/2/3** por categoria de resultado. (ADR-004)
- **Porta pública** = bind em `0.0.0.0`, `::` ou `*`; qualquer outro endereço é interno.
- **Chave da plataforma** = comentário da linha em `authorized_keys` contém `metacortex-platform`.
- **Versões** comparadas como tuplas dos três primeiros grupos numéricos.

## Risks / Trade-offs

- [Host key aceita no primeiro contato (`AutoAddPolicy`)] → aceitável no laboratório; produção deve usar `RejectPolicy` com `known_hosts`.
- [Serviços em `activating` logo após boot aparecem como ausentes] → rodar a auditoria em hosts estáveis; registrado na curadoria.
