"""
Testes da camada de leitura com objetos falsos da API (sem cluster):
o que a tela pode afirmar (ADR-007) e campo ausente vs. vazio.

Rodar: cd dashboard && python3 -m unittest test_k8s_reader -v
"""

from __future__ import annotations

import unittest
from types import SimpleNamespace as NS

from kubernetes.client.exceptions import ApiException

from k8s_reader import ClusterReader


def container_spec(nome: str, com_probe: bool):
    return NS(name=nome, readiness_probe=NS(http_get=NS(path="/ready")) if com_probe else None)


def status(nome: str, pronto: bool):
    return NS(name=nome, ready=pronto, restart_count=0, state=NS(waiting=None, terminated=None, running=NS()),
              last_state=NS(terminated=None))


def pod(containers, prontos):
    return NS(
        metadata=NS(name="p"),
        spec=NS(containers=containers),
        status=NS(phase="Running", container_statuses=prontos, init_container_statuses=None),
    )


def leitor() -> ClusterReader:
    r = ClusterReader.__new__(ClusterReader)  # sem carregar kubeconfig
    return r


class TestProntoSemProbe(unittest.TestCase):
    def test_pronto_sem_readiness_e_sinalizado(self):
        p = pod([container_spec("postgres", False)], [status("postgres", True)])
        resumo = leitor()._resumir_pod(p)
        self.assertEqual(resumo["ready"], "1/1")
        self.assertTrue(resumo["sem_readiness"])

    def test_pronto_com_readiness_nao_e_sinalizado(self):
        p = pod([container_spec("api", True)], [status("api", True)])
        self.assertFalse(leitor()._resumir_pod(p)["sem_readiness"])

    def test_um_container_sem_probe_basta(self):
        p = pod([container_spec("api", True), container_spec("sidecar", False)],
                [status("api", True), status("sidecar", True)])
        self.assertTrue(leitor()._resumir_pod(p)["sem_readiness"])


class TestEndpointNaoVerificado(unittest.TestCase):
    def test_403_no_endpointslice_nao_vira_sem_endpoint(self):
        r = leitor()

        class Core:
            def list_namespaced_service(self, ns, **kw):
                return NS(items=[NS(metadata=NS(name="nyx-api"))])

        class Discovery:
            def list_namespaced_endpoint_slice(self, ns, **kw):
                raise ApiException(status=403, reason="Forbidden")

        r._core, r._discovery = Core(), Discovery()
        res = r.listar_services_com_endpoint("nyx-stg")
        self.assertTrue(res.ok)
        self.assertEqual(res.dados[0]["endpoint_texto"], "endpoint não verificado (403)")

    def test_fatia_sem_enderecos_e_sem_endpoint(self):
        r = leitor()

        class Core:
            def list_namespaced_service(self, ns, **kw):
                return NS(items=[NS(metadata=NS(name="nyx-api"))])

        class Discovery:
            def list_namespaced_endpoint_slice(self, ns, **kw):
                return NS(data=b'{"items": [{"endpoints": null}]}')

        r._core, r._discovery = Core(), Discovery()
        self.assertEqual(r.listar_services_com_endpoint("nyx-stg").dados[0]["endpoint_texto"], "sem endpoint")


class TestFormatacaoReady(unittest.TestCase):
    def test_asterisco_so_quando_pronto_sem_probe(self):
        from app import formatar_ready
        self.assertEqual(formatar_ready({"ready": "1/1", "pronto": True, "sem_readiness": True}), "1/1*")
        self.assertEqual(formatar_ready({"ready": "1/1", "pronto": True, "sem_readiness": False}), "1/1")
        self.assertEqual(formatar_ready({"ready": "0/1", "pronto": False, "sem_readiness": True}), "0/1")


class TestCampoAusente(unittest.TestCase):
    def test_ready_replicas_ausente_vira_zero(self):
        dep = NS(metadata=NS(name="orion-web"), spec=NS(replicas=3),
                 status=NS(ready_replicas=None, conditions=None))
        d = leitor()._resumir_deployment(dep)
        self.assertEqual((d["pronto"], d["desejado"]), (0, 3))


if __name__ == "__main__":
    unittest.main()
