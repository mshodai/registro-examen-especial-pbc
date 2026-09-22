"""Cálculo según docs/especificacion-calculo.md: para cada régimen, si el registro está completo y qué le falta.

El régimen es un parámetro (especificación, D-1): `calcular` devuelve siempre
los cinco. Donde la norma no decide, se exploran las lecturas y se devuelven
todas; el cálculo no elige (D-6). Una dimensión solo se consulta si el
registro la pone en juego: la evaluación pide la lectura cuando la necesita, y
cada petición sin respuesta abre una rama por lectura.

Del sistema de IA solo se usa lo que recoge el modelo: qué participación hubo,
en qué momento, cuándo, qué la cita y qué intervención humana tuvo. La salida
no se interpreta nunca (modelo, §0.2, regla 2).

Las decisiones de la especificación se citan como «D-n»; los casos no
resueltos, como «R-n».
"""

from dataclasses import dataclass, field
from datetime import date
from itertools import product

from registro.modelo import (
    COMUNICACION_INTERNA,
    COMUNICAR,
    MIEMBRO_ORGANO,
    NO_COMUNICAR,
    ORGANO_CONTROL_INTERNO,
    PERSONA,
    PERSONA_AUTORIZADA,
    PROPUESTA_DECISION,
    REPRESENTANTE,
    RESPONSABLE_CUMPLIMIENTO,
    ABSTENCION,
    AlertaDescartada,
    Entrada,
    Expediente,
)

# --- Regímenes (§1.1) -----------------------------------------------------------

LEY_RD = "ley_rd"
AMLR = "amlr"
T1, T2, T3 = "T-1", "T-2", "T-3"
TRANSICION = (T1, T2, T3)
REGIMENES = (LEY_RD, AMLR, *TRANSICION)

A_GENERAL = date(2027, 7, 10)
A_FUTBOL = date(2029, 7, 10)

# --- Estados y resultados (§1.2, §1.3) ------------------------------------------------

COMPLETO = "completo"
INCOMPLETO = "incompleto"
NO_EXIGIBLE = "no_exigible"
INDETERMINADO = "indeterminado"

CUMPLE = "cumple"
FALTA = "falta"
NO_APLICA = "no_aplica"

GARANTIZADO = "garantizado por la validación"  # D-10

# --- Requisitos (§3.1, §4.1) -----------------------------------------------------------

REQUISITOS = {
    "RD-01": "Fechas de apertura y cierre",
    "RD-02": "Motivo del examen",
    "RD-03": "Descripción de la operativa",
    "RD-04": "Fases de análisis",
    "RD-05": "Gestiones realizadas",
    "RD-06": "Fuentes consultadas",
    "RD-07": "Conclusión",
    "RD-08": "Razones",
    "RD-09": "Decisión y su fecha",
    "RD-10": "Motivación de la decisión",
    "RD-11": "Decisor previsto",
    "RD-12": "Voto de cada miembro",
    "RD-13": "Mayoría",
    "RD-14": "Fecha de la comunicación",
    "RD-15": "Informar al comunicante",
    "AM-01": "Información considerada",
    "AM-02": "Circunstancias consideradas",
    "AM-03": "Resultados",
    "AM-04": "Salida del sistema entre las circunstancias",
    "AM-05": "Copia de la comunicación",
    "AM-06": "Intervención humana antes de la decisión",
    "AM-07": "Quién decide",
}
REQUISITOS_DECISOR_RD = ("RD-11", "RD-12", "RD-13")  # D-21

# --- Dimensiones de lectura (§1.4) ----------------------------------------------------


@dataclass(frozen=True)
class Dimension:
    id: str
    lecturas: tuple[str, ...]
    caso: str
    seccion: str
    pregunta: str


