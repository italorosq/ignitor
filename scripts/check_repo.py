#!/usr/bin/env python3
"""Falha se artefatos gerados/locais estiverem rastreados pelo Git."""

from __future__ import annotations

import subprocess
import sys
from pathlib import PurePosixPath

PROIBIDOS = (
    "__pycache__/",
    ".pytest_cache/",
    ".ruff_cache/",
    ".opencode/",
    "AUDITORIA_PCB/",
    "/analysis/",
    ".history/",
    "smd_fr/",
    "jlcpcb/project.db",
)
SUFIXOS = (".kicad_prl", ".kicad_pcb.lck", ".lck", ".bak")


def main() -> int:
    saida = subprocess.run(
        ["git", "ls-files"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    arquivos = [linha.strip() for linha in saida.splitlines() if linha.strip()]

    ofensores = []
    for arquivo in arquivos:
        caminho = "/" + arquivo
        if any(padrao in caminho for padrao in PROIBIDOS) or arquivo.endswith(SUFIXOS):
            ofensores.append(arquivo)

    if ofensores:
        print("Artefatos gerados/locais rastreados pelo Git:")
        print("\n".join(f"  - {item}" for item in ofensores))
        print("\nRemova do indice com: git rm --cached <arquivo>")
        return 1

    print("Nenhum artefato gerado rastreado.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
