"""D-7: todo `indeterminado` queda atribuido, y solo a dimensiones que cambian el estado.

Se recorren combinaciones de variantes de un expediente y de una alerta
descartada (fechas a los dos lados del 10 de julio de 2027, decisores,
participaciones y huecos del registro), y en cada régimen se comprueba el
criterio de D-7 contra la rejilla completa de lecturas.
"""

from itertools import product

from ayudas import (
    PERSONAS,
    alerta,
    cargar_dict,
    circunstancia,
    decisor_organo,
    decisor_persona,
    expediente,
    fase,
    intervencion,
    participacion,
    persona,
    registro,
)
from registro.calculo import DIMENSIONES, INDETERMINADO, REGIMENES, _estado_en, calcular

PERSONAS_AMPLIADAS = PERSONAS + [persona("P-8", "persona_autorizada_por_el_representante")]

FECHAS = {
    "antes": dict(apertura="2026-04-06", fin_analisis="2026-04-20", decision="2026-04-24", cierre="2026-05-04"),
    "abarca": dict(apertura="2027-06-21", fin_analisis="2027-07-14", decision="2027-07-16", cierre="2027-07-19"),
    "despues": dict(apertura="2028-02-14", fin_analisis="2028-02-28", decision="2028-03-03", cierre="2028-03-10"),
}
DECISORES = {
    "representante": decisor_persona("P-1"),
    "responsable": decisor_persona("P-6"),
    "autorizada": decisor_persona("P-8"),
    "organo_con_abstencion": decisor_organo(
        {"persona": "P-2", "sentido": "comunicar", "motivacion": "Motivo de ejemplo"},
        {"persona": "P-3", "sentido": "comunicar", "motivacion": "Motivo de ejemplo"},
        {"persona": "P-5", "sentido": "no_comunicar", "motivacion": "Motivo de ejemplo"},
        {"persona": "P-1", "sentido": "abstencion", "motivacion": "Motivo de ejemplo"},
    ),
}


def _participaciones(tipo, decision):
    if tipo == "ninguna":
        return [], {}
    if tipo == "propuesta":
        p = participacion("IA-7", "SIS-C", "propuesta_decision", decision)
        return [p], dict(fases=[fase("FA-1", participaciones=["IA-7"])])
    p = participacion("IA-2", "SIS-B", "analisis", decision, [intervencion("P-4", decision)])
    return [p], dict(
        fases=[fase("FA-1", participaciones=["IA-2"])],
        circunstancias=[circunstancia("C-1"), circunstancia("C-2", participaciones=["IA-2"])],
        razones=[{"descripcion": "Razón de ejemplo", "circunstancias": ["C-2"]}],
    )


def _expedientes():
    for fechas, decisor, tipo, sin_circunstancias, comunicacion_interna in product(
        FECHAS, DECISORES, ("ninguna", "propuesta", "en_razones"), (False, True), (False, True)
    ):
        participaciones, extra = _participaciones(tipo, FECHAS[fechas]["decision"])
        if sin_circunstancias:
            extra = {**extra, "circunstancias": [], "razones": [{"descripcion": "Razón", "circunstancias": []}]}
        x = expediente(
            **FECHAS[fechas],
            comunicacion=None,
            decisor=DECISORES[decisor],
            origen_tipo="comunicacion_interna" if comunicacion_interna else "otro",
            **extra,
        )
        yield registro(x, participaciones=participaciones, personas=PERSONAS_AMPLIADAS)


def _alertas():
    for revision, vacia in product(("2026-11-10", "2027-10-05"), (False, True)):
        a = alerta(revision=revision, **(dict(fuentes=[], circunstancias=[], resultado=None) if vacia else {}))
        yield registro(alerta_=a, participaciones=[participacion("IA-1", "SIS-A", "generacion_alerta", revision)])


def _comprobar(resultado):
    for g in REGIMENES:
        res = resultado.regimenes[g]
        if res.estado != INDETERMINADO:
            assert res.atribuciones == ()
            continue
        assert res.atribuciones, f"{g}: indeterminado sin atribuir"
        hojas = [(l.lecturas, l.estado) for l in res.lecturas]
        presentes = {d for l in res.lecturas for d, _ in l.lecturas}
        atribuidas = {a.dimension for a in res.atribuciones}
        rejilla = [
            dict(zip(sorted(presentes), valores))
            for valores in product(*(DIMENSIONES[d].lecturas for d in sorted(presentes)))
        ]
        for d in presentes:
            cambia = any(
                _estado_en(hojas, {**p, d: r}) != _estado_en(hojas, p) for p in rejilla for r in DIMENSIONES[d].lecturas
            )
            assert cambia == (d in atribuidas), f"{g}: {d}"
        assert {d.dimension for d in res.decisiones} == atribuidas


def test_ningun_indeterminado_queda_sin_atribuir():
    vistos = 0
    for datos in list(_expedientes()) + list(_alertas()):
        resultado = calcular(cargar_dict(datos))
        _comprobar(resultado)
        vistos += sum(r.estado == INDETERMINADO for r in resultado.regimenes.values())
    # Que el recorrido pruebe algo: hay muchos indeterminados.
    assert vistos > 100


def test_cada_dimension_se_atribuye_en_algun_caso():
    atribuidas = set()
    for datos in list(_expedientes()) + list(_alertas()):
        for res in calcular(cargar_dict(datos)).regimenes.values():
            atribuidas |= {a.dimension for a in res.atribuciones}
    assert atribuidas == set(DIMENSIONES)
