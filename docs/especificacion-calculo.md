# Especificación del cálculo

Este documento explica cómo se comprueba, para un registro y un régimen, **si el registro está completo y qué le falta**. Un registro es un examen especial (o evaluación) o una alerta revisada y descartada. Se comprueba con la Ley 10/2010 y su Reglamento, con el AMLR y con cada lectura de la transición del 10 de julio de 2027. La entrada es el JSON de [`modelo-datos.md`](modelo-datos.md), que solo recoge hechos y no lleva régimen. No contiene código.

Siglas y fuentes: las de [`modelo-datos.md`](modelo-datos.md) (detalle y huellas en [`fuentes/FUENTES.md`](fuentes/FUENTES.md)). Las referencias «R-n» remiten a los casos que la norma no resuelve (modelo, §14). «Modelo, §n» remite a una sección de [`modelo-datos.md`](modelo-datos.md).

Convenciones:

- Las citas van entre comillas «» y son literales.
- **[D-n]** marca una decisión de este proyecto que no sale de los textos. Todas están numeradas y reunidas en el [§11](#11-índice-de-decisiones). Los números son estables: una decisión retirada conserva su número y no se reutiliza.
- **Lectura** es una interpretación posible de un texto que no se resuelve. Cada lectura tiene un identificador (por ejemplo `SC-2`). Cuando hay varias, el cálculo las devuelve todas con su resultado y no elige. Si dan estados distintos, el estado es `indeterminado`.
- **Requisito** es algo que un régimen exige que conste en el registro. Cada uno tiene un identificador (`RD-nn` para la Ley y el RD, `AM-nn` para el AMLR) y su cita.
- Ni el AI Act ni el borrador de la Comisión definen requisitos (modelo, §11). No aparecen en el cálculo.

---

## 1. Marco común

### 1.1. El régimen es un parámetro del cálculo

**[D-1]** El cálculo recibe la entrada y un **régimen**. Una ejecución completa calcula siempre los cinco regímenes sobre la misma entrada y los devuelve juntos. Ninguno es el principal ni el resultado por defecto. Es la misma decisión que D-4 en `plazos-actualizacion-pbc`.

| Régimen | Qué calcula | Sección |
|---|---|---|
| `ley_rd` | Los requisitos de la Ley y el RD, aplicados solos, en cualquier fecha. | §3 |
| `amlr` | Los requisitos del AMLR, aplicados solos, en cualquier fecha. | §4 |
| `T-1` a `T-3` | Los requisitos que se aplican al registro según cada lectura de si el art. 25 del RD sigue aplicándose desde el 10 de julio de 2027 (R-3). | §5 |

Los dos primeros sirven para comparar las normas tal como están escritas. Los tres últimos, para saber qué se exige a un registro concreto según cómo se resuelva la transición, que ningún texto resuelve.

**[D-2]** En todo el documento:

- **A** es la fecha de aplicación del AMLR (art. 90): 2027-07-10, o 2029-07-10 si `sujeto.actividad` es `agente_de_futbol` o `club_de_futbol_profesional`.
- **Fecha del registro**: en una alerta descartada, `alerta_descartada.revision.fecha`. En un expediente, la que diga la lectura FT (§5.3): `fecha_apertura` o `fecha_cierre`. Si las dos son anteriores a A, o las dos iguales o posteriores, FT no se consulta.

### 1.2. Qué se comprueba y qué no

Para cada régimen y cada combinación de lecturas, el cálculo toma los requisitos que el régimen aplica al registro y comprueba cada uno contra la entrada. Cada requisito da uno de tres resultados:

| Resultado | Significado |
|---|---|
| `cumple` | La entrada tiene lo que el requisito pide. |
| `falta` | No lo tiene. El resultado dice qué campo falta o qué dato lo incumple, con su ruta en el JSON. |
| `no_aplica` | El requisito no se aplica a este registro. Por ejemplo, informar al comunicante cuando el origen no es una comunicación interna. |

**[D-3]** Una cadena vacía o formada solo por espacios cuenta como ausente. La validación la admite (modelo, §13), porque es un hecho posible: que la entidad dejó el campo en blanco.

**[D-9]** El cálculo comprueba lo que el registro muestra. No comprueba:

- **Que el examen fuera integral** (RD, art. 25.1: «toda la operativa relacionada, todos los intervinientes»). Para eso haría falta saber qué operaciones e intervinientes existían y no se examinaron, y eso no está en la entrada.
- **Que la intervención humana fuera «significativa»** (AMLR, art. 76.5.b). Es una valoración (modelo, §9.4). El cálculo comprueba que la intervención existe y es anterior a la decisión (§4.4), y lo avisa.
- **Los plazos sin fecha fija**: el «sin demora» del RD, art. 25.2, y el «sin dilación» de la Ley, art. 18.2. No hay un número de días con el que comparar. El resultado da, como dato informativo, los días naturales que pasaron entre el fin del análisis técnico y la decisión, y entre la decisión y la comunicación.
- **La condición del AMLR, art. 76.5.a** (datos limitados al capítulo III). El modelo no la recoge (modelo, §9.1). Si hay participaciones de sistemas, el resultado lleva un aviso.

**[D-10]** Los requisitos que la validación ya garantiza (por ejemplo, las fechas de apertura y cierre del RD, art. 25.3, que son obligatorias en la entrada) se listan en el resultado como `cumple`, con la nota «garantizado por la validación». Así se ve la lista completa de lo que exige cada régimen.

### 1.3. Estados

Cada combinación de lecturas da un estado:

| Estado | Significado |
|---|---|
| `completo` | El régimen exige un registro y todos sus requisitos dan `cumple` o `no_aplica`. |
| `incompleto` | El régimen exige un registro y algún requisito da `falta`. |
| `no_exigible` | El régimen, con esa lectura, no exige ningún registro de este hecho. Solo ocurre con una alerta descartada (§3.3, §4.5). |

**[D-4]** `no_exigible` no es `completo`. Los dos quieren decir que no falta nada, pero dicen cosas distintas sobre lo que la norma exige, que es precisamente lo que pregunta R-6.

**[D-5]** El estado del régimen es el de sus combinaciones si todas coinciden, aunque les falten cosas distintas. Si no coinciden, es `indeterminado`. El resultado da siempre:

- **Lo que falta en todas las combinaciones** (las faltas seguras).
- **Lo que falta solo en algunas**, con las lecturas en que falta.

Así, un registro `incompleto` en todas las lecturas pero con faltas que dependen de la lectura no es `indeterminado`: su estado está claro, aunque no la lista de lo que falta (ejemplo 3).

### 1.4. Lecturas, combinaciones y atribución

**[D-6]** Las lecturas de dimensiones distintas se combinan todas con todas. Una dimensión solo se **consulta** si el registro la pone en juego: por ejemplo, las lecturas sobre la mayoría (MA) solo se consultan si un órgano colegiado decidió con alguna abstención. Las combinaciones que solo difieren en dimensiones no consultadas son la misma.

Las dimensiones de lectura son estas:

| Dimensión | Lecturas | Régimen | Se consulta cuando | Sección |
|---|---|---|---|---|
| Autorizado que decide (R-10) | PA-1, PA-2 | `ley_rd` | decide una persona con cargo `persona_autorizada_por_el_representante` y sin `representante_servicio_ejecutivo` | §3.1 |
| Mayoría del órgano (R-8) | MA-1, MA-2 | `ley_rd` | decide el órgano de control interno y hay alguna abstención | §3.1 |
| Salida como circunstancia (R-1) | SC-1, SC-2, SC-3 | `amlr` | hay alguna participación de un sistema | §4.3 |
| Intervención humana en la decisión de comunicar (R-2) | IH-1, IH-2, IH-3 | `amlr` | un expediente tiene una participación con `momento` `propuesta_decision`, o una salida que llega a las razones | §4.4 |
| Quién decide con el AMLR (R-4) | DC-1, DC-2 | `amlr` | siempre, en un expediente | §4.2 |
| Alerta descartada (R-6) | AD-1, AD-2 | `amlr` | siempre, en una alerta descartada | §4.5 |
| Fecha que decide la norma del expediente (R-11) | FT-1, FT-2 | `T-1` a `T-3` | `fecha_apertura` < A ≤ `fecha_cierre` | §5.3 |

Los regímenes de transición consultan también las dimensiones de `ley_rd` y `amlr` cuando aplican sus requisitos.

**[D-7] Atribución del `indeterminado`.** Se sigue el criterio de `plazos-actualizacion-pbc` (D-30): cada `indeterminado` se atribuye a las dimensiones que lo causan. **Una dimensión causa el `indeterminado` si existe alguna combinación de las demás dimensiones en la que cambiar solo esa cambia el estado.** No hay combinación de referencia, porque el cálculo no elige lecturas. Así se atribuyen también las dimensiones que solo cambian el estado junto con otra (ejemplo 3, variante b).

Para cada dimensión atribuida, el resultado da:
- los estados que da cada una de sus lecturas;
- los datos de la entrada que la ponen en juego, citados por su `id` y su ruta en el JSON (por ejemplo, la participación `IA-1` en `participaciones_ia[0]`).

Una dimensión que se consulta pero no cambia el estado en ninguna combinación no se atribuye, aunque cambie lo que falta. Se informa en «lo que falta solo en algunas» (D-5).

**Consecuencia.** Todo `indeterminado` tiene al menos una dimensión atribuida: si dos combinaciones dan estados distintos, se puede pasar de una a otra cambiando una dimensión cada vez, y en algún paso cambia el estado.

**[D-8] Salir del `indeterminado`.** Como en `plazos-actualizacion-pbc` (D-36), cada `indeterminado` se presenta como las preguntas que hay que responder. Hay una por dimensión atribuida, con su referencia (R-n y sección). Para cada respuesta posible da el estado y lo que falta, y si con ella el estado queda resuelto o sigue dependiendo de otras dimensiones. Esas otras dimensiones se calculan aplicando D-7 solo a las combinaciones compatibles con la respuesta.

---

## 2. Datos informativos

No cambian el estado. El resultado los da en todos los regímenes.

### 2.1. Días transcurridos

Con un expediente ([D-9]):
- días naturales entre `fecha_fin_analisis_tecnico` y `decision_comunicacion.fecha` (RD, art. 25.2: «sin demora»);
- días naturales entre `decision_comunicacion.fecha` y `comunicacion.fecha`, si hubo comunicación (Ley, art. 18.2: «sin dilación»; AMLR, art. 69.1: «sin demora»).

### 2.2. Umbral de operaciones del RD, art. 23 (R-7)

**[D-24]** El resultado indica si el sujeto obligado supera las 10.000 operaciones anuales del RD, art. 23, párrafo segundo. No es un requisito del registro: el modelo no recoge si la entidad tiene implantados modelos automatizados de alertas (modelo, §2.1), así que el cálculo no puede decir si cumple esa obligación. Sirve para leer el registro: con más de 10.000 operaciones, la generación y la priorización de alertas debían ser automatizadas.

Qué año cuenta no está resuelto (R-7). Dos lecturas:
- **OA-1:** el año natural anterior al de la fecha del registro.
- **OA-2:** el año natural de la fecha del registro.

Con cada lectura, el indicador es `supera` (`numero` > 10.000), `no_supera` o `sin_dato` (el año no está en `sujeto.operaciones_anuales`). Si las lecturas dan valores distintos, el indicador es `indeterminado`, atribuido a OA. En un expediente, la fecha del registro es `fecha_apertura` para este indicador, porque es cuando se revisó la alerta que lo abrió.

### 2.3. Declaración sobre los sistemas

**[D-18]** El resultado lista cada sistema con su `declaracion_sistema_ia` y las participaciones en que interviene. La declaración no cambia ningún requisito: el AMLR, art. 76.5, da el mismo trato a los procesos automatizados y a los sistemas de IA (modelo, §9.1 y §9.2). Por la misma razón, qué reglamento es el «2024/XXX» del art. 76.5 y con qué versión de la definición declara la entidad (R-5) no son dimensiones de lectura: no cambian nada en el cálculo.

---

## 3. Régimen de la Ley 10/2010 y el RD 304/2014

### 3.1. Requisitos de un expediente

| Id | Requisito | Cita | Comprobación | `no_aplica` cuando |
|---|---|---|---|---|
| RD-01 | Fechas de apertura y cierre | RD, art. 25.3 | Garantizado por la validación ([D-10]). | — |
| RD-02 | Motivo del examen | RD, art. 25.3: «el motivo que generó su realización» | `origen.descripcion` no está vacía ([D-3]). | — |
| RD-03 | Descripción de la operativa | RD, art. 25.3: «una descripción de la operativa analizada» | `operativa_analizada.descripcion` no está vacía. | — |
| RD-04 | Fases de análisis | RD, art. 25.1: «documentándose las fases de análisis» | `fases` tiene al menos un elemento, y ninguna fase tiene la `descripcion` vacía. | — |
| RD-05 | Gestiones realizadas | RD, art. 25.1: «las gestiones realizadas» | Alguna fase tiene al menos una gestión no vacía. | — |
| RD-06 | Fuentes consultadas | RD, art. 25.1: «las fuentes de información consultadas» | `fuentes` tiene al menos un elemento, y ninguna fuente tiene la `descripcion` vacía. | — |
| RD-07 | Conclusión | RD, art. 25.3: «la conclusión alcanzada tras el examen»; Ley, art. 17: «reseñando por escrito los resultados del examen» | `conclusion.texto` no está vacío. | — |
| RD-08 | Razones | RD, art. 25.3: «las razones en que se basa» | Ninguna razón tiene la `descripcion` vacía. Que haya al menos una lo garantiza la validación (modelo, §13, V-12). | — |
| RD-09 | Decisión y su fecha | RD, art. 25.3 | Garantizado por la validación. | — |
| RD-10 | Motivación de la decisión | RD, art. 25.2: «motivadamente»; «haciéndose constar la motivación en el expediente» | `decision_comunicacion.motivacion` no está vacía. | — |
| RD-11 | Decisor previsto | RD, art. 25.2 | Ver abajo. | — |
| RD-12 | Voto de cada miembro | RD, art. 25.2: «debiendo constar expresamente en el acta, el sentido y motivación del voto de cada uno de los miembros» | `decisor.votos` no es `null` ni está vacía, y ningún voto tiene `motivacion` `null` o vacía. | el decisor no es `organo_control_interno` |
| RD-13 | Mayoría | RD, art. 25.2: «adoptará la decisión por mayoría» | El sentido de `comunicar` tiene mayoría en `votos`, según MA. | el decisor no es `organo_control_interno`, o `votos` es `null` o vacía (ya falta RD-12) |
| RD-14 | Fecha de la comunicación | RD, art. 25.3: «la fecha en que, en su caso, se realizó la comunicación» | Si `comunicacion` no es `null`, su fecha la garantiza la validación. Ver [D-11]. | `comunicar` es `false` |
| RD-15 | Informar al comunicante | RD, art. 25.2, párrafo cuarto | `fecha_puesta_en_conocimiento_comunicante` no es `null`. | `origen.tipo` no es `comunicacion_interna` |

**RD-11, decisor previsto.** **[D-12]**
- `tipo` `persona`: cumple si la persona tiene el cargo `representante_servicio_ejecutivo` (RD, art. 25.2: «el representante ante el Servicio Ejecutivo de la Comisión adoptará [...] la decisión»). Si no lo tiene pero tiene `persona_autorizada_por_el_representante`, se consulta PA (R-10):
  - **PA-1:** la persona autorizada puede adoptar la decisión, porque actúa «bajo la dirección y responsabilidad del representante» (RD, art. 35.1). Cumple.
  - **PA-2:** solo puede asistirle; la decisión es del representante. Falta.

  Con cualquier otro cargo, falta.
- `tipo` `organo_control_interno`: cumple (RD, art. 25.2, párrafo segundo).
- `tipo` `otro_organo_colegiado`: falta. El RD solo prevé el representante y el órgano de control interno.

**[D-14]** Si alguna persona de `votos` no tiene el cargo `miembro_organo_control_interno`, el resultado lleva un aviso, pero RD-12 no da `falta`: el cargo es un dato que la entidad puede haber omitido, y el RD no exige que el acta lo acredite.

**RD-13, mayoría.** **[D-13]** Sean *c*, *n* y *a* el número de votos `comunicar`, `no_comunicar` y `abstencion`. El sentido de la decisión es `comunicar` si `comunicar` es `true`, y `no_comunicar` si es `false`. Si no hay abstenciones, las dos lecturas coinciden: el sentido tiene mayoría si tiene más votos que el contrario, y MA no se consulta. Con abstenciones (R-8):
- **MA-1. Mayoría de los votos emitidos.** Las abstenciones no cuentan. El sentido tiene mayoría si sus votos superan a los del contrario.
- **MA-2. Mayoría de los que votan, abstenciones incluidas.** El sentido tiene mayoría si sus votos superan la mitad de *c* + *n* + *a*.

Con empate no hay mayoría en ninguna lectura, y RD-13 da `falta`. La lectura «mayoría de los miembros del órgano» no se calcula: el modelo no recoge cuántos miembros tiene el órgano (modelo, R-8).

**[D-11] Comunicación decidida y no realizada.** Con `comunicar` `true` y `comunicacion` `null`, RD-14 da `cumple`: el RD, art. 25.3, pide la fecha de la comunicación «en su caso», es decir, si se hizo. El resultado lleva el aviso «comunicación decidida y no realizada». Es un posible incumplimiento de la obligación de comunicar «sin dilación» (Ley, art. 18.2), no un defecto del registro. Mismo aviso con el AMLR (§4.1, AM-05).

### 3.2. Lo que el régimen no comprueba en un expediente

- La revisión de la alerta que abrió el expediente (RD, art. 23): la propia apertura muestra que se revisó y se decidió examinar ([D-12]).
- Las participaciones de sistemas: el RD no pone condiciones al uso de «aplicaciones informáticas» (Ley, art. 17) ni a sus resultados. SC, IH y DC no se consultan.
- Las circunstancias consideradas y la copia de la comunicación: son del AMLR (modelo, §11).

### 3.3. Alerta descartada

**[D-20]** Con `ley_rd`, una alerta descartada es `no_exigible`. El RD, art. 23, solo exige revisar la alerta, y la revisión consta siempre en `alerta_descartada.revision`, que es obligatorio en la entrada. El registro del RD, art. 25.3, es de cada expediente, y la alerta no lo abrió.

---

## 4. Régimen del AMLR

### 4.1. Requisitos

| Id | Requisito | Cita | Expediente | Alerta descartada (con AD-2) | `no_aplica` cuando |
|---|---|---|---|---|---|
| AM-01 | Información considerada | Art. 77.1.b: «la información [...] considerada» | `fuentes` tiene al menos un elemento, o alguna circunstancia cita una participación. | Lo mismo, con las `fuentes` y las circunstancias de la alerta. | — |
| AM-02 | Circunstancias consideradas | Art. 77.1.b: «las circunstancias consideradas» | `circunstancias_consideradas` tiene al menos un elemento, y ninguno tiene la `descripcion` vacía. | Lo mismo. | — |
| AM-03 | Resultados | Art. 77.1.b: «los resultados de dicha evaluación» | `conclusion.texto` no está vacío. | `resultado` no es `null` ni está vacío. | — |
| AM-04 | Salida del sistema entre las circunstancias | Art. 77.1.b; R-1 | Según SC (§4.3). | Según SC (§4.3). | no hay participaciones |
| AM-05 | Copia de la comunicación | Art. 77.1.b: «una copia de las comunicaciones, si las hay» | `comunicacion.referencia_copia` no es `null` ni está vacía. | — | `comunicacion` es `null` (con `comunicar` `true`, aviso [D-11]) |
| AM-06 | Intervención humana antes de la decisión | Art. 76.5.b; R-2 | Según IH (§4.4). | — | IH no se consulta |
| AM-07 | Quién decide | Arts. 11.2 y 69.6; R-4 | Según DC (§4.2). | — | — |

**[D-15] AM-01.** La información considerada son las fuentes y las salidas de sistemas que la entidad trató como circunstancias. Basta una. Se cuenta la salida de un sistema como información solo si una circunstancia la cita, para no dar por considerada una salida que la entidad no enlazó a nada (si debería haberlo hecho es AM-04).

El AMLR no pide fechas de apertura y cierre, ni motivo, ni fases, ni gestiones, ni razones, ni motivación, ni votos (modelo, §11). Nada de eso se comprueba con `amlr`.

### 4.2. Quién decide (R-4)

**[D-19]** AM-07 se comprueba en todo expediente, con dos lecturas:
- **DC-1. El AMLR no dice quién decide.** Los arts. 11.2 y 69.6 hablan de «comunicar» y «remitir», que es el acto de enviar. Cumple siempre.
- **DC-2. Decide el responsable del cumplimiento normativo.** Ser «responsable de comunicar las operaciones sospechosas» (art. 11.2) incluye decidir. Cumple si `decisor.tipo` es `persona` y la persona tiene el cargo `responsable_cumplimiento_normativo`. Con un órgano colegiado, falta: el órgano puede deliberar, pero la decisión no es de la persona que el AMLR designa.

### 4.3. La salida del sistema como circunstancia considerada (R-1)

**[D-16]** AM-04 se consulta si hay alguna participación. Tres lecturas:
- **SC-1. Toda salida es información considerada.** Toda participación del registro debe estar citada por alguna circunstancia. Las que no lo están dan `falta`.
- **SC-2. Solo la salida que la entidad usó.** En un expediente, toda participación citada por una fase (`fases[].participaciones_ia`) debe estar citada por alguna circunstancia. En una alerta descartada no hay fases, y AM-04 da `cumple`. **[D-16]**: se toma la cita desde una fase como el hecho que muestra que la entidad usó la salida en el análisis; una participación solo incorporada o de origen no se considera usada.
- **SC-3. La salida no es una circunstancia.** Es una valoración sobre la operación, no una circunstancia de ella. AM-04 da `cumple`.

### 4.4. Intervención humana en la decisión de comunicar (R-2)

**[D-17]** AM-06 tiene tres lecturas:
- **IH-1. El art. 76.5.b no alcanza la decisión de comunicar.** La letra b) enumera las decisiones que exigen intervención humana significativa, y la de comunicar no está entre ellas. IH-1 no exige nada.
- **IH-2. La alcanza cuando un sistema la propone.** La excepción de la letra c) para «el informe a que se refiere el artículo 69» indica que el apartado 5 abarca esa decisión. Cada participación con `momento` `propuesta_decision` debe tener al menos una intervención humana con `fecha` ≤ `decision_comunicacion.fecha`.
- **IH-3. La alcanza también cuando la salida llega a las razones.** Además de las de IH-2, cada participación citada por una circunstancia que cita alguna razón (`conclusion.razones[].circunstancias`) debe tener una intervención humana con `fecha` ≤ `decision_comunicacion.fecha`.

