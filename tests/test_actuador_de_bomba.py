import sys
import os
import pytest
from math import inf

# Añadir el directorio src al PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from atomics.actuador_de_bomba import ActuadorDeLaBomba

def test_ajuste_caudal_latencia():
    """
    Prueba que al iniciar en estado 'estable' y recibir un comando para ajustar
    el caudal a 80, el estado cambie a 'transicion', el caudal objetivo sea 80,
    y el avance de tiempo (sigma) sea de 0.5.
    """
    model = ActuadorDeLaBomba("ActuadorTest")
    
    # Estado inicial: fase estable
    model.state = {
        "fase": "estable",
        "caudalActual": 0.0,
        "caudalObjetivo": 0.0,
        "sigma": inf
    }
    model.elapsed = 0.0
    
    # Entrada de ajuste de caudal
    inputs = {model.in_ajustarCaudal: 80.0}
    model.extTransition(inputs)
    
    # Verificaciones de estado post-transición
    assert model.state["fase"] == "transicion"
    assert model.state["caudalObjetivo"] == 80.0
    assert model.state["sigma"] == 0.5
    assert model.timeAdvance() == 0.5

def test_detencion_inmediata():
    """
    Prueba que al recibir un comando de detener la bomba, la fase pase a 'transicion',
    el caudal objetivo se fije en 0.0, y el avance de tiempo (sigma) sea de 0.5.
    """
    model = ActuadorDeLaBomba("ActuadorTest")
    
    # Estado inicial: bomba funcionando en fase estable
    model.state = {
        "fase": "estable",
        "caudalActual": 50.0,
        "caudalObjetivo": 50.0,
        "sigma": inf
    }
    model.elapsed = 0.0
    
    # Entrada para detener la bomba
    inputs = {model.in_detenerBomba: True} # El valor específico no se lee en el modelo
    model.extTransition(inputs)
    
    # Verificaciones de estado post-transición
    assert model.state["fase"] == "transicion"
    assert model.state["caudalObjetivo"] == 0.0
    assert model.state["sigma"] == 0.5
    assert model.timeAdvance() == 0.5

def test_emision_caudal_transicion():
    """
    Prueba que estando en fase de 'transicion' con un caudal objetivo de 80,
    la función de salida emita el valor 80 por el puerto out_caudalActual.
    """
    model = ActuadorDeLaBomba("ActuadorTest")
    
    # Estado de transición a punto de consolidarse (sigma = 0)
    model.state = {
        "fase": "transicion",
        "caudalActual": 0.0,
        "caudalObjetivo": 80.0,
        "sigma": 0.0
    }
    
    # Invocamos la función de salida
    salida = model.outputFnc()
    
    # Verificaciones de salida
    assert model.out_caudalActual in salida
    assert salida[model.out_caudalActual] == [80.0]

def test_consolidacion_estable():
    """
    Prueba que luego de una fase de 'transicion' con caudal objetivo de 80,
    la transición interna consolide el estado a 'estable', actualizando el 
    caudal actual a 80 y restableciendo el avance de tiempo a infinito.
    """
    model = ActuadorDeLaBomba("ActuadorTest")
    
    # Estado de transición que acaba de realizar outputFnc
    model.state = {
        "fase": "transicion",
        "caudalActual": 0.0,
        "caudalObjetivo": 80.0,
        "sigma": 0.0
    }
    
    # Invocamos la transición interna
    model.intTransition()
    
    # Verificaciones de estado consolidado
    assert model.state["fase"] == "estable"
    assert model.state["caudalActual"] == 80.0
    assert model.state["sigma"] == inf
    assert model.timeAdvance() == inf
