# 0001. Validar el registro de la evaluación, no el sistema de IA

- Estado: aceptada
- Fecha: 22/09/2026

## Contexto

Los sujetos obligados por la normativa de prevención del blanqueo de capitales (PBC) examinan las operaciones que pueden estar relacionadas con el blanqueo y deciden si las comunican. Cada vez más, en ese examen interviene un sistema automatizado o de inteligencia artificial: genera la alerta, la prioriza, analiza la operativa o propone la decisión. Tres normas tocan esa intervención, y ninguna la cierra.

**El AMLR autoriza la IA en la evaluación, pero su garantía de intervención humana no alcanza expresamente la decisión de comunicar.**
- Art. 76.5: las entidades «podrán adoptar decisiones resultantes de procesos automatizados, incluida la elaboración de perfiles [...], o de procesos que impliquen sistemas de inteligencia artificial», con tres condiciones.
- La letra b) exige «una intervención humana significativa» en «toda decisión de entablar o negarse a entablar o mantener una relación de negocios con un cliente, o de llevar a cabo o negarse a realizar una operación ocasional para un cliente, o de aumentar o reducir el alcance de las medidas de diligencia debida». La decisión de comunicar una sospecha no está en la lista.
- La letra c) excluye de la explicación y la impugnación «el informe a que se refiere el artículo 69», lo que sugiere que el apartado 5 sí la abarca. Si la intervención humana la alcanza es el caso [R-2](../ambiguedades.md#r-2).
- El AMLR tampoco dice quién decide la comunicación: el responsable del cumplimiento normativo «comunica» y «remite» (arts. 11.2 y 69.6), sin que ningún artículo diga que decide ([R-4](../ambiguedades.md#r-4)).
- El art. 76.5 remite a la definición de sistema de IA de un «Reglamento (UE) 2024/XXX» que el texto publicado no identifica ([R-5](../ambiguedades.md#r-5)).

**El AI Act no suele aplicar a estos sistemas como alto riesgo.**
- El anexo III no recoge la prevención del blanqueo entre sus casos de uso. El más cercano, el punto 5.b, es la evaluación de la solvencia, «salvo los sistemas de IA utilizados al objeto de detectar fraudes financieros».
- El borrador de directrices de la Comisión, **no vinculante**, lo lee así: los sistemas de prevención del blanqueo quedan fuera del punto 5.b salvo que se usen también para evaluar la solvencia (apartado 309), y una entidad que los usa para cumplir sus propias obligaciones no actúa en nombre de las autoridades del punto 6 (apartado 2.5).
- Aunque aplicara, las obligaciones de alto riesgo del anexo III rigen desde el 2 de diciembre de 2027 (art. 113, letra c), según el texto consolidado) y recaen sobre el sistema y su uso (supervisión humana, archivos de registro, explicación), no sobre el registro de cada examen.

**La norma española asigna hoy la decisión a una persona con nombre.**
- RD, art. 25.2: «Concluido el análisis técnico, el representante ante el Servicio Ejecutivo de la Comisión adoptará, motivadamente y sin demora, la decisión sobre si procede o no la comunicación». O, si el procedimiento lo prevé, el órgano de control interno por mayoría, con el voto de cada miembro en el acta.
- El representante es una persona física designada, residente en España y con cargo de administración o dirección, cuyo nombramiento se comunica al Servicio Ejecutivo con su trayectoria profesional, salvo las excepciones que fije el reglamento (Ley, art. 26 ter.1 y 2).
- El RD también fija qué se registra de cada examen: fechas de apertura y cierre, motivo, operativa, conclusión y razones, decisión y su fecha, fecha de la comunicación (art. 25.3), y fases, gestiones y fuentes (art. 25.1).

Desde el 10 de julio de 2027 se aplica el AMLR (art. 90), que pide otro registro (art. 77.1.b: la información y las circunstancias consideradas, los resultados y la copia de la comunicación) y no deroga el art. 25 del RD. Ningún texto dice si el art. 25 sigue aplicándose ([R-3](../ambiguedades.md#r-3)).

El resultado es un hueco: la norma europea autoriza que un modelo intervenga en la evaluación y no asigna la decisión que la española asigna con nombre. La pregunta práctica de una entidad no es si su sistema es bueno, sino si el registro de cada examen, con o sin sistema, contiene lo que cada norma exige, y dónde depende de preguntas que nadie ha respondido.

## Decisión

**1. La herramienta valida el registro de la evaluación bajo cinco regímenes.**

Los cinco son la Ley y el RD aplicados solos (`ley_rd`), el AMLR aplicado solo (`amlr`) y tres lecturas de si el art. 25 del RD sigue aplicándose desde el 10 de julio de 2027: desplazamiento (T-1), suma con prevalencia del AMLR (T-2) y suma sin más (T-3). Se calculan siempre los cinco y ninguno es el principal ([especificación](../especificacion-calculo.md), §1.1 y §5; D-1, D-21).

Para cada régimen, el registro está `completo`, `incompleto` o `no_exigible`, con la lista de lo que falta, cada requisito con su artículo. Donde la norma no decide, cada pregunta es una dimensión de lectura; si sus respuestas dan estados distintos, el régimen es `indeterminado`, y la salida lo atribuye a las preguntas que lo causan (D-7) y dice qué da cada respuesta (D-8). Es el mismo planteamiento que en `plazos-actualizacion-pbc` (su ADR 0001).

El registro puede ser un examen especial o una alerta revisada y descartada sin abrir examen, porque en el AMLR esa revisión puede ser una evaluación que hay que registrar ([R-6](../ambiguedades.md#r-6)).

**2. El sistema de IA es una caja cerrada, y su salida es un dato opaco.**

Del sistema solo se recoge lo que el registro puede atestiguar sin mirar dentro (modelo, §0.2, regla 2, y §9):
- un identificador opaco y la **declaración** de la entidad sobre si lo considera un sistema de IA según el art. 3.1 del AI Act (`si`, `no` o `desconocido`), que no se infiere ni se comprueba;
- cada **participación**: en qué momento (generación o priorización de la alerta, análisis, propuesta de decisión), cuándo, qué parte del registro la cita;
- la **salida**, como cadena, tal como la dio el sistema, que el cálculo no interpreta nunca;
- la **intervención humana** sobre esa salida: quién, cuándo y qué hizo.

No se modelan variables, umbrales, reglas, tipos de alerta ni la clasificación del sistema. Los procesos automatizados y los sistemas de IA reciben el mismo trato, como en el art. 76.5.

## Consecuencias

**Lo que la herramienta puede comprobar desde el registro:**
- que constan los datos que exige cada régimen, con la ruta de cada falta;
- quién decidió, con qué cargo, y si un órgano colegiado dejó el voto y la motivación de cada miembro y tuvo mayoría (con las dos lecturas de la mayoría, [R-8](../ambiguedades.md#r-8));
- si la salida de un sistema figura entre las circunstancias consideradas, con las tres lecturas de [R-1](../ambiguedades.md#r-1);
- si una propuesta de decisión, o una salida que llegó a las razones, tuvo una intervención humana anterior a la decisión o del mismo día, con las lecturas de [R-2](../ambiguedades.md#r-2);
- qué cambia según la norma que se aplique y según cómo se resuelva la transición.

**Lo que no puede comprobar:**
- **La condición del art. 76.5.a.** El AMLR exige que «los datos tratados por dichos sistemas se limiten a los datos obtenidos con arreglo al capítulo III». Comprobarlo exige conocer las variables del sistema, que el modelo no recoge a propósito. No se verifica desde el registro: es una comprobación sobre el sistema, y la salida lo avisa, en los regímenes que aplican el AMLR, cada vez que hay participaciones (D-9).
- **Si la intervención humana fue «significativa»** (art. 76.5.b). Es una valoración, no un hecho del registro. La herramienta comprueba que existe y no es posterior a la decisión, y avisa de que no la valora.
- **Si el sistema es de alto riesgo, o si es un sistema de IA.** Solo recoge la declaración de la entidad, que no cambia ningún requisito (D-18).
- **Si el sistema acierta.** La salida no se interpreta. Un sistema que produce alertas inútiles y uno que produce alertas precisas dejan el mismo registro.
- **Si el examen fue integral** (RD, art. 25.1), si la decisión se tomó «sin demora» o la comunicación «sin dilación», o si las decisiones responden a «criterios homogéneos»: la herramienta da los días transcurridos, pero ni hay un número de días con que comparar ni puede ver lo que no se examinó.

**Hay tres costes.**
- **`indeterminado` es frecuente.** Cualquier expediente en el que participe un sistema consulta al menos una dimensión (R-1), y todo expediente consulta quién decide con el AMLR (R-4). En el corpus, siete de ocho casos tienen algún régimen `indeterminado`. El código de salida no mira si los regímenes coinciden, sino si alguna lectura exige completar el registro (D-25).
- **El borrador de la Comisión se usa como contexto, no como norma.** Ningún caso R-n depende de él ([ambiguedades.md](../ambiguedades.md), §2). Si las directrices finales, anunciadas para finales de 2026, clasificaran estos sistemas como de alto riesgo, el cálculo no cambiaría, pero habría que revisar el contexto de esta decisión, el §11 del modelo y el README.
- **La caja cerrada es deliberada, y deja fuera preguntas reales.** Quien necesite saber si su sistema cumple el art. 76.5.a o el AI Act tiene que mirar el sistema, no el registro. Esta herramienta no lo sustituye: dice si el registro de cada examen deja constancia de lo que la norma exige, incluida la intervención de un sistema, y dónde la respuesta depende de una pregunta que nadie ha respondido.

## Referencias

- Ley 10/2010, de 28 de abril, arts. 17, 18 y 26 ter (texto consolidado, última modificación de 21 de marzo de 2026): <https://www.boe.es/buscar/act.php?id=BOE-A-2010-6737>
- Real Decreto 304/2014, de 5 de mayo, arts. 23, 25 y 35 (texto consolidado, última modificación de 24 de abril de 2024): <https://www.boe.es/buscar/act.php?id=BOE-A-2014-4742>
- Reglamento (UE) 2024/1624 (AMLR), arts. 11, 69, 76.5, 77 y 90 (DO L de 19.6.2024): <http://data.europa.eu/eli/reg/2024/1624/oj>
- Reglamento (UE) 2024/1689 (AI Act), arts. 3.1, 6 y 113 y anexo III (DO L de 12.7.2024, y texto consolidado a 27 de julio de 2026, sin efecto jurídico): <http://data.europa.eu/eli/reg/2024/1689/oj>
- Comisión Europea, «Draft Commission guidelines on the classification of high-risk AI systems under Article 6 of Regulation (EU) 2024/1689», anexo III, 19 de mayo de 2026. **Borrador no vinculante**: <https://digital-strategy.ec.europa.eu/en/library/draft-commission-guidelines-classification-high-risk-ai-systems>
- Versiones y huellas de los documentos usados: [fuentes/FUENTES.md](../fuentes/FUENTES.md)
