"""Los ejemplos del §7 de docs/especificacion-calculo.md, con sus fechas.

Todos los textos son genéricos e inventados, y las salidas de los sistemas,
cadenas opacas (modelo, §0.2, regla 3).
"""

import re
from pathlib import Path

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
    sistema,
    voto,
)
from registro.calculo import (
    AMLR,
    COMPLETO,
    INCOMPLETO,
    INDETERMINADO,
    LEY_RD,
    NO_EXIGIBLE,
    REGIMENES,
    T1,
    T2,
    T3,
    TRANSICION,
    calcular,
)
from registro.carga import cargar

RAIZ = Path(__file__).resolve().parent.parent
EJEMPLOS_MODELO = re.findall(r"```json\n(.*?)\n```", (RAIZ / "docs" / "modelo-datos.md").read_text(encoding="utf-8"), re.S)


def estados(resultado):
    return {r: resultado.regimenes[r].estado for r in REGIMENES}


def tabla(res):
    """{lecturas: (estado, faltas)} de un régimen."""
    return {l.ids: (l.estado, l.faltas) for l in res.lecturas}


def atribuidas(res):
    return [a.dimension for a in res.atribuciones]


def avisos(res):
    return {a.codigo for a in res.avisos}


# --- Ejemplo 1 --------------------------------------------------------------------------


def test_ejemplo_1_expediente_del_modelo():
    r = calcular(cargar(EJEMPLOS_MODELO[0]).entrada)
    assert r.regimenes[LEY_RD].estado == COMPLETO
    amlr = r.regimenes[AMLR]
    assert amlr.estado == INDETERMINADO
    assert atribuidas(amlr) == ["SC", "DC"]
    # IH se consulta (IA-2 llega a las razones) pero no cambia nada: cumple con las tres lecturas.
    assert {dict(l.lecturas)["IH"] for l in amlr.lecturas} == {"IH-1", "IH-2", "IH-3"}
    por_sc_dc = {(dict(l.lecturas)["SC"], dict(l.lecturas)["DC"]): (l.estado, l.faltas) for l in amlr.lecturas}
    assert por_sc_dc == {
        ("SC-1", "DC-1"): (INCOMPLETO, ("AM-04",)),
        ("SC-1", "DC-2"): (INCOMPLETO, ("AM-04", "AM-07")),
        ("SC-2", "DC-1"): (COMPLETO, ()),
        ("SC-2", "DC-2"): (INCOMPLETO, ("AM-07",)),
        ("SC-3", "DC-1"): (COMPLETO, ()),
        ("SC-3", "DC-2"): (INCOMPLETO, ("AM-07",)),
    }
    sc = next(a for a in amlr.atribuciones if a.dimension == "SC")
    assert sc.datos == ("participaciones_ia[0] (IA-1)", "participaciones_ia[1] (IA-2)")
    decisiones = {d.dimension: {x.lectura: x for x in d.respuestas} for d in amlr.decisiones}
    assert decisiones["SC"]["SC-1"].estados == (INCOMPLETO,) and decisiones["SC"]["SC-1"].depende_de == ()
    assert decisiones["SC"]["SC-2"].depende_de == ("DC",)
    assert decisiones["DC"]["DC-2"].estados == (INCOMPLETO,)
    assert decisiones["DC"]["DC-1"].depende_de == ("SC",)
    assert "D-9" in avisos(amlr)
    # T-1 a T-3 dan la misma tabla.
    for t in TRANSICION:
        assert r.regimenes[t].estado == INDETERMINADO
        assert atribuidas(r.regimenes[t]) == ["SC", "DC"]
    assert r.transicion_coincide
    assert not r.normas_coinciden
    i = r.informativos
    assert (i.dias_analisis_a_decision, i.dias_decision_a_comunicacion) == (3, 1)
    assert i.umbral_operaciones.valor == INDETERMINADO
    assert i.umbral_operaciones.lecturas == (("OA-1", 2026, "supera"), ("OA-2", 2027, "sin_dato"))
    assert i.declaraciones == (("SIS-A", "no", ("IA-1",)), ("SIS-B", "si", ("IA-2",)))
    assert r.exige_actuar


# --- Ejemplo 2 --------------------------------------------------------------------------


