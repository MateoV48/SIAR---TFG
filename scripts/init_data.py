# Script para inicializar datos básicos en la base de datos
# Ejecutar desde la raíz del proyecto: python scripts/init_data.py

import sys
import os

# Agregar el directorio raíz del proyecto al path
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

from app import create_app, db
from app.models import Curso

app = create_app()

with app.app_context():
    # Crear cursos básicos si no existen
    cursos_default = [
        {'nombre': '5to A', 'nivel': '5to', 'division': 'A'},
        {'nombre': '5to B', 'nivel': '5to', 'division': 'B'},
        {'nombre': '5to C', 'nivel': '5to', 'division': 'C'},
        {'nombre': '4to A', 'nivel': '4to', 'division': 'A'},
        {'nombre': '4to B', 'nivel': '4to', 'division': 'B'},
        {'nombre': '4to C', 'nivel': '4to', 'division': 'C'},
    ]
    
    for curso_data in cursos_default:
        curso = Curso.query.filter_by(nombre=curso_data['nombre']).first()
        if not curso:
            curso = Curso(**curso_data)
            db.session.add(curso)
            print(f"Creado curso: {curso_data['nombre']}")
        else:
            print(f"Curso {curso_data['nombre']} ya existe")
    
    db.session.commit()
    print("\n✅ Inicialización de datos completada!")

