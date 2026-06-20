import ast
import matplotlib.pyplot as plt

def graficar_desde_traza(archivo_txt):
    tiempo_actual = 0.0
    modelo_actual = ""

    # Listas para guardar las coordenadas X (tiempo) e Y (valores)
    t_obj, y_obj = [0.0], [0.0]
    t_fase, y_fase = [0.0], ["suspendido"]
    t_real, y_real = [0.0], [0.0]

    print(f"Leyendo trazas desde: {archivo_txt}...")

    try:
        with open(archivo_txt, "r", encoding="utf-8") as f:
            for linea in f:
                # 1. Capturar el reloj de la simulación
                if "Current Time:" in linea:
                    # Ej: "__  Current Time: 10.00 ________________"
                    partes = linea.split("Current Time:")
                    tiempo_str = partes[1].split()[0]
                    if tiempo_str != "inf":
                        tiempo_actual = float(tiempo_str)

                # 2. Identificar qué modelo está actuando en este instante
                elif "in model" in linea:
                    modelo_actual = linea.strip()

                # 3. Leer el diccionario del estado nuevo
                elif "New State:" in linea:
                    # Extraemos todo lo que está a la derecha de "New State:"
                    estado_str = linea.split("New State:")[1].strip()
                    try:
                        # ast.literal_eval convierte el texto "{'fase': 'ajustando'...}" en un diccionario real de Python
                        estado = ast.literal_eval(estado_str)
                        
                        # Si el estado que leímos pertenece al Controlador
                        if "Controlador" in modelo_actual and "fase" in estado:
                            t_obj.append(tiempo_actual)
                            y_obj.append(estado["caudalObj"])
                            
                            t_fase.append(tiempo_actual)
                            y_fase.append(estado["fase"])

                        # Si el estado que leímos pertenece al Sensor de Flujo
                        elif "Sensor" in modelo_actual and "caudal" in estado:
                            t_real.append(tiempo_actual)
                            y_real.append(estado["caudal"])
                    except:
                        pass # Ignorar si no se puede interpretar la línea
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo '{archivo_txt}'. Asegurate de correr el main.py primero.")
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
    # Apuntamos al archivo de texto que genera tu main.py
    graficar_desde_traza("traza_escenario_1.txt")