def test_ejemplo_2_alerta_del_modelo():
    r = calcular(cargar(EJEMPLOS_MODELO[1]).entrada)
    assert r.regimenes[LEY_RD].estado == NO_EXIGIBLE
    for g in (AMLR, *TRANSICION):
        res = r.regimenes[g]
        assert res.estado == INDETERMINADO
        assert atribuidas(res) == ["AD"]
        assert {l.estado for l in res.lecturas} == {NO_EXIGIBLE, COMPLETO}
    # D-25: en ninguna lectura falta nada.
    assert not r.exige_actuar


def _alerta_vacia(revision, generada):
    return registro(
        alerta_=alerta(revision=revision, fuentes=[], circunstancias=[], resultado=None),
        participaciones=[participacion("IA-1", "SIS-A", "generacion_alerta", generada)],
    )


def test_ejemplo_2_variante_sin_nada_mas_que_la_revision():
    r = calcular(cargar_dict(_alerta_vacia("2028-05-10", "2028-05-09")))
    assert r.regimenes[LEY_RD].estado == NO_EXIGIBLE
    amlr = r.regimenes[AMLR]
    assert amlr.estado == INDETERMINADO and atribuidas(amlr) == ["AD"]
    assert tabla(amlr) == {
        ("AD-1",): (NO_EXIGIBLE, ()),
        ("SC-1", "AD-2"): (INCOMPLETO, ("AM-01", "AM-02", "AM-03", "AM-04")),
        ("SC-2", "AD-2"): (INCOMPLETO, ("AM-01", "AM-02", "AM-03")),
        ("SC-3", "AD-2"): (INCOMPLETO, ("AM-01", "AM-02", "AM-03")),
    }
    for t in TRANSICION:
        assert tabla(r.regimenes[t]) == tabla(amlr)
    assert r.exige_actuar


def test_ejemplo_2_variante_revisada_antes_de_la_aplicacion():
    r = calcular(cargar_dict(_alerta_vacia("2026-11-10", "2026-11-09")))
    for t in TRANSICION:
        assert r.regimenes[t].estado == NO_EXIGIBLE
    assert "D-23" in avisos(r.regimenes[AMLR])


# --- Ejemplo 3 --------------------------------------------------------------------------


def _ejemplo_3(comunicante=None, circunstancias=(), razones_circunstancias=()):
    alerta_incorporada = participacion("IA-5", "SIS-A", "generacion_alerta", "2027-06-28")
    return registro(
        expediente(
            apertura="2027-06-21",
            fin_analisis="2027-07-14",
            decision="2027-07-16",
            cierre="2027-07-19",
            comunicar=False,
            origen_tipo="comunicacion_interna",
            incorporadas=["IA-5"],
            circunstancias=list(circunstancias),
            razones=[{"descripcion": "Razón de ejemplo", "circunstancias": list(razones_circunstancias)}],
            comunicante=comunicante,
        ),
        participaciones=[alerta_incorporada],
    )


def test_ejemplo_3_expediente_que_abarca_la_fecha_de_aplicacion():
    r = calcular(cargar_dict(_ejemplo_3()))
    ley = r.regimenes[LEY_RD]
    assert (ley.estado, ley.faltas_seguras) == (INCOMPLETO, ("RD-15",))
    amlr = r.regimenes[AMLR]
    assert amlr.estado == INCOMPLETO
    assert amlr.faltas_seguras == ("AM-02",)
    assert list(amlr.faltas_segun_lectura) == ["AM-04"]
    assert all("SC-1" in ids for ids in amlr.faltas_segun_lectura["AM-04"])
    # SC se consulta pero no cambia el estado: no se atribuye (D-7).
    assert amlr.atribuciones == ()
    assert "D-23" in avisos(amlr)
    for t in TRANSICION:
        res = r.regimenes[t]
        assert res.estado == INCOMPLETO
        por_ft = {}
        for l in res.lecturas:
            por_ft.setdefault(dict(l.lecturas)["FT"], set()).update(l.faltas)
        assert por_ft["FT-1"] == {"RD-15"}
    assert {f for l in r.regimenes[T1].lecturas if dict(l.lecturas)["FT"] == "FT-2" for f in l.faltas} == {"AM-02", "AM-04"}
    assert {f for l in r.regimenes[T2].lecturas if dict(l.lecturas)["FT"] == "FT-2" for f in l.faltas} == {
        "RD-15",
        "AM-02",
        "AM-04",
    }
    # T-1 no coincide con T-2 y T-3 porque sus faltas son distintas (D-26).
    assert not r.transicion_coincide
    assert r.regimenes[T2].firma == r.regimenes[T3].firma


