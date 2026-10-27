#!/usr/bin/env python3
"""
metacortex-inventario — audita uma VM contra baseline.yaml via SSH.

Uso:
  python3 inventario.py \\
    --host   <ip_ou_hostname> \\
    --user   <usuario_ssh> \\
    --key    <caminho_chave_privada> \\
    [--baseline baseline.yaml] \\
    [--format json|md|both] \\
    [--porta 22]

Saída: stdout (JSON e/ou Markdown). Erros: stderr.

Códigos de saída:
  0  — host alcançado, sem desvios confirmados
  1  — host alcançado, há desvios
  2  — falha de conexão (endereço que não resolve, SSH fora do ar, timeout, chave recusada)
  3  — erro de uso (baseline inválido, chave ausente/ilegível/com senha, argumento faltando)

Dado que não pôde ser coletado vira nao_verificado com motivo (ADR-002); a
conformidade tem exatamente uma entrada por regra do baseline (ADR-005).
"""

from __future__ import annotations

import argparse
import json
import os
import re
import socket
import sys
from datetime import datetime, timezone

try:
    import paramiko
    import yaml
except ImportError as e:
    print(
        f"Erro: dependência ausente — {e}. Execute: pip3 install paramiko pyyaml",
        file=sys.stderr,
    )
    sys.exit(3)


# ──────────────────────────────────────────────────────────────────
#  SSH
# ──────────────────────────────────────────────────────────────────

class ErroDeUso(Exception):
    """Problema na chamada (não no host): sai com código 3."""


class SSHConexao:
    """Encapsula a conexão SSH. A chave privada nunca é exposta em logs ou erros.

    Cada tipo de falha vira uma mensagem que diz o que houve (ADR-004).
    """

    def __init__(self, host: str, usuario: str, chave_path: str, porta: int = 22):
        self.host = host
        self._client = paramiko.SSHClient()
        self._client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        alvo = f"{host}:{porta}"
        try:
            self._client.connect(
                hostname=host,
                username=usuario,
                key_filename=chave_path,
                port=porta,
                timeout=10,
                banner_timeout=10,
                auth_timeout=10,
                allow_agent=False,
                look_for_keys=False,
            )
        except paramiko.PasswordRequiredException:
            raise ErroDeUso("a chave privada está protegida por senha; use uma chave sem senha para a auditoria")
        except paramiko.AuthenticationException:
            raise ConnectionError(f"autenticação recusada em {alvo}: o host não aceitou o usuário ou a chave")
        except socket.gaierror:
            raise ConnectionError(f"endereço não resolve: {host}")
        except (paramiko.ssh_exception.NoValidConnectionsError, ConnectionRefusedError):
            raise ConnectionError(f"conexão recusada em {alvo}: nada escuta na porta SSH (serviço fora do ar?)")
        except socket.timeout:
            raise ConnectionError(f"tempo esgotado ao conectar em {alvo}: host desligado, inexistente ou filtrado")
        except paramiko.SSHException as e:
            raise ConnectionError(f"falha no protocolo SSH com {alvo}: {e}")
        except OSError as e:
            raise ConnectionError(f"host inalcançável: {alvo} ({e.strerror or type(e).__name__})")

    def executar(self, cmd: str) -> tuple[str, int]:
        """Executa um comando de leitura no host remoto. Retorna (stdout, exit_code)."""
        _, stdout, _ = self._client.exec_command(cmd, timeout=30)
        saida = stdout.read().decode(errors="replace").strip()
        codigo = stdout.channel.recv_exit_status()
        return saida, codigo

    def fechar(self):
        self._client.close()


# ──────────────────────────────────────────────────────────────────
#  COLETA
# ──────────────────────────────────────────────────────────────────

