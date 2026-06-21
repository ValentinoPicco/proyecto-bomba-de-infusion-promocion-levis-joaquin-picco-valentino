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
    
    # Importar y ejecutar el graficador/métricas automáticamente
    from graficar import calcular_metricas_y_graficar
    calcular_metricas_y_graficar("logs_simulacion.txt", "registro_eventos.txt")
    
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

def menu_escenarios_existentes(parametros):
    while True:
        limpiar_pantalla()
        print("--- ESCENARIOS PREDEFINIDOS ---")
        print("1. Funcionamiento normal, sin fallas.")
        print("2. Cambio de orden médica durante la infusión.")
        print("3. Orden médica con caudal igual a cero (detención).")
        print("4. Desvío leve de caudal que es corregido (-5% ruido).")
        print("5. Desvío de caudal mayor al 10% (-15% ruido sostenido).")
        print("6. Fin de bolsa con confirmación del enfermero.")
        print("7. Alarma crítica no confirmada durante 30s (-15% ruido).")
        print("8. Volver al menú principal")
        
        op = input("\nSeleccione el escenario a ejecutar (1-8): ")
        
        # Reseteamos parámetros por defecto para escenarios limpios
        parametros.RUIDO_ACTUADOR = 0.0
        cronograma = []
        escenario = []
        tiempo_max = 250.0
        
        if op == "1":
            # 6 eventos: Múltiples cambios de caudal exitosos
            escenario = [(0, 10), (50, 15), (70, 15), (30, 15), (100, 15), (50, 20)]
            tiempo_max = 90.0
            print("\n[Resumen] Escenario 1: Cambios constantes (5 eventos de caudal). Funcionamiento perfecto sin alarmas.")
        elif op == "2":
            # 5 eventos: Subidas y bajadas
            escenario = [(0, 10), (50, 15), (80, 20), (40, 15), (120, 20)]
            tiempo_max = 80.0
            print("\n[Resumen] Escenario 2: Inicia en 50, sube a 80, baja a 40, sube a 120. Comprobación de agilidad del actuador.")
        elif op == "3":
            # 6 eventos: Encendidos y apagados iterativos
            escenario = [(0, 10), (50, 15), (0, 10), (80, 15), (0, 10), (60, 15)]
            tiempo_max = 75.0
            print("\n[Resumen] Escenario 3: La orden cae a 0 múltiples veces, suspendiendo y reanudando la bomba repetidamente.")
        elif op == "4":
            # 5 eventos: Cambios con ruido leve
            escenario = [(0, 10), (100, 15), (50, 15), (120, 15), (80, 15)]
            parametros.RUIDO_ACTUADOR = -0.05
            tiempo_max = 70.0
            print("\n[Resumen] Escenario 4: 5 cambios de caudal con un error físico del 5%. Al ser menor al 10%, el sistema lo tolera en silencio.")
        elif op == "5":
            # 4 eventos combinados: 2 órdenes y 2 confirmaciones
            escenario = [(0, 10), (100, 35), (60, 35)]
            cronograma = [("conf_enf", 30), ("conf_enf", 40)]
            parametros.RUIDO_ACTUADOR = -0.15
            tiempo_max = 150.0
            print("\n[Resumen] Escenario 5: Error del 15%. La bomba se bloquea, el enfermero confirma, cambiamos la orden, se vuelve a bloquear y confirma de nuevo.")
        elif op == "6":
            # 5 eventos: Órdenes + Fin de bolsa + Auto detención + Confirmación
            escenario = [(0, 10), (50, 20), (80, 90), (60, 20)]
            cronograma = [("fin_bolsa", 40), ("conf_enf", 130)]
            tiempo_max = 140.0
            print("\n[Resumen] Escenario 6: Fin de bolsa a los 40s. A los 100s la bomba se bloquea por seguridad. A los 130s confirma enfermero y reanuda a 60ml/h.")
        elif op == "7":
            # 5 eventos: Cambios frenéticos antes del error crítico
            escenario = [(0, 10), (50, 5), (80, 5), (100, 5), (60, 70)]
            parametros.RUIDO_ACTUADOR = -0.15
            tiempo_max = 95.0
            print("\n[Resumen] Escenario 7: Error del 15%. Cambios rápidos iniciales, luego falla sostenida. Alarma crítica entra en bucle infinito de 30s + 10s repetitivos.")
        elif op == "8":
            break
        else:
            continue
            
        input("Presione ENTER para arrancar el simulador...")
        ejecutar_simulacion(parametros, escenario, cronograma, tiempo_max)

def menu_personalizado(parametros, escenario_ordenes, cronograma_eventos, tiempo_max):
    while True:
        limpiar_pantalla()
        print("==================================================")
        print("           ESCENARIO PERSONALIZADO")
        print("==================================================")
        print("\nESTADO DE LA CONFIGURACIÓN:")
        print(f"  - Órdenes médicas en escenario: {len(escenario_ordenes)}")
        print(f"  - Eventos externos programados: {len(cronograma_eventos)}")
        print(f"  - Ruido físico del actuador:    {parametros.RUIDO_ACTUADOR*100:.1f}%")
        print(f"  - Tiempo máximo de simulación:  {tiempo_max}s")
        
        print("\nOPCIONES:")
        print("  1. ► Correr Simulación")
        print("  2. ⚙ Configurar Parámetros del Sistema (y Ruido)")
        print("  3. 💉 Configurar Escenario de Órdenes Médicas")
        print("  4. ⏰ Configurar Cronograma de Eventos Externos")
        print("  5. ⏳ Cambiar Tiempo Máximo de Simulación")
        print("  6. ◄ Volver al Menú Principal")
        
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
            break

def main():
    parametros = ParametrosSistema()
    escenario_ordenes = [(50, 0), (80, 100), (0, 100)]
    cronograma_eventos = []
    tiempo_max = 250.0
    
    while True:
        # limpiar_pantalla()
        print("==================================================")
        print("        SIMULADOR DE BOMBA DE INFUSIÓN")
        print("==================================================")
        print("\nMENÚ:")
        print("  1. Ejecutar escenario existente")
        print("  2. Ejecutar escenario personalizado")
        print("  3. Salir")
        
        op = input("\nSeleccione una opción (1-3): ")
        
        if op == "1":
            menu_escenarios_existentes(parametros)
            calcular_metricas_y_graficar("logs_simulacion.txt", "registro_eventos.txt")
        elif op == "2":
            menu_personalizado(parametros, escenario_ordenes, cronograma_eventos, tiempo_max)
            calcular_metricas_y_graficar("logs_simulacion.txt", "registro_eventos.txt")
        elif op == "3":
            limpiar_pantalla()
            print("Saliendo del simulador...")
            sys.exit(0)

if __name__ == "__main__":
    main()