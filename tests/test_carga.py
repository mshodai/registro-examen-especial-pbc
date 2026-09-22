"""Validaciones del §13 de docs/modelo-datos.md, una a una.

Cada test parte de una entrada válida (un expediente o una alerta descartada)
y cambia solo lo necesario para provocar el error.
"""

import json
from datetime import date

import pytest

from ayudas import (
    alerta,
    circunstancia,
    decisor_organo,
    decisor_persona,
    expediente,
    fase,
    intervencion,
    participacion,
    persona,
    registro,
    sistema,
    voto,
)
from registro.carga import cargar, cargar_fichero
from registro.modelo import ERRORES


def base_expediente():
    return registro(expediente())


def base_alerta():
    return registro(alerta_=alerta(), participaciones=[participacion("IA-1", "SIS-A", "generacion_alerta", "2027-10-04")])


def validar(datos):
    return cargar(json.dumps(datos))


def codigos(datos):
    return [e.codigo for e in validar(datos).errores]


def rutas(datos, codigo):
    return [e.ruta for e in validar(datos).errores if e.codigo == codigo]


# --- Entradas válidas ----------------------------------------------------------


def test_las_bases_son_validas():
    for datos in (base_expediente(), base_alerta()):
        resultado = validar(datos)
        assert resultado.valida, resultado.errores
    entrada = validar(base_expediente()).entrada
    assert type(entrada.expediente.fecha_apertura) is date


def test_todos_los_codigos_estan_documentados():
    assert list(ERRORES) == [f"ERR-{n:02d}" for n in range(1, 13)]


def test_con_errores_no_hay_entrada():
    datos = base_expediente()
    datos["expediente"]["conclusion"]["razones"] = []
    resultado = validar(datos)
    assert resultado.entrada is None
    assert not resultado.valida


def test_cargar_fichero(tmp_path):
    fichero = tmp_path / "entrada.json"
    fichero.write_text(json.dumps(base_expediente()), encoding="utf-8")
    assert cargar_fichero(fichero).valida


# --- ERR-01: estructura y tipos -----------------------------------------------


def test_json_mal_formado():
    assert [e.codigo for e in cargar("{").errores] == ["ERR-01"]


def test_clave_repetida():
    # Modelo, V-20.
    texto = json.dumps(base_expediente())[:-1] + ', "version_modelo": 1}'
    assert "ERR-01" in [e.codigo for e in cargar(texto).errores]


def test_nan():
    texto = json.dumps(base_expediente()).replace('"numero": 18450', '"numero": NaN')
    assert [e.codigo for e in cargar(texto).errores] == ["ERR-01"]


def test_regimen():
    # §2 y modelo, V-1.
    datos = dict(base_expediente(), regimen="amlr")
    assert rutas(datos, "ERR-01") == ["regimen"]


def test_campo_desconocido_en_cualquier_objeto():
    datos = base_expediente()
    datos["expediente"]["fases"][0]["prioridad"] = "alta"
    assert rutas(datos, "ERR-01") == ["expediente.fases[0].prioridad"]


def test_campo_que_admite_null_omitido():
    # Modelo, V-2.
    datos = base_expediente()
    del datos["expediente"]["decision_comunicacion"]["fecha_puesta_en_conocimiento_comunicante"]
    assert codigos(datos) == ["ERR-01"]


def test_version_distinta():
    datos = dict(base_expediente(), version_modelo=2)
    assert codigos(datos) == ["ERR-01"]


@pytest.mark.parametrize("fecha", ["20280214", "2028-02-30", "2028-2-14", 20280214])
def test_fecha_no_valida(fecha):
    # Modelo, V-3.
    datos = base_expediente()
    datos["expediente"]["fecha_apertura"] = fecha
    assert rutas(datos, "ERR-01") == ["expediente.fecha_apertura"]


@pytest.mark.parametrize("valor", [True, 12.0, -1, "12"])
def test_numero_de_operaciones_no_valido(valor):
    # Modelo, V-23.
    datos = base_expediente()
    datos["sujeto"]["operaciones_anuales"][0]["numero"] = valor
    assert codigos(datos) == ["ERR-01"]


