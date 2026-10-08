"""
Testes da coleta + auditoria do metacortex-inventario sem SSH real.

Um SSH falso responde cada comando com (stdout, exit_code) do jeito que um
host real responderia. O cenário principal reproduz a VM da revisão: sem
systemd em execução (systemctl presente, responde "offline" com exit 1) e
sem o comando ss (exit 127).

Rodar: python3 -m unittest test_inventario.py -v
"""

import os
import unittest

import yaml

from inventario import Coletor, auditar, resumir

BASELINE = os.path.join(os.path.dirname(__file__), "baseline.yaml")

CMD_NAO_ENCONTRADO = ("", 127)


class SSHFalso:
    def __init__(self, respostas: dict):
        self._respostas = respostas

    def executar(self, cmd: str) -> tuple[str, int]:
        for prefixo, resposta in self._respostas.items():
            if cmd.startswith(prefixo):
                return resposta
        return CMD_NAO_ENCONTRADO


HOST_SAUDAVEL = {
    "hostname": ("vm-ok", 0),
    ". /etc/os-release": ("ubuntu 22.04", 0),
    "uname -r": ("6.5.0-41-generic", 0),
    "test -d /run/systemd/system": ("", 0),
    "systemctl list-units --type=service": (
        "ssh.service loaded active running OpenSSH\n"
        "containerd.service loaded active running containerd\n"
        "node_exporter.service loaded active running node_exporter\n"
        "chrony.service loaded active running chrony", 0),
    "systemctl list-units --type=socket": ("dbus.socket loaded active listening D-Bus", 0),
    "cat /proc/swaps": ("Filename\tType\tSize\tUsed\tPriority", 0),
    "ss -tlnp": (
        "State  Recv-Q Send-Q Local Address:Port Peer Address:Port Process\n"
        "LISTEN 0      128    0.0.0.0:22         0.0.0.0:*\n"
        "LISTEN 0      128    10.0.0.5:9100      0.0.0.0:*", 0),
    "test -e ~/.ssh/authorized_keys": ("", 0),
    "cat ~/.ssh/authorized_keys": ("ssh-ed25519 AAAA ops@metacortex-platform", 0),
    "sshd -T": ("permitrootlogin no", 0),
    "timedatectl show": ("NTPSynchronized=yes\nNTPService=chronyd", 0),
}

# VM da revisão: systemctl existe mas o systemd não é o PID 1, e não há ss.
HOST_SEM_SYSTEMD_SEM_SS = {
    "hostname": ("vm-minima", 0),
    ". /etc/os-release": ("ubuntu 22.04", 0),
    "uname -r": ("6.5.0-41-generic", 0),
    "test -d /run/systemd/system": ("", 1),
    "systemctl is-system-running": ("offline", 1),
    "systemctl list-units": ("", 1),
    "cat /proc/swaps": ("Filename\tType\tSize\tUsed\tPriority", 0),
    "ss -tlnp": CMD_NAO_ENCONTRADO,
    "test -e ~/.ssh/authorized_keys": ("", 0),
    "cat ~/.ssh/authorized_keys": ("ssh-ed25519 AAAA ops@metacortex-platform", 0),
    "sshd -T": ("", 1),
    "timedatectl": ("", 1),
}


def rodar(respostas: dict) -> dict[tuple, dict]:
    with open(BASELINE) as f:
        baseline = yaml.safe_load(f)
    dados = Coletor(SSHFalso(respostas)).coletar_tudo("10.0.0.5")
    conformidade = auditar(baseline, dados)
    return conformidade


def vereditos(conformidade: list[dict], regra: str) -> set[str]:
    return {c["veredito"] for c in conformidade if c["regra"] == regra}


