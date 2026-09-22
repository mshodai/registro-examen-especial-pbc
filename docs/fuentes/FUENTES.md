# Fuentes

Documentos que usa el proyecto. Los PDF no se redistribuyen (están en `.gitignore`), así que cada uno debe descargarse de su URL y guardarse en `docs/fuentes/` con el nombre indicado.

Hay tres grupos:

- **Normativa de prevención del blanqueo** (Ley 10/2010, RD 304/2014 y AMLR): la que define el registro del examen especial. Estas copias proceden de `plazos-actualizacion-pbc` (`docs/fuentes/`), que a su vez las tomó de `plazos-conservacion-pbc` y este de `calculo-titularidad-real`. Su SHA-256 coincide con el que figura en el `FUENTES.md` de `plazos-actualizacion-pbc` para los mismos ficheros, así que son la misma versión.
- **Reglamento de Inteligencia Artificial** (Reglamento (UE) 2024/1689, «AI Act»), en dos versiones:
  - el **texto original** publicado en el Diario Oficial de la Unión Europea, que es el auténtico;
  - el **texto consolidado a 27 de julio de 2026**, que incorpora la modificación del Reglamento (UE) 2026/1744 y dos rectificaciones. **Por sí solo no tiene efecto jurídico.** Su primera página lo dice: «Este texto es exclusivamente un instrumento de documentación y no surte efecto jurídico. [...] Las versiones auténticas de los actos pertinentes, incluidos sus preámbulos, son las publicadas en el Diario Oficial de la Unión Europea». Se usa para saber qué dice hoy el AI Act; cuando una cita importa, se contrasta con el original y con el acto modificativo.

  El AI Act no define ningún campo del registro. Se usa para dos cosas: saber qué es un «sistema de IA», porque el art. 76.5 del AMLR remite a su art. 3, punto 1, y documentar las obligaciones que el propio AI Act puede imponer al sujeto obligado como responsable del despliegue.
- **Borrador de directrices de la Comisión** sobre la clasificación de sistemas de IA de alto riesgo (art. 6 del AI Act). **Es un borrador no vinculante.** Se publicó para consulta de las partes interesadas, y el propio documento lo advierte: «These Guidelines are still a draft document» [estas directrices siguen siendo un borrador]. Ni siquiera las directrices finales serán norma. Se usa solo para documentar cómo propone la Comisión clasificar un sistema de IA usado en la prevención del blanqueo, y siempre se cita como borrador.

**Qué significa cada columna:**

- **Autor.** Órgano emisor, tal como figura en la cabecera del documento. Entre paréntesis, el editor del PDF según sus metadatos (`pdfinfo`).
- **Versión o fecha declarada.** Copiada literalmente del documento.
- **Fecha de descarga.**
  - En la normativa de prevención del blanqueo, es la de la descarga original en `calculo-titularidad-real`, tal como la recoge el `FUENTES.md` de `plazos-actualizacion-pbc`. Las copias de este repositorio se crearon el 2026-09-22.
  - En los otros tres documentos, es la fecha en que el fichero se añadió a este repositorio (`kMDItemDateAdded`: 2026-09-22). Los metadatos de origen de macOS (`kMDItemWhereFroms`) solo guardan el dominio (`https://www.boe.es/`, `https://eur-lex.europa.eu/`, `https://digital-strategy.ec.europa.eu/`), no la URL completa.
- **URL.**
  - En la normativa de prevención del blanqueo, se copian de `plazos-actualizacion-pbc`. Todas se comprobaron por descarga el 22/09/2026: cada una devolvió un fichero idéntico al local (mismo SHA-256), también la de EUR-Lex. EUR-Lex rechaza a veces las descargas automáticas: responde `202` con un cuerpo vacío. Por eso, en la primera comprobación, el 2026-09-15, su URL no se pudo comprobar, y el 22/09/2026 hicieron falta varios intentos.
  - En los otros tres documentos, se da la página de referencia y, si se ha localizado, el enlace de descarga del PDF. Lo comprobado el 2026-09-22 se indica en cada fila.

## Documentos

