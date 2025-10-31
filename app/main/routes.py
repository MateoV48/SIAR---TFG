from flask import Blueprint, render_template


main = Blueprint('main', __name__)


@main.route('/dashboard')
def dashboard():
    alumnos = [
        {"apellido": "García", "nombre": "Sofía", "curso": "5to \"A\"", "riesgo": "Alto", "precision": 92},
        {"apellido": "Martínez", "nombre": "Mateo", "curso": "4to \"B\"", "riesgo": "Alto", "precision": 89},
        {"apellido": "Rodríguez", "nombre": "Camila", "curso": "5to \"A\"", "riesgo": "Medio", "precision": 85},
        {"apellido": "López", "nombre": "Benjamín", "curso": "5to \"C\"", "riesgo": "Bajo", "precision": 95},
    ]
    cursos = ["5to \"A\"", "4to \"B\"", "5to \"C\""]
    return render_template('main/dashboard.html', alumnos=alumnos, cursos=cursos)


@main.route('/alumno/<int:alumno_id>')
def alumno_detalle(alumno_id: int):
    alumno = {
        "nombre_completo": "García, Sofía",
        "curso": "5to \"A\"",
        "promedio_g2": 4.5,
        "materias_previas": 2,
        "inasistencias": 15,
        "tiempo_estudio": "< 2 horas",
        "factores_riesgo": [
            "Número de materias reprobadas.",
            "Alto número de inasistencias.",
            "Bajo tiempo de estudio semanal.",
        ],
        "recomendacion": "Iniciar protocolo de seguimiento con tutor y preceptor.",
    }
    return render_template('main/alumno_detalle.html', alumno=alumno)


@main.route('/usuarios')
def usuarios():
    usuarios_data = [
        {"apellido": "Pérez", "nombre": "Juan", "email": "jperez@colegio.edu.ar", "rol": "Docente"},
        {"apellido": "Gómez", "nombre": "Ana", "email": "agomez@colegio.edu.ar", "rol": "Docente"},
    ]
    return render_template('main/usuarios.html', usuarios=usuarios_data)


