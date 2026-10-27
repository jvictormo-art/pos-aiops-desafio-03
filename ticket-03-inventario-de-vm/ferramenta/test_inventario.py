"""
Testes da coleta + auditoria do metacortex-inventario sem SSH real.

Um SSH falso responde cada comando com (stdout, exit_code) do jeito que um
host real responderia. O cenário principal reproduz a VM da revisão: sem
systemd em execução (systemctl presente, responde "offline" com exit 1) e
sem o comando ss (exit 127).

Rodar: python3 -m unittest test_inventario.py -v
"""

import os
import socket
import subprocess
import sys
import tempfile
import unittest

import yaml

from inventario import Coletor, auditar, renderizar_markdown, resumir

BASELINE = os.path.join(os.path.dirname(__file__), "baseline.yaml")

CMD_NAO_ENCONTRADO = ("", 127)


class SSHFalso:
    def __init__(self, respostas: dict):
        self._respostas = respostas

    def executar(self, cmd: str) -> tuple[str, int]:
        for prefixo, resposta in self._respostas.items():
            if cmd.startswith(prefixo):
                if isinstance(resposta, Exception):
                    raise resposta
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


def carregar_baseline() -> dict:
    with open(BASELINE) as f:
        return yaml.safe_load(f)


def coletar(respostas: dict) -> tuple[dict, list[dict]]:
    baseline = carregar_baseline()
    dados = Coletor(SSHFalso(respostas)).coletar_tudo("10.0.0.5")
    dados["_baseline_versao"] = baseline.get("versao", 1)
    return dados, auditar(baseline, dados)


def rodar(respostas: dict) -> list[dict]:
    return coletar(respostas)[1]


def entrada(conformidade: list[dict], regra: str) -> dict:
    achadas = [c for c in conformidade if c["regra"] == regra]
    assert len(achadas) == 1, f"{regra}: {len(achadas)} entradas"
    return achadas[0]


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


N_REGRAS = 11  # regras do baseline.yaml


class TestUmaEntradaPorRegra(unittest.TestCase):
    """Revisão 2: o enunciado pede uma entrada de conformidade por regra do baseline."""

    def test_host_saudavel_tem_uma_entrada_por_regra(self):
        conf = rodar(HOST_SAUDAVEL)
        self.assertEqual(len(conf), N_REGRAS)
        self.assertEqual(len({c["regra"] for c in conf}), N_REGRAS)

    def test_host_minimo_tem_uma_entrada_por_regra(self):
        self.assertEqual(len(rodar(HOST_SEM_SYSTEMD_SEM_SS)), N_REGRAS)

    def test_resumo_soma_o_numero_de_regras(self):
        r = resumir(rodar(HOST_SEM_SYSTEMD_SEM_SS))
        self.assertEqual(r["conforme"] + r["desvio"] + r["nao_verificado"], N_REGRAS)

    def test_servicos_ausentes_agregados_numa_entrada(self):
        respostas = dict(HOST_SAUDAVEL)
        respostas["systemctl list-units --type=service"] = (
            "ssh.service loaded active running OpenSSH\n"
            "chrony.service loaded active running chrony", 0)
        e = entrada(rodar(respostas), "servicos.ativos")
        self.assertEqual(e["veredito"], "desvio")
        self.assertEqual(e["severidade"], "alto")
        self.assertEqual(e["encontrado"], "ausente: containerd, node_exporter")

    def test_servico_proibido_ativo_agregado(self):
        respostas = dict(HOST_SAUDAVEL)
        respostas["systemctl list-units --type=socket"] = ("telnet.socket loaded active listening telnet", 0)
        e = entrada(rodar(respostas), "servicos.proibidos")
        self.assertEqual(e["veredito"], "desvio")
        self.assertEqual(e["encontrado"], "ativo: telnet.socket")

    def test_porta_interna_exposta(self):
        respostas = dict(HOST_SAUDAVEL)
        respostas["ss -tlnp"] = ("LISTEN 0 128 0.0.0.0:22 0.0.0.0:*\nLISTEN 0 128 0.0.0.0:9100 0.0.0.0:*", 0)
        e = entrada(rodar(respostas), "portas_em_escuta.somente_rede_interna")
        self.assertEqual((e["veredito"], e["esperado"], e["encontrado"]),
                         ("desvio", "9100 na rede interna", "9100 em 0.0.0.0"))