DIMENSIONES = {
    d.id: d
    for d in (
        Dimension("PA", ("PA-1", "PA-2"), "R-10", "§3.1",
                  "¿Puede adoptar la decisión una persona autorizada por el representante?"),
        Dimension("MA", ("MA-1", "MA-2"), "R-8", "§3.1",
                  "¿Cuentan las abstenciones para la mayoría del órgano de control interno?"),
        Dimension("SC", ("SC-1", "SC-2", "SC-3"), "R-1", "§4.3",
                  "¿La salida de un sistema es una circunstancia considerada aunque la entidad no la enlace?"),
        Dimension("IH", ("IH-1", "IH-2", "IH-3"), "R-2", "§4.4",
                  "¿Alcanza la intervención humana del art. 76.5.b a la decisión de comunicar?"),
        Dimension("DC", ("DC-1", "DC-2"), "R-4", "§4.2", "¿Quién decide la comunicación con el AMLR?"),
        Dimension("AD", ("AD-1", "AD-2"), "R-6", "§4.5",
                  "¿La revisión de una alerta descartada es una evaluación del art. 69.2 del AMLR?"),
        Dimension("FT", ("FT-1", "FT-2"), "R-11", "§5.3",
                  "¿Qué fecha decide la norma de un expediente abierto antes de la fecha de aplicación y cerrado después?"),
    )
}

# D-24: la dimensión del dato informativo del RD, art. 23. No cambia el estado.
DIMENSION_OA = Dimension("OA", ("OA-1", "OA-2"), "R-7", "§2.2", "¿Qué año cuenta para el umbral de 10.000 operaciones?")
UMBRAL_OPERACIONES = 10_000
SUPERA = "supera"
NO_SUPERA = "no_supera"
SIN_DATO = "sin_dato"


# --- Estructuras del resultado --------------------------------------------------------


@dataclass(frozen=True)
class Aviso:
    codigo: str
    mensaje: str


@dataclass(frozen=True)
class ResultadoRequisito:
    id: str
    resultado: str
    rutas: tuple[str, ...] = ()  # con `falta`, los datos que faltan o lo incumplen
    nota: str = ""


@dataclass(frozen=True)
class Lectura:
    """Una hoja: las lecturas consultadas y su resultado."""

    lecturas: tuple[tuple[str, str], ...]
    estado: str
    requisitos: tuple[ResultadoRequisito, ...]
    avisos: tuple[Aviso, ...]

    @property
    def faltas(self) -> tuple[str, ...]:
        return tuple(r.id for r in self.requisitos if r.resultado == FALTA)

    @property
    def ids(self) -> tuple[str, ...]:
        return tuple(valor for _, valor in self.lecturas)


@dataclass(frozen=True)
class Atribucion:
    """D-7: una dimensión que causa el `indeterminado`."""

    dimension: str
    lecturas: tuple[tuple[str, tuple[str, ...]], ...]  # lectura → estados que da
    datos: tuple[str, ...]  # datos de la entrada que la ponen en juego


@dataclass(frozen=True)
class Respuesta:
    """D-8: qué pasa si se responde con esta lectura."""

    lectura: str
    estados: tuple[str, ...]
    faltas: tuple[str, ...]
    depende_de: tuple[str, ...]


@dataclass(frozen=True)
class Decision:
    dimension: str
    pregunta: str
    respuestas: tuple[Respuesta, ...]


@dataclass(frozen=True)
class Activador:
    """D-25: una combinación que exige actuar (da `incompleto`), con sus faltas."""

    regimen: str
    lecturas: tuple[str, ...]
    faltas: tuple[str, ...]
    estado: str = INCOMPLETO


@dataclass(frozen=True)
class ResultadoRegimen:
    regimen: str
    estado: str
    lecturas: tuple[Lectura, ...]
    atribuciones: tuple[Atribucion, ...]
    decisiones: tuple[Decision, ...]
    avisos: tuple[Aviso, ...]

    @property
    def faltas_seguras(self) -> tuple[str, ...]:
        """D-5: lo que falta en todas las combinaciones."""
        conjuntos = [set(l.faltas) for l in self.lecturas]
        comunes = set.intersection(*conjuntos) if conjuntos else set()
        return tuple(r for r in REQUISITOS if r in comunes)

    @property
    def faltas_segun_lectura(self) -> dict[str, tuple[tuple[str, ...], ...]]:
        """D-5: lo que falta solo en algunas combinaciones, con las lecturas en que falta."""
        seguras = set(self.faltas_seguras)
        resultado: dict[str, list[tuple[str, ...]]] = {}
        for l in self.lecturas:
            for f in l.faltas:
                if f not in seguras:
                    resultado.setdefault(f, []).append(l.ids)
        return {r: tuple(resultado[r]) for r in REQUISITOS if r in resultado}

    @property
    def activadores(self) -> tuple[Activador, ...]:
        return tuple(Activador(self.regimen, l.ids, l.faltas) for l in self.lecturas if l.estado == INCOMPLETO)

    @property
    def firma(self):
        """D-26: dos regímenes coinciden si dan el mismo estado y las mismas faltas."""
        return self.estado, frozenset((l.estado, l.faltas) for l in self.lecturas)


