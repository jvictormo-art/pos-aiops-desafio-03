#!/usr/bin/env bash
# Roda uma tarefa do projeto do dashboard numa sessão gravada do Claude Code,
# na raiz do desafio, onde as skills dos Tickets 01 e 02 estão instaladas em
# .claude/skills/. O pedido nunca cita uma skill: o objetivo é observar quais
# disparam sozinhas, quais não disparam e quais aparecem onde não deviam.
#
# Uso: ./sessao.sh <id> "<pedido>" [perfil]
#   perfil "leitura"   : só lê arquivos e o cluster (MCP, modo não destrutivo)
#   perfil "manifests" : pode ler o repositório do projeto, escrever arquivos e
#                        rodar trivy/check-manifest; não pode usar kubectl
# Saída: logs/<id>.jsonl

set -euo pipefail
ID="$1"; PEDIDO="$2"; PERFIL="${3:-leitura}"
MODELO="${MODELO:-sonnet}"
AQUI="$(cd "$(dirname "$0")" && pwd)"
RAIZ="$(cd "$AQUI/../../.." && pwd)"
MCP="$RAIZ/ticket-02-triagem-no-cluster/.mcp.json"
mkdir -p "$AQUI/logs"
[[ -n "${ANTHROPIC_API_KEY:-}" && "${USAR_API_KEY:-0}" != "1" ]] && unset ANTHROPIC_API_KEY

LEITURA="Skill,Read,Glob,Grep,mcp__kubernetes__kubectl_get,mcp__kubernetes__kubectl_describe,mcp__kubernetes__kubectl_logs"
case "$PERFIL" in
  leitura)
    PERMITIDAS="$LEITURA"
    NEGADAS="Bash,Edit,Write,NotebookEdit,Agent"
    MODO="default" ;;
  manifests)
    PERMITIDAS="$LEITURA,Write,Edit,WebFetch,Bash(git clone:*),Bash(trivy config:*),Bash(python3:*),Bash(ls:*),Bash(cat:*),Bash(find:*),Bash(grep:*)"
    NEGADAS="Bash(kubectl:*),Bash(docker:*),Bash(rm:*),NotebookEdit,Agent"
    MODO="acceptEdits" ;;
  *) echo "perfil desconhecido: $PERFIL" >&2; exit 1 ;;
esac

echo "→ sessão $ID ($PERFIL)"
(cd "$RAIZ" && claude -p "$PEDIDO" \
    --model "$MODELO" \
    --output-format stream-json --verbose \
    --setting-sources project \
    --strict-mcp-config --mcp-config "$MCP" \
    --permission-mode "$MODO" \
    --allowedTools "$PERMITIDAS" \
    --disallowedTools "$NEGADAS" \
    --no-session-persistence \
    > "$AQUI/logs/$ID.jsonl" 2>/dev/null) || true

python3 - "$AQUI/logs/$ID.jsonl" <<'EOF'
import json, sys
ev = [json.loads(l) for l in open(sys.argv[1]) if l.strip()]
skills = [b["input"].get("skill") for e in ev if e.get("type") == "assistant"
          for b in e["message"]["content"] if b.get("type") == "tool_use" and b["name"] == "Skill"]
fim = next(e for e in reversed(ev) if e.get("type") == "result")
print("  skills disparadas:", skills or "nenhuma")
print("  turnos:", fim.get("num_turns"), "| custo US$", round(fim.get("total_cost_usd", 0), 4))
EOF