class TestFalhaInesperadaIsolada(unittest.TestCase):
    """Revisão 2: erro inesperado num item não derruba a execução."""

    def test_timeout_no_ss_vira_nao_verificado_e_o_resto_segue(self):
        respostas = dict(HOST_SAUDAVEL)
        respostas["ss -tlnp"] = socket.timeout("timed out")
        conf = rodar(respostas)
        e = entrada(conf, "portas_em_escuta.publicas_permitidas")
        self.assertEqual(e["veredito"], "nao_verificado")
        self.assertEqual(e["motivo"], f"falha inesperada na coleta ({type(socket.timeout()).__name__})")
        self.assertEqual(entrada(conf, "swap.habilitado")["veredito"], "conforme")
        self.assertEqual(len(conf), N_REGRAS)


class TestMarkdownNoFormatoDoEnunciado(unittest.TestCase):
    def setUp(self):
        dados, conf = coletar(HOST_SEM_SYSTEMD_SEM_SS)
        self.md = renderizar_markdown(dados, conf)
        self.linhas = self.md.splitlines()

    def test_titulo_e_linha_de_coleta(self):
        self.assertEqual(self.linhas[0], "# Inventário de vm-minima (10.0.0.5)")
        self.assertRegex(self.linhas[1], r"^Coletado em \d{4}-\d{2}-\d{2} \d{2}:\d{2} UTC · baseline v1$")

    def test_tabela_nao_verificado_com_duas_colunas(self):
        self.assertIn("| Regra | Motivo |", self.linhas)
        self.assertIn("| ssh.login_de_root | exige privilégio que o usuário da coleta não tem |", self.linhas)
        self.assertNotIn("| Regra | Esperado | Motivo |", self.linhas)

    def test_cada_regra_aparece_uma_vez_na_tabela(self):
        linhas_nv = [l for l in self.linhas if l.startswith("| servicos.ativos |")]
        self.assertEqual(len(linhas_nv), 1)


class TestCodigosDeSaidaDaCli(unittest.TestCase):
    """Executa a CLI de verdade: chave inexistente, endereço que não resolve, porta fechada."""

    CLI = os.path.join(os.path.dirname(__file__), "inventario.py")

    @classmethod
    def setUpClass(cls):
        import paramiko
        cls.tmp = tempfile.TemporaryDirectory()
        cls.chave = os.path.join(cls.tmp.name, "id_teste")
        paramiko.Ed25519Key  # garante que a lib carrega
        subprocess.run(["ssh-keygen", "-q", "-t", "ed25519", "-N", "", "-f", cls.chave], check=True)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def rodar_cli(self, *args):
        return subprocess.run([sys.executable, self.CLI, "--baseline", BASELINE, *args],
                              capture_output=True, text=True, timeout=60)

    def test_chave_inexistente_e_erro_de_uso(self):
        r = self.rodar_cli("--host", "127.0.0.1", "--user", "x", "--key", "/nao/existe/id_ed25519")
        self.assertEqual(r.returncode, 3)
        self.assertEqual(r.stdout, "")
        self.assertIn("arquivo da chave", r.stderr)
        self.assertNotIn("Traceback", r.stderr)

    def test_endereco_que_nao_resolve(self):
        r = self.rodar_cli("--host", "host-que-nao-existe.invalid", "--user", "x", "--key", self.chave)
        self.assertEqual(r.returncode, 2)
        self.assertEqual(r.stdout, "")
        self.assertIn("não resolve", r.stderr)
        self.assertNotIn("Traceback", r.stderr)

    def test_porta_fechada(self):
        r = self.rodar_cli("--host", "127.0.0.1", "--porta", "1", "--user", "x", "--key", self.chave)
        self.assertEqual(r.returncode, 2)
        self.assertIn("conexão recusada", r.stderr)
        self.assertNotIn("Traceback", r.stderr)

    def test_conteudo_da_chave_nunca_aparece(self):
        conteudo = open(self.chave).read().splitlines()[1]
        r = self.rodar_cli("--host", "127.0.0.1", "--porta", "1", "--user", "x", "--key", self.chave)
        self.assertNotIn(conteudo, r.stdout + r.stderr)


if __name__ == "__main__":
    unittest.main()
