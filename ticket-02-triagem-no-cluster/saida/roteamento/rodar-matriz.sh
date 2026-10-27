#!/usr/bin/env bash
# Testa a matriz de roteamento entre metacortex-manifest (Ticket 01) e
# metacortex-triage (Ticket 02) com as duas skills INSTALADAS em
# .claude/skills/ na raiz do desafio.
#
# Cada frase roda em sessão limpa (claude -p, sem histórico, sem settings,
# num diretório isolado com só as skills — sem acesso aos documentos do desafio,
# plugins ou hooks do usuário), REPETICOES vezes. O que se registra é a
# primeira chamada à ferramenta Skill: qual skill o agente escolheu só pela
# descrição. Bash/Edit/Write ficam bloqueados: o teste é de roteamento, não
# de execução, e nada pode ser alterado no disco ou no cluster.
#
# Uso:   [SKILLS=<dir com as skills>] ./rodar-matriz.sh [repeticoes] [rotulo] [arquivo-de-frases]
#        rotulo separa rodadas (ex.: "antes" e "depois" de mudar descriptions)
#        arquivo-de-frases: linhas "esperado|frase" (padrão: frases-enunciado.txt)
# Saída: logs/<rotulo>/<nn>-<n>.jsonl  e  resultado-<rotulo>.md

set -euo pipefail

REPETICOES="${1:-3}"
ROTULO="${2:-rodada1}"
MODELO="${MODELO:-sonnet}"

AQUI="$(cd "$(dirname "$0")" && pwd)"
RAIZ="$(cd "$AQUI/../../.." && pwd)"          # raiz do desafio, onde fica .claude/skills
MCP="$RAIZ/ticket-02-triagem-no-cluster/.mcp.json"
LOGS="$AQUI/logs/$ROTULO"
mkdir -p "$LOGS"

if [[ -n "${ANTHROPIC_API_KEY:-}" && "${USAR_API_KEY:-0}" != "1" ]]; then
  echo "ANTHROPIC_API_KEY ignorada; usando o login do claude.ai." >&2
  unset ANTHROPIC_API_KEY
fi


ARQ_FRASES="${3:-$AQUI/frases-enunciado.txt}"
FRASES=()
while IFS='|' read -r _esperado frase; do
  [[ -n "$frase" ]] && FRASES+=("$frase")
done < "$ARQ_FRASES"

# Workspace isolado: só as skills (copiadas de SKILLS, padrão = as instaladas)
# e o manifesto citado numa frase reformulada. Rodar dentro do repositório
# deixava o agente achar esta própria matriz (o gabarito) com Glob/Grep.
SKILLS="${SKILLS:-$RAIZ/.claude/skills}"
WS="$(mktemp -d)"
trap 'rm -rf "$WS"' EXIT
mkdir -p "$WS/.claude/skills" "$WS/ticket-01-padrao-de-manifests/saida"
for s in metacortex-manifest metacortex-triage; do cp -RL "$SKILLS/$s" "$WS/.claude/skills/$s"; done
cp "$RAIZ/ticket-01-padrao-de-manifests/saida/nyx-barrado.yaml" "$WS/ticket-01-padrao-de-manifests/saida/"
(cd "$WS" && git init -q)  # raiz de projeto própria: nada acima dela é lido

for i in "${!FRASES[@]}"; do
  nn=$(printf "%02d" $((i + 1)))
  for n in $(seq 1 "$REPETICOES"); do
    echo "→ [$nn] ${FRASES[$i]}  (execução $n)"
    (cd "$WS" && claude -p "${FRASES[$i]}" \
        --model "$MODELO" \
        --output-format stream-json --verbose \
        --setting-sources project \
        --strict-mcp-config --mcp-config "$MCP" \
        --allowedTools "Skill,Read,Glob,Grep,mcp__kubernetes__kubectl_get,mcp__kubernetes__kubectl_describe,mcp__kubernetes__kubectl_logs" \
        --disallowedTools "Bash,Edit,Write,NotebookEdit,WebFetch,WebSearch,Agent" \
        --max-turns 4 \
        --no-session-persistence \
        > "$LOGS/$nn-$n.jsonl" 2>/dev/null) || true
  done
done

python3 "$AQUI/consolidar-matriz.py" "$ROTULO" "$ARQ_FRASES"
