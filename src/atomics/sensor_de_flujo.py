from pypdevs.DEVS import AtomicDEVS
from parametros import ParametrosSistema

class SensorDeFlujo(AtomicDEVS):
    def __init__(self, nombre="SensorDeFlujo", parametros=None):
        """
        Inicializa el modelo atómico del Sensor de Flujo.
        :param nombre: Nombre del modelo.
        :param parametros: Instancia de configuración del sistema.
        """
        # Inicializamos la clase base
        AtomicDEVS.__init__(self, nombre)
        self.parametros = parametros if parametros else ParametrosSistema()
        
        # Definimos los puertos de Entrada (X) y Salida (Y)
        self.in_caudalActual = self.addInPort("caudalActual")
        self.out_sensorFlujo = self.addOutPort("sensorFlujo")
        
        # Definimos el Conjunto de Estados (S)
        # El sensor arranca en reposo (caudal 0) y su temporizador comienza a correr
        # con el período de muestreo definido.
        self.state = {
            "caudal": 0.0, 
            "sigma": self.parametros.PERIODO_MUESTREO_SENSOR
        }

    def timeAdvance(self):
        """
        Función de Avance de Tiempo (ta).
        """
        return self.state["sigma"]

    def extTransition(self, inputs):
        """
        Transición Externa (δext).
        Se ejecuta cuando un evento llega al puerto de entrada (el Actuador cambió el caudal).
        """
        # 1. Actualizamos el tiempo restante restando el tiempo que ya pasó (self.elapsed)
        self.state["sigma"] -= self.elapsed
        
        # 2. Verificamos si llegó un evento por nuestro puerto específico
        if self.in_caudalActual in inputs:
            # Los eventos llegan en una lista
            # Tomamos el primer evento de la lista (en este caso, solo esperamos uno por ciclo)
            nuevo_caudal = inputs[self.in_caudalActual]
            
            # Validación del dominio de datos utilizando CAUDAL_MAXIMO
            if 0 <= nuevo_caudal <= self.parametros.CAUDAL_MAXIMO:
                self.state["caudal"] = nuevo_caudal
            else:
                raise ValueError(f"Lectura anómala del sensor: {nuevo_caudal} ml/h no es un valor físico posible.")
                
        return self.state

    def outputFnc(self):
        """
        Función de Salida (λ).
        Se ejecuta cuando sigma llega a 0. Envía el último caudal medido al Controlador.
        """
        caudal_leido = self.state["caudal"]
        return {self.out_sensorFlujo: [caudal_leido]}

    def intTransition(self):
        """
        Transición Interna (δint).
        Se ejecuta inmediatamente después de enviar la lectura.
        """
        # Reiniciamos el temporizador usando el PERIODO_MUESTREO_SENSOR
        self.state["sigma"] = self.parametros.PERIODO_MUESTREO_SENSOR
        
        return self.state