"""Línea de órdenes: registro-examen-especial FICHERO [--json]."""

import argparse
import sys

from registro.carga import cargar_fichero
from registro.salida import como_json, informe, texto

EPILOG = (
    "códigos de salida: 1 si alguna combinación de lecturas de alguno de los cinco regímenes "
    "(ley_rd, amlr, T-1 a T-3) da «incompleto», es decir, si alguna lectura exige completar el "
    "registro; 0 si ninguna lo exige, aunque los regímenes discrepen (la discrepancia está en el "
    "informe); 2 si el fichero no se puede leer o la entrada no es válida."
)


class _Formato(argparse.HelpFormatter):
    def add_usage(self, usage, actions, groups, prefix=None):
        return super().add_usage(usage, actions, groups, prefix or "uso: ")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        prog="registro-examen-especial",
        description=(
            "Comprueba si el registro de un examen especial de prevención del blanqueo de capitales, o de "
            "una alerta revisada y descartada, está completo según la Ley 10/2010 y el RD 304/2014, según el "
            "AMLR y según cada lectura de la transición entre ambos; dice qué le falta y qué hay que decidir "
            "para salir de cada «indeterminado». Es un cálculo bajo las lecturas que declara la "
            "especificación, no una determinación jurídica."
        ),
        epilog=EPILOG,
        formatter_class=_Formato,
        add_help=False,
    )
    argumentos = parser.add_argument_group("argumentos")
    argumentos.add_argument("fichero", help="fichero JSON con el registro (docs/modelo-datos.md)")
    opciones = parser.add_argument_group("opciones")
    opciones.add_argument("-h", "--help", action="help", help="muestra esta ayuda y termina")
    opciones.add_argument("--json", action="store_true", help="emite el informe en JSON en lugar de texto")
    args = parser.parse_args(argv)  # un uso incorrecto termina con código 2 (argparse)

    try:
        carga = cargar_fichero(args.fichero)
    except FileNotFoundError:
        return _error(parser, f"no existe el fichero {args.fichero}")
    except IsADirectoryError:
        return _error(parser, f"{args.fichero} es un directorio")
    except UnicodeDecodeError:
        return _error(parser, f"el fichero {args.fichero} no está codificado en UTF-8")
    except OSError as e:
        return _error(parser, f"no se puede leer el fichero {args.fichero}: {e.strerror}")

    inf = informe(carga)
    if args.json:
        print(como_json(inf))
    else:
        print(texto(inf), end="")
    return codigo_de_salida(inf)


def codigo_de_salida(inf) -> int:
    """Especificación, §9.1."""
    if not inf.valida:
        return 2
    # D-25: 1 si alguna lectura exige actuar; la discrepancia entre regímenes no cuenta.
    return 1 if inf.exige_actuar else 0


def _error(parser, mensaje):
    print(f"{parser.prog}: error: {mensaje}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
