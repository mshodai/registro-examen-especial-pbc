# registro-examen-especial-pbc

Un sujeto obligado por la normativa de prevención del blanqueo de capitales examina las operaciones que pueden estar relacionadas con el blanqueo, decide si las comunica y deja registro de cada examen. Cada vez más, en ese examen interviene un sistema automatizado o de inteligencia artificial. Esta herramienta comprueba si el registro de un examen, o de una alerta revisada y descartada, contiene lo que exige cada norma, y dónde la respuesta depende de una pregunta que ningún texto resuelve.

El escenario. La norma europea autoriza que un modelo intervenga en la evaluación: el Reglamento (UE) 2024/1624 (AMLR), aplicable desde el 10 de julio de 2027, permite decisiones «resultantes de procesos automatizados [...] o de procesos que impliquen sistemas de inteligencia artificial» (art. 76.5). Pero deja sin asignar la decisión de comunicar una sospecha:
- **La intervención humana significativa** que exige el art. 76.5.b se refiere a entablar o mantener una relación, a una operación ocasional y a las medidas de diligencia debida. La decisión de comunicar no está en la lista.
- **Quién decide** tampoco lo dice: el responsable del cumplimiento normativo «comunica» y «remite» (arts. 11.2 y 69.6).
- **La norma española sí lo asigna, y con nombre.** El RD 304/2014, art. 25.2: «el representante ante el Servicio Ejecutivo de la Comisión adoptará, motivadamente y sin demora, la decisión». El representante es una persona designada cuyo nombramiento se comunica al Servicio Ejecutivo (Ley 10/2010, art. 26 ter).
- **El Reglamento de Inteligencia Artificial no suele aplicar como alto riesgo**: su anexo III no recoge la prevención del blanqueo, y el borrador de directrices de la Comisión, no vinculante, lo lee así.

Si la entidad decide quién decide con el AMLR, y si el art. 25 del RD sigue aplicándose desde el 10 de julio de 2027, cambia lo que se exige al registro.

Esta herramienta no dice si el sistema es bueno ni si cumple el AI Act. Trata el sistema como una caja cerrada cuya salida es un dato más del registro, y comprueba el registro en cinco regímenes: la Ley y el RD, el AMLR y tres lecturas de la transición entre ambos. Cuando el resultado depende de una pregunta que la norma no resuelve, dice cuál es, qué pasa con cada respuesta y qué dato de la entrada la pone en juego. El porqué está en el [ADR 0001](docs/adr/0001-validar-el-registro-no-el-sistema.md).

## El caso, calculado

El repositorio incluye un corpus de ocho registros sintéticos en `corpus/`, cada uno con su resultado esperado. En el caso 05 decide la persona responsable del cumplimiento normativo, que no es el representante ante el Servicio Ejecutivo:

```
$ registro-examen-especial corpus/05-decide-el-responsable-del-cumplimiento.json
Expediente EXP-FICTICIO-05
AMLR aplicable desde el 2027-07-10

Resultado de un cálculo bajo las lecturas que declara la especificación (docs/especificacion-calculo.md), no una determinación jurídica. Donde la norma no decide, el cálculo da todas las lecturas y no elige; las decisiones propias se citan como D-n.

Estado del registro:
  ley_rd  incompleto
  amlr    completo
  T-1     completo
  T-2     indeterminado
  T-3     incompleto

Dónde difieren:
  ley_rd y amlr no coinciden: la norma cambia lo que se exige al registro.
  T-1, T-2, T-3 no coinciden: lo que se exige depende de si el art. 25 del RD sigue aplicándose desde el 2027-07-10 (R-3, D-26).
  ley_rd, T-3: incompleto; amlr, T-1: completo; T-2: indeterminado
  «indeterminado»: las lecturas de ese régimen dan estados distintos (D-5).

Exige actuar:
  Sí (D-25). Lo exigen:
    ley_rd:
      sin lecturas que decidir: falta RD-11
    T-2 (estado del régimen: indeterminado):
      DC-1: falta RD-11
    T-3:
      DC-1: falta RD-11
      DC-2: falta RD-11

Qué falta (D-5):
  ley_rd:
    En todas las lecturas:
      RD-11 Decisor previsto (expediente.decision_comunicacion.decisor.persona)
  amlr, T-1: nada.
  T-2:
    Solo en algunas:
      RD-11 Decisor previsto (expediente.decision_comunicacion.decisor.persona): con DC-1
  T-3:
    En todas las lecturas:
      RD-11 Decisor previsto (expediente.decision_comunicacion.decisor.persona)

Qué hay que decidir para salir del indeterminado (D-7, D-8):
  T-2:
    DC — ¿Quién decide la comunicación con el AMLR? (R-4, §4.2)
      DC-1: incompleto (falta RD-11)
      DC-2: completo
      Datos: expediente.decision_comunicacion.decisor

Datos informativos (§2):
  Días entre el fin del análisis técnico y la decisión: 4 (RD, art. 25.2: «sin demora»).
  Días entre la decisión y la comunicación: 3 (Ley, art. 18.2: «sin dilación»).
  Más de 10.000 operaciones anuales (RD, art. 23; D-24): indeterminado — OA-1 (2027): no_supera; OA-2 (2028): sin_dato.
```

