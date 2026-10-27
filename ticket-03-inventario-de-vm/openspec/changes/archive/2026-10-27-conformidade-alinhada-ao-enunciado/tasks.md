# Tasks

## 1. Testes primeiro

- [x] 1.1 Ajustar `test_inventario.py` para o novo contrato: uma entrada por regra, agregação de `servicos.ativos`/`servicos.proibidos`, resumo somando 11, falha inesperada isolada por item, Markdown no formato do enunciado — verificação: os testes novos falham contra o código atual

## 2. Implementação

- [x] 2.1 Isolar cada coletor: exceção vira `None` com motivo "falha inesperada na coleta (<tipo>)" — verificação: teste de timeout num coletor passa e as outras regras são avaliadas
- [x] 2.2 Reescrever `auditar()` com uma entrada por regra e agregação dos itens — verificação: testes de conformidade passam; `len(conformidade) == 11`
- [x] 2.3 Ajustar `renderizar_markdown()` ao formato do enunciado (título, horário, tabela Não verificado de duas colunas, motivo acentuado) — verificação: teste de formato passa
- [x] 2.4 Validar o arquivo da chave antes de conectar (código 3) e especializar as mensagens de falha de conexão — verificação: execução com chave inexistente sai 3; endereço errado, porta fechada e chave recusada saem 2 com mensagens distintas

## 3. Evidência real

- [x] 3.1 Preparar a VM Ubuntu 24.04 (Lima) conforme o baseline e auditar duas vezes — verificação: 0 desvios, código 0, conformidade idêntica nas duas execuções
- [x] 3.2 Auditar a VM de teste com desvios — verificação: código 1, cada desvio com a severidade do baseline
- [x] 3.3 Auditar a VM mínima (sem systemd e sem `ss`) — verificação: serviços e portas como `nao_verificado`, nunca `conforme`
- [x] 3.4 Registrar os três casos de host inalcançável (endereço errado, chave recusada, SSH fora do ar) e a chave inexistente — verificação: códigos 2, 2, 2 e 3, stdout vazio, mensagem específica
- [x] 3.5 Confirmar que o conteúdo da chave não aparece em nenhuma saída — verificação: `grep` da chave em todos os arquivos de evidência retorna vazio

## 4. Documentação

- [x] 4.1 Atualizar TRD, ADRs, curadoria e README do ticket com o que mudou e o que a implementação revelou — verificação: README aponta cada item do Entregue