| Fichero | Título | Autor | Versión o fecha declarada | Descarga | URL |
|---|---|---|---|---|---|
| `BOE-A-2010-6737-consolidado.pdf` | Ley 10/2010, de 28 de abril, de prevención del blanqueo de capitales y de la financiación del terrorismo | Jefatura del Estado (Agencia Estatal Boletín Oficial del Estado) | Texto consolidado. «Última modificación: 21 de marzo de 2026». Original: «BOE» núm. 103, de 29 de abril de 2010 | 2026-09-15 | https://www.boe.es/buscar/pdf/2010/BOE-A-2010-6737-consolidado.pdf · ficha: https://www.boe.es/buscar/act.php?id=BOE-A-2010-6737 |
| `BOE-A-2014-4742-consolidado.pdf` | Real Decreto 304/2014, de 5 de mayo, por el que se aprueba el Reglamento de la Ley 10/2010, de 28 de abril, de prevención del blanqueo de capitales y de la financiación del terrorismo | Ministerio de Economía y Competitividad (Agencia Estatal Boletín Oficial del Estado) | Texto consolidado. «Última modificación: 24 de abril de 2024». Original: «BOE» núm. 110, de 06 de mayo de 2014 | 2026-09-15 | https://www.boe.es/buscar/pdf/2014/BOE-A-2014-4742-consolidado.pdf · ficha: https://www.boe.es/buscar/act.php?id=BOE-A-2014-4742 |
| `OJ_L_202401624_ES_TXT.pdf` | Reglamento (UE) 2024/1624 del Parlamento Europeo y del Consejo, de 31 de mayo de 2024, relativo a la prevención de la utilización del sistema financiero para el blanqueo de capitales o la financiación del terrorismo (AMLR) | Parlamento Europeo y Consejo (Oficina de Publicaciones de la Unión Europea) | Texto publicado, no consolidado: «DO L de 19.6.2024». No declara fecha de modificación. Art. 90: aplicable a partir del 10 de julio de 2027 (10 de julio de 2029 para las entidades del art. 3, punto 3, letras n) y o)) | 2026-09-15 | https://eur-lex.europa.eu/legal-content/ES/TXT/PDF/?uri=OJ:L_202401624 (comprobado el 22/09/2026 por descarga) · ELI impreso en el documento: http://data.europa.eu/eli/reg/2024/1624/oj |
| `AI-Act-DOUE-original.pdf` | Reglamento (UE) 2024/1689 del Parlamento Europeo y del Consejo, de 13 de junio de 2024, por el que se establecen normas armonizadas en materia de inteligencia artificial y por el que se modifican los Reglamentos (CE) n.º 300/2008, (UE) n.º 167/2013, (UE) n.º 168/2013, (UE) 2018/858, (UE) 2018/1139 y (UE) 2019/2144 y las Directivas 2014/90/UE, (UE) 2016/797 y (UE) 2020/1828 (Reglamento de Inteligencia Artificial) | Parlamento Europeo y Consejo (Oficina de Publicaciones de la Unión Europea) | **Texto original, auténtico.** «DO L de 12.7.2024», serie L, 2024/1689. No incorpora modificaciones ni rectificaciones posteriores | 2026-09-22 | Ficha del BOE: https://www.boe.es/buscar/doc.php?id=DOUE-L-2024-81079 · PDF: https://www.boe.es/doue/2024/1689/L00001-00144.pdf. Comprobado el 2026-09-22: la ficha responde `200`, y el PDF descargado con `curl` tiene el mismo SHA-256 que la copia local · ELI impreso en el documento: http://data.europa.eu/eli/reg/2024/1689/oj |
| `CELEX_02024R1689-20260727_ES_TXT.pdf` | Reglamento (UE) 2024/1689 (Reglamento de Inteligencia Artificial), texto consolidado | Oficina de Publicaciones de la Unión Europea (metadatos: «Publications Office») | **Texto consolidado sin efecto jurídico.** Cabecera: «02024R1689 — ES — 27.07.2026 — 001.001». Incorpora: «►M1 Reglamento (UE) 2026/1744 del Parlamento Europeo y del Consejo de 8 de julio de 2026», DO L 1744 de 24.7.2026; rectificaciones «►C1» (DO L 90802 de 9.10.2025) y «►C2» (DO L 90343 de 4.5.2026) | 2026-09-22 | Página: https://eur-lex.europa.eu/legal-content/ES/TXT/?uri=CELEX%3A02024R1689-20260727 · PDF: https://eur-lex.europa.eu/legal-content/ES/TXT/PDF/?uri=CELEX:02024R1689-20260727 (comprobado el 22/09/2026 por descarga: mismo SHA-256 que la copia local. Los primeros intentos de ese día recibieron de EUR-Lex `202` sin contenido, tanto en la página como en el PDF) |
| `Comision-borrador-directrices-alto-riesgo-AnexoIII.pdf` | «Draft Commission guidelines on the classification of high-risk AI systems under Article 6 of Regulation (EU) 2024/1689 (AI Act) for stakeholder consultation» (proyecto de directrices de la Comisión sobre la clasificación de los sistemas de IA de alto riesgo del art. 6 del AI Act, para consulta). Es el anexo dedicado al anexo III del AI Act. Solo en inglés | Comisión Europea (el PDF no declara autor ni editor en sus metadatos; fecha de creación: 19 de mayo de 2026) | **Borrador no vinculante.** «Brussels, XXX», «[…](2026) XXX draft»: sin fecha ni número. Página de la Comisión: publicado el «19 May 2026». Consulta: ver el párrafo siguiente | 2026-09-22 | Página del borrador: https://digital-strategy.ec.europa.eu/en/library/draft-commission-guidelines-classification-high-risk-ai-systems · descarga del anexo III: https://ec.europa.eu/newsroom/dae/redirection/document/128561. Comprobado el 2026-09-22: el PDF descargado con `curl` desde ese enlace tiene el mismo SHA-256 que la copia local. La misma página ofrece otros dos PDF que no se han descargado: los principios generales (`document/128559`) y el anexo I (`document/128560`) |

