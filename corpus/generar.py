"""Genera el corpus: registros sintéticos con su resultado esperado.

Los resultados esperados están escritos a mano a partir de
docs/especificacion-calculo.md, no sacados del código. Antes de escribir nada,
cada caso se calcula con el código de src/ y se compara con lo esperado. Si
alguno no coincide, termina con error y no escribe ningún fichero.

    python corpus/generar.py

Los datos son sintéticos (modelo, §0.2, regla 3): identificadores con
«FICTICIO», motivos genéricos e inventados y salidas de los sistemas como
cadenas opacas.
"""

import json
import sys
from dataclasses import dataclass
from pathlib import Path

DIRECTORIO = Path(__file__).resolve().parent
# Usa siempre el código de src/, no una versión instalada del paquete.
sys.path.insert(0, str(DIRECTORIO.parent / "src"))

from registro.calculo import REGIMENES  # noqa: E402
from registro.carga import cargar  # noqa: E402
from registro.cli import codigo_de_salida  # noqa: E402
from registro.salida import como_dict, informe  # noqa: E402

COMPLETO = "completo"
INCOMPLETO = "incompleto"
NO_EXIGIBLE = "no_exigible"
INDET = "indeterminado"


# --- Entradas ---------------------------------------------------------------------------


def persona(n, *cargos):
    return {"id": f"P-FICTICIO-{n}", "cargos": list(cargos) or ["otro"]}


PERSONAS = [
    persona(1, "representante_servicio_ejecutivo", "responsable_cumplimiento_normativo"),
    persona(2, "miembro_organo_control_interno"),
    persona(3, "miembro_organo_control_interno"),
    persona(4),
    persona(5, "miembro_organo_control_interno"),
    persona(6, "responsable_cumplimiento_normativo"),
    persona(7, "miembro_organo_control_interno"),
]


def p(n):
    return f"P-FICTICIO-{n}"


def sistema(letra, declaracion):
    return {"id": f"SIS-FICTICIO-{letra}", "declaracion_sistema_ia": declaracion}


def participacion(n, letra, momento, fecha, intervenciones=()):
    return {
        "id": f"IA-FICTICIO-{n}",
        "sistema": f"SIS-FICTICIO-{letra}",
        "momento": momento,
        "fecha": fecha,
        "salida": f"SALIDA-FICTICIO-{n}",
        "intervencion_humana": [
            {"persona": p(quien), "fecha": cuando, "descripcion": "Contraste de ejemplo de la salida con una fuente"}
            for quien, cuando in intervenciones
        ],
    }


def ia(n):
    return f"IA-FICTICIO-{n}"


FUENTE = {"id": "F-FICTICIO-1", "descripcion": "Documentación de ejemplo del cliente ficticio", "ambito": "sujeto_obligado"}


def fase(n, participaciones=()):
    return {
        "id": f"FA-FICTICIO-{n}",
        "descripcion": f"Fase de análisis de ejemplo {n}",
        "gestiones": [f"Gestión de ejemplo {n}"],
        "fuentes": ["F-FICTICIO-1"],
        "participaciones_ia": list(participaciones),
    }


def circunstancia(n, fuentes=("F-FICTICIO-1",), participaciones=()):
    return {
        "id": f"C-FICTICIO-{n}",
        "descripcion": f"Circunstancia de ejemplo {n} (motivo inventado)",
        "fuentes": list(fuentes),
        "participaciones_ia": list(participaciones),
    }


def razon(*circunstancias):
    return {"descripcion": "Razón de ejemplo (motivo inventado)", "circunstancias": [f"C-FICTICIO-{c}" for c in circunstancias]}


FECHAS_2028 = dict(apertura="2028-02-14", fin="2028-02-28", decision="2028-03-03", comunicacion="2028-03-06", cierre="2028-03-10")


