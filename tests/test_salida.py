"""La salida en texto y JSON (especificación, §9)."""

import json
import re
from pathlib import Path

from ayudas import alerta, circunstancia, decisor_persona, expediente, participacion, registro
from registro.carga import cargar
from registro.salida import como_dict, como_json, informe, texto

RAIZ = Path(__file__).resolve().parent.parent
EJEMPLOS = re.findall(r"```json\n(.*?)\n```", (RAIZ / "docs" / "modelo-datos.md").read_text(encoding="utf-8"), re.S)


def _informe(datos):
    return informe(cargar(json.dumps(datos) if isinstance(datos, dict) else datos))


def _apartado(salida, titulo):
    return salida.split(titulo, 1)[1].split("\n\n", 1)[0]


def test_json_del_ejemplo_1():
    datos = como_dict(_informe(EJEMPLOS[0]))
    assert datos["valida"] is True
    assert (datos["tipo_registro"], datos["registro"]) == ("expediente", "EXP-0001")
    assert datos["fecha_aplicacion_amlr"] == "2027-07-10"
    assert set(datos["regimenes"]) == {"ley_rd", "amlr", "T-1", "T-2", "T-3"}
    assert datos["comparacion"]["normas_coinciden"] is False
    assert datos["comparacion"]["transicion_coincide"] is True
    amlr = datos["regimenes"]["amlr"]
    assert amlr["estado"] == "indeterminado"
    assert [d["dimension"] for d in amlr["decisiones"]] == ["SC", "DC"]
    sc = {x["lectura"]: x for x in amlr["decisiones"][0]["respuestas"]}
    assert sc["SC-1"]["resuelve"] is True and sc["SC-2"]["depende_de"] == ["DC"]
    assert amlr["faltas"]["en_todas"] == []
    assert [f["id"] for f in amlr["faltas"]["segun_lectura"]] == ["AM-04", "AM-07"]
    assert datos["exige_actuar"]["valor"] is True
    activado = datos["exige_actuar"]["activado_por"][0]
    assert activado == {"regimen": "amlr", "lecturas": ["SC-1", "IH-1", "DC-1"], "estado": "incompleto", "faltas": ["AM-04"]}
    assert datos["informativos"]["umbral_operaciones"]["valor"] == "indeterminado"
    assert len(amlr["lecturas"]) == 18
    # JSON serializable y en UTF-8 legible.
    assert "Información considerada" in como_json(_informe(EJEMPLOS[0]))


def test_texto_del_ejemplo_1():
    salida = texto(_informe(EJEMPLOS[0]))
    assert salida.startswith("Expediente EXP-0001\n")
    assert "  ley_rd  completo\n" in salida
    assert "ley_rd y amlr no coinciden" in salida
    exige = _apartado(salida, "Exige actuar:")
    # Los regímenes que coinciden van juntos, y más de tres combinaciones se resumen.
    assert "    amlr, T-1, T-2, T-3 (estado del régimen: indeterminado):" in exige
    assert "y 9 combinaciones más (todas en --json)" in exige
    falta = _apartado(salida, "Qué falta (D-5):")
    assert "  ley_rd: nada." in falta
    assert "Solo en algunas:" in falta and "En todas las lecturas:" not in falta
    decidir = _apartado(salida, "Qué hay que decidir para salir del indeterminado (D-7, D-8):")
    assert "SC-2: completo o incompleto (falta AM-07); aún depende de DC" in decidir
    assert "  T-1: lo mismo que amlr" in decidir


def test_texto_separa_lo_que_falta_en_todas_de_lo_que_falta_en_algunas():
    # Ejemplo 3 de la especificación: AM-02 falta en todas; AM-04 solo con SC-1.
    datos = registro(
        expediente(
            apertura="2027-06-21", fin_analisis="2027-07-14", decision="2027-07-16", cierre="2027-07-19",
            comunicar=False, origen_tipo="comunicacion_interna", incorporadas=["IA-5"], circunstancias=[],
            razones=[{"descripcion": "Razón de ejemplo", "circunstancias": []}],
        ),
        participaciones=[participacion("IA-5", "SIS-A", "generacion_alerta", "2027-06-28")],
    )
    falta = _apartado(texto(_informe(datos)), "Qué falta (D-5):")
    bloque_amlr = falta.split("  amlr:", 1)[1]
    assert bloque_amlr.index("En todas las lecturas:") < bloque_amlr.index("AM-02") < bloque_amlr.index("Solo en algunas:")
    assert "AM-04 Salida del sistema entre las circunstancias (participaciones_ia[0] (IA-5)): con SC-1" in bloque_amlr


def test_sin_nada_que_hacer():
    datos = registro(expediente(decisor=decisor_persona("P-1")))
    inf = _informe(datos)
    salida = texto(inf)
    assert "  No: ninguna lectura de ningún régimen da «incompleto» (D-25)." in salida
    assert "Los cinco regímenes coinciden." in salida
    assert "Qué hay que decidir" not in salida
    assert como_dict(inf)["exige_actuar"] == {"valor": False, "activado_por": []}


def test_alerta_descartada():
    datos = registro(
        alerta_=alerta(revision="2028-05-10", fuentes=[], circunstancias=[], resultado=None),
        participaciones=[participacion("IA-1", "SIS-A", "generacion_alerta", "2028-05-09")],
    )
    salida = texto(_informe(datos))
    assert salida.startswith("Alerta descartada ALE-EJEMPLO\n")
    assert "AD — ¿La revisión de una alerta descartada es una evaluación del art. 69.2 del AMLR? (R-6, §4.5)" in salida
    assert "AD-1: no_exigible" in salida
    assert "Días entre" not in salida


def test_entrada_no_valida():
    inf = _informe({"version_modelo": 2})
    assert texto(inf).startswith("La entrada no es válida (")
    datos = como_dict(inf)
    assert datos["valida"] is False and datos["regimenes"] == {} and datos["exige_actuar"] is None
    assert datos["errores"][0]["codigo"] == "ERR-01"


def test_la_salida_del_sistema_no_se_interpreta():
    # Regla 2: la salida no aparece en el informe ni cambia nada; solo el id de la participación.
    p = participacion("IA-2", "SIS-B", "analisis", "2028-02-20", salida="SALIDA-OPACA-XYZ")
    datos = registro(expediente(circunstancias=[circunstancia("C-1"), circunstancia("C-2", participaciones=["IA-2"])]), participaciones=[p])
    inf = _informe(datos)
    assert "SALIDA-OPACA-XYZ" not in texto(inf)
    assert "SALIDA-OPACA-XYZ" not in como_json(inf)
