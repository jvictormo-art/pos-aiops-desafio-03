# Design

## Context

O comportamento atual e as divergências estão em proposal.md. A coleta (`Coletor`) já devolve `None` para dado não coletado desde a change `coleta-nao-verificada`; o que muda é a forma da conformidade, a renderização, o isolamento de falhas por item e a validação dos argumentos.

## Goals / Non-Goals

**Goals:**
- Conformidade com exatamente uma entrada por regra (11 com o baseline atual).
- Markdown idêntico ao exemplo do enunciado.
- Nenhum erro inesperado de coleta derruba a execução.

**Non-Goals:**
- Mudar os comandos de coleta ou o baseline.
- Elevar privilégio (`sudo`) para reduzir `nao_verificado` (ADR-002, alternativa C).

## Decisions

- **Agregação por regra com `encontrado` em texto** (ADR-005). Alternativas: manter uma entrada por item (contraria o enunciado) ou `encontrado` estruturado por item (tipos diferentes por regra; o detalhe por item já está em `inventario`).
- **Isolamento por item:** cada método do coletor roda dentro de um invólucro que captura `Exception`, devolve `None` e guarda o motivo num mapa `motivos[item]`; a auditoria usa esse motivo quando existir e o motivo padrão do item caso contrário. Alternativa descartada: um único `try` em volta de `coletar_tudo()`, que é exatamente o comportamento atual (aborta tudo).
- **Motivo acentuado só no Markdown:** o JSON mantém o texto sem acento do exemplo do enunciado (`exige privilegio que o usuario da coleta nao tem`); o Markdown aplica a acentuação na renderização, como no exemplo. Alternativa descartada: acentuar também o JSON, divergindo do exemplo.
- **Validação da chave antes de conectar:** `os.access(path, R_OK)` antes de abrir a conexão; erro de uso sai com código 3. Mensagens de conexão a partir do tipo da exceção (`socket.gaierror` → endereço não resolve; `ConnectionRefusedError` / `NoValidConnectionsError` → conexão recusada; `socket.timeout` → tempo esgotado; `AuthenticationException` → autenticação recusada).

## Risks / Trade-offs

- [Consumidor que contava entradas por item] → não há consumidor em produção; a mudança está marcada como BREAKING na proposta e documentada no ADR-005.
- [Capturar `Exception` por item pode esconder bug do próprio coletor] → o motivo registra o tipo do erro e a regra aparece como `nao_verificado`, visível no relatório; os testes cobrem cada coletor separadamente.

## Migration Plan

Sem migração de dados. As evidências de `saida/evidencia/` são regeneradas com a nova versão; as anteriores ficam no histórico do git.
