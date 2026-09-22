"""La salida pegada en el README es la que da hoy la línea de órdenes."""

import re
from pathlib import Path

from registro.cli import main

RAIZ = Path(__file__).resolve().parent.parent


def test_la_salida_del_readme_es_la_real(capsys, monkeypatch):
    readme = (RAIZ / "README.md").read_text(encoding="utf-8")
    bloque = re.search(r"```\n\$ registro-examen-especial (\S+)\n(.*?)\n```", readme, re.S)
    fichero, pegada = bloque.group(1), bloque.group(2)
    monkeypatch.chdir(RAIZ)
    codigo = main([fichero])
    assert capsys.readouterr().out.rstrip("\n") == pegada
    assert codigo == 1
    assert "El código de salida es 1" in readme
