from pypdevs.DEVS import CoupledDEVS
from couples.a2 import ModeloAcopladoA2
from atomics.generador_eventos_externos import GeneradorEventosExternos
from parametros import ParametrosSistema

class EntornoSimulacion(CoupledDEVS):
    def __init__(self, nombre="Entorno", escenario_ordenes=[], cronograma_eventos=[], parametros=None):
        """
        Modelo Acoplado de nivel superior que actúa como el entorno del paciente/médico.
        Contiene la Bomba de Infusión (A2) y el generador de eventos externos (fin de bolsa, etc).
        """
        CoupledDEVS.__init__(self, nombre)
        self.parametros = parametros if parametros else ParametrosSistema()
        
        # Instanciar submódulos
        self.bomba = self.addSubModel(ModeloAcopladoA2("Bomba", escenario_ordenes, self.parametros))
        self.generador_ext = self.addSubModel(GeneradorEventosExternos("EventosEntorno", cronograma_eventos))
        
        # Acoplamientos Internos (IC)
        # Conectar el generador externo a las entradas de la bomba
        self.connectPorts(self.generador_ext.out_finBolsa, self.bomba.in_finBolsa)
        self.connectPorts(self.generador_ext.out_confEnf, self.bomba.in_confEnf)