Cómo leerlo:

- **Estado del registro.** Con la Ley y el RD falta RD-11: la decisión la tomó quien no es el representante. Con el AMLR está completo con las dos lecturas de quién decide: si no lo dice (DC-1), y si decide el responsable del cumplimiento (DC-2), que es quien decidió.
- **Dónde difieren.** Las tres lecturas de la transición dan tres respuestas. Si el AMLR desplaza el art. 25 del RD (T-1), el registro está completo. Si se suman los dos y no se examina su compatibilidad (T-3), está incompleto. Si se suman con prevalencia del AMLR (T-2), depende además de quién decide con el AMLR.
- **Exige actuar.** Qué régimen y qué combinación de lecturas dan `incompleto`, y qué falta en cada una. Es lo que decide el código de salida.
- **Qué hay que decidir.** La pregunta que deja T-2 abierto, con lo que da cada respuesta: si el AMLR no dice quién decide (DC-1), falta RD-11; si decide el responsable del cumplimiento (DC-2), el registro está completo.
- **Datos informativos.** Los días entre el análisis, la decisión y la comunicación, que la herramienta no juzga porque «sin demora» no es un número de días, y si el sujeto supera las 10.000 operaciones anuales del RD, art. 23, que depende de qué año se cuente.

El código de salida es 1, porque alguna lectura exige completar el registro.

## Instalación

Hace falta Python 3.11 o posterior. No tiene dependencias externas: `pip install` solo descarga setuptools para construir el paquete. Desde la raíz del repositorio:

```sh
python3 -m venv .venv
source .venv/bin/activate        # en Windows: .venv\Scripts\activate
pip install .
registro-examen-especial corpus/05-decide-el-responsable-del-cumplimiento.json
```

**Uso:** `registro-examen-especial FICHERO [--json]`. Con `--json`, el mismo informe en JSON, con todas las combinaciones de lecturas, los requisitos de cada una y las rutas de lo que falta. En texto, más de tres combinaciones se resumen.

**Códigos de salida:**
- **1:** alguna combinación de lecturas de algún régimen da `incompleto`: alguna lectura exige completar el registro. También si todas lo dan.
- **0:** ninguna lectura lo exige, aunque los regímenes discrepen; la discrepancia está en el informe. Por ejemplo, una alerta descartada bien registrada es `indeterminado` (depende de si revisarla es evaluar), pero en ninguna lectura le falta nada.
- **2:** el fichero no se puede leer o la entrada no es válida. Los errores de validación salen con su código (`ERR-01` a `ERR-12`) y la ruta del dato.

**Con tu propio registro.** La entrada es un JSON con:
- el sujeto obligado: su actividad y su número de operaciones por año;
- las personas que deciden, votan o revisan, identificadas por un código y con sus cargos;
- los sistemas, con lo que declara la entidad sobre si son sistemas de IA, y cada participación: en qué momento, cuándo, su salida tal como la dio y la intervención humana sobre ella;
- el expediente (fechas, origen, operativa, fases, fuentes, circunstancias consideradas, conclusión y razones, decisión y comunicación) o la alerta descartada.