def expediente(n, fechas, decisor, *, comunicar=True, origen="otro", origen_participaciones=(), incorporadas=(),
               fases=None, circunstancias=None, razones=None, comunicante=None):
    return {
        "id": f"EXP-FICTICIO-{n:02d}",
        "fecha_apertura": fechas["apertura"],
        "fecha_fin_analisis_tecnico": fechas["fin"],
        "fecha_cierre": fechas["cierre"],
        "origen": {
            "tipo": origen,
            "descripcion": "Motivo de ejemplo que dio lugar al examen (inventado)",
            "participaciones_ia": list(origen_participaciones),
            "expediente_devuelto": None,
        },
        "participaciones_incorporadas": list(incorporadas),
        "operativa_analizada": {
            "descripcion": "Operativa de ejemplo de un cliente ficticio",
            "operaciones": [{"id": "OP-FICTICIO-1", "descripcion": "Operación de ejemplo", "ejecutada": True}],
            "intervinientes": [{"id": "INT-FICTICIO-1", "papel": "cliente"}],
        },
        "fuentes": [FUENTE],
        "fases": fases if fases is not None else [fase(1)],
        "circunstancias_consideradas": circunstancias if circunstancias is not None else [circunstancia(1)],
        "conclusion": {"texto": "Conclusión de ejemplo (motivo inventado)", "razones": razones or [razon(1)]},
        "decision_comunicacion": {
            "comunicar": comunicar,
            "fecha": fechas["decision"],
            "motivacion": "Motivación de ejemplo de la decisión",
            "decisor": decisor,
            "comunicacion": (
                {"fecha": fechas["comunicacion"], "referencia_copia": f"DOC-FICTICIO-{n:02d}"} if comunicar else None
            ),
            "fecha_puesta_en_conocimiento_comunicante": comunicante,
        },
    }


def decisor_persona(n):
    return {"tipo": "persona", "persona": p(n), "votos": None}


def decisor_organo(*votos):
    return {
        "tipo": "organo_control_interno",
        "persona": None,
        "votos": [{"persona": p(n), "sentido": s, "motivacion": "Motivación de ejemplo del voto"} for n, s in votos],
    }


def registro(expediente_=None, alerta=None, participaciones=(), sistemas=()):
    return {
        "version_modelo": 1,
        "sujeto": {"actividad": "otra", "operaciones_anuales": [{"anio": 2027, "numero": 9500}]},
        "personas": PERSONAS,
        "sistemas": list(sistemas),
        "participaciones_ia": list(participaciones),
        "expediente": expediente_,
        "alerta_descartada": alerta,
    }


# --- Resultado esperado --------------------------------------------------------------------


def resp(estados, depende=()):
    """Una respuesta de una decisión (D-8): estados y de qué depende aún."""
    return {"estados": sorted(estados), "depende_de": list(depende)}


def reg(estado, decisiones=None, en_todas=(), segun_lectura=(), avisos=()):
    """Un régimen: estado, decisiones por dimensión, faltas (D-5) y códigos de aviso."""
    return {
        "estado": estado,
        "decisiones": decisiones or {},
        "faltas_en_todas": list(en_todas),
        "faltas_segun_lectura": list(segun_lectura),
        "avisos": sorted(set(avisos)),
    }


def resultado(codigo, regimenes):
    return {"codigo_salida": codigo, "regimenes": dict(zip(REGIMENES, regimenes))}


def resumen(inf):
    """Lo que se compara de cada caso, sacado de la salida en JSON (especificación, §9)."""
    datos = como_dict(inf)
    regimenes = {}
    for r in REGIMENES:
        d = datos["regimenes"][r]
        regimenes[r] = reg(
            d["estado"],
            {
                x["dimension"]: {y["lectura"]: resp(y["estados"], y["depende_de"]) for y in x["respuestas"]}
                for x in d["decisiones"]
            },
            [f["id"] for f in d["faltas"]["en_todas"]],
            [f["id"] for f in d["faltas"]["segun_lectura"]],
            [a["codigo"] for a in d["avisos"]],
        )
    return {"codigo_salida": codigo_de_salida(inf), "regimenes": regimenes}


# --- Los casos --------------------------------------------------------------------------------


@dataclass(frozen=True)
class Caso:
    nombre: str
    demuestra: str
    entrada: dict
    esperado: dict