def test_salida_numerica():
    # §9.3: la salida es siempre una cadena.
    datos = base_alerta()
    datos["participaciones_ia"][0]["salida"] = 0.87
    assert rutas(datos, "ERR-01") == ["participaciones_ia[0].salida"]


def test_valores_enumerados():
    datos = base_expediente()
    datos["personas"][0]["cargos"].append("presidente")
    datos["expediente"]["origen"]["tipo"] = "sospecha"
    assert sorted(rutas(datos, "ERR-01")) == ["expediente.origen.tipo", "personas[0].cargos[2]"]


def test_textos_vacios_admitidos():
    # Modelo, V-22: es un hecho; el cálculo los trata como ausentes.
    datos = base_expediente()
    datos["expediente"]["origen"]["descripcion"] = ""
    datos["expediente"]["decision_comunicacion"]["motivacion"] = "   "
    assert validar(datos).valida


def test_con_err_01_no_se_comprueba_la_coherencia():
    # Modelo, V-21: con la fecha mal, el orden de fechas (ERR-04) y la referencia rota (ERR-03)
    # no se comprueban.
    datos = base_expediente()
    datos["expediente"]["fecha_apertura"] = "mal"
    datos["expediente"]["fases"][0]["fuentes"] = ["F-9"]
    assert codigos(datos) == ["ERR-01"]


# --- ERR-02: repetidos --------------------------------------------------------


def test_id_repetido():
    datos = base_expediente()
    datos["expediente"]["fuentes"].append(dict(datos["expediente"]["fuentes"][0]))
    assert rutas(datos, "ERR-02") == ["expediente.fuentes[1].id"]


def test_anio_repetido():
    datos = base_expediente()
    datos["sujeto"]["operaciones_anuales"].append({"anio": 2026, "numero": 1})
    assert rutas(datos, "ERR-02") == ["sujeto.operaciones_anuales[1].anio"]


def test_cargo_repetido_y_persona_repetida_en_votos():
    datos = registro(expediente(decisor=decisor_organo(voto("P-2", "comunicar"), voto("P-2", "comunicar"))))
    datos["personas"][1]["cargos"].append("miembro_organo_control_interno")
    assert sorted(rutas(datos, "ERR-02")) == [
        "expediente.decision_comunicacion.decisor.votos[1].persona",
        "personas[1].cargos[1]",
    ]


def test_referencia_repetida():
    # Modelo, V-24.
    datos = base_expediente()
    datos["expediente"]["fases"][0]["fuentes"] = ["F-1", "F-1"]
    assert rutas(datos, "ERR-02") == ["expediente.fases[0].fuentes[1]"]


# --- ERR-03: referencias ------------------------------------------------------


def test_referencias_inexistentes():
    # Modelo, V-5.
    datos = base_expediente()
    datos["expediente"]["fases"][0]["fuentes"] = ["F-9"]
    datos["expediente"]["conclusion"]["razones"][0]["circunstancias"] = ["C-9"]
    datos["expediente"]["decision_comunicacion"]["decisor"]["persona"] = "P-9"
    assert rutas(datos, "ERR-03") == [
        "expediente.fases[0].fuentes[0]",
        "expediente.conclusion.razones[0].circunstancias[0]",
        "expediente.decision_comunicacion.decisor.persona",
    ]


def test_fuentes_de_la_alerta_son_las_suyas():
    # Modelo, V-5: la circunstancia de la alerta cita las fuentes de la alerta.
    datos = base_alerta()
    datos["alerta_descartada"]["fuentes"] = []
    assert rutas(datos, "ERR-03") == ["alerta_descartada.circunstancias_consideradas[0].fuentes[0]"]


def test_sistema_y_persona_de_una_participacion():
    datos = base_alerta()
    datos["participaciones_ia"][0]["sistema"] = "SIS-X"
    datos["participaciones_ia"][0]["intervencion_humana"] = [intervencion("P-9", "2027-10-05")]
    errores = validar(datos).errores
    assert [(e.codigo, e.ruta) for e in errores if e.codigo == "ERR-03"] == [
        ("ERR-03", "participaciones_ia[0].sistema"),
        ("ERR-03", "participaciones_ia[0].intervencion_humana[0].persona"),
    ]


