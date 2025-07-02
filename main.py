"""
Punto de entrada principal para CarPark Project v3.0 - GUI Moderna
Sistema avanzado de detección de espacios de estacionamiento con interfaz moderna
Lanza únicamente la GUI moderna con tema oscuro y todas las funcionalidades integradas
"""
import sys
import os
import tkinter as tk
from tkinter import messagebox
import logging
from datetime import datetime

# Agregar el directorio actual al path para poder importar los módulos
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('carpark.log'),
        logging.StreamHandler()
    ]
)

def check_dependencies():
    """Verifica que todas las dependencias estén instaladas"""
    missing_deps = []
    optional_deps = []
    
    # Dependencias principales
    required_modules = {
        'cv2': 'opencv-python',
        'numpy': 'numpy', 
        'PIL': 'Pillow'
    }
    
    # Dependencias opcionales para mejores funcionalidades
    optional_modules = {
        'cvzone': 'cvzone',
        'scipy': 'scipy',
        'skimage': 'scikit-image'
    }
    
    # Verificar dependencias principales
    for module, package in required_modules.items():
        try:
            __import__(module)
        except ImportError:
            missing_deps.append(package)
    
    # Verificar dependencias opcionales
    for module, package in optional_modules.items():
        try:
            __import__(module)
        except ImportError:
            optional_deps.append(package)
    
    if missing_deps:
        messagebox.showerror(
            "Error de Dependencias Críticas",
            f"Faltan las siguientes dependencias críticas:\n" + 
            "\n".join(f"• {dep}" for dep in missing_deps) +
            "\n\nInstala las dependencias con:\n"
            "pip install -r requirements.txt"
        )
        return False
    
    if optional_deps:
        print(f"⚠️  Dependencias opcionales faltantes: {', '.join(optional_deps)}")
        print("Para funcionalidades avanzadas, instala: pip install " + " ".join(optional_deps))
    
    return True

def main():
    """Función principal de la aplicación"""
    print("=" * 60)
    print("🚗 CarPark Project v3.0 - GUI Moderna")
    print("🎯 Sistema avanzado con interfaz moderna y tema oscuro")
    print(f"📅 Iniciado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Configurar logging
    logging.info("Iniciando CarPark Project v3.0 - GUI Moderna")
    
    # Verificar dependencias
    if not check_dependencies():
        logging.error("Error en verificación de dependencias")
        return
    
    try:
        # Crear ventana principal
        root = tk.Tk()
        
        # Configurar icono y estilo de ventana
        try:
            root.iconbitmap(default='assets/icon.ico')  # Si existe un icono
        except:
            pass
        
        # Configurar el protocolo de cierre
        def on_closing():
            if messagebox.askokcancel("Salir", "¿Deseas cerrar la aplicación?"):
                logging.info("Aplicación cerrada por el usuario")
                root.destroy()
        
        root.protocol("WM_DELETE_WINDOW", on_closing)
        
        # Inicializar GUI Moderna directamente
        from src.modern_gui import create_modern_gui
        app = create_modern_gui(root)
        
        print("✅ Aplicación moderna iniciada correctamente")
        print("🖥️  Interfaz moderna con tema oscuro activada")
        print("📝 Funcionalidades disponibles:")
        print("   • 🎨 Interfaz moderna con tema oscuro")
        print("   • 📺 Monitor principal con pestañas")
        print("   • ✏️ Editor visual de espacios integrado")
        print("   • 📈 Análisis y estadísticas en tiempo real")
        print("   • 🔧 Herramientas legacy completamente funcionales")
        logging.info("GUI moderna iniciada correctamente")
        
        # Ejecutar la aplicación
        root.mainloop()
        
    except ImportError as e:
        error_msg = f"No se pudo cargar la aplicación:\n{str(e)}\n\nVerifica que todos los archivos estén presentes en src/"
        print(f"❌ Error: {error_msg}")
        logging.error(f"Error de importación: {e}")
        messagebox.showerror("Error de Importación", error_msg)
    except Exception as e:
        error_msg = f"Error al inicializar la aplicación:\n{str(e)}"
        print(f"❌ Error inesperado: {error_msg}")
        logging.error(f"Error inesperado: {e}")
        messagebox.showerror("Error Inesperado", error_msg)

if __name__ == "__main__":
    main()