def _caso_01():
    # Expediente de 2028 (≥ A), sin sistemas. Decide P-1, representante y responsable del cumplimiento.
    # RD-01 a RD-14 cumplen; RD-15 no aplica. AMLR: AM-01 a AM-03 y AM-05 cumplen; AM-04 y AM-06 no
    # aplican; AM-07 cumple con DC-1 y con DC-2. T-2 con DC-2: RD-11 a RD-13 no aplican y rige AM-07.
    todos = reg(COMPLETO)
    return Caso(
        "01-expediente-completo",
        "Expediente de 2028 sin sistemas, con fases, fuentes, circunstancias, conclusión y razones, decidido por "
        "quien es a la vez representante ante el Servicio Ejecutivo y responsable del cumplimiento normativo, y "
        "comunicado con copia. Completo en los cinco regímenes y con todas las lecturas: código 0.",
        registro(expediente(1, FECHAS_2028, decisor_persona(1))),
        resultado(0, [todos] * 5),
    )


def _caso_02():
    # IA-2 (análisis) está en la fase FA-1, pero ninguna circunstancia la cita.
    # AM-04: SC-1 falta (toda salida); SC-2 falta (la cita una fase); SC-3 cumple.
    # IH no se consulta: no hay propuesta de decisión e IA-2 no llega a las razones.
    sc = {"SC-1": resp([INCOMPLETO]), "SC-2": resp([INCOMPLETO]), "SC-3": resp([COMPLETO])}
    amlr = reg(INDET, {"SC": sc}, segun_lectura=["AM-04"], avisos=["D-9"])
    return Caso(
        "02-salida-del-sistema-no-consta-como-circunstancia",
        "Expediente de 2028 en el que un sistema participó en el análisis (fase FA-FICTICIO-1), pero ninguna "
        "circunstancia considerada cita su salida. Con la Ley y el RD está completo. Con el AMLR depende de R-1: "
        "si toda salida es información considerada (SC-1) o si basta con que la haya usado una fase (SC-2), falta "
        "AM-04; si la salida no es una circunstancia (SC-3), está completo.",
        registro(
            expediente(2, FECHAS_2028, decisor_persona(1), fases=[fase(1, [ia(2)])]),
            participaciones=[participacion(2, "B", "analisis", "2028-02-20", [(4, "2028-02-21")])],
            sistemas=[sistema("B", "si")],
        ),
        resultado(1, [reg(COMPLETO), amlr, amlr, amlr, amlr]),
    )


def _caso_03():
    # Alerta revisada el 2028-05-10 sin fuentes, sin circunstancias y sin resultado.
    # Ley/RD: no exigible (D-20). AMLR: AD-1 no exigible; AD-2 faltan AM-01 a AM-03, y AM-04 con SC-1.
    # Con AD-2 las tres SC dan incompleto, así que AD-2 resuelve.
    ad = {"AD-1": resp([NO_EXIGIBLE]), "AD-2": resp([INCOMPLETO])}
    amlr = reg(INDET, {"AD": ad}, segun_lectura=["AM-01", "AM-02", "AM-03", "AM-04"], avisos=["D-9"])
    return Caso(
        "03-alerta-descartada-revisar-es-evaluar",
        "Alerta generada por un sistema el 2028-05-09 y revisada y descartada al día siguiente, sin registrar "
        "fuentes, circunstancias ni resultado. La Ley y el RD no exigen registro. Con el AMLR depende de R-6: si "
        "revisar la alerta no es evaluar (AD-1), no es exigible; si lo es (AD-2), faltan la información, las "
        "circunstancias y el resultado del art. 77.1.b.",
        registro(
            alerta={
                "id": "ALE-FICTICIO-03",
                "participaciones_ia": [ia(1)],
                "descripcion_operativa": "Operación de ejemplo de un cliente ficticio",
                "revision": {"persona": p(4), "fecha": "2028-05-10"},
                "fuentes": [],
                "circunstancias_consideradas": [],
                "resultado": None,
            },
            participaciones=[participacion(1, "A", "generacion_alerta", "2028-05-09")],
            sistemas=[sistema("A", "no")],
        ),
        resultado(1, [reg(NO_EXIGIBLE), amlr, amlr, amlr, amlr]),
    )