Cada campo cita el artículo del que sale. El formato, con dos ejemplos, está en [docs/modelo-datos.md](docs/modelo-datos.md). La entrada recoge hechos, no el régimen: el régimen es un parámetro del cálculo.

**El corpus.** Los ocho casos, con su tabla de estados, están en [corpus/README.md](corpus/README.md). Se regeneran con `python corpus/generar.py`, que comprueba cada caso contra su resultado esperado antes de escribirlo. Los resultados esperados están escritos a mano desde la especificación.

**Tests:** `pip install pytest` y `pytest` desde la raíz.

## Qué comprueba

Para un registro, si está `completo`, `incompleto` o `no_exigible`, y qué le falta, en cinco regímenes:

- **`ley_rd`:** la Ley 10/2010 y el RD 304/2014. Quince requisitos (RD-01 a RD-15): fechas, motivo, operativa, fases, gestiones y fuentes (RD, art. 25.1 y 25.3), conclusión y razones, decisión motivada, que decida el representante o el órgano de control interno por mayoría con el voto de cada miembro (art. 25.2), la fecha de la comunicación y que se informe a quien comunicó internamente. Una alerta descartada no exige registro.
- **`amlr`:** el AMLR. Siete requisitos (AM-01 a AM-07): la información y las circunstancias consideradas, los resultados y la copia de la comunicación (art. 77.1.b); si la salida de un sistema debe figurar entre las circunstancias; la intervención humana antes de la decisión (art. 76.5.b); y quién decide.
- **`T-1` a `T-3`:** lo que se exige desde el 10 de julio de 2027 según si el art. 25 del RD sigue aplicándose.
  - T-1: el AMLR lo desplaza.
  - T-2: se suman los dos, y prevalece el AMLR donde se contradicen.
  - T-3: se suman los dos.

Donde la norma no resuelve una pregunta, el cálculo da una lectura por cada respuesta: si la salida de un sistema es una circunstancia considerada, si la intervención humana alcanza la decisión de comunicar, quién decide con el AMLR, si revisar una alerta es evaluar, cómo cuentan las abstenciones, qué fecha decide la norma de un expediente que abarca el 10 de julio de 2027, entre otras. Si las lecturas dan estados distintos, el estado es `indeterminado`, y la salida lo atribuye a las preguntas que lo causan. Las reglas completas, con las decisiones propias numeradas (D-1 a D-26) y su motivo, están en la [especificación del cálculo](docs/especificacion-calculo.md).

## Qué no hace

