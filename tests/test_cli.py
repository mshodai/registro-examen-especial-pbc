"""La línea de órdenes registro-examen-especial y sus códigos de salida (especificación, §9.1)."""

import json
import subprocess
import sys
import tomllib
from pathlib import Path

import pytest

from ayudas import alerta, decisor_persona, expediente, participacion, registro
from registro.cli import main

RAIZ = Path(__file__).resolve().parent.parent


@pytest.fixture
def fichero(tmp_path):
    def escribir(datos, nombre="entrada.json"):
        ruta = tmp_path / nombre
        if isinstance(datos, bytes):
            ruta.write_bytes(datos)
        else:
            ruta.write_text(datos if isinstance(datos, str) else json.dumps(datos), encoding="utf-8")
        return str(ruta)

    return escribir


COMPLETO = registro(expediente(decisor=decisor_persona("P-1")))
ALERTA_COMPLETA = registro(
    alerta_=alerta(), participaciones=[participacion("IA-1", "SIS-A", "generacion_alerta", "2027-10-04")]
)
ALERTA_VACIA = registro(
    alerta_=alerta(revision="2028-05-10", fuentes=[], circunstancias=[], resultado=None),
    participaciones=[participacion("IA-1", "SIS-A", "generacion_alerta", "2028-05-09")],
)


def test_codigo_0_si_ninguna_lectura_exige_actuar(fichero, capsys):
    assert main([fichero(COMPLETO)]) == 0
    assert "Los cinco regímenes coinciden." in capsys.readouterr().out


def test_codigo_0_con_indeterminado_entre_completo_y_no_exigible(fichero, capsys):
    # D-25: la alerta bien registrada es indeterminado por R-6, pero en ninguna lectura falta nada.
    assert main([fichero(ALERTA_COMPLETA)]) == 0
    assert "indeterminado" in capsys.readouterr().out


def test_codigo_1_si_alguna_lectura_da_incompleto(fichero, capsys):
    assert main([fichero(ALERTA_VACIA)]) == 1
    assert "Sí (D-25). Lo exigen:" in capsys.readouterr().out


def test_codigo_1_con_incompleto_en_todas_las_lecturas(fichero):
    # D-25: aunque el estado no sea dudoso.
    assert main([fichero(registro(expediente(decisor=decisor_persona("P-4"))))]) == 1


def test_json(fichero, capsys):
    assert main([fichero(ALERTA_VACIA), "--json"]) == 1
    datos = json.loads(capsys.readouterr().out)
    assert datos["exige_actuar"]["valor"] is True
    assert {a["regimen"] for a in datos["exige_actuar"]["activado_por"]} == {"amlr", "T-1", "T-2", "T-3"}


def test_entrada_no_valida(fichero, capsys):
    assert main([fichero({"version_modelo": 2})]) == 2
    assert capsys.readouterr().out.startswith("La entrada no es válida")
    assert main([fichero("{"), "--json"]) == 2
    assert json.loads(capsys.readouterr().out)["valida"] is False


@pytest.mark.parametrize(
    "ruta, mensaje",
    [
        (lambda f, tmp: str(tmp / "no-existe.json"), "no existe el fichero"),
        (lambda f, tmp: str(tmp), "es un directorio"),
        (lambda f, tmp: f("{}".encode("utf-16")), "no está codificado en UTF-8"),
    ],
)
def test_fichero_ilegible(fichero, tmp_path, capsys, ruta, mensaje):
    assert main([ruta(fichero, tmp_path)]) == 2
    salida = capsys.readouterr()
    assert salida.out == ""
    assert salida.err.startswith("registro-examen-especial: error: ")
    assert mensaje in salida.err


def test_uso_incorrecto(capsys):
    with pytest.raises(SystemExit) as salida:
        main([])
    assert salida.value.code == 2
    assert "uso: registro-examen-especial" in capsys.readouterr().err


def test_ayuda(capsys):
    with pytest.raises(SystemExit) as salida:
        main(["--help"])
    assert salida.value.code == 0
    ayuda = capsys.readouterr().out
    assert "códigos de salida" in ayuda and "--json" in ayuda


def test_punto_de_entrada_declarado():
    proyecto = tomllib.loads((RAIZ / "pyproject.toml").read_text(encoding="utf-8"))
    assert proyecto["project"]["scripts"] == {"registro-examen-especial": "registro.cli:main"}


def test_como_modulo(fichero):
    resultado = subprocess.run(
        [sys.executable, "-m", "registro.cli", fichero(COMPLETO)],
        capture_output=True,
        text=True,
        env={"PYTHONPATH": str(RAIZ / "src")},
    )
    assert resultado.returncode == 0, resultado.stderr
    assert resultado.stdout.startswith("Expediente EXP-EJEMPLO")
