# 🚗 CarPark Project - Sistema Completo de Análisis de Estacionamientos

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![OpenCV](https://img.shields.io/badge/OpenCV-4.8+-green.svg)](https://opencv.org)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 📋 Descripción

**CarPark Project** es un sistema completo e inteligente para el **análisis automático de espacios de estacionamiento** usando visión por computadora. El proyecto incluye detección automática avanzada, análisis de ocupación en tiempo real, y herramientas profesionales de edición integradas en una sola aplicación moderna.

### ✨ Características Principales

- 🧠 **Detección Automática Inteligente** con algoritmos avanzados
- 📊 **Análisis de Ocupación** con múltiples métodos (fijo, adaptativo, ML)
- 🎨 **Interfaz Moderna** con tema oscuro y herramientas profesionales
- 📹 **Soporte Multi-fuente** (videos, cámaras, imágenes)
- 💾 **Múltiples Formatos** (JSON, CSV, Pickle)
- 🔧 **Editor Visual** de espacios con herramientas avanzadas
- 📈 **Estadísticas en Tiempo Real** y exportación de resultados
- 🎯 **Una Sola Ventana** - Todo integrado sin aplicaciones separadas

---

## 🚀 Inicio Rápido

### 1. **Instalar Dependencias**
```bash
pip install -r requirements.txt
```

### 2. **Ejecutar la Aplicación Principal**
```bash
python main_app.py
```

### 3. **¡Listo!** 
- La aplicación se abrirá con todas las funcionalidades integradas
- Incluye editor de espacios, análisis automático y monitoreo en tiempo real
- Ejemplos incluidos: video, imagen y configuración de espacios guardada

---

## 📁 Estructura del Proyecto (Limpia y Optimizada)

```
CarParkProject/
├── 🚀 main_app.py                    # Aplicación principal moderna (ÚNICO PUNTO DE ENTRADA)
├── ⚙️ config.py                      # Configuración del proyecto
├── 📋 requirements.txt               # Dependencias actualizadas
├── 📖 README.md                      # Documentación principal
├── 📂 assets/                        # Recursos multimedia
│   ├── 🎬 carPark.mp4               # Video de ejemplo
│   ├── 🖼️ carParkImg.png            # Imagen de ejemplo
│   └── 📍 CarParkPos                # Posiciones guardadas
├── 📂 docs/                          # Documentación técnica
│   └── 📚 REFACTOR_v2_README.md     # Información técnica del refactor
└── 📂 legacy/                        # Versiones de referencia (solo principales)
    ├── 📱 main.py                   # Versión original del proyecto
    └── 📱 main_app.py               # Versión anterior refactorizada
```

### 🎯 **Filosofía del Proyecto: Simplicidad y Potencia**
- **Una sola aplicación**: `main_app.py` - Todo integrado en una ventana moderna
- **Sin duplicaciones**: Eliminados archivos redundantes y herramientas innecesarias
- **Estructura limpia**: Solo archivos esenciales y bien organizados
- **Plug & Play**: Ejecutar `python main_app.py` y funciona inmediatamente

---

## 🛠️ Funcionalidades Integradas

### 🎨 Editor Visual de Espacios
- Herramientas de dibujo, selección, movimiento y redimensionado
- Detección automática inteligente de espacios
- Guardado/carga en múltiples formatos
- Vista previa en tiempo real

### 📊 Análisis de Ocupación
- Algoritmos adaptativos para diferentes condiciones de luz
- Estadísticas en tiempo real
- Exportación de reportes en CSV
- Historial de ocupación

### 📹 Gestión de Fuentes
- Soporte para videos (MP4, AVI, MOV, etc.)
- Cámaras web en vivo
- Imágenes estáticas
- Controles de reproducción avanzados

---

## 📋 Requisitos del Sistema

- **Python**: 3.8 o superior
- **OpenCV**: 4.x (instalado automáticamente)
- **Tkinter**: Incluido con Python
- **PIL/Pillow**: Para manejo de imágenes
- **NumPy**: Para cálculos numéricos

---

## ⚡ Instalación y Uso

### Instalación Básica
```bash
# 1. Clonar o descargar el proyecto
git clone [tu-repositorio]
cd CarParkProject

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Ejecutar
python main_app.py
```

### Primer Uso
1. **Abrir video**: Clic en "Cargar Video" y selecciona `assets/carPark.mp4`
2. **Cargar espacios**: Clic en "Cargar Espacios" y selecciona `assets/CarParkPos`
3. **Iniciar análisis**: Clic en "Iniciar/Pausar" para comenzar el monitoreo
4. **Ver estadísticas**: Panel derecho muestra ocupación en tiempo real

---

## 🔧 Configuración Avanzada

El archivo `config.py` permite personalizar:
- Rutas de archivos de ejemplo
- Colores de espacios ocupados/libres
- Configuraciones de detección
- Extensiones de archivo soportadas

---

## 📚 Documentación Técnica

- 📖 **[Información del Refactor](docs/REFACTOR_v2_README.md)** - Detalles técnicos y arquitectura

---

## 🎯 Diferencias con Versiones Anteriores

### ✅ Versión Actual (Optimizada)
- Una sola aplicación integrada
- Interfaz moderna y unificada
- Sin archivos redundantes
- Estructura limpia y profesional
- Configuración centralizada

### ❌ Versiones Anteriores (Legacy)
- Múltiples aplicaciones separadas
- Archivos duplicados y herramientas redundantes
- Estructura compleja con muchas carpetas
- Configuraciones dispersas

---

## 📝 Licencia

Este proyecto está bajo la licencia MIT. Ver el archivo LICENSE para más detalles.

---

## 👥 Contribuir

Las contribuciones son bienvenidas. Por favor:
1. Fork el proyecto
2. Crea una rama para tu feature
3. Commit tus cambios
4. Push a la rama
5. Abre un Pull Request

---

**🚀 ¡Disfruta analizando estacionamientos con tecnología moderna!**