IH se consulta en un expediente si IH-2 o IH-3 ponen en juego alguna participación. Si no, AM-06 da `no_aplica`.

Una intervención posterior a la decisión no cuenta: la decisión tiene que estar «sujeta» a la intervención, y una revisión posterior no la condicionó. El resultado lleva un aviso cuando hay intervenciones posteriores a la decisión, con cualquier lectura. Cuando AM-06 da `cumple` con IH-2 o IH-3, el resultado avisa de que no se ha valorado si la intervención fue «significativa» ([D-9]).

La declaración sobre el sistema no cambia AM-06 ([D-18]): un sistema declarado `no` o `desconocido` sigue siendo un proceso automatizado del art. 76.5.

### 4.5. Alerta descartada (R-6)

**[D-20]** Con `amlr`, una alerta descartada consulta siempre AD:
- **AD-1. La revisión de una alerta no es una evaluación del art. 69.2.** Estado `no_exigible`.
- **AD-2. Sí lo es.** Se comprueban AM-01 a AM-04 (§4.1). AM-05 a AM-07 no se aplican: no hay decisión sobre la comunicación (modelo, §10.1).

### 4.6. Fecha del registro anterior a A

**[D-23]** `amlr` se calcula en cualquier fecha, como comparación. Si la fecha del registro es anterior a A con las dos lecturas FT (o, en una alerta, si `revision.fecha` < A), el resultado lleva el aviso «el AMLR no era aplicable en la fecha del registro». Si `fecha_apertura` < A ≤ `fecha_cierre`, el aviso dice que el expediente abarca la fecha de aplicación (R-11).

