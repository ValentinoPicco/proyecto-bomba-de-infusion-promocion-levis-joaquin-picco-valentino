class ParametrosSistema:
    """
    Clase centralizada para los parámetros configurables de la Bomba de Infusión.
    Contiene los valores por defecto establecidos en la Sección 6 (Tabla 1) del PDF.
    """
    def __init__(self):
        self.CAUDAL_MAXIMO = 200.0                   # ml/h
        self.TIEMPO_INICIO_INFUSION = 3.0            # segundos
        self.PERIODO_MUESTREO_SENSOR = 1.0           # segundos
        self.LATENCIA_ACTUADOR = 0.5                 # segundos
        self.MARGEN_ERROR_CAUDAL = 0.10              # 10%
        self.TIEMPO_DESVIO_MEDIA = 5                 # ticks/segundos
        self.TIEMPO_DESVIO_CRITICA = 9               # ticks/segundos
        self.TIEMPO_MAX_FIN_BOLSA = 60.0             # segundos
        self.TIEMPO_REEMPLAZO_BOLSA = 120.0          # segundos
        self.TIEMPO_ESPERA_ALARMA_CRITICA = 30.0     # segundos
        self.TIEMPO_REPETICION_ALARMA_CRITICA = 10.0 # segundos
