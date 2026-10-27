#!/usr/bin/env python3
"""
Transforma logs/chamado-*.jsonl (stream-json do claude -p) em
../triagem-chamado-*.md: o pedido, a skill carregada, cada chamada às
ferramentas do mcp-server-kubernetes com o que o cluster respondeu, e o
diagnóstico final do agente.
"""

from __future__ import annotations

import glob
import json
import os

AQUI = os.path.dirname(os.path.abspath(__file__))
TITULOS = {
    "01-nyx-prod": "triagem-chamado-01-nyx-prod.md",
    "02-orion-stg": "triagem-chamado-02-orion-stg.md",
    "03-nyx-stg": "triagem-chamado-03-nyx-stg.md",
}
MAX_LINHAS = 45


def texto_resultado(conteudo) -> str:
    if isinstance(conteudo, str):
        return conteudo
    partes = []
    for b in conteudo or []:
        if isinstance(b, dict) and b.get("type") == "text":
            partes.append(b["text"])
    return "\n".join(partes)


def cortar(texto: str) -> str:
    # O MCP devolve JSON em uma linha; formatar facilita a leitura.
    try:
        texto = json.dumps(json.loads(texto), ensure_ascii=False, indent=2)
    except (json.JSONDecodeError, TypeError):
        pass
    linhas = texto.splitlines()
    if len(linhas) > MAX_LINHAS:
        resto = len(linhas) - MAX_LINHAS
        linhas = linhas[:MAX_LINHAS] + [f"… ({resto} linhas omitidas; resposta completa no log .jsonl)"]
    return "\n".join(linhas)


def transcrever(caminho: str) -> tuple[str, str]:
    cid = os.path.basename(caminho)[len("chamado-"):-len(".jsonl")]
    eventos = [json.loads(l) for l in open(caminho) if l.strip()]
    init = next(e for e in eventos if e.get("subtype") == "init")
    final = next(e for e in reversed(eventos) if e.get("type") == "result")
    resultados = {}
    for e in eventos:
        if e.get("type") == "user":
            for b in e["message"].get("content", []) if isinstance(e["message"].get("content"), list) else []:
                if isinstance(b, dict) and b.get("type") == "tool_result":
                    resultados[b["tool_use_id"]] = (texto_resultado(b.get("content")), b.get("is_error", False))

    servidores = ", ".join("`%s` (%s)" % (m["name"], m["status"]) for m in init.get("mcp_servers", []))
    ferramentas_k8s = sorted(t for t in init.get("tools", []) if t.startswith("mcp__kubernetes__"))
    skills = sorted(s for s in init.get("skills", []) if s.startswith("metacortex"))

    linhas = [
        f"# Triagem — Chamado {cid}",
        "",
        "Saída real da skill `metacortex-triage`, executada pelo agente numa sessão limpa do Claude Code "
        f"(`claude -p`, modelo `{init.get('model')}`). O acesso ao cluster foi **só** pelo `mcp-server-kubernetes` "
        "em modo não destrutivo ([`.mcp.json`](../.mcp.json)); Bash ficou bloqueado na sessão, então não havia como "
        "rodar `kubectl` direto. Registro bruto: "
        f"[`triagens/logs/chamado-{cid}.jsonl`](./triagens/logs/chamado-{cid}.jsonl).",
        "",
        "| Item | Valor |",
        "|---|---|",
        f"| Servidor MCP | {servidores} |",
        f"| Ferramentas do servidor disponíveis na sessão | {len(ferramentas_k8s)} (nenhuma de escrita destrutiva: o modo não destrutivo remove `kubectl_delete`, `exec_in_pod` e afins) |",
        f"| Skills instaladas | {', '.join(skills)} |",
        f"| Turnos / duração / custo | {final.get('num_turns')} / {round((final.get('duration_ms') or 0) / 1000)} s / US$ {final.get('total_cost_usd', 0):.4f} |",
        "",
    ]

    n = 0
    for e in eventos:
        if e.get("type") != "assistant":
            continue
        for b in e["message"]["content"]:
            if b.get("type") != "tool_use":
                continue
            nome, entrada = b["name"], b.get("input", {})
            if nome == "Skill":
                linhas += [f"**Skill carregada:** `{entrada.get('skill')}`", ""]
                continue
            if nome == "ToolSearch":
                continue
            n += 1
            res, erro = resultados.get(b["id"], ("", False))
            linhas += [
                f"## Chamada {n}: `{nome}`" + (" (erro)" if erro else ""),
                "",
                "```json",
                json.dumps(entrada, ensure_ascii=False),
                "```",
                "",
                "Resposta do cluster:",
                "",
                "```",
                cortar(res),
                "```",
                "",
            ]

    linhas += ["## Diagnóstico do agente", "", (final.get("result") or "").strip(), ""]
    return cid, "\n".join(linhas)


def main():
    for caminho in sorted(glob.glob(os.path.join(AQUI, "logs", "chamado-*.jsonl"))):
        cid, md = transcrever(caminho)
        destino = os.path.join(AQUI, "..", TITULOS.get(cid, f"triagem-chamado-{cid}.md"))
        with open(destino, "w") as f:
            f.write(md)
        print("gerado:", os.path.relpath(destino, AQUI))


if __name__ == "__main__":
    main()
