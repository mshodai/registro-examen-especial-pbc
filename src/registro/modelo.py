"""Estructuras de datos de la entrada, según docs/modelo-datos.md (versión 1).

Describen la entrada ya validada y no contienen ninguna regla de cálculo. No
hay régimen: es un parámetro del cálculo (modelo, §0.1). Todas las fechas son
`date`; el texto AAAA-MM-DD solo existe en el JSON.

Del sistema de IA solo hay lo que el modelo recoge: un identificador opaco, la
declaración de la entidad y, en cada participación, el momento, la fecha, la
salida tal como la dio y la intervención humana (modelo, §0.2, regla 2).

Cada elemento de una lista se identifica por su `id`, salvo las razones, los
votos y las intervenciones humanas, que se identifican por su posición. El
cálculo cita esos identificadores al atribuir un `indeterminado`.
"""

from dataclasses import dataclass
from datetime import date

VERSION_MODELO = 1

# §2.1
ACTIVIDADES = ("agente_de_futbol", "club_de_futbol_profesional", "otra")

# §2.2
REPRESENTANTE = "representante_servicio_ejecutivo"
PERSONA_AUTORIZADA = "persona_autorizada_por_el_representante"
MIEMBRO_ORGANO = "miembro_organo_control_interno"
DIRECTOR_CUMPLIMIENTO = "director_cumplimiento_normativo"
RESPONSABLE_CUMPLIMIENTO = "responsable_cumplimiento_normativo"
OTRO = "otro"
CARGOS = (REPRESENTANTE, PERSONA_AUTORIZADA, MIEMBRO_ORGANO, DIRECTOR_CUMPLIMIENTO, RESPONSABLE_CUMPLIMIENTO, OTRO)

# §4
ALERTA = "alerta"
COMUNICACION_INTERNA = "comunicacion_interna"
DEVOLUCION = "devolucion_servicio_ejecutivo"
IMPOSIBILIDAD_DD = "imposibilidad_diligencia_debida"
TIPOS_ORIGEN = (ALERTA, COMUNICACION_INTERNA, DEVOLUCION, IMPOSIBILIDAD_DD, OTRO)

# §6.1
AMBITOS = ("sujeto_obligado", "grupo", "externa")

# §8.1
PERSONA = "persona"
ORGANO_CONTROL_INTERNO = "organo_control_interno"
OTRO_ORGANO = "otro_organo_colegiado"
TIPOS_DECISOR = (PERSONA, ORGANO_CONTROL_INTERNO, OTRO_ORGANO)

COMUNICAR = "comunicar"
NO_COMUNICAR = "no_comunicar"
ABSTENCION = "abstencion"
SENTIDOS = (COMUNICAR, NO_COMUNICAR, ABSTENCION)

# §9.2
DECLARACIONES = ("si", "no", "desconocido")

# §9.3
GENERACION_ALERTA = "generacion_alerta"
PRIORIZACION_ALERTA = "priorizacion_alerta"
ANALISIS = "analisis"
PROPUESTA_DECISION = "propuesta_decision"
MOMENTOS = (GENERACION_ALERTA, PRIORIZACION_ALERTA, ANALISIS, PROPUESTA_DECISION)
MOMENTOS_DE_ALERTA = (GENERACION_ALERTA, PRIORIZACION_ALERTA)

# Modelo, §13.1 (V-19).
ERRORES = {
    "ERR-01": "JSON mal formado o con claves repetidas, campo obligatorio ausente, valor de tipo no válido, "
    "`version_modelo` distinto de 1, o campo `regimen` u otro desconocido",
    "ERR-02": "`id` repetido en su lista, `anio` repetido, cargo repetido en una persona, persona repetida en "
    "`votos`, o una misma referencia repetida en una lista de referencias",
    "ERR-03": "Una referencia apunta a un `id` que no existe en su lista",
    "ERR-04": "Fechas del expediente en un orden imposible",
    "ERR-05": "Decisor incoherente con su tipo, o `expediente_devuelto` incoherente con el origen",
    "ERR-06": "`comunicar` es false y `comunicacion` no es null",
    "ERR-07": "`conclusion.razones` vacía",
    "ERR-08": "Ni `expediente` ni `alerta_descartada`, o los dos",
    "ERR-09": "Un sistema que no aparece en ninguna participación",
    "ERR-10": "La alerta descartada no tiene una participación de generación de la alerta, o tiene una "
    "propuesta de decisión",
    "ERR-11": "Una participación que no cita ninguna parte del registro",
    "ERR-12": "`origen.participaciones_ia` con un momento que no es de alerta, o sin generación de la alerta "
    "con `origen.tipo` `alerta`",
}


@dataclass(frozen=True)
class OperacionesAnio:
    """§2.1. RD, art. 23."""

    anio: int
    numero: int


@dataclass(frozen=True)
class Sujeto:
    """§2.1."""

    actividad: str
    operaciones_anuales: tuple[OperacionesAnio, ...]