class Coletor:
    """Coleta dados de inventário via SSH. Apenas leitura — nada é modificado no host."""

    def __init__(self, ssh: SSHConexao):
        self._ssh = ssh

    def _run(self, cmd: str) -> tuple[str, int]:
        return self._ssh.executar(cmd)

    # Regra geral da coleta: comando que falha (exit != 0) ou não existe
    # devolve None — nunca um valor vazio que possa ser lido como "conforme".
    # A auditoria transforma None em nao_verificado com o motivo.

    def so(self) -> dict | None:
        saida, codigo = self._run('. /etc/os-release && echo "$ID $VERSION_ID"')
        partes = saida.split(None, 1)
        if codigo != 0 or len(partes) < 2:
            return None
        return {"distribuicao": partes[0], "versao": partes[1].strip()}

    def kernel(self) -> dict | None:
        saida, codigo = self._run("uname -r")
        if codigo != 0 or not saida:
            return None
        return {"versao": saida}

    def servicos(self) -> list[dict] | None:
        """Lista unidades ativas. None se o systemd não é o init em execução."""
        # /run/systemd/system só existe quando o systemd é o PID 1 (mesmo
        # teste do sd_booted()). O exit code de `systemctl is-system-running`
        # não serve: sem systemd em execução ele responde "offline" com exit 1,
        # o mesmo código de "degraded".
        _, codigo = self._run("test -d /run/systemd/system")
        if codigo != 0:
            return None

        lista = []
        for tipo in ("service", "socket"):
            saida, codigo = self._run(
                f"systemctl list-units --type={tipo} --state=active "
                f"--no-legend --plain --no-pager 2>/dev/null"
            )
            if codigo != 0:
                return None
            for linha in saida.splitlines():
                partes = linha.split()
                if not partes:
                    continue
                nome = partes[0]
                if nome.endswith(f".{tipo}"):
                    lista.append({"nome": nome, "tipo": tipo, "estado": "active"})
        return lista

    def swap(self) -> dict | None:
        saida, codigo = self._run("cat /proc/swaps")
        if codigo != 0:
            return None
        linhas = [l for l in saida.splitlines() if l and not l.startswith("Filename")]
        if not linhas:
            return {"habilitado": False, "tamanho": None}
        total_kb = 0
        for linha in linhas:
            partes = linha.split()
            if len(partes) >= 3:
                try:
                    total_kb += int(partes[2])
                except ValueError:
                    pass
        gb = total_kb / (1024 * 1024)
        mb = total_kb / 1024
        tamanho = f"{gb:.0f}G" if gb >= 1 else f"{mb:.0f}M"
        return {"habilitado": True, "tamanho": tamanho}

    def portas(self) -> list[dict] | None:
        """Portas TCP em LISTEN. None se o `ss` não existe ou falha."""
        saida, codigo = self._run("ss -tlnp 2>/dev/null")
        if codigo != 0:
            return None
        resultado = []
        for linha in saida.splitlines():
            partes = linha.split()
            if not partes or partes[0] != "LISTEN":
                continue
            if len(partes) < 4:
                continue
            endereco_porta = partes[3]
            idx = endereco_porta.rfind(":")
            if idx == -1:
                continue
            try:
                porta = int(endereco_porta[idx + 1:])
            except ValueError:
                continue
            bind = endereco_porta[:idx].strip("[]") or "*"
            processo = None
            m = re.search(r'users:\(\("([^"]+)"', linha)
            if m:
                processo = m.group(1)
            resultado.append({"porta": porta, "bind": bind, "processo": processo})
        return resultado

    def chaves_ssh(self) -> list[dict] | None:
        """Chaves do authorized_keys. [] se o arquivo não existe; None se não foi possível lê-lo."""
        _, existe = self._run("test -e ~/.ssh/authorized_keys")
        if existe != 0:
            return []
        saida, codigo = self._run("cat ~/.ssh/authorized_keys 2>/dev/null")
        if codigo != 0:
            return None
        chaves = []
        for linha in saida.splitlines():
            linha = linha.strip()
            if not linha or linha.startswith("#"):
                continue
            partes = linha.split(None, 2)
            if len(partes) >= 3:
                identificacao = partes[2].strip()
            elif len(partes) == 2:
                identificacao = "(sem comentário)"
            else:
                continue
            chaves.append({"identificacao": identificacao})
        return chaves

    def ssh_config(self) -> dict | None:
        """Configuração efetiva do sshd (`sshd -T`). Exige privilégio; sem ele, None."""
        saida, codigo = self._run("sshd -T 2>/dev/null | grep -i permitrootlogin")
        m = re.search(r'permitrootlogin\s+(\S+)', saida, re.IGNORECASE) if codigo == 0 else None
        if not m:
            return None
        valor = m.group(1).lower()
        return {"login_de_root": valor in ("yes", "without-password", "prohibit-password")}

    def ntp(self) -> dict | None:
        saida, codigo = self._run(
            "timedatectl show --property=NTPSynchronized,NTPService 2>/dev/null"
        )
        sincronizado = None
        mecanismo = None
        if codigo == 0 and saida:
            for linha in saida.splitlines():
                if "=" in linha:
                    k, _, v = linha.partition("=")
                    if k.strip() == "NTPSynchronized":
                        sincronizado = v.strip().lower() == "yes"
                    elif k.strip() == "NTPService":
                        mecanismo = v.strip() or None
        if sincronizado is None:
            # Reserva: timedatectl status
            saida2, codigo2 = self._run("timedatectl status 2>/dev/null")
            if codigo2 == 0:
                for linha in saida2.splitlines():
                    linha_l = linha.lower()
                    if "synchronized:" in linha_l or "system clock synchronized" in linha_l:
                        sincronizado = "yes" in linha_l
        if sincronizado is None:
            return None
        return {"sincronizado": sincronizado, "mecanismo": mecanismo}

    # Motivo de cada item quando o coletor devolve None.
    MOTIVOS = {
        "so": "/etc/os-release nao legivel",
        "kernel": "uname -r falhou",
        "servicos": "systemd nao disponivel ou nao acessivel",
        "swap": "/proc/swaps nao legivel",
        "portas_em_escuta": "comando ss nao disponivel ou falhou",
        "chaves_ssh": "authorized_keys existe mas nao pode ser lido",
        "ssh": "exige privilegio que o usuario da coleta nao tem",
        "ntp": "timedatectl nao disponivel",
    }

    def _coletar(self, item: str, coletor, motivos: dict):
        """Roda um coletor isolado: erro inesperado num item não derruba os outros."""
        try:
            valor = coletor()
        except Exception as e:  # noqa: BLE001 — o motivo registra o tipo do erro
            motivos[item] = f"falha inesperada na coleta ({type(e).__name__})"
            return None
        if valor is None:
            motivos[item] = self.MOTIVOS[item]
        return valor

    def coletar_tudo(self, host_address: str) -> dict:
        coletado_em = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        try:
            hostname, codigo = self._run("hostname")
        except Exception:  # noqa: BLE001 — hostname não é regra do baseline
            hostname, codigo = "", 1
        motivos: dict[str, str] = {}
        inv = {
            item: self._coletar(item, coletor, motivos)
            for item, coletor in (
                ("so", self.so),
                ("kernel", self.kernel),
                ("servicos", self.servicos),
                ("swap", self.swap),
                ("portas_em_escuta", self.portas),
                ("chaves_ssh", self.chaves_ssh),
                ("ssh", self.ssh_config),
                ("ntp", self.ntp),
            )
        }
        # Forma do enunciado para os itens não coletados de ssh e ntp.
        if inv["ssh"] is None:
            inv["ssh"] = {"login_de_root": None}
        if inv["ntp"] is None:
            inv["ntp"] = {"sincronizado": None, "mecanismo": None}
        return {
            "host": {
                "endereco": host_address,
                "hostname": (hostname if codigo == 0 else "") or host_address,
                "coletado_em": coletado_em,
            },
            "inventario": inv,
            "_motivos": motivos,
        }


