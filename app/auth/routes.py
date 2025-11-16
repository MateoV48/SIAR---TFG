from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from app import bcrypt
from app.models import Usuario


auth = Blueprint('auth', __name__)


@auth.route('/')
def index():
    return redirect(url_for('auth.login'))


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        
        if not email or not password:
            flash('Por favor, completa todos los campos.', 'warning')
            return render_template('auth/login.html')
        
        # Buscar usuario en la base de datos
        usuario = Usuario.query.filter_by(email=email).first()
        
        # Si no hay usuarios en la BD, crear uno admin por defecto
        if usuario is None and Usuario.query.count() == 0:
            # Crear usuario admin por defecto solo la primera vez
            from app import db
            password_hash = bcrypt.generate_password_hash('admin123').decode('utf-8')
            usuario = Usuario(
                email='admin@colegio.edu.ar',
                password_hash=password_hash,
                nombre='Administrador',
                apellido='Sistema',
                rol='Admin'
            )
            db.session.add(usuario)
            db.session.commit()
            flash('Usuario administrador creado automáticamente. Usa: admin@colegio.edu.ar / admin123', 'info')
            # Ahora buscar el usuario recién creado
            usuario = Usuario.query.filter_by(email='admin@colegio.edu.ar').first()
        
        # Validar usuario y contraseña
        if usuario and bcrypt.check_password_hash(usuario.password_hash, password):
            login_user(usuario, remember=True)
            flash(f'¡Bienvenido, {usuario.nombre} {usuario.apellido}!', 'success')
            return redirect(url_for('main.dashboard'))
        else:
            flash('Credenciales incorrectas. Si es la primera vez, usa: admin@colegio.edu.ar / admin123', 'danger')
    
    return render_template('auth/login.html')


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Has cerrado sesión correctamente.', 'info')
    return redirect(url_for('auth.login'))



