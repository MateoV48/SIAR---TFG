# Archivo: /config.py

import os
from dotenv import load_dotenv

# Carga las variables del archivo .env (si existe)
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    """Clase base de configuración."""
    
    # Clave secreta para proteger los formularios y sesiones
    # ¡Debe ser un valor aleatorio y secreto!
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'una-clave-secreta-muy-dificil-de-adivinar'

    # Configuración de la Base de Datos PostgreSQL [cite: 121]
    # Lee la URL desde las variables de entorno, o usa una local por defecto.
    # Formato: postgresql://usuario:contraseña@host:puerto/nombre_db
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'postgresql://postgres:postgres@localhost:5432/tfg_db'
    
    # Desactiva una advertencia de SQLAlchemy
    SQLALCHEMY_TRACK_MODIFICATIONS = False