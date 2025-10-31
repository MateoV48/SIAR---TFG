from flask import Blueprint, render_template, request, redirect, url_for


auth = Blueprint('auth', __name__)


@auth.route('/')
def index():
    return redirect(url_for('auth.login'))


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Aquí luego se validarán credenciales reales.
        # Por ahora, simplemente recargamos la página (UI lista).
        pass
    return render_template('auth/login.html')


