# Ambigüedades

Casos en que el resultado no está determinado por un texto único. Para cada uno:
- qué dice la norma;
- por qué no determina un comportamiento único;
- qué hace esta implementación;
- cómo se señala en la salida;
- a qué régimen afecta.

Siglas y fuentes: las de [`modelo-datos.md`](modelo-datos.md) (detalle y huellas en [`fuentes/FUENTES.md`](fuentes/FUENTES.md)). Las decisiones se citan como en su documento: **D-n** en [`especificacion-calculo.md`](especificacion-calculo.md) y **V-n** en el §13.2 de [`modelo-datos.md`](modelo-datos.md). Los identificadores R-n son estables: no se renumeran ni se reutilizan. R-11 apareció al escribir la especificación de la transición.

Hay dos secciones:

- [**Casos que la norma no resuelve**](#1-casos-que-la-norma-no-resuelve) (R-1 a R-11): el texto calla, se contradice o no dice cuál de dos normas rige.
- [**Lo que depende del borrador de la Comisión**](#2-lo-que-depende-del-borrador-de-la-comisión). **El borrador no es vinculante**, y las directrices finales se anuncian para finales de 2026. Ningún caso R-n existe por el borrador; la sección dice qué partes del repositorio se apoyan en él y qué cambiaría con las directrices finales.

**Cómo se señala en la salida.** La salida (especificación, §9) tiene cinco mecanismos, y cada caso dice cuáles usa:

- **decisiones**: una dimensión de lectura (por ejemplo `SC`, con las lecturas `SC-1` a `SC-3`). Si sus lecturas dan estados distintos, el régimen es `indeterminado`. La salida presenta la dimensión como una pregunta, con el estado y lo que falta con cada respuesta, si con ella el estado queda resuelto y los datos que la ponen en juego (D-7, D-8);
- **regímenes de transición**: T-1 a T-3 junto a `ley_rd` y `amlr`, con la comparación que dice si no coinciden (D-26);
- **estados propios**: `no_exigible`, que dice que la norma no exige registro en lugar de darlo por completo (D-4);
- **avisos y datos informativos**: incidencias y datos que no cambian el estado, citados por su D-n;
- **no se señala**: la implementación aplica una decisión, y la salida no dice que otra lectura cambiaría el resultado.

**Regímenes.** `ley_rd` es la Ley 10/2010 con el RD 304/2014; `amlr`, el AMLR; T-1 a T-3, las lecturas de si el art. 25 del RD sigue aplicándose desde el 10 de julio de 2027 (especificación, §5). Antes de esa fecha, T-1 a T-3 dan lo mismo que `ley_rd`. Cuando un caso afecta a `ley_rd`, también afecta a los T-n que la aplican.

---

## 1. Casos que la norma no resuelve

<a id="r-1"></a>
### R-1. ¿Es la salida del sistema una «circunstancia considerada» del art. 77.1.b?

**Qué dice la norma.**
- AMLR, art. 77.1.b: el registro incluye «la información y las circunstancias consideradas y los resultados de dicha evaluación».
- AMLR, art. 69.2, párrafo segundo: la sospecha se basa en características del cliente, cuantía, naturaleza, patrones, relación entre operaciones, origen y destino de los fondos, «o cualquier otra circunstancia conocida por la entidad obligada».
- Ningún texto menciona la salida de un sistema como circunstancia ni como información.

**Por qué no determina un comportamiento único.** - Puede leerse que la salida es «información» considerada (es un dato que la entidad tiene) y, por tanto, debe constar siempre que se generó.
- Puede leerse que solo es «circunstancia considerada» si la entidad la tuvo en cuenta para su conclusión.
- O puede leerse que la salida no es una circunstancia de la operación, sino una valoración sobre ella, y que lo que se registra son las circunstancias que el sistema señaló, no su salida.
- Tampoco está claro si una salida que la entidad descartó debe constar.

**Qué hace la implementación.** El modelo recoge todas las participaciones, con su salida, se usaran o no (modelo, §9), y deja que la entidad enlace la salida desde `circunstancias_consideradas` y desde `razones` (modelo, §7). Así se distinguen tres hechos: la salida existió; la entidad la trató como circunstancia considerada; la salida llegó a las razones de la conclusión. Cada lectura usa el que le corresponde.

Dimensión **SC** en el requisito AM-04 (especificación, §4.3; D-16): **SC-1**, toda participación debe estar citada por una circunstancia; **SC-2**, solo las que cita una fase; **SC-3**, ninguna.

**Cómo se señala en la salida.** Decisión `SC`, y AM-04 entre los requisitos que faltan «solo en algunas» lecturas. Corpus: casos 02 y 08. Especificación, ejemplos 1 y 3.

**Régimen.** AMLR.

<a id="r-2"></a>
### R-2. ¿Alcanza la intervención humana del art. 76.5.b a la decisión de comunicar?

**Qué dice la norma.**
- AMLR, art. 76.5: las entidades «podrán adoptar decisiones resultantes de procesos automatizados [...] o de procesos que impliquen sistemas de inteligencia artificial», siempre que se cumplan tres condiciones.
- Letra b): «toda decisión de entablar o negarse a entablar o mantener una relación de negocios con un cliente, o de llevar a cabo o negarse a realizar una operación ocasional para un cliente, o de aumentar o reducir el alcance de las medidas de diligencia debida [...] esté sujeta a una intervención humana significativa».
- Letra c): el cliente puede obtener una explicación e impugnar la decisión, «excepto en relación con el informe a que se refiere el artículo 69 del presente Reglamento».
- Considerando 150: las entidades «deben poder adoptar procesos que permitan las decisiones individuales automatizadas, incluida la elaboración de perfiles, tal como se establece en el artículo 22 del Reglamento (UE) 2016/679».

