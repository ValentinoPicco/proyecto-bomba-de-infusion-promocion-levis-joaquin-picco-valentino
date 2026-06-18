"""
Tests unitarios para el modelo atómico SensorDeFlujo.

Se verifican:
- Período de muestreo de 1 segundo (sigma inicial y tras intTransition).
- Reporte correcto del caudal en la salida.
- Actualización del caudal al recibir un evento externo.
- Validación del rango de caudal (0–200 ml/h).
- Descuento correcto del tiempo elapsed sobre sigma.
"""

import sys
import os
import pytest

# Agregar el directorio src al path para poder importar los modelos
sys.path.insert(
    0,
    os.path.join(
        os.path.dirname(__file__),
        "..",
        "src",
    ),
)

from atomics.sensor_de_flujo import SensorDeFlujo


# ---------- Helpers ----------

def _crear_sensor() -> SensorDeFlujo:
    """Crea una instancia fresca de SensorDeFlujo."""
    return SensorDeFlujo()


# ---------- Tests ----------


def test_periodo_muestreo_1s():
    """Verifica que el sigma inicial es 1.0 y que intTransition lo restablece a 1.0."""
    sensor = _crear_sensor()

    # Sigma inicial debe ser 1.0
    assert sensor.timeAdvance() == 1.0

    # Tras una transición interna, sigma debe restablecerse a 1.0
    sensor.intTransition()
    assert sensor.state["sigma"] == 1.0
    assert sensor.timeAdvance() == 1.0


def test_reporte_caudal_recibido():
    """Verifica que outputFnc reporta el caudal almacenado en el estado."""
    sensor = _crear_sensor()
    sensor.state["caudal"] = 75.0

    salida = sensor.outputFnc()

    assert salida == {sensor.out_sensorFlujo: [75.0]}


def test_actualizacion_caudal():
    """
    Verifica que al recibir un evento externo con caudal 100.0
    (elapsed=0.5), el estado se actualiza correctamente:
    - caudal pasa a 100.0
    - sigma se descuenta según elapsed: 1.0 - 0.5 = 0.5
    """
    sensor = _crear_sensor()
    sensor.elapsed = 0.5

    sensor.extTransition({sensor.in_caudalActual: 100.0})

    assert sensor.state["caudal"] == 100.0
    assert sensor.state["sigma"] == pytest.approx(0.5)


def test_validacion_rango():
    """
    Verifica que un caudal fuera del rango físico (0–200 ml/h)
    lanza un ValueError.
    """
    sensor = _crear_sensor()
    sensor.elapsed = 0.0

    with pytest.raises(ValueError, match="Lectura anómala del sensor"):
        sensor.extTransition({sensor.in_caudalActual: 250})


def test_descuento_elapsed():
    """
    Verifica que sigma se descuenta correctamente por el tiempo
    transcurrido (elapsed). Con elapsed=0.3 y sigma inicial 1.0,
    el nuevo sigma debe ser 0.7.
    """
    sensor = _crear_sensor()
    sensor.elapsed = 0.3

    sensor.extTransition({sensor.in_caudalActual: 50})

    assert sensor.state["sigma"] == pytest.approx(0.7)
    assert sensor.state["caudal"] == 50
