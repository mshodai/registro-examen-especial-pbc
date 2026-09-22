"""La salida: el estado del registro en los cinco regímenes, dónde difieren, qué
falta y qué hay que decidir para salir de cada `indeterminado`.

`informe` calcula los cinco regímenes sobre una entrada ya cargada. `texto` y
`como_json` lo presentan según el §9 de la especificación:

- el **estado** en cada régimen y la **comparación** entre regímenes (D-26);
- **exige actuar** (D-25): qué régimen y qué combinación de lecturas dan
  `incompleto`, y qué falta en cada una;
- **qué falta**: los requisitos que faltan en todas las lecturas, separados de
  los que faltan solo en algunas (D-5);
- para cada `indeterminado`, la **pregunta** de cada dimensión que lo causa
  (D-7) y qué da cada respuesta (D-8);
- los **datos informativos** (§2) y los **avisos**.

Las decisiones se citan como «D-n»; el resto de comentarios son de formato.
"""

import json
from dataclasses import dataclass

from registro.calculo import (
    AMLR,
    INCOMPLETO,
    INDETERMINADO,
    LEY_RD,
    REGIMENES,
    REQUISITOS,
    TRANSICION,
    Activador,
    Decision,
    Resultado,
    ResultadoRegimen,
    calcular,
)
from registro.modelo import Incidencia, ResultadoCarga

ADVERTENCIA = (
    "Resultado de un cálculo bajo las lecturas que declara la especificación "
    "(docs/especificacion-calculo.md), no una determinación jurídica. Donde la norma no decide, el "
    "cálculo da todas las lecturas y no elige; las decisiones propias se citan como D-n."
)

EXPEDIENTE = "expediente"
ALERTA_DESCARTADA = "alerta_descartada"


@dataclass(frozen=True)
class Informe:
    errores: tuple[Incidencia, ...]
    tipo_registro: str | None = None
    registro_id: str | None = None
    resultado: Resultado | None = None

    @property
    def valida(self) -> bool:
        return not self.errores

    def __getitem__(self, regimen: str) -> ResultadoRegimen:
        return self.resultado.regimenes[regimen]

    @property
    def regimenes(self) -> tuple[ResultadoRegimen, ...]:
        return tuple(self.resultado.regimenes[r] for r in REGIMENES)

    @property
    def estados(self) -> dict[str, str]:
        return {r.regimen: r.estado for r in self.regimenes}

    @property
    def grupos(self) -> dict[str, tuple[str, ...]]:
        """Estado → regímenes que lo dan, en el orden de REGIMENES."""
        grupos: dict[str, list[str]] = {}
        for regimen, estado in self.estados.items():
            grupos.setdefault(estado, []).append(regimen)
        return {estado: tuple(rs) for estado, rs in grupos.items()}

    @property
    def hay_indeterminado(self) -> bool:
        return INDETERMINADO in self.estados.values()

    @property
    def exige_actuar(self) -> bool:
        return self.resultado.exige_actuar

    @property
    def activadores(self) -> tuple[Activador, ...]:
        return self.resultado.activadores


def informe(carga: ResultadoCarga) -> Informe:
    if not carga.valida:
        return Informe(errores=carga.errores)
    entrada = carga.entrada
    if entrada.expediente is not None:
        tipo, id_ = EXPEDIENTE, entrada.expediente.id
    else:
        tipo, id_ = ALERTA_DESCARTADA, entrada.alerta_descartada.id
    return Informe(errores=(), tipo_registro=tipo, registro_id=id_, resultado=calcular(entrada))


# --- JSON -----------------------------------------------------------------------------


def _faltas_dict(r: ResultadoRegimen) -> dict:
    rutas = _rutas_por_requisito(r)
    return {
        "en_todas": [{"id": f, "requisito": REQUISITOS[f], "rutas": rutas[f]} for f in r.faltas_seguras],
        "segun_lectura": [
            {"id": f, "requisito": REQUISITOS[f], "rutas": rutas[f], "combinaciones": [list(c) for c in combinaciones]}
            for f, combinaciones in r.faltas_segun_lectura.items()
        ],
    }


