from pypdevs.DEVS import AtomicDEVS

class Logger(AtomicDEVS):
    def __init__(self, nombre="Logger"):
        AtomicDEVS.__init__(self, nombre)
        
        # Puerto de Entrada (X) 
        self.in_evento = self.addInPort("in_evento")
        
        # Conjunto de Estados (S) 
        # Guardamos la lista de eventos y el avance de tiempo inicializado en infinito
        self.state = {
            "historial": [],
            "sigma": float('inf')
        }

    def timeAdvance(self):
        # Al ser un modelo puramente pasivo, el tiempo de avance siempre es infinito 
        return self.state["sigma"]

    def extTransition(self, inputs):
        """
        Transición Externa (δext).
        Se ejecuta cada vez que el controlador envía una notificación de evento.
        """
        # Hacemos una copia de la lista actual para no sufrir efectos colaterales con el simulador
        historial = list(self.state["historial"])
        
        if self.in_evento in inputs:
            # Capturamos el evento entrante y lo agregamos al final de la lista 
            evento = inputs[self.in_evento]
            historial.append(evento)
            
        # Actualizamos el estado manteniendo el sigma en infinito 
        self.state.update({
            "historial": historial,
            "sigma": float('inf')
        })
        return self.state

    def outputFnc(self):
        # Al no tener tiempo finito y no poseer puertos de salida, nunca genera eventos  
        return {}

    def intTransition(self):
        # No existen transiciones internas porque el modelo jamás despierta por su cuenta 
        return self.state