# Proposal

> **Change reconstituída.** O ciclo original (2026-09-17) foi feito com documentos próprios em `spec/` (proposta, decisões, comportamento, tarefas, arquivo final; commit "Add metacortex-dashboard e entregas do Ticket 04"), sem a CLI do OpenSpec. Em 2026-10-27 o conteúdo foi transcrito para esta change e arquivado com `openspec archive`, para que a spec principal reflita a versão 1.0 e a revisão seguinte seja um delta sobre ela. Nenhum requisito foi acrescentado na transcrição.

## Why

Toda triagem começa com seis a dez comandos no terminal para montar o retrato de um namespace. Uma tela que mostre esse retrato a partir do kubeconfig de quem opera encurta os primeiros minutos de cada chamado.

## What Changes

- Nova aplicação de terminal (`dashboard/app.py`) que lê o contexto corrente do kubeconfig e mostra namespaces, pods, deployments, services com endpoint e eventos, com filtro por namespace e busca por nome.
- Camada de leitura (`dashboard/k8s_reader.py`) com o cliente oficial, só verbos de leitura, erro tipado por painel.
- Tratamento de cluster que não responde, credencial inválida e permissão negada por tipo de recurso.

## Capabilities

### New Capabilities
- `dashboard-cluster`: retrato de leitura de um namespace do cluster do contexto corrente, com degradação por painel quando o ambiente falha.

### Modified Capabilities

## Impact

- Código novo em `dashboard/`; dependências `kubernetes` e `textual`.
- Nenhuma escrita no cluster.
