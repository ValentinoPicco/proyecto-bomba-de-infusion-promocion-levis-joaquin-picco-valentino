from pypdevs.simulator import Simulator
from couples.a2 import ModeloAcopladoA2

# Definimos un escenario de prueba (lista de tuplas: caudal, tiempo)
# Ej: Empieza con 50 ml/h a los 0s, cambia a 80 ml/h a los 100s, se detiene a los 200s.
escenario_1 = [(50, 0), (80, 100), (0, 100)]

# Instanciamos el modelo acoplado principal
modelo_bomba = ModeloAcopladoA2(nombre="BombaInfusion", escenario_ordenes=escenario_1)

# Configuramos el simulador
sim = Simulator(modelo_bomba)
# sim.setClassicDEVS() # Usamos la convención DEVS clásica
sim.setTerminationTime(250.0) # Tiempo máximo de simulación en segundos
sim.setVerbose("traza_escenario_1.txt") 

# Ejecutamos la simulación
print("Iniciando simulación...")
sim.simulate()
print("Simulación terminada.")

# Extraemos los datos del Logger para analizarlos
historial = modelo_bomba.logger.state["historial"]
print(f"Eventos registrados: {len(historial)}")

print("\n--- Historial de Eventos ---")
if len(historial) == 0:
    print("El historial está vacío. Revisá la conexión out_notificarEvento -> in_evento.")
else:
    for i, evento in enumerate(historial, start=1):
        print(f"Evento {i}: {evento}")