def _caso_04():
    # IA-7 propone la decisión el 2028-03-01 y no tiene intervención humana. La citan FA-2 y C-2,
    # así que AM-04 cumple con las tres SC. AM-06: IH-1 cumple; IH-2 e IH-3 faltan.
    ih = {"IH-1": resp([COMPLETO]), "IH-2": resp([INCOMPLETO]), "IH-3": resp([INCOMPLETO])}
    amlr = reg(INDET, {"IH": ih}, segun_lectura=["AM-06"], avisos=["D-9"])
    return Caso(
        "04-propuesta-de-decision-sin-revision-humana",
        "Expediente de 2028 en el que un sistema, que la entidad declara no saber si es un sistema de IA, propone "
        "la decisión de comunicar dos días antes de que se tome, y nadie revisa su salida. Con la Ley y el RD está "
        "completo. Con el AMLR depende de R-2: si la intervención humana del art. 76.5.b no alcanza la decisión de "
        "comunicar (IH-1), completo; si la alcanza (IH-2, IH-3), falta AM-06. La declaración no cambia nada (D-18).",
        registro(
            expediente(
                4,
                FECHAS_2028,
                decisor_persona(1),
                fases=[fase(1), fase(2, [ia(7)])],
                circunstancias=[circunstancia(1), circunstancia(2, fuentes=(), participaciones=[ia(7)])],
                razones=[razon(1)],
            ),
            participaciones=[participacion(7, "C", "propuesta_decision", "2028-03-01")],
            sistemas=[sistema("C", "desconocido")],
        ),
        resultado(1, [reg(COMPLETO), amlr, amlr, amlr, amlr]),
    )


def _caso_05():
    # Decide P-6, responsable del cumplimiento normativo, que no es el representante.
    # Ley/RD: falta RD-11. AMLR: AM-07 cumple con DC-1 y DC-2: completo. T-1 = AMLR.
    # T-2: DC-1 suma y falta RD-11; DC-2 prevalece AM-07 y RD-11 no aplica (D-21). T-3: falta RD-11.
    dc = {"DC-1": resp([INCOMPLETO]), "DC-2": resp([COMPLETO])}
    return Caso(
        "05-decide-el-responsable-del-cumplimiento",
        "Expediente de 2028 en el que decide la persona responsable del cumplimiento normativo, que no es el "
        "representante ante el Servicio Ejecutivo. Con la Ley y el RD falta RD-11; con el AMLR está completo. Las "
        "lecturas de la transición divergen (R-3): T-1 completo, T-3 incompleto y T-2 depende además de quién "
        "decide con el AMLR (R-4).",
        registro(expediente(5, FECHAS_2028, decisor_persona(6))),
        resultado(1, [
            reg(INCOMPLETO, en_todas=["RD-11"]),
            reg(COMPLETO),
            reg(COMPLETO),
            reg(INDET, {"DC": dc}, segun_lectura=["RD-11"]),
            reg(INCOMPLETO, en_todas=["RD-11"]),
        ]),
    )


def _caso_06():
    # Expediente de 2026 (< A). Órgano de control interno: 2 comunicar, 1 no comunicar, 1 abstención.
    # MA-1: 2 > 1, mayoría; MA-2: 2 no supera la mitad de 4, falta RD-13. T-n = ley_rd.
    # AMLR, como comparación (aviso D-23): con DC-2 falta AM-07, porque decide un órgano.
    ma = {"MA-1": resp([COMPLETO]), "MA-2": resp([INCOMPLETO])}
    ley = reg(INDET, {"MA": ma}, segun_lectura=["RD-13"])
    dc = {"DC-1": resp([COMPLETO]), "DC-2": resp([INCOMPLETO])}
    fechas = dict(apertura="2026-04-06", fin="2026-04-20", decision="2026-04-24", comunicacion="2026-04-27", cierre="2026-05-04")
    return Caso(
        "06-abstencion-en-el-organo-de-control-interno",
        "Expediente de 2026 decidido por el órgano de control interno con dos votos a favor de comunicar, uno en "
        "contra y una abstención. Si las abstenciones no cuentan (MA-1) hay mayoría; si cuentan (MA-2), no (R-8). "
        "Antes del 10 de julio de 2027, T-1 a T-3 son la Ley y el RD. El AMLR se calcula como comparación.",
        registro(
            expediente(
                6,
                fechas,
                decisor_organo((2, "comunicar"), (3, "comunicar"), (5, "no_comunicar"), (7, "abstencion")),
            )
        ),
        resultado(1, [ley, reg(INDET, {"DC": dc}, segun_lectura=["AM-07"], avisos=["D-23"]), ley, ley, ley]),
    )


