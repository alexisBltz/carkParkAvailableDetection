#!/usr/bin/env python3
"""
Test de integración para verificar que los analizadores funcionan en la GUI
"""
import sys
import os

# Agregar src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_analyzers_import():
    """Probar que los analizadores se pueden importar"""
    print("🔧 Probando imports de analizadores...")
    
    try:
        from src.simple_analyzer import SimpleOccupancyAnalyzer
        print("✅ SimpleOccupancyAnalyzer importado correctamente")
        
        from src.working_analyzer import WorkingOccupancyAnalyzer
        print("✅ WorkingOccupancyAnalyzer importado correctamente")
        
        from src.models import ParkingSpace, OccupancyStatus
        print("✅ Modelos importados correctamente")
        
        return True
        
    except ImportError as e:
        print(f"❌ Error de importación: {e}")
        return False

def test_analyzers_functionality():
    """Probar funcionalidad básica de los analizadores"""
    print("\n🔧 Probando funcionalidad de analizadores...")
    
    try:
        import cv2
        import numpy as np
        from src.simple_analyzer import SimpleOccupancyAnalyzer
        from src.working_analyzer import WorkingOccupancyAnalyzer
        from src.models import ParkingSpace
        
        # Crear una imagen de prueba
        test_image = np.ones((400, 600, 3), dtype=np.uint8) * 128  # Imagen gris
        
        # Crear espacios de prueba
        spaces = [
            ParkingSpace(x=50, y=50, width=100, height=80, id="test_1"),
            ParkingSpace(x=200, y=50, width=100, height=80, id="test_2"),
        ]
        
        # Probar analizador simple
        simple_analyzer = SimpleOccupancyAnalyzer(threshold=0.23)
        simple_results = simple_analyzer.analyze_spaces(test_image, spaces)
        print(f"✅ Analizador simple: {len(simple_results)} resultados")
        
        # Probar analizador working
        working_analyzer = WorkingOccupancyAnalyzer(pixel_threshold=900)
        working_results = working_analyzer.analyze_spaces(test_image, spaces)
        print(f"✅ Analizador working: {len(working_results)} resultados")
        
        # Probar métodos de configuración
        print(f"✅ Threshold simple: {simple_analyzer.get_threshold()}")
        print(f"✅ Threshold working: {working_analyzer.get_pixel_threshold()}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en pruebas: {e}")
        return False

def test_gui_import():
    """Probar que la GUI se puede importar"""
    print("\n🔧 Probando import de GUI...")
    
    try:
        from src.gui import CarParkGUI
        print("✅ CarParkGUI importado correctamente")
        return True
        
    except ImportError as e:
        print(f"❌ Error importando GUI: {e}")
        return False

def main():
    """Función principal de pruebas"""
    print("🚗 Test de Integración CarPark Project")
    print("=" * 50)
    
    success = True
    
    # Test de imports
    if not test_analyzers_import():
        success = False
    
    # Test de funcionalidad
    if not test_analyzers_functionality():
        success = False
    
    # Test de GUI
    if not test_gui_import():
        success = False
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 TODOS LOS TESTS PASARON")
        print("💡 Puedes ejecutar 'python main.py' para usar la aplicación")
    else:
        print("❌ ALGUNOS TESTS FALLARON")
        print("🔧 Revisa las dependencias e imports")
    
    return success

if __name__ == "__main__":
    main()
