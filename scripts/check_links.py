#!/usr/bin/env python3
"""Verifica links relativos quebrados em arquivos Markdown do repositorio."""

from __future__ import annotations

import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
PADRAO = re.compile(r"\]\((?!https?://|mailto:|#)([^)#]+)")
IGNORAR = {
    ".git",
    ".opencode",
    ".pytest_cache",
    ".ruff_cache",
    "AUDITORIA_PCB",
    "node_modules",
    "__pycache__",
}


def main() -> int:
    quebrados: list[str] = []
    for md in RAIZ.rglob("*.md"):
        if any(parte in IGNORAR for parte in md.parts):
            continue
        for numero, linha in enumerate(md.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
            for alvo in PADRAO.findall(linha):
                alvo = alvo.strip()
                if not alvo:
                    continue
                destino = (md.parent / alvo).resolve()
                if not destino.exists():
                    quebrados.append(f"{md.relative_to(RAIZ)}:{numero}: {alvo}")

    if quebrados:
        print("Links relativos quebrados:")
        print("\n".join(quebrados))
        return 1

    print("Nenhum link relativo quebrado.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
