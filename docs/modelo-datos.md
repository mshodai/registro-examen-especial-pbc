# Modelo de datos de entrada

Este documento define el JSON que describe **un examen especial** (Ley 10/2010 y RD 304/2014) **o una evaluación de las operaciones o actividades de un cliente** (AMLR, art. 69.2) en la que puede haber participado un sistema de IA. Solo describe la entrada. Todavía no hay especificación del cálculo ni código.

Siglas y fuentes (detalle y huellas en [`fuentes/FUENTES.md`](fuentes/FUENTES.md)):

- **Ley**: Ley 10/2010, texto consolidado con última modificación de 21 de marzo de 2026.
- **RD**: Reglamento aprobado por el Real Decreto 304/2014, texto consolidado con última modificación de 24 de abril de 2024.
- **AMLR**: Reglamento (UE) 2024/1624, texto publicado en el DO L de 19.6.2024. Aplicable desde el 10 de julio de 2027 (art. 90).
- **AI Act**: Reglamento (UE) 2024/1689. Se cita por el texto original (DO L de 12.7.2024) salvo que se diga «consolidado», que es el texto a 27 de julio de 2026, **sin efecto jurídico**.
- **Borrador de la Comisión**: proyecto de directrices sobre la clasificación de sistemas de IA de alto riesgo, anexo dedicado al anexo III del AI Act, publicado el 19 de mayo de 2026. **Es un borrador no vinculante.** Ningún campo sale de él.

Convenciones:

- Las citas van entre comillas «» y son literales. Las del borrador de la Comisión están en inglés, el único idioma en que se publicó, con una traducción propia entre corchetes.
- **[Decisión propia]** marca lo que no sale de los textos, sino del diseño de este proyecto.
- Los casos que la norma no resuelve (R-1 a R-10) están en el §13. El modelo no los decide: recoge los hechos que hacen falta para aplicar cada lectura.
- Los términos siguen a cada texto: «examen especial», «Servicio Ejecutivo de la Comisión» y «comunicación por indicio» en la Ley y el RD; «evaluación», «UIF» y «comunicación de sospechas» en el AMLR. El modelo usa `expediente` y `decision_comunicacion` para los dos. **[Decisión propia]**

---

## 0. Principios

### 0.1. Los de la serie