def _caso_07():
    # Abierto el 2027-06-21 y cerrado el 2027-07-23: FT se consulta. Sin circunstancias consideradas.
    # Ley/RD: completo. AMLR: falta AM-02 con todas las lecturas (aviso D-23: abarca A).
    # T-n: FT-1 (apertura) = ley_rd, completo; FT-2 (cierre) incluye AM-02, incompleto.
    ft = {"FT-1": resp([COMPLETO]), "FT-2": resp([INCOMPLETO])}
    t = reg(INDET, {"FT": ft}, segun_lectura=["AM-02"])
    fechas = dict(apertura="2027-06-21", fin="2027-07-14", decision="2027-07-16", comunicacion="2027-07-20", cierre="2027-07-23")
    return Caso(
        "07-abierto-antes-y-cerrado-despues-del-10-de-julio-de-2027",
        "Expediente abierto el 2027-06-21 y cerrado el 2027-07-23, sin circunstancias consideradas. Con la Ley y el "
        "RD está completo; con el AMLR falta AM-02. En la transición depende de qué fecha decide la norma (R-11): "
        "la apertura (FT-1) o el cierre (FT-2).",
        registro(
            expediente(7, fechas, decisor_persona(1), circunstancias=[], razones=[razon()]),
        ),
        resultado(1, [reg(COMPLETO), reg(INCOMPLETO, en_todas=["AM-02"], avisos=["D-23"]), t, t, t]),
    )


def _caso_08():
    # Origen: comunicación interna; se informa al comunicante. IA-5, alerta generada después, solo en
    # `participaciones_incorporadas` (modelo, V-17). AM-04: SC-1 falta; SC-2 cumple (no la cita ninguna
    # fase); SC-3 cumple. IH no se consulta.
    sc = {"SC-1": resp([INCOMPLETO]), "SC-2": resp([COMPLETO]), "SC-3": resp([COMPLETO])}
    amlr = reg(INDET, {"SC": sc}, segun_lectura=["AM-04"], avisos=["D-9"])
    return Caso(
        "08-comunicacion-interna-con-alerta-incorporada",
        "Expediente de 2028 abierto por la comunicación interna de un empleado, al que después se suma una alerta "
        "generada por un sistema sobre la misma operativa. Se informa al comunicante de la decisión. Con la Ley y "
        "el RD está completo. Con el AMLR, la alerta incorporada no figura en ninguna circunstancia: falta AM-04 "
        "solo si toda salida es información considerada (SC-1), porque ninguna fase la usó.",
        registro(
            expediente(
                8, FECHAS_2028, decisor_persona(1), origen="comunicacion_interna", incorporadas=[ia(5)],
                comunicante="2028-03-08",
            ),
            participaciones=[participacion(5, "A", "generacion_alerta", "2028-02-20")],
            sistemas=[sistema("A", "no")],
        ),
        resultado(1, [reg(COMPLETO), amlr, amlr, amlr, amlr]),
    )


CASOS = [_caso_01(), _caso_02(), _caso_03(), _caso_04(), _caso_05(), _caso_06(), _caso_07(), _caso_08()]


# --- Autoverificación y escritura ---------------------------------------------------------------


