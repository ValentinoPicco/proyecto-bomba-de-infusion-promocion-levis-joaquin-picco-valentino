import sys
import os

# Agregamos src al PYTHONPATH para que los imports funcionen correctamente
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from couples.a1 import ModeloAcopladoA1
from couples.a2 import ModeloAcopladoA2


def test_a1_conexiones_internas():
    """
    Instancia el ModeloAcopladoA1 y verifica las conexiones internas (IC).
    """
    a1 = ModeloAcopladoA1(escenario_ordenes=[])
    
    # Verificamos la conexión entre generador y controlador
    assert a1.controlador.in_ordenMedica in a1.generador.out_ordenMedica.outline
    
    # Verificamos la conexión entre sensor y controlador
    assert a1.controlador.in_sensorFlujo in a1.sensor.out_sensorFlujo.outline


def test_a1_conexiones_eic():
    """
    Instancia el ModeloAcopladoA1 y verifica las conexiones de entrada externa (EIC).
    """
    a1 = ModeloAcopladoA1(escenario_ordenes=[])
    
    # Verificamos que los puertos globales conecten hacia adentro
    assert a1.sensor.in_caudalActual in a1.in_caudalActual.outline
    assert a1.controlador.in_finBolsa in a1.in_finBolsa.outline
    assert a1.controlador.in_confEnf in a1.in_confEnf.outline


def test_a2_instanciacion_conexiones():
    """
    Instancia el ModeloAcopladoA2 y verifica que todos sus componentes internos
    (a1, actuador, alarmas, logger) estén correctamente conectados.
    """
    a2 = ModeloAcopladoA2(escenario_ordenes=[])
    
    # 1. Verificamos conexión entre a1 y actuador
    assert a2.actuador.in_ajustarCaudal in a2.a1.out_ajustarCaudal.outline
    assert a2.actuador.in_detenerBomba in a2.a1.out_detenerBomba.outline
    
    # 2. Feedback: Actuador hacia a1 (sensor)
    assert a2.a1.in_caudalActual in a2.actuador.out_caudalActual.outline
    
    # 3. Verificamos conexión entre a1 y alarmas
    assert a2.alarmas.in_alarmaBaja in a2.a1.out_alarmaBaja.outline
    assert a2.alarmas.in_alarmaMedia in a2.a1.out_alarmaMedia.outline
    assert a2.alarmas.in_alarmaCritica in a2.a1.out_alarmaCritica.outline
    
    # 4. Verificamos conexión entre a1 y logger
    assert a2.logger.in_evento in a2.a1.out_notificarEvento.outline

    # Extras EIC/EOC para estar seguros de la integridad de la instanciación de A2
    assert a2.a1.in_finBolsa in a2.in_finBolsa.outline
    assert a2.a1.in_confEnf in a2.in_confEnf.outline
    assert a2.alarmas.in_confirmacionEnfermero in a2.in_confEnf.outline
    assert a2.out_notificacionAlarma in a2.alarmas.out_notificacionAlarma.outline
