# ADR-004 — Códigos de saída para uso em pipeline

| Campo | Valor |
|---|---|
| Status | aceito (revisado em 2026-10-27) |
| Data | 2026-09-17 (registrado como ADR em 2026-10-27; origem: `spec/spec-comportamento.md`, seção "Exit codes") |

## Contexto

O enunciado pede "código de saída utilizável em pipeline". Um cron ou CI precisa decidir sem ler o relatório se o host está dentro do padrão, fora dele, ou se a auditoria nem aconteceu. Um host inalcançável **não pode** ser confundido com host conforme.

## Decisão

| Código | Significado |
|---|---|
| 0 | Host alcançado, nenhum desvio (pode haver `nao_verificado`) |
| 1 | Host alcançado, pelo menos um desvio |
| 2 | Falha de conexão (endereço que não resolve, SSH fora do ar, timeout, chave recusada) |
| 3 | Erro de uso (baseline inválido, arquivo de chave ausente ou ilegível, argumento faltando) |

Nos códigos 2 e 3, stdout fica vazio e o stderr traz uma linha que diz o que houve.

## Alternativas consideradas

> A spec de 2026-09-17 registrou só a tabela de códigos. As alternativas abaixo foram escritas na reconstituição de 2026-10-27, para cumprir o formato de ADR.

### A. Só 0 e 1 (sucesso/falha)

- **Ganha:** convenção mais simples possível.
- **Perde:** "host com desvio" e "host que não respondeu" ficam iguais; o pipeline marcaria o host como fora do padrão quando, na verdade, ele nem foi auditado.

### B. Código igual ao número de desvios (ou à maior severidade)

- **Ganha:** mais informação no código.
- **Perde:** colide com códigos de erro de conexão, satura em 255 e acopla o contrato do pipeline à quantidade de regras do baseline. A severidade já está no JSON.

### C. Quatro códigos por categoria (escolhida)

- **Ganha:** cada situação que pede ação diferente tem um código: corrigir host (1), investigar acesso (2), corrigir a chamada (3).
- **Perde:** `nao_verificado` não aparece no código; quem precisa de cobertura total lê `resumo.nao_verificado`.

## Consequências

- **Revisão 2:** antes, um arquivo de chave inexistente caía no tratamento de `OSError` da conexão e era reportado como "host inalcançável" (código 2). Agora o arquivo é verificado antes de conectar e o erro é de uso (código 3), porque o problema está na chamada, não no host.