def test_ejemplo_3_variante_b_dos_dimensiones_que_solo_cambian_el_estado_juntas():
    datos = _ejemplo_3("2027-07-20", [circunstancia("C-1")], ["C-1"])
    r = calcular(cargar_dict(datos))
    assert r.regimenes[LEY_RD].estado == COMPLETO
    amlr = r.regimenes[AMLR]
    assert (amlr.estado, atribuidas(amlr)) == (INDETERMINADO, ["SC"])
    for t in TRANSICION:
        res = r.regimenes[t]
        assert res.estado == INDETERMINADO
        assert atribuidas(res) == ["SC", "FT"]
        rejilla = {(dict(l.lecturas).get("SC", "—"), dict(l.lecturas)["FT"]): l.estado for l in res.lecturas}
        assert rejilla[("—", "FT-1")] == COMPLETO
        assert rejilla[("SC-1", "FT-2")] == INCOMPLETO
        assert rejilla[("SC-2", "FT-2")] == rejilla[("SC-3", "FT-2")] == COMPLETO
        ft = next(d for d in res.decisiones if d.dimension == "FT")
        respuestas = {x.lectura: x for x in ft.respuestas}
        assert (respuestas["FT-1"].estados, respuestas["FT-1"].depende_de) == ((COMPLETO,), ())
        assert respuestas["FT-2"].depende_de == ("SC",)


# --- Ejemplo 4 --------------------------------------------------------------------------


def _ejemplo_4(intervenciones=()):
    propuesta = participacion("IA-7", "SIS-C", "propuesta_decision", "2028-03-01", intervenciones)
    return registro(
        expediente(
            fases=[fase("FA-1"), fase("FA-2", participaciones=["IA-7"])],
            circunstancias=[circunstancia("C-1"), circunstancia("C-2", fuentes=[], participaciones=["IA-7"])],
            razones=[{"descripcion": "Razón de ejemplo", "circunstancias": ["C-1"]}],
        ),
        participaciones=[propuesta],
        sistemas=[sistema("SIS-C", "desconocido")],
    )


def test_ejemplo_4_un_sistema_propone_la_decision_y_nadie_revisa_su_salida():
    r = calcular(cargar_dict(_ejemplo_4()))
    assert r.regimenes[LEY_RD].estado == COMPLETO
    for g in (AMLR, *TRANSICION):
        res = r.regimenes[g]
        assert res.estado == INDETERMINADO
        assert atribuidas(res) == ["IH"]
        por_ih = {dict(l.lecturas)["IH"]: (l.estado, l.faltas) for l in res.lecturas}
        assert por_ih == {"IH-1": (COMPLETO, ()), "IH-2": (INCOMPLETO, ("AM-06",)), "IH-3": (INCOMPLETO, ("AM-06",))}
    assert "D-9" in avisos(r.regimenes[AMLR])


def test_ejemplo_4_la_declaracion_no_cambia_nada():
    # D-18: el mismo registro con el sistema declarado «si» da el mismo resultado.
    datos = _ejemplo_4()
    datos["sistemas"] = [sistema("SIS-C", "si")]
    otro = calcular(cargar_dict(datos))
    base = calcular(cargar_dict(_ejemplo_4()))
    assert {g: base.regimenes[g].firma for g in REGIMENES} == {g: otro.regimenes[g].firma for g in REGIMENES}


def test_ejemplo_4_variante_intervencion_despues_de_la_decision():
    r = calcular(cargar_dict(_ejemplo_4([intervencion("P-4", "2028-03-05")])))
    amlr = r.regimenes[AMLR]
    por_ih = {dict(l.lecturas)["IH"]: l.faltas for l in amlr.lecturas}
    assert por_ih["IH-2"] == por_ih["IH-3"] == ("AM-06",)
    assert "D-17" in avisos(amlr)


# --- Ejemplo 5 --------------------------------------------------------------------------


