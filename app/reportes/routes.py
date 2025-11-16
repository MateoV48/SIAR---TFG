# Archivo: /app/reportes/routes.py
# Rutas para generar reportes en PDF usando WeasyPrint

from flask import Blueprint, render_template, make_response, flash, redirect, url_for
from flask_login import login_required, current_user
from datetime import datetime
import json
from app.models import Alumno, Curso
from app import db
import csv
import io

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
    
    # Verificar permisos: Solo Admin o Docentes pueden ver reportes de cursos
    # Los docentes solo pueden ver sus propios cursos (esto se puede mejorar con una BD de asignaciones)
    if current_user.rol not in ['Admin', 'Docente', 'Preceptor']:
        flash('No tienes permisos para generar reportes de este curso.', 'danger')
        return redirect(url_for('main.dashboard'))
    
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


@reportes.route('/reportes/curso/<int:curso_id>/csv')
@login_required
def curso_csv(curso_id):
    """Exporta un reporte del curso en formato CSV"""
    curso = Curso.query.get_or_404(curso_id)
    
    # Verificar permisos
    if current_user.rol not in ['Admin', 'Docente', 'Preceptor']:
        flash('No tienes permisos para descargar reportes de este curso.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    # Obtener alumnos del curso
    alumnos_query = Alumno.query.filter_by(curso_id=curso_id, activo=True).order_by(Alumno.apellido, Alumno.nombre)
    alumnos_list = alumnos_query.all()
    
    # Crear CSV en memoria
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Encabezados
    writer.writerow([
        'Apellido', 'Nombre', 'DNI', 'Promedio G2', 'Materias Previas',
        'Inasistencias', 'Tiempo Estudio', 'Nivel Riesgo', 'Precisión (%)',
        'Recomendación'
    ])
    
    # Datos de alumnos
    for alumno in alumnos_list:
        writer.writerow([
            alumno.apellido,
            alumno.nombre,
            alumno.dni or 'No especificado',
            alumno.promedio_g2 or 0,
            alumno.materias_previas or 0,
            alumno.inasistencias or 0,
            alumno.tiempo_estudio_semanal or 'No especificado',
            alumno.nivel_riesgo or 'Sin analizar',
            int(alumno.precision_prediccion) if alumno.precision_prediccion else 0,
            (alumno.recomendacion or 'Sin recomendación').replace('\n', ' ')
        ])
    
    # Preparar respuesta
    output.seek(0)
    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'text/csv; charset=utf-8'
    response.headers['Content-Disposition'] = f'attachment; filename=reporte_curso_{curso.nombre}_{datetime.now().strftime("%Y%m%d")}.csv'
    
    return response


@reportes.route('/reportes/alumno/<int:alumno_id>/csv')
@login_required
def alumno_csv(alumno_id):
    """Exporta el reporte de un alumno en formato CSV"""
    alumno = Alumno.query.get_or_404(alumno_id)
    
    # Obtener factores de riesgo
    factores_riesgo = []
    if alumno.factores_riesgo:
        try:
            factores_riesgo = json.loads(alumno.factores_riesgo)
        except:
            factores_riesgo = [alumno.factores_riesgo] if alumno.factores_riesgo else []
    
    # Crear CSV en memoria
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Información del alumno
    curso_nombre = alumno.curso_obj.nombre if alumno.curso_obj else "Sin curso"
    
    writer.writerow(['Reporte Individual de Alumno'])
    writer.writerow(['Fecha de generación', datetime.now().strftime('%d/%m/%Y %H:%M:%S')])
    writer.writerow([])
    writer.writerow(['Datos Personales'])
    writer.writerow(['Apellido', alumno.apellido])
    writer.writerow(['Nombre', alumno.nombre])
    writer.writerow(['DNI', alumno.dni or 'No especificado'])
    writer.writerow(['Curso', curso_nombre])
    writer.writerow([])
    writer.writerow(['Datos Académicos'])
    writer.writerow(['Promedio G2', alumno.promedio_g2 or 0])
    writer.writerow(['Materias Previas', alumno.materias_previas or 0])
    writer.writerow(['Inasistencias', alumno.inasistencias or 0])
    writer.writerow(['Tiempo Estudio Semanal', alumno.tiempo_estudio_semanal or 'No especificado'])
    writer.writerow([])
    writer.writerow(['Análisis de Riesgo'])
    writer.writerow(['Nivel de Riesgo', alumno.nivel_riesgo or 'Sin analizar'])
    writer.writerow(['Precisión de Predicción', f"{int(alumno.precision_prediccion) if alumno.precision_prediccion else 0}%"])
    writer.writerow(['Factores de Riesgo', '; '.join(factores_riesgo) if factores_riesgo else 'Ninguno identificado'])
    writer.writerow([])
    writer.writerow(['Recomendación'])
    writer.writerow([alumno.recomendacion or 'Sin recomendación disponible'])
    
    # Preparar respuesta
    output.seek(0)
    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'text/csv; charset=utf-8'
    response.headers['Content-Disposition'] = f'attachment; filename=reporte_alumno_{alumno.apellido}_{alumno.nombre}_{datetime.now().strftime("%Y%m%d")}.csv'
    
    return response


@reportes.route('/reportes/mis-cursos')
@login_required
def mis_cursos():
    """Dashboard de reportes para docentes - lista sus cursos"""
    if current_user.rol not in ['Admin', 'Docente', 'Preceptor']:
        flash('No tienes permisos para acceder a esta sección.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    # Obtener todos los cursos activos (en el futuro se puede filtrar por asignación docente)
    cursos = Curso.query.filter_by(activo=True).order_by(Curso.nombre).all()
    
    # Preparar datos de cada curso
    cursos_data = []
    for curso in cursos:
        total_alumnos = Alumno.query.filter_by(curso_id=curso.id, activo=True).count()
        alumnos_analizados = Alumno.query.filter_by(curso_id=curso.id, activo=True).filter(
            Alumno.nivel_riesgo.isnot(None)
        ).count()
        
        riesgo_alto = Alumno.query.filter_by(curso_id=curso.id, activo=True, nivel_riesgo='Alto').count()
        riesgo_medio = Alumno.query.filter_by(curso_id=curso.id, activo=True, nivel_riesgo='Medio').count()
        
        cursos_data.append({
            'id': curso.id,
            'nombre': curso.nombre,
            'total_alumnos': total_alumnos,
            'alumnos_analizados': alumnos_analizados,
            'riesgo_alto': riesgo_alto,
            'riesgo_medio': riesgo_medio
        })
    
    return render_template('reportes/mis_cursos.html', cursos=cursos_data, usuario_rol=current_user.rol)

