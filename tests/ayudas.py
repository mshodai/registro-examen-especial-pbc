"""Construcción de entradas para los tests.

Las entradas se escriben como en el JSON y pasan por la carga, así que cada
test usa una entrada válida según el modelo. Todos los textos son genéricos e
inventados (modelo, §0.2, regla 3): ninguno describe una tipología real ni un
caso real, y las salidas de los sistemas son cadenas opacas.
"""

import copy
import json

from registro.carga import cargar


def persona(id_, *cargos):
    return {"id": id_, "cargos": list(cargos) or ["otro"]}


def sistema(id_, declaracion="desconocido"):
    return {"id": id_, "declaracion_sistema_ia": declaracion}


def intervencion(persona_, fecha, descripcion="Intervención de ejemplo"):
    return {"persona": persona_, "fecha": fecha, "descripcion": descripcion}


def participacion(id_, sistema_, momento, fecha, intervenciones=(), salida=None):
    return {
        "id": id_,
        "sistema": sistema_,
        "momento": momento,
        "fecha": fecha,
        "salida": salida or f"SALIDA-EJEMPLO-{id_}",
        "intervencion_humana": list(intervenciones),
    }


def fuente(id_, ambito="sujeto_obligado"):
    return {"id": id_, "descripcion": f"Fuente de ejemplo {id_}", "ambito": ambito}


def fase(id_, fuentes=("F-1",), participaciones=(), gestiones=("Gestión de ejemplo",)):
    return {
        "id": id_,
        "descripcion": f"Fase de ejemplo {id_}",
        "gestiones": list(gestiones),
        "fuentes": list(fuentes),
        "participaciones_ia": list(participaciones),
    }


def circunstancia(id_, fuentes=("F-1",), participaciones=()):
    return {
        "id": id_,
        "descripcion": f"Circunstancia de ejemplo {id_} (motivo inventado)",
        "fuentes": list(fuentes),
        "participaciones_ia": list(participaciones),
    }


def voto(persona_, sentido, motivacion="Motivación de ejemplo del voto"):
    return {"persona": persona_, "sentido": sentido, "motivacion": motivacion}


def decisor_persona(persona_):
    return {"tipo": "persona", "persona": persona_, "votos": None}


def decisor_organo(*votos, tipo="organo_control_interno"):
    return {"tipo": tipo, "persona": None, "votos": list(votos)}


def expediente(
    apertura="2028-02-14",
    fin_analisis="2028-02-28",
    decision="2028-03-03",
    cierre="2028-03-10",
    comunicar=True,
    comunicacion="2028-03-06",
    copia="DOC-EJEMPLO-0001",
    decisor=None,
    origen_tipo="otro",
    origen_participaciones=(),
    incorporadas=(),
    fases=None,
    fuentes=None,
    circunstancias=None,
    razones=None,
    comunicante=None,
    expediente_devuelto=None,
):
    """Un expediente completo con los dos regímenes, sin participaciones de sistemas."""
    return {
        "id": "EXP-EJEMPLO",
        "fecha_apertura": apertura,
        "fecha_fin_analisis_tecnico": fin_analisis,
        "fecha_cierre": cierre,
        "origen": {
            "tipo": origen_tipo,
            "descripcion": "Motivo de ejemplo del examen (inventado)",
            "participaciones_ia": list(origen_participaciones),
            "expediente_devuelto": expediente_devuelto,
        },
        "participaciones_incorporadas": list(incorporadas),
        "operativa_analizada": {
            "descripcion": "Operativa de ejemplo de un cliente ficticio",
            "operaciones": [{"id": "OP-1", "descripcion": "Operación de ejemplo 1", "ejecutada": True}],
            "intervinientes": [{"id": "INT-1", "papel": "cliente"}],
        },
        "fuentes": fuentes if fuentes is not None else [fuente("F-1")],
        "fases": fases if fases is not None else [fase("FA-1")],
        "circunstancias_consideradas": circunstancias if circunstancias is not None else [circunstancia("C-1")],
        "conclusion": {
            "texto": "Conclusión de ejemplo (motivo inventado)",
            "razones": razones if razones is not None else [{"descripcion": "Razón de ejemplo", "circunstancias": ["C-1"]}],
        },
        "decision_comunicacion": {
            "comunicar": comunicar,
            "fecha": decision,
            "motivacion": "Motivación de ejemplo de la decisión",
            "decisor": decisor or decisor_persona("P-1"),
            "comunicacion": (
                {"fecha": comunicacion, "referencia_copia": copia} if comunicar and comunicacion is not None else None
            ),
            "fecha_puesta_en_conocimiento_comunicante": comunicante,
        },
    }


def alerta(
    revision="2027-10-05",
    participaciones=("IA-1",),
    fuentes=None,
    circunstancias=None,
    resultado="Resultado de ejemplo (motivo inventado)",
    revisor="P-4",
):
    return {
        "id": "ALE-EJEMPLO",
        "participaciones_ia": list(participaciones),
        "descripcion_operativa": "Operación de ejemplo de un cliente ficticio",
        "revision": {"persona": revisor, "fecha": revision},
        "fuentes": fuentes if fuentes is not None else [fuente("F-1")],
        "circunstancias_consideradas": (
            circunstancias if circunstancias is not None else [circunstancia("C-1", participaciones=["IA-1"])]
        ),
        "resultado": resultado,
    }


PERSONAS = [
    persona("P-1", "representante_servicio_ejecutivo", "responsable_cumplimiento_normativo"),
    persona("P-2", "miembro_organo_control_interno"),
    persona("P-3", "miembro_organo_control_interno"),
    persona("P-4"),
    persona("P-5", "miembro_organo_control_interno"),
    persona("P-6", "responsable_cumplimiento_normativo"),
]


def registro(expediente_=None, alerta_=None, participaciones=(), sistemas=None, personas=None,
             actividad="otra", operaciones_anuales=None):
    """Una entrada completa en forma de dict (como el JSON)."""
    if sistemas is None:
        sistemas = [sistema(s) for s in dict.fromkeys(p["sistema"] for p in participaciones)]
    return {
        "version_modelo": 1,
        "sujeto": {
            "actividad": actividad,
            "operaciones_anuales": operaciones_anuales if operaciones_anuales is not None else [{"anio": 2026, "numero": 18450}],
        },
        "personas": copy.deepcopy(personas if personas is not None else PERSONAS),
        "sistemas": sistemas,
        "participaciones_ia": list(participaciones),
        "expediente": expediente_,
        "alerta_descartada": alerta_,
    }


def cargar_dict(datos):
    """La entrada validada; falla si no es válida, con sus errores."""
    resultado = cargar(json.dumps(datos))
    assert resultado.valida, resultado.errores
    return resultado.entrada
