# Curadoria — metacortex-dashboard

O enunciado pede três coisas: **onde a spec precisou ser corrigida durante a implementação**, **o que o agente entendeu diferente do que foi escrito** e, **para cada decisão em aberto, a justificativa estendida** comparando o caminho escolhido com pelo menos dois descartados.

| Ciclo | Change do OpenSpec | Quando |
|---|---|---|
| Versão 1.0 | `2026-10-27-dashboard-cluster` (reconstituída de `spec/`) | 2026-09-17 |
| Revisão 2 | `2026-10-27-leitura-garantida-e-saude-honesta` (ciclo feito com a CLI, spec antes do código) | 2026-10-27 |

---

## Onde a spec precisou ser corrigida durante a implementação

### Versão 1.0

1. **Versão mínima do Python.** A spec fixava 3.10+; a estação de laboratório tem 3.9.6. Resolvido com `from __future__ import annotations`; a decisão de stack não mudou.
2. **O cliente tipado quebra exatamente no dado que o enunciado avisou ser sensível.** Um `EndpointSlice` sem endereços vem com `"endpoints": null`, e o modelo gerado do cliente oficial trata o campo como obrigatório: `ValueError` na desserialização, e a listagem **do namespace inteiro** cai por causa de uma fatia. Correção: leitura crua (`_preload_content=False`) só nessa chamada.
3. **Pod preso em initContainer.** A spec lia o motivo só de `containerStatuses`; com o initContainer em `ImagePullBackOff`, o container principal diz `PodInitializing`, que é verdadeiro e inútil. Correção: ler `initContainerStatuses` antes, prefixando `Init:` como o `kubectl`.
4. **Credencial inválida nem sempre é 401.** A spec supunha `401`; com certificado de cliente, a falha podia acontecer no handshake TLS (`SSLError` dentro de `MaxRetryError`), na mesma família de "cluster fora do ar". Correção: separar o caso de SSL. (Na revisão 2, o `kind` atual aceitou o handshake e devolveu `401`; os dois caminhos estão cobertos.)
5. **`DuplicateIds` na troca de painéis** (correção de código, não de spec): remontar widgets com o mesmo `id` antes de a remoção assíncrona terminar. Correção: criar uma vez e alternar visibilidade.

### Revisão 2 (2026-10-27)

6. **A pergunta sobre saúde nunca foi respondida.** O enunciado pede para definir o quanto a tela pode afirmar sobre saúde, já que "pronto" não é "saudável". A spec 1.0 não dizia nada, e a tela mostrava READY sem distinguir "a probe passou" de "o processo subiu". Correção: ADR-007, com o vocabulário da API e a marca `1/1*` para pronto sem readinessProbe. A evidência `01` mostra o Postgres de apoio, que não tem probe, marcado.
7. **"Sem endpoint" afirmado sem ser verificado.** Se a leitura de `EndpointSlice` falhasse (ex.: 403), o código contava zero e a tela dizia "sem endpoint", uma afirmação falsa, do mesmo tipo do defeito que a revisão 1 achou no Ticket 03. Correção: "endpoint não verificado (403)".
8. **A garantia de só leitura era uma intenção.** O enunciado exige a garantia visível no projeto. A 1.0 tinha a convenção no código e um `grep` descrito numa tarefa, que ninguém roda. Correção (ADR-006): teste por árvore sintática que falha com verbo de escrita ou `getattr` com nome montado, e ClusterRole versionada só com `get`/`list`/`watch`, conferida pelo mesmo teste.
9. **Cenários de falha não reproduzíveis.** O contexto restrito e os kubeconfigs de falha da evidência 1.0 não estavam no repositório. Correção: `laboratorio/cenarios-de-falha.sh` e `evidencia/capturar.py`, que gera todas as capturas sem terminal.
10. **Pré-requisito não cumprido: o fake-shop nunca rodou.** Na 1.0 ele ficava em `Init:ErrImagePull`, porque `registry.metacortex.io` não existe fora da ficção. Ao espelhar a imagem no `kind`, apareceram dois defeitos escondidos:
    - **No manifest do Ticket 01:** a migração no initContainer importa a aplicação, que exige `PROMETHEUS_MULTIPROC_DIR` apontando para um diretório existente. Corrigido no Ticket 01, manifest e skill.
    - **No Secret:** o manifest traz `CHANGE_ME` (certo pela regra 3.3), e um `kubectl apply` da pasta inteira sobrescreve o Secret real. O `subir-workloads.sh` cria os Secrets fora do Git e não aplica o placeholder.
