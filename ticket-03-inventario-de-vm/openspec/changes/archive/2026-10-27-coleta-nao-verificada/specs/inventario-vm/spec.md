# Spec Delta

## MODIFIED Requirements

### Requirement: Dado não coletado
Todo dado que não pôde ser coletado — por falta de privilégio, porque o comando não existe no host ou porque o comando terminou com código de saída diferente de zero — SHALL levar as regras que dependem dele a `nao_verificado` com um `motivo`, e SHALL NOT ser interpretado como valor vazio, `conforme` ou `desvio`. A execução SHALL continuar para as demais regras.

#### Scenario: sshd -T sem privilégio
- **WHEN** o usuário da coleta não consegue executar `sshd -T`
- **THEN** `ssh.login_de_root` sai como `nao_verificado` com motivo "exige privilegio que o usuario da coleta nao tem", e as outras regras são avaliadas normalmente

#### Scenario: Host sem systemd em execução
- **WHEN** o binário `systemctl` existe mas o systemd não é o init em execução (`is-system-running` responde `offline` com exit 1)
- **THEN** `servicos.ativos` e `servicos.proibidos` saem como `nao_verificado` com motivo "systemd nao disponivel ou nao acessivel", e não como `conforme`

#### Scenario: Host sem o comando ss
- **WHEN** o comando `ss` não existe no host
- **THEN** `portas_em_escuta.publicas_permitidas` e `portas_em_escuta.somente_rede_interna` saem como `nao_verificado` com motivo "comando ss nao disponivel ou falhou"

#### Scenario: authorized_keys inexistente versus ilegível
- **WHEN** o arquivo `~/.ssh/authorized_keys` não existe
- **THEN** a lista de chaves é vazia e `chaves_ssh.emitidas_por` sai como `desvio`; e **WHEN** o arquivo existe mas não pode ser lido, **THEN** a regra sai como `nao_verificado`
