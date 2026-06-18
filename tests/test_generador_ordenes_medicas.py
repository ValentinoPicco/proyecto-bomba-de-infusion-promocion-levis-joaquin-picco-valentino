"""
Tests unitarios para el modelo atómico GeneradorDeOrdenesMedicas.

Se invocan directamente las funciones DEVS (outputFnc, intTransition, timeAdvance)
sin ejecutar el simulador completo.
"""

import sys
import os
import math
import pytest

# Agregar el directorio src al path para que los imports funcionen
sys.path.insert(
    0,
    os.path.join(os.path.dirname(__file__), "..", "src"),
)

from atomics.generador_ordenes_medicas import GeneradorDeOrdenesMedicas


# --------------------------------------------------------------------------- #
# 1. Verificar que emite el primer caudal correctamente
# --------------------------------------------------------------------------- #
def test_emite_primer_caudal():
    """Con escenario [(50, 10)], el estado inicial debe tener caudal=50 y
    sigma=10, y outputFnc debe devolver {out_ordenMedica: [50]}."""
    modelo = GeneradorDeOrdenesMedicas("gen", [(50, 10)])

    # Estado inicial
    assert modelo.state["caudal"] == 50
    assert modelo.state["sigma"] == 10
    assert modelo.timeAdvance() == 10

    # Salida
    salida = modelo.outputFnc()
    assert salida[modelo.out_ordenMedica] == [50]


# --------------------------------------------------------------------------- #
# 2. Verificar la secuencia de órdenes médicas
# --------------------------------------------------------------------------- #
def test_secuencia_de_ordenes():
    """Con escenario [(50, 10), (80, 3600)], luego de la primera
    intTransition el estado debe pasar a caudal=80, sigma=3600."""
    modelo = GeneradorDeOrdenesMedicas("gen", [(50, 10), (80, 3600)])

    # Verificar estado inicial
    assert modelo.state["caudal"] == 50
    assert modelo.state["sigma"] == 10

    # Transición interna: avanza al siguiente paso del escenario
    modelo.intTransition()

    assert modelo.state["caudal"] == 80
    assert modelo.state["sigma"] == 3600
    assert modelo.timeAdvance() == 3600


# --------------------------------------------------------------------------- #
# 3. Verificar que queda pasivo al finalizar el escenario
# --------------------------------------------------------------------------- #
def test_pasiva_al_finalizar():
    """Con escenario [(50, 10)], después de intTransition el sigma debe
    ser infinito (modelo pasivo)."""
    modelo = GeneradorDeOrdenesMedicas("gen", [(50, 10)])

    modelo.intTransition()

    assert modelo.state["sigma"] == float("inf")
    assert modelo.timeAdvance() == float("inf")


# --------------------------------------------------------------------------- #
# 4. Verificar validación de dominio del caudal
# --------------------------------------------------------------------------- #
def test_validacion_dominio():
    """Un caudal fuera del rango [0, 200] debe lanzar ValueError."""
    with pytest.raises(ValueError):
        GeneradorDeOrdenesMedicas("gen", [(250, 10)])


# --------------------------------------------------------------------------- #
# 5. Verificar comportamiento con escenario vacío
# --------------------------------------------------------------------------- #
def test_escenario_vacio():
    """Con escenario vacío [], el estado debe tener caudal=0 y sigma=inf."""
    modelo = GeneradorDeOrdenesMedicas("gen", [])

    assert modelo.state["caudal"] == 0
    assert modelo.state["sigma"] == float("inf")
    assert modelo.timeAdvance() == float("inf")
