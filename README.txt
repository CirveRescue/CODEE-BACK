
# Proyecto de Detección de Placas y Reconocimiento de Caracteres (OCR) con YOLOv8

Este proyecto utiliza dos modelos YOLOv8: uno para la detección de placas de vehículos y otro para el reconocimiento de caracteres (OCR). Se pueden usar imágenes estáticas o un stream de video desde una cámara IP.

## Requisitos

### Bibliotecas de Python necesarias

- `opencv-python`
- `ultralytics`
- `matplotlib`
- `torch`

Para instalar las dependencias, puedes ejecutar el siguiente comando:

```bash
pip install -r requirements.txt
```

### Modelos YOLOv8 entrenados

Asegúrate de tener los modelos YOLOv8 entrenados:

- `best.pt`: Modelo YOLOv8 entrenado para la detección de placas.
- `best_OCR.pt`: Modelo YOLOv8 entrenado para el reconocimiento de caracteres (OCR).

Coloca estos modelos en la carpeta `Models/` o ajusta la ruta en el archivo `main.py` según sea necesario.

## Estructura del Proyecto

```
.
├── Models/                     # Carpeta donde se almacenan los modelos entrenados
│   ├── best.pt                 # Modelo YOLOv8 entrenado para detección de placas
│   ├── best_OCR.pt             # Modelo YOLOv8 entrenado para OCR
├── images/                     # Carpeta de imágenes de prueba
│   ├── 4.jpg                   # Imagen de prueba
├── main.py                     # Código principal del proyecto
├── requirements.txt            # Archivo con dependencias
├── README.md                   # Este archivo README
```

## Uso

### 1. Detección de Placas y OCR en Imágenes

Para detectar placas en una imagen de prueba y luego aplicar OCR para extraer el texto de la placa:

1. Abre el archivo `main.py`.
2. Asegúrate de que la variable `use_camera` esté configurada como `False`:
    ```python
    use_camera = False
    ```
3. Configura la ruta de la imagen de prueba:
    ```python
    image_path = "images/4.jpg"
    ```
4. Ejecuta el script:

    ```bash
    python main.py
    ```

El programa procesará la imagen, detectará la placa y los caracteres, y mostrará los resultados en pantalla.

### 2. Detección de Placas y OCR en Tiempo Real con Cámara IP

Para utilizar una cámara IP y procesar video en tiempo real:

1. Cambia la variable `use_camera` a `True` en el archivo `main.py`:
    ```python
    use_camera = True
    ```
2. Configura la URL de la cámara IP:
    ```python
    camera_ip_url = "rtsp://usuario:contraseña@IP_CAMARA:554/cam/realmonitor?channel=1&subtype=0"
    ```
3. Ejecuta el script:

    ```bash
    python main.py
    ```

El programa capturará video desde la cámara IP, detectará las placas de los vehículos y aplicará OCR para extraer los caracteres.

### Notas Adicionales

- **Visualización**: Las imágenes de las placas detectadas y los resultados de OCR se mostrarán en ventanas. Si no deseas visualizar las imágenes, puedes comentar o eliminar las líneas que muestran las ventanas con `cv2.imshow()` o `plt.show()`.
- **OCR**: El OCR se realiza utilizando otro modelo YOLOv8 entrenado específicamente para detectar caracteres alfanuméricos de placas. Los caracteres se ordenan de izquierda a derecha en base a su posición para formar la secuencia correcta de la placa.
- **Múltiples cámaras**: Para conectar varias cámaras IP, puedes modificar el script para manejar múltiples fuentes de video simultáneamente, asegurando que no haya conflictos entre las conexiones.

## Licencia

Este proyecto está bajo la Licencia MIT.
