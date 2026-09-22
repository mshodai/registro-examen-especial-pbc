# Corpus

Registros sintéticos con su resultado esperado. Lo genera `corpus/generar.py`, que comprueba cada caso con el código de `src/` antes de escribirlo. No se edita a mano.

```
python corpus/generar.py
```

Cada caso tiene la entrada (`NN-nombre.json`, según `docs/modelo-datos.md`) y el resultado esperado (`NN-nombre.esperado.json`): en cada uno de los cinco regímenes, el estado, las decisiones que hay que tomar para salir de cada `indeterminado` (con los estados de cada respuesta y de qué depende aún), los requisitos que faltan en todas las lecturas y los que faltan solo en algunas, y los códigos D-n de los avisos. Los resultados esperados están escritos a mano en `generar.py` a partir de `docs/especificacion-calculo.md`. El código de salida es el de `registro-examen-especial` (§9.1): 1 si alguna combinación de lecturas de algún régimen da `incompleto`; 0 si ninguna (D-25).

Los datos son sintéticos: identificadores con «FICTICIO», motivos genéricos e inventados y salidas de los sistemas como cadenas opacas (`SALIDA-FICTICIO-n`).

| Caso | ley_rd | amlr | T-1 | T-2 | T-3 | Código |
|---|---|---|---|---|---|---|
| 01-expediente-completo | completo | completo | completo | completo | completo | 0 |
| 02-salida-del-sistema-no-consta-como-circunstancia | completo | indeterminado | indeterminado | indeterminado | indeterminado | 1 |
| 03-alerta-descartada-revisar-es-evaluar | no_exigible | indeterminado | indeterminado | indeterminado | indeterminado | 1 |
| 04-propuesta-de-decision-sin-revision-humana | completo | indeterminado | indeterminado | indeterminado | indeterminado | 1 |
| 05-decide-el-responsable-del-cumplimiento | incompleto | completo | completo | indeterminado | incompleto | 1 |
| 06-abstencion-en-el-organo-de-control-interno | indeterminado | indeterminado | indeterminado | indeterminado | indeterminado | 1 |
| 07-abierto-antes-y-cerrado-despues-del-10-de-julio-de-2027 | completo | incompleto | indeterminado | indeterminado | indeterminado | 1 |
| 08-comunicacion-interna-con-alerta-incorporada | completo | indeterminado | indeterminado | indeterminado | indeterminado | 1 |

## Qué demuestra cada caso

**01-expediente-completo.** Expediente de 2028 sin sistemas, con fases, fuentes, circunstancias, conclusión y razones, decidido por quien es a la vez representante ante el Servicio Ejecutivo y responsable del cumplimiento normativo, y comunicado con copia. Completo en los cinco regímenes y con todas las lecturas: código 0.

**02-salida-del-sistema-no-consta-como-circunstancia.** Expediente de 2028 en el que un sistema participó en el análisis (fase FA-FICTICIO-1), pero ninguna circunstancia considerada cita su salida. Con la Ley y el RD está completo. Con el AMLR depende de R-1: si toda salida es información considerada (SC-1) o si basta con que la haya usado una fase (SC-2), falta AM-04; si la salida no es una circunstancia (SC-3), está completo.

**03-alerta-descartada-revisar-es-evaluar.** Alerta generada por un sistema el 2028-05-09 y revisada y descartada al día siguiente, sin registrar fuentes, circunstancias ni resultado. La Ley y el RD no exigen registro. Con el AMLR depende de R-6: si revisar la alerta no es evaluar (AD-1), no es exigible; si lo es (AD-2), faltan la información, las circunstancias y el resultado del art. 77.1.b.

**04-propuesta-de-decision-sin-revision-humana.** Expediente de 2028 en el que un sistema, que la entidad declara no saber si es un sistema de IA, propone la decisión de comunicar dos días antes de que se tome, y nadie revisa su salida. Con la Ley y el RD está completo. Con el AMLR depende de R-2: si la intervención humana del art. 76.5.b no alcanza la decisión de comunicar (IH-1), completo; si la alcanza (IH-2, IH-3), falta AM-06. La declaración no cambia nada (D-18).

**05-decide-el-responsable-del-cumplimiento.** Expediente de 2028 en el que decide la persona responsable del cumplimiento normativo, que no es el representante ante el Servicio Ejecutivo. Con la Ley y el RD falta RD-11; con el AMLR está completo. Las lecturas de la transición divergen (R-3): T-1 completo, T-3 incompleto y T-2 depende además de quién decide con el AMLR (R-4).

**06-abstencion-en-el-organo-de-control-interno.** Expediente de 2026 decidido por el órgano de control interno con dos votos a favor de comunicar, uno en contra y una abstención. Si las abstenciones no cuentan (MA-1) hay mayoría; si cuentan (MA-2), no (R-8). Antes del 10 de julio de 2027, T-1 a T-3 son la Ley y el RD. El AMLR se calcula como comparación.

**07-abierto-antes-y-cerrado-despues-del-10-de-julio-de-2027.** Expediente abierto el 2027-06-21 y cerrado el 2027-07-23, sin circunstancias consideradas. Con la Ley y el RD está completo; con el AMLR falta AM-02. En la transición depende de qué fecha decide la norma (R-11): la apertura (FT-1) o el cierre (FT-2).

**08-comunicacion-interna-con-alerta-incorporada.** Expediente de 2028 abierto por la comunicación interna de un empleado, al que después se suma una alerta generada por un sistema sobre la misma operativa. Se informa al comunicante de la decisión. Con la Ley y el RD está completo. Con el AMLR, la alerta incorporada no figura en ninguna circunstancia: falta AM-04 solo si toda salida es información considerada (SC-1), porque ninguna fase la usó.
