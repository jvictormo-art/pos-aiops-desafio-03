# ADR-005 — Uma entrada de conformidade por regra do baseline

| Campo | Valor |
|---|---|
| Status | aceito |
| Data | 2026-10-27 (revisão 2; change OpenSpec `conformidade-alinhada-ao-enunciado`) |
| Substitui | o comportamento da versão 1.0, que gerava uma entrada por item das regras com lista |

## Contexto

O enunciado define a conformidade como "uma entrada por regra do baseline". A versão 1.0 gerava uma entrada por **item** nas regras que listam vários valores: quatro entradas `servicos.ativos` (uma por serviço), duas `servicos.proibidos`, uma por porta em `somente_rede_interna`. Com isso o resumo contava 15 entradas para um baseline de 11 regras, e o Markdown repetia o mesmo nome de regra várias vezes, o que obrigou a primeira revisão a acrescentar uma coluna "Esperado" fora do formato do enunciado.

## Decisão

Exatamente uma entrada por regra (11 com o baseline atual). Regras com lista **agregam** os itens: o `esperado` traz a lista do baseline e o `encontrado` diz quais itens falharam (`ausente: containerd, node_exporter`). O veredito da regra é `desvio` se algum item falhar, `nao_verificado` se o dado não pôde ser coletado, e `conforme` caso contrário.

## Alternativas consideradas

### A. Manter uma entrada por item

- **Ganha:** granularidade máxima; cada serviço ausente é uma linha.
- **Perde:** contraria o enunciado; o `resumo` deixa de contar regras; a severidade é contada várias vezes para uma única regra violada.

### B. Uma entrada por regra com `encontrado` estruturado (lista de objetos por item)

- **Ganha:** o Roster recebe o detalhe por item já estruturado.
- **Perde:** `encontrado` passa a ter tipos diferentes por regra (texto, booleano, lista de objetos), e o Markdown precisaria achatar a estrutura de qualquer forma. O detalhe por item já existe no bloco `inventario` do mesmo JSON.

### C. Uma entrada por regra, `encontrado` em texto agregado (escolhida)

- **Ganha:** bate com o enunciado; `resumo` conta regras; uma linha por regra no Markdown, sem coluna extra; o detalhe por item continua disponível em `inventario`.
- **Perde:** quem quiser reagir a um serviço específico lê `inventario.servicos`, não a conformidade.

## Consequências

- O `resumo` soma 11 com o baseline atual: `conforme + desvio + nao_verificado = número de regras`.
- A tabela "Não verificado" do Markdown volta ao formato do enunciado (`Regra | Motivo`).
