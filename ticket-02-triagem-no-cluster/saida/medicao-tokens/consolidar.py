#!/usr/bin/env python3
"""
Consolida as execuções de medir.sh em tabelas de tokens com × sem skill.

Lê runs/*.jsonl (stream-json do `claude -p`), extrai do evento final
`result` os tokens por modelo (modelUsage), o custo, os turnos e, dos eventos
`assistant`, as tool calls feitas. Gera resultado.md e atualiza o bloco entre
os marcadores <!-- tokens:inicio --> / <!-- tokens:fim --> em
../comparacao-com-sem-skill.md.

Uso: python3 consolidar.py
"""

from __future__ import annotations

import glob
import json
import os
import re
from statistics import mean

AQUI = os.path.dirname(os.path.abspath(__file__))
COMPARACAO = os.path.join(AQUI, "..", "comparacao-com-sem-skill.md")
INICIO, FIM = "<!-- tokens:inicio -->", "<!-- tokens:fim -->"

NOMES_CASO = {
    "A-nyx-prod": "Caso A — Chamado 1 (nyx-prod, OOMKilled)",
    "B-nyx-stg": "Caso B — Chamado 3 (nyx-stg, 503 com pods Running)",
}


def ler_execucao(caminho: str) -> dict | None:
    eventos = []
    with open(caminho) as f:
        for linha in f:
            linha = linha.strip()
            if linha:
                try:
                    eventos.append(json.loads(linha))
                except json.JSONDecodeError:
                    pass
    final = next((e for e in reversed(eventos) if e.get("type") == "result"), None)
    if final is None:
        return None

    tools = []
    for e in eventos:
        if e.get("type") != "assistant":
            continue
        for bloco in e.get("message", {}).get("content", []):
            if bloco.get("type") == "tool_use":
                tools.append(bloco.get("name", ""))

    # modelUsage soma todos os modelos da sessão (inclusive chamadas auxiliares);
    # usage cobre só o modelo principal — fica como reserva.
    tok = {"entrada": 0, "cache_escrita": 0, "cache_leitura": 0, "saida": 0}
    modelos = final.get("modelUsage") or {}
    if modelos:
        for uso in modelos.values():
            tok["entrada"] += uso.get("inputTokens", 0)
            tok["cache_escrita"] += uso.get("cacheCreationInputTokens", 0)
            tok["cache_leitura"] += uso.get("cacheReadInputTokens", 0)
            tok["saida"] += uso.get("outputTokens", 0)
    else:
        uso = final.get("usage", {})
        tok["entrada"] = uso.get("input_tokens", 0)
        tok["cache_escrita"] = uso.get("cache_creation_input_tokens", 0)
        tok["cache_leitura"] = uso.get("cache_read_input_tokens", 0)
        tok["saida"] = uso.get("output_tokens", 0)
    tok["total"] = sum(tok.values())

    return {
        **tok,
        "custo": final.get("total_cost_usd") or 0.0,
        "turnos": final.get("num_turns", 0),
        "duracao_s": (final.get("duration_ms") or 0) / 1000,
        "tool_calls_k8s": sum(1 for t in tools if t.startswith("mcp__kubernetes__")),
        "usou_skill": any(t == "Skill" for t in tools),
        "erro": final.get("is_error", False),
        "modelos": ", ".join(sorted(modelos)) or "?",
        "diagnostico": (final.get("result") or "").strip(),
    }


def fmt_int(v: float) -> str:
    return f"{v:,.0f}".replace(",", ".")


