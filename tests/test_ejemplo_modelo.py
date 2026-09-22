"""Los dos ejemplos de docs/modelo-datos.md, §1, leídos del propio documento.

Si un ejemplo cambia y deja de ser válido, o el modelo cambia y el ejemplo no,
estos tests fallan. También comprueban que los códigos y las decisiones de
validación del documento son los del código.
"""

import dataclasses
import re
from datetime import date
from pathlib import Path

from registro.carga import cargar
from registro.modelo import ERRORES

RAIZ = Path(__file__).resolve().parent.parent
MODELO = RAIZ / "docs" / "modelo-datos.md"
CARGA = RAIZ / "src" / "registro" / "carga.py"


def _seccion(texto, titulo):
    """Texto desde el encabezado `titulo` hasta el siguiente de igual o mayor nivel."""
    nivel = titulo.split(" ")[0]
    inicio = texto.index(titulo)
    fin = re.search(rf"^#{{1,{len(nivel)}}} ", texto[inicio + len(titulo) :], re.MULTILINE)
    return texto[inicio : inicio + len(titulo) + fin.start()] if fin else texto[inicio:]


TEXTO = MODELO.read_text(encoding="utf-8")
EJEMPLOS = re.findall(r"```json\n(.*?)\n```", _seccion(TEXTO, "## 1. Ejemplos"), re.DOTALL)
EXPEDIENTE = cargar(EJEMPLOS[0])
ALERTA = cargar(EJEMPLOS[1])


def test_los_dos_ejemplos_son_validos():
    assert len(EJEMPLOS) == 2
    assert EXPEDIENTE.errores == ()
    assert ALERTA.errores == ()


def test_estructura_del_expediente():
    e = EXPEDIENTE.entrada
    assert e.alerta_descartada is None
    x = e.expediente
    assert (x.fecha_apertura, x.fecha_fin_analisis_tecnico, x.fecha_cierre) == (
        date(2027, 9, 6),
        date(2027, 9, 24),
        date(2027, 9, 29),
    )
    assert x.origen.tipo == "alerta"
    assert x.origen.participaciones_ia == ("IA-1",)
    assert x.participaciones_incorporadas == ()
    assert [f.ambito for f in x.fuentes] == ["sujeto_obligado", "grupo", "externa"]
    assert [c.participaciones_ia for c in x.circunstancias_consideradas] == [(), (), ("IA-2",)]
    d = x.decision_comunicacion
    assert d.decisor.tipo == "organo_control_interno"
    assert [v.sentido for v in d.decisor.votos] == ["comunicar", "comunicar", "no_comunicar"]
    assert d.comunicacion.referencia_copia == "DOC-EJEMPLO-0001"
    assert {s.id: s.declaracion_sistema_ia for s in e.sistemas} == {"SIS-A": "no", "SIS-B": "si"}
    assert [p.momento for p in e.participaciones_ia] == ["generacion_alerta", "analisis"]
    assert e.sujeto.operaciones_anuales[0].numero == 18450


def test_estructura_de_la_alerta():
    e = ALERTA.entrada
    assert e.expediente is None
    a = e.alerta_descartada
    assert a.revision.fecha == date(2027, 10, 5)
    assert a.participaciones_ia == ("IA-1",)
    assert a.resultado.startswith("Resultado de ejemplo")


def _campos_fecha(objeto, ruta="entrada"):
    """(ruta, valor) de todos los campos cuyo nombre es o empieza por «fecha»."""
    if dataclasses.is_dataclass(objeto):
        for campo in dataclasses.fields(objeto):
            valor = getattr(objeto, campo.name)
            if campo.name.startswith("fecha"):
                yield f"{ruta}.{campo.name}", valor
            yield from _campos_fecha(valor, f"{ruta}.{campo.name}")
    elif isinstance(objeto, tuple):
        for i, elemento in enumerate(objeto):
            yield from _campos_fecha(elemento, f"{ruta}[{i}]")


def test_todas_las_fechas_son_date():
    fechas = list(_campos_fecha(EXPEDIENTE.entrada)) + list(_campos_fecha(ALERTA.entrada))
    # Expediente: 4 de participaciones e intervenciones, 3 del expediente, 3 de la decisión
    # (fecha, comunicación, comunicante). Alerta: 1 de participación y 1 de revisión.
    assert len(fechas) == 12
    for ruta, valor in fechas:
        assert valor is None or type(valor) is date, ruta


def test_los_codigos_son_los_del_documento():
    """§13.1: los códigos de la tabla son los de ERRORES, en el mismo orden."""
    tabla = _seccion(TEXTO, "### 13.1. Errores")
    assert re.findall(r"^\| `(ERR-\d\d)` \|", tabla, re.MULTILINE) == list(ERRORES)


def test_los_codigos_citados_en_el_codigo_existen():
    usados = set(re.findall(r'"(ERR-\d\d)"', CARGA.read_text(encoding="utf-8")))
    assert usados == set(ERRORES)


def test_las_decisiones_citadas_en_el_codigo_existen():
    """Cada «Modelo, V-n» del código es una fila del §13.2, y las filas son V-1 a V-24."""
    tabla = _seccion(TEXTO, "### 13.2. Decisiones de validación")
    decisiones = re.findall(r"^\| (V-\d+) \|", tabla, re.MULTILINE)
    assert decisiones == [f"V-{n}" for n in range(1, 25)]
    citadas = set(re.findall(r"Modelo, (V-\d+)", CARGA.read_text(encoding="utf-8")))
    assert citadas and citadas <= set(decisiones)
