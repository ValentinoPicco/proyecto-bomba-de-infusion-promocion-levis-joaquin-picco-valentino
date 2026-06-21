import re
import matplotlib.pyplot as plt

def calcular_metricas_y_graficar(archivo_log, archivo_eventos):
    tiempo_actual = 0.0
    modelo_actual = ""

    # Series temporales para graficos e integrales
    # Formato: [(tiempo, valor), ...]
    hist_obj = [(0.0, 0.0)]
    hist_real = [(0.0, 0.0)]
    hist_fase = [(0.0, "suspendido")]
    
    # Variables de estado para métricas
    t_inicio_desvio = None
    tiempos_respuesta_desvio = []
    
    t_inicio_fin_bolsa = None
    tiempos_respuesta_bolsa = []
    
    detenciones_preventivas = 0
    
    tiempo_final = 0.0

    print(f"Analizando trazas matemáticas desde '{archivo_log}'...")

    try:
        with open(archivo_log, "r", encoding="utf-8") as f:
            for linea in f:
                if "TIEMPO ACTUAL:" in linea:
                    tiempo_str = linea.split("TIEMPO ACTUAL:")[1].strip().split()[0]
                    if tiempo_str != "inf":
                        tiempo_actual = float(tiempo_str)
                        tiempo_final = max(tiempo_final, tiempo_actual)

                elif "en el modelo <" in linea:
                    modelo_actual = linea.split("<")[1].split(">")[0]

                elif "Estado Inicial:" in linea or "Nuevo Estado:" in linea:
                    if "Controlador" in modelo_actual:
                        # Extraer fase
                        match_fase = re.search(r"'fase':\s*'([^']+)'", linea)
                        if match_fase:
                            fase = match_fase.group(1)
                            if hist_fase[-1][1] != fase:
                                hist_fase.append((tiempo_actual, fase))
                                
                                # Detección de detenciones preventivas (por error crítico)
                                if fase == "bloqueado":
                                    detenciones_preventivas += 1
                                    
                                # Detección de tiempos de respuesta fin bolsa
                                if fase == "fin_bolsa":
                                    if t_inicio_fin_bolsa is None:
                                        t_inicio_fin_bolsa = tiempo_actual
                                elif fase == "reemplazando_bolsa" and t_inicio_fin_bolsa is not None:
                                    tiempos_respuesta_bolsa.append(tiempo_actual - t_inicio_fin_bolsa)
                                    t_inicio_fin_bolsa = None

                        # Extraer caudal objetivo
                        match_obj = re.search(r"'caudalObj':\s*([\d\.]+)", linea)
                        if match_obj:
                            obj = float(match_obj.group(1))
                            if hist_obj[-1][1] != obj:
                                hist_obj.append((tiempo_actual, obj))
                                
                        # Extraer tiempDesvio para medir la respuesta del controlador
                        match_desvio = re.search(r"'tiempDesvio':\s*([\d\.]+)", linea)
                        if match_desvio:
                            tdesvio = float(match_desvio.group(1))
                            # El desvío arranca cuando el timer empieza a contar (tdesvio = 1)
                            if tdesvio == 1 and t_inicio_desvio is None:
                                t_inicio_desvio = tiempo_actual
                            # Salta alarma media cuando llega a 6
                            elif tdesvio == 6 and t_inicio_desvio is not None:
                                tiempos_respuesta_desvio.append(tiempo_actual - t_inicio_desvio)
                                t_inicio_desvio = None
                            # Se resetea
                            elif tdesvio == 0:
                                t_inicio_desvio = None

                    elif "Sensor" in modelo_actual:
                        match_caudal = re.search(r"'caudal':\s*([\d\.]+)", linea)
                        if match_caudal:
                            real = float(match_caudal.group(1))
                            if hist_real[-1][1] != real:
                                hist_real.append((tiempo_actual, real))

    except FileNotFoundError:
        print(f"Error: No se encontró el archivo '{archivo_log}'. Corré una simulación primero.")
        return

    # Leer archivo de eventos limpios
    alarmas_generadas = []
    try:
        with open(archivo_eventos, "r", encoding="utf-8") as f:
            for linea in f:
                if "Alarma" in linea or "Detener" in linea:
                    # Limpiar el número del item (ej: "1. Alarma...")
                    msg = linea.split(".", 1)[-1].strip() if "." in linea[:4] else linea.strip()
                    if msg:
                        alarmas_generadas.append(msg)
    except FileNotFoundError:
        pass

    # ---------------------------------------------------------
    # CALCULAR PORCENTAJE DE INFUSIÓN CORRECTA (INTEGRAL TIEMPO)
    # ---------------------------------------------------------
    # Reconstruimos la señal segundo a segundo integrando áreas rectangulares
    tiempo_correcto = 0.0
    if tiempo_final > 0:
        # Obtenemos todos los puntos de tiempo donde hubo algún cambio
        eventos_tiempo = sorted(list(set([t for t, v in hist_obj] + [t for t, v in hist_real] + [tiempo_final])))
        
        for i in range(len(eventos_tiempo) - 1):
            t_start = eventos_tiempo[i]
            t_end = eventos_tiempo[i+1]
            dt = t_end - t_start
            
            # Encontrar el valor vigente en t_start recorriendo la lista hacia atrás
            v_obj = next((v for t, v in reversed(hist_obj) if t <= t_start), 0.0)
            v_real = next((v for t, v in reversed(hist_real) if t <= t_start), 0.0)
            
            if v_obj > 0:
                margen = 0.10 * v_obj
                # Si la diferencia entre lo que queremos y la realidad es menor al 10%
                if abs(v_obj - v_real) <= margen:
                    tiempo_correcto += dt
            else:
                # Si el objetivo es 0 y el real es 0, es correcto
                if v_real == 0.0:
                    tiempo_correcto += dt
                    
        porcentaje_correcto = (tiempo_correcto / tiempo_final) * 100
    else:
        porcentaje_correcto = 0.0


    # ---------------------------------------------------------
    # IMPRIMIR REPORTE DE MÉTRICAS
    # ---------------------------------------------------------
    print("\n" + "="*60)
    print("      RESULTADOS ESPERADOS")
    print("="*60)
    
    # 1 y 2. Gráficos (se abren al final)
    print("1-2. Gráficos de Caudal y Fases: Se abrirán en una ventana aparte.")
    
    # 3. Alarmas
    print("\n3. Registro de alarmas generadas:")
    if not alarmas_generadas:
        print("   - No se generaron alarmas en esta corrida.")
    else:
        for a in alarmas_generadas:
            print(f"   - {a}")
            
    # 4. Respuesta a desvíos
    print("\n4. Tiempo de respuesta ante desvíos de caudal (Alarma Media):")
    if tiempos_respuesta_desvio:
        print(f"   - Promedio: {sum(tiempos_respuesta_desvio)/len(tiempos_respuesta_desvio):.2f} segundos.")
    else:
        print("   - N/A (No hubo desvíos sostenidos detectados por alarma).")
        
    # 5. Respuesta a fin de bolsa
    print("\n5. Tiempo de respuesta ante fin de bolsa (Autocorte de seguridad):")
    if tiempos_respuesta_bolsa:
        print(f"   - Tiempo exacto: {tiempos_respuesta_bolsa[0]:.2f} segundos.")
    else:
        print("   - N/A (No hubo evento de fin de bolsa en esta simulación).")
        
    # 6. Detenciones preventivas
    print(f"\n6. Cantidad de detenciones preventivas (Por error crítico): {detenciones_preventivas}")
    
    # 7. Porcentaje de infusión
    print(f"\n7. Porcentaje de tiempo con infusión correcta: {porcentaje_correcto:.1f}%")
    
    print("="*60)
    print("Mostrando Gráficos... (Cerrá la ventana de Matplotlib para avanzar)")


    # ---------------------------------------------------------
    # DIBUJAR GRÁFICOS
    # ---------------------------------------------------------
    if len(hist_obj) <= 1 and len(hist_real) <= 1:
        return

    # Expandir listas hasta el tiempo final para que las líneas horizontales se dibujen hasta el final
    hist_obj.append((tiempo_final, hist_obj[-1][1]))
    hist_real.append((tiempo_final, hist_real[-1][1]))
    hist_fase.append((tiempo_final, hist_fase[-1][1]))

    # Separar en listas X e Y
    t_obj, y_obj = zip(*hist_obj)
    t_real, y_real = zip(*hist_real)
    t_fase, y_fase_str = zip(*hist_fase)
    
    # Mapeo de fases para el eje Y (para que el gráfico tenga un orden lógico ascendente según gravedad)
    fase_niveles = {
        "suspendido": 0,
        "fin_bolsa": 1,
        "reemplazando_bolsa": 2,
        "ajustando": 3,
        "bloqueando": 4,
        "bloqueado": 5
    }
    y_fase_num = [fase_niveles.get(f, 0) for f in y_fase_str]

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=True)

    # Gráfico 1: Caudal Indicado vs Real
    t_obj_inicio = t_obj[:-1]
    t_obj_fin = t_obj[1:]
    y_obj_vals = y_obj[:-1]

    t_real_inicio = t_real[:-1]
    t_real_fin = t_real[1:]
    y_real_vals = y_real[:-1]

    ax1.hlines(y=y_obj_vals, xmin=t_obj_inicio, xmax=t_obj_fin, label='Caudal Indicado (Orden)', colors='#2ca02c', linewidth=2.5)
    ax1.plot(t_obj_inicio, y_obj_vals, 'o', color='#2ca02c', markersize=5)

    ax1.hlines(y=y_real_vals, xmin=t_real_inicio, xmax=t_real_fin, label='Caudal Real (Sensor)', colors='#d62728', linestyles='--', linewidth=2.5)
    ax1.plot(t_real_inicio, y_real_vals, 'o', color='#d62728', markersize=5)

    ax1.set_title("Caudal Indicado vs Caudal Real", fontsize=14, fontweight='bold')
    ax1.set_ylabel("Caudal (ml/h)", fontsize=12)
    ax1.legend(loc='upper right')
    ax1.grid(True, alpha=0.4, linestyle='--')

    # Gráfico 2: Fase del Controlador
    # Usamos hlines en vez de step para que no dibuje las líneas verticales de conexión 
    # y no parezca que pasa por estados intermedios.
    t_inicio = t_fase[:-1]
    t_fin = t_fase[1:]
    y_vals = y_fase_num[:-1]
    
    ax2.hlines(y=y_vals, xmin=t_inicio, xmax=t_fin, color='#9467bd', linewidth=3.5)
    
    # Añadir puntitos para indicar exactamente cuándo empieza el estado
    ax2.plot(t_inicio, y_vals, 'o', color='#9467bd', markersize=5)

    ax2.set_title("Estado de la Bomba a lo largo del tiempo", fontsize=14, fontweight='bold')
    ax2.set_xlabel("Tiempo de Simulación (segundos)", fontsize=12)
    ax2.set_ylabel("Fase del Controlador", fontsize=12)
    ax2.set_yticks(list(fase_niveles.values()))
    ax2.set_yticklabels(list(fase_niveles.keys()), fontsize=10)
    ax2.grid(True, alpha=0.4, linestyle='--')

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    calcular_metricas_y_graficar("logs_simulacion.txt", "registro_eventos.txt")