**Por qué no determina un comportamiento único.** - La letra b) enumera decisiones, y la de comunicar no está entre ellas. Leída como lista cerrada, la decisión de comunicar no necesita intervención humana significativa por el art. 76.5.
- Pero la letra c) excluye expresamente «el informe a que se refiere el artículo 69». Si la decisión de comunicar no fuera una de las decisiones del apartado 5, esa excepción no haría falta. Eso sugiere que el apartado 5 sí la abarca, y que la letra b) solo exige la intervención humana en las decisiones que enumera.
- Tampoco está claro si una salida con `momento` `analisis` que influye en la conclusión es ya una «decisión resultante» de un proceso automatizado, o si solo lo es cuando el sistema propone la decisión.
- Fuera del AMLR, el art. 22 del Reglamento (UE) 2016/679 puede exigir intervención humana por su cuenta. Este proyecto no lo analiza.

**Qué hace la implementación.** El modelo recoge, para cada participación, el momento (incluido `propuesta_decision`), su fecha, y quién intervino sobre la salida, cuándo y cómo (modelo, §9). No dice si la intervención fue «significativa».

Dimensión **IH** en el requisito AM-06 (especificación, §4.4; D-17): **IH-1**, no exige nada; **IH-2**, las propuestas de decisión necesitan una intervención humana anterior o del mismo día que la decisión; **IH-3**, también las salidas que llegan a las razones. El cálculo comprueba que la intervención existe y es anterior; no valora si fue «significativa» (D-9).

**Cómo se señala en la salida.** Decisión `IH`. Avisos D-17 (intervención posterior a la decisión, que no cuenta) y D-9 (no se ha valorado si fue significativa). Corpus: caso 04. Especificación, ejemplo 4.

**Régimen.** AMLR.

<a id="r-3"></a>
### R-3. ¿Sigue aplicándose el art. 25 del RD desde el 10 de julio de 2027?

