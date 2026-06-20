from pypdevs.DEVS import CoupledDEVS
from couples.a1 import ModeloAcopladoA1
from atomics.actuador_de_bomba import ActuadorDeLaBomba
from atomics.modulo_de_alarmas import ModuloDeAlarmas
from atomics.logger import Logger
from parametros import ParametrosSistema

class ModeloAcopladoA2(CoupledDEVS):
    def __init__(self, nombre="Modelo_A2", escenario_ordenes=[], parametros=None):
        """
        Inicializa el Modelo Acoplado A1.
        :param nombre: Nombre del modelo.
        :param escenario_ordenes: La lista de órdenes que se pasará al Generador.
        :param parametros: Instancia de ParametrosSistema.
        """
        # Iniciamos la clase base
        CoupledDEVS.__init__(self, nombre)
        self.parametros = parametros if parametros else ParametrosSistema()
        
        # Puertos de Entrada Globales de A2(X)
        self.in_finBolsa = self.addInPort("in_finBolsa")
        self.in_confEnf = self.addInPort("in_confirmacionEnfermero")
        
        # Puerto de Salida Global de A2 (Y)
        self.out_notificacionAlarma = self.addOutPort("out_notificacionAlarma")
        
        # Instanciamos los Submodelos
        self.a1 = self.addSubModel(ModeloAcopladoA1("A1", escenario_ordenes, self.parametros))
        self.actuador = self.addSubModel(ActuadorDeLaBomba("Actuador", self.parametros))
        self.alarmas = self.addSubModel(ModuloDeAlarmas("Alarmas", self.parametros))
        self.logger = self.addSubModel(Logger("Logger"))
        
        # --- Acoplamientos de Entrada (EIC) ---
        self.connectPorts(self.in_finBolsa, self.a1.in_finBolsa)
        self.connectPorts(self.in_confEnf, self.a1.in_confEnf)
        self.connectPorts(self.in_confEnf, self.alarmas.in_confirmacionEnfermero)
        
        # --- Acoplamientos Internos (IC) ---
        # Controlador (desde A1) hacia Actuador
        self.connectPorts(self.a1.out_ajustarCaudal, self.actuador.in_ajustarCaudal)
        self.connectPorts(self.a1.out_detenerBomba, self.actuador.in_detenerBomba)
        
        # Feedback: Actuador hacia Sensor (en A1)
        self.connectPorts(self.actuador.out_caudalActual, self.a1.in_caudalActual)
        
        # Controlador (desde A1) hacia Alarmas
        self.connectPorts(self.a1.out_alarmaBaja, self.alarmas.in_alarmaBaja)
        self.connectPorts(self.a1.out_alarmaMedia, self.alarmas.in_alarmaMedia)
        self.connectPorts(self.a1.out_alarmaCritica, self.alarmas.in_alarmaCritica)
        
        # Controlador (desde A1) hacia Logger
        self.connectPorts(self.a1.out_notificarEvento, self.logger.in_evento)
        
        # --- Acoplamientos de Salida (EOC) ---
        self.connectPorts(self.alarmas.out_notificacionAlarma, self.out_notificacionAlarma)