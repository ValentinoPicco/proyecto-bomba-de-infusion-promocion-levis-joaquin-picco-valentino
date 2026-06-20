import re
import matplotlib.pyplot as plt

def graficar_desde_traza(archivo_txt):
    tiempo_actual = 0.0
    modelo_actual = ""

    # Listas inicializadas en el tiempo 0
    t_obj, y_obj = [0.0], [0.0]
    t_fase, y_fase = [0.0], ["suspendido"]
    t_real, y_real = [0.0], [0.0]

    print(f"Leyendo trazas desde: {archivo_txt}...")

    try:
        with open(archivo_txt, "r", encoding="utf-8") as f:
            for linea in f:
                # 1. Capturar el reloj de la simulación (Busca "TIEMPO ACTUAL:")
                if "TIEMPO ACTUAL:" in linea:
                    partes = linea.split("TIEMPO ACTUAL:")
                    tiempo_str = partes[1].strip().split()[0]
                    if tiempo_str != "inf":
                        tiempo_actual = float(tiempo_str)

                # 2. Identificar qué modelo está actuando (Busca el nombre entre < >)
                elif "en el modelo <" in linea:
                    modelo_actual = linea.split("<")[1].split(">")[0]

                # 3. Leer el estado (Busca "Estado Inicial" o "Nuevo Estado")
                elif "Estado Inicial:" in linea or "Nuevo Estado:" in linea:
                    
                    # --- Si es el Controlador, pescamos la fase y el caudal objetivo ---
                    if "Controlador" in modelo_actual:
                        match_fase = re.search(r"'fase':\s*'([^']+)'", linea)
                        match_obj = re.search(r"'caudalObj':\s*([\d\.]+)", linea)
                        
                        if match_fase and match_obj:
                            t_obj.append(tiempo_actual)
                            y_obj.append(float(match_obj.group(1)))
                            
                            t_fase.append(tiempo_actual)
                            y_fase.append(match_fase.group(1))

                    # --- Si es el Sensor, pescamos el caudal real ---
                    elif "Sensor" in modelo_actual:
                        match_caudal = re.search(r"'caudal':\s*([\d\.]+)", linea)
                        
                        if match_caudal:
                            t_real.append(tiempo_actual)
                            y_real.append(float(match_caudal.group(1)))

    except FileNotFoundError:
        print(f"Error: No se encontró el archivo '{archivo_txt}'.")
        return

    # Comprobación de seguridad si el txt estaba vacío o no se leyó nada
    if len(t_obj) <= 1 and len(t_real) <= 1:
        print("No se encontraron datos útiles en el txt. Revisá el formato.")
        return

    # --- Creación de los gráficos ---
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=True)

    # Gráfico 1: Caudal Indicado vs Real
    ax1.step(t_obj, y_obj, where='post', label='Caudal Indicado (Orden)', color='blue', linewidth=2)
    ax1.step(t_real, y_real, where='post', label='Caudal Real (Sensor)', color='red', linestyle='--', linewidth=2)
    ax1.set_title("Caudal Indicado vs Caudal Real")
    ax1.set_ylabel("Caudal (ml/h)")
    ax1.legend()
    ax1.grid(True)

    # Gráfico 2: Fase del Controlador
    ax2.step(t_fase, y_fase, where='post', color='purple', linewidth=2)
    ax2.set_title("Estado de la Bomba a lo largo del tiempo")
    ax2.set_xlabel("Tiempo de Simulación (segundos)")
    ax2.set_ylabel("Fase del Controlador")
    ax2.grid(True)

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    # Poné acá el nombre exacto de tu archivo txt generado
    graficar_desde_traza("traza_escenario_1.txt")