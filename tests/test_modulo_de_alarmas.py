import sys
import os
import math
import pytest

# Agregar src al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from atomics.modulo_de_alarmas import ModuloDeAlarmas


def test_emision_inmediata():
    """Prueba que al recibir una alarma crítica, la fase cambia a emitir con sigma 0."""
    modelo = ModuloDeAlarmas()
    
    # Simular paso del tiempo antes del evento externo
    modelo.elapsed = 10.0
    
    # Transición externa recibiendo alarma crítica
    modelo.extTransition({modelo.in_alarmaCritica: "alarma_critica_value"})
    
    # Verificaciones de estado
    assert modelo.state["tipo"] == "critica"
    assert modelo.state["fase"] == "emitir"
    assert modelo.state["sigma"] == 0.0


def test_ciclo_alarma_critica():
    """Prueba que tras emitir una alarma crítica, cambia a fase esperar30 con sigma 30."""
    modelo = ModuloDeAlarmas()
    
    # Forzar estado inicial
    modelo.state["tipo"] = "critica"
    modelo.state["fase"] = "emitir"
    modelo.state["sigma"] = 0.0
    
    # Transición interna
    modelo.intTransition()
    
    # Verificaciones de estado
    assert modelo.state["tipo"] == "critica"
    assert modelo.state["fase"] == "esperar30"
    assert modelo.state["sigma"] == 30.0


def test_repeticion_alarma_critica():
    """Prueba que luego de esperar 30s en alarma crítica, se repite la espera cada 10s."""
    modelo = ModuloDeAlarmas()
    
    # Forzar estado inicial
    modelo.state["tipo"] = "critica"
    modelo.state["fase"] = "esperar30"
    modelo.state["sigma"] = 0.0
    
    # Transición interna
    modelo.intTransition()
    
    # Verificaciones de estado
    assert modelo.state["tipo"] == "critica"
    assert modelo.state["fase"] == "esperar10"
    assert modelo.state["sigma"] == 10.0


def test_bucle_infinito_alarma():
    """Prueba que estando en fase esperar10, se mantiene en esperar10 con sigma 10."""
    modelo = ModuloDeAlarmas()
    
    # Forzar estado inicial
    modelo.state["tipo"] = "critica"
    modelo.state["fase"] = "esperar10"
    modelo.state["sigma"] = 0.0
    
    # Transición interna
    modelo.intTransition()
    
    # Verificaciones de estado
    assert modelo.state["tipo"] == "critica"
    assert modelo.state["fase"] == "esperar10"
    assert modelo.state["sigma"] == 10.0


def test_silencio_por_confirmacion():
    """Prueba que al recibir confirmación del enfermero, la alarma se silencia (vuelve a pasivo)."""
    modelo = ModuloDeAlarmas()
    
    # Forzar estado inicial (como si estuviera sonando o esperando)
    modelo.state["tipo"] = "critica"
    modelo.state["fase"] = "esperar10"
    modelo.state["sigma"] = 5.0
    
    # Simular tiempo transcurrido
    modelo.elapsed = 2.0
    
    # Transición externa recibiendo confirmación
    modelo.extTransition({modelo.in_confirmacionEnfermero: "confirmacion"})
    
    # Verificaciones de estado
    assert modelo.state["tipo"] == "ninguna"
    assert modelo.state["fase"] == "pasivo"
    assert math.isinf(modelo.state["sigma"])


def test_apagar_alarma_no_critica():
    """Prueba que las alarmas no críticas se apagan solas luego de emitir."""
    modelo = ModuloDeAlarmas()
    
    # Forzar estado inicial
    modelo.state["tipo"] = "media"
    modelo.state["fase"] = "emitir"
    modelo.state["sigma"] = 0.0
    
    # Transición interna
    modelo.intTransition()
    
    # Verificaciones de estado
    assert modelo.state["tipo"] == "ninguna"
    assert modelo.state["fase"] == "pasivo"
    assert math.isinf(modelo.state["sigma"])