---

## 5. Transición: el art. 25 del RD desde el 10 de julio de 2027 (R-3)

### 5.1. Lo que dicen los textos

- AMLR, art. 90: «Será aplicable a partir del 10 de julio de 2027», y «será obligatorio en todos sus elementos y directamente aplicable en cada Estado miembro».
- El AMLR no deroga el RD ni tiene una disposición transitoria sobre el registro del examen.
- Ni la Ley consolidada a 21 de marzo de 2026 ni el RD consolidado a 24 de abril de 2024 mencionan el Reglamento (UE) 2024/1624.
- El RD, art. 25, pide más datos que el AMLR, art. 77.1.b, y el AMLR pide dos que el RD no tiene (modelo, §11).

**Lo que ningún texto dice:** si, desde A, un registro tiene que cumplir los requisitos del RD, los del AMLR o los dos.

### 5.2. Lecturas

| Régimen | Idea | Fecha del registro < A | Fecha del registro ≥ A |
|---|---|---|---|
| **T-1. Desplazamiento** | El AMLR, directamente aplicable, desplaza el art. 25 del RD. | `ley_rd` | `amlr` |
| **T-2. Suma, con prevalencia del AMLR** | El art. 25 sigue como norma nacional en lo que no contradiga el AMLR. | `ley_rd` | Requisitos de `ley_rd` y de `amlr`. Si se contradicen, se aplica el del AMLR. |
| **T-3. Suma, sin examen de compatibilidad** | El art. 25 sigue hasta que se derogue o se adapte, y se aplica tal cual. | `ley_rd` | Requisitos de `ley_rd` y de `amlr`, todos. |

