from pypdevs.DEVS import CoupledDEVS
from atomics.generador_ordenes_medicas import GeneradorDeOrdenesMedicas
from atomics.sensor_de_flujo import SensorDeFlujo
from atomics.controlador_de_bomba import ControladorDeBomba
from parametros import ParametrosSistema

class ModeloAcopladoA1(CoupledDEVS):
    def __init__(self, nombre="Modelo_A1", escenario_ordenes=[], parametros=None):
        """
        Inicializa el Modelo Acoplado A1.
        :param nombre: Nombre del modelo.
        :param escenario_ordenes: La lista de órdenes que se pasará al Generador.
        :param parametros: Instancia de ParametrosSistema (opcional).
        """
        # Inicializamos la clase base
        CoupledDEVS.__init__(self, nombre)
        self.parametros = parametros if parametros else ParametrosSistema()
        
        # Definimos los Puertos de Entrada Globales de A1 (X)
        self.in_caudalActual = self.addInPort("in_caudalActual")
        self.in_finBolsa = self.addInPort("in_finBolsa")
        self.in_confEnf = self.addInPort("in_confirmacionEnfermero")
        
        # Definimos los Puertos de Salida Globales de A1 (Y)
        self.out_ajustarCaudal = self.addOutPort("out_ajustarCaudal")
        self.out_detenerBomba = self.addOutPort("out_detenerBomba")
        self.out_alarmaBaja = self.addOutPort("out_baja")
        self.out_alarmaMedia = self.addOutPort("out_media")
        self.out_alarmaCritica = self.addOutPort("out_critica")
        self.out_notificarEvento = self.addOutPort("out_notificarEvento")
        
        # Instanciamos los Submodelos (Componentes) y les pasamos los parametros
        self.generador = self.addSubModel(GeneradorDeOrdenesMedicas("Generador", escenario_ordenes, self.parametros))
        self.sensor = self.addSubModel(SensorDeFlujo("Sensor", self.parametros))
        self.controlador = self.addSubModel(ControladorDeBomba("Controlador", self.parametros))
        
        # Acoplamientos de Entrada Externa (EIC)
        # Ingresan al modulo A1 y viajan hacia el Sensor y el Controlador
        self.connectPorts(self.in_caudalActual, self.sensor.in_caudalActual)
        self.connectPorts(self.in_finBolsa, self.controlador.in_finBolsa)
        self.connectPorts(self.in_confEnf, self.controlador.in_confEnf)
        
        # Acoplamientos Internos (IC)
        # Comunicación interna directa entre los modulos
        self.connectPorts(self.generador.out_ordenMedica, self.controlador.in_ordenMedica)
        self.connectPorts(self.sensor.out_sensorFlujo, self.controlador.in_sensorFlujo)
        
        # Acoplamientos de Salida Externa (EOC)
        # Lo que el controlador decide, se dispara hacia afuera del A1
        self.connectPorts(self.controlador.out_ajustarCaudal, self.out_ajustarCaudal)
        self.connectPorts(self.controlador.out_detenerBomba, self.out_detenerBomba)
        self.connectPorts(self.controlador.out_alarmaBaja, self.out_alarmaBaja)
        self.connectPorts(self.controlador.out_alarmaMedia, self.out_alarmaMedia)
        self.connectPorts(self.controlador.out_alarmaCritica, self.out_alarmaCritica)
        self.connectPorts(self.controlador.out_notificarEvento, self.out_notificarEvento)