# Spec Delta

## MODIFIED Requirements

### Requirement: Conformidade com o baseline
A ferramenta SHALL produzir exatamente uma entrada de conformidade por regra do `baseline.yaml`, com a regra, o valor esperado, o valor encontrado e um veredito entre `conforme`, `desvio` e `nao_verificado`. Regras que listam vários itens SHALL agregar os itens numa única entrada: o veredito é `desvio` se algum item violar a regra, e o valor encontrado SHALL dizer quais itens a violam. Todo `desvio` SHALL trazer a severidade que o baseline atribui à regra, e o `resumo` SHALL somar o número de regras do baseline.

#### Scenario: Swap habilitado
- **WHEN** o host tem swap de 4G e o baseline exige swap desabilitado
- **THEN** a regra `swap.habilitado` sai como `desvio` com severidade `critico` e encontrado `true (4G)`

#### Scenario: Dois serviços obrigatórios ausentes
- **WHEN** `containerd` e `node_exporter` não estão ativos e `ssh` e `chrony` estão
- **THEN** existe uma única entrada `servicos.ativos`, com veredito `desvio`, severidade `alto` e encontrado `ausente: containerd, node_exporter`

#### Scenario: Host conforme
- **WHEN** o host atende a todas as regras que puderam ser verificadas
- **THEN** nenhuma entrada sai como `desvio` e `conforme + desvio + nao_verificado` é igual ao número de regras do baseline

### Requirement: Dado não coletado
Todo dado que não pôde ser coletado — por falta de privilégio, porque o comando não existe no host, porque o comando terminou com código de saída diferente de zero ou porque a coleta daquele item falhou de forma inesperada — SHALL levar as regras que dependem dele a `nao_verificado` com um `motivo`, e SHALL NOT ser interpretado como valor vazio, `conforme` ou `desvio`. A falha na coleta de um item SHALL NOT interromper a coleta dos demais.

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

#### Scenario: Falha inesperada na coleta de um item
- **WHEN** a coleta de um item levanta um erro inesperado (por exemplo, o comando excede o tempo limite)
- **THEN** as regras daquele item saem como `nao_verificado` com motivo "falha inesperada na coleta (<tipo do erro>)", as demais regras são avaliadas e a ferramenta termina com o código correspondente aos desvios encontrados

### Requirement: Formatos de saída
A ferramenta SHALL produzir, a partir do mesmo dado, um JSON com `host`, `inventario`, `conformidade` e `resumo`, e um Markdown no formato do enunciado: título `# Inventário de <hostname> (<endereço>)`, linha `Coletado em <AAAA-MM-DD HH:MM> UTC · baseline v<versão>`, seção `## Desvios` (sempre presente, tabela `Severidade | Regra | Esperado | Encontrado` ordenada por severidade), seção `## Não verificado` (só quando houver, tabela `Regra | Motivo`) e seção `## Conforme` com as regras separadas por ` · `.

#### Scenario: Formato both
- **WHEN** o operador pede `--format both`
- **THEN** o JSON sai primeiro, depois um separador `---`, depois o Markdown, todos em stdout

#### Scenario: Tabela Não verificado
- **WHEN** `ssh.login_de_root` não pôde ser verificado
- **THEN** o Markdown traz a linha `| ssh.login_de_root | exige privilégio que o usuário da coleta não tem |` numa tabela de duas colunas

### Requirement: Códigos de saída
A ferramenta SHALL sair com 0 quando não houver desvio, 1 quando houver pelo menos um desvio, 2 em falha de conexão e 3 em erro de uso, incluindo arquivo de chave privada ausente ou ilegível, que SHALL ser verificado antes de conectar. Nos códigos 2 e 3, SHALL escrever em stderr uma linha que explica o que houve — endereço que não resolve, conexão recusada, tempo esgotado ou autenticação recusada —, sem stack trace e sem nada em stdout.

#### Scenario: Host inalcançável
- **WHEN** o endereço resolve mas o host não responde dentro do tempo limite
- **THEN** a ferramenta sai com código 2, stdout vazio e uma linha em stderr dizendo que o tempo de conexão se esgotou

#### Scenario: Endereço errado
- **WHEN** o endereço informado não resolve
- **THEN** a ferramenta sai com código 2, stdout vazio e uma linha em stderr dizendo que o endereço não resolve

#### Scenario: SSH fora do ar
- **WHEN** o host existe mas nada escuta na porta SSH
- **THEN** a ferramenta sai com código 2 e a mensagem diz que a conexão foi recusada na porta informada

#### Scenario: Chave recusada
- **WHEN** o host recusa a chave
- **THEN** a ferramenta sai com código 2 e a mensagem diz que a autenticação foi recusada

#### Scenario: Arquivo de chave inexistente
- **WHEN** o caminho passado em `--key` não existe
- **THEN** a ferramenta sai com código 3 sem tentar conectar, e a mensagem diz que o arquivo da chave não foi encontrado
