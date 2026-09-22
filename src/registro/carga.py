"""Lectura y validación de la entrada, según docs/modelo-datos.md (versión 1).

`cargar` lee el JSON y devuelve un ResultadoCarga con la entrada validada (o
None si hay errores) y los errores del §13 del modelo. No calcula nada, y la
validación no depende del régimen (modelo, §0.1, principio 3).

La validación va en dos pasadas. La primera lee la estructura y anota ERR-01
(forma y tipos) y ERR-02 (repetidos). Si hay algún ERR-01, la segunda no se
hace, porque sus comprobaciones dependen de datos que no se han podido leer
(modelo, V-21). La segunda comprueba referencias, fechas y coherencia
(ERR-03 a ERR-12). En cada pasada se recogen todos los errores, no solo el
primero.

Las decisiones de validación del modelo se citan como «Modelo, V-n». Los
demás comentarios son de implementación.
"""

import json
import re
from datetime import date
from pathlib import Path

from registro.modelo import (
    ACTIVIDADES,
    ALERTA,
    AMBITOS,
    CARGOS,
    DECLARACIONES,
    DEVOLUCION,
    GENERACION_ALERTA,
    MOMENTOS,
    MOMENTOS_DE_ALERTA,
    PERSONA,
    PROPUESTA_DECISION,
    SENTIDOS,
    TIPOS_DECISOR,
    TIPOS_ORIGEN,
    VERSION_MODELO,
    AlertaDescartada,
    Circunstancia,
    Comunicacion,
    Conclusion,
    DecisionComunicacion,
    Decisor,
    Entrada,
    Expediente,
    Fase,
    Fuente,
    Incidencia,
    IntervencionHumana,
    Interviniente,
    Operacion,
    OperacionesAnio,
    OperativaAnalizada,
    Origen,
    Participacion,
    Persona,
    Razon,
    ResultadoCarga,
    RevisionAlerta,
    Sistema,
    Sujeto,
    Voto,
)

_FECHA = re.compile(r"\d{4}-\d{2}-\d{2}")


def cargar(texto: str) -> ResultadoCarga:
    """Lee y valida una entrada en JSON."""
    return _Carga().ejecutar(texto)


def cargar_fichero(ruta) -> ResultadoCarga:
    return cargar(Path(ruta).read_text(encoding="utf-8"))


# --- Lectura del JSON --------------------------------------------------------


def _leer_json(texto):
    """Devuelve (datos, claves repetidas). Rechaza NaN e Infinity."""
    repetidas = []

    def objeto(pares):
        resultado = {}
        for clave, valor in pares:
            if clave in resultado:
                repetidas.append(clave)
            resultado[clave] = valor
        return resultado

    def constante(nombre):
        raise ValueError(f"{nombre} no es un número JSON válido")

    datos = json.loads(texto, parse_constant=constante, object_pairs_hook=objeto)
    return datos, repetidas


def _ruta(base, clave):
    return f"{base}.{clave}" if base else clave


def _es_entero(v):
    # Modelo, V-3 y V-23: ni booleanos (en Python, True es un int) ni reales como 12.0.
    return isinstance(v, int) and not isinstance(v, bool)


# --- Primera pasada: estructura (ERR-01, ERR-02) -------------------------------
#
# Cada lectura anota su ERR-01 y devuelve None en lugar del dato. Así se leen
# todos los campos y se recogen todos los errores. Con algún ERR-01 la entrada
# se descarta, así que esos None no llegan al cálculo.