**[D-21] Dónde se contradicen.** Los requisitos del RD y del AMLR solo se contradicen en quién decide, y solo con DC-2: el RD admite que decida el representante o el órgano de control interno (RD-11 a RD-13), y el AMLR, con DC-2, exige que decida el responsable del cumplimiento normativo (AM-07). Por eso T-2 y T-3 solo difieren con DC-2:
- **T-2 con DC-2:** RD-11, RD-12 y RD-13 dan `no_aplica`, y rige AM-07.
- **T-3 con DC-2:** se aplican RD-11 a RD-13 y AM-07. Se cumplen a la vez si decide una persona que es representante y responsable del cumplimiento normativo.
- **Con DC-1**, T-2 y T-3 son iguales.

Los demás requisitos no se contradicen: uno pide más datos que el otro, y se pueden dar los dos. En particular, el RD no impide registrar circunstancias ni conservar la copia de la comunicación.

Notas:
- **Alerta descartada.** Con fecha < A, los tres dan `no_exigible` (`ley_rd`). Con fecha ≥ A, los tres dan el resultado de `amlr`, porque `ley_rd` no exige nada (§3.3): la suma de nada y los requisitos de AD es AD.
- **Antes de A**, los tres son `ley_rd`. Se calculan igual ([D-1]) y la comparación dice que coinciden.
- Dentro de cada T-n se aplican las lecturas de §3 y §4: una T-n puede ser `indeterminado` por sí misma.
- **[D-26]** La salida compara T-1 a T-3 y dice expresamente si no coinciden: lo que se exige al registro depende entonces de cómo se resuelva R-3. También dice si `ley_rd` y `amlr` no coinciden. Dos regímenes coinciden si dan el mismo estado y la misma lista de faltas en cada combinación.

