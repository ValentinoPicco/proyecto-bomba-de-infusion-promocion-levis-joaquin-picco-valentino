from pypdevs.DEVS import AtomicDEVS

class GeneradorDeOrdenesMedicas(AtomicDEVS):
    def __init__(self, nombre, escenario_ordenes):
        """
        Inicializa el modelo atómico.
        :param nombre: Nombre del modelo.
        :param escenario_ordenes: Lista de tuplas (caudal, tiempo_sigma) 
               Ej: [(50, 10), (80, 3600)] -> En 10s emite 50, luego espera 3600s y emite 80.
        """
        # Inicializamos la clase base
        AtomicDEVS.__init__(self, nombre)
        
        # Definimos el conjunto de salidas (Y) creando el puerto
        self.out_ordenMedica = self.addOutPort("ordenMedica")
        
        # Revisamos que el dominio de los caudales sea correcto (0 a 200 ml/h)
        for caudal, tiempo in escenario_ordenes:
            if not (0 <= caudal <= 200):
                raise ValueError(f"Error de dominio: El caudal {caudal} ml/h está fuera del rango permitido [2].")
        
        # Definimos el Conjunto de Estados (S)
        self.escenario = escenario_ordenes
        self.indice_actual = 0
        
        if len(self.escenario) > 0:
            caudal_inicial, sigma_inicial = self.escenario[self.indice_actual]
            self.state = {"caudal": caudal_inicial, "sigma": sigma_inicial}
        else:
            # Si arranca vacío, se queda pasivo para siempre
            self.state = {"caudal": 0, "sigma": float('inf')}

    def timeAdvance(self):
        """
        Función de Avance de Tiempo (ta).
        Retorna el valor del temporizador interno sigma.
        """
        return self.state["sigma"]

    def outputFnc(self):
        """
        Función de Salida (λ).
        Se ejecuta cuando sigma llega a 0. Emite el caudal por el puerto.
        Las salidas se devuelven en forma de lista.
        """
        caudal_a_emitir = self.state["caudal"]
        return {self.out_ordenMedica: [caudal_a_emitir]}

    def intTransition(self):
        """
        Transición Interna (δint).
        Se ejecuta inmediatamente después de outputFnc.
        Actualiza el estado al próximo caudal y su respectivo tiempo de espera.
        """
        self.indice_actual += 1
        
        if self.indice_actual < len(self.escenario):
            # Cargamos la próxima orden del escenario
            proximo_caudal, proximo_sigma = self.escenario[self.indice_actual]
            self.state["caudal"] = proximo_caudal
            self.state["sigma"] = proximo_sigma
        else:
            # Si no hay más órdenes en la lista, pasivamos el modelo (sigma = infinito)
            self.state["sigma"] = float('inf')
            
        return self.state