class _Carga:
    def __init__(self):
        self.errores: list[Incidencia] = []

    def error(self, codigo, mensaje, ruta=""):
        self.errores.append(Incidencia(codigo, mensaje, ruta))

    def _hay(self, codigo):
        return any(e.codigo == codigo for e in self.errores)

    def ejecutar(self, texto):
        try:
            datos, repetidas = _leer_json(texto)
        except ValueError as e:
            # Modelo, V-20: un JSON mal formado es ERR-01.
            self.error("ERR-01", f"El JSON no es válido: {e}")
            return self._resultado(None)
        for clave in repetidas:
            # Modelo, V-20: una clave repetida es ERR-01. El módulo json se quedaría en
            # silencio con el último valor.
            self.error("ERR-01", f"La clave «{clave}» aparece repetida en un mismo objeto")
        if isinstance(datos, dict) and "regimen" in datos:
            # §2: no hay campo de régimen (modelo, §0.1, principio 2).
            self.error(
                "ERR-01", "La entrada no lleva régimen: es un parámetro del cálculo (modelo, §0.1 y §2)", "regimen"
            )
        entrada = self._entrada(datos)
        if self._hay("ERR-01"):
            # Modelo, V-21.
            return self._resultado(None)
        _Coherencia(self, entrada).comprobar()
        return self._resultado(None if self.errores else entrada)

    def _resultado(self, entrada):
        return ResultadoCarga(entrada=entrada, errores=tuple(sorted(self.errores, key=lambda i: i.codigo)))

    # --- Tipos básicos -------------------------------------------------------

    def _objeto(self, obj, ruta, campos, ignorar=()):
        """Comprueba que `obj` es un objeto con exactamente esos campos. Devuelve si es un objeto."""
        if not isinstance(obj, dict):
            self.error("ERR-01", "Debe ser un objeto", ruta)
            return False
        for clave in campos:
            if clave not in obj:
                # Modelo, V-2: también los campos que admiten null.
                self.error("ERR-01", f"Falta el campo obligatorio «{clave}»", _ruta(ruta, clave))
        for clave in obj:
            if clave not in campos and clave not in ignorar:
                # Modelo, V-1: cualquier campo desconocido es ERR-01, no solo `regimen`.
                self.error("ERR-01", f"Campo desconocido «{clave}»", _ruta(ruta, clave))
        return True

    def _valor(self, obj, clave, ruta, es_valido, descripcion, nulo=False):
        """obj[clave] validado, o None si falta (ya anotado), es un null admitido o está mal."""
        if clave not in obj:
            return None
        valor = obj[clave]
        if valor is None and nulo:
            return None
        if valor is None or not es_valido(valor):
            self.error("ERR-01", f"«{clave}» debe ser {descripcion}", _ruta(ruta, clave))
            return None
        return valor

    def _texto(self, obj, clave, ruta, nulo=False):
        # Modelo, V-22: se admiten textos vacíos.
        descripcion = "un texto" + (" o null" if nulo else "")
        return self._valor(obj, clave, ruta, lambda v: isinstance(v, str), descripcion, nulo)

    def _booleano(self, obj, clave, ruta):
        return self._valor(obj, clave, ruta, lambda v: isinstance(v, bool), "true o false")

    def _entero(self, obj, clave, ruta, minimo, maximo=None):
        # Modelo, V-23.
        if maximo is None:
            descripcion = f"un entero mayor o igual que {minimo}"
        else:
            descripcion = f"un entero entre {minimo} y {maximo}"
        return self._valor(
            obj, clave, ruta, lambda v: _es_entero(v) and v >= minimo and (maximo is None or v <= maximo), descripcion
        )

    def _enumerado(self, obj, clave, ruta, valores):
        descripcion = " o ".join(f"«{v}»" for v in valores)
        return self._valor(obj, clave, ruta, lambda v: isinstance(v, str) and v in valores, descripcion)

    def _fecha(self, obj, clave, ruta, nulo=False):
        texto = self._valor(obj, clave, ruta, lambda v: isinstance(v, str), "una fecha AAAA-MM-DD", nulo)
        if texto is None:
            return None
        try:
            # Modelo, V-3: fromisoformat admite también otras formas (20240101, semanas);
            # el modelo pide AAAA-MM-DD (§2).
            if not _FECHA.fullmatch(texto):
                raise ValueError
            return date.fromisoformat(texto)
        except ValueError:
            self.error("ERR-01", f"«{clave}» debe ser una fecha AAAA-MM-DD", _ruta(ruta, clave))
            return None

    def _lista(self, obj, clave, ruta, leer_elemento):
        """Los elementos de obj[clave] leídos con `leer_elemento` (None los mal formados).

        Si falta (ya anotado) o no es una lista, devuelve una lista vacía.
        """
        if clave not in obj:
            return []
        valor = obj[clave]
        if not isinstance(valor, list):
            self.error("ERR-01", f"«{clave}» debe ser una lista", _ruta(ruta, clave))
            return []
        return [leer_elemento(elemento, f"{_ruta(ruta, clave)}[{i}]") for i, elemento in enumerate(valor)]

    def _sub(self, obj, clave, ruta, leer):
        """Lee el objeto obj[clave] con `leer`; None si falta (ya anotado)."""
        if clave not in obj:
            return None
        return leer(obj[clave], _ruta(ruta, clave))

    def _nulo_o(self, obj, clave, ruta, leer):
        """Como `_sub`, pero un null es un valor admitido."""
        if clave not in obj or obj[clave] is None:
            return None
        return leer(obj[clave], _ruta(ruta, clave))

    def _elemento_enumerado(self, valores):
        def leer(valor, ruta):
            if not (isinstance(valor, str) and valor in valores):
                self.error("ERR-01", "Debe ser " + " o ".join(f"«{v}»" for v in valores), ruta)
                return None
            return valor

        return leer

    def _cadena_suelta(self, valor, ruta):
        if not isinstance(valor, str):
            self.error("ERR-01", "Debe ser un texto", ruta)
            return None
        return valor

    def _referencias(self, obj, clave, ruta):
        """Lista de `id` citados. Modelo, V-24: una referencia repetida es ERR-02."""
        ids = self._lista(obj, clave, ruta, self._cadena_suelta)
        self._unicos(list(enumerate(ids)), _ruta(ruta, clave), None, "referencia")
        return tuple(i for i in ids if i is not None)

    def _unicos(self, valores, ruta_lista, campo, que):
        """ERR-02 por cada valor repetido. `valores` es una lista de (índice, valor)."""
        vistos = set()
        for i, valor in valores:
            if valor is None:
                continue
            if valor in vistos:
                ruta = f"{ruta_lista}[{i}]" + (f".{campo}" if campo else "")
                self.error("ERR-02", f"{que.capitalize()} «{valor}» repetido", ruta)
            vistos.add(valor)

    def _con_ids(self, obj, clave, ruta, leer, que):
        """Lista de objetos con `id`. Modelo, V-4: los `id` son únicos en su lista."""
        elementos = self._lista(obj, clave, ruta, leer)
        self._unicos([(i, e.id) for i, e in enumerate(elementos) if e], _ruta(ruta, clave), "id", f"id de {que}")
        return tuple(e for e in elementos if e)

    # --- Primer nivel (§2) ---------------------------------------------------

    def _entrada(self, datos):
        campos = (
            "version_modelo",
            "sujeto",
            "personas",
            "sistemas",
            "participaciones_ia",
            "expediente",
            "alerta_descartada",
        )
        if not self._objeto(datos, "", campos, ignorar=("regimen",)):
            return None
        return Entrada(
            self._version(datos),
            self._sub(datos, "sujeto", "", self._sujeto),
            self._con_ids(datos, "personas", "", self._persona, "persona"),
            self._con_ids(datos, "sistemas", "", self._sistema, "sistema"),
            self._con_ids(datos, "participaciones_ia", "", self._participacion, "participación"),
            self._nulo_o(datos, "expediente", "", self._expediente),
            self._nulo_o(datos, "alerta_descartada", "", self._alerta),
        )

    def _version(self, datos):
        version = self._valor(datos, "version_modelo", "", _es_entero, "un entero")
        if version is not None and version != VERSION_MODELO:
            # Modelo, V-3.
            self.error("ERR-01", f"«version_modelo» debe ser {VERSION_MODELO}", "version_modelo")
            return None
        return version

    def _sujeto(self, obj, ruta):
        if not self._objeto(obj, ruta, ("actividad", "operaciones_anuales")):
            return None
        anios = self._lista(obj, "operaciones_anuales", ruta, self._operaciones_anio)
        # Modelo, V-4: `anio` no se repite.
        self._unicos([(i, a.anio) for i, a in enumerate(anios) if a], f"{ruta}.operaciones_anuales", "anio", "año")
        return Sujeto(self._enumerado(obj, "actividad", ruta, ACTIVIDADES), tuple(a for a in anios if a))

    def _operaciones_anio(self, obj, ruta):
        if not self._objeto(obj, ruta, ("anio", "numero")):
            return None
        return OperacionesAnio(self._entero(obj, "anio", ruta, 1, 9999), self._entero(obj, "numero", ruta, 0))

    def _persona(self, obj, ruta):
        if not self._objeto(obj, ruta, ("id", "cargos")):
            return None
        cargos = self._lista(obj, "cargos", ruta, self._elemento_enumerado(CARGOS))
        # Modelo, V-4: un cargo no se repite en una persona.
        self._unicos(list(enumerate(cargos)), f"{ruta}.cargos", None, "cargo")
        return Persona(self._texto(obj, "id", ruta), tuple(c for c in cargos if c))

    def _sistema(self, obj, ruta):
        if not self._objeto(obj, ruta, ("id", "declaracion_sistema_ia")):
            return None
        return Sistema(self._texto(obj, "id", ruta), self._enumerado(obj, "declaracion_sistema_ia", ruta, DECLARACIONES))

    def _participacion(self, obj, ruta):
        if not self._objeto(obj, ruta, ("id", "sistema", "momento", "fecha", "salida", "intervencion_humana")):
            return None
        return Participacion(
            self._texto(obj, "id", ruta),
            self._texto(obj, "sistema", ruta),
            self._enumerado(obj, "momento", ruta, MOMENTOS),
            self._fecha(obj, "fecha", ruta),
            # §9.3: la salida es una cadena, tal como la dio el sistema. Un número es ERR-01.
            self._texto(obj, "salida", ruta),
            tuple(i for i in self._lista(obj, "intervencion_humana", ruta, self._intervencion) if i),
        )

    def _intervencion(self, obj, ruta):
        if not self._objeto(obj, ruta, ("persona", "fecha", "descripcion")):
            return None
        return IntervencionHumana(
            self._texto(obj, "persona", ruta), self._fecha(obj, "fecha", ruta), self._texto(obj, "descripcion", ruta)
        )

    # --- Expediente (§3 a §8) ------------------------------------------------

    def _expediente(self, obj, ruta):
        campos = (
            "id",
            "fecha_apertura",
            "fecha_fin_analisis_tecnico",
            "fecha_cierre",
            "origen",
            "participaciones_incorporadas",
            "operativa_analizada",
            "fuentes",
            "fases",
            "circunstancias_consideradas",
            "conclusion",
            "decision_comunicacion",
        )
        if not self._objeto(obj, ruta, campos):
            return None
        return Expediente(
            self._texto(obj, "id", ruta),
            self._fecha(obj, "fecha_apertura", ruta),
            self._fecha(obj, "fecha_fin_analisis_tecnico", ruta),
            self._fecha(obj, "fecha_cierre", ruta),
            self._sub(obj, "origen", ruta, self._origen),
            self._referencias(obj, "participaciones_incorporadas", ruta),
            self._sub(obj, "operativa_analizada", ruta, self._operativa),
            self._con_ids(obj, "fuentes", ruta, self._fuente, "fuente"),
            self._con_ids(obj, "fases", ruta, self._fase, "fase"),
            self._con_ids(obj, "circunstancias_consideradas", ruta, self._circunstancia, "circunstancia"),
            self._sub(obj, "conclusion", ruta, self._conclusion),
            self._sub(obj, "decision_comunicacion", ruta, self._decision),
        )

    def _origen(self, obj, ruta):
        if not self._objeto(obj, ruta, ("tipo", "descripcion", "participaciones_ia", "expediente_devuelto")):
            return None
        return Origen(
            self._enumerado(obj, "tipo", ruta, TIPOS_ORIGEN),
            self._texto(obj, "descripcion", ruta),
            self._referencias(obj, "participaciones_ia", ruta),
            self._texto(obj, "expediente_devuelto", ruta, nulo=True),
        )

    def _operativa(self, obj, ruta):
        if not self._objeto(obj, ruta, ("descripcion", "operaciones", "intervinientes")):
            return None
        return OperativaAnalizada(
            self._texto(obj, "descripcion", ruta),
            self._con_ids(obj, "operaciones", ruta, self._operacion, "operación"),
            self._con_ids(obj, "intervinientes", ruta, self._interviniente, "interviniente"),
        )

    def _operacion(self, obj, ruta):
        if not self._objeto(obj, ruta, ("id", "descripcion", "ejecutada")):
            return None
        return Operacion(
            self._texto(obj, "id", ruta), self._texto(obj, "descripcion", ruta), self._booleano(obj, "ejecutada", ruta)
        )

    def _interviniente(self, obj, ruta):
        if not self._objeto(obj, ruta, ("id", "papel")):
            return None
        return Interviniente(self._texto(obj, "id", ruta), self._texto(obj, "papel", ruta))

    def _fuente(self, obj, ruta):
        if not self._objeto(obj, ruta, ("id", "descripcion", "ambito")):
            return None
        return Fuente(
            self._texto(obj, "id", ruta), self._texto(obj, "descripcion", ruta), self._enumerado(obj, "ambito", ruta, AMBITOS)
        )

    def _fase(self, obj, ruta):
        if not self._objeto(obj, ruta, ("id", "descripcion", "gestiones", "fuentes", "participaciones_ia")):
            return None
        return Fase(
            self._texto(obj, "id", ruta),
            self._texto(obj, "descripcion", ruta),
            tuple(g for g in self._lista(obj, "gestiones", ruta, self._cadena_suelta) if g is not None),
            self._referencias(obj, "fuentes", ruta),
            self._referencias(obj, "participaciones_ia", ruta),
        )

    def _circunstancia(self, obj, ruta):
        if not self._objeto(obj, ruta, ("id", "descripcion", "fuentes", "participaciones_ia")):
            return None
        return Circunstancia(
            self._texto(obj, "id", ruta),
            self._texto(obj, "descripcion", ruta),
            self._referencias(obj, "fuentes", ruta),
            self._referencias(obj, "participaciones_ia", ruta),
        )

    def _conclusion(self, obj, ruta):
        if not self._objeto(obj, ruta, ("texto", "razones")):
            return None
        razones = self._lista(obj, "razones", ruta, self._razon)
        return Conclusion(self._texto(obj, "texto", ruta), tuple(r for r in razones if r))

    def _razon(self, obj, ruta):
        if not self._objeto(obj, ruta, ("descripcion", "circunstancias")):
            return None
        return Razon(self._texto(obj, "descripcion", ruta), self._referencias(obj, "circunstancias", ruta))

    def _decision(self, obj, ruta):
        campos = (
            "comunicar",
            "fecha",
            "motivacion",
            "decisor",
            "comunicacion",
            "fecha_puesta_en_conocimiento_comunicante",
        )
        if not self._objeto(obj, ruta, campos):
            return None
        return DecisionComunicacion(
            self._booleano(obj, "comunicar", ruta),
            self._fecha(obj, "fecha", ruta),
            self._texto(obj, "motivacion", ruta),
            self._sub(obj, "decisor", ruta, self._decisor),
            self._nulo_o(obj, "comunicacion", ruta, self._comunicacion),
            self._fecha(obj, "fecha_puesta_en_conocimiento_comunicante", ruta, nulo=True),
        )

    def _decisor(self, obj, ruta):
        if not self._objeto(obj, ruta, ("tipo", "persona", "votos")):
            return None
        votos = None
        if obj.get("votos") is not None:
            leidos = self._lista(obj, "votos", ruta, self._voto)
            # Modelo, V-4: una persona no se repite en `votos`.
            self._unicos([(i, v.persona) for i, v in enumerate(leidos) if v], f"{ruta}.votos", "persona", "persona")
            votos = tuple(v for v in leidos if v)
        return Decisor(
            self._enumerado(obj, "tipo", ruta, TIPOS_DECISOR), self._texto(obj, "persona", ruta, nulo=True), votos
        )

    def _voto(self, obj, ruta):
        if not self._objeto(obj, ruta, ("persona", "sentido", "motivacion")):
            return None
        return Voto(
            self._texto(obj, "persona", ruta),
            self._enumerado(obj, "sentido", ruta, SENTIDOS),
            self._texto(obj, "motivacion", ruta, nulo=True),
        )

    def _comunicacion(self, obj, ruta):
        if not self._objeto(obj, ruta, ("fecha", "referencia_copia")):
            return None
        return Comunicacion(self._fecha(obj, "fecha", ruta), self._texto(obj, "referencia_copia", ruta, nulo=True))

    # --- Alerta descartada (§10) ---------------------------------------------

    def _alerta(self, obj, ruta):
        campos = (
            "id",
            "participaciones_ia",
            "descripcion_operativa",
            "revision",
            "fuentes",
            "circunstancias_consideradas",
            "resultado",
        )
        if not self._objeto(obj, ruta, campos):
            return None
        return AlertaDescartada(
            self._texto(obj, "id", ruta),
            self._referencias(obj, "participaciones_ia", ruta),
            self._texto(obj, "descripcion_operativa", ruta),
            self._sub(obj, "revision", ruta, self._revision),
            self._con_ids(obj, "fuentes", ruta, self._fuente, "fuente"),
            self._con_ids(obj, "circunstancias_consideradas", ruta, self._circunstancia, "circunstancia"),
            self._texto(obj, "resultado", ruta, nulo=True),
        )

    def _revision(self, obj, ruta):
        if not self._objeto(obj, ruta, ("persona", "fecha")):
            return None
        return RevisionAlerta(self._texto(obj, "persona", ruta), self._fecha(obj, "fecha", ruta))


