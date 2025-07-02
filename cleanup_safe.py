#!/usr/bin/env python3
"""
Script de limpieza automática para CarPark Project v3.0
Elimina archivos innecesarios manteniendo solo lo esencial para main.py
"""

import os
import shutil
from pathlib import Path

def safe_remove(filepath):
    """Eliminar archivo de forma segura"""
    try:
        if os.path.exists(filepath):
            os.remove(filepath)
            print(f"✅ Eliminado: {filepath}")
            return True
        else:
            print(f"⚠️  No encontrado: {filepath}")
            return False
    except Exception as e:
        print(f"❌ Error eliminando {filepath}: {e}")
        return False

def safe_remove_dir(dirpath):
    """Eliminar directorio de forma segura"""
    try:
        if os.path.exists(dirpath) and os.path.isdir(dirpath):
            shutil.rmtree(dirpath)
            print(f"✅ Directorio eliminado: {dirpath}")
            return True
        else:
            print(f"⚠️  Directorio no encontrado: {dirpath}")
            return False
    except Exception as e:
        print(f"❌ Error eliminando directorio {dirpath}: {e}")
        return False

def cleanup_carpark_project():
    """Limpiar el proyecto CarPark manteniendo solo archivos esenciales"""
    
    print("🧹 Iniciando limpieza del proyecto CarPark v3.0")
    print("🎯 Objetivo: Mantener solo archivos necesarios para main.py")
    print("=" * 60)
    
    # Cambiar al directorio del proyecto
    project_dir = Path(__file__).parent
    os.chdir(project_dir)
    
    eliminated_count = 0
    
    # FASE 1: Eliminar archivos main alternativos
    print("\n📋 FASE 1: Eliminando archivos main alternativos...")
    main_alternatives = [
        "main_modern.py",
        "main_selector.py", 
        "main_simple.py",
        "main_working.py",
        "carpark_simple.py",
        "demo_modern.py",
        "launcher_legacy.py",
        "simple_space_editor.py",
        "setup_carpark.py",
        "cleanup_project.py",
        "create_icons.py"
    ]
    
    for file in main_alternatives:
        if safe_remove(file):
            eliminated_count += 1
    
    # FASE 2: Eliminar archivos obsoletos en src/
    print("\n📋 FASE 2: Eliminando archivos obsoletos en src/...")
    obsolete_src_files = [
        "src/gui.py",
        "src/modern_gui_fixed.py", 
        "src/analyzer.py"  # Reemplazado por working_analyzer.py
    ]
    
    for file in obsolete_src_files:
        if safe_remove(file):
            eliminated_count += 1
    
    # FASE 3: Eliminar archivos de test
    print("\n📋 FASE 3: Eliminando archivos de test...")
    test_files = [
        "test_analyzer_simple.py",
        "test_canvas_update.py", 
        "test_complete_workflow.py",
        "test_corrections.py",
        "test_fixed_gui.py",
        "test_fixes.py",
        "test_full_workflow.py",
        "test_immediate_feedback.py",
        "test_integration.py",
        "test_load_spaces_error.py",
        "test_resize_fixes.py",
        "test_scaling_fix.py",
        "test_simple.py",
        "test_simple_analyzer.py",
        "test_user_scenario.py",
        "test_video.py",
        "test_working_analyzer.py"
    ]
    
    for file in test_files:
        if safe_remove(file):
            eliminated_count += 1
    
    # FASE 4: Limpiar documentación excesiva
    print("\n📋 FASE 4: Consolidando documentación...")
    doc_files_to_remove = [
        "README_FINAL.md",
        "README_MODERN_v3.md",
        "README_MODULAR.md", 
        "README_NEW.md",
        "README_SIMPLE.md",
        "DOCUMENTACION_COMPLETA.md",
        "ESTADO_FINAL.md",
        "FLUJO_COMPLETO_IMPLEMENTADO.md",
        "FUNCIONALIDADES_IMPLEMENTADAS.md",
        "CORRECCIONES_COMPLETADAS.md",
        "SOLUTION_REPORT.md"
    ]
    
    for file in doc_files_to_remove:
        if safe_remove(file):
            eliminated_count += 1
    
    # FASE 5: Limpiar archivos de log y temporales
    print("\n📋 FASE 5: Eliminando archivos temporales...")
    temp_files = [
        "carpark.log",
        "test_spaces.json"  # Si existe del testing
    ]
    
    for file in temp_files:
        if safe_remove(file):
            eliminated_count += 1
    
    # FASE 6: Limpiar __pycache__ 
    print("\n📋 FASE 6: Eliminando archivos cache...")
    cache_dirs = [
        "__pycache__",
        "src/__pycache__"
    ]
    
    for cache_dir in cache_dirs:
        if safe_remove_dir(cache_dir):
            eliminated_count += 1
    
    # VERIFICACIÓN: Mostrar archivos que QUEDAN (esenciales)
    print("\n" + "=" * 60)
    print("✅ LIMPIEZA COMPLETADA")
    print(f"📊 Archivos eliminados: {eliminated_count}")
    print("\n📁 ARCHIVOS ESENCIALES QUE QUEDAN:")
    
    essential_files = [
        "main.py",
        "config.py", 
        "requirements.txt",
        "README.md",
        "CLEANUP_ANALYSIS.md",
        "src/__init__.py",
        "src/modern_gui.py",
        "src/models.py",
        "src/modern_theme.py",
        "src/video_manager.py",
        "src/detector.py",
        "src/working_analyzer.py",
        "src/simple_analyzer.py",
        "src/file_manager.py",
        "src/space_editor.py",
        "src/legacy_detector.py"
    ]
    
    missing_essential = []
    for file in essential_files:
        if os.path.exists(file):
            print(f"  ✅ {file}")
        else:
            print(f"  ❌ {file} (FALTANTE)")
            missing_essential.append(file)
    
    if missing_essential:
        print(f"\n⚠️  ATENCIÓN: Faltan {len(missing_essential)} archivos esenciales")
        print("Verifica que no se hayan eliminado por error")
    else:
        print("\n🎉 ¡PROYECTO LIMPIO Y COMPLETO!")
        print("✅ Todos los archivos esenciales están presentes")
        print("🚀 El proyecto está listo para distribución")
    
    print("\n📋 PARA VERIFICAR QUE TODO FUNCIONA:")
    print("   python main.py")
    
    return eliminated_count, missing_essential

if __name__ == "__main__":
    try:
        eliminated, missing = cleanup_carpark_project()
        if not missing:
            print(f"\n🎯 RESUMEN: Proyecto limpiado exitosamente ({eliminated} archivos eliminados)")
        else:
            print(f"\n⚠️  RESUMEN: Limpieza completada con advertencias")
    except Exception as e:
        print(f"❌ Error durante la limpieza: {e}")
        import traceback
        traceback.print_exc()
