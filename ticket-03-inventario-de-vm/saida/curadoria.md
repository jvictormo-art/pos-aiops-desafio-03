# Curadoria — metacortex-inventario

O enunciado pede duas coisas: **onde a spec precisou ser corrigida durante a implementação** e **o que o agente entendeu diferente do que foi escrito**. As correções estão organizadas pelo ciclo em que apareceram; cada ciclo corresponde a uma change do OpenSpec em [`../openspec/changes/archive/`](../openspec/changes/archive/).

| Ciclo | Change | Quando |
|---|---|---|
| Versão 1.0 | `2026-10-27-inventario-vm` (reconstituída de `spec/`) | 2026-09-17 |
| Revisão 1 | `2026-10-27-coleta-nao-verificada` (reconstituída do commit "fix(ticket-03): marcar como nao_verificado todo dado que nao foi coletado") | 2026-10-08 |
| Revisão 2 | `2026-10-27-conformidade-alinhada-ao-enunciado` (ciclo feito com a CLI, spec antes do código) | 2026-10-27 |

---

## Onde a spec precisou ser corrigida durante a implementação

### Versão 1.0

1. **Determinismo tinha a granularidade errada.** A spec dizia "execução repetida devolve o mesmo retrato". Num container recém-iniciado, a lista de unidades mudou entre duas coletas com 11 segundos de intervalo (`systemd-timedated.service` só apareceu na segunda), porque o systemd ainda terminava o boot. O invariante correto é **o mesmo veredito por regra e o mesmo resumo**; o inventário bruto é uma fotografia do instante. A spec foi corrigida para isso (requisito "Determinismo").
2. **`ss` mostra a porta 53 como `127.0.0.53%lo`.** O parser separa porta por `rfind(":")`, e o bind resultante (`127.0.0.53%lo`) não é wildcard, então é tratado como interno. A spec não mudou, mas o caso passou a ser citado no TRD.
3. **Processo dono da porta é `null` com usuário comum.** `ss -tlnp` só mostra o processo de quem roda o comando. O schema já aceitava `null`; o campo é informativo, não regra.
4. **Container Docker expõe o swap da VM do Docker Desktop.** `/proc/swaps` dentro do container mostra o swap do kernel do host. Por isso o host conforme da evidência final é uma VM de verdade (Lima), não um container.
5. **Versão mínima do Python.** A spec dizia 3.10+; a estação de laboratório tem 3.9.6. Resolvido com `from __future__ import annotations` (ADR-003).

### Revisão 1 (2026-10-08)

6. **Dado não coletado virava `conforme`.** O revisor rodou a ferramenta numa VM sem systemd em execução e sem `ss`, e recebeu `servicos.proibidos` e as duas regras de porta como `conforme`. A detecção do systemd aceitava o exit 1 de `systemctl is-system-running` (que é o `offline` de um host sem systemd) e nenhum coletor conferia o código de saída: saída vazia virava "nada encontrado". A spec dizia "comando que falha vira `nao_verificado`", mas o código só fazia isso para `sshd -T`. Correção: o systemd é detectado por `/run/systemd/system` e todo coletor confere o código de saída (ADR-002). Comparação real da versão anterior e da corrigida na mesma VM: [`../saida/evidencia/anteriores/`](../saida/evidencia/anteriores/).

### Revisão 2 (2026-10-27)

