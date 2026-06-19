from pypdevs.DEVS import AtomicDEVS

class SensorDeFlujo(AtomicDEVS):
    def __init__(self, nombre="SensorDeFlujo"):
        """
        Inicializa el modelo atómico del Sensor de Flujo.
        :param nombre: Nombre del modelo.
        """
        # Inicializamos la clase base
        AtomicDEVS.__init__(self, nombre)
        
        # Definimos los puertos de Entrada (X) y Salida (Y)
        self.in_caudalActual = self.addInPort("caudalActual")
        self.out_sensorFlujo = self.addOutPort("sensorFlujo")
        
        # Definimos el Conjunto de Estados (S)
        # Inicialmente el caudal leído es 0 y falta 1 segundo para el primer reporte
        self.state = {"caudal": 0.0, "sigma": 1.0}

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
            
            # Validación del dominio de datos
            if 0 <= nuevo_caudal <= 200:
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
        # Reiniciamos el temporizador para emitir la siguiente lectura en exactamente 1 segundo
        self.state["sigma"] = 1.0
        
        return self.state