### 5.3. Expediente abierto antes de A y cerrado después (R-11)

**[D-22]** Si `fecha_apertura` < A ≤ `fecha_cierre`, la fecha del registro tiene dos lecturas:
- **FT-1. La apertura.** El examen se rige por la norma con que empezó. Los tres T-n dan `ley_rd`.
- **FT-2. El cierre.** El registro es de la evaluación «realizada», y se completa al cerrar. Se aplica la columna «≥ A» de §5.2.

Se elige el cierre y no la decisión porque es la fecha que el propio RD registra como fin del expediente. Qué hecho cierra el expediente no está resuelto (R-9), pero el cálculo no lo necesita: usa la fecha que la entidad declara.

---

## 6. Resumen: qué requisito aplica cada régimen

| Requisito | `ley_rd` | `amlr` | T-1 (≥ A) | T-2 (≥ A) | T-3 (≥ A) |
|---|---|---|---|---|---|
| RD-01 a RD-10, RD-14, RD-15 | sí | — | — | sí | sí |
| RD-11 a RD-13 | sí | — | — | sí con DC-1; `no_aplica` con DC-2 | sí |
| AM-01 a AM-06 | — | sí | sí | sí | sí |
| AM-07 | — | sí | sí | sí | sí |
| Alerta descartada | `no_exigible` | AD | AD | AD | AD |

Antes de A, T-1 a T-3 son `ley_rd`.

---

## 7. Ejemplos

Salvo que se indique otra cosa: `sujeto.actividad = "otra"` (A = 2027-07-10), y los campos que no se mencionan cumplen su requisito. En las tablas, «cumple» y «falta» son el resultado del requisito y los estados van en `código`.

### Ejemplo 1. El expediente del modelo, §1.1