7. **"Uma entrada por regra" não estava sendo cumprido.** O código gerava uma entrada por item (quatro `servicos.ativos`, duas `servicos.proibidos`) e o resumo somava 15 para 11 regras. A spec 1.0 não dizia nada sobre agregação, e a revisão 1 chegou a acrescentar uma coluna "Esperado" na tabela "Não verificado" para disfarçar a repetição, o que afastou o Markdown do formato do enunciado. Correção: uma entrada por regra com os itens agregados (ADR-005).
8. **Falha inesperada abortava tudo, contrariando a própria spec.** `spec-decisoes.md` dizia que uma exceção na coleta de um item "é capturada, o item é marcado como `nao_verificado` e a coleta continua". O código tinha um único `try` em volta da coleta inteira e saía com código 3. Correção: cada coletor roda isolado.
9. **O `argparse` usava o código 2 para argumento faltando.** A spec reservava 2 para falha de conexão e 3 para erro de uso, mas o `argparse` sai com 2 por padrão: num pipeline, "esqueci o `--key`" ficava igual a "host fora do ar". Só apareceu ao escrever o teste de códigos de saída. Correção: o parser sai com 3.
10. **Arquivo de chave inexistente era "host inalcançável".** O `paramiko` levanta `FileNotFoundError` (um `OSError`), que caía no mesmo `except` de falha de rede. Correção: o arquivo é verificado antes de conectar, e o erro é de uso (código 3).
11. **O nome do tipo de erro depende da versão do Python.** O motivo "falha inesperada na coleta (<tipo>)" mostra `timeout` no Python 3.9 e `TimeoutError` no 3.10+, onde `socket.timeout` virou apelido. O teste compara com o nome do tipo em tempo de execução, não com um texto fixo.
12. **O baseline nomeia unidades literalmente.** No Ubuntu 24.04, o pacote do node_exporter instala a unidade `prometheus-node-exporter.service`, e a regra `servicos.ativos` pede `node_exporter`. Um host com o exporter rodando pelo pacote oficial sai como desvio. Para a evidência, a VM conforme usa uma unidade chamada `node_exporter` (ver [`../ferramenta/preparar-vm-conforme.sh`](../ferramenta/preparar-vm-conforme.sh)). O baseline do parque deveria aceitar apelidos de unidade; fica registrado como pendência do baseline, não da ferramenta.
13. **"SSH fora do ar" no Ubuntu 24.04 exige parar dois objetos.** O SSH é ativado por socket: parar só `ssh.service` não fecha a porta 22, porque `ssh.socket` continua escutando e o reativa. A evidência para os dois e agenda a volta (`gerar-evidencias.sh`).

---

## O que o agente entendeu diferente do que foi escrito

1. **Porta da rede interna sem escuta.** A spec não dizia o que fazer se a 9100 não estivesse em escuta. O agente tratou como `conforme`: não estar escutando não é exposição, e a falta do processo já é coberta por `servicos.ativos`. A interpretação foi mantida e passou a constar do TRD.
2. **Serviço em `activating`.** O chrony estava `activating` logo após o boot; `list-units --state=active` não o lista, e o agente marcou desvio. Correto pela letra do baseline, mas gera falso positivo transitório em host recém-reiniciado. A spec não cobria; o TRD passou a recomendar auditar hosts estáveis.
3. **Chave sem comentário.** A spec dizia "não reconhecida"; o agente a tratou como desvio crítico, porque uma chave de origem desconhecida é exatamente o que o Roster quer encontrar.
4. **"Uma entrada por regra" lido como "uma por item".** O baseline lista serviços e portas, e o agente gerou uma entrada para cada um. Era uma leitura razoável do YAML, mas não do enunciado. Só ficou visível ao comparar o resumo (15) com o número de regras (11), na revisão 2 (item 7 acima).
5. **Formato do Markdown "melhorado".** Na revisão 1, o agente acrescentou a coluna "Esperado" à tabela "Não verificado" para desambiguar as linhas repetidas. Resolveu o sintoma, mas criou um segundo desvio em relação ao enunciado. A correção certa estava um nível acima: agregar por regra.
6. **Correções que o agente fez sem ser pedido.** Normalizar booleanos no Markdown (`True` → `true`, `None` → `null`) e deduplicar a seção "Conforme" para casar com o exemplo do enunciado.

---

## O que o método fixou e o que ficou com o agente

**Fixado pela spec:** os comandos de coleta, o significado de cada veredito, os códigos de saída, a proteção da chave e, desde a revisão 2, a forma da conformidade e do Markdown.

**Ficou com o agente:** porta sem escuta, serviço em `activating`, normalização de booleanos. Os três foram resolvidos de forma defensiva e hoje estão escritos no TRD, para não dependerem de interpretação.