class TestHostSemSystemdSemSs(unittest.TestCase):
    def setUp(self):
        self.conf = rodar(HOST_SEM_SYSTEMD_SEM_SS)

    def test_servicos_proibidos_nao_verificado(self):
        self.assertEqual(vereditos(self.conf, "servicos.proibidos"), {"nao_verificado"})

    def test_servicos_ativos_nao_verificado(self):
        self.assertEqual(vereditos(self.conf, "servicos.ativos"), {"nao_verificado"})

    def test_regras_de_porta_nao_verificado(self):
        self.assertEqual(vereditos(self.conf, "portas_em_escuta.publicas_permitidas"), {"nao_verificado"})
        self.assertEqual(vereditos(self.conf, "portas_em_escuta.somente_rede_interna"), {"nao_verificado"})

    def test_todo_nao_verificado_tem_motivo(self):
        for c in self.conf:
            if c["veredito"] == "nao_verificado":
                self.assertTrue(c.get("motivo"), c)

    def test_nada_sem_coleta_vira_conforme(self):
        conformes = {c["regra"] for c in self.conf if c["veredito"] == "conforme"}
        self.assertFalse(conformes & {
            "servicos.ativos", "servicos.proibidos",
            "portas_em_escuta.publicas_permitidas", "portas_em_escuta.somente_rede_interna",
            "ssh.login_de_root", "ntp.sincronizado",
        })


class TestFalhasPontuais(unittest.TestCase):
    def test_list_units_falha_com_systemd_presente(self):
        respostas = dict(HOST_SAUDAVEL)
        respostas["systemctl list-units --type=socket"] = ("", 1)
        conf = rodar(respostas)
        self.assertEqual(vereditos(conf, "servicos.proibidos"), {"nao_verificado"})

    def test_proc_swaps_ilegivel(self):
        respostas = dict(HOST_SAUDAVEL)
        respostas["cat /proc/swaps"] = ("", 1)
        self.assertEqual(vereditos(rodar(respostas), "swap.habilitado"), {"nao_verificado"})

    def test_authorized_keys_ilegivel(self):
        respostas = dict(HOST_SAUDAVEL)
        respostas["cat ~/.ssh/authorized_keys"] = ("", 1)
        self.assertEqual(vereditos(rodar(respostas), "chaves_ssh.emitidas_por"), {"nao_verificado"})

    def test_authorized_keys_inexistente_e_desvio(self):
        respostas = dict(HOST_SAUDAVEL)
        respostas["test -e ~/.ssh/authorized_keys"] = ("", 1)
        self.assertEqual(vereditos(rodar(respostas), "chaves_ssh.emitidas_por"), {"desvio"})

    def test_os_release_ilegivel(self):
        respostas = dict(HOST_SAUDAVEL)
        respostas[". /etc/os-release"] = ("", 1)
        conf = rodar(respostas)
        self.assertEqual(vereditos(conf, "so.distribuicao"), {"nao_verificado"})
        self.assertEqual(vereditos(conf, "so.versao_minima"), {"nao_verificado"})


class TestHostSaudavel(unittest.TestCase):
    def test_tudo_conforme(self):
        conf = rodar(HOST_SAUDAVEL)
        self.assertEqual(resumir(conf)["desvio"], 0, [c for c in conf if c["veredito"] != "conforme"])
        self.assertEqual(resumir(conf)["nao_verificado"], 0)

    def test_servico_proibido_ativo_e_desvio(self):
        respostas = dict(HOST_SAUDAVEL)
        respostas["systemctl list-units --type=socket"] = ("telnet.socket loaded active listening telnet", 0)
        self.assertIn("desvio", vereditos(rodar(respostas), "servicos.proibidos"))

    def test_porta_interna_exposta_e_desvio(self):
        respostas = dict(HOST_SAUDAVEL)
        respostas["ss -tlnp"] = ("LISTEN 0 128 0.0.0.0:22 0.0.0.0:*\nLISTEN 0 128 0.0.0.0:9100 0.0.0.0:*", 0)
        conf = rodar(respostas)
        self.assertEqual(vereditos(conf, "portas_em_escuta.somente_rede_interna"), {"desvio"})
        self.assertEqual(vereditos(conf, "portas_em_escuta.publicas_permitidas"), {"desvio"})


if __name__ == "__main__":
    unittest.main()
