# Ticket 01 — Padrão de Manifests da Metacortex

Este documento mapeia e aponta onde está cada item solicitado no **Entregue** do Ticket 01:

| Item do Entregue | Arquivo / Diretório | Descrição |
|---|---|---|
| **Skill de Manifests** | [`skill/SKILL.md`](./skill/SKILL.md) | Skill `metacortex-manifest` com os modos de escrita e conferência |
| **Script Mecânico** | [`skill/check-manifest.py`](./skill/check-manifest.py) | Script de validação mecânica das regras que o Trivy não cobre |
| **Matriz de Regras** | [`skill/regras-buckets.md`](./skill/regras-buckets.md) | Mapeamento regra × balde (trivy, script, instrução, fora) |
| **Saída real: conferência do manifesto barrado** | [`saida/conferencia-nyx-barrado.md`](./saida/conferencia-nyx-barrado.md) | Trivy + script + leitura do repositório do kube-news para as probes |
| **YAML Defeituoso de Teste** | [`saida/nyx-barrado.yaml`](./saida/nyx-barrado.yaml) | Manifesto com falhas obrigatórias e proibidas para validação |
| **Saída real: manifests gerados (fake-shop, cliente orion)** | [`saida/manifests-orion/`](./saida/manifests-orion/) | Usados de novo no Ticket 04, onde sobem e respondem HTTP 200 |
| **Origem da skill** (fluxo, como foi produzida, ferramenta) | [`origem-e-curadoria.md`](./origem-e-curadoria.md), seção "Como a skill nasceu" | Conferência primeiro, Trivy antes do script, depois escrita; Claude Code |
| **Curadoria: linha entre script e instrução, regra por regra** | [`origem-e-curadoria.md`](./origem-e-curadoria.md) + [`skill/regras-buckets.md`](./skill/regras-buckets.md) | Tabela regra × balde (trivy, script, instrução, fora) com justificativa |
| **Curadoria: o que o Trivy já cobria** | [`origem-e-curadoria.md`](./origem-e-curadoria.md), seção "O que o Trivy já cobria" | 2.1, 3.1, 3.2, 3.6; KSV-0125 suprimido |
| **Curadoria: corpo da skill × arquivo sob demanda** | [`origem-e-curadoria.md`](./origem-e-curadoria.md), seções "O que ficou no corpo" e "O que virou arquivo de apoio" | |
| **Curadoria: o que não foi empacotado e por quê** | [`origem-e-curadoria.md`](./origem-e-curadoria.md), seção "O que foi decidido NÃO empacotar" | Bloco 4, 2.5, 2.6, 3.5 |
| **Curadoria: permissões que a skill pede** | [`origem-e-curadoria.md`](./origem-e-curadoria.md), seção "Permissões que a skill pede" | |
| **Instalação no agente** | [`../.claude/skills/metacortex-manifest`](../.claude/skills/) | Symlink para `skill/`; usada com disparo automático no Ticket 04 |
| **Correção encontrada ao usar no Ticket 04** | [`origem-e-curadoria.md`](./origem-e-curadoria.md), última seção | Migração do fake-shop precisava do diretório do Prometheus; manifest e skill corrigidos |
| **Padrão da Metacortex** | [`Padrao de Manifests da Metacortex.md`](./Padrao%20de%20Manifests%20da%20Metacortex.md) | Documento-fonte corporativo de regras de manifests |

---
- **Agente:** Claude Code
- **Modelos:** Claude Opus 4.8 / Claude Sonnet 4.6
