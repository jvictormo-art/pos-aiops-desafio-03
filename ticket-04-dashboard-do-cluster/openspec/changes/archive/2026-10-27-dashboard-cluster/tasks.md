# Tasks

> Transcrição de `spec/tarefas.md` (T1–T8, 2026-09-17), todas concluídas antes da transcrição.

## 1. Preparação e leitura

- [x] 1.1 Subir workload real no cluster de laboratório (T1) — verificado: pods saudáveis e quebrados no `kind-metacortex-lab`
- [x] 1.2 `ClusterReader` só com verbos de leitura (T2) — verificado: nenhum `create_`/`patch_`/`delete_`/`replace_` no código
- [x] 1.3 Erro tipado por painel (T3) — verificado: os cenários de falha não derrubam a tela

## 2. Interface

- [x] 2.1 TUI com os cinco painéis, seletor, busca e rodapé (T4) — verificado: `evidencia/01`–`05`
- [x] 2.2 Polling de 5 s sem bloquear a interface (T5) — verificado: falha de um ciclo não trava os seguintes

## 3. Validação

- [x] 3.1 Evidência contra cluster real, incluindo os cenários de falha (T6) — verificado: `evidencia/06`–`08`
- [x] 3.2 Registro das skills (T7) — verificado: `saida/skills-neste-projeto.md`
- [x] 3.3 Arquivo final com as correções da spec (T8) — verificado: `spec/arquivo-final.md`
