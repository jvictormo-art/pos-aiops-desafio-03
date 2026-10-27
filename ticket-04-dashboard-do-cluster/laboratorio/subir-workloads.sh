#!/usr/bin/env bash
# Sobe no cluster de laboratório os dois workloads do pré-requisito do Ticket 04,
# com os manifests gerados pela skill metacortex-manifest:
#   kube-news (cliente nyx)   → nyx-dev     manifests: ticket-04-dashboard-do-cluster/manifests-kube-news/
#   fake-shop (cliente orion) → orion-prod  manifests: ticket-01-padrao-de-manifests/saida/manifests-orion/
#
# Os Secrets versionados trazem CHANGE_ME (regra 3.3: segredo não vai para o
# Git). Este script NÃO aplica esses arquivos: cria os Secrets direto no
# cluster com as credenciais do Postgres de laboratório (postgres-suporte.yaml),
# que podem ser trocadas pelas variáveis abaixo.
#
# Uso: ./subir-workloads.sh

set -euo pipefail
AQUI="$(cd "$(dirname "$0")" && pwd)"
RAIZ="$(cd "$AQUI/../.." && pwd)"
CTX="${CTX:-kind-metacortex-lab}"
K="kubectl --context $CTX"

NYX_DB_USER="${NYX_DB_USER:-kubedevnews}";  NYX_DB_PASS="${NYX_DB_PASS:-Pg#123}"
ORION_DB_USER="${ORION_DB_USER:-orion}";    ORION_DB_PASS="${ORION_DB_PASS:-orion-db-pass}"

echo "== 1. Imagens no registry interno (espelho do Loom)"
"$AQUI/espelhar-imagens-loom.sh"

echo "== 2. Namespaces e Postgres de apoio"
for ns in nyx-dev orion-prod; do $K create namespace "$ns" --dry-run=client -o yaml | $K apply -f - >/dev/null; done
$K apply -f "$AQUI/postgres-suporte.yaml"

echo "== 3. Secrets (fora do Git)"
$K -n nyx-dev create secret generic nyx-kube-news-db \
  --from-literal=db-user="$NYX_DB_USER" --from-literal=db-password="$NYX_DB_PASS" \
  --dry-run=client -o yaml | $K apply -f -
$K -n orion-prod create secret generic orion-fakeshop-db \
  --from-literal=db-user="$ORION_DB_USER" --from-literal=db-password="$ORION_DB_PASS" \
  --dry-run=client -o yaml | $K apply -f -

echo "== 4. Manifests gerados pela skill (sem o secret.yaml placeholder)"
aplicar() {  # aplicar <diretório>
  for f in "$1"/*.yaml; do
    [[ "$(basename "$f")" == "secret.yaml" ]] && continue
    $K apply -f "$f"
  done
}
aplicar "$RAIZ/ticket-04-dashboard-do-cluster/manifests-kube-news"
aplicar "$RAIZ/ticket-01-padrao-de-manifests/saida/manifests-orion"

echo "== 5. Remove a versão anterior do kube-news (nomes nyx-kubenews*), se existir"
$K -n nyx-dev delete deploy/nyx-kubenews svc/nyx-kubenews sa/nyx-kubenews \
  cm/nyx-kubenews-config secret/nyx-kubenews-db --ignore-not-found

echo "== 6. Esperando os rollouts"
$K -n nyx-dev rollout status deploy/nyx-kube-news --timeout=240s
$K -n orion-prod rollout restart deploy/orion-fakeshop >/dev/null
$K -n orion-prod rollout status deploy/orion-fakeshop --timeout=300s
$K get pods -n nyx-dev; $K get pods -n orion-prod
