# Spec Delta

## MODIFIED Requirements

### Requirement: Retrato do namespace
A aplicação SHALL listar os namespaces e, para o namespace selecionado, SHALL mostrar pods (estado, reinícios e motivo quando em falha), deployments (réplicas prontas sobre desejadas), services (com ou sem endpoint) e os eventos recentes, com filtro por namespace e busca por nome. A tela SHALL usar o vocabulário da API (pronto, disponível, sem endpoint) e SHALL NOT afirmar que um objeto está "saudável". Um pod pronto em que algum container não tem `readinessProbe` SHALL ser marcado, com uma legenda que explica que, nesse caso, pronto só indica que o processo subiu.

#### Scenario: Pod em OOMKilled
- **WHEN** o namespace tem um pod cujo último término foi por `OOMKilled`
- **THEN** a linha do pod mostra os reinícios e o motivo `OOMKilled`

#### Scenario: Pronto sem readinessProbe
- **WHEN** um pod está com todos os containers prontos e algum deles não declara `readinessProbe`
- **THEN** a coluna READY mostra o valor com asterisco (por exemplo `1/1*`) e a legenda "pronto sem readinessProbe: só indica que o processo subiu" está visível

#### Scenario: Pronto com readinessProbe
- **WHEN** um pod está pronto e todos os containers declaram `readinessProbe`
- **THEN** a coluna READY mostra o valor sem marca

### Requirement: Campo ausente não aparece como valor
A aplicação SHALL tratar campos ausentes da API sem exibir `None`: `readyReplicas` ausente aparece como `0/<desejadas>`, e Service sem endereço pronto em nenhum EndpointSlice aparece como "sem endpoint". Quando os EndpointSlices de um Service não puderem ser lidos, a aplicação SHALL mostrar "endpoint não verificado" com o motivo, e SHALL NOT afirmar "sem endpoint".

#### Scenario: Deployment sem réplica pronta
- **WHEN** a API omite `status.readyReplicas` de um deployment com 3 réplicas desejadas
- **THEN** a tela mostra `0/3`

#### Scenario: EndpointSlice ilegível
- **WHEN** o contexto pode listar services mas recebe 403 ao listar EndpointSlices
- **THEN** a coluna de endpoint mostra "endpoint não verificado (403)" em vez de "sem endpoint"

### Requirement: Somente leitura
A aplicação SHALL NOT executar nenhuma operação de escrita no cluster, e essa garantia SHALL ser verificável no projeto: um teste automático SHALL falhar se o código do dashboard chamar qualquer método de escrita do cliente ou montar nomes de método dinamicamente, e o repositório SHALL trazer uma ClusterRole que concede só `get`, `list` e `watch` nos recursos que a tela lê.

#### Scenario: Uso normal
- **WHEN** a aplicação roda por qualquer tempo com uma credencial que pode escrever
- **THEN** nenhuma requisição de criação, alteração ou remoção chega ao apiserver

#### Scenario: Código novo com verbo de escrita
- **WHEN** alguém acrescenta ao dashboard uma chamada como `delete_namespaced_pod`
- **THEN** o teste de somente leitura falha apontando o arquivo e a linha

#### Scenario: Identidade só de leitura
- **WHEN** o dashboard roda com uma ServiceAccount ligada à ClusterRole versionada
- **THEN** todos os painéis funcionam e qualquer tentativa de escrita seria recusada pelo apiserver
