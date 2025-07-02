# CarPark Project v3.0 - Sistema Completo Mejorado

## 🎯 Descripción General

CarPark Project v3.0 es un sistema completo de detección y análisis de espacios de estacionamiento que combina:

- **🔧 Funcionalidades Legacy**: Implementación mejorada del algoritmo original
- **🚀 Sistema Modular**: Arquitectura moderna con componentes separados
- **🖥️ Interfaz Gráfica**: GUI intuitiva para todas las funcionalidades
- **⚡ Múltiples Algoritmos**: Diferentes métodos de detección y análisis

## 📁 Estructura del Proyecto

```
CarPark Project v3.0/
├── main.py                    # 🎯 Punto de entrada principal
├── launcher_legacy.py         # 🔧 Launcher para funcionalidades legacy
├── test_simple.py            # 🧪 Prueba básica del algoritmo original
├── requirements.txt          # 📦 Dependencias del proyecto
├── config.py                 # ⚙️ Configuraciones globales
├── CarParkPos               # 💾 Archivo de posiciones de espacios
├── carpark.log              # 📄 Archivo de logs
├── assets/                  # 📂 Recursos multimedia
│   ├── carParkImg.png       # 🖼️ Imagen para editor de espacios
│   └── carPark.mp4          # 🎬 Video para análisis
├── src/                     # 📂 Código fuente modular
│   ├── gui.py               # 🖥️ Interfaz gráfica principal
│   ├── legacy_detector.py   # 🔧 Funcionalidades legacy mejoradas
│   ├── detector.py          # 🔍 Detectores automáticos
│   ├── analyzer.py          # 📊 Analizadores de ocupación
│   ├── models.py            # 📋 Modelos de datos
│   ├── space_editor.py      # ✏️ Editor visual de espacios
│   ├── video_manager.py     # 🎬 Gestión de video
│   └── file_manager.py      # 📁 Gestión de archivos
└── docs/                    # 📚 Documentación
    └── REFACTOR_v3_README.md # 📖 Esta documentación
```

## 🚀 Instalación y Configuración

### 1. Instalar Dependencias

```bash
# Instalar dependencias principales
pip install -r requirements.txt

# O instalar manualmente:
pip install opencv-python numpy Pillow cvzone scipy scikit-image
```

### 2. Preparar Archivos de Recursos

Asegúrate de tener estos archivos en la carpeta `assets/`:
- `carParkImg.png`: Imagen del estacionamiento para el editor
- `carPark.mp4`: Video del estacionamiento para análisis

## 🎮 Formas de Uso

### 1. 🖥️ Interfaz Gráfica Completa (Recomendado)

```bash
python main.py
```

**Funcionalidades disponibles:**
- ✨ Detección automática de espacios
- ✏️ Editor visual moderno
- 📊 Análisis en tiempo real
- 🔧 Herramientas legacy integradas
- 📈 Estadísticas y exportación

### 2. 🔧 Herramientas Legacy Independientes

```bash
# Modo interactivo
python launcher_legacy.py

# Línea de comandos
python launcher_legacy.py editor --image assets/carParkImg.png
python launcher_legacy.py video --video assets/carPark.mp4
python launcher_legacy.py check
```

### 3. 🧪 Prueba Básica del Algoritmo Original

```bash
python test_simple.py
```

Esta opción replica exactamente el comportamiento del código original.

## 🔧 Funcionalidades Legacy Mejoradas

### Editor de Espacios Clásico

**Características:**
- Interfaz idéntica al original
- Clic izquierdo: Agregar espacio
- Clic derecho: Eliminar espacio
- Guardado automático en `CarParkPos`
- Tamaño configurable de espacios (tecla 's')

**Mejoras añadidas:**
- ✅ Manejo de errores robusto
- 🔢 Numeración visual de espacios
- 💾 Callback para integración con GUI
- 📊 Información en pantalla

### Análisis de Video Legacy

**Características originales:**
- Preprocesamiento con filtros morfológicos
- Umbralización adaptativa
- Conteo de píxeles para determinar ocupación
- Visualización en tiempo real

**Mejoras añadidas:**
- ⏸️ Control de pausa/reproducción (ESPACIO)
- 🔄 Reinicio de video (tecla 'r')
- 🎨 Mejor visualización con cvzone (opcional)
- 🔧 Fallback sin cvzone
- 📊 Estadísticas mejoradas

## 📊 Algoritmos Disponibles

### 1. Legacy Algorithm (Original)
```python
# Preprocesamiento
img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
img_blur = cv2.GaussianBlur(img_gray, (3, 3), 1)
img_threshold = cv2.adaptiveThreshold(img_blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                     cv2.THRESH_BINARY_INV, 25, 16)
img_median = cv2.medianBlur(img_threshold, 5)
kernel = np.ones((3, 3), np.uint8)
img_dilate = cv2.dilate(img_median, kernel, iterations=1)

# Detección
count = cv2.countNonZero(img_crop)
is_occupied = count >= 900  # Umbral fijo
```