@dataclass(frozen=True)
class Indicador:
    """D-24: umbral de operaciones del RD, art. 23."""

    valor: str  # supera, no_supera, sin_dato o indeterminado
    lecturas: tuple[tuple[str, int, str], ...]  # (OA-n, año, valor)


@dataclass(frozen=True)
class Informativos:
    """§2: no cambian el estado."""

    dias_analisis_a_decision: int | None
    dias_decision_a_comunicacion: int | None
    umbral_operaciones: Indicador
    declaraciones: tuple[tuple[str, str, tuple[str, ...]], ...]  # (sistema, declaración, participaciones)


@dataclass(frozen=True)
class Resultado:
    fecha_aplicacion_amlr: date
    regimenes: dict[str, ResultadoRegimen]
    informativos: Informativos

    @property
    def normas_coinciden(self) -> bool:
        return self.regimenes[LEY_RD].firma == self.regimenes[AMLR].firma

    @property
    def transicion_coincide(self) -> bool:
        return len({self.regimenes[t].firma for t in TRANSICION}) == 1

    @property
    def activadores(self) -> tuple[Activador, ...]:
        return tuple(a for r in REGIMENES for a in self.regimenes[r].activadores)

    @property
    def exige_actuar(self) -> bool:
        """D-25: alguna combinación de algún régimen da `incompleto`."""
        return bool(self.activadores)


# --- Exploración de lecturas ----------------------------------------------------------


class _Pregunta(Exception):
    def __init__(self, dimension):
        self.dimension = dimension


class _Lecturas:
    """Las lecturas fijadas en una rama. Pedir una no fijada abre una rama por lectura (D-6)."""

    def __init__(self, fijadas, datos):
        self.fijadas = fijadas
        self.consultadas: list[str] = []
        self.datos = datos  # dimensión → datos de la entrada que la ponen en juego

    def __call__(self, dimension, datos=()):
        self.datos.setdefault(dimension, [])
        for d in datos:
            if d not in self.datos[dimension]:
                self.datos[dimension].append(d)
        if dimension not in self.fijadas:
            raise _Pregunta(dimension)
        if dimension not in self.consultadas:
            self.consultadas.append(dimension)
        return self.fijadas[dimension]


def _explorar(evaluar, dimensiones):
    """Hojas de la evaluación: (lecturas consultadas, valor). `evaluar(lect)` devuelve el valor."""
    hojas = []
    datos: dict[str, list[str]] = {}
    pendientes = [{}]
    while pendientes:
        fijadas = pendientes.pop()
        lect = _Lecturas(fijadas, datos)
        try:
            valor = evaluar(lect)
        except _Pregunta as p:
            for lectura in reversed(dimensiones[p.dimension].lecturas):
                pendientes.append({**fijadas, p.dimension: lectura})
            continue
        orden = list(dimensiones)
        consultadas = tuple(sorted(((d, fijadas[d]) for d in lect.consultadas), key=lambda x: orden.index(x[0])))
        hojas.append((consultadas, valor))
    hojas.sort(key=lambda h: [_orden(dimensiones, d, v) for d, v in h[0]])
    return hojas, datos


def _orden(dimensiones, dimension, lectura):
    return (list(dimensiones).index(dimension), dimensiones[dimension].lecturas.index(lectura))


def _estado_en(hojas, punto):
    """El estado de la hoja compatible con el punto de la rejilla."""
    for lecturas, estado in hojas:
        if all(punto.get(d) == v for d, v in lecturas):
            return estado
    raise AssertionError("rejilla sin hoja compatible")


