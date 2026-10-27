# ADR-002 — Como falar com a API do Kubernetes

| Campo | Valor |
|---|---|
| Status | aceito |
| Data | 2026-09-17 (registrado como ADR próprio em 2026-10-27; origem: `spec/spec-decisoes.md`, Decisão 2) |
| Decisão em aberto do enunciado | "Como falar com a API do Kubernetes: cliente oficial da linguagem, kubectl como subprocesso, ou HTTP direto com o apiserver" |

## Decisão

**Escolhido**: biblioteca cliente oficial Python (`kubernetes` no PyPI, gerada a partir da OpenAPI spec do projeto).


**Por quê**: ela resolve autenticação, contexto e tipagem do jeito que o ticket pede que seja resolvido — uma vez, corretamente, sem reimplementar. `kubernetes.config.load_kube_config()` lê o `current-context` do kubeconfig e lida nativamente com certificado-cliente, token, e plugins `exec` (usados por autenticação de nuvem) sem código adicional. Erros vêm como `ApiException` com `status` HTTP inspecionável — essencial para diferenciar programaticamente "cluster fora do ar" (erro de conexão) de "permissão negada" (403) de "recurso não encontrado" (404), que é exatamente o comportamento que os critérios de aceite exigem.

## Alternativas descartadas

### Alternativa descartada A — `kubectl` como subprocesso, lendo a saída em JSON

- **O que se ganha**: zero dependência nova — todo operador já tem `kubectl` instalado, e a saída `-o json` é um contrato estável e testado pela própria comunidade Kubernetes. Não exige aprender a API gerada (que é grande e, em partes, verbosa).

- **O que se perde**: cada chamada gasta o custo de um processo novo (mais lento que uma chamada de biblioteca em memória). Mais importante: o erro de `kubectl` chega como texto em stderr mais um código de saída — para diferenciar "cluster inalcançável" de "403 Forbidden neste recurso" seria necessário fazer *string matching* na mensagem de erro do kubectl, que muda de formato entre versões e é exatamente o tipo de acoplamento frágil que o Ticket 02 já identificou como antipadrão de triagem (ler texto de erro para decidir causa, em vez de ler o dado estruturado). E se a decisão de atualização evoluir para watch/informer no futuro, subprocess não tem caminho — teria que reimplementar do zero.

### Alternativa descartada B — HTTP direto ao apiserver

- **O que se ganha**: controle total sobre a requisição, nenhuma dependência do `kubectl` nem do cliente gerado, superfície mínima.

- **O que se perde**: seria necessário reimplementar manualmente a leitura do kubeconfig para os múltiplos tipos de autenticação que ele pode conter — certificado cliente, token estático, e plugins `exec` (comuns em provedores de nuvem, que executam um binário externo para obter um token temporário). Isso é precisamente o trabalho que o ticket cita como caro e específico ("como ela conversa com o host remoto... é decisão sua, com consequência") — e reimplementá-lo mal significa um bug de autenticação sutil e recorrente, exatamente o tipo de manutenção cara que a proposta busca evitar ao delegar essa responsabilidade a uma biblioteca mantida pelo próprio projeto Kubernetes.

## O que a implementação confirmou ou contestou

**Cliente oficial vs. subprocess/HTTP direto**: a decisão de usar o cliente oficial *quase* foi contestada pelo bug do `EndpointSlice` (item 2) — mas a correção (usar `_preload_content=False` para pegar o JSON bruto numa chamada específica) é possível justamente **porque** é o cliente oficial: ele expõe esse escape hatch de baixo nível quando o modelo tipado falha. Um cliente HTTP feito à mão não teria esse problema de tipagem, mas teria todos os outros (auth, contexto) que a Decisão 2 já descartou. A decisão se mantém, com uma nuance a mais registrada.
