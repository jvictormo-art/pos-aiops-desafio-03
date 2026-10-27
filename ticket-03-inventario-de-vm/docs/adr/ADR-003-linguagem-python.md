# ADR-003 — Linguagem: Python 3

| Campo | Valor |
|---|---|
| Status | aceito |
| Data | 2026-09-17 (registrado como ADR em 2026-10-27; origem: `spec/spec-decisoes.md`, seção "Linguagem") |
| Decisão exigida pelo enunciado | "Em que linguagem ela é escrita, e por quê" |

## Contexto

Quem mantém a ferramenta é o time de infraestrutura. Ela precisa de SSH, leitura de YAML (baseline), comparação de versões, JSON e Markdown. Roda na estação de quem opera, onde já existe Python (o macOS do laboratório tem 3.9; as estações Linux do parque têm 3.10+).

## Decisão

**Python 3.9+**, com `paramiko` e `PyYAML` como únicas dependências.

## Alternativas consideradas

### A. Go

- **Ganha:** binário único e estático, sem interpretador nem `pip install` na estação; tipagem forte.
- **Perde:** `x/crypto/ssh` é mais verboso para o que são nove comandos; o time escreve Python nos outros artefatos do desafio (scripts das skills, dashboard), e uma segunda linguagem é um segundo pipeline de build e de revisão.

### B. Shell (bash + `ssh`)

- **Ganha:** zero dependência; os comandos de coleta já são shell.
- **Perde:** parsear `ss`, comparar versões, montar JSON e Markdown e testar cada regra isoladamente em shell é frágil; os testes da revisão 1 (13 casos com SSH simulado) seriam muito mais difíceis.

### C. Python (escolhida)

- **Ganha:** `paramiko` com exceções tipadas ([ADR-001](./ADR-001-comunicacao-ssh-com-paramiko.md)), `yaml` e `json` prontos, testes com `unittest` sem rede, mesma linguagem do resto do time.
- **Perde:** exige Python e duas dependências instaladas na estação; distribuição menos simples que um binário.

## Consequências

- **Versão mínima corrigida durante a implementação:** a spec dizia 3.10+; a estação de laboratório tem 3.9.6. As anotações `X | None` funcionam no 3.9 com `from __future__ import annotations`, adotado nos arquivos da ferramenta.
