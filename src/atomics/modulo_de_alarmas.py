from pypdevs.DEVS import AtomicDEVS
from parametros import ParametrosSistema

class ModuloDeAlarmas(AtomicDEVS):
    def __init__(self, nombre="ModuloAlarmas", parametros=None):
        AtomicDEVS.__init__(self, nombre)
        self.parametros = parametros if parametros else ParametrosSistema()
        
        # Puertos de Entrada (X) [cite: 380-385]
        self.in_alarmaBaja = self.addInPort("in_alarmaBaja")
        self.in_alarmaMedia = self.addInPort("in_alarmaMedia")
        self.in_alarmaCritica = self.addInPort("in_alarmaCritica")
        self.in_confirmacionEnfermero = self.addInPort("in_confirmacionEnfermero")
        
        # Puerto de Salida (Y) [cite: 386-388]
        self.out_notificacionAlarma = self.addOutPort("out_notificacionAlarma")
        
        # Conjunto de Estados (S) [cite: 389-391]
        self.state = {
            "tipo": "ninguna",
            "fase": "pasivo",
            "sigma": float('inf')
        }

    def timeAdvance(self):
        # Retorna el tiempo restante programado 
        return self.state["sigma"]

    def extTransition(self, inputs):
        # Descontamos el tiempo transcurrido si el modelo no estaba pasivo
        if self.state["sigma"] != float('inf'):
            self.state["sigma"] -= self.elapsed

        tipo = self.state["tipo"]
        fase = self.state["fase"]
        sigma = self.state["sigma"]

        # Si entra cualquier alarma, la fase pasa a "emitir" inmediatamente con sigma 0 
        if self.in_alarmaBaja in inputs:
            tipo = "baja"
            fase = "emitir"
            sigma = 0.0
        elif self.in_alarmaMedia in inputs:
            tipo = "media"
            fase = "emitir"
            sigma = 0.0
        elif self.in_alarmaCritica in inputs:
            tipo = "critica"
            fase = "emitir"
            sigma = 0.0
            
        # Si entra la confirmación del enfermero, se silencia todo 
        elif self.in_confirmacionEnfermero in inputs:
            tipo = "ninguna"
            fase = "pasivo"
            sigma = float('inf')

        self.state.update({"tipo": tipo, "fase": fase, "sigma": sigma})
        return self.state

    def outputFnc(self):
        # Esta función solo se gatilla cuando sigma llega a 0.
        # Emite directamente el tipo de alarma que está en el estado .
        return {self.out_notificacionAlarma: self.state["tipo"]}

    def intTransition(self):
        # Reacciones en cadena luego de emitir la alarma 
        tipo = self.state["tipo"]
        fase = self.state["fase"]
        sigma = self.state["sigma"]

        # Si era alarma crítica, entra en el bucle de espera 
        if fase == "emitir" and tipo == "critica":
            fase = "esperar30"
            sigma = self.parametros.TIEMPO_ESPERA_ALARMA_CRITICA
            
        # Si NO era crítica, simplemente se apaga (ya cumplió con avisar) 
        elif fase == "emitir" and tipo != "critica":
            tipo = "ninguna"
            fase = "pasivo"
            sigma = float('inf')
            
        # Si pasaron los segundos de espera (o un ciclo previo), 
        # vuelve a cargar el tiempo de repeticion para seguir molestando 
        elif fase == "esperar30" or fase == "esperar10":
            fase = "esperar10"
            sigma = self.parametros.TIEMPO_REPETICION_ALARMA_CRITICA

        self.state.update({"tipo": tipo, "fase": fase, "sigma": sigma})
        return self.state