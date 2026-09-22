"""Las tablas de docs/especificacion-calculo.md coinciden con el código.

Requisitos (§3.1 y §4.1), dimensiones de lectura (§1.4) y decisiones citadas
en el código (índice del §11).
"""

import re
from pathlib import Path

from registro.calculo import DIMENSION_OA, DIMENSIONES, REQUISITOS

RAIZ = Path(__file__).resolve().parent.parent
ESPECIFICACION = (RAIZ / "docs" / "especificacion-calculo.md").read_text(encoding="utf-8")
CALCULO = (RAIZ / "src" / "registro" / "calculo.py").read_text(encoding="utf-8")


def _seccion(titulo):
    nivel = titulo.split(" ")[0]
    inicio = ESPECIFICACION.index(titulo)
    resto = ESPECIFICACION[inicio + len(titulo) :]
    fin = re.search(rf"^#{{1,{len(nivel)}}} ", resto, re.MULTILINE)
    return ESPECIFICACION[inicio : inicio + len(titulo) + fin.start()] if fin else ESPECIFICACION[inicio:]


def test_requisitos_de_la_ley_y_el_rd():
    filas = re.findall(r"^\| (RD-\d\d) \| ([^|]+?) \|", _seccion("### 3.1. Requisitos de un expediente"), re.M)
    assert filas == [(k, v) for k, v in REQUISITOS.items() if k.startswith("RD-")]


def test_requisitos_del_amlr():
    filas = re.findall(r"^\| (AM-\d\d) \| ([^|]+?) \|", _seccion("### 4.1. Requisitos"), re.M)
    assert filas == [(k, v) for k, v in REQUISITOS.items() if k.startswith("AM-")]


def test_dimensiones():
    tabla = _seccion("### 1.4. Lecturas, combinaciones y atribución")
    filas = re.findall(r"^\| [^|]+\((R-\d+)\) \| ([A-Z]{2}-\d(?:, [A-Z]{2}-\d)*) \| [^|]+ \| [^|]+ \| (§[\d.]+) \|", tabla, re.M)
    esperadas = [(d.caso, ", ".join(d.lecturas), d.seccion) for d in DIMENSIONES.values()]
    assert filas == esperadas


def test_dimension_del_dato_informativo():
    texto = _seccion("### 2.2. Umbral de operaciones del RD, art. 23 (R-7)")
    assert all(f"**{l}:**" in texto for l in DIMENSION_OA.lecturas)


def test_las_decisiones_citadas_en_el_codigo_existen():
    indice = re.findall(r"^\| (D-\d+) \|", _seccion("## 11. Índice de decisiones"), re.M)
    assert indice == [f"D-{n}" for n in range(1, len(indice) + 1)]
    citadas = set(re.findall(r"\bD-\d+\b", CALCULO))
    assert citadas and citadas <= set(indice)


def test_los_casos_citados_en_el_codigo_existen():
    ambiguedades = (RAIZ / "docs" / "ambiguedades.md").read_text(encoding="utf-8")
    casos = set(re.findall(r'^<a id="(r-\d+)"></a>', ambiguedades, re.M))
    citados = {c.lower() for c in re.findall(r"\bR-\d+\b", CALCULO)}
    assert citados and citados <= casos


def test_los_enlaces_a_los_casos_llevan_a_ambiguedades():
    """Los casos se extrajeron del modelo; sus enlaces apuntan a ambiguedades.md y existen."""
    ambiguedades = (RAIZ / "docs" / "ambiguedades.md").read_text(encoding="utf-8")
    anclas = set(re.findall(r'^<a id="(r-\d+)"></a>', ambiguedades, re.M))
    assert anclas == {f"r-{n}" for n in range(1, 12)}
    for nombre in ("modelo-datos.md", "especificacion-calculo.md"):
        texto = (RAIZ / "docs" / nombre).read_text(encoding="utf-8")
        assert "](#r-" not in texto
        assert set(re.findall(r"\]\(ambiguedades\.md#(r-\d+)\)", texto)) <= anclas
    for caso in re.findall(r"^### (R-\d+)\.", ambiguedades, re.M):
        seccion = ambiguedades.split(f"### {caso}.", 1)[1].split("\n### ", 1)[0]
        for apartado in ("**Qué dice la norma.**", "**Por qué no determina un comportamiento único.**",
                         "**Qué hace la implementación.**", "**Cómo se señala en la salida.**", "**Régimen.**"):
            assert apartado in seccion, (caso, apartado)
