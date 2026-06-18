"""
Tests unitarios para el modelo atómico ControladorDeBomba.

Se invocan directamente las funciones DEVS (extTransition, intTransition,
outputFnc, timeAdvance) sin usar el simulador completo.

Organización por escenarios:
  1. Funcionamiento normal
  2. Cambio de orden médica
  3. Detención
  4. Desvío leve (dentro del margen)
  5. Desvío sostenido >10%
  6. Fin de bolsa
"""

import sys
import os
import pytest

# Agregar el directorio src al path para poder importar los módulos del proyecto
sys.path.insert(
    0,
    os.path.join(os.path.dirname(__file__), "..", "src"),
)

from atomics.controlador_de_bomba import ControladorDeBomba


# ────────────────────────────────────────────────────────────────────
# Fixture
# ────────────────────────────────────────────────────────────────────

@pytest.fixture
def ctrl():
    """Crea una instancia fresca del ControladorDeBomba."""
    return ControladorDeBomba()


# ════════════════════════════════════════════════════════════════════
# Escenario 1 — Funcionamiento normal
# ════════════════════════════════════════════════════════════════════

class TestFuncionamientoNormal:
    """Inicio de infusión, salida, transición interna y caudal dentro del margen."""

    def test_inicio_infusion(self, ctrl):
        """Recibir ordenMedica=50 pasa a fase 'ajustando' con caudal objetivo 50."""
        ctrl.elapsed = 0
        ctrl.extTransition({ctrl.in_ordenMedica: 50})

        assert ctrl.state["fase"] == "ajustando"
        assert ctrl.state["caudalObj"] == 50
        assert ctrl.state["sigma"] == 3.0
        assert ctrl.state["salida"] == (ctrl.out_ajustarCaudal, 50)

    def test_salida_ajustar_caudal(self, ctrl):
        """outputFnc emite el caudal por el puerto out_ajustarCaudal."""
        # Preparar el estado como si acabara de recibir la orden
        ctrl.state["salida"] = (ctrl.out_ajustarCaudal, 50)

        resultado = ctrl.outputFnc()

        assert ctrl.out_ajustarCaudal in resultado
        assert resultado[ctrl.out_ajustarCaudal] == [50]

    def test_post_ajuste_pasiva(self, ctrl):
        """Tras intTransition en fase 'ajustando', el modelo queda pasivo."""
        ctrl.state["fase"] = "ajustando"
        ctrl.state["salida"] = (ctrl.out_ajustarCaudal, 50)
        ctrl.state["sigma"] = 3.0

        ctrl.intTransition()

        assert ctrl.state["sigma"] == float("inf")
        assert ctrl.state["salida"] is None

    def test_caudal_normal_no_alarma(self, ctrl):
        """Caudal dentro del margen (±10%) resetea tiempDesvio a 0."""
        ctrl.state["fase"] = "ajustando"
        ctrl.state["caudalObj"] = 100
        ctrl.state["tiempDesvio"] = 0
        ctrl.state["sigma"] = float("inf")
        ctrl.elapsed = 0

        # 105 está a 5% del objetivo 100 → dentro del margen de 10%
        ctrl.extTransition({ctrl.in_sensorFlujo: 105})

        assert ctrl.state["tiempDesvio"] == 0


# ════════════════════════════════════════════════════════════════════
# Escenario 2 — Cambio de orden médica
# ════════════════════════════════════════════════════════════════════

class TestCambioDeOrden:
    """Una nueva orden médica reemplaza la anterior."""

    def test_cambio_orden_50_a_80(self, ctrl):
        """Cambiar la orden de 50 a 80 actualiza caudalObj y salida."""
        ctrl.state["fase"] = "ajustando"
        ctrl.state["caudalObj"] = 50
        ctrl.state["sigma"] = float("inf")
        ctrl.elapsed = 0

        ctrl.extTransition({ctrl.in_ordenMedica: 80})

        assert ctrl.state["fase"] == "ajustando"
        assert ctrl.state["caudalObj"] == 80
        assert ctrl.state["salida"] == (ctrl.out_ajustarCaudal, 80)
        assert ctrl.state["sigma"] == 3.0


# ════════════════════════════════════════════════════════════════════
# Escenario 3 — Detención
# ════════════════════════════════════════════════════════════════════

class TestDetencion:
    """Orden con caudal 0 detiene la bomba."""

    def test_orden_caudal_cero(self, ctrl):
        """Recibir ordenMedica=0 pasa a 'suspendido' y emite detenerBomba."""
        ctrl.state["fase"] = "ajustando"
        ctrl.state["caudalObj"] = 50
        ctrl.state["sigma"] = float("inf")
        ctrl.elapsed = 0

        ctrl.extTransition({ctrl.in_ordenMedica: 0})

        assert ctrl.state["fase"] == "suspendido"
        assert ctrl.state["caudalObj"] == 0
        assert ctrl.state["tiempDesvio"] == 0
        assert ctrl.state["salida"] == (ctrl.out_detenerBomba, "emitir")
        assert ctrl.state["sigma"] == 0.0

    def test_post_detencion_pasiva(self, ctrl):
        """Tras intTransition en 'suspendido', el modelo queda pasivo."""
        ctrl.state["fase"] = "suspendido"
        ctrl.state["salida"] = (ctrl.out_detenerBomba, "emitir")
        ctrl.state["sigma"] = 0.0

        ctrl.intTransition()

        assert ctrl.state["sigma"] == float("inf")
        assert ctrl.state["salida"] is None


