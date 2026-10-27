# Tasks

> Transcrição do que foi feito em 2026-10-08 (commit "fix(ticket-03): marcar como nao_verificado todo dado que nao foi coletado").

## 1. Coleta

- [x] 1.1 Detectar o systemd por `test -d /run/systemd/system` e conferir o exit code de `list-units` — verificado: teste `test_servicos_proibidos_nao_verificado`
- [x] 1.2 Conferir o exit code de `ss`, `/proc/swaps`, `authorized_keys`, `os-release` e `uname`; falha devolve `None` — verificado: testes `TestFalhasPontuais`

## 2. Auditoria e evidência

- [x] 2.1 Transformar `None` em `nao_verificado` com motivo em todas as regras — verificado: 13 testes passam; a versão anterior falha em 10
- [x] 2.2 Executar por SSH real na VM mínima (sem systemd e sem `ss`) com a versão anterior e a corrigida — verificado: `saida/evidencia/revisao-vm-minima-*`
