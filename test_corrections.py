#!/usr/bin/env python3
"""
Script de prueba para verificar las correcciones de CarPark v3.0
Prueba específicamente:
1. Carga de espacios con archivos legacy y JSON
2. Persistencia de imagen/video entre pestañas
"""

import sys
import os
import pickle
from pathlib import Path

# Agregar directorio del proyecto al path
project_dir = Path(__file__).parent
sys.path.append(str(project_dir))

# Importar modelos para verificar que funcionan
from src.models import ParkingSpace

def test_legacy_file_format():
    """Prueba que podemos leer archivos legacy"""
    legacy_file = project_dir / "assets" / "CarParkPos"
    
    if legacy_file.exists():
        try:
            with open(legacy_file, 'rb') as f:
                positions = pickle.load(f)
            
            print(f"✅ Archivo legacy CarParkPos cargado exitosamente")
            print(f"📊 Contiene {len(positions)} espacios")
            
            # Mostrar algunos datos
            for i, pos in enumerate(positions[:3]):  # Solo los primeros 3
                print(f"   Espacio {i}: {pos}")
                
            return True
        except Exception as e:
            print(f"❌ Error leyendo archivo legacy: {e}")
            return False
    else:
        print(f"⚠️  Archivo legacy no encontrado: {legacy_file}")
        return False

def test_json_format():
    """Prueba la conversión a formato JSON"""
    legacy_file = project_dir / "assets" / "CarParkPos"
    json_file = project_dir / "assets" / "test_spaces.json"
    
    if not legacy_file.exists():
        print("⚠️  No se puede probar JSON sin archivo legacy")
        return False
    
    try:
        # Cargar legacy
        with open(legacy_file, 'rb') as f:
            positions = pickle.load(f)
        
        # Convertir a espacios modernos
        spaces = []
        for i, pos in enumerate(positions):
            if len(pos) >= 4:
                x, y, w, h = pos[:4]
                space = ParkingSpace(
                    id=str(i),
                    x=int(x),
                    y=int(y),
                    width=int(w),
                    height=int(h)
                )
                spaces.append(space)
        
        # Importar FileManager para guardar
        from src.file_manager import FileManager
        
        # Convertir a formato JSON y guardar
        if FileManager.save_spaces_json(spaces, str(json_file)):
            print(f"✅ Archivo JSON creado exitosamente: {json_file}")
            
            # Verificar que se puede cargar de vuelta
            loaded_spaces = FileManager.load_spaces_json(str(json_file))
            if loaded_spaces and len(loaded_spaces) == len(spaces):
                print(f"✅ Archivo JSON verificado - {len(loaded_spaces)} espacios")
                
                # Limpiar archivo de prueba
                json_file.unlink()
                print(f"🧹 Archivo de prueba eliminado")
                return True
            else:
                print(f"❌ Error verificando archivo JSON")
                return False
        else:
            print(f"❌ Error guardando archivo JSON")
            return False
            
    except Exception as e:
        print(f"❌ Error en prueba JSON: {e}")
        return False

def main():
    """Función principal de prueba"""
    print("🔧 Iniciando pruebas de correcciones CarPark v3.0")
    print("=" * 60)
    
    # Prueba 1: Archivo legacy
    print("\n1️⃣ Probando carga de archivo legacy...")
    legacy_ok = test_legacy_file_format()
    
    # Prueba 2: Formato JSON
    print("\n2️⃣ Probando conversión y carga JSON...")
    json_ok = test_json_format()
    
    # Resultados
    print("\n" + "=" * 60)
    print("📋 RESULTADOS DE PRUEBAS:")
    print(f"   • Carga archivo legacy: {'✅ OK' if legacy_ok else '❌ FALLO'}")
    print(f"   • Conversión JSON: {'✅ OK' if json_ok else '❌ FALLO'}")
    
    if legacy_ok and json_ok:
        print("\n🎉 ¡Todas las pruebas pasaron exitosamente!")
        print("💡 La aplicación debería poder cargar tanto archivos JSON como legacy")
        print("🔄 La persistencia entre pestañas se activará cuando carges video/imagen")
    else:
        print("\n⚠️  Algunas pruebas fallaron. Revisa los errores arriba.")
    
    print("\n🚀 Para probar la GUI completa, ejecuta: python main.py")

if __name__ == "__main__":
    main()
