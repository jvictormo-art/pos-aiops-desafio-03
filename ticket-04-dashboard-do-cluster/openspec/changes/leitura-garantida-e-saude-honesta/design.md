# Design

## Context

As lacunas estão em proposal.md. O ponto de partida é a versão 1.0: `ClusterReader` devolve dicionários por objeto e `app.py` só formata.

## Goals / Non-Goals

**Goals:**
- A tela não afirma nada que a API não saiba (saúde, endpoint).
- "Só leitura" verificável por quem não escreveu o código.
- Cenários de falha e evidências reproduzíveis com um comando.

**Non-Goals:**
- Checagem ativa de saúde (`/health` via proxy) — ADR-007, alternativa B.
- Watch, multicluster.

## Decisions

- **Marca de "pronto sem probe"** (ADR-007): `_resumir_pod` passa a devolver `sem_readiness` (algum container sem `readinessProbe`); `app.py` acrescenta `*` ao READY quando o pod está pronto e `sem_readiness` é verdadeiro, e mostra a legenda fixa no rodapé. Alternativas descartadas: semáforo "saudável" (afirma o que a API não sabe) e checar `/health` (exige `pods/proxy` e não existe no fake-shop).
- **Endpoint não verificado:** `_contar_endpoints_prontos` devolve `None` com o motivo quando a leitura falha; `listar_services_com_endpoint` escreve "endpoint não verificado (<motivo>)". Alternativa descartada: marcar o painel inteiro como restrito (perderia a lista de services, que foi lida).
- **Teste estático por AST** (ADR-006): percorre `dashboard/*.py` (exceto testes) procurando `Call` cujo atributo começa com `create_`, `patch_`, `replace_`, `delete_` ou `connect_`, e `getattr` com segundo argumento que não seja literal. Alternativa descartada: `grep` (pega comentários e docstrings, e não falha sozinho num pipeline).
- **ClusterRole `metacortex-dashboard-leitura`** com `get`/`list`/`watch` em namespaces, pods, services, events, deployments e endpointslices.
- **Cenários:** `cenarios-de-falha.sh` deriva do kubeconfig do kind três arquivos: `inalcancavel` (server `https://127.0.0.1:1`), `credencial-invalida` (certificado de cliente autoassinado gerado com `openssl`) e `platform-ro` (token de ServiceAccount com Role só para pods, eventos e namespaces).
- **Captura de evidência:** `capturar.py` roda o app com `App.run_test()` (piloto headless do Textual), seleciona o namespace, espera um ciclo de polling e salva SVG com `save_screenshot`. Alternativa descartada: capturas manuais (não reproduzíveis).

## Risks / Trade-offs

- [O teste por AST não pega escrita feita por outra biblioteca (ex.: `requests` direto ao apiserver)] → o teste também falha se `k8s_reader.py` importar `requests` ou `urllib3` para fazer requisição; a ClusterRole cobre o resto.
- [A marca `*` pode ser ignorada] → a legenda é fixa no rodapé, não um tooltip.

## Migration Plan

Sem migração. As evidências SVG são regeneradas; as anteriores ficam no histórico do git.