def atribuir(hojas, dimensiones):
    """D-7: dimensiones que cambian el estado en alguna combinación de las demás.

    `hojas` son pares (lecturas, estado). Se recorre la rejilla completa de las
    dimensiones consultadas: el estado de cada punto es el de la hoja compatible.
    """
    orden = list(dimensiones)
    presentes = sorted({d for lecturas, _ in hojas for d, _ in lecturas}, key=orden.index)
    rejilla = [dict(zip(presentes, valores)) for valores in product(*(dimensiones[d].lecturas for d in presentes))]
    causantes = []
    for d in presentes:
        for punto in rejilla:
            base = _estado_en(hojas, punto)
            if any(_estado_en(hojas, {**punto, d: r}) != base for r in dimensiones[d].lecturas):
                causantes.append(d)
                break
    return causantes


# --- Utilidades -----------------------------------------------------------------------


def _vacio(texto):
    """D-3: una cadena vacía o de espacios cuenta como ausente."""
    return texto is None or not texto.strip()


def fecha_aplicacion(entrada: Entrada) -> date:
    """D-2."""
    return A_FUTBOL if entrada.sujeto.actividad in ("agente_de_futbol", "club_de_futbol_profesional") else A_GENERAL


def _cumple(id_, nota=""):
    return ResultadoRequisito(id_, CUMPLE, (), nota)


def _falta(id_, *rutas):
    return ResultadoRequisito(id_, FALTA, tuple(rutas))


def _no_aplica(id_):
    return ResultadoRequisito(id_, NO_APLICA)


def _segun(id_, rutas):
    return _falta(id_, *rutas) if rutas else _cumple(id_)


# --- Evaluación de un registro ----------------------------------------------------------


@dataclass
class _Evaluacion:
    """Una evaluación con unas lecturas fijadas: requisitos y avisos."""

    requisitos: dict[str, ResultadoRequisito] = field(default_factory=dict)
    avisos: list[Aviso] = field(default_factory=list)
    no_exigible: bool = False

    def poner(self, r: ResultadoRequisito):
        self.requisitos[r.id] = r

    def avisar(self, codigo, mensaje):
        aviso = Aviso(codigo, mensaje)
        if aviso not in self.avisos:
            self.avisos.append(aviso)

    def estado(self):
        if self.no_exigible:
            return NO_EXIGIBLE
        return INCOMPLETO if any(r.resultado == FALTA for r in self.requisitos.values()) else COMPLETO