def tabela_caso(caso: str, por_variante: dict[str, list[dict]]) -> list[str]:
    sem, com = por_variante.get("sem", []), por_variante.get("com", [])
    linhas = [f"### {NOMES_CASO.get(caso, caso)}", ""]
    if not sem or not com:
        return linhas + ["*Faltam execuções de uma das variantes.*", ""]

    def m(lista, k):
        return mean(r[k] for r in lista)

    def delta(k):
        a, b = m(sem, k), m(com, k)
        return f"{(b - a) / a * 100:+.0f}%" if a else "—"

    linhas += [
        f"Média de {len(sem)} execução(ões) sem skill e {len(com)} com skill.",
        "",
        "| Métrica | Sem skill | Com skill | Variação |",
        "|---|---:|---:|---:|",
    ]
    for rotulo, k in [
        ("Tokens de entrada (sem cache)", "entrada"),
        ("Tokens de escrita em cache", "cache_escrita"),
        ("Tokens de leitura de cache", "cache_leitura"),
        ("Tokens de saída", "saida"),
        ("**Tokens totais**", "total"),
    ]:
        linhas.append(f"| {rotulo} | {fmt_int(m(sem, k))} | {fmt_int(m(com, k))} | {delta(k)} |")
    linhas += [
        f"| Custo (USD) | {m(sem, 'custo'):.4f} | {m(com, 'custo'):.4f} | {delta('custo')} |",
        f"| Tool calls no cluster | {m(sem, 'tool_calls_k8s'):.1f} | {m(com, 'tool_calls_k8s'):.1f} | {delta('tool_calls_k8s')} |",
        f"| Turnos | {m(sem, 'turnos'):.1f} | {m(com, 'turnos'):.1f} | {delta('turnos')} |",
        f"| Duração (s) | {m(sem, 'duracao_s'):.0f} | {m(com, 'duracao_s'):.0f} | {delta('duracao_s')} |",
        f"| Skill acionada | {sum(r['usou_skill'] for r in sem)}/{len(sem)} | {sum(r['usou_skill'] for r in com)}/{len(com)} | |",
        "",
    ]
    return linhas


def detalhe(execucoes: list[tuple[str, dict]]) -> list[str]:
    linhas = [
        "| Execução | Tokens totais | Saída | Custo (USD) | Tool calls | Skill | Erro |",
        "|---|---:|---:|---:|---:|:-:|:-:|",
    ]
    for nome, r in execucoes:
        linhas.append(
            f"| `{nome}` | {fmt_int(r['total'])} | {fmt_int(r['saida'])} | {r['custo']:.4f} "
            f"| {r['tool_calls_k8s']} | {'sim' if r['usou_skill'] else 'não'} | {'sim' if r['erro'] else ''} |"
        )
    return linhas


def main():
    arquivos = sorted(glob.glob(os.path.join(AQUI, "runs", "*.jsonl")))
    if not arquivos:
        raise SystemExit("Nenhuma execução em runs/. Rode ./medir.sh primeiro.")

    grupos: dict[str, dict[str, list[dict]]] = {}
    execucoes: list[tuple[str, dict]] = []
    modelos = set()
    for caminho in arquivos:
        nome = os.path.basename(caminho)[: -len(".jsonl")]
        m = re.match(r"(.+)-(sem|com)-(\d+)$", nome)
        r = ler_execucao(caminho)
        if not m or r is None:
            print(f"ignorado (sem evento result): {nome}")
            continue
        grupos.setdefault(m.group(1), {}).setdefault(m.group(2), []).append(r)
        execucoes.append((nome, r))
        modelos.update(x.strip() for x in r["modelos"].split(","))

    bloco = [
        "## Medição real de tokens",
        "",
        "Números extraídos do `claude -p --output-format stream-json` de cada sessão "
        "(gerados por [`medicao-tokens/medir.sh`](./medicao-tokens/medir.sh) e "
        "[`medicao-tokens/consolidar.py`](./medicao-tokens/consolidar.py); "
        "o JSON bruto de cada execução está em `medicao-tokens/runs/`). "
        "Cada execução é uma sessão limpa, com o mesmo servidor MCP, as mesmas "
        "permissões e o mesmo prompt; a única diferença entre as variantes é a "
        "skill instalada em `.claude/skills/`.",
        "",
        f"Modelo(s): {', '.join(sorted(modelos))}.",
        "",
    ]
    for caso in sorted(grupos):
        bloco += tabela_caso(caso, grupos[caso])
    bloco += ["<details><summary>Execuções individuais</summary>", ""] + detalhe(execucoes) + ["", "</details>"]
    texto = "\n".join(bloco)

    with open(os.path.join(AQUI, "resultado.md"), "w") as f:
        # O bloco é escrito para comparacao-com-sem-skill.md (pasta acima); aqui os links são locais.
        f.write(texto.replace("./medicao-tokens/", "./") + "\n\n## Diagnóstico final de cada execução\n\n")
        for nome, r in execucoes:
            f.write(f"### `{nome}`\n\n{r['diagnostico']}\n\n")

    with open(COMPARACAO) as f:
        doc = f.read()
    if INICIO in doc and FIM in doc:
        antes, resto = doc.split(INICIO, 1)
        _, depois = resto.split(FIM, 1)
        doc = f"{antes}{INICIO}\n{texto}\n{FIM}{depois}"
        with open(COMPARACAO, "w") as f:
            f.write(doc)
        print("comparacao-com-sem-skill.md atualizado.")
    print(f"resultado.md gerado com {len(execucoes)} execução(ões).")


if __name__ == "__main__":
    main()
