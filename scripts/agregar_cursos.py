"""
Script para agregar cursos de educación secundaria a la base de datos.
Ejecutar desde la raíz del proyecto con:
    python scripts/agregar_cursos.py
"""

import sys
import os

# Agregar la raíz del proyecto al path para importar app
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from app import create_app, db
from app.models import Curso

def agregar_cursos():
    """Agrega los cursos de secundaria a la BD"""
    app = create_app()
    
    with app.app_context():
        # Cursos de educación secundaria
        cursos_data = [
            # 1er año (9no grado)
            {'nombre': '1ro A', 'nivel': '1ro', 'division': 'A'},
            {'nombre': '1ro B', 'nivel': '1ro', 'division': 'B'},
            {'nombre': '1ro C', 'nivel': '1ro', 'division': 'C'},
            {'nombre': '1ro D', 'nivel': '1ro', 'division': 'D'},
            
            # 2do año (10mo grado)
            {'nombre': '2do A', 'nivel': '2do', 'division': 'A'},
            {'nombre': '2do B', 'nivel': '2do', 'division': 'B'},
            {'nombre': '2do C', 'nivel': '2do', 'division': 'C'},
            {'nombre': '2do D', 'nivel': '2do', 'division': 'D'},
            
            # 3er año (11vo grado)
            {'nombre': '3ro A', 'nivel': '3ro', 'division': 'A'},
            {'nombre': '3ro B', 'nivel': '3ro', 'division': 'B'},
            {'nombre': '3ro C', 'nivel': '3ro', 'division': 'C'},
            {'nombre': '3ro D', 'nivel': '3ro', 'division': 'D'},
            
            # 4to año (12vo grado)
            {'nombre': '4to A', 'nivel': '4to', 'division': 'A'},
            {'nombre': '4to B', 'nivel': '4to', 'division': 'B'},
            {'nombre': '4to C', 'nivel': '4to', 'division': 'C'},
            
            # 5to año (13er grado - final)
            {'nombre': '5to A', 'nivel': '5to', 'division': 'A'},
            {'nombre': '5to B', 'nivel': '5to', 'division': 'B'},
            {'nombre': '5to C', 'nivel': '5to', 'division': 'C'},
        ]
        
        cursos_agregados = 0
        cursos_existentes = 0
        
        for curso_info in cursos_data:
            # Verificar si ya existe
            curso_existente = Curso.query.filter_by(nombre=curso_info['nombre']).first()
            
            if curso_existente:
                print(f"⊘ {curso_info['nombre']} ya existe en la BD")
                cursos_existentes += 1
            else:
                # Crear nuevo curso
                nuevo_curso = Curso(
                    nombre=curso_info['nombre'],
                    nivel=curso_info['nivel'],
                    division=curso_info['division'],
                    activo=True
                )
                db.session.add(nuevo_curso)
                print(f"✓ {curso_info['nombre']} agregado")
                cursos_agregados += 1
        
        # Guardar cambios
        if cursos_agregados > 0:
            db.session.commit()
            print(f"\n✓ {cursos_agregados} cursos nuevos agregados exitosamente")
        else:
            db.session.rollback()
            print(f"\n⊘ No se agregaron cursos nuevos")
        
        print(f"⊘ {cursos_existentes} cursos ya existían")
        print(f"Total de cursos en la BD: {Curso.query.count()}")

if __name__ == '__main__':
    agregar_cursos()
