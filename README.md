# 🚗 CarPark Project - Sistema Modular de Análisis de Estacionamientos

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![OpenCV](https://img.shields.io/badge/OpenCV-4.8+-green.svg)](https://opencv.org)
[![Arquitectura](https://img.shields.io/badge/Arquitectura-Modular-brightgreen.svg)]()
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 📋 Descripción

**CarPark Project v3.0** es un sistema **modular e inteligente** para el análisis automático de espacios de estacionamiento usando visión por computadora. Esta versión ha sido completamente refactorizada con una **arquitectura modular profesional** que separa responsabilidades y mejora el mantenimiento del código.

### ✨ Características Principales

- 🧠 **Detección Automática Inteligente** con múltiples algoritmos
- 📊 **Análisis de Ocupación Avanzado** (fijo, adaptativo, sustracción de fondo)
- 🎨 **Interfaz Moderna y Responsive** con editor visual integrado
- 📹 **Soporte Multi-fuente** (videos, cámaras web, imágenes)
- 💾 **Múltiples Formatos** (JSON moderno, Pickle legacy)
- 🔧 **Editor Visual Profesional** con herramientas avanzadas
- 📈 **Estadísticas en Tiempo Real** y exportación automática
- 🏗️ **Arquitectura Modular** con separación clara de responsabilidades

---

## 🏗️ Arquitectura Modular

### 📦 Módulos Principales

```
src/
├── 📊 models.py          # Modelos de datos (ParkingSpace, OccupancyStatus, etc.)
├── 📹 video_manager.py   # Gestión de video y captura de frames
├── 🧠 detector.py        # Detección inteligente de espacios
├── 📈 analyzer.py        # Análisis de ocupación con múltiples métodos  
├── 💾 file_manager.py    # Gestión de archivos y persistencia
├── 🎨 space_editor.py    # Editor visual interactivo
└── 🖼️ gui.py            # Interfaz gráfica principal
```

### 🎯 Beneficios de la Modularización

- **✅ Mantenibilidad**: Cada módulo tiene una responsabilidad específica
- **✅ Escalabilidad**: Fácil agregar nuevas funcionalidades
- **✅ Testabilidad**: Cada módulo puede probarse independientemente
- **✅ Reutilización**: Módulos pueden usarse en otros proyectos
- **✅ Legibilidad**: Código organizado y fácil de entender

---

## 🚀 Inicio Rápido

### 1. **Verificar Python**
```bash
python --version  # Requiere Python 3.8+
```

### 2. **Instalar Dependencias**
```bash
pip install -r requirements.txt
```

### 3. **Ejecutar Aplicación**
```bash
python main.py
```

### 4. **¡Listo!** 
- La aplicación verificará dependencias automáticamente
- Se abrirá la interfaz moderna con todas las funcionalidades
- Ejemplos incluidos listos para usar

---

## 📁 Estructura del Proyecto (Arquitectura Modular)

```
CarParkProject/
├── 🚀 main.py                        # Punto de entrada principal
├── ⚙️ config.py                      # Configuración centralizada
├── 📋 requirements.txt               # Dependencias del proyecto
├── 📖 README.md                      # Esta documentación
├── 📂 src/                           # Código fuente modular
│   ├── 📊 models.py                 # Modelos de datos
│   ├── 📹 video_manager.py          # Gestión de video
│   ├── 🧠 detector.py               # Detección de espacios
│   ├── 📈 analyzer.py               # Análisis de ocupación
│   ├── 💾 file_manager.py           # Gestión de archivos
│   ├── 🎨 space_editor.py           # Editor visual
│   └── 🖼️ gui.py                   # Interfaz principal
├── 📂 assets/                        # Recursos multimedia
│   ├── 🎬 carPark.mp4               # Video de ejemplo
│   ├── 🖼️ carParkImg.png            # Imagen de ejemplo
│   └── 📍 CarParkPos                # Configuración guardada
├── 📂 docs/                          # Documentación técnica
│   └── 📚 REFACTOR_v2_README.md     # Info del refactor anterior
└── 📂 legacy/                        # Versiones anteriores
    ├── 📱 main.py                   # Versión original
    ├── 📱 main_app.py               # Versión intermedia
    └── 📱 main_app_monolithic.py    # Versión monolítica (1300+ líneas)
```

---

## 🛠️ Módulos y Funcionalidades

### 📊 **models.py** - Modelos de Datos
- `ParkingSpace`: Representa espacios de estacionamiento
- `OccupancyStatus`: Estado de ocupación
- `AnalysisStats`: Estadísticas de análisis
- Serialización/deserialización automática

### 📹 **video_manager.py** - Gestión de Video
- Soporte para archivos de video y cámaras
- Captura threaded no bloqueante
- Control de reproducción (pausar/reanudar/buscar)
- Callbacks para procesamiento en tiempo real

### 🧠 **detector.py** - Detección Inteligente
- Detección por contornos
- Detección por líneas de Hough
- Template matching
- Método combinado con fusión inteligente

### 📈 **analyzer.py** - Análisis de Ocupación
- Umbral fijo optimizado
- Umbral adaptativo por región
- Sustracción de fondo con MOG2
- Análisis con historial para estabilidad

### 💾 **file_manager.py** - Gestión de Archivos
- Guardado/carga en JSON moderno
- Compatibilidad con Pickle legacy
- Exportación a CSV para análisis
- Validación de formatos automática

### 🎨 **space_editor.py** - Editor Visual
- Múltiples modos (seleccionar, dibujar, mover, etc.)
- Detección automática integrada
- Canvas interactivo con zoom/scroll
- Vista previa en tiempo real

### 🖼️ **gui.py** - Interfaz Principal
- Diseño moderno y responsive
- Integración de todos los módulos
- Estadísticas en tiempo real
- Controles intuitivos

---

## 🎯 Comparación: Monolítico vs Modular

### ❌ Versión Anterior (Monolítica)
- **1327 líneas** en un solo archivo
- Responsabilidades mezcladas
- Difícil mantenimiento y testing
- Código duplicado
- Escalabilidad limitada

### ✅ Versión Actual (Modular)
- **7 módulos especializados** (~200-300 líneas c/u)
- Responsabilidades bien definidas
- Fácil mantenimiento y testing
- Código reutilizable
- Escalabilidad excelente

---

## 📋 Requisitos del Sistema

- **Python**: 3.8 o superior
- **OpenCV**: 4.x (instalado automáticamente)
- **NumPy**: Para cálculos numéricos
- **Pillow**: Para manejo de imágenes
- **Tkinter**: Incluido con Python (interfaz gráfica)

---

## ⚡ Uso Avanzado

### 🔧 Personalización
Edita `config.py` para personalizar:
- Colores de espacios
- Algoritmos de detección
- Formatos soportados
- Configuraciones de análisis

### 🧪 Testing Individual de Módulos
```bash
# Probar detector
python -c "from src.detector import SmartDetector; print('Detector OK')"

# Probar analizador  
python -c "from src.analyzer import OccupancyAnalyzer; print('Analyzer OK')"

# Verificar configuración
python config.py
```

### 📊 Integración en Otros Proyectos
Los módulos pueden importarse independientemente:
```python
from src.models import ParkingSpace
from src.detector import SmartDetector
from src.analyzer import OccupancyAnalyzer
```

---

## 🔧 Desarrollo y Extensión

### Agregar Nuevo Método de Detección
1. Editar `src/detector.py`
2. Agregar método `detect_spaces_nuevo_metodo()`
3. Integrar en `detect_spaces_combined()`

### Agregar Nuevo Análisis
1. Editar `src/analyzer.py`
2. Agregar método `analyze_nuevo_metodo()`
3. Actualizar `analyze_with_history()`

### Nueva Funcionalidad UI
1. Editar `src/gui.py`
2. Agregar controles en `setup_ui()`
3. Implementar lógica correspondiente

---

## 📚 Documentación Adicional

- 📖 **[Documentación Técnica](docs/REFACTOR_v2_README.md)** - Detalles de implementación
- 🏗️ **[Arquitectura](src/)** - Explora el código fuente modular

---

## 🎊 Conclusión

Esta versión modular representa una **evolución significativa** del proyecto CarPark:

- ✅ **Arquitectura profesional** con separación de responsabilidades
- ✅ **Código mantenible** y escalable
- ✅ **Funcionalidad completa** sin comprometer características
- ✅ **Fácil extensión** para nuevas funcionalidades
- ✅ **Mejor organización** y legibilidad del código

**¡Disfruta analizando estacionamientos con una arquitectura de software profesional!** 🚀

---

## 📝 Licencia

Este proyecto está bajo la licencia MIT. Ver el archivo LICENSE para más detalles.
