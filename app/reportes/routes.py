# Archivo: /app/reportes/routes.py
# Rutas para generar reportes en PDF usando WeasyPrint

from flask import Blueprint, render_template, make_response, flash, redirect, url_for
from flask_login import login_required, current_user
from datetime import datetime
import json
from app.models import Alumno, Curso
from app import db

# Importar WeasyPrint de forma condicional para evitar errores si faltan librerías del sistema
try:
    from weasyprint import HTML
    from weasyprint.text.fonts import FontConfiguration
    WEASYPRINT_AVAILABLE = True
except (OSError, ImportError) as e:
    WEASYPRINT_AVAILABLE = False
    WEASYPRINT_ERROR = str(e)


reportes = Blueprint('reportes', __name__)


@reportes.route('/reportes/alumno/<int:alumno_id>/pdf')
@login_required
def alumno_pdf(alumno_id):
    """Genera un PDF del reporte individual de un alumno"""
    if not WEASYPRINT_AVAILABLE:
        flash('Error: WeasyPrint no está disponible. Por favor, instala GTK para Windows o usa otro método de exportación.', 'danger')
        return redirect(url_for('main.alumno_detalle', alumno_id=alumno_id))
    
    alumno = Alumno.query.get_or_404(alumno_id)
    
    # Parsear factores de riesgo si es JSON
    factores_riesgo = []
    if alumno.factores_riesgo:
        try:
            factores_riesgo = json.loads(alumno.factores_riesgo)
        except:
            factores_riesgo = [alumno.factores_riesgo] if alumno.factores_riesgo else []
    
    curso_nombre = alumno.curso_obj.nombre if alumno.curso_obj else "Sin curso"
    
    alumno_data = {
        "id": alumno.id,
        "nombre_completo": alumno.nombre_completo,
        "nombre": alumno.nombre,
        "apellido": alumno.apellido,
        "dni": alumno.dni or "No especificado",
        "curso": curso_nombre,
        "promedio_g2": alumno.promedio_g2 or 0,
        "materias_previas": alumno.materias_previas or 0,
        "inasistencias": alumno.inasistencias or 0,
        "tiempo_estudio": alumno.tiempo_estudio_semanal or "No especificado",
        "factores_riesgo": factores_riesgo,
        "recomendacion": alumno.recomendacion or "Sin recomendación disponible",
        "nivel_riesgo": alumno.nivel_riesgo or "Sin analizar",
        "precision": alumno.precision_prediccion or 0,
        "fecha_actualizacion": alumno.fecha_actualizacion or alumno.fecha_creacion
    }
    
    # Renderizar template HTML
    html = render_template('reportes/alumno_pdf.html', 
                         alumno=alumno_data,
                         fecha_generacion=datetime.now())
    
    # Generar PDF
    font_config = FontConfiguration()
    pdf = HTML(string=html).write_pdf(font_config=font_config)
    
    # Crear respuesta
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'inline; filename=reporte_alumno_{alumno.apellido}_{alumno.nombre}_{datetime.now().strftime("%Y%m%d")}.pdf'
    
    return response


