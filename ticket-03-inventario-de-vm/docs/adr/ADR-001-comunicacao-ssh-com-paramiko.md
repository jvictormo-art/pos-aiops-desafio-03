# ADR-001 — Comunicação com o host: SSH via paramiko

| Campo | Valor |
|---|---|
| Status | aceito |
| Data | 2026-09-17 (registrado como ADR em 2026-10-27; origem: `spec/spec-decisoes.md`, seção "Biblioteca SSH") |
| Decisão exigida pelo enunciado | "Como a ferramenta se comunica com o host remoto" |

## Contexto

As VMs não têm agente e nenhum será instalado. O único acesso comum a todo o parque é SSH com chave. A ferramenta roda na máquina de quem opera, recebe endereço, usuário e chave, e precisa: executar comandos de leitura, obter **stdout e código de saída** de cada um (a revisão 1 mostrou que o código de saída é indispensável) e distinguir com precisão os tipos de falha de conexão, para a mensagem dizer o que houve.

## Decisão

Usar a biblioteca **paramiko** (SSH2 em Python puro): uma conexão por execução, um `exec_command` por item coletado, lendo `stdout` e `recv_exit_status()`. Host key com `AutoAddPolicy`.

## Alternativas consideradas

### A. Binário `ssh` do sistema via `subprocess`

- **Ganha:** nenhuma dependência Python; respeita `~/.ssh/config`, agentes e `ProxyJump` sem código.
- **Perde:** cada comando é um processo novo; os tipos de falha chegam como texto no stderr do `ssh`, que muda entre versões do OpenSSH, e distinguir "chave recusada" de "SSH fora do ar" vira comparação de strings. A chave passaria por argumento de linha de comando, visível em `ps`.

### B. Ansible (módulo `command`/`setup`) — *acrescentada na reconstituição de 2026-10-27*

- **Ganha:** inventário, paralelismo e fatos prontos.
- **Perde:** exige Python no host remoto e transforma uma CLI de nove comandos numa dependência inteira, com saída e erros no formato do Ansible, não no do enunciado.

### C. paramiko (escolhida)

- **Ganha:** exceções tipadas por falha (`AuthenticationException`, `socket.gaierror`, `ConnectionRefusedError`, `socket.timeout`), o que dá mensagens precisas; código de saída de cada comando; a chave é carregada pela biblioteca e o código da ferramenta nunca toca no conteúdo.
- **Perde:** não lê `~/.ssh/config` (bastion/`ProxyJump` exigiriam código); uma dependência a instalar (`requirements.txt`).

## Consequências

- `AutoAddPolicy` aceita a host key no primeiro contato: adequado ao laboratório, inadequado à produção. O caminho para produção é `RejectPolicy` com `known_hosts` populado pelo Construct. Fica registrado como pendência consciente, não como esquecimento.
- Hosts atrás de bastion não são alcançáveis nesta versão.
