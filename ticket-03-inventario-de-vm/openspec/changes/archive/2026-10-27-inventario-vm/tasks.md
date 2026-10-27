# Tasks

> Transcrição de `spec/tarefas.md` (T1–T8, 2026-09-17), todas concluídas antes da transcrição.

## 1. Spec e estrutura

- [x] 1.1 Escrever spec de comportamento e decisões antes do código (T1) — verificado: `spec/spec-comportamento.md` e `spec/spec-decisoes.md` no commit "Add ferramenta metacortex-inventario e entregas do Ticket 03"
- [x] 1.2 Criar `baseline.yaml` e esqueleto da CLI com argparse e códigos de saída (T2) — verificado: `--help` funciona; host inexistente sai com código 2

## 2. Coleta, auditoria e saída

- [x] 2.1 Implementar o coletor SSH com um método por item (T3) — verificado: `coletar_tudo()` devolve os nove itens; chave não aparece em stderr
- [x] 2.2 Implementar a auditoria contra o baseline (T4) — verificado: `nao_verificado` nunca vira `conforme` para `ssh.login_de_root`
- [x] 2.3 Implementar JSON e Markdown a partir do mesmo dado (T5) — verificado: JSON válido e tabelas Markdown íntegras

## 3. Validação

- [x] 3.1 Ambiente de teste e execução real por SSH (T6) — verificado: `Dockerfile.test-vm` e saídas em `saida/evidencia/`
- [x] 3.2 Evidência dos critérios de aceite (T7) — verificado: desvios, host inalcançável, segunda execução, códigos de saída
- [x] 3.3 Arquivo final e curadoria (T8) — verificado: `spec/arquivo-final.md` e `saida/curadoria.md`