def _decision_dict(d: Decision, datos) -> dict:
    return {
        "dimension": d.dimension,
        "pregunta": d.pregunta,
        "respuestas": [
            {
                "lectura": x.lectura,
                "estados": list(x.estados),
                "faltas": list(x.faltas),
                "resuelve": not x.depende_de,
                "depende_de": list(x.depende_de),
            }
            for x in d.respuestas
        ],
        "datos": list(datos),
    }


def _regimen_dict(r: ResultadoRegimen) -> dict:
    datos = {a.dimension: a.datos for a in r.atribuciones}
    return {
        "estado": r.estado,
        "faltas": _faltas_dict(r),
        "decisiones": [_decision_dict(d, datos[d.dimension]) for d in r.decisiones],
        "lecturas": [
            {
                "lecturas": dict(l.lecturas),
                "estado": l.estado,
                "requisitos": [
                    {"id": q.id, "requisito": REQUISITOS[q.id], "resultado": q.resultado, "rutas": list(q.rutas), "nota": q.nota}
                    for q in l.requisitos
                ],
                "avisos": [{"codigo": a.codigo, "mensaje": a.mensaje} for a in l.avisos],
            }
            for l in r.lecturas
        ],
        "avisos": [{"codigo": a.codigo, "mensaje": a.mensaje} for a in r.avisos],
    }


def _informativos_dict(inf: Informe) -> dict:
    i = inf.resultado.informativos
    return {
        "dias_analisis_a_decision": i.dias_analisis_a_decision,
        "dias_decision_a_comunicacion": i.dias_decision_a_comunicacion,
        "umbral_operaciones": {
            "valor": i.umbral_operaciones.valor,
            "lecturas": [{"lectura": l, "anio": a, "valor": v} for l, a, v in i.umbral_operaciones.lecturas],
        },
        "sistemas": [
            {"sistema": s, "declaracion_sistema_ia": d, "participaciones": list(p)} for s, d, p in i.declaraciones
        ],
    }


def como_dict(inf: Informe) -> dict:
    datos = {
        "advertencia": ADVERTENCIA,
        "valida": inf.valida,
        "errores": [{"codigo": e.codigo, "mensaje": e.mensaje, "ruta": e.ruta} for e in inf.errores],
        "tipo_registro": inf.tipo_registro,
        "registro": inf.registro_id,
        "fecha_aplicacion_amlr": None,
        "exige_actuar": None,
        "comparacion": None,
        "informativos": None,
        "regimenes": {},
    }
    if not inf.valida:
        return datos
    datos["fecha_aplicacion_amlr"] = inf.resultado.fecha_aplicacion_amlr.isoformat()
    # D-25: qué régimen, qué lecturas y qué faltas lo activan.
    datos["exige_actuar"] = {
        "valor": inf.exige_actuar,
        "activado_por": [
            {"regimen": a.regimen, "lecturas": list(a.lecturas), "estado": a.estado, "faltas": list(a.faltas)}
            for a in inf.activadores
        ],
    }
    datos["comparacion"] = {
        "normas_coinciden": inf.resultado.normas_coinciden,
        "transicion_coincide": inf.resultado.transicion_coincide,
        "hay_indeterminado": inf.hay_indeterminado,
        "grupos": [{"estado": e, "regimenes": list(rs)} for e, rs in inf.grupos.items()],
    }
    datos["informativos"] = _informativos_dict(inf)
    datos["regimenes"] = {r.regimen: _regimen_dict(r) for r in inf.regimenes}
    return datos


def como_json(inf: Informe) -> str:
    return json.dumps(como_dict(inf), ensure_ascii=False, indent=2)


# --- Texto ------------------------------------------------------------------------------

ANCHO_REGIMEN = max(len(r) for r in REGIMENES)
# Como D-39 de plazos-actualizacion-pbc: en texto, más combinaciones se resumen; el JSON las da todas.
MAX_COMBINACIONES_TEXTO = 3


def _rutas_por_requisito(r: ResultadoRegimen) -> dict[str, list[str]]:
    """Requisito → rutas que faltan, reunidas de todas las combinaciones, sin repetir."""
    rutas: dict[str, list[str]] = {}
    for l in r.lecturas:
        for q in l.requisitos:
            if q.rutas:
                destino = rutas.setdefault(q.id, [])
                destino += [x for x in q.rutas if x not in destino]
    return {f: rutas.get(f, []) for f in REQUISITOS}