# ──────────────────────────────────────────────────────────────────
#  AUDITORIA
# ──────────────────────────────────────────────────────────────────

WILDCARDS = {"0.0.0.0", "::", "*", ""}


def _versao_tuple(v: str) -> tuple:
    """'5.15.0-118-generic' → (5, 15, 0). '22.04' → (22, 4)."""
    partes = re.findall(r'\d+', str(v))
    return tuple(int(x) for x in partes[:3]) if partes else (0,)


def _lista(itens) -> str:
    return ", ".join(str(i) for i in itens)


def auditar(baseline: dict, dados: dict) -> list[dict]:
    """Compara inventário com baseline: exatamente uma entrada por regra (ADR-005).

    Dado não coletado (None no inventário) vira nao_verificado com o motivo
    registrado na coleta (ADR-002) — nunca conforme, nunca desvio.
    """
    esperado = baseline.get("esperado", {})
    severidades = baseline.get("severidade", {})
    inv = dados["inventario"]
    motivos = dados.get("_motivos", {})

    def sev(regra: str) -> str:
        for nivel, regras in severidades.items():
            if regra in regras:
                return nivel
        return "info"

    def ok(regra, esp, enc):
        return {"regra": regra, "esperado": esp, "encontrado": enc, "veredito": "conforme"}

    def desvio(regra, esp, enc):
        return {"regra": regra, "esperado": esp, "encontrado": enc, "veredito": "desvio", "severidade": sev(regra)}

    def nv(regra, esp, item):
        return {"regra": regra, "esperado": esp, "encontrado": None, "veredito": "nao_verificado",
                "motivo": motivos.get(item, Coletor.MOTIVOS[item])}

    resultado = []

    # ── so.distribuicao / so.versao_minima ──
    dist_esp = esperado.get("so", {}).get("distribuicao")
    versao_min = esperado.get("so", {}).get("versao_minima")
    so = inv["so"]
    if so is None:
        resultado.append(nv("so.distribuicao", dist_esp, "so"))
        resultado.append(nv("so.versao_minima", versao_min, "so"))
    else:
        resultado.append(ok("so.distribuicao", dist_esp, so["distribuicao"])
                         if so["distribuicao"] == dist_esp
                         else desvio("so.distribuicao", dist_esp, so["distribuicao"]))
        resultado.append(ok("so.versao_minima", versao_min, so["versao"])
                         if _versao_tuple(so["versao"]) >= _versao_tuple(versao_min)
                         else desvio("so.versao_minima", versao_min, so["versao"]))

    # ── kernel.versao_minima ──
    kernel_min = esperado.get("kernel", {}).get("versao_minima")
    if inv["kernel"] is None:
        resultado.append(nv("kernel.versao_minima", kernel_min, "kernel"))
    else:
        kernel_enc = inv["kernel"]["versao"]
        resultado.append(ok("kernel.versao_minima", kernel_min, kernel_enc)
                         if _versao_tuple(kernel_enc) >= _versao_tuple(kernel_min)
                         else desvio("kernel.versao_minima", kernel_min, kernel_enc))

    # ── servicos.ativos / servicos.proibidos (agregados por regra) ──
    servicos = inv["servicos"]
    ativos = esperado.get("servicos", {}).get("ativos", [])
    proibidos = esperado.get("servicos", {}).get("proibidos", [])
    esp_ativos = f"{_lista(ativos)} ativos"
    esp_proibidos = f"{_lista(proibidos)} inativos"
    if servicos is None:
        resultado.append(nv("servicos.ativos", esp_ativos, "servicos"))
        resultado.append(nv("servicos.proibidos", esp_proibidos, "servicos"))
    else:
        nomes = {s["nome"] for s in servicos}

        def presente(svc: str, tipo_padrao: str) -> bool:
            return svc in nomes or (f"{svc}.{tipo_padrao}" in nomes if "." not in svc else False)

        ausentes = [s for s in ativos if not presente(s, "service")]
        resultado.append(desvio("servicos.ativos", esp_ativos, f"ausente: {_lista(ausentes)}")
                         if ausentes else ok("servicos.ativos", esp_ativos, "todos ativos"))
        ligados = [s for s in proibidos if presente(s, "socket")]
        resultado.append(desvio("servicos.proibidos", esp_proibidos, f"ativo: {_lista(ligados)}")
                         if ligados else ok("servicos.proibidos", esp_proibidos, "nenhum ativo"))

    # ── swap.habilitado ──
    swap_esp = esperado.get("swap", {}).get("habilitado")
    if inv["swap"] is None:
        resultado.append(nv("swap.habilitado", swap_esp, "swap"))
    else:
        swap_enc = inv["swap"]["habilitado"]
        tamanho = inv["swap"].get("tamanho")
        enc_str = f"true ({tamanho})" if swap_enc and tamanho else swap_enc
        resultado.append(ok("swap.habilitado", swap_esp, swap_enc)
                         if swap_enc == swap_esp
                         else desvio("swap.habilitado", swap_esp, enc_str))

    # ── portas_em_escuta.* ──
    publicas_perm = esperado.get("portas_em_escuta", {}).get("publicas_permitidas", [])
    somente_int = esperado.get("portas_em_escuta", {}).get("somente_rede_interna", [])
    esp_pub = f"apenas {_lista(publicas_perm)} em endereço público"
    esp_int = f"{_lista(somente_int)} na rede interna"
    portas = inv["portas_em_escuta"]
    if portas is None:
        resultado.append(nv("portas_em_escuta.publicas_permitidas", esp_pub, "portas_em_escuta"))
        resultado.append(nv("portas_em_escuta.somente_rede_interna", esp_int, "portas_em_escuta"))
    else:
        nao_perm = [p for p in portas if p["bind"] in WILDCARDS and p["porta"] not in publicas_perm]
        resultado.append(
            desvio("portas_em_escuta.publicas_permitidas", esp_pub,
                   _lista(f"{p['porta']} em {p['bind'] or '*'}" for p in nao_perm))
            if nao_perm else
            ok("portas_em_escuta.publicas_permitidas", esp_pub, "nenhuma outra porta pública"))

        vazadas, situacao = [], []
        for porta in somente_int:
            binds = [p["bind"] for p in portas if p["porta"] == porta]
            publicos = [b for b in binds if b in WILDCARDS]
            if publicos:
                vazadas.append(f"{porta} em {publicos[0] or '*'}")
            situacao.append(f"{porta} em {binds[0]}" if binds else f"{porta} sem escuta")
        resultado.append(desvio("portas_em_escuta.somente_rede_interna", esp_int, _lista(vazadas))
                         if vazadas else
                         ok("portas_em_escuta.somente_rede_interna", esp_int, _lista(situacao)))

    # ── chaves_ssh.emitidas_por ──
    emitidas_por = esperado.get("chaves_ssh", {}).get("emitidas_por", "")
    esp_chaves = f"todas emitidas por {emitidas_por}"
    chaves = inv["chaves_ssh"]
    if chaves is None:
        resultado.append(nv("chaves_ssh.emitidas_por", esp_chaves, "chaves_ssh"))
    elif not chaves:
        resultado.append(desvio("chaves_ssh.emitidas_por", esp_chaves, "nenhuma chave em authorized_keys"))
    else:
        estranhas = [c["identificacao"] for c in chaves if emitidas_por not in c["identificacao"]]
        resultado.append(
            desvio("chaves_ssh.emitidas_por", esp_chaves, f"não reconhecida(s): {_lista(estranhas)}")
            if estranhas else
            ok("chaves_ssh.emitidas_por", esp_chaves, f"{len(chaves)} chave(s), todas da plataforma"))

    # ── ssh.login_de_root ──
    root_esp = esperado.get("ssh", {}).get("login_de_root")
    login_root = inv["ssh"]["login_de_root"]
    if login_root is None:
        resultado.append(nv("ssh.login_de_root", root_esp, "ssh"))
    else:
        resultado.append(ok("ssh.login_de_root", root_esp, login_root)
                         if login_root == root_esp
                         else desvio("ssh.login_de_root", root_esp, login_root))

    # ── ntp.sincronizado ──
    ntp_esp = esperado.get("ntp", {}).get("sincronizado")
    ntp_enc = inv["ntp"]["sincronizado"]
    if ntp_enc is None:
        resultado.append(nv("ntp.sincronizado", ntp_esp, "ntp"))
    else:
        resultado.append(ok("ntp.sincronizado", ntp_esp, ntp_enc)
                         if ntp_enc == ntp_esp
                         else desvio("ntp.sincronizado", ntp_esp, ntp_enc))

    return resultado


