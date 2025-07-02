"""
Setup CarPark - Script de instalación y verificación
Prepara el entorno y verifica que todo esté listo para usar
"""
import subprocess
import sys
import os
import urllib.request
from pathlib import Path

def install_dependencies():
    """Instala las dependencias necesarias"""
    print("📦 Instalando dependencias...")
    
    try:
        # Actualizar pip
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
        
        # Instalar dependencias desde requirements.txt
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        
        print("✅ Dependencias instaladas correctamente")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error instalando dependencias: {e}")
        return False

def verify_installation():
    """Verifica que las dependencias estén instaladas"""
    print("🔍 Verificando instalación...")
    
    required_modules = [
        ("cv2", "opencv-python"),
        ("numpy", "numpy"),
        ("PIL", "Pillow")
    ]
    
    optional_modules = [
        ("cvzone", "cvzone"),
        ("scipy", "scipy"),
        ("skimage", "scikit-image")
    ]
    
    missing_required = []
    missing_optional = []
    
    # Verificar módulos requeridos
    for module, package in required_modules:
        try:
            __import__(module)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package}")
            missing_required.append(package)
    
    # Verificar módulos opcionales
    for module, package in optional_modules:
        try:
            __import__(module)
            print(f"✅ {package} (opcional)")
        except ImportError:
            print(f"⚠️  {package} (opcional)")
            missing_optional.append(package)
    
    if missing_required:
        print(f"\n❌ Faltan dependencias críticas: {', '.join(missing_required)}")
        return False
    
    if missing_optional:
        print(f"\n⚠️  Dependencias opcionales faltantes: {', '.join(missing_optional)}")
        print("El sistema funcionará pero con funcionalidades limitadas")
    
    return True

def create_directories():
    """Crea los directorios necesarios"""
    print("📁 Creando directorios...")
    
    directories = [
        "assets",
        "docs",
        "src/__pycache__",
        "__pycache__"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ {directory}")

def download_sample_files():
    """Descarga archivos de ejemplo si no existen"""
    print("📥 Verificando archivos de ejemplo...")
    
    sample_files = {
        "assets/carParkImg.png": "https://via.placeholder.com/800x600/CCCCCC/000000?text=Car+Park+Image",
        "config.py": None  # Se crea localmente
    }
    
    # Crear config.py si no existe
    if not os.path.exists("config.py"):
        config_content = '''"""
Configuración del sistema CarPark
"""
import os

# Rutas
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

# Configuraciones de análisis
ANALYSIS_METHODS = ["fixed", "adaptive", "background"]
DEFAULT_ANALYSIS_METHOD = "adaptive"
'''
        with open("config.py", "w", encoding="utf-8") as f:
            f.write(config_content)
        print("✅ config.py creado")
    
    # Verificar archivos en assets
    assets_files = [
        "assets/carParkImg.png",
        "assets/carPark.mp4"
    ]
    
    missing_files = []
    for file_path in assets_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"⚠️  {file_path} - No encontrado")
            missing_files.append(file_path)
    
    if missing_files:
        print("\n📝 Archivos faltantes:")
        for file_path in missing_files:
            print(f"   • {file_path}")
        print("\nPuedes:")
        print("   1. Colocar tus propios archivos en la carpeta assets/")
        print("   2. Usar el editor legacy para crear espacios")
        print("   3. Cargar archivos desde la GUI")

def run_tests():
    """Ejecuta pruebas básicas del sistema"""
    print("🧪 Ejecutando pruebas básicas...")
    
    try:
        # Probar importaciones
        sys.path.insert(0, "src")
        
        from src.models import ParkingSpace
        space = ParkingSpace(0, 0, 100, 50)
        print("✅ Modelos de datos")
        
        from src.legacy_detector import LegacySpaceEditor
        print("✅ Detector legacy")
        
        import tkinter as tk
        root = tk.Tk()
        root.destroy()
        print("✅ Tkinter GUI")
        
        print("✅ Todas las pruebas pasaron")
        return True
        
    except Exception as e:
        print(f"❌ Error en pruebas: {e}")
        return False

def main():
    """Función principal del setup"""
    print("=" * 60)
    print("🚗 CarPark Project v3.0 - Setup & Verificación")
    print("=" * 60)
    
    steps = [
        ("📁 Crear directorios", create_directories),
        ("📦 Instalar dependencias", install_dependencies),
        ("🔍 Verificar instalación", verify_installation),
        ("📥 Preparar archivos", download_sample_files),
        ("🧪 Ejecutar pruebas", run_tests)
    ]
    
    success_count = 0
    
    for step_name, step_func in steps:
        print(f"\n{step_name}")
        print("-" * 40)
        
        try:
            if step_func():
                success_count += 1
                print(f"✅ {step_name} completado")
            else:
                print(f"⚠️  {step_name} con advertencias")
        except Exception as e:
            print(f"❌ Error en {step_name}: {e}")
    
    print("\n" + "=" * 60)
    print(f"📊 Resumen: {success_count}/{len(steps)} pasos completados")
    
    if success_count == len(steps):
        print("🎉 ¡Setup completado exitosamente!")
        print("\n🚀 Puedes ejecutar:")
        print("   python main.py                 # GUI completa")
        print("   python test_simple.py          # Prueba básica")
        print("   python launcher_legacy.py      # Herramientas legacy")
    else:
        print("⚠️  Setup completado con advertencias")
        print("Revisa los mensajes anteriores para más detalles")
    
    print("\n📚 Documentación completa en: docs/REFACTOR_v3_README.md")

if __name__ == "__main__":
    main()