Apertura 2027-09-06, cierre 2027-09-29: todo después de A, así que FT no se consulta. Decide el órgano de control interno: P-1 y P-2 votan `comunicar`, P-3 `no_comunicar`, sin abstenciones. Participaciones: IA-1 (origen, generación de la alerta) e IA-2 (análisis, en la fase FA-1 y en la circunstancia C-3, que cita la razón 2). Comunicación del 2027-09-28 con copia `DOC-EJEMPLO-0001`.

**`ley_rd`.** RD-01 a RD-14 cumplen. MA no se consulta, porque no hay abstenciones; 2 votos contra 1 es mayoría. RD-15 `no_aplica` (el origen es una alerta). Estado: `completo`.

**`amlr`.**
- AM-01, AM-02, AM-03 y AM-05 cumplen.
- AM-04: IA-2 está citada por C-3. IA-1 no la cita ninguna circunstancia. SC-1: falta (IA-1). SC-2: IA-2 es la única citada por una fase, y C-3 la cita: cumple. SC-3: cumple.
- AM-06: no hay `propuesta_decision`. Con IH-3, IA-2 llega a las razones (razón 2 → C-3 → IA-2), y su intervención del 2027-09-12 es anterior a la decisión del 2027-09-27: cumple. AM-06 cumple con las tres lecturas, así que IH no cambia nada. Aviso: no se ha valorado si la intervención fue «significativa».
- AM-07: el decisor es un órgano. DC-1: cumple. DC-2: falta.

| | DC-1 | DC-2 |
|---|---|---|
| SC-1 | `incompleto` (AM-04) | `incompleto` (AM-04, AM-07) |
| SC-2 | `completo` | `incompleto` (AM-07) |
| SC-3 | `completo` | `incompleto` (AM-07) |

Estado: `indeterminado`, atribuido a SC (con DC-1, pasar de SC-2 a SC-1 cambia el estado) y a DC (con SC-2, pasar de DC-1 a DC-2 lo cambia). Datos que las ponen en juego: `participaciones_ia` IA-1 (SC) y `expediente.decision_comunicacion.decisor` (DC).

Para salir del `indeterminado`:
- «¿La salida de un sistema es una circunstancia considerada aunque la entidad no la enlace? (R-1, §4.3)». Con SC-1, `incompleto`: resuelto. Con SC-2 o SC-3, aún depende de DC.
- «¿Quién decide la comunicación con el AMLR? (R-4, §4.2)». Con DC-2, `incompleto`: resuelto. Con DC-1, aún depende de SC.

**T-1:** `amlr`. **T-2** y **T-3:** con DC-1, RD-01 a RD-15 cumplen y el resultado es el de `amlr`; con DC-2, AM-07 falta en los dos. Los tres dan la misma tabla: `indeterminado` (SC, DC).

Datos informativos: 3 días entre el fin del análisis y la decisión, 1 día entre la decisión y la comunicación. Umbral de operaciones: con OA-1 (2026, 18.450) `supera`; con OA-2 (2027) `sin_dato`: el indicador es `indeterminado`, atribuido a OA.

### Ejemplo 2. La alerta descartada del modelo, §1.2

Alerta revisada el 2027-10-05, con una fuente (F-1), una circunstancia (C-1, que cita F-1 e IA-1) y resultado.

- `ley_rd`: `no_exigible`.
- `amlr`: AD-1 `no_exigible`. AD-2: AM-01 (F-1), AM-02 (C-1) y AM-03 cumplen; AM-04 cumple con las tres lecturas SC, porque C-1 cita IA-1. `completo`. Estado: `indeterminado`, atribuido a AD. En ninguna lectura falta nada.
- T-1 a T-3: la fecha es ≥ A, así que dan el resultado de `amlr`.

**Variante: la alerta sin nada más que la revisión.** Misma alerta, pero con `fuentes` y `circunstancias_consideradas` vacías y `resultado` `null`, revisada el **2028-05-10**.
- `ley_rd`: `no_exigible`.
- `amlr`: AD-1 `no_exigible`; AD-2 `incompleto` (faltan AM-01, AM-02 y AM-03; AM-04 falta con SC-1, porque ninguna circunstancia cita IA-1). Estado: `indeterminado`, atribuido a AD.
- T-1 a T-3: lo mismo que `amlr`.

Con la misma alerta revisada el **2026-11-10**, T-1 a T-3 dan `no_exigible` (`ley_rd`), y `amlr` lleva el aviso de que el AMLR no era aplicable ([D-23]).

### Ejemplo 3. Expediente que abarca la fecha de aplicación, con una alerta incorporada

- Origen: `comunicacion_interna`, sin participaciones.
- Apertura **2027-06-21**; fin del análisis 2027-07-14; decisión **2027-07-16**, `comunicar` `false`; cierre **2027-07-19**.
- `fecha_puesta_en_conocimiento_comunicante`: `null`.
- Participación IA-5, generación de una alerta del 2027-06-28 sobre la misma operativa, en `participaciones_incorporadas` (es el caso de V-17 del modelo). No la cita ninguna fase ni circunstancia.
- Una fuente, F-1. `circunstancias_consideradas` vacía.
- Decide P-1, con los cargos `representante_servicio_ejecutivo` y `responsable_cumplimiento_normativo`.

**`ley_rd`:** falta RD-15 (no se ha informado al comunicante). `incompleto`.

**`amlr`:** falta AM-02 (no hay circunstancias) con todas las lecturas. AM-04: con SC-1 falta (IA-5 no está en ninguna circunstancia); con SC-2 cumple (IA-5 no está en ninguna fase). AM-05 `no_aplica`. AM-06 `no_aplica` (IH no se consulta). AM-07 cumple con las dos lecturas DC. Estado: `incompleto`. Falta en todas las combinaciones: AM-02. Solo con SC-1: AM-04. SC se consulta pero no se atribuye, porque no cambia el estado ([D-7]).

**T-1 a T-3:** `fecha_apertura` < A ≤ `fecha_cierre`, así que se consulta FT.

| | FT-1 (apertura) | FT-2 (cierre) |
|---|---|---|
| T-1 | `incompleto` (RD-15) | `incompleto` (AM-02; AM-04 con SC-1) |
| T-2 | `incompleto` (RD-15) | `incompleto` (RD-15, AM-02; AM-04 con SC-1) |
| T-3 | `incompleto` (RD-15) | `incompleto` (RD-15, AM-02; AM-04 con SC-1) |