def resumir(conformidade: list[dict]) -> dict:
    conforme = sum(1 for c in conformidade if c["veredito"] == "conforme")
    n_desvio = sum(1 for c in conformidade if c["veredito"] == "desvio")
    nao_v = sum(1 for c in conformidade if c["veredito"] == "nao_verificado")
    por_sev: dict = {}
    for c in conformidade:
        if c["veredito"] == "desvio":
            s = c.get("severidade", "info")
            por_sev[s] = por_sev.get(s, 0) + 1
    return {"conforme": conforme, "desvio": n_desvio, "nao_verificado": nao_v, "por_severidade": por_sev}


# ──────────────────────────────────────────────────────────────────
#  RENDERIZAÇÃO
# ──────────────────────────────────────────────────────────────────

def _limpar_meta(obj):
    """Remove campos internos com prefixo '_' recursivamente."""
    if isinstance(obj, dict):
        return {k: _limpar_meta(v) for k, v in obj.items() if not k.startswith("_")}
    if isinstance(obj, list):
        return [_limpar_meta(i) for i in obj]
    return obj


def renderizar_json(dados: dict, conformidade: list[dict]) -> str:
    saida = _limpar_meta(dados)
    saida["conformidade"] = conformidade
    saida["resumo"] = resumir(conformidade)
    return json.dumps(saida, ensure_ascii=False, indent=2)