**Qué dice la norma.**
- AMLR, art. 90: «Será aplicable a partir del 10 de julio de 2027». Y al final: «El presente Reglamento será obligatorio en todos sus elementos y directamente aplicable en cada Estado miembro».
- El AMLR no deroga ninguna norma nacional ni tiene una disposición transitoria sobre el registro del examen.
- Ni la Ley consolidada a 21 de marzo de 2026 ni el RD consolidado a 24 de abril de 2024 mencionan el Reglamento (UE) 2024/1624.
- El AMLR pide menos datos que el RD (modelo, §11), y no dice si los Estados miembros pueden pedir más en este punto.

**Por qué no determina un comportamiento único.** Caben al menos tres lecturas:
- el art. 25 del RD deja de aplicarse, desplazado por los arts. 69 y 77 del AMLR;
- el art. 25 sigue aplicándose como norma nacional que desarrolla el examen, en lo que no contradiga el AMLR, y las dos listas de datos se suman;
- el art. 25 sigue aplicándose hasta que se derogue o se adapte, sin examinar su compatibilidad.

La respuesta cambia qué datos son obligatorios en un examen de 2028: con la primera lectura, no hacen falta ni las fechas de apertura y cierre, ni las fases, ni los votos.

**Qué hace la implementación.** El modelo recoge los datos de los dos regímenes en todos los exámenes, sea cual sea su fecha (modelo, §0.1, principio 3). El régimen, y con él esta lectura, es un parámetro del cálculo.

