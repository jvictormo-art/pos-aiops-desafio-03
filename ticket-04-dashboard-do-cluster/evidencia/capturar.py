#!/usr/bin/env python3
"""
Gera as evidências do dashboard: roda a aplicação sem terminal (piloto do
Textual) contra cada contexto, espera a primeira leitura e salva a tela em SVG.

Pré-requisitos:
  - cluster kind-metacortex-lab com os chamados do Ticket 02 e os workloads de
    ../laboratorio/subir-workloads.sh
  - kubeconfigs de ../laboratorio/cenarios-de-falha.sh (e, para a 08,
    `cenarios-de-falha.sh platform-ro`)

Uso: python3 capturar.py [id ...]     (sem argumentos: todas)
"""

from __future__ import annotations

import asyncio
import os
import subprocess
import sys
import tempfile

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(AQUI, "..", "dashboard"))
KCFG = os.path.join(AQUI, "..", "laboratorio", "kubeconfigs")

from app import MetacortexDashboard  # noqa: E402
from textual.widgets import Input  # noqa: E402


def kubeconfig_lab() -> str:
    """Kubeconfig só com o contexto do laboratório (o app lê o current-context)."""
    conteudo = subprocess.run(
        ["kubectl", "config", "view", "--minify", "--flatten", "--context", "kind-metacortex-lab"],
        check=True, capture_output=True, text=True).stdout
    f = tempfile.NamedTemporaryFile("w", suffix=".kubeconfig", delete=False)
    f.write(conteudo)
    f.close()
    return f.name


LAB = kubeconfig_lab()

# id → (kubeconfig, namespace inicial, busca)
CAPTURAS = {
    "01-nyx-dev-kube-news": (LAB, "nyx-dev", ""),
    "02-nyx-prod-oomkilled": (LAB, "nyx-prod", ""),
    "03-orion-stg-imagepull": (LAB, "orion-stg", ""),
    "04-nyx-stg-sem-endpoint": (LAB, "nyx-stg", ""),
    "05-orion-prod-fake-shop": (LAB, "orion-prod", ""),
    "06-cluster-inalcancavel": (os.path.join(KCFG, "inalcancavel.kubeconfig"), None, ""),
    "07-credencial-invalida": (os.path.join(KCFG, "credencial-invalida.kubeconfig"), None, ""),
    "08-rbac-restrito-platform-ro": (os.path.join(KCFG, "platform-ro.kubeconfig"), "nyx-stg", ""),
    "09-busca-por-nome": (LAB, "nyx-prod", "postgres"),
}


async def capturar(nome: str, kubeconfig: str, namespace: str | None, busca: str) -> None:
    app = MetacortexDashboard(kubeconfig=kubeconfig, namespace_inicial=namespace)
    async with app.run_test(size=(150, 46)) as piloto:
        await piloto.pause(1.0)
        if busca:
            app.query_one("#input-busca", Input).value = busca
            await piloto.pause(0.5)
            app._atualizar_paineis()
            await piloto.pause(0.5)
        app.save_screenshot(filename=f"{nome}.svg", path=AQUI)
    print("gerado:", f"{nome}.svg")


def main():
    escolhidos = sys.argv[1:] or list(CAPTURAS)
    for nome in escolhidos:
        kubeconfig, ns, busca = CAPTURAS[nome]
        if not os.path.exists(kubeconfig):
            print(f"pulado: {nome} (falta {os.path.relpath(kubeconfig, AQUI)})")
            continue
        asyncio.run(capturar(nome, kubeconfig, ns, busca))


if __name__ == "__main__":
    main()