def _fmt(v) -> str:
    """Formata um valor para exibição em Markdown: bool → true/false, None → null."""
    if v is True:
        return "true"
    if v is False:
        return "false"
    if v is None:
        return "null"
    return str(v)


# O JSON mantém o motivo sem acento, como no exemplo do enunciado; o Markdown,
# lido por gente, acentua (também como no exemplo).
_ACENTOS = {"privilegio": "privilégio", "usuario": "usuário", "nao": "não",
            "disponivel": "disponível", "acessivel": "acessível", "legivel": "legível"}


def _acentuar(texto: str) -> str:
    return re.sub(r"\b(" + "|".join(_ACENTOS) + r")\b", lambda m: _ACENTOS[m.group(1)], texto)


_SEV_ORDEM = {"critico": 0, "alto": 1, "medio": 2, "info": 3}
_SEV_PT = {"critico": "crítico", "alto": "alto", "medio": "médio", "info": "info"}


def renderizar_markdown(dados: dict, conformidade: list[dict]) -> str:
    host = dados["host"]
    resumo = resumir(conformidade)
    ts = host["coletado_em"][:16].replace("T", " ")

    desvios = sorted((c for c in conformidade if c["veredito"] == "desvio"),
                     key=lambda c: _SEV_ORDEM.get(c.get("severidade", "info"), 99))
    nao_vs = [c for c in conformidade if c["veredito"] == "nao_verificado"]
    conformes = [c["regra"] for c in conformidade if c["veredito"] == "conforme"]

    linhas = [
        f"# Inventário de {host['hostname']} ({host['endereco']})",
        f"Coletado em {ts} UTC · baseline v{dados.get('_baseline_versao', 1)}",
        "",
        "## Desvios",
        "",
    ]
    if desvios:
        linhas += ["| Severidade | Regra | Esperado | Encontrado |", "|---|---|---|---|"]
        for c in desvios:
            sev = _SEV_PT.get(c.get("severidade", "info"), c.get("severidade", ""))
            linhas.append(f"| {sev} | {c['regra']} | {_fmt(c['esperado'])} | {_fmt(c['encontrado'])} |")
    else:
        linhas.append("*Nenhum desvio encontrado.*")
    linhas.append("")

    if nao_vs:
        linhas += ["## Não verificado", "", "| Regra | Motivo |", "|---|---|"]
        for c in nao_vs:
            linhas.append(f"| {c['regra']} | {_acentuar(c.get('motivo', ''))} |")
        linhas.append("")

    if conformes:
        linhas += ["## Conforme", " · ".join(conformes), ""]

    linhas += [
        "---",
        f"**Resumo**: {resumo['conforme']} conforme · {resumo['desvio']} desvio · "
        f"{resumo['nao_verificado']} não verificado",
    ]
    if resumo["por_severidade"]:
        partes = [f"{v} {_SEV_PT.get(k, k)}"
                  for k, v in sorted(resumo["por_severidade"].items(), key=lambda kv: _SEV_ORDEM.get(kv[0], 99))]
        linhas.append(f"**Por severidade**: {' · '.join(partes)}")

    return "\n".join(linhas)


