# Simulador de Bomba de Infusión DEVS

Este proyecto implementa el modelado y la simulación de eventos discretos para un controlador simplificado de una bomba de infusión intravenosa utilizando el formalismo DEVS y la biblioteca PyPDEVS.

---

## Instalación de Dependencias

### En Linux (Debian/Ubuntu)
1. Asegúrate de tener instalado Python 3 y `pip`:
   ```bash
   sudo apt update
   sudo apt install python3 python3-pip python3-tk
   ```
2. Instala las bibliotecas requeridas para los gráficos y las pruebas automatizadas:
   ```bash
   pip install matplotlib pytest
   ```

### En Windows
1. Descarga e instala la última versión de [Python para Windows](https://www.python.org/downloads/).
   > [!IMPORTANT]
   > Durante la instalación, asegúrate de marcar la casilla **"Add Python to PATH"** (Agregar Python al PATH).
2. Abre la Terminal (PowerShell o Símbolo del Sistema) e instala las dependencias ejecutando:
   ```powershell
   pip install matplotlib pytest
   ```

### Instalación de PythonPDevs
1. Se debe clonar el repositorio de la biblioteca.
   ```bash
   git clone https://github.com/capocchi/PythonPDEVS.git
   ```
   > [!IMPORTANT]
   > Es probable que si intenta instalar inmediatamente luego de clonar vea varios errores y no se instale nada.
1.2. Abra src/pypdevs/controller.py que se encuentra dentro del repositorio de la biblioteca que acaba de clonar.
1.3. cambie las lineas 551 y 552:
   ```python
   async = AsynchronousComboGenerator(generator_file, self.threading_backend)
   self.asynchronous_generator = async
   ```
   por lo siguiente:
   ```python
   async_gen = AsynchronousComboGenerator(generator_file, self.threading_backend)
   self.asynchronous_generator = async_gen
   ```
2. Siguiendo el readme del repositorio de la biblioteca, ejecute:
   ```bash
   cd src
   python3 setup.py install --user
   ```
---

## Cómo Usar el Sistema

### 1. Ejecutar el Simulador
Para iniciar la interfaz interactiva en consola, ejecuta el siguiente comando desde la raíz del proyecto:
   ```bash
   python3 src/main.py o python src/main.py
   ```

### 2. Opciones del Menú
El simulador ofrece un menú principal interactivo con las siguientes opciones:
*   **1. Ejecutar escenario existente:** Permite seleccionar y correr uno de los 7 escenarios de prueba predefinidos en la consigna (funcionamiento normal, cambios de caudal, desvíos leves, alarmas críticas, fin de bolsa, etc.).
*   **2. Ejecutar escenario personalizado:** Permite configurar manualmente tu propio cronograma de órdenes médicas, eventos de enfermería (confirmaciones, recambios de bolsa) e incluso inyectar un porcentaje de ruido físico en el actuador.
*   **3. Salir:** Cierra la aplicación.

### 3. Reporte de Métricas y Gráficos
Al finalizar cualquier simulación:
1.  Se imprimirán por consola los **Resultados Esperados** (registro de alarmas, tiempos promedio de respuesta ante desvíos, tiempo exacto de autocorte, conteo de detenciones preventivas y porcentaje de infusión correcta).
2.  Se generarán los archivos de reporte técnico `logs_simulacion.txt` y `registro_eventos.txt`.
3.  Se abrirá automáticamente una ventana interactiva de `matplotlib` con dos gráficos alineados temporalmente:
    *   **Gráfico de Caudal:** Caudal Indicado (Orden Médica) vs. Caudal Real (Lectura del Sensor).
    *   **Gráfico del Estado de la Bomba:** Evolución cronológica de las fases internas del controlador (suspendido, ajustando, bloqueado, etc.).
4.  Al cerrar la ventana gráfica, el sistema regresará al menú principal.

### 4. Ejecutar Pruebas Unitarias
Para correr la suite completa de pruebas automatizadas sobre la estructura y lógica de los modelos atómicos y acoplados, ejecuta:
```bash
pytest
```
