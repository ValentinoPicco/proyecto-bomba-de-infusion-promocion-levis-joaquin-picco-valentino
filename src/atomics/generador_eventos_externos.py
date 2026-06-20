from pypdevs.DEVS import AtomicDEVS

class GeneradorEventosExternos(AtomicDEVS):
    def __init__(self, nombre="GeneradorExterno", cronograma=[]):
        """
        Generador genérico para inyectar eventos en tiempos específicos de la simulación.
        :param cronograma: Lista de tuplas (tipo_evento, sigma)
                           Ejemplo: [("fin_bolsa", 100.0), ("conf_enf", 30.0)]
        """
        AtomicDEVS.__init__(self, nombre)
        
        self.out_finBolsa = self.addOutPort("out_finBolsa")
        self.out_confEnf = self.addOutPort("out_confEnf")
        
        self.cronograma = cronograma
        self.indice = 0
        
        if len(self.cronograma) > 0:
            evento, sigma = self.cronograma[0]
            self.state = {"evento_proximo": evento, "sigma": sigma}
        else:
            self.state = {"evento_proximo": None, "sigma": float('inf')}

    def timeAdvance(self):
        return self.state["sigma"]

    def outputFnc(self):
        evento = self.state["evento_proximo"]
        if evento == "fin_bolsa":
            return {self.out_finBolsa: ["emitir"]}
        elif evento == "conf_enf":
            return {self.out_confEnf: ["emitir"]}
        return {}

    def intTransition(self):
        self.indice += 1
        if self.indice < len(self.cronograma):
            evento, sigma = self.cronograma[self.indice]
            self.state["evento_proximo"] = evento
            self.state["sigma"] = sigma
        else:
            self.state["evento_proximo"] = None
            self.state["sigma"] = float('inf')
        return self.state
