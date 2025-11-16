from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app.models import Alumno, Curso, Usuario
from app import db
from app.analisis import AnalizadorRiesgo
import json


main = Blueprint('main', __name__)


@main.route('/dashboard')
@login_required
def dashboard():
    """Dashboard principal con listado de alumnos y análisis de riesgo"""
    # Obtener parámetros de filtro
    curso_filtro = request.args.get('curso', '')
    ordenar_por = request.args.get('ordenar', 'apellido')
    
    # Query base
    query = Alumno.query.filter_by(activo=True)
    
    # Aplicar filtro de curso
    curso_seleccionado = None
    if curso_filtro:
        curso_seleccionado = Curso.query.filter_by(nombre=curso_filtro).first()
        if curso_seleccionado:
            query = query.filter_by(curso_id=curso_seleccionado.id)
    
    # Aplicar ordenamiento
    if ordenar_por == 'riesgo':
        # Ordenar por nivel de riesgo: Alto > Medio > Bajo
        from sqlalchemy import case
        orden_riesgo = case(
            (Alumno.nivel_riesgo == 'Alto', 1),
            (Alumno.nivel_riesgo == 'Medio', 2),
            (Alumno.nivel_riesgo == 'Bajo', 3),
            else_=4
        )
        alumnos = query.order_by(orden_riesgo, Alumno.apellido).all()
    elif ordenar_por == 'apellido':
        alumnos = query.order_by(Alumno.apellido, Alumno.nombre).all()
    else:
        alumnos = query.order_by(Alumno.apellido, Alumno.nombre).all()
    
    # Obtener todos los cursos activos
    cursos = Curso.query.filter_by(activo=True).order_by(Curso.nombre).all()
    
    # Preparar datos para el template
    alumnos_data = []
    for alumno in alumnos:
        curso_nombre = alumno.curso_obj.nombre if alumno.curso_obj else "Sin curso"
        alumnos_data.append({
            "id": alumno.id,
            "apellido": alumno.apellido,
            "nombre": alumno.nombre,
            "curso": curso_nombre,
            "riesgo": alumno.nivel_riesgo or "Sin analizar",
            "precision": int(alumno.precision_prediccion) if alumno.precision_prediccion else 0
        })
    
    # Verificar estado del modelo ML para mostrar el botón solo cuando sea útil
    modelo_estado = None
    if current_user.rol == 'Admin':
        analizador = AnalizadorRiesgo()
        alumnos_historicos = Alumno.query.filter(
            Alumno.nivel_riesgo.isnot(None),
            Alumno.nivel_riesgo.in_(['Alto', 'Medio', 'Bajo'])
        ).count()
        
        modelo_estado = {
            'entrenado': analizador.entrenado,
            'muestras_disponibles': alumnos_historicos,
            'puede_entrenar': alumnos_historicos >= 15,
            'puede_mejorar': alumnos_historicos >= 30  # Sugerir reentrenar si hay más datos
        }
    
    return render_template('main/dashboard.html', 
                         alumnos=alumnos_data, 
                         cursos=cursos,
                         curso_filtro=curso_filtro,
                         curso_seleccionado=curso_seleccionado,
                         ordenar_por=ordenar_por,
                         modelo_estado=modelo_estado)


@main.route('/alumno/<int:alumno_id>')
@login_required
def alumno_detalle(alumno_id: int):
    """Vista detallada de un alumno con su análisis de riesgo"""
    alumno = Alumno.query.get_or_404(alumno_id)
    
    # Si no tiene análisis, calcularlo
    if not alumno.nivel_riesgo:
        analizador = AnalizadorRiesgo()
        analizador.analizar_alumno(alumno)
        db.session.refresh(alumno)
    
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
        "curso": curso_nombre,
        "promedio_g2": alumno.promedio_g2 or 0,
        "materias_previas": alumno.materias_previas or 0,
        "inasistencias": alumno.inasistencias or 0,
        "tiempo_estudio": alumno.tiempo_estudio_semanal or "No especificado",
        "factores_riesgo": factores_riesgo,
        "recomendacion": alumno.recomendacion or "Sin recomendación disponible",
        "nivel_riesgo": alumno.nivel_riesgo or "Sin analizar",
        "precision": alumno.precision_prediccion or 0
    }
    
    return render_template('main/alumno_detalle.html', alumno=alumno_data)


