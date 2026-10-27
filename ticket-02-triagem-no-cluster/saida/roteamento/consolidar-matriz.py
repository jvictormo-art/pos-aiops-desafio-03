#!/usr/bin/env python3
"""
Lê logs/<rotulo>/*.jsonl gerados por rodar-matriz.sh e monta a tabela
"frase × skill disparada" em resultado-<rotulo>.md.

Skill disparada = input.skill da primeira chamada à ferramenta Skill da
sessão; "nenhuma" quando a sessão terminou sem chamar Skill.

Uso: python3 consolidar-matriz.py <rotulo> [arquivo-de-frases]
"""

from __future__ import annotations

import glob
import json
import os
import sys
from collections import Counter

AQUI = os.path.dirname(os.path.abspath(__file__))

def carregar_frases(arquivo: str) -> tuple[list[str], dict[int, str]]:
    frases, esperado = [], {}
    for linha in open(arquivo, encoding="utf-8"):
        if "|" in linha:
            esp, frase = linha.rstrip("\n").split("|", 1)
            frases.append(frase)
            esperado[len(frases)] = esp
    return frases, esperado


def ler(caminho: str) -> dict:
    eventos = [json.loads(l) for l in open(caminho) if l.strip()]
    init = next((e for e in eventos if e.get("subtype") == "init"), {})
    skill, ferramentas = None, []
    for e in eventos:
        if e.get("type") != "assistant":
            continue
        for b in e.get("message", {}).get("content", []):
            if b.get("type") == "tool_use":
                ferramentas.append(b["name"])
                if b["name"] == "Skill" and skill is None:
                    skill = b.get("input", {}).get("skill")
    final = next((e for e in reversed(eventos) if e.get("type") == "result"), {})
    instaladas = sorted(s for s in init.get("skills", []) if s.startswith("metacortex"))
    return {
        "skill": skill or "nenhuma",
        "instaladas": instaladas,
        "ferramentas": ferramentas,
        "resposta": (final.get("result") or "").strip().replace("\n", " "),
    }


def main():
    rotulo = sys.argv[1] if len(sys.argv) > 1 else "rodada1"
    arquivo = sys.argv[2] if len(sys.argv) > 2 else os.path.join(AQUI, "frases-enunciado.txt")
    FRASES, ESPERADO = carregar_frases(arquivo)
    pasta = os.path.join(AQUI, "logs", rotulo)
    por_frase: dict[int, list[dict]] = {}
    for caminho in sorted(glob.glob(os.path.join(pasta, "*.jsonl"))):
        nn = int(os.path.basename(caminho).split("-")[0])
        por_frase.setdefault(nn, []).append(ler(caminho) | {"arquivo": os.path.relpath(caminho, AQUI)})

    instaladas = sorted({s for rs in por_frase.values() for r in rs for s in r["instaladas"]})
    linhas = [
        f"# Matriz de roteamento — resultado `{rotulo}`",
        "",
        f"Skills instaladas nas sessões (evento `init`): {', '.join(instaladas) or 'NENHUMA'}.",
        "",
        "| # | Frase | Esperado | Disparou (por execução) | Confere? |",
        "|---|---|---|---|---|",
    ]
    for nn in sorted(por_frase):
        rs = por_frase[nn]
        disparos = [r["skill"].replace("metacortex-", "") for r in rs]
        esp = ESPERADO[nn]
        if esp == "ambígua":
            confere = "ambígua — ver análise"
        else:
            ok = sum(r["skill"] == esp for r in rs)
            confere = "sim" if ok == len(rs) else f"**não** ({ok}/{len(rs)})"
        linhas.append(f"| {nn} | {FRASES[nn - 1]} | {esp.replace('metacortex-', '')} | {' · '.join(disparos)} | {confere} |")

    linhas += ["", "## Resposta de cada sessão", ""]
    for nn in sorted(por_frase):
        linhas.append(f"### {nn}. \"{FRASES[nn - 1]}\"")
        linhas.append("")
        for r in por_frase[nn]:
            seq = " → ".join(f.replace("mcp__kubernetes__", "k8s:") for f in r["ferramentas"]) or "(nenhuma ferramenta)"
            linhas.append(f"- `{r['arquivo']}` — skill: **{r['skill']}** — ferramentas: {seq}")
            linhas.append(f"  > {r['resposta'][:300]}")
        linhas.append("")

    destino = os.path.join(AQUI, f"resultado-{rotulo}.md")
    with open(destino, "w") as f:
        f.write("\n".join(linhas) + "\n")
    print(f"{destino} gerado.")
    print(Counter((nn, r["skill"]) for nn, rs in por_frase.items() for r in rs))


if __name__ == "__main__":
    main()
