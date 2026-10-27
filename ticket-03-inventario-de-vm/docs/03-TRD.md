# TRD — metacortex-inventario

| Campo | Valor |
|---|---|
| Versão | 1.2 |
| Status | aprovado |
| Histórico | 1.0 (2026-09-17, origem: `spec/spec-decisoes.md` e `spec/spec-comportamento.md`, commit "Add ferramenta metacortex-inventario e entregas do Ticket 03") · 1.1 (2026-10-08, revisão 1) · 1.2 (2026-10-27, revisão 2) |
| Decisões | [ADR-001](./adr/ADR-001-comunicacao-ssh-com-paramiko.md) · [ADR-002](./adr/ADR-002-dado-nao-coletado-vira-nao-verificado.md) · [ADR-003](./adr/ADR-003-linguagem-python.md) · [ADR-004](./adr/ADR-004-codigos-de-saida.md) · [ADR-005](./adr/ADR-005-uma-entrada-por-regra.md) |

> A versão 1.0 foi escrita em dois arquivos (`spec/spec-decisoes.md` e `spec/spec-comportamento.md`). Em 2026-10-27 eles foram fundidos neste TRD e as decisões viraram ADRs próprios. Onde a revisão mudou o comportamento, a seção indica a versão.

---

## 1. Visão geral

```
operador ──SSH (paramiko)──▶ VM auditada
   │                           só comandos de leitura
   ▼
inventario.py
  ├─ SSHConexao   conecta, executa, devolve (stdout, exit code)
  ├─ Coletor      um método por item; comando que falha → None + motivo
  ├─ auditar()    baseline × inventário → uma entrada por regra
  └─ renderizar_json() / renderizar_markdown()   mesmo dado, dois formatos
```

Nada roda no host além dos comandos da seção 3. Não há agente, arquivo temporário nem `sudo`.

## 2. Interface

```
python3 inventario.py --host <ip|hostname> --user <usuario> --key <chave_privada>
                      [--baseline baseline.yaml] [--format json|md|both] [--porta 22]
```

Saída de dados em **stdout**; mensagens de erro em **stderr**, uma linha, sem stack trace. Com `--format both`, o JSON vem primeiro, depois `---`, depois o Markdown.

## 3. Coleta: comando por item

| Item | Comando | Falha → `nao_verificado` quando |
|---|---|---|
| Identificação | `hostname`; endereço = `--host`; instante = UTC no início da coleta | `hostname` falha: usa o endereço (não é regra do baseline) |
| SO | `. /etc/os-release && echo "$ID $VERSION_ID"` | exit ≠ 0 ou saída incompleta |
| Kernel | `uname -r` | exit ≠ 0 ou vazio |
| Serviços | `test -d /run/systemd/system`, depois `systemctl list-units --type={service,socket} --state=active --no-legend --plain --no-pager` | systemd não é o init em execução, ou `list-units` com exit ≠ 0 |
| Swap | `cat /proc/swaps` | exit ≠ 0 |
| Portas | `ss -tlnp` | `ss` ausente ou exit ≠ 0 |
| Chaves SSH | `test -e ~/.ssh/authorized_keys`, depois `cat` | arquivo existe mas não pode ser lido (arquivo inexistente = lista vazia, que é desvio) |
| Login de root | `sshd -T \| grep -i permitrootlogin` | sem privilégio para `sshd -T` (caso típico com usuário comum) |
| NTP | `timedatectl show --property=NTPSynchronized,NTPService`; reserva: `timedatectl status` | nenhuma das duas responde |

**Regra geral (1.1):** todo comando tem o código de saída conferido. Saída vazia de um comando que falhou nunca é lida como "nada encontrado". O exit code de `systemctl is-system-running` não serve para detectar o systemd: sem systemd em execução ele responde `offline` com exit 1, o mesmo código de `degraded`.

**Falha inesperada (1.2):** uma exceção dentro de um coletor (por exemplo, timeout de um comando) não aborta a execução. O item vira `None` com motivo `falha inesperada na coleta (<tipo>)` e os outros itens seguem.

## 4. Definições usadas na comparação

- **Endereço público:** bind em `0.0.0.0`, `::`, `*` ou vazio. Qualquer endereço específico (`10.x`, `127.0.0.1`, `127.0.0.53%lo`) é interno.
- **Chave emitida pela plataforma:** o comentário da linha de `authorized_keys` contém `metacortex-platform`. Chave sem comentário é não reconhecida.
- **Versão mínima:** tuplas dos três primeiros grupos numéricos (`5.15.0-118-generic` → `(5, 15, 0)`), comparadas elemento a elemento.
- **Serviço sem tipo no baseline:** `ssh` vale `ssh.service` nos ativos; `telnet.socket` já vem com o tipo nos proibidos.
- **Porta da rede interna sem escuta:** conforme. Não estar escutando não é exposição; a falta do processo é coberta por `servicos.ativos`.

## 5. Conformidade (1.2: uma entrada por regra)

Uma entrada para cada uma das 11 regras do baseline ([ADR-005](./adr/ADR-005-uma-entrada-por-regra.md)). Regras que listam vários itens (`servicos.ativos`, `servicos.proibidos`, `portas_em_escuta.somente_rede_interna`) agregam os itens numa entrada só e dizem no `encontrado` quais itens falharam.