# --- Segunda pasada: referencias, fechas y coherencia (ERR-03 a ERR-12) --------


class _Coherencia:
    """Solo se ejecuta sin ningún ERR-01: todos los campos están leídos (modelo, V-21)."""

    def __init__(self, carga: _Carga, entrada: Entrada):
        self.carga = carga
        self.e = entrada
        self.personas = {p.id for p in entrada.personas}
        self.sistemas = {s.id for s in entrada.sistemas}
        self.participaciones = {p.id: p for p in entrada.participaciones_ia}

    def error(self, codigo, mensaje, ruta):
        self.carga.error(codigo, mensaje, ruta)

    def comprobar(self):
        e = self.e
        if (e.expediente is None) == (e.alerta_descartada is None):
            # Modelo, V-13.
            que = "ninguno de los dos" if e.expediente is None else "los dos"
            self.error("ERR-08", f"Debe haber uno y solo uno de «expediente» y «alerta_descartada»; hay {que}", "")
        self._participaciones()
        citadas: set[str] = set()
        if e.expediente is not None:
            citadas |= self._expediente(e.expediente)
        if e.alerta_descartada is not None:
            citadas |= self._alerta(e.alerta_descartada)
        for i, p in enumerate(e.participaciones_ia):
            if p.id not in citadas:
                # Modelo, V-16 y V-17.
                self.error(
                    "ERR-11",
                    f"La participación «{p.id}» no la cita ninguna parte del registro",
                    f"participaciones_ia[{i}]",
                )
        usados = {p.sistema for p in e.participaciones_ia}
        for i, s in enumerate(e.sistemas):
            if s.id not in usados:
                # Modelo, V-13.
                self.error("ERR-09", f"El sistema «{s.id}» no aparece en ninguna participación", f"sistemas[{i}]")

    # --- Referencias (ERR-03) -------------------------------------------------

    def _ref(self, valor, existentes, ruta, que):
        # Modelo, V-5.
        if valor not in existentes:
            self.error("ERR-03", f"{que} «{valor}» no existe", ruta)

    def _refs(self, valores, existentes, ruta, que):
        for j, valor in enumerate(valores):
            self._ref(valor, existentes, f"{ruta}[{j}]", que)

    def _participaciones(self):
        for i, p in enumerate(self.e.participaciones_ia):
            ruta = f"participaciones_ia[{i}]"
            self._ref(p.sistema, self.sistemas, f"{ruta}.sistema", "El sistema")
            for j, ih in enumerate(p.intervencion_humana):
                self._ref(ih.persona, self.personas, f"{ruta}.intervencion_humana[{j}].persona", "La persona")

    def _circunstancias(self, circunstancias, fuentes, ruta):
        ids_fuentes = {f.id for f in fuentes}
        citadas = set()
        for i, c in enumerate(circunstancias):
            r = f"{ruta}.circunstancias_consideradas[{i}]"
            # Modelo, V-5: las fuentes de las circunstancias son las del mismo objeto.
            self._refs(c.fuentes, ids_fuentes, f"{r}.fuentes", "La fuente")
            self._refs(c.participaciones_ia, self.participaciones, f"{r}.participaciones_ia", "La participación")
            citadas |= set(c.participaciones_ia)
        return citadas

    # --- Expediente -----------------------------------------------------------

    def _expediente(self, x: Expediente) -> set[str]:
        ruta = "expediente"
        citadas = set(x.origen.participaciones_ia) | set(x.participaciones_incorporadas)
        self._refs(x.origen.participaciones_ia, self.participaciones, f"{ruta}.origen.participaciones_ia", "La participación")
        self._refs(x.participaciones_incorporadas, self.participaciones, f"{ruta}.participaciones_incorporadas", "La participación")
        ids_fuentes = {f.id for f in x.fuentes}
        for i, fase in enumerate(x.fases):
            r = f"{ruta}.fases[{i}]"
            self._refs(fase.fuentes, ids_fuentes, f"{r}.fuentes", "La fuente")
            self._refs(fase.participaciones_ia, self.participaciones, f"{r}.participaciones_ia", "La participación")
            citadas |= set(fase.participaciones_ia)
        citadas |= self._circunstancias(x.circunstancias_consideradas, x.fuentes, ruta)
        ids_circunstancias = {c.id for c in x.circunstancias_consideradas}
        for i, razon in enumerate(x.conclusion.razones):
            self._refs(razon.circunstancias, ids_circunstancias, f"{ruta}.conclusion.razones[{i}].circunstancias", "La circunstancia")
        if not x.conclusion.razones:
            # Modelo, V-12.
            self.error("ERR-07", "«razones» no puede estar vacía", f"{ruta}.conclusion.razones")
        self._origen(x.origen, f"{ruta}.origen")
        self._decision(x, f"{ruta}.decision_comunicacion")
        self._fechas(x, ruta)
        return citadas

    def _origen(self, o: Origen, ruta):
        momentos = [self.participaciones[p].momento for p in o.participaciones_ia if p in self.participaciones]
        for j, p in enumerate(o.participaciones_ia):
            if p in self.participaciones and self.participaciones[p].momento not in MOMENTOS_DE_ALERTA:
                # Modelo, V-18.
                self.error(
                    "ERR-12",
                    f"La participación «{p}» tiene el momento «{self.participaciones[p].momento}», que no es de alerta",
                    f"{ruta}.participaciones_ia[{j}]",
                )
        if o.tipo == ALERTA and GENERACION_ALERTA not in momentos:
            # Modelo, V-18.
            self.error("ERR-12", "Con «tipo» «alerta», falta la participación que generó la alerta", f"{ruta}.participaciones_ia")
        # Modelo, V-7.
        if o.tipo == DEVOLUCION and o.expediente_devuelto is None:
            self.error("ERR-05", "Con «tipo» «devolucion_servicio_ejecutivo», «expediente_devuelto» no puede ser null", f"{ruta}.expediente_devuelto")
        if o.tipo != DEVOLUCION and o.expediente_devuelto is not None:
            self.error("ERR-05", "«expediente_devuelto» solo se admite con «tipo» «devolucion_servicio_ejecutivo»", f"{ruta}.expediente_devuelto")

    def _decision(self, x: Expediente, ruta):
        d = x.decision_comunicacion
        decisor = d.decisor
        r = f"{ruta}.decisor"
        # Modelo, V-7.
        if decisor.tipo == PERSONA:
            if decisor.persona is None:
                self.error("ERR-05", "Con «tipo» «persona», «persona» no puede ser null", f"{r}.persona")
            if decisor.votos is not None:
                self.error("ERR-05", "Con «tipo» «persona», «votos» debe ser null", f"{r}.votos")
        elif decisor.persona is not None:
            self.error("ERR-05", "Con un órgano colegiado, «persona» debe ser null", f"{r}.persona")
        if decisor.persona is not None:
            self._ref(decisor.persona, self.personas, f"{r}.persona", "La persona")
        for j, voto in enumerate(decisor.votos or ()):
            self._ref(voto.persona, self.personas, f"{r}.votos[{j}].persona", "La persona")
        if not d.comunicar and d.comunicacion is not None:
            # Modelo, V-8.
            self.error("ERR-06", "Con «comunicar» false, «comunicacion» debe ser null", f"{ruta}.comunicacion")

    def _fechas(self, x: Expediente, ruta):
        # Modelo, V-6. No se compara `fecha_cierre` con la decisión ni con la comunicación (R-9).
        d = x.decision_comunicacion
        cadena = [
            ("fecha_apertura", x.fecha_apertura, f"{ruta}.fecha_apertura"),
            ("fecha_fin_analisis_tecnico", x.fecha_fin_analisis_tecnico, f"{ruta}.fecha_fin_analisis_tecnico"),
            ("decision_comunicacion.fecha", d.fecha, f"{ruta}.decision_comunicacion.fecha"),
        ]
        if d.comunicacion is not None:
            cadena.append(("comunicacion.fecha", d.comunicacion.fecha, f"{ruta}.decision_comunicacion.comunicacion.fecha"))
        for (n1, f1, _), (n2, f2, r2) in zip(cadena, cadena[1:]):
            if f2 < f1:
                self.error("ERR-04", f"«{n2}» ({f2}) es anterior a «{n1}» ({f1})", r2)
        if x.fecha_cierre < x.fecha_apertura:
            self.error("ERR-04", f"«fecha_cierre» ({x.fecha_cierre}) es anterior a «fecha_apertura» ({x.fecha_apertura})", f"{ruta}.fecha_cierre")

    # --- Alerta descartada ----------------------------------------------------

    def _alerta(self, a: AlertaDescartada) -> set[str]:
        ruta = "alerta_descartada"
        self._refs(a.participaciones_ia, self.participaciones, f"{ruta}.participaciones_ia", "La participación")
        self._ref(a.revision.persona, self.personas, f"{ruta}.revision.persona", "La persona")
        citadas = set(a.participaciones_ia) | self._circunstancias(a.circunstancias_consideradas, a.fuentes, ruta)
        momentos = [self.participaciones[p].momento for p in a.participaciones_ia if p in self.participaciones]
        # Modelo, V-14.
        if GENERACION_ALERTA not in momentos:
            self.error("ERR-10", "Falta la participación que generó la alerta", f"{ruta}.participaciones_ia")
        for j, p in enumerate(a.participaciones_ia):
            if p in self.participaciones and self.participaciones[p].momento == PROPUESTA_DECISION:
                self.error("ERR-10", f"La participación «{p}» es una propuesta de decisión", f"{ruta}.participaciones_ia[{j}]")
        # Modelo, V-15: no se exige que haya fuentes, circunstancias ni resultado.
        return citadas