@main.route('/usuarios')
@login_required
def usuarios():
    """Gestión de usuarios del sistema"""
    # Solo administradores pueden acceder
    if current_user.rol != 'Admin':
        flash('No tienes permisos para acceder a esta sección.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    usuarios_data = Usuario.query.order_by(Usuario.apellido, Usuario.nombre).all()
    
    return render_template('main/usuarios.html', usuarios=usuarios_data)


@main.route('/analizar-todos', methods=['POST'])
@login_required
def analizar_todos():
    """Endpoint para analizar todos los alumnos"""
    if current_user.rol != 'Admin':
        return jsonify({'error': 'No autorizado'}), 403
    
    analizador = AnalizadorRiesgo()
    resultados = analizador.analizar_todos()
    
    flash(f'Análisis completado. Se analizaron {len(resultados)} alumnos.', 'success')
    return redirect(url_for('main.dashboard'))


@main.route('/entrenar-modelo', methods=['POST'])
@login_required
def entrenar_modelo():
    """Endpoint para entrenar el modelo de Machine Learning"""
    if current_user.rol != 'Admin':
        flash('Solo los administradores pueden entrenar el modelo.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    try:
        analizador = AnalizadorRiesgo()
        resultado = analizador.entrenar_modelo(min_muestras=15)
        
        if resultado['exito']:
            precision = resultado.get('precision', 0)
            flash(
                f"✓ {resultado['mensaje']} "
                f"Precisión del modelo: {precision:.2f}%. "
                f"El modelo ahora está activo y se usará para nuevos análisis.",
                'success'
            )
        else:
            flash(
                f"⚠ {resultado['mensaje']} "
                f"Por favor, analiza más alumnos primero para tener datos históricos suficientes.",
                'warning'
            )
    except Exception as e:
        flash(f'Error al entrenar el modelo: {str(e)}', 'danger')
    
    return redirect(url_for('main.dashboard'))


@main.route('/usuarios/nuevo', methods=['GET', 'POST'])
@login_required
def usuario_nuevo():
    """Crear un nuevo usuario"""
    if current_user.rol != 'Admin':
        flash('No tienes permisos para esta acción.', 'danger')
        return redirect(url_for('main.usuarios'))
    
    if request.method == 'POST':
        try:
            from app import bcrypt
            password_hash = bcrypt.generate_password_hash(request.form.get('password', '')).decode('utf-8')
            
            usuario = Usuario(
                email=request.form.get('email', '').strip(),
                password_hash=password_hash,
                nombre=request.form.get('nombre', '').strip(),
                apellido=request.form.get('apellido', '').strip(),
                rol=request.form.get('rol', 'Docente')
            )
            
            db.session.add(usuario)
            db.session.commit()
            
            flash(f'Usuario {usuario.nombre} {usuario.apellido} creado exitosamente.', 'success')
            return redirect(url_for('main.usuarios'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear el usuario: {str(e)}', 'danger')
    
    roles = ['Admin', 'Docente', 'Preceptor', 'Director']
    return render_template('main/usuario_formulario.html', usuario=None, roles=roles, titulo='Nuevo Usuario')


@main.route('/usuarios/<int:usuario_id>/editar', methods=['GET', 'POST'])
@login_required
def usuario_editar(usuario_id):
    """Editar un usuario existente"""
    if current_user.rol != 'Admin':
        flash('No tienes permisos para esta acción.', 'danger')
        return redirect(url_for('main.usuarios'))
    
    usuario = Usuario.query.get_or_404(usuario_id)
    
    if request.method == 'POST':
        try:
            usuario.email = request.form.get('email', '').strip()
            usuario.nombre = request.form.get('nombre', '').strip()
            usuario.apellido = request.form.get('apellido', '').strip()
            usuario.rol = request.form.get('rol', 'Docente')
            usuario.activo = request.form.get('activo') == 'on'
            
            # Actualizar contraseña si se proporciona una nueva
            nueva_password = request.form.get('password', '').strip()
            if nueva_password:
                from app import bcrypt
                usuario.password_hash = bcrypt.generate_password_hash(nueva_password).decode('utf-8')
            
            db.session.commit()
            
            flash(f'Usuario {usuario.nombre} {usuario.apellido} actualizado exitosamente.', 'success')
            return redirect(url_for('main.usuarios'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar el usuario: {str(e)}', 'danger')
    
    roles = ['Admin', 'Docente', 'Preceptor', 'Director']
    return render_template('main/usuario_formulario.html', usuario=usuario, roles=roles, titulo='Editar Usuario')


@main.route('/usuarios/<int:usuario_id>/eliminar', methods=['POST'])
@login_required
def usuario_eliminar(usuario_id):
    """Eliminar (desactivar) un usuario"""
    if current_user.rol != 'Admin':
        flash('No tienes permisos para esta acción.', 'danger')
        return redirect(url_for('main.usuarios'))
    
    usuario = Usuario.query.get_or_404(usuario_id)
    
    # No permitir eliminar a uno mismo
    if usuario.id == current_user.id:
        flash('No puedes eliminar tu propio usuario.', 'danger')
        return redirect(url_for('main.usuarios'))
    
    try:
        usuario.activo = False
        db.session.commit()
        flash(f'Usuario {usuario.nombre} {usuario.apellido} eliminado exitosamente.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar el usuario: {str(e)}', 'danger')
    
    return redirect(url_for('main.usuarios'))



