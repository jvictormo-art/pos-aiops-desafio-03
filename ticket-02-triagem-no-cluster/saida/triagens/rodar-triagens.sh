#!/usr/bin/env bash
# Executa a skill metacortex-triage nos três chamados, pelo mcp-server-kubernetes.
#
# Cada chamado roda numa sessão limpa do Claude Code (claude -p) na raiz do
# desafio, onde as skills estão instaladas em .claude/skills/. O acesso ao
# cluster é SÓ pelo servidor MCP do ticket (.mcp.json, modo não destrutivo):
# Bash fica bloqueado, então o agente não tem como chamar kubectl direto.
#
# Uso:   ./rodar-triagens.sh
# Saída: logs/chamado-0N.jsonl (registro bruto da sessão) e
#        ../triagem-chamado-0N-*.md (transcrição: cada chamada MCP, o que o
#        cluster respondeu e o diagnóstico final)

set -euo pipefail
MODELO="${MODELO:-sonnet}"
AQUI="$(cd "$(dirname "$0")" && pwd)"
TICKET="$(cd "$AQUI/../.." && pwd)"
RAIZ="$(cd "$TICKET/.." && pwd)"
mkdir -p "$AQUI/logs"

if [[ -n "${ANTHROPIC_API_KEY:-}" && "${USAR_API_KEY:-0}" != "1" ]]; then
  unset ANTHROPIC_API_KEY
fi
kubectl --context kind-metacortex-lab get ns nyx-prod orion-stg nyx-stg >/dev/null \
  || { echo "Cenários do Ticket 02 não aplicados no kind-metacortex-lab" >&2; exit 1; }

CHAMADOS=(
  "01-nyx-prod|Chamado 1, nyx-prod: a API do kube-news reinicia sozinha. O problema apareceu depois de um corte de custos que mudou os limites de recurso do namespace inteiro de uma vez."
  "02-orion-stg|Chamado 2, orion-stg: a loja do fake-shop parou depois de uma publicação do Loom. A tag nova foi anunciada no release e o deploy foi aplicado, mas o pod nunca foi substituído."
  "03-nyx-stg|Chamado 3, nyx-stg: o kube-news responde 503 para quem chama de fora. A aplicação está de pé e saudável, e mesmo assim ninguém chega nela."
)

for c in "${CHAMADOS[@]}"; do
  id="${c%%|*}"; texto="${c#*|}"
  echo "→ chamado $id"
  (cd "$RAIZ" && claude -p "$texto" \
      --model "$MODELO" \
      --output-format stream-json --verbose \
      --setting-sources project \
      --strict-mcp-config --mcp-config "$TICKET/.mcp.json" \
      --allowedTools "Skill,mcp__kubernetes__kubectl_get,mcp__kubernetes__kubectl_describe,mcp__kubernetes__kubectl_logs" \
      --disallowedTools "Bash,Edit,Write,NotebookEdit,WebFetch,WebSearch,Agent,Read,Glob,Grep" \
      --no-session-persistence \
      > "$AQUI/logs/chamado-$id.jsonl" 2>/dev/null) || true
done

python3 "$AQUI/transcrever.py"
