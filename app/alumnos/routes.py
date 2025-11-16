# Archivo: /app/alumnos/routes.py
# Rutas para gestión de alumnos (CRUD)

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models import Alumno, Curso
from app import db
from app.analisis import AnalizadorRiesgo


alumnos = Blueprint('alumnos', __name__)


@alumnos.route('/alumnos')
@login_required
def gestion():
    """Página principal de gestión de alumnos"""
    return render_template('alumnos/gestion.html')


@alumnos.route('/alumnos/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo():
    """Crear un nuevo alumno"""
    if request.method == 'POST':
        try:
            alumno = Alumno(
                nombre=request.form.get('nombre', '').strip(),
                apellido=request.form.get('apellido', '').strip(),
                dni=request.form.get('dni', '').strip() or None,
                curso_id=int(request.form.get('curso_id')),
                promedio_g2=float(request.form.get('promedio_g2')) if request.form.get('promedio_g2') else None,
                materias_previas=int(request.form.get('materias_previas', 0)),
                inasistencias=int(request.form.get('inasistencias', 0)),
                tiempo_estudio_semanal=request.form.get('tiempo_estudio_semanal', '').strip() or None
            )
            
            db.session.add(alumno)
            db.session.commit()
            
            # Analizar el nuevo alumno
            analizador = AnalizadorRiesgo()
            analizador.analizar_alumno(alumno)
            
            flash(f'Alumno {alumno.nombre_completo} creado exitosamente.', 'success')
            return redirect(url_for('main.alumno_detalle', alumno_id=alumno.id))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear el alumno: {str(e)}', 'danger')
    
    cursos = Curso.query.filter_by(activo=True).order_by(Curso.nombre).all()
    return render_template('alumnos/formulario.html', alumno=None, cursos=cursos, titulo='Nuevo Alumno')


@alumnos.route('/alumnos/<int:alumno_id>/editar', methods=['GET', 'POST'])
@login_required
def editar(alumno_id):
    """Editar un alumno existente"""
    alumno = Alumno.query.get_or_404(alumno_id)
    
    if request.method == 'POST':
        try:
            alumno.nombre = request.form.get('nombre', '').strip()
            alumno.apellido = request.form.get('apellido', '').strip()
            alumno.dni = request.form.get('dni', '').strip() or None
            alumno.curso_id = int(request.form.get('curso_id'))
            alumno.promedio_g2 = float(request.form.get('promedio_g2')) if request.form.get('promedio_g2') else None
            alumno.materias_previas = int(request.form.get('materias_previas', 0))
            alumno.inasistencias = int(request.form.get('inasistencias', 0))
            alumno.tiempo_estudio_semanal = request.form.get('tiempo_estudio_semanal', '').strip() or None
            
            db.session.commit()
            
            # Re-analizar el alumno con los nuevos datos
            analizador = AnalizadorRiesgo()
            analizador.analizar_alumno(alumno)
            
            flash(f'Alumno {alumno.nombre_completo} actualizado exitosamente.', 'success')
            return redirect(url_for('main.alumno_detalle', alumno_id=alumno.id))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar el alumno: {str(e)}', 'danger')
    
    cursos = Curso.query.filter_by(activo=True).order_by(Curso.nombre).all()
    return render_template('alumnos/formulario.html', alumno=alumno, cursos=cursos, titulo='Editar Alumno')


@alumnos.route('/alumnos/<int:alumno_id>/eliminar', methods=['POST'])
@login_required
def eliminar(alumno_id):
    """Eliminar (desactivar) un alumno"""
    if current_user.rol != 'Admin':
        flash('No tienes permisos para eliminar alumnos.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    alumno = Alumno.query.get_or_404(alumno_id)
    
    try:
        alumno.activo = False
        db.session.commit()
        flash(f'Alumno {alumno.nombre_completo} eliminado exitosamente.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar el alumno: {str(e)}', 'danger')
    
    return redirect(url_for('main.dashboard'))