# ──────────────────────────────────────────────────────────────────
#  MAIN
# ──────────────────────────────────────────────────────────────────

def _sair(mensagem: str, codigo: int):
    print(mensagem, file=sys.stderr)
    sys.exit(codigo)


def main():
    class _Parser(argparse.ArgumentParser):
        def error(self, message):  # argparse sairia com 2, que aqui é falha de conexão
            self.print_usage(sys.stderr)
            _sair(f"Erro de uso: {message}", 3)

    parser = _Parser(
        description="Audita uma VM contra baseline.yaml via SSH. Apenas leitura.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--host", required=True, help="Endereço IP ou hostname da VM")
    parser.add_argument("--user", required=True, help="Usuário SSH")
    parser.add_argument("--key", required=True, help="Caminho para a chave privada SSH")
    parser.add_argument("--baseline", default="baseline.yaml",
                        help="Arquivo baseline YAML (padrão: baseline.yaml)")
    parser.add_argument("--format", choices=["json", "md", "both"], default="both", dest="fmt")
    parser.add_argument("--porta", type=int, default=22, help="Porta SSH (padrão: 22)")
    args = parser.parse_args()

    # Baseline
    try:
        with open(args.baseline) as f:
            baseline = yaml.safe_load(f)
    except FileNotFoundError:
        _sair(f"Erro: baseline não encontrado: {args.baseline}", 3)
    except yaml.YAMLError:
        _sair(f"Erro: baseline inválido (YAML mal formado): {args.baseline}", 3)
    if not isinstance(baseline, dict) or "esperado" not in baseline:
        _sair(f"Erro: baseline inválido (sem o bloco 'esperado'): {args.baseline}", 3)

    # Chave: erro de uso, verificado antes de conectar. Nem o caminho nem o
    # conteúdo da chave aparecem na mensagem.
    if not (os.path.isfile(args.key) and os.access(args.key, os.R_OK)):
        _sair("Erro: o arquivo da chave privada informado em --key não existe ou não pode ser lido", 3)

    # Conexão
    try:
        ssh = SSHConexao(args.host, args.user, args.key, args.porta)
    except ErroDeUso as e:
        _sair(f"Erro: {e}", 3)
    except ConnectionError as e:
        _sair(f"Erro de conexão: {e}", 2)

    # Coleta: cada item é isolado no Coletor; este try só pega o inesperado fora deles.
    try:
        dados = Coletor(ssh).coletar_tudo(args.host)
        dados["_baseline_versao"] = baseline.get("versao", 1)
    except Exception as e:  # noqa: BLE001
        _sair(f"Erro durante a coleta: {type(e).__name__}", 3)
    finally:
        ssh.fechar()

    try:
        conformidade = auditar(baseline, dados)
    except Exception as e:  # noqa: BLE001
        _sair(f"Erro durante a auditoria: {type(e).__name__}: {e}", 3)

    if args.fmt in ("json", "both"):
        print(renderizar_json(dados, conformidade))
    if args.fmt == "both":
        print("\n---\n")
    if args.fmt in ("md", "both"):
        print(renderizar_markdown(dados, conformidade))

    sys.exit(1 if resumir(conformidade)["desvio"] > 0 else 0)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        _sair("Interrompido.", 130)