@reportes.route('/reportes/dashboard/pdf')
@login_required
def dashboard_pdf():
    """Genera un PDF del reporte completo del dashboard"""
    if not WEASYPRINT_AVAILABLE:
        flash('Error: WeasyPrint no está disponible. Por favor, instala GTK para Windows o usa otro método de exportación.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    # Obtener todos los alumnos activos
    alumnos_query = Alumno.query.filter_by(activo=True).order_by(Alumno.apellido, Alumno.nombre)
    alumnos_list = alumnos_query.all()
    
    # Preparar datos para el template
    alumnos_data = []
    for alumno in alumnos_list:
        curso_nombre = alumno.curso_obj.nombre if alumno.curso_obj else "Sin curso"
        alumnos_data.append({
            "apellido": alumno.apellido,
            "nombre": alumno.nombre,
            "curso": curso_nombre,
            "riesgo": alumno.nivel_riesgo or "Sin analizar",
            "precision": int(alumno.precision_prediccion) if alumno.precision_prediccion else 0
        })
    
    # Calcular estadísticas
    total_alumnos = len(alumnos_data)
    riesgo_alto = sum(1 for a in alumnos_data if a['riesgo'] == 'Alto')
    riesgo_medio = sum(1 for a in alumnos_data if a['riesgo'] == 'Medio')
    riesgo_bajo = sum(1 for a in alumnos_data if a['riesgo'] == 'Bajo')
    sin_analizar = sum(1 for a in alumnos_data if a['riesgo'] == 'Sin analizar')
    
    estadisticas = {
        'total': total_alumnos,
        'alto': riesgo_alto,
        'medio': riesgo_medio,
        'bajo': riesgo_bajo,
        'sin_analizar': sin_analizar
    }
    
    # Renderizar template HTML
    html = render_template('reportes/dashboard_pdf.html',
                         alumnos=alumnos_data,
                         estadisticas=estadisticas,
                         fecha_generacion=datetime.now(),
                         usuario=current_user.nombre + ' ' + current_user.apellido)
    
    # Generar PDF
    font_config = FontConfiguration()
    pdf = HTML(string=html).write_pdf(font_config=font_config)
    
    # Crear respuesta
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'inline; filename=reporte_dashboard_{datetime.now().strftime("%Y%m%d")}.pdf'
    
    return response


@reportes.route('/reportes/curso/<int:curso_id>/pdf')
@login_required
def curso_pdf(curso_id):
    """Genera un PDF del reporte de alumnos por curso"""
    if not WEASYPRINT_AVAILABLE:
        flash('Error: WeasyPrint no está disponible. Por favor, instala GTK para Windows o usa otro método de exportación.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    curso = Curso.query.get_or_404(curso_id)
    
    # Obtener alumnos del curso
    alumnos_query = Alumno.query.filter_by(curso_id=curso_id, activo=True).order_by(Alumno.apellido, Alumno.nombre)
    alumnos_list = alumnos_query.all()
    
    # Preparar datos para el template
    alumnos_data = []
    for alumno in alumnos_list:
        factores_riesgo = []
        if alumno.factores_riesgo:
            try:
                factores_riesgo = json.loads(alumno.factores_riesgo)
            except:
                factores_riesgo = [alumno.factores_riesgo] if alumno.factores_riesgo else []
        
        alumnos_data.append({
            "apellido": alumno.apellido,
            "nombre": alumno.nombre,
            "dni": alumno.dni or "No especificado",
            "promedio_g2": alumno.promedio_g2 or 0,
            "materias_previas": alumno.materias_previas or 0,
            "inasistencias": alumno.inasistencias or 0,
            "riesgo": alumno.nivel_riesgo or "Sin analizar",
            "precision": int(alumno.precision_prediccion) if alumno.precision_prediccion else 0,
            "factores_riesgo": factores_riesgo,
            "recomendacion": alumno.recomendacion or "Sin recomendación"
        })
    
    # Calcular estadísticas del curso
    total_alumnos = len(alumnos_data)
    riesgo_alto = sum(1 for a in alumnos_data if a['riesgo'] == 'Alto')
    riesgo_medio = sum(1 for a in alumnos_data if a['riesgo'] == 'Medio')
    riesgo_bajo = sum(1 for a in alumnos_data if a['riesgo'] == 'Bajo')
    
    estadisticas = {
        'total': total_alumnos,
        'alto': riesgo_alto,
        'medio': riesgo_medio,
        'bajo': riesgo_bajo
    }
    
    # Renderizar template HTML
    html = render_template('reportes/curso_pdf.html',
                         curso=curso,
                         alumnos=alumnos_data,
                         estadisticas=estadisticas,
                         fecha_generacion=datetime.now(),
                         usuario=current_user.nombre + ' ' + current_user.apellido)
    
    # Generar PDF
    font_config = FontConfiguration()
    pdf = HTML(string=html).write_pdf(font_config=font_config)
    
    # Crear respuesta
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'inline; filename=reporte_curso_{curso.nombre}_{datetime.now().strftime("%Y%m%d")}.pdf'
    
    return response