def test_ejemplo_5_una_abstencion_en_el_organo_antes_de_la_aplicacion():
    personas = [dict(p) for p in PERSONAS]
    personas[0] = persona("P-1", "representante_servicio_ejecutivo", "miembro_organo_control_interno")
    decisor = decisor_organo(
        voto("P-1", "comunicar"), voto("P-2", "comunicar"), voto("P-3", "no_comunicar"), voto("P-5", "abstencion")
    )
    datos = registro(
        expediente(
            apertura="2026-04-06",
            fin_analisis="2026-04-20",
            decision="2026-04-24",
            comunicacion="2026-04-27",
            cierre="2026-05-04",
            decisor=decisor,
        ),
        personas=personas,
    )
    r = calcular(cargar_dict(datos))
    ley = r.regimenes[LEY_RD]
    assert (ley.estado, atribuidas(ley)) == (INDETERMINADO, ["MA"])
    assert tabla(ley) == {("MA-1",): (COMPLETO, ()), ("MA-2",): (INCOMPLETO, ("RD-13",))}
    assert next(a for a in ley.atribuciones).datos == ("expediente.decision_comunicacion.decisor.votos[3] (P-5)",)
    for t in TRANSICION:
        assert r.regimenes[t].firma == ley.firma
    amlr = r.regimenes[AMLR]
    assert "D-23" in avisos(amlr)
    assert tabla(amlr)[("DC-2",)] == (INCOMPLETO, ("AM-07",))


def test_empate_sin_mayoria_en_ninguna_lectura():
    # D-13: sin abstenciones MA no se consulta, y el empate no da mayoría.
    decisor = decisor_organo(voto("P-2", "comunicar"), voto("P-3", "no_comunicar"))
    r = calcular(cargar_dict(registro(expediente(decisor=decisor))))
    assert tabla(r.regimenes[LEY_RD]) == {(): (INCOMPLETO, ("RD-13",))}


# --- Ejemplo 6 --------------------------------------------------------------------------


def test_ejemplo_6_las_lecturas_de_la_transicion_no_coinciden():
    r = calcular(cargar_dict(registro(expediente(decisor=decisor_persona("P-6")))))
    assert tabla(r.regimenes[LEY_RD]) == {(): (INCOMPLETO, ("RD-11",))}
    assert r.regimenes[AMLR].estado == COMPLETO
    assert r.regimenes[T1].estado == COMPLETO
    t2 = r.regimenes[T2]
    assert (t2.estado, atribuidas(t2)) == (INDETERMINADO, ["DC"])
    assert tabla(t2) == {("DC-1",): (INCOMPLETO, ("RD-11",)), ("DC-2",): (COMPLETO, ())}
    assert tabla(r.regimenes[T3]) == {("DC-1",): (INCOMPLETO, ("RD-11",)), ("DC-2",): (INCOMPLETO, ("RD-11",))}
    assert r.regimenes[T3].estado == INCOMPLETO
    assert not r.transicion_coincide


# --- Otras decisiones -----------------------------------------------------------------


def test_persona_autorizada():
    # D-12 y R-10.
    personas = PERSONAS + [persona("P-8", "persona_autorizada_por_el_representante")]
    r = calcular(cargar_dict(registro(expediente(decisor=decisor_persona("P-8")), personas=personas)))
    ley = r.regimenes[LEY_RD]
    assert tabla(ley) == {("PA-1",): (COMPLETO, ()), ("PA-2",): (INCOMPLETO, ("RD-11",))}
    assert atribuidas(ley) == ["PA"]


def test_textos_en_blanco_cuentan_como_ausentes():
    # D-3.
    datos = registro(expediente())
    datos["expediente"]["origen"]["descripcion"] = "  "
    datos["expediente"]["decision_comunicacion"]["motivacion"] = ""
    r = calcular(cargar_dict(datos))
    assert r.regimenes[LEY_RD].faltas_seguras == ("RD-02", "RD-10")


def test_comunicacion_decidida_y_no_realizada():
    # D-11: aviso, no falta.
    r = calcular(cargar_dict(registro(expediente(comunicacion=None))))
    assert r.regimenes[LEY_RD].estado == COMPLETO
    assert "D-11" in avisos(r.regimenes[LEY_RD]) and "D-11" in avisos(r.regimenes[AMLR])


def test_futbol_retrasa_la_aplicacion():
    # D-2: con agente de fútbol, A es 2029-07-10 y un expediente de 2028 es anterior.
    r = calcular(cargar_dict(registro(expediente(decisor=decisor_persona("P-6")), actividad="agente_de_futbol")))
    assert r.fecha_aplicacion_amlr.year == 2029
    for t in TRANSICION:
        assert r.regimenes[t].firma == r.regimenes[LEY_RD].firma
