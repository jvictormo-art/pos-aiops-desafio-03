#!/usr/bin/env bash
# Gera os kubeconfigs dos três cenários de falha do enunciado, a partir do
# contexto do cluster de laboratório. Saída em laboratorio/kubeconfigs/
# (ignorada pelo git: contém credenciais).
#
#   ./cenarios-de-falha.sh               inalcancavel + credencial-invalida
#                                        (só arquivos locais, nada muda no cluster)
#   ./cenarios-de-falha.sh platform-ro   cria no cluster a ServiceAccount
#                                        platform-ro com Role restrita e gera o
#                                        kubeconfig dela (escreve RBAC no cluster)
#
# Cenários:
#   inalcancavel        server aponta para https://127.0.0.1:1 (nada escuta)
#   credencial-invalida certificado de cliente autoassinado, que o cluster não reconhece
#   platform-ro         lê pods, eventos e namespaces; NÃO lê deployments nem services

set -euo pipefail
AQUI="$(cd "$(dirname "$0")" && pwd)"
CTX="${CTX:-kind-metacortex-lab}"
DEST="$AQUI/kubeconfigs"
mkdir -p "$DEST"

base() {  # kubeconfig mínimo, só com o contexto do laboratório e credenciais embutidas
  kubectl config view --minify --flatten --context "$CTX"
}

if [[ "${1:-}" != "platform-ro" ]]; then
  echo "→ inalcancavel.kubeconfig"
  base | sed -E 's#(server: )https://[^ ]+#\1https://127.0.0.1:1#' > "$DEST/inalcancavel.kubeconfig"

  echo "→ credencial-invalida.kubeconfig"
  tmp="$(mktemp -d)"
  openssl req -x509 -newkey rsa:2048 -nodes -days 1 -subj "/CN=credencial-invalida" \
    -keyout "$tmp/key.pem" -out "$tmp/cert.pem" 2>/dev/null
  cert="$(base64 < "$tmp/cert.pem" | tr -d '\n')"; key="$(base64 < "$tmp/key.pem" | tr -d '\n')"
  base | sed -E "s#(client-certificate-data: ).*#\1$cert#; s#(client-key-data: ).*#\1$key#" \
    > "$DEST/credencial-invalida.kubeconfig"
  rm -rf "$tmp"

  for f in inalcancavel credencial-invalida; do
    printf "   %-22s kubectl: " "$f"
    { kubectl --kubeconfig "$DEST/$f.kubeconfig" get ns --request-timeout=5s 2>&1 || true; } | tail -1 | cut -c1-120
  done
  exit 0
fi

echo "→ platform-ro: ServiceAccount + Role restrita no cluster"
kubectl --context "$CTX" apply -f - <<'EOF'
apiVersion: v1
kind: Namespace
metadata:
  name: metacortex-dashboard
---
apiVersion: v1
kind: ServiceAccount
metadata:
  name: platform-ro
  namespace: metacortex-dashboard
---
# Lê namespaces, pods e eventos; deployments, services e endpointslices ficam
# de fora, para provar que um 403 num painel não derruba os outros.
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: metacortex-platform-ro-restrito
rules:
  - apiGroups: [""]
    resources: [namespaces, pods, events]
    verbs: [get, list, watch]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: metacortex-platform-ro-restrito
roleRef: {apiGroup: rbac.authorization.k8s.io, kind: ClusterRole, name: metacortex-platform-ro-restrito}
subjects: [{kind: ServiceAccount, name: platform-ro, namespace: metacortex-dashboard}]
EOF
TOKEN="$(kubectl --context "$CTX" -n metacortex-dashboard create token platform-ro --duration=24h)"
base | python3 -c '
import sys, yaml
cfg = yaml.safe_load(sys.stdin)
cfg["users"] = [{"name": "platform-ro", "user": {"token": sys.argv[1]}}]
cfg["contexts"][0]["context"]["user"] = "platform-ro"
cfg["contexts"][0]["name"] = cfg["current-context"] = "platform-ro"
print(yaml.safe_dump(cfg, sort_keys=False))
' "$TOKEN" > "$DEST/platform-ro.kubeconfig"
for r in pods deployments services; do
  printf "   platform-ro pode listar %-12s %s\n" "$r:" "$(kubectl --kubeconfig "$DEST/platform-ro.kubeconfig" auth can-i list "$r" -n nyx-dev)"
done
