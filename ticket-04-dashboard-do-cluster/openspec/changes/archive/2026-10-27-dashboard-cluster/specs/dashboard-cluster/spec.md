# Spec Delta

## Purpose

Mostrar, na estação de quem opera, o retrato de leitura de um namespace do cluster do contexto corrente — pods, deployments, services com endpoint e eventos — encurtando o reconhecimento inicial de um chamado sem nunca escrever no cluster.

## ADDED Requirements

### Requirement: Contexto corrente apenas
A aplicação SHALL ler somente o `current-context` do kubeconfig no momento em que sobe, SHALL NOT oferecer seletor de cluster nem trocar de contexto, e SHALL mostrar o nome do contexto na tela.

#### Scenario: Abertura da aplicação
- **WHEN** o operador abre a aplicação com o contexto `kind-metacortex-lab` ativo
- **THEN** a tela mostra os dados desse cluster e o nome do contexto, sem perguntar qual cluster usar

### Requirement: Retrato do namespace
A aplicação SHALL listar os namespaces e, para o namespace selecionado, SHALL mostrar pods (estado, reinícios e motivo quando em falha), deployments (réplicas prontas sobre desejadas), services (com ou sem endpoint) e os eventos recentes, com filtro por namespace e busca por nome.

#### Scenario: Pod em OOMKilled
- **WHEN** o namespace tem um pod cujo último término foi por `OOMKilled`
- **THEN** a linha do pod mostra os reinícios e o motivo `OOMKilled`

### Requirement: Campo ausente não aparece como valor
A aplicação SHALL tratar campos ausentes da API sem exibir `None`: `readyReplicas` ausente aparece como `0/<desejadas>`, e Service sem endereço pronto em nenhum EndpointSlice aparece como "sem endpoint".

#### Scenario: Deployment sem réplica pronta
- **WHEN** a API omite `status.readyReplicas` de um deployment com 3 réplicas desejadas
- **THEN** a tela mostra `0/3`

### Requirement: Falha do ambiente sem tela em branco
Quando o cluster não responder ou a credencial for inválida, a aplicação SHALL mostrar uma mensagem que explica o que houve, sem stack trace e sem tela em branco. Quando a permissão for negada para um tipo de recurso, só o painel daquele recurso SHALL mostrar a falta de permissão, e os outros SHALL continuar.

#### Scenario: Permissão negada para deployments
- **WHEN** o contexto pode listar pods mas recebe 403 ao listar deployments
- **THEN** o painel de deployments diz "Sem permissão para listar este recurso no contexto atual (403)" e o de pods continua mostrando dados

### Requirement: Somente leitura
A aplicação SHALL NOT executar nenhuma operação de escrita no cluster.

#### Scenario: Uso normal
- **WHEN** a aplicação roda por qualquer tempo com uma credencial que pode escrever
- **THEN** nenhuma requisição de criação, alteração ou remoção chega ao apiserver
