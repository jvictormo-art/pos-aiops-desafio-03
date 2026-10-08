# Comparação: com skill × sem skill

Dois chamados reais do lab, cada um rodado **3 vezes sem a skill e 3 vezes com a skill**, em sessões limpas do Claude Code (`claude -p`, Sonnet 5.5) contra o cluster `kind-metacortex-lab`. As duas variantes usam o mesmo servidor MCP em modo não destrutivo, as mesmas permissões e o mesmo prompt, que é o texto do chamado, sem pistas. A única diferença é a skill `metacortex-triage` instalada em `.claude/skills/`.

| Caso | Prompt enviado | Causa real |
|---|---|---|
| A — Chamado 1 (nyx-prod) | "a API do nyx-prod está reiniciando sozinha, verifica aí" | `OOMKilled`, `limits.memory: 24Mi` |
| B — Chamado 3 (nyx-stg) | "o Service do nyx-stg não está entregando tráfego" | seletor `app: nyx-api` × label `app: nyxapi` |

**Resultado em uma linha:** as 12 execuções acertaram a causa. A skill **aumentou** o consumo de tokens (+32% no caso A, +42% no caso B) e, em troca, deixou o caminho de investigação e o formato do relatório **idênticos** entre as repetições.

---

<!-- tokens:inicio -->
## Medição real de tokens

Números extraídos do `claude -p --output-format stream-json` de cada sessão (gerados por [`medicao-tokens/medir.sh`](./medicao-tokens/medir.sh) e [`medicao-tokens/consolidar.py`](./medicao-tokens/consolidar.py); o JSON bruto de cada execução está em `medicao-tokens/runs/`). Cada execução é uma sessão limpa, com o mesmo servidor MCP, as mesmas permissões e o mesmo prompt; a única diferença entre as variantes é a skill instalada em `.claude/skills/`.

Modelo(s): claude-sonnet-5-5.

### Caso A — Chamado 1 (nyx-prod, OOMKilled)

Média de 3 execução(ões) sem skill e 3 com skill.

| Métrica | Sem skill | Com skill | Variação |
|---|---:|---:|---:|
| Tokens de entrada (sem cache) | 8 | 10 | +25% |
| Tokens de escrita em cache | 10.628 | 11.093 | +4% |
| Tokens de leitura de cache | 47.551 | 66.085 | +39% |
| Tokens de saída | 1.382 | 1.414 | +2% |
| **Tokens totais** | 59.569 | 78.602 | +32% |
| Custo (USD) | 0.0659 | 0.0718 | +9% |
| Tool calls no cluster | 3.3 | 2.0 | -40% |
| Turnos | 5.3 | 6.0 | +13% |
| Duração (s) | 13 | 15 | +15% |
| Skill acionada | 0/3 | 3/3 | |

### Caso B — Chamado 3 (nyx-stg, 503 com pods Running)

Média de 3 execução(ões) sem skill e 3 com skill.

| Métrica | Sem skill | Com skill | Variação |
|---|---:|---:|---:|
| Tokens de entrada (sem cache) | 8 | 10 | +25% |
| Tokens de escrita em cache | 10.791 | 17.232 | +60% |
| Tokens de leitura de cache | 48.004 | 66.479 | +38% |
| Tokens de saída | 1.464 | 1.715 | +17% |
| **Tokens totais** | 60.267 | 85.436 | +42% |
| Custo (USD) | 0.0674 | 0.0994 | +47% |
| Tool calls no cluster | 4.7 | 5.0 | +7% |
| Turnos | 6.7 | 9.0 | +35% |
| Duração (s) | 13 | 16 | +20% |
| Skill acionada | 0/3 | 3/3 | |

<details><summary>Execuções individuais</summary>

| Execução | Tokens totais | Saída | Custo (USD) | Tool calls | Skill | Erro |
|---|---:|---:|---:|---:|:-:|:-:|
| `A-nyx-prod-com-1` | 78.539 | 1.369 | 0.0712 | 2 | sim |  |
| `A-nyx-prod-com-2` | 78.650 | 1.466 | 0.0723 | 2 | sim |  |
| `A-nyx-prod-com-3` | 78.616 | 1.408 | 0.0718 | 2 | sim |  |
| `A-nyx-prod-sem-1` | 56.605 | 1.227 | 0.0574 | 3 | não |  |
| `A-nyx-prod-sem-2` | 59.911 | 1.346 | 0.0654 | 3 | não |  |
| `A-nyx-prod-sem-3` | 62.192 | 1.573 | 0.0748 | 4 | não |  |
| `B-nyx-stg-com-1` | 86.709 | 1.732 | 0.1012 | 5 | sim |  |
| `B-nyx-stg-com-2` | 84.727 | 1.687 | 0.0983 | 5 | sim |  |
| `B-nyx-stg-com-3` | 84.871 | 1.725 | 0.0987 | 5 | sim |  |
| `B-nyx-stg-sem-1` | 60.357 | 1.564 | 0.0674 | 5 | não |  |
| `B-nyx-stg-sem-2` | 60.074 | 1.366 | 0.0679 | 4 | não |  |
| `B-nyx-stg-sem-3` | 60.371 | 1.462 | 0.0669 | 5 | não |  |