# ════════════════════════════════════════════════════════════════════
# Escenario 4 — Desvío leve (dentro del margen)
# ════════════════════════════════════════════════════════════════════

class TestDesvioLeve:
    """Lecturas del sensor que están dentro del margen de ±10%."""

    def test_desvio_dentro_margen_resetea(self, ctrl):
        """Si el desvío vuelve al margen, tiempDesvio se resetea a 0."""
        ctrl.state["fase"] = "ajustando"
        ctrl.state["caudalObj"] = 100
        ctrl.state["tiempDesvio"] = 3
        ctrl.state["sigma"] = float("inf")
        ctrl.elapsed = 0

        # 108 → desvío de 8%, dentro del 10%
        ctrl.extTransition({ctrl.in_sensorFlujo: 108})

        assert ctrl.state["tiempDesvio"] == 0

    def test_desvio_exacto_margen(self, ctrl):
        """Desvío exacto del 10% (límite) se considera dentro del margen."""
        ctrl.state["fase"] = "ajustando"
        ctrl.state["caudalObj"] = 100
        ctrl.state["tiempDesvio"] = 0
        ctrl.state["sigma"] = float("inf")
        ctrl.elapsed = 0

        # 110 → desvío de 10, margen = 10 → desvio <= margen → ok
        ctrl.extTransition({ctrl.in_sensorFlujo: 110})

        assert ctrl.state["tiempDesvio"] == 0


# ════════════════════════════════════════════════════════════════════
# Escenario 5 — Desvío sostenido >10%
# ════════════════════════════════════════════════════════════════════

class TestDesvioSostenido:
    """Lecturas consecutivas fuera del margen disparan alarmas y bloqueo."""

    def test_incremento_tiempDesvio(self, ctrl):
        """Con tiempDesvio < 5, el contador incrementa en 1."""
        ctrl.state["fase"] = "ajustando"
        ctrl.state["caudalObj"] = 100
        ctrl.state["tiempDesvio"] = 2
        ctrl.state["sigma"] = float("inf")
        ctrl.elapsed = 0

        # 120 → 20% de desvío, fuera del margen
        ctrl.extTransition({ctrl.in_sensorFlujo: 120})

        assert ctrl.state["tiempDesvio"] == 3

    def test_alarma_media_en_tiempDesvio_5(self, ctrl):
        """Al llegar a tiempDesvio==5, se emite alarma media."""
        ctrl.state["fase"] = "ajustando"
        ctrl.state["caudalObj"] = 100
        ctrl.state["tiempDesvio"] = 5
        ctrl.state["sigma"] = float("inf")
        ctrl.elapsed = 0

        ctrl.extTransition({ctrl.in_sensorFlujo: 120})

        assert ctrl.state["tiempDesvio"] == 6
        assert ctrl.state["salida"] == (ctrl.out_alarmaMedia, "emitir")
        assert ctrl.state["sigma"] == 0.0

    def test_incremento_post_alarma_media(self, ctrl):
        """Con 6 <= tiempDesvio < 9, el contador sigue incrementando."""
        ctrl.state["fase"] = "ajustando"
        ctrl.state["caudalObj"] = 100
        ctrl.state["tiempDesvio"] = 7
        ctrl.state["sigma"] = float("inf")
        ctrl.elapsed = 0

        ctrl.extTransition({ctrl.in_sensorFlujo: 120})

        assert ctrl.state["tiempDesvio"] == 8

    def test_alarma_critica_en_tiempDesvio_9(self, ctrl):
        """Al llegar a tiempDesvio==9, se emite alarma crítica y se bloquea."""
        ctrl.state["fase"] = "ajustando"
        ctrl.state["caudalObj"] = 100
        ctrl.state["tiempDesvio"] = 9
        ctrl.state["sigma"] = float("inf")
        ctrl.elapsed = 0

        ctrl.extTransition({ctrl.in_sensorFlujo: 120})

        assert ctrl.state["fase"] == "bloqueando"
        assert ctrl.state["tiempDesvio"] == 10
        assert ctrl.state["salida"] == (ctrl.out_alarmaCritica, "emitir")
        assert ctrl.state["sigma"] == 0.0

    def test_bloqueando_a_bloqueado(self, ctrl):
        """intTransition de 'bloqueando' pasa a 'bloqueado' y emite detenerBomba."""
        ctrl.state["fase"] = "bloqueando"
        ctrl.state["salida"] = (ctrl.out_alarmaCritica, "emitir")
        ctrl.state["sigma"] = 0.0

        ctrl.intTransition()

        assert ctrl.state["fase"] == "bloqueado"
        assert ctrl.state["salida"] == (ctrl.out_detenerBomba, "emitir")
        assert ctrl.state["sigma"] == 0.0

    def test_bloqueado_pasiva(self, ctrl):
        """intTransition de 'bloqueado' deja el modelo pasivo."""
        ctrl.state["fase"] = "bloqueado"
        ctrl.state["salida"] = (ctrl.out_detenerBomba, "emitir")
        ctrl.state["sigma"] = 0.0

        ctrl.intTransition()

        assert ctrl.state["sigma"] == float("inf")
        assert ctrl.state["salida"] is None

    def test_confirmacion_enfermero_desbloquea(self, ctrl):
        """Confirmación de enfermero en 'bloqueado' vuelve a 'suspendido'."""
        ctrl.state["fase"] = "bloqueado"
        ctrl.state["caudalObj"] = 100
        ctrl.state["tiempDesvio"] = 10
        ctrl.state["sigma"] = float("inf")
        ctrl.elapsed = 0

        ctrl.extTransition({ctrl.in_confEnf: "confirmar"})

        assert ctrl.state["fase"] == "suspendido"
        assert ctrl.state["caudalObj"] == 0
        assert ctrl.state["tiempDesvio"] == 0
        assert ctrl.state["salida"] is None
        assert ctrl.state["sigma"] == float("inf")


