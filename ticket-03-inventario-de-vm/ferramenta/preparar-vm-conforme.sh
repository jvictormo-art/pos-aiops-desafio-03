#!/usr/bin/env bash
# Prepara uma VM Ubuntu 24.04 para ficar CONFORME ao baseline.yaml, para a
# evidência do critério "um host conforme sai sem nenhum desvio".
#
# Roda DENTRO da VM, como root. No laboratório, a VM é criada com Lima:
#   limactl start --name=metacortex-vm --network=vzNAT template:ubuntu-24.04
#   limactl shell metacortex-vm sudo bash -s -- "$(cat id_auditor.pub)" < preparar-vm-conforme.sh
#
# Argumento: a chave pública do usuário de auditoria. O comentário dela é
# trocado por auditor@metacortex-platform (regra chaves_ssh.emitidas_por).
#
# O que cada passo atende no baseline:
#   so / kernel            Ubuntu 24.04, kernel 6.8 (nada a fazer)
#   servicos.ativos        ssh, containerd, node_exporter, chrony
#   servicos.proibidos     telnet.socket e rpcbind.socket ausentes
#   swap.habilitado        nenhum swap ativo
#   portas_em_escuta       só 22 em endereço público; 9100 no IP interno
#   chaves_ssh             só chaves com "metacortex-platform" no comentário
#   ssh.login_de_root      PermitRootLogin no
#   ntp.sincronizado       chrony sincronizado

set -euo pipefail
PUBKEY="${1:?informe a chave pública do auditor}"

export DEBIAN_FRONTEND=noninteractive
apt-get update -qq
apt-get install -y -qq containerd chrony prometheus-node-exporter >/dev/null

# node_exporter: o pacote do Ubuntu chama a unidade de prometheus-node-exporter;
# o baseline exige node_exporter. Uma unidade com esse nome usa o mesmo binário,
# escutando só no IP interno da VM (não em 0.0.0.0).
IP_INTERNO="$(ip -4 -o addr show lima0 2>/dev/null | awk '{print $4}' | cut -d/ -f1)"
IP_INTERNO="${IP_INTERNO:-$(hostname -I | awk '{print $1}')}"
systemctl disable --now prometheus-node-exporter.service >/dev/null 2>&1 || true
cat > /etc/systemd/system/node_exporter.service <<EOF
[Unit]
Description=Prometheus node_exporter (rede interna)
After=network-online.target
Wants=network-online.target

[Service]
User=prometheus
ExecStart=/usr/bin/prometheus-node-exporter --web.listen-address=${IP_INTERNO}:9100
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF
systemctl daemon-reload
systemctl enable --now containerd chrony node_exporter >/dev/null

# Serviços proibidos: garantir que não existam.
systemctl disable --now telnet.socket rpcbind.socket >/dev/null 2>&1 || true

# Swap desabilitado.
swapoff -a
sed -i '/\sswap\s/s/^/#/' /etc/fstab

# SSH: login de root desabilitado na configuração efetiva.
echo "PermitRootLogin no" > /etc/ssh/sshd_config.d/10-metacortex.conf
systemctl restart ssh

# Usuário de auditoria, sem sudo, com a chave emitida pela plataforma.
id auditor >/dev/null 2>&1 || useradd -m -s /bin/bash auditor
install -d -m 700 -o auditor -g auditor /home/auditor/.ssh
echo "$(echo "$PUBKEY" | awk '{print $1, $2}') auditor@metacortex-platform" > /home/auditor/.ssh/authorized_keys
chown auditor:auditor /home/auditor/.ssh/authorized_keys
chmod 600 /home/auditor/.ssh/authorized_keys

# Esperar o chrony sincronizar (até 2 min).
for _ in $(seq 1 24); do
  [ "$(timedatectl show -p NTPSynchronized --value)" = "yes" ] && break
  sleep 5
done

echo "--- estado final"
systemctl is-active ssh containerd node_exporter chrony
timedatectl show -p NTPSynchronized -p NTPService
swapon --show | wc -l | xargs echo "dispositivos de swap:"
ss -tlnp | awk 'NR>1 {print $4}'
echo "IP interno: ${IP_INTERNO}"