def _combinacion(lecturas) -> str:
    return " y ".join(lecturas) if lecturas else "sin lecturas que decidir"


def _falta_texto(id_, rutas) -> str:
    return f"{id_} {REQUISITOS[id_]}" + (f" ({'; '.join(rutas)})" if rutas else "")


def _agrupar(inf: Informe, clave):
    """[(regímenes, régimen de muestra)] con los regímenes de igual clave juntos, en orden."""
    grupos: dict = {}
    for r in inf.regimenes:
        grupos.setdefault(clave(r), []).append(r)
    return [(tuple(x.regimen for x in rs), rs[0]) for rs in grupos.values()]


def _exige_actuar_texto(inf: Informe) -> list[str]:
    """D-25: qué exige actuar, con los regímenes que coinciden agrupados."""
    if not inf.exige_actuar:
        return ["  No: ninguna lectura de ningún régimen da «incompleto» (D-25)."]

    def clave(r):
        combinaciones = tuple((a.lecturas, a.faltas) for a in r.activadores)
        nota = "" if r.estado == INCOMPLETO else r.estado
        return combinaciones, nota

    lineas = ["  Sí (D-25). Lo exigen:"]
    for regimenes, r in _agrupar(inf, clave):
        if not r.activadores:
            continue
        nota = "" if r.estado == INCOMPLETO else f" (estado del régimen: {r.estado})"
        lineas.append(f"    {', '.join(regimenes)}{nota}:")
        for a in r.activadores[:MAX_COMBINACIONES_TEXTO]:
            lineas.append(f"      {_combinacion(a.lecturas)}: falta {', '.join(a.faltas)}")
        resto = len(r.activadores) - MAX_COMBINACIONES_TEXTO
        if resto > 0:
            lineas.append(f"      y {resto} combinaciones más (todas en --json)")
    return lineas


def _que_falta_texto(inf: Informe) -> list[str]:
    """D-5: lo que falta en todas las lecturas, separado de lo que falta solo en algunas."""

    def clave(r):
        return r.faltas_seguras, tuple(r.faltas_segun_lectura.items()), len(r.lecturas)

    lineas = []
    for regimenes, r in _agrupar(inf, clave):
        rutas = _rutas_por_requisito(r)
        cabecera = f"  {', '.join(regimenes)}:"
        if not r.faltas_seguras and not r.faltas_segun_lectura:
            lineas.append(f"{cabecera} nada.")
            continue
        lineas.append(cabecera)
        if r.faltas_seguras:
            lineas.append("    En todas las lecturas:")
            lineas += [f"      {_falta_texto(f, rutas[f])}" for f in r.faltas_seguras]
        if r.faltas_segun_lectura:
            lineas.append("    Solo en algunas:")
            total = len(r.lecturas)
            for f, combinaciones in r.faltas_segun_lectura.items():
                if len(combinaciones) <= MAX_COMBINACIONES_TEXTO:
                    donde = "con " + "; ".join(_combinacion(c) for c in combinaciones)
                else:
                    donde = f"en {len(combinaciones)} de {total} combinaciones (todas en --json)"
                lineas.append(f"      {_falta_texto(f, rutas[f])}: {donde}")
    return lineas


def _decision_texto(d: Decision, datos) -> list[str]:
    lineas = [f"    {d.dimension} — {d.pregunta}"]
    for x in d.respuestas:
        estados = " o ".join(x.estados)
        faltas = f" (falta {', '.join(x.faltas)})" if x.faltas else ""
        resto = f"; aún depende de {', '.join(x.depende_de)}" if x.depende_de else ""
        lineas.append(f"      {x.lectura}: {estados}{faltas}{resto}")
    if datos:
        lineas.append(f"      Datos: {'; '.join(datos)}")
    return lineas