class _Registro:
    """Los requisitos de cada régimen sobre una entrada."""

    def __init__(self, entrada: Entrada):
        self.e = entrada
        self.a = fecha_aplicacion(entrada)

    # --- Ley 10/2010 y RD 304/2014 (§3) ---------------------------------------------------

    def ley_rd(self, ev: _Evaluacion, lect, prevalece_amlr_decisor=False):
        if self.e.alerta_descartada is not None:
            # D-20: el RD, art. 23, solo exige revisar la alerta, y la revisión consta siempre.
            ev.no_exigible = True
            return
        x = self.e.expediente
        r = "expediente"
        ev.poner(_cumple("RD-01", GARANTIZADO))
        ev.poner(_segun("RD-02", [f"{r}.origen.descripcion"] if _vacio(x.origen.descripcion) else []))
        ev.poner(_segun("RD-03", [f"{r}.operativa_analizada.descripcion"] if _vacio(x.operativa_analizada.descripcion) else []))
        if not x.fases:
            ev.poner(_falta("RD-04", f"{r}.fases"))
        else:
            ev.poner(_segun("RD-04", [f"{r}.fases[{i}].descripcion" for i, f in enumerate(x.fases) if _vacio(f.descripcion)]))
        gestiones = any(not _vacio(g) for f in x.fases for g in f.gestiones)
        ev.poner(_cumple("RD-05") if gestiones else _falta("RD-05", f"{r}.fases[].gestiones"))
        if not x.fuentes:
            ev.poner(_falta("RD-06", f"{r}.fuentes"))
        else:
            ev.poner(_segun("RD-06", [f"{r}.fuentes[{i}].descripcion" for i, f in enumerate(x.fuentes) if _vacio(f.descripcion)]))
        ev.poner(_segun("RD-07", [f"{r}.conclusion.texto"] if _vacio(x.conclusion.texto) else []))
        ev.poner(_segun("RD-08", [f"{r}.conclusion.razones[{i}].descripcion"
                                  for i, z in enumerate(x.conclusion.razones) if _vacio(z.descripcion)]))
        ev.poner(_cumple("RD-09", GARANTIZADO))
        d = x.decision_comunicacion
        ev.poner(_segun("RD-10", [f"{r}.decision_comunicacion.motivacion"] if _vacio(d.motivacion) else []))
        if prevalece_amlr_decisor:
            # D-21: en T-2 con DC-2, rige AM-07.
            for id_ in REQUISITOS_DECISOR_RD:
                ev.poner(_no_aplica(id_))
        else:
            self._decisor_rd(x, ev, lect)
        if not d.comunicar:
            ev.poner(_no_aplica("RD-14"))
        else:
            ev.poner(_cumple("RD-14", GARANTIZADO if d.comunicacion else ""))
            if d.comunicacion is None:
                ev.avisar("D-11", "Comunicación decidida y no realizada: posible incumplimiento del «sin dilación» "
                                  "de la Ley, art. 18.2, no un defecto del registro.")
        if x.origen.tipo != COMUNICACION_INTERNA:
            ev.poner(_no_aplica("RD-15"))
        else:
            ev.poner(_segun("RD-15", [f"{r}.decision_comunicacion.fecha_puesta_en_conocimiento_comunicante"]
                            if d.fecha_puesta_en_conocimiento_comunicante is None else []))

    def _decisor_rd(self, x: Expediente, ev: _Evaluacion, lect):
        """RD-11 a RD-13 (D-12, D-13, D-14)."""
        d = x.decision_comunicacion
        decisor = d.decisor
        ruta = "expediente.decision_comunicacion.decisor"
        if decisor.tipo == PERSONA:
            cargos = self.e.persona(decisor.persona).cargos
            if REPRESENTANTE in cargos:
                ev.poner(_cumple("RD-11"))
            elif PERSONA_AUTORIZADA in cargos:
                pa = lect("PA", (f"{ruta}.persona ({decisor.persona})",))
                ev.poner(_cumple("RD-11") if pa == "PA-1" else _falta("RD-11", f"{ruta}.persona"))
            else:
                ev.poner(_falta("RD-11", f"{ruta}.persona"))
            ev.poner(_no_aplica("RD-12"))
            ev.poner(_no_aplica("RD-13"))
            return
        if decisor.tipo != ORGANO_CONTROL_INTERNO:
            ev.poner(_falta("RD-11", f"{ruta}.tipo"))
            ev.poner(_no_aplica("RD-12"))
            ev.poner(_no_aplica("RD-13"))
            return
        ev.poner(_cumple("RD-11"))
        if not decisor.votos:
            ev.poner(_falta("RD-12", f"{ruta}.votos"))
            ev.poner(_no_aplica("RD-13"))
            return
        ev.poner(_segun("RD-12", [f"{ruta}.votos[{i}].motivacion" for i, v in enumerate(decisor.votos) if _vacio(v.motivacion)]))
        for v in decisor.votos:
            if MIEMBRO_ORGANO not in self.e.persona(v.persona).cargos:
                ev.avisar("D-14", f"La persona «{v.persona}» vota sin constar como miembro del órgano de control interno.")
        sentido = COMUNICAR if d.comunicar else NO_COMUNICAR
        contrario = NO_COMUNICAR if d.comunicar else COMUNICAR
        votos = [v.sentido for v in decisor.votos]
        a_favor, en_contra, abstenciones = votos.count(sentido), votos.count(contrario), votos.count(ABSTENCION)
        if abstenciones:
            datos = tuple(f"{ruta}.votos[{i}] ({v.persona})" for i, v in enumerate(decisor.votos) if v.sentido == ABSTENCION)
            ma = lect("MA", datos)
        else:
            ma = "MA-1"  # sin abstenciones las dos lecturas coinciden y MA no se consulta
        if ma == "MA-1":
            mayoria = a_favor > en_contra
        else:
            mayoria = 2 * a_favor > a_favor + en_contra + abstenciones
        ev.poner(_cumple("RD-13") if mayoria else _falta("RD-13", f"{ruta}.votos"))

    # --- AMLR (§4) -----------------------------------------------------------------------

    def amlr(self, ev: _Evaluacion, lect):
        """Los requisitos del AMLR. En un expediente, DC se consulta siempre (AM-07)."""
        alerta = self.e.alerta_descartada
        if alerta is not None:
            ad = lect("AD", (f"alerta_descartada ({alerta.id})",))
            if ad == "AD-1":
                ev.no_exigible = True
                return
            self._comunes_amlr(ev, lect, alerta, "alerta_descartada")
            return
        x = self.e.expediente
        self._comunes_amlr(ev, lect, x, "expediente")
        d = x.decision_comunicacion
        if d.comunicacion is None:
            ev.poner(_no_aplica("AM-05"))
            if d.comunicar:
                ev.avisar("D-11", "Comunicación decidida y no realizada: posible incumplimiento del «sin demora» "
                                  "del AMLR, art. 69.1, no un defecto del registro.")
        else:
            ev.poner(_segun("AM-05", ["expediente.decision_comunicacion.comunicacion.referencia_copia"]
                            if _vacio(d.comunicacion.referencia_copia) else []))
        self._intervencion(x, ev, lect)
        self._quien_decide(x, ev, lect)

    def _comunes_amlr(self, ev: _Evaluacion, lect, objeto, ruta):
        """AM-01 a AM-04, en un expediente o en una alerta con AD-2."""
        circunstancias = objeto.circunstancias_consideradas
        citan_salida = any(c.participaciones_ia for c in circunstancias)
        # D-15.
        ev.poner(_cumple("AM-01") if objeto.fuentes or citan_salida else _falta("AM-01", f"{ruta}.fuentes"))
        if not circunstancias:
            ev.poner(_falta("AM-02", f"{ruta}.circunstancias_consideradas"))
        else:
            ev.poner(_segun("AM-02", [f"{ruta}.circunstancias_consideradas[{i}].descripcion"
                                      for i, c in enumerate(circunstancias) if _vacio(c.descripcion)]))
        if isinstance(objeto, AlertaDescartada):
            ev.poner(_segun("AM-03", [f"{ruta}.resultado"] if _vacio(objeto.resultado) else []))
        else:
            ev.poner(_segun("AM-03", [f"{ruta}.conclusion.texto"] if _vacio(objeto.conclusion.texto) else []))
        self._salida_como_circunstancia(ev, lect, objeto)
        if self.e.participaciones_ia:
            ev.avisar("D-9", "La condición del AMLR, art. 76.5.a (datos limitados al capítulo III), no se comprueba: "
                             "el modelo no recoge las variables del sistema.")

    def _salida_como_circunstancia(self, ev: _Evaluacion, lect, objeto):
        """AM-04 (D-16, R-1)."""
        participaciones = self.e.participaciones_ia
        if not participaciones:
            ev.poner(_no_aplica("AM-04"))
            return
        sc = lect("SC", tuple(f"participaciones_ia[{i}] ({p.id})" for i, p in enumerate(participaciones)))
        citadas = {p for c in objeto.circunstancias_consideradas for p in c.participaciones_ia}
        if sc == "SC-1":
            exigidas = [p.id for p in participaciones]
        elif sc == "SC-2" and isinstance(objeto, Expediente):
            exigidas = [p for f in objeto.fases for p in f.participaciones_ia]
        else:
            exigidas = []
        indices = {p.id: i for i, p in enumerate(participaciones)}
        faltan = [f"participaciones_ia[{indices[p]}] ({p})" for p in dict.fromkeys(exigidas) if p not in citadas]
        ev.poner(_segun("AM-04", faltan))

    def _intervencion(self, x: Expediente, ev: _Evaluacion, lect):
        """AM-06 (D-17, R-2)."""
        d = x.decision_comunicacion
        propuestas = [p.id for p in self.e.participaciones_ia if p.momento == PROPUESTA_DECISION]
        por_razones = {c.id: c.participaciones_ia for c in x.circunstancias_consideradas}
        en_razones = [p for z in x.conclusion.razones for c in z.circunstancias for p in por_razones.get(c, ())]
        conjunto_2 = list(dict.fromkeys(propuestas))
        conjunto_3 = list(dict.fromkeys(propuestas + en_razones))
        posteriores = [
            p.id for p in self.e.participaciones_ia if any(i.fecha > d.fecha for i in p.intervencion_humana)
        ]
        if posteriores:
            ev.avisar("D-17", "Intervención humana posterior a la decisión en " + ", ".join(posteriores)
                              + ": no cuenta, porque la decisión no estuvo «sujeta» a ella.")
        if not conjunto_3:
            ev.poner(_no_aplica("AM-06"))
            return
        indices = {p.id: i for i, p in enumerate(self.e.participaciones_ia)}
        ih = lect("IH", tuple(f"participaciones_ia[{indices[p]}] ({p})" for p in conjunto_3))
        exigidas = {"IH-1": [], "IH-2": conjunto_2, "IH-3": conjunto_3}[ih]
        faltan = [
            f"participaciones_ia[{indices[p]}].intervencion_humana ({p})"
            for p in exigidas
            if not any(i.fecha <= d.fecha for i in self.e.participacion(p).intervencion_humana)
        ]
        ev.poner(_segun("AM-06", faltan))
        if exigidas and not faltan:
            ev.avisar("D-9", "No se ha valorado si la intervención humana fue «significativa» (AMLR, art. 76.5.b).")

    def _quien_decide(self, x: Expediente, ev: _Evaluacion, lect):
        """AM-07 (D-19, R-4)."""
        decisor = x.decision_comunicacion.decisor
        ruta = "expediente.decision_comunicacion.decisor"
        dc = lect("DC", (ruta,))
        if dc == "DC-1":
            ev.poner(_cumple("AM-07"))
        elif decisor.tipo == PERSONA and RESPONSABLE_CUMPLIMIENTO in self.e.persona(decisor.persona).cargos:
            ev.poner(_cumple("AM-07"))
        else:
            ev.poner(_falta("AM-07", f"{ruta}.persona" if decisor.tipo == PERSONA else f"{ruta}.tipo"))

    # --- Fecha del registro y transición (§5) ------------------------------------------

    def posterior_a_a(self, lect) -> bool:
        """Si la fecha del registro es igual o posterior a A (D-2, D-22)."""
        alerta = self.e.alerta_descartada
        if alerta is not None:
            return alerta.revision.fecha >= self.a
        x = self.e.expediente
        if x.fecha_apertura >= self.a:
            return True
        if x.fecha_cierre < self.a:
            return False
        ft = lect("FT", ("expediente.fecha_apertura", "expediente.fecha_cierre"))
        return ft == "FT-2"

    def aviso_fecha(self, ev: _Evaluacion):
        """D-23, solo en `amlr`."""
        alerta = self.e.alerta_descartada
        if alerta is not None:
            antes, abarca = alerta.revision.fecha < self.a, False
        else:
            x = self.e.expediente
            antes = x.fecha_cierre < self.a
            abarca = x.fecha_apertura < self.a <= x.fecha_cierre
        if antes:
            ev.avisar("D-23", f"El AMLR no era aplicable en la fecha del registro (aplicable desde el {self.a}).")
        elif abarca:
            ev.avisar("D-23", f"El expediente abarca la fecha de aplicación del AMLR, el {self.a} (R-11).")

    def evaluar(self, regimen, lect) -> _Evaluacion:
        ev = _Evaluacion()
        if regimen == LEY_RD:
            self.ley_rd(ev, lect)
        elif regimen == AMLR:
            self.aviso_fecha(ev)
            self.amlr(ev, lect)
        elif not self.posterior_a_a(lect):
            self.ley_rd(ev, lect)
        elif regimen == T1:
            self.amlr(ev, lect)
        else:
            # D-21: T-2 y T-3 suman los requisitos. Solo se contradicen en el decisor con DC-2.
            self.amlr(ev, lect)
            if ev.no_exigible or self.e.alerta_descartada is not None:
                # Alerta: `ley_rd` no exige nada, así que la suma es lo que exija el AMLR (§5.2).
                return ev
            prevalece = regimen == T2 and lect("DC") == "DC-2"
            self.ley_rd(ev, lect, prevalece_amlr_decisor=prevalece)
        return ev