1. **La entrada recoge hechos, no conclusiones.** **[Decisión propia]** El JSON dice qué se examinó, qué fuentes se consultaron, qué se concluyó, quién decidió y qué devolvió el sistema de IA. No dice si el registro cumple, si la decisión se tomó «sin demora» ni si la intervención humana fue «significativa»: eso depende del régimen y de la lectura.
2. **El régimen no forma parte de la entrada.** **[Decisión propia]** El régimen es un parámetro del cálculo. El mismo JSON se lee con la Ley y el RD y con el AMLR. Un campo `regimen` obligaría a quien rellena la entrada a decidir si el art. 25 del RD sigue aplicándose desde el 10 de julio de 2027 ([R-3](#r-3)), que ningún texto resuelve.
3. **La validación no depende del régimen.** **[Decisión propia]** Un hecho que un régimen no usa no es un error de entrada. Por ejemplo, la referencia a la copia de la comunicación (solo AMLR) en un examen de 2026, o los votos de un órgano colegiado (solo RD) en una evaluación de 2028.
4. **Los casos no resueltos se documentan, no se resuelven en silencio.** Cuando un texto admite dos lecturas, el modelo recoge los hechos que distinguen una de otra (§13).

### 0.2. Las tres reglas propias de este proyecto

Estas reglas son **[Decisión propia]** y ningún cambio del modelo puede saltárselas.

1. **Cada campo del registro se cita a su artículo. Si un campo no sale de la norma, no entra.** Un campo entra si un artículo exige que conste en el registro o si hace falta para aplicar un artículo a este examen (por ejemplo, una fecha sin la que no se puede comprobar un «sin demora»). Las tablas de cada sección dan la cita de cada campo. Los campos puramente técnicos (`version_modelo`, los `id` y las referencias entre objetos) están marcados como decisión propia y no añaden hechos. Lo que se ha dejado fuera, y por qué, está en el §11.
2. **Del sistema de IA no se modela nada interno: ni variables, ni umbrales, ni reglas, ni tipos de alerta.** El sistema es una caja cerrada. Su salida es un dato más del registro: una cadena que se guarda tal como la produjo el sistema y que el modelo no interpreta (§9). El modelo tampoco clasifica el sistema: no dice si es de alto riesgo según el AI Act ni si cumple la definición de su art. 3, punto 1.
3. **Los ejemplos usan motivos genéricos e inventados.** Ningún ejemplo de este repositorio describe una tipología real de blanqueo, un indicador de riesgo concreto ni un caso real. Las descripciones son del tipo «Circunstancia de ejemplo 1 (motivo inventado)», y las salidas del sistema, cadenas opacas como `"SALIDA-EJEMPLO-1"`, que no son puntuaciones ni etiquetas de un sistema real.

---

## 1. Ejemplo completo

Un examen especial abierto en septiembre de 2027, después de la fecha de aplicación del AMLR: con la entrada así, se puede leer con los dos regímenes ([R-3](#r-3)). Lo abre una alerta en la que participó un sistema; otro sistema interviene en el análisis; decide el órgano de control interno por mayoría.

```json
{
  "version_modelo": 1,
  "sujeto": {
    "actividad": "otra",
    "operaciones_anuales": [
      { "anio": 2026, "numero": 18450 }
    ]
  },
  "expediente": {
    "id": "EXP-0001",
    "fecha_apertura": "2027-09-06",
    "fecha_fin_analisis_tecnico": "2027-09-24",
    "fecha_cierre": "2027-09-29",
    "personas": [
      {
        "id": "P-1",
        "cargos": [
          "representante_servicio_ejecutivo",
          "responsable_cumplimiento_normativo",
          "miembro_organo_control_interno"
        ]
      },
      { "id": "P-2", "cargos": ["miembro_organo_control_interno"] },
      { "id": "P-3", "cargos": ["miembro_organo_control_interno"] },
      { "id": "P-4", "cargos": ["otro"] }
    ],
    "origen": {
      "tipo": "alerta",
      "descripcion": "Alerta de ejemplo A sobre la operativa de un cliente ficticio (motivo inventado)",
      "expediente_devuelto": null
    },
    "operativa_analizada": {
      "descripcion": "Operaciones de ejemplo de un cliente ficticio entre junio y agosto de 2027",
      "operaciones": [
        { "id": "OP-1", "descripcion": "Operación de ejemplo 1", "ejecutada": true },
        { "id": "OP-2", "descripcion": "Operación de ejemplo 2", "ejecutada": true },
        { "id": "OP-3", "descripcion": "Operación de ejemplo 3, solicitada y no realizada", "ejecutada": false }
      ],
      "intervinientes": [
        { "id": "INT-1", "papel": "cliente" },
        { "id": "INT-2", "papel": "contraparte de OP-1 y OP-2" }
      ]
    },
    "fuentes": [
      { "id": "F-1", "descripcion": "Expediente de diligencia debida del cliente", "ambito": "sujeto_obligado" },
      { "id": "F-2", "descripcion": "Información de otra entidad del grupo", "ambito": "grupo" },
      { "id": "F-3", "descripcion": "Registro público de ejemplo", "ambito": "externa" }
    ],
    "fases": [
      {
        "id": "FA-1",
        "descripcion": "Revisión de la operativa del periodo",
        "gestiones": ["Gestión de ejemplo 1"],
        "fuentes": ["F-1"],
        "participaciones_ia": ["IA-2"]
      },
      {
        "id": "FA-2",
        "descripcion": "Contraste con la información del grupo y con fuentes externas",
        "gestiones": ["Gestión de ejemplo 2", "Gestión de ejemplo 3"],
        "fuentes": ["F-2", "F-3"],
        "participaciones_ia": []
      }
    ],
    "circunstancias_consideradas": [
      { "id": "C-1", "descripcion": "Circunstancia de ejemplo 1 (motivo inventado)", "fuentes": ["F-1"], "participaciones_ia": [] },
      { "id": "C-2", "descripcion": "Circunstancia de ejemplo 2 (motivo inventado)", "fuentes": ["F-2", "F-3"], "participaciones_ia": [] },
      { "id": "C-3", "descripcion": "Salida del sistema en la fase FA-1", "fuentes": [], "participaciones_ia": ["IA-2"] }
    ],
    "conclusion": {
      "texto": "Conclusión de ejemplo: la operativa examinada no tiene una justificación que el sujeto obligado haya podido comprobar (motivo inventado)",
      "razones": [
        { "descripcion": "Razón de ejemplo 1", "circunstancias": ["C-1", "C-2"] },
        { "descripcion": "Razón de ejemplo 2", "circunstancias": ["C-3"] }
      ]
    },
    "decision_comunicacion": {
      "comunicar": true,
      "fecha": "2027-09-27",
      "motivacion": "Motivación de ejemplo de la decisión",
      "decisor": {
        "tipo": "organo_control_interno",
        "persona": null,
        "votos": [
          { "persona": "P-1", "sentido": "comunicar", "motivacion": "Motivación de ejemplo del voto 1" },
          { "persona": "P-2", "sentido": "comunicar", "motivacion": "Motivación de ejemplo del voto 2" },
          { "persona": "P-3", "sentido": "no_comunicar", "motivacion": "Motivación de ejemplo del voto 3" }
        ]
      },
      "comunicacion": {
        "fecha": "2027-09-28",
        "referencia_copia": "DOC-EJEMPLO-0001"
      },
      "fecha_puesta_en_conocimiento_comunicante": null
    },
    "participaciones_ia": [
      {
        "id": "IA-1",
        "sistema": "SIS-A",
        "momento": "generacion_alerta",
        "fecha": "2027-09-02",
        "salida": "SALIDA-EJEMPLO-1",
        "intervencion_humana": [
          { "persona": "P-4", "fecha": "2027-09-06", "descripcion": "Revisión de la alerta; se decide abrir el examen especial" }
        ]
      },
      {
        "id": "IA-2",
        "sistema": "SIS-B",
        "momento": "analisis",
        "fecha": "2027-09-10",
        "salida": "SALIDA-EJEMPLO-2",
        "intervencion_humana": [
          { "persona": "P-4", "fecha": "2027-09-12", "descripcion": "Contraste de la salida con la fuente F-1" }
        ]
      }
    ]
  }
}
```

---

## 2. Campos de primer nivel

| Campo | Tipo | Obligatorio | Descripción y cita |
|---|---|---|---|
| `version_modelo` | entero | sí | Versión de este esquema. Es `1`. **[Decisión propia]** |
| `sujeto` | objeto | sí | Hechos del sujeto obligado que no son del examen, pero de los que depende aplicarle la norma. Ver §2.1. |
| `expediente` | objeto | sí | El examen o la evaluación. Ver §3 a §9. |

No hay campo de régimen (§0.1, principio 2). Un JSON con `regimen`, o con cualquier otro campo que el modelo no define, es un error de validación (§12).

Todas las fechas son de día, en la forma `AAAA-MM-DD`, sin hora ni zona horaria. **[Decisión propia]**: ninguno de los textos fija por horas los plazos de este registro («sin demora», RD, art. 25.2; «sin dilación», Ley, art. 18.2; «sin demora», AMLR, art. 69.1).

**Un JSON, un expediente.** **[Decisión propia]** El RD pide el registro «para cada expediente de examen especial realizado» (art. 25.3), y el AMLR, «un registro de la evaluación realizada» (art. 77.1.b). El registro cronológico de todos los expedientes (RD, art. 25.3: «por orden cronológico») se forma con varios JSON ordenados por `fecha_apertura`. Este modelo no lo representa.

**Solo expedientes concluidos.** **[Decisión propia]** La entrada describe un examen con conclusión y decisión. Un examen en curso todavía no tiene los datos que exigen el RD, art. 25.3, y el AMLR, art. 77.1.b («los resultados de dicha evaluación»). Si la evaluación terminó sin abrir un examen especial, ver [R-6](#r-6).

### 2.1. `sujeto`

| Campo | Tipo | Obligatorio | Descripción y cita |
|---|---|---|---|
| `actividad` | `"agente_de_futbol"` \| `"club_de_futbol_profesional"` \| `"otra"` | sí | Hecho del que depende la fecha de aplicación del AMLR. Art. 90: «Será aplicable a partir del 10 de julio de 2027, excepto para las entidades obligadas a que se refiere el artículo 3, punto 3, letras n) a o), para quienes será aplicable desde el 10 de julio de 2029». Mismo campo y mismos valores que en `plazos-conservacion-pbc` y `plazos-actualizacion-pbc`. |
| `operaciones_anuales` | lista de `{ "anio": entero, "numero": entero ≥ 0 }` | sí | Número de operaciones del sujeto obligado por año. RD, art. 23, párrafo segundo: «En el caso de sujetos obligados cuyo número anual de operaciones exceda de 10.000, será preceptiva la implantación de modelos automatizados de generación y priorización de alertas». Puede estar vacía si el dato no consta. `anio` no se repite. |

**Por qué una lista y no un número.** El RD no dice qué año cuenta ni cómo se cuentan las operaciones ([R-7](#r-7)). Con una lista, la entrada recoge los años que la entidad conoce y cada lectura elige el suyo. **[Decisión propia]**

**Qué no dice el dato.** El modelo no recoge si la entidad tiene implantados «modelos automatizados de generación y priorización de alertas». Esa sería una afirmación sobre la configuración interna de sus sistemas (§0.2, regla 2). Lo que sí recoge es si en este examen participó un sistema en la generación o la priorización de la alerta (§9).

---

## 3. Expediente: identificación, fechas y personas

| Campo | Tipo | Obligatorio | Descripción y cita |
|---|---|---|---|
| `id` | cadena | sí | Identificador del expediente. **[Decisión propia]**; el RD habla de «cada expediente de examen especial» (art. 25.3). |
| `fecha_apertura` | fecha | sí | RD, art. 25.3: «sus fechas de apertura y cierre». |
| `fecha_fin_analisis_tecnico` | fecha | sí | Día en que concluyó el análisis técnico. RD, art. 25.2: «Concluido el análisis técnico, el representante ante el Servicio Ejecutivo de la Comisión adoptará, motivadamente y sin demora, la decisión». Sin esta fecha no se puede comprobar el «sin demora». |
| `fecha_cierre` | fecha | sí | RD, art. 25.3: «sus fechas de apertura y cierre». Qué hecho cierra el expediente es [R-9](#r-9). |
| `personas` | lista | sí | Las personas que deciden, votan o intervienen sobre la salida de un sistema. Ver §3.1. |

El AMLR no pide ninguna de estas fechas (§10). Se piden siempre, porque la validación no depende del régimen (§0.1, principio 3).

### 3.1. `personas[]`

Las personas se identifican con un código, no con su nombre. **[Decisión propia]**: el registro exige saber quién decidió y con qué cargo, no los datos de identidad, y el modelo no necesita datos personales para eso.

| Campo | Tipo | Obligatorio | Descripción y cita |
|---|---|---|---|
| `id` | cadena | sí | Identificador. Único en la lista. **[Decisión propia]** |
| `cargos` | lista de valores de la tabla siguiente, sin repetir | sí | Cargos que tiene la persona **en la fecha de la decisión**. Puede tener varios: el AMLR lo prevé (art. 11.7: las funciones del director y del responsable del cumplimiento normativo «podrán ser desempeñadas por la misma persona física»), y nada impide que el representante sea también el responsable del cumplimiento normativo. |

| Valor de `cargos` | Cita |
|---|---|
| `representante_servicio_ejecutivo` | Ley, art. 26 ter.1: «Los sujetos obligados designarán como representante ante el Servicio Ejecutivo de la Comisión a una persona residente en España que ejerza cargo de administración o dirección de la sociedad». RD, art. 35.1. |
| `persona_autorizada_por_el_representante` | RD, art. 35.1: «El representante podrá designar, asimismo, hasta dos personas autorizadas que actuarán bajo la dirección y responsabilidad del representante». Ver [R-10](#r-10). |
| `miembro_organo_control_interno` | Ley, art. 26 ter.4; RD, arts. 25.2 y 35.2. |
| `director_cumplimiento_normativo` | AMLR, art. 11.1: «un miembro del órgano de dirección en su función de gestión que será responsable de velar por el cumplimiento [...] (en lo sucesivo, «director de cumplimiento normativo»)». |
| `responsable_cumplimiento_normativo` | AMLR, art. 11.2: «El responsable del cumplimiento normativo también será responsable de comunicar las operaciones sospechosas a la UIF conforme al artículo 69, apartado 6». |
| `otro` | Cualquier otra persona: un analista, un empleado que revisa una alerta. **[Decisión propia]**: el modelo no distingue más cargos porque ningún artículo del registro les da un papel. |

---

## 4. Origen del examen: `origen`

El RD pide «el motivo que generó su realización» (art. 25.3). El tipo de origen importa porque algunos orígenes tienen reglas propias.

| Campo | Tipo | Obligatorio | Descripción y cita |
|---|---|---|---|
| `tipo` | valor de la tabla siguiente | sí | Qué dio lugar al examen. |
| `descripcion` | cadena | sí | El motivo, en palabras de la entidad. RD, art. 25.3: «el motivo que generó su realización». |
| `expediente_devuelto` | cadena \| `null` | sí | Con `tipo` `devolucion_servicio_ejecutivo`, el `id` del expediente cuya comunicación devolvió el Servicio Ejecutivo. Si no, `null`. Ley, art. 18.2: el Servicio Ejecutivo «devolverá la comunicación al sujeto obligado a efectos de que por éste se profundice en el examen de la operación». **[Decisión propia]**: se guarda el `id` del expediente anterior, no una copia de sus datos. |

| Valor de `tipo` | Cita | Regla que activa |
|---|---|---|
| `alerta` | RD, art. 23: «Las alertas generadas serán revisadas a efectos de determinar si procede el examen especial de la operación». | Si participó un sistema en la alerta, se recoge en §9 con `momento` `generacion_alerta` o `priorizacion_alerta`. |
| `comunicacion_interna` | RD, art. 24.1.b: un «cauce de comunicación con los órganos de control interno» para que los directivos, empleados y agentes comuniquen «cualquier hecho u operación que pudiera estar relacionado con el blanqueo de capitales o la financiación del terrorismo». | RD, art. 25.2, párrafo cuarto: la decisión final «será puesta en conocimiento del comunicante» (§8, `fecha_puesta_en_conocimiento_comunicante`). |
| `devolucion_servicio_ejecutivo` | Ley, art. 18.2, citado arriba. | `expediente_devuelto` es obligatorio (no `null`). |
| `imposibilidad_diligencia_debida` | Ley, art. 7.3: «Cuando se aprecie la imposibilidad en el curso de la relación de negocios, los sujetos obligados pondrán fin a la misma, procediendo a realizar el examen especial a que se refiere el artículo 17». AMLR, art. 69.1, párrafo segundo: se comunican también «las sospechas derivadas de la incapacidad de llevar a cabo la diligencia debida con el cliente». | Ninguna propia en el registro. |
| `otro` | Ley, art. 17: los sujetos obligados examinarán «cualquier hecho u operación, con independencia de su cuantía, que, por su naturaleza, pueda estar relacionado con el blanqueo de capitales». AMLR, art. 69.2: «cualquier hecho o información pertinente». | Ninguna. |

**[Decisión propia]** Los supuestos del RD, arts. 5.3 y 6.3 (seguros sin identificación del beneficiario, fiduciario que no declara su condición), van como `otro`: son orígenes previstos, pero el registro no les da ninguna regla propia.

---

## 5. Operativa analizada: `operativa_analizada`

| Campo | Tipo | Obligatorio | Descripción y cita |
|---|---|---|---|
| `descripcion` | cadena | sí | RD, art. 25.3: «una descripción de la operativa analizada». |
| `operaciones` | lista | sí | Las operaciones examinadas. Puede estar vacía si el examen es de un hecho y no de operaciones concretas (Ley, art. 17: «cualquier hecho u operación»; AMLR, art. 69.2: «operaciones o actividades»). |
| `intervinientes` | lista | sí | Las personas que intervienen en la operativa. Puede estar vacía por la misma razón. |

**Por qué listas además de la descripción.** RD, art. 25.1: el examen «tendrá naturaleza integral, debiendo analizar toda la operativa relacionada, todos los intervinientes en la operación y toda la información relevante». El registro del art. 25.3 solo pide una descripción, pero sin las listas no se puede decir qué operaciones e intervinientes abarcó el examen.

`operaciones[]`:

| Campo | Tipo | Obligatorio | Descripción y cita |
|---|---|---|---|
| `id` | cadena | sí | Único en la lista. **[Decisión propia]** |
| `descripcion` | cadena | sí | RD, art. 25.1. |
| `ejecutada` | booleano | sí | `false` si la operación se intentó y no se realizó. Ley, art. 18.2: «En el caso de operaciones meramente intentadas, el sujeto obligado registrará la operación como no ejecutada». AMLR, art. 69.1, párrafo segundo: se comunican todas las operaciones sospechosas, «inclusive las que queden en fase de tentativa». |

`intervinientes[]`:

| Campo | Tipo | Obligatorio | Descripción y cita |
|---|---|---|---|
| `id` | cadena | sí | Único en la lista. Un código, no un nombre. **[Decisión propia]**, por la misma razón que en §3.1. |
| `papel` | cadena | sí | Cómo interviene. RD, art. 25.1: «todos los intervinientes en la operación». Ley, art. 18.2.a: en la comunicación, el «concepto de su participación» en la operación. **[Decisión propia]**: texto libre; ningún texto da una lista cerrada de papeles. |

El modelo no recoge importes, monedas, fechas ni medios de pago de cada operación. La Ley los pide para el contenido de la comunicación (art. 18.2.c), no para el registro del examen (§11).

---

## 6. Fases, gestiones y fuentes

RD, art. 25.1: «El proceso de examen especial se realizará de modo estructurado, documentándose las fases de análisis, las gestiones realizadas y las fuentes de información consultadas». El AMLR no pide ninguna de las tres cosas (§10).

### 6.1. `fuentes[]`

| Campo | Tipo | Obligatorio | Descripción y cita |
|---|---|---|---|
| `id` | cadena | sí | Único en la lista. **[Decisión propia]** |
| `descripcion` | cadena | sí | RD, art. 25.1: «las fuentes de información consultadas». |
| `ambito` | `"sujeto_obligado"` \| `"grupo"` \| `"externa"` | sí | De dónde procede la información. RD, art. 25.1: «toda la información relevante obrante en el sujeto obligado y, en su caso, en el grupo empresarial». AMLR, art. 69.2: «cualquier hecho o información pertinente de que tengan conocimiento o estén en su posesión». `externa` recoge lo que la entidad conoce sin tenerlo (un registro público, por ejemplo), que el AMLR incluye y el RD no menciona. |

**Un sistema de IA no es una fuente de esta lista.** **[Decisión propia]** Su participación se recoge aparte (§9) y se enlaza desde las fases y las circunstancias con `participaciones_ia`. Así se ve dónde entró su salida sin mezclarla con la información del cliente.

### 6.2. `fases[]`

| Campo | Tipo | Obligatorio | Descripción y cita |
|---|---|---|---|
| `id` | cadena | sí | Único en la lista. **[Decisión propia]** |
| `descripcion` | cadena | sí | RD, art. 25.1: «las fases de análisis». |
| `gestiones` | lista de cadenas | sí | RD, art. 25.1: «las gestiones realizadas». Puede estar vacía. |
| `fuentes` | lista de `id` de `fuentes` | sí | Las fuentes consultadas en esta fase. RD, art. 25.1. Puede estar vacía. |
| `participaciones_ia` | lista de `id` de `participaciones_ia` | sí | Las participaciones de un sistema en esta fase (§9). Puede estar vacía. **[Decisión propia]**: el RD no menciona los sistemas de IA; el enlace sirve para ver en qué fase entró la salida. |

El orden de la lista es el de las fases. **[Decisión propia]** No se piden fechas por fase: ningún texto las exige.

---

## 7. Circunstancias consideradas, conclusión y razones

### 7.1. `circunstancias_consideradas[]`

AMLR, art. 77.1.b: las entidades conservarán «un registro de la evaluación realizada de conformidad con el artículo 69, apartado 2, incluida la información y las circunstancias consideradas y los resultados de dicha evaluación». El art. 69.2, párrafo segundo, enumera en qué se basa una sospecha: «las características del cliente y sus contrapartes, la cuantía y la naturaleza de la operación o la actividad o sus métodos y patrones, la relación entre varias operaciones o actividades, el origen, el destino o el uso de fondos o cualquier otra circunstancia conocida por la entidad obligada».

| Campo | Tipo | Obligatorio | Descripción y cita |
|---|---|---|---|
| `id` | cadena | sí | Único en la lista. **[Decisión propia]** |
| `descripcion` | cadena | sí | AMLR, art. 77.1.b: «las circunstancias consideradas». |
| `fuentes` | lista de `id` de `fuentes` | sí | De qué información sale la circunstancia. AMLR, art. 77.1.b: «la información [...] considerada». Puede estar vacía. |
| `participaciones_ia` | lista de `id` de `participaciones_ia` | sí | Si la circunstancia es, o incluye, la salida de un sistema. Puede estar vacía. Si la salida de un sistema debe figurar aquí aunque la entidad diga que no la tuvo en cuenta es [R-1](#r-1). |

**[Decisión propia]** Las circunstancias no se clasifican en las categorías del art. 69.2. El artículo dice en qué se basa una sospecha, no que la entidad deba clasificar sus circunstancias. Clasificarlas sería añadir un campo que la norma no pide.

### 7.2. `conclusion`

| Campo | Tipo | Obligatorio | Descripción y cita |
|---|---|---|---|
| `texto` | cadena | sí | RD, art. 25.3: «la conclusión alcanzada tras el examen». Ley, art. 17: «reseñando por escrito los resultados del examen». AMLR, art. 77.1.b: «los resultados de dicha evaluación». |
| `razones` | lista, al menos una | sí | RD, art. 25.3: «las razones en que se basa». |

`razones[]`:

| Campo | Tipo | Obligatorio | Descripción y cita |
|---|---|---|---|
| `descripcion` | cadena | sí | RD, art. 25.3. |
| `circunstancias` | lista de `id` de `circunstancias_consideradas` | sí | En qué circunstancias se apoya la razón. Puede estar vacía. **[Decisión propia]**: el enlace permite ver si la salida de un sistema llegó a las razones de la conclusión, sin modelar nada del sistema. |

**[Decisión propia]** La conclusión es texto, no un valor de una lista cerrada. Los dos regímenes usan términos distintos: el RD, «indicios o certeza» (arts. 25.2 y 26.1); la Ley, «conozca, sospeche o tenga motivos razonables para sospechar» (art. 18.1); el AMLR, «sepa, sospeche o tenga motivos razonables para sospechar» (art. 69.1.a). Una lista cerrada obligaría a traducir los de un régimen a los del otro, y ningún texto da esa equivalencia. El sentido de la decisión va en `decision_comunicacion.comunicar` (§8).

---

## 8. Decisión sobre la comunicación: `decision_comunicacion`

| Campo | Tipo | Obligatorio | Descripción y cita |
|---|---|---|---|
| `comunicar` | booleano | sí | RD, art. 25.3: «la decisión sobre su comunicación o no al Servicio Ejecutivo de la Comisión». AMLR, art. 77.1.b: el registro se lleva «con independencia de que dicha evaluación dé lugar o no a una comunicación de operaciones sospechosas a la UIF». |
| `fecha` | fecha | sí | RD, art. 25.3: la decisión «y su fecha». |
| `motivacion` | cadena | sí | RD, art. 25.2: la decisión se adopta «motivadamente», y «haciéndose constar la motivación en el expediente de examen especial». |
| `decisor` | objeto | sí | Quién decidió. Ver §8.1. |
| `comunicacion` | objeto \| `null` | sí | La comunicación hecha. `null` si no se comunicó. Ver §8.2. |
| `fecha_puesta_en_conocimiento_comunicante` | fecha \| `null` | sí | Con `origen.tipo` `comunicacion_interna`, el día en que se informó de la decisión a quien comunicó. `null` si no se ha informado o si el origen es otro. RD, art. 25.2, párrafo cuarto: «En aquellos supuestos en que la detección de la operación derive de la comunicación interna de un empleado, agente o directivo de la entidad, la decisión final adoptada sobre si procede o no la comunicación por indicio de la operación, será puesta en conocimiento del comunicante». |

**[Decisión propia]** `comunicar` es `true` también si se comunicó solo una parte de la operativa. El registro no recoge la decisión operación por operación: el RD habla de una decisión por expediente (art. 25.3).

**Lo que la decisión no incluye.** La decisión sobre la continuación o interrupción de la relación de negocios forma parte del contenido de la comunicación (RD, art. 26.3), no del registro del examen. Tampoco se recogen las medidas adicionales de mitigación del RD, art. 26.2 (§11).

### 8.1. `decisor`

| Campo | Tipo | Obligatorio | Descripción y cita |
|---|---|---|---|
| `tipo` | `"persona"` \| `"organo_control_interno"` \| `"otro_organo_colegiado"` | sí | Ver la tabla siguiente. |
| `persona` | `id` de `personas` \| `null` | sí | Con `tipo` `persona`, quién decidió. Si no, `null`. |
| `votos` | lista \| `null` | sí | Con un órgano colegiado, el voto de cada miembro. `null` con `tipo` `persona`, o si el acta no recoge los votos uno por uno. |

| Valor de `tipo` | Cita |
|---|---|
| `persona` | RD, art. 25.2, párrafo primero: «el representante ante el Servicio Ejecutivo de la Comisión adoptará [...] la decisión». Quién decide con el AMLR es [R-4](#r-4); el modelo recoge la persona y sus cargos (§3.1), sin presuponer cuál debe ser. |
| `organo_control_interno` | RD, art. 25.2, párrafo segundo: «el procedimiento de control interno del sujeto obligado podrá prever que la decisión sea sometida, previamente, a la consideración del órgano de control interno. En estos casos, el órgano de control interno adoptará la decisión por mayoría, debiendo constar expresamente en el acta, el sentido y motivación del voto de cada uno de los miembros». |
| `otro_organo_colegiado` | Un órgano distinto del de control interno. Ningún texto lo prevé para esta decisión, pero es un hecho posible, por ejemplo con el AMLR, que no dice quién decide ([R-4](#r-4)). **[Decisión propia]** |

`votos[]`:

| Campo | Tipo | Obligatorio | Descripción y cita |
|---|---|---|---|
| `persona` | `id` de `personas` | sí | El miembro que vota. RD, art. 25.2: «cada uno de los miembros». No se repite en la lista. |
| `sentido` | `"comunicar"` \| `"no_comunicar"` \| `"abstencion"` | sí | RD, art. 25.2: «el sentido [...] del voto». **[Decisión propia]**: `abstencion` no está en el texto, pero es un hecho que puede constar en un acta. Cómo cuenta para la mayoría es [R-8](#r-8). |
| `motivacion` | cadena \| `null` | sí | RD, art. 25.2: «y motivación del voto». `null` si el acta no la recoge: es un hecho que el cálculo debe ver, no un error de entrada. |

**[Decisión propia]** La entrada no dice si la decisión se tomó por mayoría: se deduce de los votos. Si los votos contradicen `comunicar`, la entrada no se rechaza: es un hecho que el cálculo debe señalar (§12, V-9).

### 8.2. `comunicacion`

| Campo | Tipo | Obligatorio | Descripción y cita |
|---|---|---|---|
| `fecha` | fecha | sí | RD, art. 25.3: «la fecha en que, en su caso, se realizó la comunicación». Con la fecha de la decisión, permite comprobar el «sin dilación» de la Ley, art. 18.2. |
| `referencia_copia` | cadena \| `null` | sí | Referencia a la copia conservada de la comunicación. AMLR, art. 77.1.b: el registro incluye «una copia de las comunicaciones, si las hay, de sospechas de operaciones». `null` si no consta. **[Decisión propia]**: se guarda una referencia, no el documento; el AMLR, art. 77.2, permite a la entidad conservar «las referencias a dicha información» en lugar de copias, con condiciones. |

Con `comunicar` `false`, `comunicacion` es `null`. Con `comunicar` `true`, `comunicacion` puede ser `null` si la comunicación todavía no se ha hecho: es un hecho que el cálculo debe ver (§12, V-8).

---

## 9. Participación de sistemas de IA: `participaciones_ia[]`

### 9.1. Qué se recoge y qué no

**Qué es aquí un «sistema de IA».** **[Decisión propia]** Cualquier sistema que produzca una salida usada en el examen, dentro de lo que describe el AMLR, art. 76.5: «decisiones resultantes de procesos automatizados, incluida la elaboración de perfiles [...], o de procesos que impliquen sistemas de inteligencia artificial con arreglo a la definición que figura en el artículo 3, punto 1, del Reglamento (UE) 2024/XXX». El art. 76.5 da el mismo trato a los procesos automatizados y a los sistemas de IA, y el RD, art. 23, habla de «modelos automatizados». Distinguirlos exigiría mirar dentro del sistema, que la regla 2 del §0.2 prohíbe. Qué reglamento es el «2024/XXX» es [R-5](#r-5).

**La caja cerrada.** De cada participación se recoge qué sistema intervino, en qué momento del examen, qué devolvió y qué hicieron las personas con esa salida. No se recogen las variables de entrada, los umbrales, las reglas, los pesos, los tipos de alerta, la versión del modelo ni ninguna explicación que el sistema dé de sí mismo (§0.2, regla 2).

**Consecuencia: el art. 76.5.a no se puede comprobar con este registro.** El art. 76.5.a exige que «los datos tratados por dichos sistemas se limiten a los datos obtenidos con arreglo al capítulo III». Comprobarlo exigiría saber qué datos recibe el sistema, es decir, sus variables. El modelo no lo recoge a propósito. Esa condición se comprueba sobre el sistema, no sobre el registro de un examen.

### 9.2. Campos

| Campo | Tipo | Obligatorio | Descripción y cita |
|---|---|---|---|
| `id` | cadena | sí | Único en la lista. **[Decisión propia]** |
| `sistema` | cadena | sí | Identificador del sistema que asigna la entidad. **[Decisión propia]**: es opaco y el modelo no le da significado. Hace falta para distinguir dos sistemas en el mismo examen y para que la salida tenga origen, como cualquier otra información considerada (RD, art. 25.1: «las fuentes de información consultadas»; AMLR, art. 77.1.b: «la información [...] considerada»). |
| `momento` | valor de la tabla siguiente | sí | En qué punto del examen se usó la salida. |
| `fecha` | fecha | sí | Día en que el sistema produjo la salida. Hace falta para comprobar que la intervención humana y la decisión son posteriores (AMLR, art. 76.5.b: la decisión debe estar «sujeta a una intervención humana significativa»). |
| `salida` | cadena | sí | La salida del sistema, **tal como la produjo**. **[Decisión propia]**: siempre una cadena, aunque el sistema devuelva un número o una etiqueta. Si el modelo aceptara un número, el cálculo podría compararlo con un umbral, y eso sería modelar el sistema. |
| `intervencion_humana` | lista | sí | Lo que hicieron las personas con la salida. Puede estar vacía: que nadie la revisara es un hecho. Ver §9.3. |

| Valor de `momento` | Cita |
|---|---|
| `generacion_alerta` | RD, art. 23, párrafo segundo: «modelos automatizados de generación y priorización de alertas». |
| `priorizacion_alerta` | RD, art. 23, párrafo segundo, citado arriba. AMLR, art. 69.2: «Cuando sea necesario, las entidades obligadas darán prioridad a su evaluación teniendo en cuenta la urgencia de la operación o actividad». |
| `analisis` | RD, art. 25.1 (fases de análisis); AMLR, art. 69.2 (la evaluación). |
| `propuesta_decision` | El sistema propone comunicar o no comunicar. AMLR, art. 76.5: «decisiones resultantes de procesos automatizados [...] o de procesos que impliquen sistemas de inteligencia artificial». Si el art. 76.5 alcanza la decisión de comunicar es [R-2](#r-2). |

**[Decisión propia]** Un sistema que participa en dos momentos del mismo examen da dos participaciones con el mismo `sistema`.

### 9.3. `intervencion_humana[]`

| Campo | Tipo | Obligatorio | Descripción y cita |
|---|---|---|---|
| `persona` | `id` de `personas` | sí | Quién intervino. |
| `fecha` | fecha | sí | Cuándo. Ver `fecha` en §9.2. |
| `descripcion` | cadena | sí | Qué hizo con la salida. RD, art. 23, párrafo primero: las alertas generadas «serán revisadas». AMLR, art. 76.5.b: «intervención humana significativa para garantizar la exactitud y adecuación de dicha decisión». |

**[Decisión propia]** La descripción es texto libre. El modelo no clasifica la intervención (confirmar, descartar, modificar) ni dice si fue «significativa»: eso es una valoración, no un hecho de la entrada.

---

## 10. Qué exige cada régimen y cuál no tiene el otro

«Ley/RD» es el régimen de la Ley 10/2010 y el RD 304/2014; «AMLR», el del Reglamento (UE) 2024/1624. «—» quiere decir que ese régimen no lo pide.

| Dato | Ley/RD | AMLR | Campo |
|---|---|---|---|
| Obligación de dejar constancia | Ley, art. 17: «reseñando por escrito los resultados del examen». RD, art. 25.3: «mantendrán un registro en el que, por orden cronológico, se recogerán para cada expediente». | Art. 77.1.b: «un registro de la evaluación realizada de conformidad con el artículo 69, apartado 2». | todo el JSON |
| Fechas de apertura y cierre | RD, art. 25.3. | — | `fecha_apertura`, `fecha_cierre` |
| Fin del análisis técnico | RD, art. 25.2: la decisión, «sin demora» tras el análisis técnico. | — | `fecha_fin_analisis_tecnico` |
| Motivo u origen | RD, art. 25.3: «el motivo que generó su realización». | — | `origen` |
| Descripción de la operativa | RD, art. 25.3. | — (art. 69.2 dice qué se evalúa, pero el art. 77.1.b no pide describirlo) | `operativa_analizada.descripcion` |
| Operativa e intervinientes completos | RD, art. 25.1: «toda la operativa relacionada, todos los intervinientes». | — | `operaciones`, `intervinientes` |
| Operación intentada y no ejecutada | Ley, art. 18.2: «registrará la operación como no ejecutada». | Art. 69.1: se comunican «inclusive las que queden en fase de tentativa». No pide registrarlo así. | `operaciones[].ejecutada` |
| Fases, gestiones y fuentes | RD, art. 25.1. | — (art. 69.2: la evaluación se basa en «cualquier hecho o información pertinente», sin exigir que se documenten fases) | `fases`, `fuentes` |
| Información del grupo | RD, art. 25.1: «en su caso, en el grupo empresarial». | — | `fuentes[].ambito` |
| Información y circunstancias consideradas | — (el RD pide las fuentes y las razones, no las circunstancias como tales) | Art. 77.1.b: «la información y las circunstancias consideradas». | `circunstancias_consideradas` |
| Conclusión | RD, art. 25.3: «la conclusión alcanzada». | Art. 77.1.b: «los resultados de dicha evaluación». | `conclusion.texto` |
| Razones de la conclusión | RD, art. 25.3: «las razones en que se basa». | — | `conclusion.razones` |
| Decisión de comunicar o no | RD, art. 25.3. | Art. 77.1.b: «con independencia de que dicha evaluación dé lugar o no a una comunicación». | `decision_comunicacion.comunicar` |
| Fecha de la decisión | RD, art. 25.3. | — | `decision_comunicacion.fecha` |
| Motivación de la decisión | RD, art. 25.2: «motivadamente». | — | `decision_comunicacion.motivacion` |
| Quién decide | RD, art. 25.2: el representante, o el órgano de control interno si el procedimiento lo prevé. | — (arts. 11.2 y 69.6: el responsable del cumplimiento normativo comunica y remite; ninguno dice quién decide: [R-4](#r-4)) | `decisor` |
| Votos de un órgano colegiado | RD, art. 25.2: «el sentido y motivación del voto de cada uno de los miembros». | — | `decisor.votos` |
| Criterios homogéneos | RD, art. 25.2: «Las decisiones sobre comunicación deberán responder, en todo caso, a criterios homogéneos». Se comprueba entre expedientes, no en uno (§11). | — | — |
| Fecha de la comunicación | RD, art. 25.3. | — | `comunicacion.fecha` |
| Copia de la comunicación | — | Art. 77.1.b: «una copia de las comunicaciones, si las hay». | `comunicacion.referencia_copia` |
| Informar al comunicante interno | RD, art. 25.2, párrafo cuarto. | — | `fecha_puesta_en_conocimiento_comunicante` |
| Número anual de operaciones | RD, art. 23: más de 10.000, modelos automatizados obligatorios. | — | `sujeto.operaciones_anuales` |
| Revisión de las alertas | RD, art. 23: «Las alertas generadas serán revisadas». | — | `intervencion_humana` con `momento` de alerta |
| Uso de aplicaciones informáticas | Ley, art. 17: el procedimiento incluirá «la utilización de aplicaciones informáticas apropiadas». No exige intervención humana sobre sus resultados. | Art. 76.5: condiciones para las decisiones de procesos automatizados o de sistemas de IA. | `participaciones_ia` |
| Intervención humana significativa | — | Art. 76.5.b, para las decisiones que enumera ([R-2](#r-2)). | `intervencion_humana` |
| Datos limitados al capítulo III | — | Art. 76.5.a. **No se recoge** (§9.1). | — |
| Fecha de aplicación | La Ley y el RD están vigentes; ninguno de los dos textos consolidados menciona el AMLR ([R-3](#r-3)). | Art. 90: 10 de julio de 2027; 10 de julio de 2029 para las entidades del art. 3, punto 3, letras n) y o). | `sujeto.actividad` |

**Lo que resulta de la tabla.** El RD pide más datos formales del expediente (fechas, motivo, fases, fuentes, razones, quién decide, votos). El AMLR pide menos, pero pide dos cosas que el RD no tiene: las «circunstancias consideradas» y la copia de la comunicación. Y solo el AMLR pone condiciones al uso de sistemas automatizados o de IA.

**El AI Act no es un régimen de este registro.** No exige ningún campo del registro del examen. Sus obligaciones para quien despliega un sistema de alto riesgo (supervisión humana, art. 26.2; archivos de registro durante al menos seis meses, art. 26.6; explicación de decisiones, art. 86) recaen sobre el sistema y su uso, no sobre el registro de cada examen, y dependen de que el sistema sea de alto riesgo, lo que el modelo no determina (§0.2, regla 2). Se anota, sin que el modelo dependa de ello:

- Consolidado, art. 113, letra c): las reglas de los sistemas de alto riesgo del anexo III se aplican desde el 2 de diciembre de 2027.
- Anexo III, punto 5, letra b): son de alto riesgo los sistemas para «evaluar la solvencia de personas físicas o establecer su calificación crediticia, salvo los sistemas de IA utilizados al objeto de detectar fraudes financieros».
- El borrador de la Comisión, apartado 309, dice que los sistemas de prevención del blanqueo no están cubiertos por esa excepción, pero quedan fuera del punto 5.b salvo que se usen también para evaluar la solvencia: «AI systems intended to be used for anti-money laundering [...] are not covered by the exception [...]. Such systems are nevertheless out of scope to the extent their intended use does not cover the assessment of creditworthiness» [los sistemas destinados a la prevención del blanqueo no están cubiertos por la excepción; con todo, quedan fuera del ámbito en la medida en que su uso previsto no incluya la evaluación de la solvencia].
- En el apartado 2.5, el borrador pone el ejemplo de una firma que usa un sistema de detección del blanqueo para cumplir sus propias obligaciones: «will not be considered to act on behalf of law enforcement authorities» [no se considerará que actúa en nombre de las autoridades garantes del cumplimiento del Derecho], y por eso el sistema no es de alto riesgo por el punto 6 del anexo III.

Es un borrador no vinculante, y el modelo no toma nada de él.

---

## 11. Lo que no entra

Por la regla 1 del §0.2, cada omisión tiene su motivo.

| Dato | Por qué no entra |
|---|---|
| Variables, umbrales, reglas, pesos y tipos de alerta del sistema; versión del modelo; explicación que el sistema dé de su salida | Regla 2 del §0.2. |
| Si el sistema es de alto riesgo según el AI Act, o si cumple la definición de su art. 3, punto 1 | Regla 2 del §0.2. El AI Act no es un régimen de este registro (§10). |
| Si los datos del sistema se limitan al capítulo III del AMLR (art. 76.5.a) | Exige conocer las variables del sistema (§9.1). |
| Explicación al cliente e impugnación (AMLR, art. 76.5.c) | El propio artículo lo excluye para la comunicación: «excepto en relación con el informe a que se refiere el artículo 69 del presente Reglamento». |
| Si la entidad tiene implantados modelos automatizados de alertas (RD, art. 23) | Es un hecho de la configuración de sus sistemas, no del examen. El registro recoge si participó un sistema en este examen (§2.1). |
| Prioridad de la evaluación (AMLR, art. 69.2) | El artículo permite priorizar, no pide registrar la prioridad. Si un sistema priorizó, consta como participación con `momento` `priorizacion_alerta`. |
| Importes, monedas, fechas, lugares y medios de pago de cada operación | La Ley, art. 18.2.c, los pide para el contenido de la comunicación, no para el registro del examen. |
| Contenido de la comunicación: continuación o interrupción de la relación, medidas de mitigación | RD, arts. 26.2 y 26.3: son contenido o consecuencia de la comunicación, no del registro. |
| Si las decisiones responden a «criterios homogéneos» (RD, art. 25.2) | Se comprueba comparando expedientes, no dentro de uno. |
| Plazo de conservación del expediente (RD, art. 25.4: diez años; AMLR, art. 77.3: cinco años desde el fin de la relación o la operación) | Es otro cálculo, el de `plazos-conservacion-pbc`. |
| Información compartida en asociaciones para el intercambio de información (AMLR, art. 75.4.g: la información generada con IA «solo podrá compartirse cuando dichos procesos hayan sido objeto de una supervisión humana adecuada») | Regula el intercambio entre entidades, no el registro del examen. |
| Nombres u otros datos de identidad de las personas y de los intervinientes | Ningún artículo del registro exige identificarlas por nombre para lo que el modelo necesita (§3.1, §5). |
| Fechas de cada fase | Ningún texto las exige (§6.2). |

---

## 12. Validación

La validación no depende del régimen (§0.1, principio 3). Todas las reglas son **[Decisión propia]**. Los códigos de error se fijarán al implementar la carga.

| Id | Regla | Motivo |
|---|---|---|
| V-1 | Un campo que el modelo no define es un error, en cualquier objeto. También `regimen`. | Un campo que el cálculo no lee pasaría como si sirviera de algo. Es la misma regla que en los repositorios anteriores de la serie. |
| V-2 | Los campos que admiten `null` se piden siempre: omitirlos es un error. | Un campo olvidado no se distingue de un `null` intencionado. |
| V-3 | `version_modelo` debe ser `1`. Las fechas deben tener la forma `AAAA-MM-DD` y existir. Los enteros no admiten decimales ni booleanos. | — |
| V-4 | Los `id` son únicos dentro de su lista. `sujeto.operaciones_anuales[].anio` no se repite. Un `cargo` no se repite en una persona, ni una persona en `votos`. | — |
| V-5 | Toda referencia (`fuentes`, `participaciones_ia`, `circunstancias`, `persona`) debe apuntar a un `id` que exista en su lista. `expediente_devuelto` no se comprueba: el expediente devuelto no está en la entrada. | — |
| V-6 | `fecha_apertura` ≤ `fecha_fin_analisis_tecnico` ≤ `decision_comunicacion.fecha` ≤ `comunicacion.fecha`, y `fecha_apertura` ≤ `fecha_cierre`. | No se puede decidir antes de analizar, ni comunicar antes de decidir. No se comprueba el orden entre `fecha_cierre` y la decisión o la comunicación ([R-9](#r-9)). |
| V-7 | Coherencia del decisor: con `tipo` `persona`, `persona` no es `null` y `votos` es `null`; con un órgano colegiado, `persona` es `null`. Con `origen.tipo` `devolucion_servicio_ejecutivo`, `expediente_devuelto` no es `null`; con cualquier otro, es `null`. | Son contradicciones internas de la entrada, no hechos posibles. |
| V-8 | Con `comunicar` `false`, `comunicacion` es `null`. Con `comunicar` `true`, `comunicacion` puede ser `null`. | Comunicar sin haberlo decidido contradice la entrada. Haber decidido comunicar y no haberlo hecho todavía es un hecho que el cálculo debe ver. |
| V-9 | No se comprueba que los votos den la mayoría que refleja `comunicar`. | Es un hecho que el cálculo debe señalar, y cómo cuentan las abstenciones no está resuelto ([R-8](#r-8)). |
| V-10 | No se comprueba que `fecha_puesta_en_conocimiento_comunicante` sea `null` cuando el origen no es una comunicación interna, ni que no lo sea cuando sí lo es. | Informar a alguien que no comunicó no contradice nada, y no haber informado todavía es un hecho. |
| V-11 | No se comprueba el orden de las fechas de las participaciones y de las intervenciones humanas respecto de la apertura o de la decisión. | Una alerta es anterior a la apertura, y una intervención posterior a la decisión es precisamente lo que el cálculo tiene que poder señalar ([R-2](#r-2)). |
| V-12 | `conclusion.razones` no puede estar vacía. | El RD, art. 25.3, pide «las razones en que se basa»; una conclusión sin razones no es una conclusión registrada en ningún régimen. |

---

## 13. Casos que la norma no resuelve

<a id="r-1"></a>
### R-1. ¿Es la salida del sistema una «circunstancia considerada» del art. 77.1.b?

**Régimen.** AMLR.

**Qué dice la norma.**
- AMLR, art. 77.1.b: el registro incluye «la información y las circunstancias consideradas y los resultados de dicha evaluación».
- AMLR, art. 69.2, párrafo segundo: la sospecha se basa en características del cliente, cuantía, naturaleza, patrones, relación entre operaciones, origen y destino de los fondos, «o cualquier otra circunstancia conocida por la entidad obligada».
- Ningún texto menciona la salida de un sistema como circunstancia ni como información.

**Por qué no determina un comportamiento único.**
- Puede leerse que la salida es «información» considerada (es un dato que la entidad tiene) y, por tanto, debe constar siempre que se generó.
- Puede leerse que solo es «circunstancia considerada» si la entidad la tuvo en cuenta para su conclusión.
- O puede leerse que la salida no es una circunstancia de la operación, sino una valoración sobre ella, y que lo que se registra son las circunstancias que el sistema señaló, no su salida.
- Tampoco está claro si una salida que la entidad descartó debe constar.

**Qué hace el modelo.** Recoge todas las participaciones, con su salida, se usaran o no (§9), y deja que la entidad enlace la salida desde `circunstancias_consideradas` y desde `razones` (§7). Así se distinguen tres hechos: la salida existió; la entidad la trató como circunstancia considerada; la salida llegó a las razones de la conclusión. Cada lectura usa el que le corresponde.

<a id="r-2"></a>
### R-2. ¿Alcanza la intervención humana del art. 76.5.b a la decisión de comunicar?

**Régimen.** AMLR.

**Qué dice la norma.**
- AMLR, art. 76.5: las entidades «podrán adoptar decisiones resultantes de procesos automatizados [...] o de procesos que impliquen sistemas de inteligencia artificial», siempre que se cumplan tres condiciones.
- Letra b): «toda decisión de entablar o negarse a entablar o mantener una relación de negocios con un cliente, o de llevar a cabo o negarse a realizar una operación ocasional para un cliente, o de aumentar o reducir el alcance de las medidas de diligencia debida [...] esté sujeta a una intervención humana significativa».
- Letra c): el cliente puede obtener una explicación e impugnar la decisión, «excepto en relación con el informe a que se refiere el artículo 69 del presente Reglamento».
- Considerando 150: las entidades «deben poder adoptar procesos que permitan las decisiones individuales automatizadas, incluida la elaboración de perfiles, tal como se establece en el artículo 22 del Reglamento (UE) 2016/679».

**Por qué no determina un comportamiento único.**
- La letra b) enumera decisiones, y la de comunicar no está entre ellas. Leída como lista cerrada, la decisión de comunicar no necesita intervención humana significativa por el art. 76.5.
- Pero la letra c) excluye expresamente «el informe a que se refiere el artículo 69». Si la decisión de comunicar no fuera una de las decisiones del apartado 5, esa excepción no haría falta. Eso sugiere que el apartado 5 sí la abarca, y que la letra b) solo exige la intervención humana en las decisiones que enumera.
- Tampoco está claro si una salida con `momento` `analisis` que influye en la conclusión es ya una «decisión resultante» de un proceso automatizado, o si solo lo es cuando el sistema propone la decisión.
- Fuera del AMLR, el art. 22 del Reglamento (UE) 2016/679 puede exigir intervención humana por su cuenta. Este proyecto no lo analiza.

**Qué hace el modelo.** Recoge, para cada participación, el momento (incluido `propuesta_decision`), su fecha, y quién intervino sobre la salida, cuándo y cómo (§9). No dice si la intervención fue «significativa».

<a id="r-3"></a>
### R-3. ¿Sigue aplicándose el art. 25 del RD desde el 10 de julio de 2027?

**Régimen.** Ley/RD y AMLR, para los exámenes posteriores al 10 de julio de 2027 (o al 10 de julio de 2029, con `sujeto.actividad` de fútbol).

**Qué dice la norma.**
- AMLR, art. 90: «Será aplicable a partir del 10 de julio de 2027». Y al final: «El presente Reglamento será obligatorio en todos sus elementos y directamente aplicable en cada Estado miembro».
- El AMLR no deroga ninguna norma nacional ni tiene una disposición transitoria sobre el registro del examen.
- Ni la Ley consolidada a 21 de marzo de 2026 ni el RD consolidado a 24 de abril de 2024 mencionan el Reglamento (UE) 2024/1624.
- El AMLR pide menos datos que el RD (§10), y no dice si los Estados miembros pueden pedir más en este punto.

**Por qué no determina un comportamiento único.** Caben al menos tres lecturas:
- el art. 25 del RD deja de aplicarse, desplazado por los arts. 69 y 77 del AMLR;
- el art. 25 sigue aplicándose como norma nacional que desarrolla el examen, en lo que no contradiga el AMLR, y las dos listas de datos se suman;
- el art. 25 sigue aplicándose hasta que se derogue o se adapte, sin examinar su compatibilidad.

La respuesta cambia qué datos son obligatorios en un examen de 2028: con la primera lectura, no hacen falta ni las fechas de apertura y cierre, ni las fases, ni los votos.

**Qué hace el modelo.** Recoge los datos de los dos regímenes en todos los exámenes, sea cual sea su fecha (§0.1, principio 3). El régimen, y con él esta lectura, es un parámetro del cálculo.

<a id="r-4"></a>
### R-4. ¿Quién decide la comunicación en el AMLR?

**Régimen.** AMLR.

**Qué dice la norma.**
- AMLR, art. 11.2: el responsable del cumplimiento normativo «también será responsable de comunicar las operaciones sospechosas a la UIF conforme al artículo 69, apartado 6».
- AMLR, art. 69.6: «La persona que haya sido nombrada de conformidad con el artículo 11, apartado 2, remitirá la información a que hace referencia el apartado 1 del presente artículo a la UIF».
- AMLR, art. 69.1: la obligación de comunicar es de «Las entidades obligadas y, en su caso, sus directivos y empleados».
- AMLR, art. 11.4: las entidades garantizarán que «las decisiones del responsable del cumplimiento normativo no se vean perjudicadas o influidas indebidamente por los intereses comerciales de la entidad obligada».
- En cambio, el RD, art. 25.2, dice expresamente quién decide: el representante o, si el procedimiento lo prevé, el órgano de control interno por mayoría.

**Por qué no determina un comportamiento único.** «Comunicar» y «remitir» pueden leerse como el acto de enviar, no como la decisión de hacerlo. Con esa lectura, el AMLR no dice quién decide, y la entidad puede atribuir la decisión a quien quiera, incluido un órgano colegiado. Con la lectura contraria, ser «responsable de comunicar» implica decidir, y la decisión es del responsable del cumplimiento normativo. El art. 11.4 habla de «las decisiones del responsable», sin decir cuáles. Tampoco está claro si, con el AMLR, un órgano de control interno puede seguir decidiendo por mayoría como prevé el RD ([R-3](#r-3)).

**Qué hace el modelo.** Recoge quién decidió (una persona o un órgano, §8.1) y los cargos de cada persona en la fecha de la decisión (§3.1), incluidos los del AMLR, sin presuponer cuál debe ser el decisor.

<a id="r-5"></a>
### R-5. El «Reglamento (UE) 2024/XXX» sin rellenar del art. 76.5

**Régimen.** AMLR.

**Qué dice la norma.**
- AMLR, art. 76.5: «sistemas de inteligencia artificial con arreglo a la definición que figura en el artículo 3, punto 1, del Reglamento (UE) 2024/XXX del Parlamento Europeo y del Consejo (45)».
- Nota 45: «Reglamento (UE) 2024/XXX del Parlamento Europeo y del Consejo, de XXX, por el que se establecen normas armonizadas en materia de inteligencia artificial y se modifican los Reglamentos (CE) n.o 300/2008, [...] (Ley de Inteligencia Artificial) (pendiente de publicación en el Diario Oficial)».
- El AMLR se publicó el 19 de junio de 2024, y el AI Act, el 12 de julio de 2024, como Reglamento (UE) 2024/1689, con un título que coincide con el de la nota salvo el nombre corto («Reglamento de Inteligencia Artificial» y no «Ley de Inteligencia Artificial»).

**Por qué no determina un comportamiento único.**
- El texto publicado del AMLR no identifica el reglamento. Este proyecto solo tiene ese texto y no ha comprobado si existe una corrección de errores que rellene la referencia.
- La identificación con el Reglamento (UE) 2024/1689 es la única razonable por el título, pero es una deducción, no lo que dice el texto.
- Aunque se acepte, queda por saber si la remisión es a la definición del art. 3, punto 1, tal como se publicó o tal como esté en cada momento. El texto consolidado muestra que la definición ya cambió por la rectificación «►C1» (DO L 90802 de 9.10.2025): el original dice que el sistema «puede mostrar capacidad de adaptación tras el despliegue»; el consolidado, «pueda mostrar».

**Qué hace el modelo.** Nada depende de esto en la entrada: el modelo no clasifica el sistema (§0.2, regla 2) y trata igual a los sistemas de IA y a los demás procesos automatizados del art. 76.5 (§9.1). Se documenta porque cualquier cálculo que tenga que decir si se aplica el art. 76.5 a un sistema concreto tendrá que tomar postura.

<a id="r-6"></a>
### R-6. ¿Qué evaluación genera el registro del art. 77.1.b?

**Régimen.** AMLR, y la comparación con Ley/RD.

**Qué dice la norma.**
- AMLR, art. 77.1.b: «un registro de la evaluación realizada de conformidad con el artículo 69, apartado 2 [...], con independencia de que dicha evaluación dé lugar o no a una comunicación».
- AMLR, art. 69.2: «las entidades obligadas evaluarán las operaciones o actividades llevadas a cabo por sus clientes sobre la base de cualquier hecho o información pertinente».
- RD, art. 23: las alertas «serán revisadas a efectos de determinar si procede el examen especial». El registro del art. 25.3 es «para cada expediente de examen especial realizado». Una alerta revisada y descartada no abre expediente.

**Por qué no determina un comportamiento único.** La revisión de una alerta que se descarta puede ser ya una «evaluación» del art. 69.2, que el art. 77.1.b obliga a registrar, o solo un filtro previo a la evaluación. Con la primera lectura, el AMLR exige registrar muchos más casos que el RD, incluidos los que nunca llegarían a expediente.

**Qué hace el modelo.** La entrada describe un expediente concluido (§2). Una revisión de alerta descartada no cabe en esta versión del modelo, porque no tiene fases, conclusión razonada ni decisión sobre la comunicación en el sentido del RD. Si se adopta la primera lectura, habrá que ampliar el modelo; se deja constancia aquí para no cerrar la cuestión sin decirlo.

<a id="r-7"></a>
### R-7. ¿Qué año y qué operaciones cuentan para el umbral de 10.000 del RD, art. 23?

**Régimen.** Ley/RD.

**Qué dice la norma.** RD, art. 23: «En el caso de sujetos obligados cuyo número anual de operaciones exceda de 10.000, será preceptiva la implantación de modelos automatizados de generación y priorización de alertas».

**Por qué no determina un comportamiento único.**
- «Número anual» no dice si es el año natural en curso, el anterior o los últimos doce meses.
- No dice qué es una «operación» a estos efectos: si cuenta cada movimiento, cada operación con cliente o solo las de determinados productos.
- No dice cuándo nace la obligación si el umbral se supera a mitad de año.

**Qué hace el modelo.** Recoge el número por año tal como lo cuenta la entidad (§2.1). El criterio de cómputo es de la entidad y el modelo no lo verifica.

<a id="r-8"></a>
### R-8. Abstenciones y empates en el órgano de control interno

**Régimen.** Ley/RD.

**Qué dice la norma.** RD, art. 25.2: «el órgano de control interno adoptará la decisión por mayoría, debiendo constar expresamente en el acta, el sentido y motivación del voto de cada uno de los miembros».

**Por qué no determina un comportamiento único.** «Por mayoría» puede ser de los votos emitidos, de los presentes o de los miembros. No dice cómo cuentan las abstenciones ni qué pasa con un empate. Tampoco dice si un miembro puede abstenerse, ya que el acta debe recoger el «sentido» de su voto.

**Qué hace el modelo.** Recoge el voto de cada miembro, con `abstencion` como valor posible (§8.1). No recoge el número total de miembros del órgano: no sale de ningún artículo del registro. Por eso, la lectura «mayoría de los miembros» solo puede aplicarse si todos los miembros figuran en `votos`.

<a id="r-9"></a>
### R-9. ¿Qué cierra el expediente?

**Régimen.** Ley/RD.

**Qué dice la norma.** RD, art. 25.3: el registro recoge las «fechas de apertura y cierre», y además la fecha de la decisión y la de la comunicación. El art. 25.2 habla de la conclusión del «análisis técnico», que es otro hito.

**Por qué no determina un comportamiento único.** El cierre puede ser el fin del análisis técnico, la decisión o la comunicación. Según la lectura, un expediente cerrado puede tener todavía pendiente la decisión o la comunicación.

**Qué hace el modelo.** Recoge las cuatro fechas por separado (§3, §8) y no exige ningún orden entre el cierre y la decisión o la comunicación (§12, V-6).

<a id="r-10"></a>
### R-10. ¿Puede decidir una persona autorizada por el representante?

**Régimen.** Ley/RD.

**Qué dice la norma.**
- RD, art. 25.2: la decisión la adopta «el representante ante el Servicio Ejecutivo de la Comisión».
- RD, art. 35.1: el representante «podrá designar, asimismo, hasta dos personas autorizadas que actuarán bajo la dirección y responsabilidad del representante».

**Por qué no determina un comportamiento único.** El art. 35.1 no dice qué funciones pueden ejercer las personas autorizadas. Puede leerse que actúan en todo lo que corresponde al representante, incluida la decisión del art. 25.2, o que solo le asisten.

**Qué hace el modelo.** Recoge el cargo `persona_autorizada_por_el_representante` (§3.1), de modo que se vea cuándo decidió una persona autorizada y no el representante.
