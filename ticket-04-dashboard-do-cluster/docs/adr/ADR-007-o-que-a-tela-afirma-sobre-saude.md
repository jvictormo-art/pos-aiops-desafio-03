# ADR-007 — O que a tela pode afirmar sobre a saúde de um objeto

| Campo | Valor |
|---|---|
| Status | aceito |
| Data | 2026-10-27 (revisão 2; change OpenSpec `leitura-garantida-e-saude-honesta`) |
| Exigência do enunciado | "'Pronto' não significa 'saudável'. [...] Defina o quanto o dashboard pode afirmar sobre a saúde de um objeto a partir do que a API devolve." |

## Contexto

A versão 1.0 não respondeu a esta pergunta, e a auditoria da revisão 2 encontrou a lacuna. A API só sabe o que o kubelet observa: o container está rodando, quantas vezes reiniciou, e se a **readinessProbe** passou. Quando não há readinessProbe (é o caso do fake-shop do enunciado, sem endpoint de saúde, e do Postgres de apoio), o pod fica "pronto" assim que o processo sobe, mesmo que a aplicação ainda não atenda ou esteja quebrada.

## Decisão

1. **Vocabulário da API, nunca "saudável".** A tela usa os termos do Kubernetes: `READY`, `PRONTOS/DESEJADOS`, a condição `Available`, e "sem endpoint". Nenhuma tela, coluna ou mensagem diz "saudável", "ok" ou "healthy".
2. **"Pronto sem probe" é sinalizado.** Quando um pod está pronto e algum container dele não tem readinessProbe, o READY aparece com asterisco (`1/1*`), e uma legenda fixa explica: `* pronto sem readinessProbe: só indica que o processo subiu`.
3. **Sem checagem ativa.** A aplicação não chama `/health` nem faz requisição à aplicação: só lê a API.

## Alternativas consideradas

### A. Mostrar um semáforo "saudável / com problema" derivado de fase + READY + restarts

- **Ganha:** leitura mais rápida para quem chega no chamado.
- **Perde:** afirma algo que a API não sabe. Um fake-shop sem probe com o banco fora do ar apareceria verde. É exatamente o erro que o enunciado aponta.

### B. Chamar o endpoint de saúde da aplicação (via proxy do apiserver)

- **Ganha:** uma afirmação real de saúde, quando a aplicação tem `/health`.
- **Perde:** só funciona para aplicações com endpoint (o fake-shop não tem); exige permissão `pods/proxy`, que é mais do que leitura de objetos; e transforma a tela de leitura do estado em monitoração ativa, fora do escopo.

### C. Vocabulário da API + marca de "pronto sem probe" (escolhida)

- **Ganha:** a tela nunca afirma mais do que sabe, e mostra onde "pronto" é mais fraco do que parece.
- **Perde:** o operador ainda precisa interpretar; a marca não diz se a aplicação está bem, só que o Kubernetes não tem como saber.

## Consequências

- O resumo do pod carrega `tem_readiness` (todas as probes presentes nos containers), lido de `spec.containers[].readinessProbe`.