# --- Cálculo ------------------------------------------------------------------------------


def calcular_regimen(entrada: Entrada, regimen: str) -> ResultadoRegimen:
    registro = _Registro(entrada)

    def evaluar(lect):
        ev = registro.evaluar(regimen, lect)
        orden = [r for r in REQUISITOS if r in ev.requisitos]
        return ev.estado(), tuple(ev.requisitos[r] for r in orden), tuple(ev.avisos)

    hojas, datos = _explorar(evaluar, DIMENSIONES)
    lecturas = tuple(Lectura(l, estado, requisitos, avisos) for l, (estado, requisitos, avisos) in hojas)
    estados = {l.estado for l in lecturas}
    estado = estados.pop() if len(estados) == 1 else INDETERMINADO  # D-5
    avisos = tuple(dict.fromkeys(a for l in lecturas for a in l.avisos))
    if estado != INDETERMINADO:
        return ResultadoRegimen(regimen, estado, lecturas, (), (), avisos)
    pares = [(l.lecturas, l.estado) for l in lecturas]
    causantes = atribuir(pares, DIMENSIONES)
    atribuciones = tuple(
        Atribucion(
            d,
            tuple(
                (r, tuple(sorted({l.estado for l in lecturas if dict(l.lecturas).get(d, r) == r})))
                for r in DIMENSIONES[d].lecturas
            ),
            tuple(datos.get(d, ())),
        )
        for d in causantes
    )
    decisiones = tuple(_decision(d, lecturas) for d in causantes)
    return ResultadoRegimen(regimen, estado, lecturas, atribuciones, decisiones, avisos)


