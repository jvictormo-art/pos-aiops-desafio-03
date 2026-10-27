# Proposal

## Why

A revisão 2 (2026-10-27) apontou que faltavam evidências de código de retorno, de host inalcançável nos três casos e de host conforme. Ao preparar essas evidências conferindo o enunciado item a item, apareceram quatro divergências entre a ferramenta e o enunciado, que esta change corrige antes de gerar a evidência final:

1. O enunciado pede **uma entrada por regra do baseline**; a ferramenta gera uma por item (quatro `servicos.ativos`, duas `servicos.proibidos`), e o resumo conta 15 entradas para 11 regras.
2. O Markdown diverge do exemplo do enunciado: título com travessão, horário com segundos e uma coluna "Esperado" na tabela "Não verificado".
3. Uma exceção inesperada durante a coleta de **um** item aborta a execução inteira com código 3, contrariando o próprio TRD e o enunciado ("abortar a execução inteira não ajudaria ninguém").
4. Um arquivo de chave privada inexistente é reportado como "host inalcançável" (código 2), confundindo erro de uso com falha do host; e as mensagens de falha de conexão não distinguem endereço que não resolve, SSH fora do ar e timeout.

## What Changes

- **BREAKING (formato do JSON):** `conformidade` passa a ter exatamente uma entrada por regra; regras com lista agregam os itens em `esperado` e `encontrado`. `resumo` passa a somar o número de regras.
- Markdown idêntico ao exemplo do enunciado: `# Inventário de <host> (<endereço>)`, horário `AAAA-MM-DD HH:MM UTC`, tabela "Não verificado" com `Regra | Motivo`, motivo acentuado.
- Falha inesperada num coletor vira `nao_verificado` daquele item; a execução continua.
- Arquivo de chave ausente ou ilegível é erro de uso (código 3), verificado antes de conectar.
- Mensagens de falha de conexão específicas: endereço não resolve, conexão recusada (SSH fora do ar), tempo esgotado, autenticação recusada.

## Capabilities

### New Capabilities

### Modified Capabilities
- `inventario-vm`: requisitos "Conformidade com o baseline", "Dado não coletado", "Formatos de saída" e "Códigos de saída".

## Impact

- `ferramenta/inventario.py` (auditoria, renderização, tratamento de erros), `ferramenta/test_inventario.py`.
- Consumidores do JSON: a contagem e a forma de `conformidade` mudam (nenhum consumidor em produção; o Roster ainda não existe).
- Documentos: TRD 1.2, ADR-002, ADR-004, ADR-005 (novo).