Los tres dan `incompleto` en todas las lecturas. Lo que falta depende de FT, y el resultado lo dice, pero el estado no es `indeterminado`. Aviso en `amlr`: el expediente abarca la fecha de aplicación ([D-23]). T-1 no coincide con T-2 y T-3 porque sus faltas son distintas ([D-26]).

**Variante b: dos dimensiones que solo cambian el estado juntas.** El mismo expediente, pero la entidad informó al comunicante el 2027-07-20 y registró una circunstancia C-1 que cita F-1. Ahora:
- `ley_rd`: `completo`.
- `amlr`: con SC-1 falta AM-04 (IA-5 no está en ninguna circunstancia): `incompleto`. Con SC-2 y SC-3: `completo`. Estado: `indeterminado`, atribuido a SC.
- T-1:

  | | FT-1 | FT-2 |
  |---|---|---|
  | SC-1 | `completo` | `incompleto` (AM-04) |
  | SC-2 | `completo` | `completo` |
  | SC-3 | `completo` | `completo` |

  - Con SC-2 como referencia, cambiar FT no cambiaría nada. Pero con SC-1, pasar de FT-1 a FT-2 cambia el estado: FT se atribuye.
  - Con FT-1 como referencia, cambiar SC no cambiaría nada. Pero con FT-2, pasar de SC-2 a SC-1 lo cambia: SC se atribuye.

  El `indeterminado` se atribuye a las dos. Para salir de él: con FT-1, `completo` (resuelto); con FT-2, aún depende de SC.
- T-2 y T-3: igual que T-1, porque con FT-2 los requisitos del RD se cumplen todos.

### Ejemplo 4. Un sistema propone la decisión y nadie revisa su salida

Expediente de 2028, apertura 2028-02-14, decisión **2028-03-03**, `comunicar` `true`, comunicación del 2028-03-06 con copia. Decide P-1 (representante y responsable del cumplimiento normativo). Participación IA-7 del sistema SIS-C (declarado `desconocido`), `momento` `propuesta_decision`, 2028-03-01, `intervencion_humana` vacía. IA-7 está citada por la fase FA-2 y por la circunstancia C-2. La única razón cita C-1, que cita F-1.

- `ley_rd`: `completo`. El RD no pone condiciones a la salida del sistema.
- `amlr`: AM-01 a AM-05 cumplen (AM-04 con las tres SC, porque C-2 cita IA-7). AM-07 cumple con las dos DC. AM-06: con IH-1 cumple; con IH-2 falta (IA-7 propone la decisión y no tiene intervención humana); con IH-3 falta (incluye las de IH-2). Estado: `indeterminado`, atribuido a IH.
- T-1 a T-3: con IH-1 `completo`, con IH-2 e IH-3 `incompleto` (AM-06). `indeterminado` (IH).

Que SIS-C esté declarado `desconocido` no cambia nada ([D-18]). El resultado lleva el aviso de que el art. 76.5.a no se comprueba.

**Variante: intervención después de la decisión.** Con una intervención de P-4 el 2028-03-05, AM-06 sigue dando `falta` con IH-2 e IH-3, porque es posterior a la decisión, y el resultado añade el aviso de intervención posterior ([D-17]).

### Ejemplo 5. Una abstención en el órgano de control interno, antes de A

Expediente de 2026 (apertura 2026-04-06, cierre 2026-05-04). Decide el órgano de control interno. Votos: P-1 y P-2 `comunicar`, P-3 `no_comunicar`, P-5 `abstencion`, todos motivados. `comunicar` `true`.

RD-13: *c* = 2, *n* = 1, *a* = 1. Con MA-1, 2 > 1: hay mayoría. Con MA-2, 2 no supera la mitad de 4: no la hay.

- `ley_rd`: MA-1 `completo`, MA-2 `incompleto` (RD-13). Estado: `indeterminado`, atribuido a MA.
- T-1 a T-3: la fecha es anterior a A, así que son `ley_rd`: `indeterminado` (MA).
- `amlr`: se calcula con el aviso de que no era aplicable ([D-23]). Con DC-2 falta AM-07, porque decidió un órgano.

### Ejemplo 6. Las lecturas de la transición no coinciden

Expediente de **2028** en el que decide P-6, que solo tiene el cargo `responsable_cumplimiento_normativo`. No es el representante ante el Servicio Ejecutivo. No hay participaciones de sistemas. Todo lo demás cumple los requisitos de los dos regímenes.

- `ley_rd`: falta RD-11 (el decisor no es el representante; PA no se consulta, porque P-6 no es persona autorizada). `incompleto`.
- `amlr`: DC-1 cumple; DC-2 cumple (P-6 es el responsable). `completo`.
- T-1: `amlr`, `completo`.
- T-2: con DC-1 se suman los requisitos y falta RD-11: `incompleto`. Con DC-2 prevalece AM-07 y RD-11 da `no_aplica`: `completo`. Estado: `indeterminado` (DC).
- T-3: falta RD-11 con las dos lecturas DC: `incompleto`.

La salida dice que T-1 a T-3 no coinciden ([D-26]). Qué se exige a este registro depende de R-3, y con T-2 también de R-4.

---

## 8. Relación con cada caso no resuelto

| Caso | Cómo lo trata el cálculo | Sección |
|---|---|---|
| R-1 | Dimensión SC en AM-04. | §4.3 |
| R-2 | Dimensión IH en AM-06. | §4.4 |
| R-3 | Regímenes T-1 a T-3. | §5 |
| R-4 | Dimensión DC en AM-07, y diferencia entre T-2 y T-3. | §4.2, §5.2 |
| R-5 | No es dimensión: no cambia nada ([D-18]). | §2.3 |
| R-6 | Dimensión AD. | §4.5 |
| R-7 | Dimensión OA, solo en un dato informativo. | §2.2 |
| R-8 | Dimensión MA en RD-13. | §3.1 |
| R-9 | No es dimensión: el cálculo usa `fecha_cierre` tal como la declara la entidad. | §5.3 |
| R-10 | Dimensión PA en RD-11. | §3.1 |
| R-11 | Dimensión FT en T-1 a T-3. | §5.3 |