**Consulta del borrador de la Comisión.** Comprobado el 2026-09-22 en las páginas de la Comisión:

- La nota de prensa de 19 de mayo de 2026 invita a opinar «by 23 June 2026». Esa es la fecha de cierre que suele citarse.
- La página de la consulta (https://digital-strategy.ec.europa.eu/en/news/consultation-guidelines-high-risk, «Last update 16 June 2026») dice otra cosa: «Closing: 23 July 2026». Y lo explica: «The consultation was originally open for 6 weeks until 23 June. However, the Commission has received requests [...] to extend it further by 4 weeks. [...] the deadline was extended to 23 July 2026» [la consulta estaba abierta en principio seis semanas, hasta el 23 de junio; a petición de varias asociaciones se amplió cuatro semanas, hasta el 23 de julio de 2026].
- Las dos fechas son anteriores a la de descarga: la consulta está cerrada en cualquier caso. Este proyecto toma como fecha de cierre el **23 de julio de 2026**, la de la página de la consulta, que es posterior a la nota de prensa y la corrige.
- **Directrices finales.** La misma página: «The final guidelines will be adopted by the end of 2026» [las directrices finales se adoptarán a finales de 2026]. En la fecha de descarga, la página del borrador solo ofrece el borrador.

**Plazo del art. 6.5 del AI Act.** El art. 6.5 fija: «La Comisión, previa consulta al Consejo Europeo de Inteligencia Artificial (en lo sucesivo, «Consejo de IA»), y a más tardar el 2 de febrero de 2026, proporcionará directrices que especifiquen la aplicación práctica del presente artículo [...] junto con una lista exhaustiva de ejemplos prácticos de casos de uso de sistemas de IA que sean de alto riesgo y que no sean de alto riesgo». El texto es igual en el original y en el consolidado: el Reglamento (UE) 2026/1744 no cambió esa fecha. Es un hecho que el 2 de febrero de 2026 pasó sin directrices: el borrador se publicó el 19 de mayo de 2026 y las finales se anuncian para finales de 2026. Este proyecto no saca de ese retraso ninguna consecuencia jurídica. Cuando se publiquen las directrices finales, habrá que añadirlas aquí como documento distinto y revisar lo que el proyecto toma del borrador.

**Fechas de aplicación del AI Act que cambió el Reglamento (UE) 2026/1744.** Se anotan porque deciden desde cuándo rigen las obligaciones de los sistemas de alto riesgo:

- Original, art. 113: «Será aplicable a partir del 2 de agosto de 2026», con excepciones; la letra c) solo aplaza el art. 6.1 al 2 de agosto de 2027.
- Consolidado, art. 113, letra c): el capítulo III, secciones 1 a 3, salvo el art. 6.5, será aplicable a partir del «2 de diciembre de 2027 en lo que respecta a los sistemas de IA clasificados como de alto riesgo en virtud del artículo 6, apartado 2, y el anexo III», y del «2 de agosto de 2028» para los del art. 6.1 y el anexo I.

Este proyecto no ha leído el Reglamento (UE) 2026/1744 en su publicación oficial: lo conoce solo a través del consolidado.

## Huellas SHA-256

Sirven para comprobar que una copia local es la misma versión con la que se hizo el análisis. El BOE y EUR-Lex regeneran los PDF cuando cambia el texto consolidado, así que una huella distinta indica una versión distinta. En el borrador de la Comisión, una huella distinta puede indicar que la Comisión ha sustituido el fichero.

