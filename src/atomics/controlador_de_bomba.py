from pypdevs.DEVS import AtomicDEVS
from parametros import ParametrosSistema

class ControladorDeBomba(AtomicDEVS):
    def __init__(self, nombre="Controlador", parametros=None):
        AtomicDEVS.__init__(self, nombre)
        self.parametros = parametros if parametros else ParametrosSistema()
        
        # Definimos los Puertos de Entrada (X)
        self.in_ordenMedica = self.addInPort("in_ordenMedica")
        self.in_sensorFlujo = self.addInPort("in_sensorFlujo")
        self.in_finBolsa = self.addInPort("in_finBolsa")
        self.in_confEnf = self.addInPort("in_confEnf")
        
        # Definimos los Puertos de Salida (Y)
        self.out_ajustarCaudal = self.addOutPort("out_ajustarCaudal")
        self.out_detenerBomba = self.addOutPort("out_detenerBomba")
        self.out_alarmaBaja = self.addOutPort("out_alarmaBaja")
        self.out_alarmaMedia = self.addOutPort("out_alarmaMedia")
        self.out_alarmaCritica = self.addOutPort("out_alarmaCritica")
        self.out_notificarEvento = self.addOutPort("out_notificarEvento")
        
        # Estado inicial (S)
        self.state = {
            "fase": "suspendido",
            "caudalObj": 0.0,
            "tiempDesvio": 0,
            "salida": None, # Guardará una tupla: (puerto_destino, valor)
            "sigma": float('inf')
        }

    def timeAdvance(self):
        return self.state["sigma"]

    def outputFnc(self):
        # Devuelve el evento guardado en "salida" por el puerto correspondiente
        salida_actual = self.state["salida"]
        if salida_actual is not None:
            puerto, valor = salida_actual
            return {puerto: [valor]}
        return {}

    def extTransition(self, inputs):
        # Restamos el tiempo transcurrido (e) al temporizador si está corriendo
        if self.state["sigma"] != float('inf'):
            self.state["sigma"] -= self.elapsed

        # Extraemos variables para que el código sea limpio y se parezca a tu tupla matemática
        fase = self.state["fase"]
        caudalObj = self.state["caudalObj"]
        tiempDesvio = self.state["tiempDesvio"]
        salida = self.state["salida"]
        sigma = self.state["sigma"]

        # Evaluamos qué eventos llegaron
        if self.in_ordenMedica in inputs:
            x = inputs[self.in_ordenMedica]
            if x > 0 and fase != "reemplazando_bolsa":
                fase = "ajustando"
                caudalObj = x
                salida = (self.out_ajustarCaudal, x)
                sigma = self.parametros.TIEMPO_INICIO_INFUSION
            elif x == 0:
                fase = "suspendido"
                caudalObj = 0
                tiempDesvio = 0
                salida = (self.out_detenerBomba, "emitir")
                sigma = 0.0

        elif self.in_sensorFlujo in inputs:
            x = inputs[self.in_sensorFlujo]
            if caudalObj > 0:
                margen_error = self.parametros.MARGEN_ERROR_CAUDAL * caudalObj
                desvio = abs(x - caudalObj)
                
                if desvio <= margen_error:
                    tiempDesvio = 0
                else:
                    # Lógica de escalado temporal para las alarmas
                    if tiempDesvio < self.parametros.TIEMPO_DESVIO_MEDIA:
                        tiempDesvio += 1
                    elif tiempDesvio == self.parametros.TIEMPO_DESVIO_MEDIA:
                        tiempDesvio += 1
                        salida = (self.out_alarmaMedia, "emitir")
                        sigma = 0.0
                    elif self.parametros.TIEMPO_DESVIO_MEDIA < tiempDesvio < self.parametros.TIEMPO_DESVIO_CRITICA:
                        tiempDesvio += 1
                    elif tiempDesvio == self.parametros.TIEMPO_DESVIO_CRITICA:
                        fase = "bloqueando"
                        tiempDesvio += 1
                        salida = (self.out_alarmaCritica, "emitir")
                        sigma = 0.0

        elif self.in_finBolsa in inputs:
            if fase == "ajustando":
                fase = "fin_bolsa"
                salida = (self.out_alarmaBaja, "emitir")
                sigma = 0.0

        elif self.in_confEnf in inputs:
            if fase == "bloqueado":
                fase = "suspendido"
                caudalObj = 0
                tiempDesvio = 0
                salida = None
                sigma = float('inf')

        # Actualizamos el estado interno
        self.state.update({"fase": fase, "caudalObj": caudalObj, "tiempDesvio": tiempDesvio, "salida": salida, "sigma": sigma})
        return self.state

    def intTransition(self):
        fase = self.state["fase"]
        caudalObj = self.state["caudalObj"]
        tiempDesvio = self.state["tiempDesvio"]
        salida = self.state["salida"]
        sigma = self.state["sigma"]

        # Lógica de las distintas fases después de emitir una salida
        if fase == "suspendido" or fase == "ajustando" or fase == "bloqueado":
            salida = None
            sigma = float('inf')
            
        elif fase == "fin_bolsa":
            # Si acabamos de emitir la alarma baja, programamos la detención
            if salida and salida[0] == self.out_alarmaBaja:
                salida = (self.out_detenerBomba, "emitir")
                sigma = self.parametros.TIEMPO_MAX_FIN_BOLSA
            # Si ya pasaron los segundos maximos y mandamos detener, entramos en recambio
            elif salida and salida[0] == self.out_detenerBomba:
                fase = "reemplazando_bolsa"
                caudalObj = 0
                tiempDesvio = 0
                salida = None
                sigma = self.parametros.TIEMPO_REEMPLAZO_BOLSA
                
        elif fase == "reemplazando_bolsa":
            fase = "suspendido"
            sigma = float('inf')
            
        elif fase == "bloqueando":
            fase = "bloqueado"
            salida = (self.out_detenerBomba, "emitir")
            sigma = 0.0

        self.state.update({"fase": fase, "caudalObj": caudalObj, "tiempDesvio": tiempDesvio, "salida": salida, "sigma": sigma})
        return self.state