def _decision(dimension, lecturas) -> Decision:
    """D-8: para cada lectura de la dimensión, estados, faltas y de qué depende aún."""
    dim = DIMENSIONES[dimension]
    respuestas = []
    for r in dim.lecturas:
        compatibles = [l for l in lecturas if dict(l.lecturas).get(dimension, r) == r]
        estados = tuple(sorted({l.estado for l in compatibles}))
        faltas = tuple(f for f in REQUISITOS if any(f in l.faltas for l in compatibles))
        proyectadas = [(tuple((d, v) for d, v in l.lecturas if d != dimension), l.estado) for l in compatibles]
        depende = tuple(atribuir(proyectadas, DIMENSIONES)) if len(estados) > 1 else ()
        respuestas.append(Respuesta(r, estados, faltas, depende))
    return Decision(dimension, f"{dim.pregunta} ({dim.caso}, {dim.seccion})", tuple(respuestas))


def _indicador(entrada: Entrada) -> Indicador:
    """D-24: umbral de operaciones del RD, art. 23, con OA-1 y OA-2 (R-7)."""
    if entrada.alerta_descartada is not None:
        anio = entrada.alerta_descartada.revision.fecha.year
    else:
        anio = entrada.expediente.fecha_apertura.year
    numeros = {o.anio: o.numero for o in entrada.sujeto.operaciones_anuales}
    lecturas = []
    for oa, a in (("OA-1", anio - 1), ("OA-2", anio)):
        n = numeros.get(a)
        valor = SIN_DATO if n is None else SUPERA if n > UMBRAL_OPERACIONES else NO_SUPERA
        lecturas.append((oa, a, valor))
    valores = {v for _, _, v in lecturas}
    return Indicador(valores.pop() if len(valores) == 1 else INDETERMINADO, tuple(lecturas))


def _informativos(entrada: Entrada) -> Informativos:
    x = entrada.expediente
    dias_1 = dias_2 = None
    if x is not None:
        d = x.decision_comunicacion
        dias_1 = (d.fecha - x.fecha_fin_analisis_tecnico).days
        if d.comunicacion is not None:
            dias_2 = (d.comunicacion.fecha - d.fecha).days
    # D-18: la declaración se informa, pero no cambia ningún requisito.
    declaraciones = tuple(
        (s.id, s.declaracion_sistema_ia, tuple(p.id for p in entrada.participaciones_ia if p.sistema == s.id))
        for s in entrada.sistemas
    )
    return Informativos(dias_1, dias_2, _indicador(entrada), declaraciones)


def calcular(entrada: Entrada) -> Resultado:
    """Los cinco regímenes sobre la misma entrada (D-1)."""
    return Resultado(
        fecha_aplicacion(entrada),
        {r: calcular_regimen(entrada, r) for r in REGIMENES},
        _informativos(entrada),
    )