| Regra | `esperado` | `encontrado` (exemplos) |
|---|---|---|
| `so.distribuicao` | `ubuntu` | `ubuntu` |
| `so.versao_minima` | `22.04` | `24.04` |
| `kernel.versao_minima` | `6.5` | `6.8.0-85-generic` |
| `servicos.ativos` | `ssh, containerd, node_exporter, chrony ativos` | `todos ativos` · `ausente: containerd, node_exporter` |
| `servicos.proibidos` | `telnet.socket, rpcbind.socket inativos` | `nenhum ativo` · `ativo: telnet.socket` |
| `swap.habilitado` | `false` | `false` · `true (4G)` |
| `portas_em_escuta.publicas_permitidas` | `apenas 22 em endereço público` | `nenhuma outra porta pública` · `8080 em 0.0.0.0` |
| `portas_em_escuta.somente_rede_interna` | `9100 na rede interna` | `9100 em 10.42.7.14` · `9100 em 0.0.0.0` · `9100 sem escuta` |
| `chaves_ssh.emitidas_por` | `todas emitidas por metacortex-platform` | `2 chave(s), todas da plataforma` · `não reconhecida(s): madrugada@laptop-do-dozer` |
| `ssh.login_de_root` | `false` | `false` · `true` · `null` |
| `ntp.sincronizado` | `true` | `true` · `false` |

Campos de cada entrada: `regra`, `esperado`, `encontrado`, `veredito`; `severidade` só quando `veredito = desvio` (vem do bloco `severidade` do baseline); `motivo` só quando `veredito = nao_verificado`.

## 6. Formatos de saída

**JSON**: o schema do enunciado: `host` (`endereco`, `hostname`, `coletado_em`), `inventario` (os nove itens; item não coletado vem `null`), `conformidade` e `resumo` (`conforme`, `desvio`, `nao_verificado`, `por_severidade`).

**Markdown (1.2: idêntico ao exemplo do enunciado)**:

```
# Inventário de <hostname> (<endereço>)
Coletado em <AAAA-MM-DD HH:MM> UTC · baseline v<versão>

## Desvios

| Severidade | Regra | Esperado | Encontrado |
|---|---|---|---|
(ordenado por severidade: crítico, alto, médio)

## Não verificado

| Regra | Motivo |
|---|---|

## Conforme
regra · regra · regra
```

- `## Desvios` aparece sempre (com `*Nenhum desvio encontrado.*` quando vazia); `## Não verificado` só quando há itens.
- O motivo é o mesmo do JSON, com acentuação no Markdown (`exige privilégio que o usuário da coleta não tem`), como no exemplo do enunciado.
- Ao final, uma linha de resumo (`N conforme · N desvio · N não verificado`), que o enunciado não proíbe e o plantão usa.

## 7. Códigos de saída ([ADR-004](./adr/ADR-004-codigos-de-saida.md))

| Código | Quando | stdout |
|---|---|---|
| 0 | Host alcançado, nenhum desvio (pode haver `nao_verificado`) | relatório |
| 1 | Host alcançado, pelo menos um desvio | relatório |
| 2 | Falha de conexão: endereço que não resolve, SSH fora do ar, timeout, chave recusada | vazio |
| 3 | Erro de uso: baseline inválido, arquivo da chave ausente ou ilegível, argumento faltando | vazio |

Mensagens da família 2 dizem **o que** houve: `endereço não resolve`, `conexão recusada na porta 22 (SSH fora do ar?)`, `tempo esgotado`, `autenticação recusada`. (1.2: antes, um arquivo de chave inexistente era reportado como "host inalcançável"; agora é erro de uso, código 3, verificado antes de conectar.)

## 8. Segurança

- **Chave privada:** o caminho vai direto para `paramiko.SSHClient.connect(key_filename=...)`; o código nunca lê o conteúdo. Mensagens de erro são reescritas sem o caminho nem o conteúdo da chave.
- **Host key:** `AutoAddPolicy` no MVP, porque a ferramenta não é interativa ([ADR-001](./adr/ADR-001-comunicacao-ssh-com-paramiko.md) registra o risco e o caminho para `RejectPolicy` com `known_hosts`).
- **Só leitura:** os comandos da seção 3 são os únicos enviados.

## 9. Determinismo

O invariante é **o mesmo veredito por regra e o mesmo resumo**, não o inventário bruto: num host que acabou de reiniciar, a lista de unidades pode mudar entre duas coletas (correção registrada na curadoria). `coletado_em` sempre muda.

## 10. Ambientes de teste

| Ambiente | Para quê |
|---|---|
| VM Ubuntu 24.04 (Lima, kernel 6.8, systemd real) preparada conforme o baseline | CP1: host conforme |
| `ferramenta/Dockerfile.test-vm` (Ubuntu 22.04 com systemd, desvios propositais) | CP2: desvios por severidade |
| `ferramenta/Dockerfile.test-vm-minima` (sem systemd em execução, sem `ss`) | CP3: `nao_verificado` |
| `ferramenta/test_inventario.py` (SSH simulado) | Regras de coleta e auditoria sem rede |
