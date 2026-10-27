# Spec Delta

## Purpose

Auditar uma VM do parque por SSH, sem agente e sem alterar o host, comparando o estado real com o baseline e produzindo um relatório consumível pelo Roster e legível pelo plantão.

## ADDED Requirements

### Requirement: Coleta somente leitura por SSH
A ferramenta SHALL conectar à VM por SSH com o endereço, o usuário e a chave privada recebidos, a partir da máquina de quem opera, e SHALL executar no host apenas comandos de leitura, sem instalar, escrever ou corrigir nada.

#### Scenario: Auditoria de um host alcançável
- **WHEN** o operador executa a ferramenta com endereço, usuário e chave válidos
- **THEN** a ferramenta coleta o estado do host e nenhum arquivo, pacote ou serviço do host é alterado

### Requirement: Itens coletados
A ferramenta SHALL coletar identificação (endereço usado, hostname reportado pelo host, instante UTC da coleta), distribuição e versão do SO, versão do kernel em execução, unidades ativas distinguindo `service` de `socket`, swap (habilitado e tamanho), portas TCP em escuta (porta, endereço de bind e processo dono), identificação de cada chave SSH autorizada, login de root efetivo do SSH e sincronização de tempo (estado e mecanismo).

#### Scenario: Porta exposta versus porta interna
- **WHEN** a porta 9100 está em escuta em `0.0.0.0`
- **THEN** o inventário registra o bind `0.0.0.0`, e a mesma porta em escuta num endereço específico registra esse endereço

### Requirement: Conformidade com o baseline
A ferramenta SHALL comparar o inventário com cada regra do `baseline.yaml` e, para cada comparação, SHALL registrar a regra, o valor esperado, o valor encontrado e um veredito entre `conforme`, `desvio` e `nao_verificado`. Todo `desvio` SHALL trazer a severidade que o baseline atribui à regra.

#### Scenario: Swap habilitado
- **WHEN** o host tem swap de 4G e o baseline exige swap desabilitado
- **THEN** a regra `swap.habilitado` sai como `desvio` com severidade `critico` e encontrado `true (4G)`

### Requirement: Dado não coletado
Quando um dado exigir privilégio que o usuário da coleta não tem, a regra correspondente SHALL sair como `nao_verificado` com um `motivo`, e a execução SHALL continuar para as demais regras.

#### Scenario: sshd -T sem privilégio
- **WHEN** o usuário da coleta não consegue executar `sshd -T`
- **THEN** `ssh.login_de_root` sai como `nao_verificado` com motivo "exige privilegio que o usuario da coleta nao tem", e as outras regras são avaliadas normalmente

### Requirement: Formatos de saída
A ferramenta SHALL produzir, a partir do mesmo dado, um JSON com `host`, `inventario`, `conformidade` e `resumo`, e um Markdown com as seções Desvios (ordenada por severidade), Não verificado (quando houver) e Conforme.

#### Scenario: Formato both
- **WHEN** o operador pede `--format both`
- **THEN** o JSON sai primeiro, depois um separador `---`, depois o Markdown, todos em stdout

### Requirement: Códigos de saída
A ferramenta SHALL sair com 0 quando não houver desvio, 1 quando houver pelo menos um desvio, 2 em falha de conexão e 3 em erro de uso. Em falha de conexão, SHALL escrever em stderr uma mensagem que explica o que houve, sem stack trace e sem nada em stdout.

#### Scenario: Host inalcançável
- **WHEN** o endereço não responde
- **THEN** a ferramenta sai com código 2, stdout vazio e uma linha em stderr dizendo que o host é inalcançável

### Requirement: Proteção da chave privada
A chave privada SHALL NOT aparecer em stdout, stderr ou log, nem parcialmente, inclusive em mensagens de erro de autenticação.

#### Scenario: Chave recusada
- **WHEN** o host recusa a chave
- **THEN** a mensagem diz que a autenticação foi recusada e não contém o conteúdo da chave

### Requirement: Determinismo
Duas execuções seguidas contra o mesmo host SHALL devolver o mesmo veredito para cada regra e o mesmo resumo; só o instante da coleta muda.

#### Scenario: Segunda execução
- **WHEN** a ferramenta roda duas vezes seguidas contra um host estável
- **THEN** `conformidade` e `resumo` são idênticos e `coletado_em` difere