```
4782a40bcf44165a97bc361520fd2b348acf7efbdfaa0a8d876c58332ff8601d  BOE-A-2010-6737-consolidado.pdf
59d7be80313780a8cf48e1f3f87b5bd2860855a126472c0374e1c30c7fc19f0d  BOE-A-2014-4742-consolidado.pdf
666f18e1b5d4dd6bb7e927328bd8d84420d0919e692288f0b917c357df690974  OJ_L_202401624_ES_TXT.pdf
29e6d41f41cc0efea6b5f8a1418a7ef31e9422f9eba0c297ddc7e7ed7f357b1c  AI-Act-DOUE-original.pdf
be5a4c591c71ebe5e8b9be36336c7c2a6aac0a0fd895430f8704ecce7365008f  CELEX_02024R1689-20260727_ES_TXT.pdf
b1df0ffb30310e126c7e060e03c9b5aab97c0a2ab61a2f3e3e00ede3655e2792  Comision-borrador-directrices-alto-riesgo-AnexoIII.pdf
```

Para comprobarlas: `cd docs/fuentes && shasum -a 256 -c` pegando el bloque anterior en la entrada estándar.

## Datos para la vigilancia automática

Repite en formato legible por máquina el fichero, la URL de descarga y la huella SHA-256 de cada documento de las secciones anteriores. Lo lee el script de `vigilancia-fuentes`, que comprueba que coincida con el texto. Si difieren, prevalece el texto.

En los borradores, `paginas` recoge sus páginas oficiales, donde se anunciarían las directrices finales. Para cada página se guardan las frases sobre directrices finales y los enlaces de descarga que ofrecía el 2026-09-22. El script avisa si aparece otra frase u otra descarga.

```json
{
  "documentos": [
    {
      "fichero": "BOE-A-2010-6737-consolidado.pdf",
      "url": "https://www.boe.es/buscar/pdf/2010/BOE-A-2010-6737-consolidado.pdf",
      "sha256": "4782a40bcf44165a97bc361520fd2b348acf7efbdfaa0a8d876c58332ff8601d"
    },
    {
      "fichero": "BOE-A-2014-4742-consolidado.pdf",
      "url": "https://www.boe.es/buscar/pdf/2014/BOE-A-2014-4742-consolidado.pdf",
      "sha256": "59d7be80313780a8cf48e1f3f87b5bd2860855a126472c0374e1c30c7fc19f0d"
    },
    {
      "fichero": "OJ_L_202401624_ES_TXT.pdf",
      "url": "https://eur-lex.europa.eu/legal-content/ES/TXT/PDF/?uri=OJ:L_202401624",
      "sha256": "666f18e1b5d4dd6bb7e927328bd8d84420d0919e692288f0b917c357df690974"
    },
    {
      "fichero": "AI-Act-DOUE-original.pdf",
      "url": "https://www.boe.es/doue/2024/1689/L00001-00144.pdf",
      "sha256": "29e6d41f41cc0efea6b5f8a1418a7ef31e9422f9eba0c297ddc7e7ed7f357b1c"
    },
    {
      "fichero": "CELEX_02024R1689-20260727_ES_TXT.pdf",
      "url": "https://eur-lex.europa.eu/legal-content/ES/TXT/PDF/?uri=CELEX:02024R1689-20260727",
      "sha256": "be5a4c591c71ebe5e8b9be36336c7c2a6aac0a0fd895430f8704ecce7365008f"
    },
    {
      "fichero": "Comision-borrador-directrices-alto-riesgo-AnexoIII.pdf",
      "url": "https://ec.europa.eu/newsroom/dae/redirection/document/128561",
      "sha256": "b1df0ffb30310e126c7e060e03c9b5aab97c0a2ab61a2f3e3e00ede3655e2792",
      "borrador": {
        "paginas": [
          {
            "url": "https://digital-strategy.ec.europa.eu/en/library/draft-commission-guidelines-classification-high-risk-ai-systems",
            "menciones_conocidas": [],
            "descargas_conocidas": [
              "https://ec.europa.eu/newsroom/dae/redirection/document/128559",
              "https://ec.europa.eu/newsroom/dae/redirection/document/128560",
              "https://ec.europa.eu/newsroom/dae/redirection/document/128561"
            ]
          },
          {
            "url": "https://digital-strategy.ec.europa.eu/en/news/consultation-guidelines-high-risk",
            "menciones_conocidas": [
              "The final guidelines will be adopted by the end of 2026.",
              "Feedback received will be considered by the Commission in the final version of the guidelines."
            ],
            "descargas_conocidas": []
          }
        ]
      }
    }
  ]
}
```
