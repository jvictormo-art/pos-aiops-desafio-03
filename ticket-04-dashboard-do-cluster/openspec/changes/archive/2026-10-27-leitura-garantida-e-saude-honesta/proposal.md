# Proposal

## Why

A revisão 2 (2026-10-27) apontou que o projeto não seguia o arco de spec e que os pré-requisitos não estavam cumpridos. Ao conferir o enunciado item a item para corrigir isso, apareceram quatro lacunas no próprio dashboard:

1. **Saúde.** O enunciado pede para "definir o quanto o dashboard pode afirmar sobre a saúde de um objeto", porque "pronto" não significa "saudável". Nenhum documento nem o código responde isso: a tela mostra READY sem dizer quando ele só significa "o processo subiu".
2. **Garantia de leitura frágil.** O enunciado exige a garantia "visível no projeto (código, configuração ou permissões), não só na intenção". Hoje ela é uma convenção no código mais um `grep` descrito numa tarefa, que ninguém executa automaticamente.
3. **Endpoint afirmado sem ser verificado.** Se a leitura de `EndpointSlice` falha (ex.: 403), o código conta zero endereços e a tela diz "sem endpoint", uma afirmação falsa.
4. **Cenários de falha não reproduzíveis.** O contexto restrito "tipo platform-ro" e os kubeconfigs de cluster inalcançável e credencial inválida usados na evidência não estão versionados.

## What Changes

- Pod pronto com container sem `readinessProbe` passa a ser marcado (`1/1*`), com legenda fixa; a tela nunca usa "saudável".
- Teste automático de somente leitura (`dashboard/test_somente_leitura.py`) e ClusterRole de leitura versionada (`rbac/dashboard-leitura.yaml`).
- Falha ao ler `EndpointSlice` aparece como "endpoint não verificado (<motivo>)", não como "sem endpoint".
- Script que gera os kubeconfigs dos três cenários de falha (`laboratorio/cenarios-de-falha.sh`) e script que captura as telas de evidência sem terminal (`evidencia/capturar.py`).

## Capabilities

### New Capabilities

### Modified Capabilities
- `dashboard-cluster`: requisitos "Retrato do namespace", "Campo ausente não aparece como valor" e "Somente leitura".

## Impact

- `dashboard/k8s_reader.py`, `dashboard/app.py`; novos `dashboard/test_somente_leitura.py`, `dashboard/test_k8s_reader.py`, `rbac/`, `laboratorio/cenarios-de-falha.sh`, `evidencia/capturar.py`.
- Documentos: PRD 1.1, TRD 1.1, ADR-006 (ampliado), ADR-007 (novo).