def test_expediente_devuelto_no_se_comprueba():
    # Modelo, V-5: el expediente devuelto no está en la entrada.
    datos = registro(expediente(origen_tipo="devolucion_servicio_ejecutivo", expediente_devuelto="EXP-ANTERIOR"))
    assert validar(datos).valida


# --- ERR-04: fechas -----------------------------------------------------------


def test_orden_de_fechas():
    # Modelo, V-6.
    datos = registro(expediente(fin_analisis="2028-02-10", comunicacion="2028-03-01", cierre="2028-02-01"))
    assert rutas(datos, "ERR-04") == [
        "expediente.fecha_fin_analisis_tecnico",
        "expediente.decision_comunicacion.comunicacion.fecha",
        "expediente.fecha_cierre",
    ]


def test_cierre_antes_de_la_decision_se_admite():
    # Modelo, V-6: no se compara el cierre con la decisión ni con la comunicación (R-9).
    datos = registro(expediente(cierre="2028-03-01"))
    assert validar(datos).valida


# --- ERR-05: coherencia -------------------------------------------------------


def test_decisor_incoherente():
    # Modelo, V-7.
    datos = base_expediente()
    datos["expediente"]["decision_comunicacion"]["decisor"] = {"tipo": "persona", "persona": None, "votos": []}
    assert sorted(rutas(datos, "ERR-05")) == [
        "expediente.decision_comunicacion.decisor.persona",
        "expediente.decision_comunicacion.decisor.votos",
    ]
    datos["expediente"]["decision_comunicacion"]["decisor"] = {"tipo": "organo_control_interno", "persona": "P-1", "votos": None}
    assert rutas(datos, "ERR-05") == ["expediente.decision_comunicacion.decisor.persona"]


def test_organo_sin_votos_se_admite():
    # §8.1: `votos` null si el acta no los recoge uno por uno.
    datos = registro(expediente(decisor={"tipo": "organo_control_interno", "persona": None, "votos": None}))
    assert validar(datos).valida


def test_expediente_devuelto_incoherente():
    datos = registro(expediente(origen_tipo="devolucion_servicio_ejecutivo"))
    assert rutas(datos, "ERR-05") == ["expediente.origen.expediente_devuelto"]
    datos = registro(expediente(expediente_devuelto="EXP-ANTERIOR"))
    assert rutas(datos, "ERR-05") == ["expediente.origen.expediente_devuelto"]


# --- ERR-06 y ERR-07 -----------------------------------------------------------


def test_comunicacion_sin_haber_decidido_comunicar():
    # Modelo, V-8.
    datos = base_expediente()
    datos["expediente"]["decision_comunicacion"]["comunicar"] = False
    assert codigos(datos) == ["ERR-06"]


def test_comunicar_sin_comunicacion_se_admite():
    # Modelo, V-8: decidido y no hecho todavía es un hecho.
    assert validar(registro(expediente(comunicacion=None))).valida


def test_razones_vacias():
    # Modelo, V-12.
    assert codigos(registro(expediente(razones=[]))) == ["ERR-07"]


# --- ERR-08 y ERR-09 -----------------------------------------------------------


def test_ni_expediente_ni_alerta_o_los_dos():
    # Modelo, V-13.
    assert codigos(registro()) == ["ERR-08"]
    datos = base_alerta()
    datos["expediente"] = expediente()
    assert "ERR-08" in codigos(datos)


def test_sistema_sin_participacion():
    # Modelo, V-13.
    datos = base_expediente()
    datos["sistemas"] = [sistema("SIS-Z")]
    assert rutas(datos, "ERR-09") == ["sistemas[0]"]


# --- ERR-10: participaciones de la alerta descartada -------------------------------


def test_alerta_sin_generacion():
    # Modelo, V-14.
    datos = base_alerta()
    datos["participaciones_ia"][0]["momento"] = "priorizacion_alerta"
    assert codigos(datos) == ["ERR-10"]


