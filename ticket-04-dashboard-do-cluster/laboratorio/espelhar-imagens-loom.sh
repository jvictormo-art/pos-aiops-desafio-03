#!/usr/bin/env bash
# Simula, no cluster de laboratório, o espelhamento que o Loom faz no parque:
# imagem pública → registry.metacortex.io (regra 3.7 do padrão de manifests).
# O Loom "espelha, escaneia e republica"; aqui a republicação acrescenta
# rótulos de procedência à imagem.
#
# O registry interno não existe fora da ficção do desafio. Em vez de trocar
# os manifests para a imagem pública (o que violaria a regra 3.7), a imagem
# é baixada, republicada com o nome interno e carregada direto no nó do
# kind. Como a tag não é :latest, o kubelet usa imagePullPolicy IfNotPresent
# e encontra a imagem no nó, sem tentar o pull.
#
# Uso: ./espelhar-imagens-loom.sh [nome-do-cluster-kind]

set -euo pipefail
CLUSTER="${1:-metacortex-lab}"
PLATAFORMA="linux/$(docker exec "$CLUSTER-control-plane" uname -m | sed 's/aarch64/arm64/;s/x86_64/amd64/')"

# origem pública                     → nome interno usado nos manifests
ESPELHOS=(
  "fabricioveronez/fake-shop:v1        registry.metacortex.io/orion/fake-shop:1.0.0"
  "fabricioveronez/kube-news:v1.0.0    registry.metacortex.io/nyx/kube-news:1.0.0"
)

for linha in "${ESPELHOS[@]}"; do
  read -r origem interno <<<"$linha"
  echo "→ $origem  ⇒  $interno"
  docker pull -q --platform "$PLATAFORMA" "$origem" >/dev/null
  # O Loom republica (não só re-etiqueta): a imagem interna ganha rótulos de
  # procedência e, com isso, um ID próprio. Isso também importa no kind: o
  # kubelet 1.36 guarda registro dos pulls que ele fez, e uma imagem com o
  # mesmo ID de uma já baixada da internet (kube-news:v1, usada nos chamados do
  # Ticket 02) não é tratada como pré-carregada; ele tenta o pull e falha.
  printf 'FROM %s\nLABEL org.metacortex.loom.origem="%s" org.metacortex.loom.espelhado-em="%s"\n' \
    "$origem" "$origem" "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
    | docker build -q --platform "$PLATAFORMA" -t "$interno" - >/dev/null
  # `kind load docker-image` importa com --all-platforms e falha quando a imagem
  # é multiplataforma e só a arquitetura local foi baixada. Exportar só a
  # plataforma do nó evita o problema.
  arquivo="$(mktemp -t loom).tar"
  docker save --platform "$PLATAFORMA" -o "$arquivo" "$interno"
  kind load image-archive "$arquivo" --name "$CLUSTER" >/dev/null
  rm -f "$arquivo"
done

docker exec "$CLUSTER-control-plane" crictl images | grep registry.metacortex.io