11. **O Secret do kube-news versionava a senha de verdade**, o que viola a regra 3.3. Os manifests foram regerados com a skill instalada e saem com `CHANGE_ME`.
12. **O kubelet 1.36 lembra o que já baixou.** A imagem do kube-news re-etiquetada como `registry.metacortex.io/...` tinha o mesmo ID de `fabricioveronez/kube-news:v1`, baixada pelo kubelet para os chamados do Ticket 02. Por causa dos registros de pull em `/var/lib/kubelet/image_manager/pulled`, o kubelet não a tratou como imagem pré-carregada e tentou o pull, que falhava no DNS. A do fake-shop, nunca baixada pelo kubelet, funcionou com o mesmo procedimento. Correção fiel ao enunciado ("o Loom espelha, escaneia e republica"): o espelho republica a imagem com rótulos de procedência, o que gera um ID próprio.

---

## O que o agente entendeu diferente do que foi escrito

1. **"Distinguir ausência de vazio" foi entendido na intenção, não na mecânica.** A spec tratava o caso como um `if` na apresentação; na prática, o cliente tipado nem deixava o código chegar ao `if` (item 2 acima).
2. **"Painel independente" foi implementado mais rígido do que o texto pedia.** O agente fez uma chamada de rede por painel, cada uma com seu tratamento de erro. A spec não exigia essa granularidade, mas foi ela que fez o cenário de permissão parcial funcionar sem lógica extra.
3. **"Sem endpoint" virou o valor-padrão de qualquer falha.** O agente tratou a exceção na leitura de `EndpointSlice` retornando 0, o caminho "seguro" para não derrubar a tela, sem notar que isso fazia a tela afirmar algo não verificado (item 7).
4. **"Pronto" foi lido como resposta suficiente.** A spec copiava o exemplo do enunciado (READY, réplicas prontas) e o agente implementou exatamente isso, sem tratar o aviso de que "pronto não significa saudável" como requisito. Só a releitura do enunciado na revisão 2 transformou o aviso em decisão (item 6).
5. **Escolha consciente de não repetir o `_meta` do Ticket 03.** A informação equivalente (painel restrito) já tinha canal próprio no `Resultado.tipo_erro`.

---

## Justificativa estendida das decisões em aberto

Cada decisão em aberto do enunciado tem ADR próprio, com o caminho escolhido, **duas alternativas descartadas e o que se ganha e o que se perde em cada uma**, e o que a implementação confirmou ou contestou:

| Decisão em aberto | ADR | Escolha | Descartadas | A implementação... |
|---|---|---|---|---|
| Linguagem e stack | [ADR-001](../docs/adr/ADR-001-linguagem-e-stack.md) | Python + Textual (TUI) | Go + client-go; web local | confirmou |
| Como falar com a API | [ADR-002](../docs/adr/ADR-002-acesso-a-api-do-kubernetes.md) | cliente oficial | `kubectl` subprocesso; HTTP direto | quase contestou (item 2), e o escape de leitura crua do próprio cliente resolveu |
| Atualização da tela | [ADR-003](../docs/adr/ADR-003-atualizacao-da-tela.md) | polling de 5 s | sob demanda; watch | confirmou |
| Endpoints × EndpointSlice | [ADR-004](../docs/adr/ADR-004-fonte-dos-endpoints.md) | EndpointSlice | Endpoints; ler os dois | confirmou (o próprio `kubectl` avisa que Endpoints está obsoleto desde a 1.33) |
| Recorte da primeira fatia | [ADR-005](../docs/adr/ADR-005-recorte-da-primeira-fatia.md) | os cinco objetos mínimos | só pods; incluir métricas e PDB | confirmou (o cluster não tem metrics-server) |

Duas decisões que não estavam na lista do enunciado, mas que ele exige de outra forma, também viraram ADR: [ADR-006](../docs/adr/ADR-006-garantia-de-somente-leitura.md) (garantia de leitura visível) e [ADR-007](../docs/adr/ADR-007-o-que-a-tela-afirma-sobre-saude.md) (o que a tela afirma sobre saúde).