- **No mira dentro del sistema de IA.** No modela variables, umbrales, reglas ni tipos de alerta, y no interpreta su salida. Por eso no comprueba la condición del AMLR, art. 76.5.a (que el sistema solo trate datos obtenidos en la diligencia debida): eso se comprueba sobre el sistema, no sobre el registro.
- **No clasifica el sistema.** No dice si es de alto riesgo ni si es un sistema de IA según el AI Act. Recoge lo que declara la entidad, que no cambia ningún requisito.
- **No valora.** No dice si la intervención humana fue «significativa», si la decisión se tomó «sin demora», si el examen fue integral ni si la conclusión es acertada.
- **No dice qué lectura es la correcta.** Lo calcula todo y no elige.
- **No compara expedientes.** No comprueba el registro cronológico ni que las decisiones respondan a «criterios homogéneos» (RD, art. 25.2).
- **No calcula plazos de conservación.** Eso lo hace [plazos-conservacion-pbc](https://github.com/mshodai/plazos-conservacion-pbc).
- **No trata la comunicación en sí.** Su contenido y su formato quedan fuera.

## Los once casos que la norma no resuelve

Al analizar los textos aparecieron once puntos en que el resultado no está determinado por un texto único. Entre ellos:
- si la salida de un sistema es una «circunstancia considerada» del AMLR, art. 77.1.b;
- si la intervención humana del art. 76.5.b alcanza la decisión de comunicar;
- si el art. 25 del RD sigue aplicándose desde el 10 de julio de 2027;
- quién decide la comunicación con el AMLR;
- el «Reglamento (UE) 2024/XXX» que el art. 76.5 cita sin identificar;
- si revisar una alerta que se descarta es ya una evaluación que hay que registrar.

Están en [docs/ambiguedades.md](docs/ambiguedades.md), cada uno con qué dice la norma, por qué no determina un comportamiento único, qué hace esta implementación, cómo se señala en la salida y a qué régimen afecta. Ninguno depende del borrador de la Comisión; el mismo documento dice qué partes del repositorio se apoyan en él y qué cambiaría con las directrices finales.

## Fuentes

| Documento | Versión |
|---|---|
| Ley 10/2010, de 28 de abril, de prevención del blanqueo de capitales y de la financiación del terrorismo | Texto consolidado, última modificación de 21 de marzo de 2026 |
| Real Decreto 304/2014, de 5 de mayo, Reglamento de la Ley 10/2010 | Texto consolidado, última modificación de 24 de abril de 2024 |
| Reglamento (UE) 2024/1624 (AMLR), de 31 de mayo de 2024 | Texto publicado en el DO L de 19 de junio de 2024, sin consolidar |
| Reglamento (UE) 2024/1689 (Reglamento de Inteligencia Artificial, AI Act), de 13 de junio de 2024 | Texto original publicado en el DO L de 12 de julio de 2024 |
| Reglamento (UE) 2024/1689, texto consolidado | A 27 de julio de 2026, con el Reglamento (UE) 2026/1744. **Sin efecto jurídico**: es un instrumento de documentación |
| Comisión Europea, «Draft Commission guidelines on the classification of high-risk AI systems under Article 6 of Regulation (EU) 2024/1689 (AI Act)», anexo sobre el anexo III | **Borrador no vinculante.** Publicado el 19 de mayo de 2026; consulta cerrada el 23 de julio de 2026 |

La Ley, el RD y el AMLR se descargaron el 15 de septiembre de 2026, y los demás documentos el 22 de septiembre de 2026. Las URL y las huellas SHA-256 de cada versión están en [docs/fuentes/FUENTES.md](docs/fuentes/FUENTES.md). Los PDF no se redistribuyen.

El borrador de la Comisión no define ningún requisito ni ninguna lectura. Se cita solo como contexto de por qué el AI Act no suele aplicar a estos sistemas como alto riesgo, y siempre como borrador.

**Calendario.**
- **2 de febrero de 2026:** plazo que fijaba el AI Act, art. 6.5, para que la Comisión publicara las directrices sobre la clasificación de los sistemas de alto riesgo. Pasó sin ellas.
- **19 de mayo a 23 de julio de 2026:** consulta del borrador de la Comisión, ampliada desde el 23 de junio.
- **Finales de 2026:** directrices finales, según la Comisión («The final guidelines will be adopted by the end of 2026»).
- **Hasta el 9 de julio de 2027:** se aplican la Ley 10/2010 y el RD 304/2014. La herramienta calcula también el AMLR, para comparar, y avisa de que todavía no es aplicable.
- **10 de julio de 2027:** el AMLR «será aplicable» (art. 90). Ningún texto dice si el art. 25 del RD sigue aplicándose; de ahí T-1 a T-3.
- **2 de diciembre de 2027:** se aplican las reglas de los sistemas de alto riesgo del anexo III del AI Act (art. 113, letra c), en la redacción del Reglamento (UE) 2026/1744, según el texto consolidado).
- **10 de julio de 2029:** aplicación del AMLR a los agentes de fútbol y a los clubes de fútbol profesional (art. 90).

## Otros repositorios del proyecto

- [validador-cadena-verifactu](https://github.com/mshodai/validador-cadena-verifactu): comprueba la integridad de una cadena de registros de facturación de Verifactu.
- [calculo-titularidad-real](https://github.com/mshodai/calculo-titularidad-real): calcula la titularidad real bajo la Ley 10/2010 y el AMLR.
- [plazos-conservacion-pbc](https://github.com/mshodai/plazos-conservacion-pbc): calcula el estado de conservación de la documentación bajo la Ley 10/2010 y el AMLR.
- [plazos-actualizacion-pbc](https://github.com/mshodai/plazos-actualizacion-pbc): calcula la próxima revisión obligatoria de la información de un cliente bajo el RD 304/2014 y el AMLR.

---

Es una implementación de referencia, probada sobre datos sintéticos. No es software de cumplimiento normativo y no constituye asesoramiento jurídico.
