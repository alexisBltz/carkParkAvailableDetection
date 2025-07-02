"""
Demo de CarPark Professional v3.0
Muestra todas las funcionalidades de la nueva interfaz moderna
"""
import tkinter as tk
from tkinter import messagebox
import sys
import os

# Agregar el directorio actual al path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

def main():
    """Función principal de la demo"""
    print("=" * 70)
    print("🚗 CARPARK PROFESSIONAL v3.0 - DEMO")
    print("=" * 70)
    print()
    print("🎨 NUEVAS CARACTERÍSTICAS:")
    print("   ✅ Interfaz completamente renovada con tema oscuro")
    print("   ✅ Diseño moderno inspirado en aplicaciones profesionales")
    print("   ✅ Organización por pestañas para mejor navegación")
    print("   ✅ Estadísticas en tiempo real con indicadores visuales")
    print("   ✅ Integración completa de funcionalidades legacy")
    print("   ✅ Tooltips informativos en todos los controles")
    print("   ✅ Barra de estado moderna con información del sistema")
    print("   ✅ Iconos personalizados y colores profesionales")
    print()
    print("📺 PESTAÑAS DISPONIBLES:")
    print("   1. 📺 Monitor Principal - Vista en tiempo real del estacionamiento")
    print("   2. ✏️ Editor de Espacios - Herramientas de edición avanzadas")
    print("   3. 📈 Análisis - Gráficos y estadísticas detalladas")
    print("   4. 🔧 Legacy Tools - Funcionalidades del algoritmo original")
    print("   5. ⚙️ Configuración - Parámetros del sistema")
    print()
    print("🔧 FUNCIONALIDADES LEGACY MEJORADAS:")
    print("   • Editor clásico con interfaz original preservada")
    print("   • Análisis de video con algoritmo original optimizado")
    print("   • Compatibilidad total con archivos CarParkPos")
    print("   • Mejoras visuales sin cambiar la funcionalidad")
    print()
    print("🎯 MEJORAS EN LA INTERFAZ:")
    print("   • Tema oscuro profesional con paleta de colores moderna")
    print("   • Tarjetas y paneles con bordes redondeados")
    print("   • Botones con estados hover y pressed")
    print("   • Indicadores de estado con colores semáforo")
    print("   • Barras de progreso para visualización de ocupación")
    print("   • Iconos emoji para mejor identificación visual")
    print()
    
    # Mostrar diálogo de confirmación
    root = tk.Tk()
    root.withdraw()  # Ocultar ventana principal
    
    response = messagebox.askyesno(
        "CarPark Professional v3.0",
        "¿Deseas iniciar la aplicación con la nueva interfaz moderna?\n\n"
        "✨ Características nuevas:\n"
        "• Tema oscuro profesional\n"
        "• Navegación por pestañas\n"
        "• Estadísticas en tiempo real\n"
        "• Herramientas legacy integradas\n"
        "• Configuración avanzada\n\n"
        "¡La funcionalidad original se mantiene 100% intacta!"
    )
    
    if response:
        print("🚀 Iniciando CarPark Professional v3.0...")
        print("   Cargando interfaz moderna...")
        
        root.destroy()
        
        # Ejecutar la aplicación principal
        exec(open('main.py').read())
    else:
        print("👋 Demo cancelada. ¡Gracias por probar CarPark Professional!")
        root.destroy()

if __name__ == "__main__":
    main()
