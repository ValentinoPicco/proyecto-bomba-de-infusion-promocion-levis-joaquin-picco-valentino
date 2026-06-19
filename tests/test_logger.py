import sys
import os
import pytest

# Agregar src al path para importar el modelo
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from atomics.logger import Logger

def test_acumulacion_eventos():
    """
    Prueba que el modelo agrega eventos al historial al recibirlos por su puerto de entrada.
    """
    logger = Logger()
    
    # Simular tiempo transcurrido
    logger.elapsed = 2.0
    
    # Evento entrante
    evento = "AlarmaCritica"
    
    # Ejecutar transición externa
    logger.extTransition({logger.in_evento: evento})
    
    # Verificar estado
    assert "historial" in logger.state
    assert len(logger.state["historial"]) == 1
    assert logger.state["historial"][-1] == evento

def test_siempre_pasivo():
    """
    Prueba que el modelo sea puramente pasivo (sigma infinito) y no emita salidas.
    """
    logger = Logger()
    
    # Verificar avance de tiempo inicial
    assert logger.timeAdvance() == float('inf')
    
    # Verificar que no genera salida
    assert logger.outputFnc() == {}
    
    # Verificar luego de recibir un evento
    logger.elapsed = 5.0
    logger.extTransition({logger.in_evento: "OtroEvento"})
    
    assert logger.timeAdvance() == float('inf')
    assert logger.outputFnc() == {}