def comprobar(caso):
    """Calcula el caso y devuelve las diferencias con lo esperado (vacío si coincide)."""
    carga = cargar(json.dumps(caso.entrada, ensure_ascii=False))
    if carga.errores:
        return [f"la entrada no es válida: {[(e.codigo, e.ruta) for e in carga.errores]}"]
    obtenido = resumen(informe(carga))
    diferencias = []
    if obtenido["codigo_salida"] != caso.esperado["codigo_salida"]:
        diferencias.append(
            f"codigo_salida: se esperaba {caso.esperado['codigo_salida']!r} y se obtuvo {obtenido['codigo_salida']!r}"
        )
    for regimen in REGIMENES:
        for parte, esperado in caso.esperado["regimenes"][regimen].items():
            calculado = obtenido["regimenes"][regimen][parte]
            if calculado != esperado:
                diferencias.append(f"{regimen}.{parte}: se esperaba {esperado!r} y se obtuvo {calculado!r}")
    return diferencias


def ficheros(caso):
    esperado = {"caso": caso.nombre, "demuestra": caso.demuestra, "resultado": caso.esperado}
    return {f"{caso.nombre}.json": _json(caso.entrada), f"{caso.nombre}.esperado.json": _json(esperado)}


def readme():
    lineas = [
        "# Corpus",
        "",
        "Registros sintéticos con su resultado esperado. Lo genera `corpus/generar.py`, que comprueba cada caso "
        "con el código de `src/` antes de escribirlo. No se edita a mano.",
        "",
        "```",
        "python corpus/generar.py",
        "```",
        "",
        "Cada caso tiene la entrada (`NN-nombre.json`, según `docs/modelo-datos.md`) y el resultado esperado "
        "(`NN-nombre.esperado.json`): en cada uno de los cinco regímenes, el estado, las decisiones que hay que "
        "tomar para salir de cada `indeterminado` (con los estados de cada respuesta y de qué depende aún), los "
        "requisitos que faltan en todas las lecturas y los que faltan solo en algunas, y los códigos D-n de los "
        "avisos. Los resultados esperados están escritos a mano en `generar.py` a partir de "
        "`docs/especificacion-calculo.md`. El código de salida es el de `registro-examen-especial` (§9.1): 1 si "
        "alguna combinación de lecturas de algún régimen da `incompleto`; 0 si ninguna (D-25).",
        "",
        "Los datos son sintéticos: identificadores con «FICTICIO», motivos genéricos e inventados y salidas de los "
        "sistemas como cadenas opacas (`SALIDA-FICTICIO-n`).",
        "",
        "| Caso | " + " | ".join(REGIMENES) + " | Código |",
        "|---|" + "---|" * len(REGIMENES) + "---|",
    ]
    for caso in CASOS:
        r = caso.esperado
        fila = [caso.nombre, *(r["regimenes"][g]["estado"] for g in REGIMENES), str(r["codigo_salida"])]
        lineas.append("| " + " | ".join(fila) + " |")
    lineas += ["", "## Qué demuestra cada caso", ""]
    for caso in CASOS:
        lineas += [f"**{caso.nombre}.** {caso.demuestra}", ""]
    return "\n".join(lineas).rstrip("\n") + "\n"


def _json(datos):
    return json.dumps(datos, ensure_ascii=False, indent=2) + "\n"


def main():
    fallos = [(caso.nombre, diferencias) for caso in CASOS if (diferencias := comprobar(caso))]
    if fallos:
        for nombre, diferencias in fallos:
            print(f"{nombre}:", *diferencias, sep="\n  ", file=sys.stderr)
        sys.exit(f"{len(fallos)} caso(s) no dan el resultado esperado: no se escribe nada")
    for caso in CASOS:
        for nombre, contenido in ficheros(caso).items():
            (DIRECTORIO / nombre).write_text(contenido, encoding="utf-8", newline="\n")
        print(f"Escrito corpus/{caso.nombre}.json y .esperado.json")
    (DIRECTORIO / "README.md").write_text(readme(), encoding="utf-8", newline="\n")
    print("Escrito corpus/README.md")


if __name__ == "__main__":
    main()