### 2. Smart Detection (Nuevo)
- Detección automática por contornos
- Detección por líneas de Hough
- Template matching
- Filtros de área y aspect ratio

### 3. Adaptive Analysis (Nuevo)
- Umbral adaptativo
- Análisis de background
- Historial de ocupación
- Confianza estadística

## 🎛️ Configuraciones

### Archivo `config.py`
```python
# Rutas predeterminadas
ASSETS_DIR = "assets"
DEFAULT_IMAGE = "assets/carParkImg.png"
DEFAULT_VIDEO = "assets/carPark.mp4"

# Parámetros del algoritmo legacy
LEGACY_WIDTH = 107
LEGACY_HEIGHT = 48
LEGACY_THRESHOLD = 900

# Configuraciones de la GUI
GUI_WIDTH = 1400
GUI_HEIGHT = 900
```

### Parámetros del Editor Legacy
- **Ancho del espacio**: 107 píxeles (configurable)
- **Alto del espacio**: 48 píxeles (configurable)
- **Archivo de posiciones**: `CarParkPos`

### Parámetros del Análisis Legacy
- **Umbral de ocupación**: 900 píxeles
- **Kernel morfológico**: 3x3
- **Parámetros de umbralización**: (25, 16)

## 🖥️ Uso de la GUI

### Panel Principal
1. **Carga de Medios**:
   - 📁 "Cargar Video": Selecciona archivo MP4/AVI
   - 📹 "Cargar Cámara": Conecta cámara web
   - 🖼️ "Cargar Imagen": Para editor legacy

2. **Detección de Espacios**:
   - 🤖 "Detectar Automático": Algoritmos inteligentes
   - ✏️ "Editor Manual": Editor moderno
   - 💾 "Cargar/Guardar Espacios": Gestión de archivos

3. **Herramientas Legacy**:
   - 🔧 "Editor Clásico": Editor original mejorado
   - 🎬 "Video + Detección": Análisis legacy
   - 🖼️ "Cargar Imagen": Para vista previa

### Panel de Control
- ⚙️ **Configuración**: Método de análisis
- 📊 **Estadísticas**: Resultados en tiempo real
- 📈 **Exportación**: CSV de estadísticas y ocupación

## 🔧 Resolución de Problemas

### Errores Comunes

1. **"cv2 no encontrado"**
   ```bash
   pip install opencv-python
   ```

2. **"cvzone no encontrado"**
   ```bash
   pip install cvzone
   ```
   *Nota: cvzone es opcional, el sistema funciona sin él*

3. **"Archivo CarParkPos no encontrado"**
   - Usa primero el editor de espacios
   - El archivo se crea automáticamente

4. **"No se puede cargar video/imagen"**
   - Verifica que los archivos estén en `assets/`
   - Formatos soportados: MP4, AVI, PNG, JPG

### Verificación del Sistema

```bash
# Verificar archivos necesarios
python launcher_legacy.py check

# O en modo interactivo
python test_simple.py
# Seleccionar opción 3
```

## 📈 Nuevas Funcionalidades v3.0

### ✨ Integración Legacy-Modular
- Ambos sistemas funcionan en paralelo
- Intercambio de datos entre algoritmos
- Comparación de resultados

### 🎨 Visualización Mejorada
- Interfaz moderna con tkinter
- Soporte para cvzone (opcional)
- Fallback sin dependencias opcionales
- Numeración de espacios

### 🔧 Editor Dual
- Editor clásico (OpenCV directo)
- Editor moderno (GUI integrada)
- Compatibilidad de archivos

### 📊 Análisis Avanzado
- Múltiples algoritmos
- Estadísticas en tiempo real
- Exportación de datos
- Historial de ocupación

### 🎬 Control de Video Mejorado
- Pausa/reproducción
- Reinicio automático
- Reproducción en bucle
- Control por teclado

## 🎯 Casos de Uso

### 1. Desarrollo y Pruebas
```bash
# Prueba rápida del algoritmo original
python test_simple.py
```

### 2. Uso Productivo
```bash
# Sistema completo con GUI
python main.py
```

### 3. Configuración de Espacios
```bash
# Editor independiente
python launcher_legacy.py editor
```

### 4. Análisis de Video
```bash
# Análisis independiente
python launcher_legacy.py video
```

## 🔮 Roadmap Futuro

- [ ] 🤖 Integración con Machine Learning
- [ ] 🌐 API REST para integración externa
- [ ] 📱 Aplicación móvil
- [ ] ☁️ Procesamiento en la nube
- [ ] 📊 Dashboard web
- [ ] 🔔 Notificaciones en tiempo real

## 📞 Soporte

Para problemas o sugerencias:
1. Revisa esta documentación
2. Ejecuta las verificaciones del sistema
3. Consulta los logs en `carpark.log`
4. Prueba con el modo simple (`test_simple.py`)

---

**CarPark Project v3.0** - Sistema profesional de detección de espacios de estacionamiento  
*Desarrollado con ❤️ combinando lo mejor del algoritmo original con arquitectura moderna*
