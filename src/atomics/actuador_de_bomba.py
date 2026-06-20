from pypdevs.DEVS import AtomicDEVS
from parametros import ParametrosSistema

class ActuadorDeLaBomba(AtomicDEVS):
    def __init__(self, nombre="ActuadorBomba", parametros=None):
        """
        Inicializa el modelo atómico del Actuador de la Bomba.
        """
        AtomicDEVS.__init__(self, nombre)
        self.parametros = parametros if parametros else ParametrosSistema()
        
        # Definimos los Puertos de Entrada (X)
        self.in_ajustarCaudal = self.addInPort("in_ajustarCaudal")
        self.in_detenerBomba = self.addInPort("in_detenerBomba")
        
        # Definimos el Puerto de Salida (Y)
        self.out_caudalActual = self.addOutPort("out_caudalActual")
        
        # Conjunto de Estados (S): (fase, caudalActual, caudalObjetivo, sigma)
        self.state = {
            "fase": "estable",
            "caudalActual": 0.0,
            "caudalObjetivo": 0.0,
            "sigma": float('inf')
        }

    def timeAdvance(self):
        """
        Función de Avance de Tiempo (ta).
        Retorna el tiempo restante en la fase actual.
        """
        return self.state["sigma"]

    def extTransition(self, inputs):
        """
        Transición Externa (δext).
        Reacciona ante comandos del Controlador para ajustar flujo o detener la bomba.
        """
        # Descontamos el tiempo transcurrido si el temporizador estaba activo
        if self.state["sigma"] != float('inf'):
            self.state["sigma"] -= self.elapsed

        fase = self.state["fase"]
        caudalActual = self.state["caudalActual"]
        caudalObjetivo = self.state["caudalObjetivo"]
        sigma = self.state["sigma"]

        # Caso 1: Llega una orden de ajustar caudal desde fase estable
        if self.in_ajustarCaudal in inputs:
            fase = "transicion"
            val = inputs[self.in_ajustarCaudal]
            caudalObjetivo = val[0] if isinstance(val, list) else val
            sigma = self.parametros.LATENCIA_ACTUADOR
        elif self.in_detenerBomba in inputs:
            fase = "transicion"
            caudalObjetivo = 0.0
            sigma = self.parametros.LATENCIA_ACTUADOR

        self.state.update({
            "fase": fase,
            "caudalActual": caudalActual,
            "caudalObjetivo": caudalObjetivo,
            "sigma": sigma
        })
        return self.state

    def outputFnc(self):
        """
        Transición de Salida (λ).
        Se ejecuta justo antes de la Transición Interna.
        """
        fase = self.state["fase"]
        if fase == "transicion":
            # Emitimos el caudal objetivo afectado por el posible ruido de fallo físico
            caudal_real = self.state["caudalObjetivo"] * (1.0 + self.parametros.RUIDO_ACTUADOR)
            return {self.out_caudalActual: [caudal_real]}
        return {}

    def intTransition(self):
        """
        Transición Interna (δint).
        Se ejecuta inmediatamente después de outputFnc para consolidar el estado estable.
        """
        fase = self.state["fase"]
        caudalObjetivo = self.state["caudalObjetivo"]

        if fase == "transicion":
            fase = "estable"
            caudalActual = caudalObjetivo
            sigma = float('inf')
        else:
            caudalActual = self.state["caudalActual"]
            sigma = float('inf')

        self.state.update({
            "fase": fase,
            "caudalActual": caudalActual,
            "sigma": sigma
        })
        return self.state