def test_alerta_con_propuesta_de_decision():
    datos = base_alerta()
    datos["participaciones_ia"].append(participacion("IA-2", "SIS-A", "propuesta_decision", "2027-10-04"))
    datos["alerta_descartada"]["participaciones_ia"].append("IA-2")
    assert rutas(datos, "ERR-10") == ["alerta_descartada.participaciones_ia[1]"]


def test_alerta_sin_fuentes_circunstancias_ni_resultado_se_admite():
    # Modelo, V-15.
    datos = registro(
        alerta_=alerta(fuentes=[], circunstancias=[], resultado=None),
        participaciones=[participacion("IA-1", "SIS-A", "generacion_alerta", "2028-05-09")],
    )
    assert validar(datos).valida


# --- ERR-11: participación sin citar -------------------------------------------


def test_participacion_sin_citar():
    # Modelo, V-16.
    datos = registro(
        expediente(), participaciones=[participacion("IA-9", "SIS-A", "analisis", "2028-02-20")]
    )
    assert rutas(datos, "ERR-11") == ["participaciones_ia[0]"]


def test_v17_alerta_incorporada_a_un_expediente_de_comunicacion_interna():
    """Modelo, V-17: una alerta que llega después a un expediente abierto por un empleado."""
    alerta_posterior = participacion("IA-5", "SIS-A", "generacion_alerta", "2027-06-28")
    # Citada en `participaciones_incorporadas`: se acepta.
    datos = registro(
        expediente(origen_tipo="comunicacion_interna", incorporadas=["IA-5"]), participaciones=[alerta_posterior]
    )
    assert validar(datos).valida
    # Sin citar en ninguna parte: ERR-11.
    datos = registro(expediente(origen_tipo="comunicacion_interna"), participaciones=[alerta_posterior])
    assert codigos(datos) == ["ERR-11"]
    # Una fecha anterior a la apertura no se comprueba.
    datos = registro(
        expediente(origen_tipo="comunicacion_interna", incorporadas=["IA-5"], apertura="2028-02-14"),
        participaciones=[dict(alerta_posterior, fecha="2020-01-01")],
    )
    assert validar(datos).valida


def test_citada_por_fase_o_circunstancia():
    p = participacion("IA-2", "SIS-B", "analisis", "2028-02-20")
    assert validar(registro(expediente(fases=[fase("FA-1", participaciones=["IA-2"])]), participaciones=[p])).valida
    circunstancias = [circunstancia("C-1", participaciones=["IA-2"])]
    assert validar(registro(expediente(circunstancias=circunstancias), participaciones=[p])).valida


# --- ERR-12: participaciones del origen ------------------------------------------


def test_origen_alerta_sin_generacion():
    # Modelo, V-18.
    datos = registro(expediente(origen_tipo="alerta"))
    assert rutas(datos, "ERR-12") == ["expediente.origen.participaciones_ia"]


def test_origen_con_analisis():
    p = participacion("IA-1", "SIS-A", "analisis", "2028-02-10")
    datos = registro(expediente(origen_participaciones=["IA-1"]), participaciones=[p])
    assert rutas(datos, "ERR-12") == ["expediente.origen.participaciones_ia[0]"]


def test_origen_alerta_con_generacion():
    p = participacion("IA-1", "SIS-A", "generacion_alerta", "2028-02-10")
    assert validar(registro(expediente(origen_tipo="alerta", origen_participaciones=["IA-1"]), participaciones=[p])).valida


def test_se_recogen_todos_los_errores():
    datos = registro(expediente(razones=[], comunicacion="2028-03-01"))
    datos["sistemas"] = [sistema("SIS-Z")]
    assert codigos(datos) == ["ERR-04", "ERR-07", "ERR-09"]


def test_persona_sin_cargos_se_admite():
    datos = base_expediente()
    datos["personas"].append(persona("P-9"))
    datos["personas"][-1]["cargos"] = []
    assert validar(datos).valida


def test_decisor_persona_es_la_base():
    assert validar(registro(expediente(decisor=decisor_persona("P-6")))).valida
