"""
Configuración del proyecto CarPark - Versión Modular
Este archivo contiene las rutas y configuraciones principales del proyecto.
"""
import os

# Directorio base del proyecto
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Directorios
SRC_DIR = os.path.join(BASE_DIR, "src")
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
DOCS_DIR = os.path.join(BASE_DIR, "docs")
LEGACY_DIR = os.path.join(BASE_DIR, "legacy")

# Archivos de ejemplo incluidos
EXAMPLE_VIDEO = os.path.join(ASSETS_DIR, "carPark.mp4")
EXAMPLE_IMAGE = os.path.join(ASSETS_DIR, "carParkImg.png")
EXAMPLE_POSITIONS = os.path.join(ASSETS_DIR, "CarParkPos")

# Configuraciones por defecto
DEFAULT_CONFIG = {
    "video_extensions": [".mp4", ".avi", ".mov", ".mkv", ".wmv"],
    "image_extensions": [".jpg", ".jpeg", ".png", ".bmp", ".tiff"],
    "detection_confidence": 0.7,
    "min_space_area": 1000,
    "max_space_area": 50000,
    "default_space_color": (0, 255, 0),  # Verde
    "occupied_space_color": (0, 0, 255),  # Rojo
    "empty_space_color": (0, 255, 0),    # Verde
    "analysis_methods": ["fixed", "adaptive", "background"],
    "default_analysis_method": "adaptive",
}

def get_asset_path(filename: str) -> str:
    """Obtiene la ruta completa de un archivo en assets/"""
    return os.path.join(ASSETS_DIR, filename)

def ensure_directories():
    """Asegura que todas las carpetas necesarias existan"""
    for directory in [SRC_DIR, ASSETS_DIR, DOCS_DIR, LEGACY_DIR]:
        os.makedirs(directory, exist_ok=True)

def get_project_info() -> dict:
    """Retorna información del proyecto"""
    return {
        "name": "CarPark Project",
        "version": "3.0 - Modular",
        "description": "Sistema modular de análisis de estacionamiento",
        "architecture": "Modular con separación de responsabilidades",
        "modules": [
            "models - Modelos de datos",
            "video_manager - Gestión de video", 
            "detector - Detección de espacios",
            "analyzer - Análisis de ocupación",
            "file_manager - Gestión de archivos",
            "space_editor - Editor visual",
            "gui - Interfaz principal"
        ]
    }

if __name__ == "__main__":
    print("=== Configuración del Proyecto CarPark Modular ===")
    
    info = get_project_info()
    print(f"Proyecto: {info['name']} v{info['version']}")
    print(f"Descripción: {info['description']}")
    print(f"Arquitectura: {info['architecture']}")
    
    print(f"\nDirectorios:")
    print(f"Base: {BASE_DIR}")
    print(f"Código fuente: {SRC_DIR}")
    print(f"Assets: {ASSETS_DIR}")
    print(f"Documentación: {DOCS_DIR}")
    print(f"Legacy: {LEGACY_DIR}")
    
    print(f"\nMódulos principales:")
    for module in info['modules']:
        print(f"  - {module}")
    
    print(f"\nArchivos de ejemplo:")
    print(f"Video: {EXAMPLE_VIDEO}")
    print(f"Imagen: {EXAMPLE_IMAGE}")
    print(f"Posiciones: {EXAMPLE_POSITIONS}")
    
    ensure_directories()
    print(f"\n✅ Configuración verificada")