@dataclass(frozen=True)
class Persona:
    """§2.2. Un código, no un nombre."""

    id: str
    cargos: tuple[str, ...]


@dataclass(frozen=True)
class Sistema:
    """§9.2. `id` opaco; `declaracion_sistema_ia` es lo que declara la entidad."""

    id: str
    declaracion_sistema_ia: str


@dataclass(frozen=True)
class IntervencionHumana:
    """§9.4."""

    persona: str
    fecha: date
    descripcion: str


@dataclass(frozen=True)
class Participacion:
    """§9.3. `salida` es una cadena opaca: el cálculo no la interpreta."""

    id: str
    sistema: str
    momento: str
    fecha: date
    salida: str
    intervencion_humana: tuple[IntervencionHumana, ...]


@dataclass(frozen=True)
class Origen:
    """§4."""

    tipo: str
    descripcion: str
    participaciones_ia: tuple[str, ...]
    expediente_devuelto: str | None


@dataclass(frozen=True)
class Operacion:
    """§5."""

    id: str
    descripcion: str
    ejecutada: bool


@dataclass(frozen=True)
class Interviniente:
    """§5."""

    id: str
    papel: str


@dataclass(frozen=True)
class OperativaAnalizada:
    """§5."""

    descripcion: str
    operaciones: tuple[Operacion, ...]
    intervinientes: tuple[Interviniente, ...]


@dataclass(frozen=True)
class Fuente:
    """§6.1."""

    id: str
    descripcion: str
    ambito: str


@dataclass(frozen=True)
class Fase:
    """§6.2."""

    id: str
    descripcion: str
    gestiones: tuple[str, ...]
    fuentes: tuple[str, ...]
    participaciones_ia: tuple[str, ...]


@dataclass(frozen=True)
class Circunstancia:
    """§7.1."""

    id: str
    descripcion: str
    fuentes: tuple[str, ...]
    participaciones_ia: tuple[str, ...]


@dataclass(frozen=True)
class Razon:
    """§7.2."""

    descripcion: str
    circunstancias: tuple[str, ...]


@dataclass(frozen=True)
class Conclusion:
    """§7.2."""

    texto: str
    razones: tuple[Razon, ...]


@dataclass(frozen=True)
class Voto:
    """§8.1."""

    persona: str
    sentido: str
    motivacion: str | None


@dataclass(frozen=True)
class Decisor:
    """§8.1."""

    tipo: str
    persona: str | None
    votos: tuple[Voto, ...] | None


@dataclass(frozen=True)
class Comunicacion:
    """§8.2."""

    fecha: date
    referencia_copia: str | None


@dataclass(frozen=True)
class DecisionComunicacion:
    """§8."""

    comunicar: bool
    fecha: date
    motivacion: str
    decisor: Decisor
    comunicacion: Comunicacion | None
    fecha_puesta_en_conocimiento_comunicante: date | None


@dataclass(frozen=True)
class Expediente:
    """§3 a §8."""

    id: str
    fecha_apertura: date
    fecha_fin_analisis_tecnico: date
    fecha_cierre: date
    origen: Origen
    participaciones_incorporadas: tuple[str, ...]
    operativa_analizada: OperativaAnalizada
    fuentes: tuple[Fuente, ...]
    fases: tuple[Fase, ...]
    circunstancias_consideradas: tuple[Circunstancia, ...]
    conclusion: Conclusion
    decision_comunicacion: DecisionComunicacion


@dataclass(frozen=True)
class RevisionAlerta:
    """§10.2, `revision`."""

    persona: str
    fecha: date


@dataclass(frozen=True)
class AlertaDescartada:
    """§10."""

    id: str
    participaciones_ia: tuple[str, ...]
    descripcion_operativa: str
    revision: RevisionAlerta
    fuentes: tuple[Fuente, ...]
    circunstancias_consideradas: tuple[Circunstancia, ...]
    resultado: str | None


@dataclass(frozen=True)
class Entrada:
    """§2. Uno y solo uno de `expediente` y `alerta_descartada` no es None (modelo, V-13)."""

    version_modelo: int
    sujeto: Sujeto
    personas: tuple[Persona, ...]
    sistemas: tuple[Sistema, ...]
    participaciones_ia: tuple[Participacion, ...]
    expediente: Expediente | None
    alerta_descartada: AlertaDescartada | None

    def persona(self, id_: str) -> Persona:
        return next(p for p in self.personas if p.id == id_)

    def participacion(self, id_: str) -> Participacion:
        return next(p for p in self.participaciones_ia if p.id == id_)


@dataclass(frozen=True)
class Incidencia:
    """Error de validación del §13. `ruta` señala el dato en el JSON, p. ej.
    `expediente.fases[1].fuentes[0]`."""

    codigo: str
    mensaje: str
    ruta: str = ""


@dataclass(frozen=True)
class ResultadoCarga:
    """La entrada validada, o None si hay algún error."""

    entrada: Entrada | None
    errores: tuple[Incidencia, ...]

    @property
    def valida(self) -> bool:
        return not self.errores