Tres regímenes de transición junto a `ley_rd` y `amlr` (especificación, §5; D-21): **T-1**, desplazamiento, desde el 10 de julio de 2027 solo el AMLR; **T-2**, suma de requisitos con prevalencia del AMLR si se contradicen; **T-3**, suma sin más. Solo se contradicen en quién decide, y solo con DC-2 ([R-4](#r-4)). Antes de esa fecha, los tres son `ley_rd`.

**Cómo se señala en la salida.** Regímenes de transición, con la comparación que dice si T-1 a T-3 no coinciden (D-26). Corpus: caso 05. Especificación, ejemplo 6.

**Régimen.** Ley/RD y AMLR, para los exámenes posteriores al 10 de julio de 2027 (o al 10 de julio de 2029, con `sujeto.actividad` de fútbol).

<a id="r-4"></a>
### R-4. ¿Quién decide la comunicación en el AMLR?

**Qué dice la norma.**
- AMLR, art. 11.2: el responsable del cumplimiento normativo «también será responsable de comunicar las operaciones sospechosas a la UIF conforme al artículo 69, apartado 6».
- AMLR, art. 69.6: «La persona que haya sido nombrada de conformidad con el artículo 11, apartado 2, remitirá la información a que hace referencia el apartado 1 del presente artículo a la UIF».
- AMLR, art. 69.1: la obligación de comunicar es de «Las entidades obligadas y, en su caso, sus directivos y empleados».
- AMLR, art. 11.4: las entidades garantizarán que «las decisiones del responsable del cumplimiento normativo no se vean perjudicadas o influidas indebidamente por los intereses comerciales de la entidad obligada».
- En cambio, el RD, art. 25.2, dice expresamente quién decide: el representante o, si el procedimiento lo prevé, el órgano de control interno por mayoría.

**Por qué no determina un comportamiento único.** «Comunicar» y «remitir» pueden leerse como el acto de enviar, no como la decisión de hacerlo. Con esa lectura, el AMLR no dice quién decide, y la entidad puede atribuir la decisión a quien quiera, incluido un órgano colegiado. Con la lectura contraria, ser «responsable de comunicar» implica decidir, y la decisión es del responsable del cumplimiento normativo. El art. 11.4 habla de «las decisiones del responsable», sin decir cuáles. Tampoco está claro si, con el AMLR, un órgano de control interno puede seguir decidiendo por mayoría como prevé el RD ([R-3](#r-3)).

**Qué hace la implementación.** El modelo recoge quién decidió (una persona o un órgano; modelo, §8.1) y los cargos de cada persona en la fecha de la decisión (modelo, §2.2), incluidos los del AMLR, sin presuponer cuál debe ser el decisor.

Dimensión **DC** en el requisito AM-07 (especificación, §4.2; D-19): **DC-1**, el AMLR no dice quién decide y cumple siempre; **DC-2**, decide el responsable del cumplimiento normativo. Con DC-2, T-2 deja sin aplicar RD-11 a RD-13 y T-3 los mantiene (D-21).

**Cómo se señala en la salida.** Decisión `DC`. Corpus: casos 05 y 06. Especificación, ejemplos 1, 5 y 6.

**Régimen.** AMLR.

<a id="r-5"></a>
### R-5. El «Reglamento (UE) 2024/XXX» sin rellenar del art. 76.5

**Qué dice la norma.**
- AMLR, art. 76.5: «sistemas de inteligencia artificial con arreglo a la definición que figura en el artículo 3, punto 1, del Reglamento (UE) 2024/XXX del Parlamento Europeo y del Consejo (45)».
- Nota 45: «Reglamento (UE) 2024/XXX del Parlamento Europeo y del Consejo, de XXX, por el que se establecen normas armonizadas en materia de inteligencia artificial y se modifican los Reglamentos (CE) n.o 300/2008, [...] (Ley de Inteligencia Artificial) (pendiente de publicación en el Diario Oficial)».
- El AMLR se publicó el 19 de junio de 2024, y el AI Act, el 12 de julio de 2024, como Reglamento (UE) 2024/1689, con un título que coincide con el de la nota salvo el nombre corto («Reglamento de Inteligencia Artificial» y no «Ley de Inteligencia Artificial»).

**Por qué no determina un comportamiento único.** - El texto publicado del AMLR no identifica el reglamento. Este proyecto solo tiene ese texto y no ha comprobado si existe una corrección de errores que rellene la referencia.
- La identificación con el Reglamento (UE) 2024/1689 es la única razonable por el título, pero es una deducción, no lo que dice el texto.
- Aunque se acepte, queda por saber si la remisión es a la definición del art. 3, punto 1, tal como se publicó o tal como esté en cada momento. El texto consolidado muestra que la definición ya cambió por la rectificación «►C1» (DO L 90802 de 9.10.2025): el original dice que el sistema «puede mostrar capacidad de adaptación tras el despliegue»; el consolidado, «pueda mostrar».

**Qué hace la implementación.** El modelo no clasifica el sistema (modelo, §0.2, regla 2) y trata igual a los sistemas de IA y a los demás procesos automatizados del art. 76.5 (modelo, §9.1). Recoge lo que la entidad declara sobre la definición del art. 3, punto 1 (modelo, §9.2), pero no con qué reglamento ni con qué versión de la definición lo ha decidido: la declaración se toma tal como la da la entidad. Se documenta porque cualquier cálculo que tenga que decir si se aplica el art. 76.5 a un sistema concreto tendrá que tomar postura.

No es una dimensión de lectura: la respuesta no cambia ningún requisito, porque el art. 76.5 trata igual a los sistemas de IA y a los demás procesos automatizados (especificación, §2.3; D-18). La declaración de la entidad se da como dato informativo.

**Cómo se señala en la salida.** **No se señala.** Los datos informativos listan cada sistema con la declaración de la entidad y dicen que no cambia ningún requisito.

**Régimen.** AMLR.

<a id="r-6"></a>
### R-6. ¿Qué evaluación genera el registro del art. 77.1.b?

**Qué dice la norma.**
- AMLR, art. 77.1.b: «un registro de la evaluación realizada de conformidad con el artículo 69, apartado 2 [...], con independencia de que dicha evaluación dé lugar o no a una comunicación».
- AMLR, art. 69.2: «las entidades obligadas evaluarán las operaciones o actividades llevadas a cabo por sus clientes sobre la base de cualquier hecho o información pertinente».
- RD, art. 23: las alertas «serán revisadas a efectos de determinar si procede el examen especial». El registro del art. 25.3 es «para cada expediente de examen especial realizado». Una alerta revisada y descartada no abre expediente.

**Por qué no determina un comportamiento único.** La revisión de una alerta que se descarta puede ser ya una «evaluación» del art. 69.2, que el art. 77.1.b obliga a registrar, o solo un filtro previo a la evaluación. Con la primera lectura, el AMLR exige registrar muchos más casos que el RD, incluidos los que nunca llegarían a expediente.

**Qué hace la implementación.** Un registro puede ser un `expediente` o una `alerta_descartada` (modelo, §10). La alerta descartada lleva los campos mínimos para calcular dos lecturas:
- **AD-1:** revisar una alerta no es evaluar en el sentido del art. 69.2. Con el AMLR, la alerta descartada no exige registro, igual que con la Ley y el RD.
- **AD-2:** revisar una alerta ya es evaluar. El art. 77.1.b exige registrar la información y las circunstancias consideradas (`fuentes`, `circunstancias_consideradas`) y los resultados (`resultado`).

Con las dos lecturas y con la Ley y el RD, la entrada recoge que la alerta se revisó, quién y cuándo (RD, art. 23). La validación admite una alerta descartada sin fuentes, sin circunstancias y sin resultado: con AD-2 eso es un registro incompleto que el cálculo debe señalar, y con AD-1 no lo es (modelo, §13, V-15).

Dimensión **AD** (especificación, §4.5; D-20): **AD-1**, `no_exigible`; **AD-2**, se comprueban AM-01 a AM-04. Con `ley_rd` la alerta descartada es siempre `no_exigible` (especificación, §3.3).

**Cómo se señala en la salida.** Decisión `AD`, con el estado propio `no_exigible`. Una alerta bien registrada da código 0 aunque sea `indeterminado`, porque en ninguna lectura falta nada (D-25). Corpus: caso 03. Especificación, ejemplo 2.

**Régimen.** AMLR, para las alertas revisadas y descartadas; la Ley y el RD no tienen el problema.

<a id="r-7"></a>
### R-7. ¿Qué año y qué operaciones cuentan para el umbral de 10.000 del RD, art. 23?

**Qué dice la norma.**
RD, art. 23: «En el caso de sujetos obligados cuyo número anual de operaciones exceda de 10.000, será preceptiva la implantación de modelos automatizados de generación y priorización de alertas».

**Por qué no determina un comportamiento único.** - «Número anual» no dice si es el año natural en curso, el anterior o los últimos doce meses.
- No dice qué es una «operación» a estos efectos: si cuenta cada movimiento, cada operación con cliente o solo las de determinados productos.
- No dice cuándo nace la obligación si el umbral se supera a mitad de año.

**Qué hace la implementación.** El modelo recoge el número por año tal como lo cuenta la entidad (modelo, §2.1). El criterio de cómputo es de la entidad y el modelo no lo verifica.

Dimensión **OA** en un dato informativo, no en el estado (especificación, §2.2; D-24): **OA-1**, el año natural anterior al de la fecha del registro; **OA-2**, el de la fecha del registro. El modelo no recoge si la entidad tiene modelos automatizados de alertas, así que la obligación del art. 23 no se comprueba.

**Cómo se señala en la salida.** Dato informativo del umbral de operaciones, con el valor de cada lectura; puede ser `indeterminado`, pero no cambia el estado de ningún régimen.

**Régimen.** Ley/RD.

<a id="r-8"></a>
### R-8. Abstenciones y empates en el órgano de control interno

**Qué dice la norma.**
RD, art. 25.2: «el órgano de control interno adoptará la decisión por mayoría, debiendo constar expresamente en el acta, el sentido y motivación del voto de cada uno de los miembros».

**Por qué no determina un comportamiento único.** «Por mayoría» puede ser de los votos emitidos, de los presentes o de los miembros. No dice cómo cuentan las abstenciones ni qué pasa con un empate. Tampoco dice si un miembro puede abstenerse, ya que el acta debe recoger el «sentido» de su voto.

**Qué hace la implementación.** El modelo recoge el voto de cada miembro, con `abstencion` como valor posible (modelo, §8.1). No recoge el número total de miembros del órgano: no sale de ningún artículo del registro. Por eso, la lectura «mayoría de los miembros» solo puede aplicarse si todos los miembros figuran en `votos`.

Dimensión **MA** en el requisito RD-13 (especificación, §3.1; D-13), solo si hay abstenciones: **MA-1**, mayoría de los votos emitidos; **MA-2**, mayoría con las abstenciones en el total. Un empate no da mayoría con ninguna lectura. La lectura «mayoría de los miembros» no se calcula.

**Cómo se señala en la salida.** Decisión `MA`. Corpus: caso 06. Especificación, ejemplo 5.

**Régimen.** Ley/RD.

<a id="r-9"></a>
### R-9. ¿Qué cierra el expediente?

**Qué dice la norma.**
RD, art. 25.3: el registro recoge las «fechas de apertura y cierre», y además la fecha de la decisión y la de la comunicación. El art. 25.2 habla de la conclusión del «análisis técnico», que es otro hito.

**Por qué no determina un comportamiento único.** El cierre puede ser el fin del análisis técnico, la decisión o la comunicación. Según la lectura, un expediente cerrado puede tener todavía pendiente la decisión o la comunicación.

**Qué hace la implementación.** El modelo recoge las cuatro fechas por separado (modelo, §3 y §8) y no exige ningún orden entre el cierre y la decisión o la comunicación (modelo, §13, V-6).

No es una dimensión de lectura: el cálculo usa `fecha_cierre` tal como la declara la entidad, también para decidir la norma del expediente con FT-2 ([R-11](#r-11); especificación, §5.3).

**Cómo se señala en la salida.** **No se señala.**

**Régimen.** Ley/RD.

<a id="r-10"></a>
### R-10. ¿Puede decidir una persona autorizada por el representante?

**Qué dice la norma.**
- RD, art. 25.2: la decisión la adopta «el representante ante el Servicio Ejecutivo de la Comisión».
- RD, art. 35.1: el representante «podrá designar, asimismo, hasta dos personas autorizadas que actuarán bajo la dirección y responsabilidad del representante».

**Por qué no determina un comportamiento único.** El art. 35.1 no dice qué funciones pueden ejercer las personas autorizadas. Puede leerse que actúan en todo lo que corresponde al representante, incluida la decisión del art. 25.2, o que solo le asisten.

**Qué hace la implementación.** El modelo recoge el cargo `persona_autorizada_por_el_representante` (modelo, §2.2), de modo que se vea cuándo decidió una persona autorizada y no el representante.

Dimensión **PA** en el requisito RD-11 (especificación, §3.1; D-12), si decide una persona autorizada que no es el representante: **PA-1**, puede decidir; **PA-2**, no.

**Cómo se señala en la salida.** Decisión `PA`.

**Régimen.** Ley/RD.

<a id="r-11"></a>
### R-11. ¿Qué fecha decide la norma de un expediente abierto antes del 10 de julio de 2027 y cerrado después?

**Qué dice la norma.**
- AMLR, art. 90: «Será aplicable a partir del 10 de julio de 2027».
- RD, art. 25.3: el registro recoge las fechas de apertura y cierre de «cada expediente de examen especial realizado». AMLR, art. 77.1.b: «un registro de la evaluación realizada».
- Ningún texto tiene una regla transitoria para los exámenes en curso ese día.

**Por qué no determina un comportamiento único.** El examen puede regirse por la norma con que empezó, o por la vigente cuando se concluye y se registra («la evaluación realizada», «cada expediente [...] realizado»).

**Qué hace la implementación.** El modelo recoge las dos fechas (modelo, §3). La especificación calcula las dos lecturas (FT-1, la apertura; FT-2, el cierre).

Dimensión **FT** en T-1 a T-3 (especificación, §5.3; D-22): **FT-1**, la apertura; **FT-2**, el cierre. Con FT-1 el expediente se rige por `ley_rd`; con FT-2, por la columna «desde el 10 de julio de 2027» de cada T-n.

**Cómo se señala en la salida.** Decisión `FT` en T-1 a T-3, y aviso D-23 en `amlr` cuando el expediente abarca la fecha de aplicación. Corpus: caso 07. Especificación, ejemplo 3.

**Régimen.** Los regímenes de transición de la especificación (T-1 a T-3), para un expediente con `fecha_apertura` anterior a la fecha de aplicación del AMLR y `fecha_cierre` igual o posterior.

---

## 2. Lo que depende del borrador de la Comisión

> **Borrador no vinculante.** «Draft Commission guidelines on the classification of high-risk AI systems under Article 6 of Regulation (EU) 2024/1689 (AI Act) for stakeholder consultation», anexo dedicado al anexo III del AI Act, publicado el 19 de mayo de 2026. La consulta se cerró el 23 de julio de 2026, después de ampliarse desde el 23 de junio, y la Comisión anuncia las directrices finales para finales de 2026 ([FUENTES.md](fuentes/FUENTES.md)). El plazo que fijaba el art. 6.5 del AI Act para esas directrices, el 2 de febrero de 2026, pasó sin ellas.

**Ningún caso R-n depende del borrador.** Todos salen de la Ley, el RD o el AMLR, y ninguna lectura existe por el borrador. El borrador solo se cita en dos sitios, y en ninguno cambia un resultado del cálculo:

| Dónde | Qué toma del borrador | Qué cambiaría con las directrices finales |
|---|---|---|
| Modelo, §11 («El AI Act no es un régimen de este registro») | Que los sistemas de prevención del blanqueo quedan fuera del punto 5.b del anexo III salvo que se usen también para evaluar la solvencia (apartado 309), y que una entidad que los usa para cumplir sus propias obligaciones no actúa en nombre de las autoridades del punto 6 (apartado 2.5). Se anota como contexto, sin que el modelo dependa de ello. | Si las directrices finales clasificaran estos sistemas como de alto riesgo, les alcanzarían las obligaciones de quien los despliega (AI Act, arts. 14, 26 y 86), aplicables desde el 2 de diciembre de 2027 según el texto consolidado. El cálculo no cambiaría: no clasifica el sistema (modelo, §0.2, regla 2) y el AI Act no define requisitos del registro. Habría que revisar el §11 del modelo, el [ADR 0001](adr/0001-validar-el-registro-no-el-sistema.md) y el README, que dicen que el AI Act no suele aplicar. |
| [ADR 0001](adr/0001-validar-el-registro-no-el-sistema.md) y README | La misma lectura, como parte del contexto de la decisión. | Lo mismo. Si las directrices finales cambiaran la clasificación, la decisión de tratar el sistema como caja cerrada seguiría, pero su motivo cambiaría: ya no sería que el AI Act no suele aplicar, sino que sus obligaciones recaen sobre el sistema y su uso y no sobre el registro de cada examen. |

**Cuando se publiquen las directrices finales** hará falta añadirlas a [FUENTES.md](fuentes/FUENTES.md) como documento distinto, con su versión y su huella, y revisar las filas de esta tabla. Si además dijeran algo sobre la definición de sistema de IA del art. 3, punto 1, habría que revisar [R-5](#r-5), que hoy no cambia ningún resultado.
