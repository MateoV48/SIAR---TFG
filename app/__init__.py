# Archivo: /app/__init__.py

from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bcrypt import Bcrypt

# 1. Inicializamos las extensiones (sin vincularlas a una app aún)
db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()
login_manager = LoginManager()

# Configuración de Flask-Login
# Le dice a Flask-Login cuál es la vista (ruta) de login
login_manager.login_view = 'auth.login' 
# Mensaje que muestra si un usuario no logueado intenta entrar a una pág. protegida
login_manager.login_message = 'Por favor, inicie sesión para acceder a esta página.'
login_manager.login_message_category = 'warning' # Categoría para Bootstrap/CSS


def create_app(config_class=Config):
    """
    Patrón Application Factory: Crea y configura la instancia de la app.
    """
    # 2. Creamos la instancia de la aplicación Flask
    app = Flask(__name__)
    
    # 3. Cargamos la configuración desde la clase Config
    app.config.from_object(config_class)
    
    # Solución para problema de encoding en Windows con psycopg2
    # Asegurar que SQLALCHEMY_DATABASE_URI está en formato correcto
    if 'SQLALCHEMY_DATABASE_URI' in app.config:
        db_url = app.config['SQLALCHEMY_DATABASE_URI']
        # Limpiar cualquier problema de encoding
        if isinstance(db_url, bytes):
            try:
                db_url = db_url.decode('utf-8')
            except UnicodeDecodeError:
                db_url = db_url.decode('latin-1', errors='replace')
        # Asegurar que es un string válido
        db_url = str(db_url).strip()
        # Re-encode para limpiar caracteres problemáticos
        try:
            # Convertir a bytes ASCII y de vuelta para limpiar
            db_url_clean = db_url.encode('ascii', errors='ignore').decode('ascii')
            if db_url_clean.startswith('postgresql://'):
                app.config['SQLALCHEMY_DATABASE_URI'] = db_url_clean
        except:
            pass

    # 4. Vinculamos las extensiones con nuestra app
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    # 5. Registramos los "Blueprints" (nuestros módulos de rutas)
    # (Esto dará error ahora, pero lo crearemos en el sig. paso)
    
    from app.auth.routes import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/') 
    
    from app.main.routes import main as main_blueprint
    app.register_blueprint(main_blueprint, url_prefix='/')
    
    from app.alumnos.routes import alumnos as alumnos_blueprint
    app.register_blueprint(alumnos_blueprint, url_prefix='/')
    
    from app.reportes.routes import reportes as reportes_blueprint
    app.register_blueprint(reportes_blueprint, url_prefix='/')

    # 6. --- IMPORTAR MODELOS ---
    # ESTA LÍNEA ES ESENCIAL. Si falta, el error 'Missing user_loader' ocurre.
    from app import models 

    return app