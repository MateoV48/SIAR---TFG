"""
Script simplificado para agregar cursos directamente a la migración.
"""
from app import create_app, db
from app.models import Curso

def seed_cursos():
    app = create_app()
    
    with app.app_context():
        # Cursos de educación secundaria
        cursos_data = [
            # 1er año
            {'nombre': '1ro A', 'nivel': '1ro', 'division': 'A'},
            {'nombre': '1ro B', 'nivel': '1ro', 'division': 'B'},
            {'nombre': '1ro C', 'nivel': '1ro', 'division': 'C'},
            {'nombre': '1ro D', 'nivel': '1ro', 'division': 'D'},
            # 2do año
            {'nombre': '2do A', 'nivel': '2do', 'division': 'A'},
            {'nombre': '2do B', 'nivel': '2do', 'division': 'B'},
            {'nombre': '2do C', 'nivel': '2do', 'division': 'C'},
            {'nombre': '2do D', 'nivel': '2do', 'division': 'D'},
            # 3er año
            {'nombre': '3ro A', 'nivel': '3ro', 'division': 'A'},
            {'nombre': '3ro B', 'nivel': '3ro', 'division': 'B'},
            {'nombre': '3ro C', 'nivel': '3ro', 'division': 'C'},
            {'nombre': '3ro D', 'nivel': '3ro', 'division': 'D'},
            # 4to año
            {'nombre': '4to A', 'nivel': '4to', 'division': 'A'},
            {'nombre': '4to B', 'nivel': '4to', 'division': 'B'},
            {'nombre': '4to C', 'nivel': '4to', 'division': 'C'},
            # 5to año
            {'nombre': '5to A', 'nivel': '5to', 'division': 'A'},
            {'nombre': '5to B', 'nivel': '5to', 'division': 'B'},
            {'nombre': '5to C', 'nivel': '5to', 'division': 'C'},
        ]
        
        try:
            agregados = 0
            for c in cursos_data:
                if not Curso.query.filter_by(nombre=c['nombre']).first():
                    db.session.add(Curso(**c, activo=True))
                    agregados += 1
                    print(f"✓ {c['nombre']}")
            
            db.session.commit()
            print(f"\nTotal: {agregados} cursos agregados")
        except Exception as e:
            print(f"Error: {e}")
            db.session.rollback()

if __name__ == '__main__':
    seed_cursos()