def _informativos_texto(inf: Informe) -> list[str]:
    i = inf.resultado.informativos
    lineas = []
    if i.dias_analisis_a_decision is not None:
        lineas.append(
            f"  Días entre el fin del análisis técnico y la decisión: {i.dias_analisis_a_decision} "
            "(RD, art. 25.2: «sin demora»)."
        )
    if i.dias_decision_a_comunicacion is not None:
        lineas.append(
            f"  Días entre la decisión y la comunicación: {i.dias_decision_a_comunicacion} "
            "(Ley, art. 18.2: «sin dilación»)."
        )
    u = i.umbral_operaciones
    detalle = "; ".join(f"{l} ({a}): {v}" for l, a, v in u.lecturas)
    lineas.append(f"  Más de 10.000 operaciones anuales (RD, art. 23; D-24): {u.valor} — {detalle}.")
    for sistema, declaracion, participaciones in i.declaraciones:
        lineas.append(
            f"  Sistema {sistema}: la entidad declara «{declaracion}» sobre el art. 3.1 del AI Act; "
            f"participaciones {', '.join(participaciones)}. No cambia ningún requisito (D-18)."
        )
    return lineas


def texto(inf: Informe) -> str:
    lineas: list[str] = []
    if not inf.valida:
        lineas.append(f"La entrada no es válida ({len(inf.errores)} errores):")
        for e in inf.errores:
            lineas.append(f"  {e.codigo}  {e.ruta or '(raíz)'}: {e.mensaje}")
        return "\n".join(lineas) + "\n"

    que = "Expediente" if inf.tipo_registro == EXPEDIENTE else "Alerta descartada"
    a = inf.resultado.fecha_aplicacion_amlr
    lineas += [f"{que} {inf.registro_id}", f"AMLR aplicable desde el {a}", "", ADVERTENCIA, "", "Estado del registro:"]
    for r in inf.regimenes:
        lineas.append(f"  {r.regimen:<{ANCHO_REGIMEN}}  {r.estado}")

    lineas += ["", "Dónde difieren:"]
    if not inf.resultado.normas_coinciden:
        lineas.append(f"  {LEY_RD} y {AMLR} no coinciden: la norma cambia lo que se exige al registro.")
    if not inf.resultado.transicion_coincide:
        lineas.append(
            f"  {', '.join(TRANSICION)} no coinciden: lo que se exige depende de si el art. 25 del RD sigue "
            f"aplicándose desde el {a} (R-3, D-26)."
        )
    if len(inf.grupos) == 1 and inf.resultado.normas_coinciden and inf.resultado.transicion_coincide:
        lineas.append("  Los cinco regímenes coinciden.")
    else:
        lineas.append("  " + "; ".join(f"{', '.join(rs)}: {e}" for e, rs in inf.grupos.items()))
    if inf.hay_indeterminado:
        lineas.append("  «indeterminado»: las lecturas de ese régimen dan estados distintos (D-5).")

    lineas += ["", "Exige actuar:"]
    lineas += _exige_actuar_texto(inf)

    lineas += ["", "Qué falta (D-5):"]
    lineas += _que_falta_texto(inf)

    if inf.hay_indeterminado:
        lineas += ["", "Qué hay que decidir para salir del indeterminado (D-7, D-8):"]
        mostrados: dict = {}
        for r in inf.regimenes:
            if r.estado != INDETERMINADO:
                continue
            clave = r.decisiones
            if clave in mostrados:
                lineas.append(f"  {r.regimen}: lo mismo que {mostrados[clave]}")
                continue
            mostrados[clave] = r.regimen
            lineas.append(f"  {r.regimen}:")
            datos = {x.dimension: x.datos for x in r.atribuciones}
            for d in r.decisiones:
                lineas += _decision_texto(d, datos[d.dimension])

    lineas += ["", "Datos informativos (§2):"]
    lineas += _informativos_texto(inf)

    avisos: dict = {}
    for r in inf.regimenes:
        for aviso in r.avisos:
            avisos.setdefault(aviso, []).append(r.regimen)
    if avisos:
        lineas += ["", "Avisos:"]
        for aviso, regimenes in avisos.items():
            lineas.append(f"  ({', '.join(regimenes)}) {aviso.codigo}: {aviso.mensaje}")

    return "\n".join(lineas) + "\n"