---

## 9. Salida

El resultado tiene una entrada por régimen, con:

- `estado`: uno de los de §1.3, o `indeterminado`.
- `requisitos`: cada requisito que el régimen aplica, con su cita y su resultado (`cumple`, `falta`, `no_aplica`), y si depende de la lectura, el resultado con cada una.
- `faltas_seguras` y `faltas_segun_lectura` ([D-5]), con las rutas de los campos.
- `lecturas`: una entrada por combinación que da un resultado distinto, con sus identificadores, su estado y sus faltas.
- `indeterminado`: si lo es, las dimensiones atribuidas ([D-7]) y las preguntas para salir de él ([D-8]).
- `avisos`.

Además, fuera de los regímenes: los datos informativos (§2) y la comparación de [D-26].

El informe empieza con la advertencia de que es un cálculo bajo las lecturas que declara esta especificación, no una determinación jurídica.

### 9.1. Códigos de salida

| Código | Cuándo |
|---|---|
| 0 | La entrada es válida y ninguna combinación de ningún régimen da `incompleto`. |
| 1 | La entrada es válida y alguna combinación de algún régimen da `incompleto`. |
| 2 | La entrada no es válida (modelo, §13), el fichero no se puede leer, o la orden se usa mal. |

**[D-25]** El código responde a «¿le falta algo al registro con alguna norma y alguna lectura?». Un `indeterminado` entre `completo` y `no_exigible` da 0 (ejemplo 2): en ninguna lectura falta nada. La alternativa, dar 1 por cualquier `indeterminado` como en `plazos-actualizacion-pbc`, marcaría como defectuosa toda alerta descartada bien registrada, solo porque R-6 no está resuelto.

---

## 10. Lo que queda fuera

- Ordenar varios registros y comprobar el registro cronológico del RD, art. 25.3 (modelo, §2).
- Comprobar que las decisiones responden a «criterios homogéneos» (RD, art. 25.2), que exige comparar expedientes.
- Los plazos de conservación (RD, art. 25.4; AMLR, art. 77.3), que son de `plazos-conservacion-pbc`.
- Cualquier requisito del AI Act (modelo, §11).

---

## 11. Índice de decisiones

| Id | Decisión | Sección |
|---|---|---|
| D-1 | El régimen es un parámetro; se calculan siempre los cinco y ninguno es principal. | §1.1 |
| D-2 | A según `sujeto.actividad`; fecha del registro: la de la revisión en una alerta, la que diga FT en un expediente. | §1.1 |
| D-3 | Una cadena vacía o de espacios cuenta como ausente. | §1.2 |
| D-4 | `no_exigible` es un estado distinto de `completo`. | §1.3 |
| D-5 | Mismo estado con faltas distintas no es `indeterminado`; se dan las faltas seguras y las que dependen de la lectura. | §1.3 |
| D-6 | Las lecturas se combinan todas con todas; solo se consultan las dimensiones que el registro pone en juego. | §1.4 |
| D-7 | El `indeterminado` se atribuye a toda dimensión que cambia el estado en alguna combinación de las demás (D-30 de `plazos-actualizacion-pbc`). | §1.4 |
| D-8 | Cada `indeterminado` se presenta como preguntas, con el resultado de cada respuesta y si resuelve (D-36 de `plazos-actualizacion-pbc`). | §1.4 |
| D-9 | No se comprueba la integralidad del examen, el carácter «significativo» de la intervención, los plazos sin fecha fija ni el art. 76.5.a; se dan días transcurridos y avisos. | §1.2 |
| D-10 | Los requisitos garantizados por la validación se listan como `cumple`. | §1.2 |
| D-11 | Comunicación decidida y no realizada: aviso, no falta. | §3.1 |
| D-12 | Decisor del RD: el representante o el órgano de control interno; persona autorizada según PA; otro órgano, falta. La apertura de un expediente muestra la revisión de su alerta. | §3.1, §3.2 |
| D-13 | Mayoría: MA-1 votos emitidos, MA-2 con abstenciones; empate, sin mayoría. | §3.1 |
| D-14 | Un votante sin cargo de miembro del órgano da aviso, no falta. | §3.1 |
| D-15 | Información considerada: fuentes, o salidas citadas por una circunstancia. | §4.1 |
| D-16 | SC-1 toda salida; SC-2 la citada por una fase; SC-3 ninguna. | §4.3 |
| D-17 | IH-1 nada; IH-2 propuestas de decisión; IH-3 además las que llegan a las razones. La intervención debe ser anterior o del mismo día que la decisión. | §4.4 |
| D-18 | La declaración sobre el sistema no cambia ningún requisito; R-5 no es dimensión. | §2.3 |
| D-19 | DC-1 el AMLR no dice quién decide; DC-2 decide el responsable del cumplimiento normativo. | §4.2 |
| D-20 | Alerta descartada: `no_exigible` con `ley_rd`; con `amlr`, AD-1 `no_exigible` y AD-2 AM-01 a AM-04. | §3.3, §4.5 |
| D-21 | T-1 desplazamiento; T-2 suma con prevalencia del AMLR; T-3 suma. Solo se contradicen en el decisor con DC-2. | §5.2 |
| D-22 | Expediente que abarca A: FT-1 la apertura, FT-2 el cierre. | §5.3 |
| D-23 | `amlr` en cualquier fecha, con aviso si el registro es anterior a A o la abarca. | §4.6 |
| D-24 | Umbral del RD, art. 23: dato informativo, con OA-1 el año anterior y OA-2 el del registro. | §2.2 |
| D-25 | Código 1 si alguna combinación da `incompleto`. | §9.1 |
| D-26 | Se comparan T-1 a T-3 y `ley_rd` con `amlr`; coinciden si dan el mismo estado y las mismas faltas. | §5.2 |