</details>
<!-- tokens:fim -->

---

## Caminho percorrido em cada execução

Sequência de ferramentas extraída dos eventos `tool_use` de cada sessão. `ToolSearch` é o carregamento das ferramentas MCP e aparece nas duas variantes.

| Execução | Sequência |
|---|---|
| A sem 1 | `get pods` → `describe pod` → `logs --previous` |
| A sem 2 | `get pods` → `describe pod` → `logs --previous` |
| A sem 3 | `get pods` → `describe pod` → `logs --previous` → `get` |
| A com 1–3 | `Skill` → `get pods` → `describe pod` (as três iguais) |
| B sem 1 | `get` ×4 → `describe pod` |
| B sem 2 | `get` ×4 |
| B sem 3 | `get` ×5 |
| B com 1–3 | `Skill` → `get` ×5: pods, endpoints, service, pods -o yaml (as três iguais) |

Nenhuma das 12 execuções teve permissão negada, ou seja, nenhuma tentou usar uma ferramenta de escrita.

---

## Leitura dos números

**Por que a skill custa mais tokens.** Ela entra no contexto quando é acionada: o `SKILL.md` tem cerca de 5 KB e a chamada `Skill` acrescenta um turno. Como cada turno relê o contexto inteiro, esse acréscimo se repete a cada passo da investigação. É isso que aparece na linha "Tokens de leitura de cache" (+39% no caso A, +38% no B). Os tokens de saída quase não mudam (+2% e +17%). A diferença está no contexto, não no texto que o agente produz.

**Por que o custo em dólares sobe menos que os tokens no caso A** (+9% contra +32%). A maior parte do acréscimo é leitura de cache, que é cobrada bem abaixo da entrada normal.

**Onde a skill economiza.** No caso A ela corta a leitura de logs: 2 chamadas ao cluster contra 3,3 na média. A skill manda parar quando `describe` já mostra `OOMKilled` com exit 137. Sem ela, o agente sempre pediu `logs --previous`, que nesse cenário falhou ("unable to retrieve container logs") e não acrescentou nada. Mesmo assim, a economia de uma chamada é menor que o custo de carregar a skill.

**O que a medição não confirmou.** A versão anterior deste documento afirmava que, sem skill, o agente percorreria hipóteses erradas e, no caso B, poderia concluir que "a app está OK, o problema é fora do cluster". Com o Sonnet 5.5 isso não aconteceu: nas 3 execuções sem skill do caso B, o agente foi direto a endpoints e seletor e encontrou a divergência. A afirmação de que a skill "custa menos token nos casos simples" também é desmentida pelos números.

---

## Conclusão sobre ganho real

**Em tokens, a skill não compensa nestes dois chamados.** Com um modelo atual, os dois casos são diagnosticáveis sem método explícito, e carregar o método custa entre 32% e 42% a mais de tokens por triagem.

O ganho medido é de **consistência**, e é real:

1. **Mesmo caminho em todas as execuções.** Com a skill, as três repetições de cada caso fizeram exatamente a mesma sequência de chamadas. Sem ela, a sequência variou (3 ou 4 chamadas no caso A; 4 ou 5, com e sem `describe`, no B). Em plantão, isso significa que dois operadores, ou duas sessões, chegam à causa pelo mesmo caminho e o relatório de um é comparável ao do outro.
2. **Mesmo formato de relatório.** Com a skill, as seis saídas trazem `CAUSA` / `EVIDÊNCIA` / `AÇÃO SUGERIDA` com os campos do Kubernetes citados. Sem a skill, cada saída teve uma estrutura diferente ("## Diagnóstico", "**Causa:**", "## Causa raiz"…), nenhuma trouxe os três campos, e algumas já detalhavam a correção com mais de uma alternativa.
3. **Parada definida.** A skill encerra a investigação quando a evidência fecha a causa: "Causa fechada; o skill manda parar aqui". Sem ela, o agente às vezes seguiu investigando depois de já ter a resposta (`A sem 3`).

A recomendação que sai da medição: manter a skill pelo padrão de saída e pela previsibilidade, aceitando o custo extra, e reduzir esse custo enxugando o `SKILL.md` (por exemplo, separando a tabela de sintomas em um arquivo de referência carregado só quando necessário). Uma nova medição com o `medir.sh` mostra se o enxugamento funciona.
