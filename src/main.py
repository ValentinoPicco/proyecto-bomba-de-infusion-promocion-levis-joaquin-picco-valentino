import sys
from pypdevs.simulator import Simulator
from couples.entorno import EntornoSimulacion
from parametros import ParametrosSistema

def limpiar_pantalla():
    print("\n" * 50)

def ejecutar_simulacion(parametros, escenario_ordenes, cronograma_eventos, tiempo_max):
    print("\n--- INICIANDO SIMULACIÓN DE LA BOMBA DE INFUSIÓN ---")
    # Instanciamos el entorno envolvente
    entorno = EntornoSimulacion("Entorno", escenario_ordenes, cronograma_eventos, parametros)
    
    # Configuramos el simulador
    sim = Simulator(entorno)
    sim.setTerminationTime(tiempo_max)
    # Activamos la traza técnica de PyPDEVS totalmente traducida al español
    sim.setCustomTracer("tracer_espanol", "TracerEspanol", ["logs_simulacion.txt"])
    
    print("Ejecutando PyPDEVS...\n")
    sim.simulate()
    
    print("Simulación terminada.\n")
    # Extraer historial
    historial = entorno.bomba.logger.state["historial"]
    
    print("--- HISTORIAL DE EVENTOS (LOGGER) ---")
    if not historial:
        print("No se registraron eventos en el logger.")
    else:
        with open("registro_eventos.txt", "w", encoding="utf-8") as f:
            f.write("=== REGISTRO DE EVENTOS DE LA SIMULACIÓN ===\n")
            for i, evento in enumerate(historial, 1):
                linea = f"{i}. {evento}"
                print(linea)
                f.write(linea + "\n")
            
    print("\n[INFO] La traza de PyPDEVS en español fue guardada en 'logs_simulacion.txt'.")
    print("[INFO] El historial limpio de eventos se guardó en 'registro_eventos.txt'.")
    input("\nPresione ENTER para continuar...")

def menu_parametros(parametros):
    while True:
        limpiar_pantalla()
        print("--- CONFIGURACIÓN DE PARÁMETROS ---")
        attrs = [a for a in dir(parametros) if not a.startswith("__")]
        
        for i, attr in enumerate(attrs, 1):
            valor = getattr(parametros, attr)
            print(f"{i}. {attr}: {valor}")
        
        print(f"{len(attrs) + 1}. Volver")
        
        op = input("\nSeleccione el parámetro a modificar: ")
        try:
            op_idx = int(op) - 1
            if op_idx == len(attrs):
                break
            if 0 <= op_idx < len(attrs):
                attr = attrs[op_idx]
                nuevo_val_str = input(f"Ingrese nuevo valor para {attr}: ")
                nuevo_val = float(nuevo_val_str)
                setattr(parametros, attr, nuevo_val)
                print("¡Parámetro actualizado!")
        except ValueError:
            print("Entrada inválida.")

def menu_escenario(escenario_ordenes):
    while True:
        limpiar_pantalla()
        print("--- ESCENARIO DE ÓRDENES MÉDICAS ---")
        if not escenario_ordenes:
            print("No hay órdenes configuradas.")
        else:
            for i, (caudal, tiempo) in enumerate(escenario_ordenes, 1):
                print(f"{i}. Caudal: {caudal} ml/h, Tiempo de espera posterior: {tiempo}s")
                
        print("\nOpciones:")
        print("1. Agregar nueva orden médica")
        print("2. Limpiar escenario")
        print("3. Cargar escenario Ejemplo (50 ml/h, 80 ml/h, 0 ml/h)")
        print("4. Volver")
        
        op = input("\nSeleccione opción: ")
        if op == "1":
            try:
                c = float(input("Caudal a inyectar (ml/h): "))
                t = float(input("Tiempo a esperar tras emitir esta orden (sigma): "))
                escenario_ordenes.append((c, t))
            except ValueError:
                print("Valor numérico inválido.")
        elif op == "2":
            escenario_ordenes.clear()
        elif op == "3":
            escenario_ordenes.clear()
            escenario_ordenes.extend([(50, 0), (80, 100), (0, 100)])
        elif op == "4":
            break

def menu_cronograma(cronograma_eventos):
    while True:
        limpiar_pantalla()
        print("--- CRONOGRAMA DE EVENTOS EXTERNOS ---")
        if not cronograma_eventos:
            print("No hay eventos externos configurados.")
        else:
            for i, (evento, tiempo) in enumerate(cronograma_eventos, 1):
                print(f"{i}. Evento: {evento}, Espera desde el anterior: {tiempo}s")
                
        print("\nOpciones:")
        print("1. Programar 'fin_bolsa'")
        print("2. Programar 'conf_enf' (Confirmación del Enfermero)")
        print("3. Limpiar cronograma")
        print("4. Cargar ejemplo: Fin de bolsa a los 50s, confirmación a los 80s")
        print("5. Volver")
        
        op = input("\nSeleccione opción: ")
        if op == "1":
            try:
                t = float(input("Tiempo a esperar desde el último evento (o desde el inicio si es el primero): "))
                cronograma_eventos.append(("fin_bolsa", t))
            except ValueError:
                pass
        elif op == "2":
            try:
                t = float(input("Tiempo a esperar desde el último evento (o desde el inicio si es el primero): "))
                cronograma_eventos.append(("conf_enf", t))
            except ValueError:
                pass
        elif op == "3":
            cronograma_eventos.clear()
        elif op == "4":
            cronograma_eventos.clear()
            cronograma_eventos.extend([("fin_bolsa", 50.0), ("conf_enf", 30.0)])
        elif op == "5":
            break

def main():
    parametros = ParametrosSistema()
    escenario_ordenes = [(50, 0), (80, 100), (0, 100)]
    cronograma_eventos = []
    tiempo_max = 250.0
    
    while True:
        limpiar_pantalla()
        print("==================================================")
        print("      SIMULADOR DE BOMBA DE INFUSIÓN (DEVS)")
        print("==================================================")
        print("\nESTADO DE LA CONFIGURACIÓN:")
        print(f"  - Órdenes médicas en escenario: {len(escenario_ordenes)}")
        print(f"  - Eventos externos programados: {len(cronograma_eventos)}")
        print(f"  - Tiempo máximo de simulación:  {tiempo_max}s")
        
        print("\nMENÚ PRINCIPAL:")
        print("  1. ► Correr Simulación")
        print("  2. ⚙ Configurar Parámetros del Sistema")
        print("  3. 💉 Configurar Escenario de Órdenes Médicas")
        print("  4. ⏰ Configurar Cronograma de Eventos Externos")
        print("  5. ⏳ Cambiar Tiempo Máximo de Simulación")
        print("  6. ✖ Salir")
        
        op = input("\nSeleccione una opción (1-6): ")
        
        if op == "1":
            ejecutar_simulacion(parametros, escenario_ordenes, cronograma_eventos, tiempo_max)
        elif op == "2":
            menu_parametros(parametros)
        elif op == "3":
            menu_escenario(escenario_ordenes)
        elif op == "4":
            menu_cronograma(cronograma_eventos)
        elif op == "5":
            try:
                tiempo_max = float(input("\nIngrese nuevo tiempo máximo de simulación (en segundos): "))
            except ValueError:
                print("Valor inválido.")
        elif op == "6":
            limpiar_pantalla()
            print("Saliendo del simulador...")
            sys.exit(0)

if __name__ == "__main__":
    main()