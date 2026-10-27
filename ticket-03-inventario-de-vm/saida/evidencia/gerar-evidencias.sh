#!/usr/bin/env bash
# Gera as evidências de execução real do metacortex-inventario contra hosts
# alcançáveis por SSH, cobrindo cada critério de pronto do enunciado.
#
# Hosts do laboratório (ver docs/03-TRD.md, seção 10):
#   VM_CONFORME   VM Ubuntu 24.04 (Lima) preparada com ferramenta/preparar-vm-conforme.sh
#   VM_DESVIOS    container de ferramenta/Dockerfile.test-vm (desvios propositais), porta 2222
#   VM_MINIMA     container de ferramenta/Dockerfile.test-vm-minima (sem systemd, sem ss), porta 2223
#
# Uso: CHAVE=<chave do auditor> CHAVE_ESTRANHA=<chave não autorizada> ./gerar-evidencias.sh
#
# Cada arquivo .txt registra o comando, o código de retorno, stdout e stderr.
# O caminho da chave aparece como <chave-auditor> / <chave-nao-autorizada>.

set -uo pipefail

AQUI="$(cd "$(dirname "$0")" && pwd)"
FERRAMENTA="$AQUI/../../ferramenta"
CHAVE="${CHAVE:?informe CHAVE}"
CHAVE_ESTRANHA="${CHAVE_ESTRANHA:?informe CHAVE_ESTRANHA}"
VM_CONFORME="${VM_CONFORME:-192.168.64.2}"
VM_NAO_RESPONDE="${VM_NAO_RESPONDE:-192.168.64.250}"
LIMA_VM="${LIMA_VM:-metacortex-vm}"

registrar() {  # registrar <arquivo> <args da ferramenta...>
  local arquivo="$1"; shift
  local out err code
  out="$(mktemp)"; err="$(mktemp)"
  (cd "$FERRAMENTA" && python3 inventario.py "$@" >"$out" 2>"$err"); code=$?
  {
    local cmd="python3 inventario.py $*"
    cmd="${cmd//$CHAVE_ESTRANHA/<chave-nao-autorizada>}"
    cmd="${cmd//$CHAVE/<chave-auditor>}"
    echo "\$ $cmd"
    echo "[código de retorno: $code]"
    echo "--- stdout ---"
    cat "$out"
    echo "--- stderr ---"
    cat "$err"
  } > "$AQUI/$arquivo"
  rm -f "$out" "$err"
  printf "%-45s código %s\n" "$arquivo" "$code"
}

echo "== CP1 e CP5: host conforme, duas execuções seguidas"
registrar 01-conforme-execucao1-json.txt --host "$VM_CONFORME" --user auditor --key "$CHAVE" --format json
registrar 02-conforme-execucao1-md.txt   --host "$VM_CONFORME" --user auditor --key "$CHAVE" --format md
registrar 03-conforme-execucao2-json.txt --host "$VM_CONFORME" --user auditor --key "$CHAVE" --format json

echo "== CP2: host com desvios"
registrar 04-desvios-json.txt --host 127.0.0.1 --porta 2222 --user auditor --key "$CHAVE" --format json
registrar 05-desvios-md.txt   --host 127.0.0.1 --porta 2222 --user auditor --key "$CHAVE" --format md

echo "== CP3: dado não coletado (sem systemd em execução, sem ss)"
registrar 06-sem-systemd-sem-ss-md.txt   --host 127.0.0.1 --porta 2223 --user auditor --key "$CHAVE" --format md
registrar 07-sem-systemd-sem-ss-json.txt --host 127.0.0.1 --porta 2223 --user auditor --key "$CHAVE" --format json

echo "== CP4: host inalcançável"
registrar 08-inalcancavel-endereco-que-nao-resolve.txt --host vm-14.metacortex.invalid --user auditor --key "$CHAVE"
registrar 09-inalcancavel-ip-sem-resposta.txt          --host "$VM_NAO_RESPONDE" --user auditor --key "$CHAVE"
registrar 10-inalcancavel-chave-recusada.txt           --host "$VM_CONFORME" --user auditor --key "$CHAVE_ESTRANHA"
# SSH fora do ar no próprio host conforme: para o sshd e agenda a volta em 60 s.
limactl shell "$LIMA_VM" sudo sh -c 'systemd-run --quiet --on-active=60 systemctl start ssh.socket ssh.service; systemctl stop ssh.socket ssh.service' >/dev/null 2>&1
sleep 2
registrar 11-inalcancavel-ssh-fora-do-ar.txt           --host "$VM_CONFORME" --user auditor --key "$CHAVE"
sleep 62

echo "== Erros de uso (código 3)"
registrar 12-uso-chave-inexistente.txt --host "$VM_CONFORME" --user auditor --key /caminho/que/nao/existe
registrar 13-uso-argumento-faltando.txt --host "$VM_CONFORME" --user auditor

echo "== CP5: comparação das duas execuções do host conforme"
python3 - "$AQUI" > "$AQUI/14-segunda-execucao-mesmo-resultado.txt" <<'EOF'
import json, sys, os
d = sys.argv[1]
def carregar(nome):
    texto = open(os.path.join(d, nome)).read()
    corpo = texto.split("--- stdout ---\n", 1)[1].split("--- stderr ---", 1)[0]
    return json.loads(corpo)
a, b = carregar("01-conforme-execucao1-json.txt"), carregar("03-conforme-execucao2-json.txt")
print("Execução 1 coletada em:", a["host"]["coletado_em"])
print("Execução 2 coletada em:", b["host"]["coletado_em"])
print("conformidade idêntica:", a["conformidade"] == b["conformidade"])
print("resumo idêntico:      ", a["resumo"] == b["resumo"])
print("resumo:", json.dumps(a["resumo"], ensure_ascii=False))
for k in ("so", "kernel", "swap", "portas_em_escuta", "chaves_ssh", "ssh", "ntp"):
    print(f"inventario.{k} idêntico:", a["inventario"][k] == b["inventario"][k])
EOF
cat "$AQUI/14-segunda-execucao-mesmo-resultado.txt"

echo "== CP6: o conteúdo das chaves não aparece em nenhuma evidência"
{
  for chave in "$CHAVE" "$CHAVE_ESTRANHA"; do
    corpo="$(sed -n 2p "$chave")"
    if grep -rqF -- "$corpo" "$AQUI"/*.txt; then echo "VAZOU: conteúdo de chave encontrado"; else echo "ok: conteúdo da chave ausente de todas as evidências"; fi
  done
} | tee "$AQUI/15-chave-nao-aparece.txt"
