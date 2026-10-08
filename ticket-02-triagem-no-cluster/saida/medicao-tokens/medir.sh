#!/usr/bin/env bash
# Mede tokens da triagem COM e SEM a skill metacortex-triage.
#
# Cada execução é uma sessão limpa do Claude Code em modo não interativo
# (claude -p), num diretório temporário que contém só:
#   - .mcp.json e .claude/settings.json do ticket (mesmo servidor MCP, mesmas permissões)
#   - .claude/skills/metacortex-triage/SKILL.md   ← apenas na variante "com"
# A única diferença entre as variantes é a presença da skill.
#
# Uso:   ./medir.sh [repeticoes]          (padrão: 3 por caso/variante)
#        MODELO=sonnet ./medir.sh 3
# Saída: runs/<caso>-<variante>-<n>.jsonl  (stream-json bruto de cada sessão)
#        e, ao final, resultado.md via consolidar.py

set -euo pipefail

REPETICOES="${1:-3}"
MODELO="${MODELO:-sonnet}"
CONTEXTO="kind-metacortex-lab"

AQUI="$(cd "$(dirname "$0")" && pwd)"
TICKET="$(cd "$AQUI/../.." && pwd)"
RUNS="$AQUI/runs"
mkdir -p "$RUNS"

# Casos: id | namespace exigido | prompt (o mesmo texto do chamado, sem pistas)
CASOS=(
  "A-nyx-prod|nyx-prod|a API do nyx-prod está reiniciando sozinha, verifica aí"
  "B-nyx-stg|nyx-stg|o Service do nyx-stg não está entregando tráfego"
)

# ── Autenticação: uma ANTHROPIC_API_KEY no ambiente tem precedência sobre o
# login do claude.ai. Por padrão ela é ignorada; USAR_API_KEY=1 a mantém.
if [[ -n "${ANTHROPIC_API_KEY:-}" && "${USAR_API_KEY:-0}" != "1" ]]; then
  echo "ANTHROPIC_API_KEY ignorada; usando o login do claude.ai (USAR_API_KEY=1 para usar a chave)." >&2
  unset ANTHROPIC_API_KEY
fi

# ── Pré-checagem: cluster de lab no ar e cenários aplicados ──
if ! kubectl --context "$CONTEXTO" get ns >/dev/null 2>&1; then
  echo "Cluster $CONTEXTO inalcançável. Suba o Docker e o kind antes de medir." >&2
  exit 1
fi
for caso in "${CASOS[@]}"; do
  ns="$(cut -d'|' -f2 <<<"$caso")"
  if ! kubectl --context "$CONTEXTO" get ns "$ns" >/dev/null 2>&1; then
    echo "Namespace $ns não existe. Aplique o cenário: kubectl --context $CONTEXTO apply -f $TICKET/manifests/" >&2
    exit 1
  fi
done

# Ferramentas que o agente NÃO pode usar em nenhuma variante: sem elas o
# "sem skill" poderia contornar o MCP com kubectl via Bash e a comparação
# deixaria de medir o mesmo caminho.
BLOQUEADAS="Bash,Edit,Write,NotebookEdit,WebFetch,WebSearch,Agent,mcp__kubernetes__kubectl_apply,mcp__kubernetes__kubectl_create,mcp__kubernetes__kubectl_patch,mcp__kubernetes__kubectl_scale,mcp__kubernetes__kubectl_rollout,mcp__kubernetes__install_helm_chart,mcp__kubernetes__upgrade_helm_chart,mcp__kubernetes__helm_template_apply,mcp__kubernetes__helm_template_uninstall,mcp__kubernetes__port_forward,mcp__kubernetes__kubectl_context"
LIBERADAS="mcp__kubernetes__kubectl_get,mcp__kubernetes__kubectl_describe,mcp__kubernetes__kubectl_logs,Skill,Read"

rodar() {
  local id="$1" prompt="$2" variante="$3" n="$4"
  local dir; dir="$(mktemp -d)"
  mkdir -p "$dir/.claude"
  cp "$TICKET/.mcp.json" "$dir/.mcp.json"
  cp "$TICKET/.claude/settings.json" "$dir/.claude/settings.json"
  if [[ "$variante" == "com" ]]; then
    mkdir -p "$dir/.claude/skills/metacortex-triage"
    cp "$TICKET/skill/SKILL.md" "$dir/.claude/skills/metacortex-triage/SKILL.md"
  fi

  local saida="$RUNS/$id-$variante-$n.jsonl"
  echo "→ $id / $variante skill / execução $n"
  # --setting-sources project: ignora settings, plugins e hooks do usuário,
  #   que injetariam contexto extra e distorceriam a contagem.
  # --strict-mcp-config: só o servidor kubernetes do ticket.
  # O diretório temporário não é "confiável", então o Claude Code ignora o
  # bloco allow do settings.json (o deny continua valendo); --allowedTools
  # libera explicitamente as mesmas ferramentas.
  (cd "$dir" && claude -p "$prompt" \
      --model "$MODELO" \
      --output-format stream-json --verbose \
      --setting-sources project \
      --strict-mcp-config --mcp-config .mcp.json \
      --allowedTools "$LIBERADAS" \
      --disallowedTools "$BLOQUEADAS" \
      --no-session-persistence \
      > "$saida" 2> >(grep -v "has not been trusted" >&2)) || echo "  (execução terminou com erro; ver $saida)" >&2
  rm -rf "$dir"
}

for caso in "${CASOS[@]}"; do
  id="$(cut -d'|' -f1 <<<"$caso")"
  prompt="$(cut -d'|' -f3 <<<"$caso")"
  for n in $(seq 1 "$REPETICOES"); do
    # Alterna a ordem para que cache/aquecimento não favoreça uma variante.
    if (( n % 2 )); then ordem=(sem com); else ordem=(com sem); fi
    for variante in "${ordem[@]}"; do
      rodar "$id" "$prompt" "$variante" "$n"
    done
  done
done

python3 "$AQUI/consolidar.py"
