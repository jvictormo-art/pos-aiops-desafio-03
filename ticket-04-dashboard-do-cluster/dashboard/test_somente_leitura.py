"""
Garantia de somente leitura verificável (ADR-006).

1. Nenhum arquivo do dashboard chama método de escrita do cliente do
   Kubernetes (create_/patch_/replace_/delete_/connect_), nem monta nome de
   método dinamicamente com getattr (o que escaparia da verificação 1).
2. A camada de leitura não faz requisição HTTP por fora do cliente oficial.
3. A ClusterRole versionada (rbac/dashboard-leitura.yaml) só concede
   get, list e watch.

Rodar: cd dashboard && python3 -m unittest test_somente_leitura -v
"""

from __future__ import annotations

import ast
import glob
import os
import unittest

import yaml

AQUI = os.path.dirname(os.path.abspath(__file__))
RBAC = os.path.join(AQUI, "..", "rbac", "dashboard-leitura.yaml")
PREFIXOS_ESCRITA = ("create_", "patch_", "replace_", "delete_", "connect_")
VERBOS_LEITURA = {"get", "list", "watch"}


def fontes() -> list[str]:
    return [f for f in glob.glob(os.path.join(AQUI, "*.py")) if not os.path.basename(f).startswith("test_")]


class TestCodigoSoLe(unittest.TestCase):
    def test_existem_fontes_para_verificar(self):
        self.assertTrue(any(f.endswith("k8s_reader.py") for f in fontes()))

    def test_nenhuma_chamada_de_escrita(self):
        violacoes = []
        for arquivo in fontes():
            arvore = ast.parse(open(arquivo).read(), filename=arquivo)
            for no in ast.walk(arvore):
                if isinstance(no, ast.Call) and isinstance(no.func, ast.Attribute) \
                        and no.func.attr.startswith(PREFIXOS_ESCRITA):
                    violacoes.append(f"{os.path.basename(arquivo)}:{no.lineno} {no.func.attr}()")
        self.assertEqual(violacoes, [], "chamadas de escrita encontradas")

    def test_nenhum_getattr_com_nome_montado(self):
        violacoes = []
        for arquivo in fontes():
            for no in ast.walk(ast.parse(open(arquivo).read())):
                if isinstance(no, ast.Call) and isinstance(no.func, ast.Name) and no.func.id == "getattr" \
                        and len(no.args) >= 2 and not isinstance(no.args[1], ast.Constant):
                    violacoes.append(f"{os.path.basename(arquivo)}:{no.lineno}")
        self.assertEqual(violacoes, [], "getattr com nome de método montado em tempo de execução")

    def test_leitura_nao_faz_http_por_fora_do_cliente(self):
        arvore = ast.parse(open(os.path.join(AQUI, "k8s_reader.py")).read())
        importados = set()
        for no in ast.walk(arvore):
            if isinstance(no, ast.Import):
                importados |= {a.name.split(".")[0] for a in no.names}
            elif isinstance(no, ast.ImportFrom) and no.module:
                if no.module.split(".")[0] in ("requests", "http", "httpx"):
                    importados.add(no.module.split(".")[0])
        self.assertFalse(importados & {"requests", "http", "httpx"})


class TestClusterRoleSoLe(unittest.TestCase):
    def test_clusterrole_existe_e_so_tem_verbos_de_leitura(self):
        self.assertTrue(os.path.exists(RBAC), "rbac/dashboard-leitura.yaml não existe")
        papeis = [d for d in yaml.safe_load_all(open(RBAC)) if d and d.get("kind") == "ClusterRole"]
        self.assertEqual(len(papeis), 1)
        verbos = {v for regra in papeis[0]["rules"] for v in regra["verbs"]}
        self.assertTrue(verbos <= VERBOS_LEITURA, f"verbos além de leitura: {verbos - VERBOS_LEITURA}")

    def test_clusterrole_cobre_os_recursos_da_tela(self):
        papel = next(d for d in yaml.safe_load_all(open(RBAC)) if d and d.get("kind") == "ClusterRole")
        recursos = {r for regra in papel["rules"] for r in regra["resources"]}
        for r in ("namespaces", "pods", "services", "events", "deployments", "endpointslices"):
            self.assertIn(r, recursos)


if __name__ == "__main__":
    unittest.main()
