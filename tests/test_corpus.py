"""El corpus de corpus/: cada caso da su resultado esperado, y los datos son sintéticos.

Los resultados esperados están escritos a mano en corpus/generar.py; aquí se
comprueba que los ficheros escritos son los que genera el script, que el
cálculo los reproduce y que la línea de órdenes devuelve el código esperado.
"""

import importlib.util
import json
import re
from pathlib import Path

import pytest

from registro.carga import cargar_fichero
from registro.cli import main as cli
from registro.salida import informe

RAIZ = Path(__file__).resolve().parent.parent
CORPUS = RAIZ / "corpus"

_spec = importlib.util.spec_from_file_location("generar", CORPUS / "generar.py")
G = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(G)

ESPERADOS = sorted(CORPUS.glob("*.esperado.json"))
IDS = [p.name.removesuffix(".esperado.json") for p in ESPERADOS]


def test_estan_todos_los_casos():
    assert IDS == [c.nombre for c in G.CASOS]
    assert len(ESPERADOS) == 8


@pytest.mark.parametrize("caso", G.CASOS, ids=lambda c: c.nombre)
def test_los_ficheros_son_los_del_script(caso):
    for nombre, contenido in G.ficheros(caso).items():
        assert (CORPUS / nombre).read_text(encoding="utf-8") == contenido
    assert (CORPUS / "README.md").read_text(encoding="utf-8") == G.readme()


@pytest.mark.parametrize("caso", G.CASOS, ids=lambda c: c.nombre)
def test_cada_caso_da_su_resultado(caso):
    assert G.comprobar(caso) == []
    assert G.resumen(informe(cargar_fichero(CORPUS / f"{caso.nombre}.json"))) == caso.esperado


@pytest.mark.parametrize("esperado", ESPERADOS, ids=IDS)
def test_la_linea_de_ordenes_da_el_codigo_esperado(esperado, capsys):
    datos = json.loads(esperado.read_text(encoding="utf-8"))
    fichero = str(CORPUS / f"{datos['caso']}.json")
    assert cli([fichero]) == datos["resultado"]["codigo_salida"]
    assert cli([fichero, "--json"]) == datos["resultado"]["codigo_salida"]


def test_lo_que_demuestra_cada_caso():
    def reg(n, regimen):
        return G.CASOS[n - 1].esperado["regimenes"][regimen]

    assert G.CASOS[0].esperado["codigo_salida"] == 0
    assert {r["estado"] for r in G.CASOS[0].esperado["regimenes"].values()} == {"completo"}
    assert set(reg(2, "amlr")["decisiones"]) == {"SC"}
    assert set(reg(3, "amlr")["decisiones"]) == {"AD"}
    assert set(reg(4, "amlr")["decisiones"]) == {"IH"}
    assert [reg(5, t)["estado"] for t in ("T-1", "T-2", "T-3")] == ["completo", "indeterminado", "incompleto"]
    assert set(reg(6, "ley_rd")["decisiones"]) == {"MA"}
    assert set(reg(7, "T-1")["decisiones"]) == {"FT"}
    entrada_8 = G.CASOS[7].entrada["expediente"]
    assert entrada_8["origen"]["tipo"] == "comunicacion_interna" and entrada_8["participaciones_incorporadas"]


def _ids(valor):
    """Todos los valores de campos `id` y de referencias a identificadores."""
    if isinstance(valor, dict):
        for clave, v in valor.items():
            if clave in ("id", "persona", "sistema", "expediente_devuelto", "referencia_copia") and isinstance(v, str):
                yield v
            elif clave in ("participaciones_ia", "participaciones_incorporadas", "fuentes", "circunstancias") and all(
                isinstance(x, str) for x in v
            ):
                yield from v
            else:
                yield from _ids(v)
    elif isinstance(valor, list):
        for v in valor:
            yield from _ids(v)


def _textos(valor):
    if isinstance(valor, dict):
        for clave, v in valor.items():
            if clave in ("descripcion", "texto", "motivacion", "resultado", "descripcion_operativa") and isinstance(v, str):
                yield v
            else:
                yield from _textos(v)
    elif isinstance(valor, list):
        for v in valor:
            yield from _textos(v)


@pytest.mark.parametrize("caso", G.CASOS, ids=lambda c: c.nombre)
def test_los_datos_son_sinteticos(caso):
    """Regla 3: identificadores «FICTICIO», textos de ejemplo o inventados, salidas opacas."""
    ids = list(_ids(caso.entrada))
    assert ids and all("FICTICIO" in i for i in ids), [i for i in ids if "FICTICIO" not in i]
    for texto in _textos(caso.entrada):
        assert re.search(r"ejemplo|inventad|ficticio", texto, re.I), texto
    for p in caso.entrada["participaciones_ia"]:
        assert re.fullmatch(r"SALIDA-FICTICIO-\d+", p["salida"])