# ════════════════════════════════════════════════════════════════════
# Escenario 6 — Fin de bolsa
# ════════════════════════════════════════════════════════════════════

class TestFinDeBolsa:
    """Secuencia de fin de bolsa: alarma baja → detener → reemplazar → suspendido."""

    def test_fin_bolsa_en_ajustando(self, ctrl):
        """Recibir finBolsa en 'ajustando' dispara alarma baja."""
        ctrl.state["fase"] = "ajustando"
        ctrl.state["caudalObj"] = 50
        ctrl.state["sigma"] = float("inf")
        ctrl.elapsed = 0

        ctrl.extTransition({ctrl.in_finBolsa: "emitir"})

        assert ctrl.state["fase"] == "fin_bolsa"
        assert ctrl.state["salida"] == (ctrl.out_alarmaBaja, "emitir")
        assert ctrl.state["sigma"] == 0.0

    def test_fin_bolsa_programa_detencion(self, ctrl):
        """Tras emitir alarma baja por fin de bolsa, se programa detenerBomba a los 60s."""
        ctrl.state["fase"] = "fin_bolsa"
        ctrl.state["salida"] = (ctrl.out_alarmaBaja, "emitir")
        ctrl.state["sigma"] = 0.0

        ctrl.intTransition()

        assert ctrl.state["fase"] == "fin_bolsa"
        assert ctrl.state["salida"] == (ctrl.out_detenerBomba, "emitir")
        assert ctrl.state["sigma"] == 60.0

    def test_fin_bolsa_a_reemplazando(self, ctrl):
        """Tras emitir detenerBomba por fin de bolsa, pasa a reemplazar bolsa por 120s."""
        ctrl.state["fase"] = "fin_bolsa"
        ctrl.state["salida"] = (ctrl.out_detenerBomba, "emitir")
        ctrl.state["sigma"] = 60.0

        ctrl.intTransition()

        assert ctrl.state["fase"] == "reemplazando_bolsa"
        assert ctrl.state["caudalObj"] == 0
        assert ctrl.state["tiempDesvio"] == 0
        assert ctrl.state["salida"] is None
        assert ctrl.state["sigma"] == 120.0

    def test_orden_ignorada_en_reemplazando(self, ctrl):
        """Una orden médica positiva se ignora si se está reemplazando la bolsa."""
        ctrl.state["fase"] = "reemplazando_bolsa"
        ctrl.state["caudalObj"] = 0
        ctrl.state["sigma"] = 120.0
        ctrl.elapsed = 0

        ctrl.extTransition({ctrl.in_ordenMedica: 50})

        # La condición `x > 0 and fase != "reemplazando_bolsa"` es False
        assert ctrl.state["fase"] == "reemplazando_bolsa"
        assert ctrl.state["caudalObj"] == 0

    def test_reemplazando_a_suspendido(self, ctrl):
        """Tras agotar el tiempo de reemplazo, vuelve a 'suspendido'."""
        ctrl.state["fase"] = "reemplazando_bolsa"
        ctrl.state["caudalObj"] = 0
        ctrl.state["tiempDesvio"] = 0
        ctrl.state["salida"] = None
        ctrl.state["sigma"] = 120.0

        ctrl.intTransition()

        assert ctrl.state["fase"] == "suspendido"
        assert ctrl.state["sigma"] == float("inf")
