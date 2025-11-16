# Archivo: /config.py

import os
from dotenv import load_dotenv

# Carga las variables del archivo .env (si existe)
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

def _clean_database_url(url_str):
    """
    Limpia y normaliza la URL de conexión a la BD.
    Maneja problemas de encoding de Windows y caracteres especiales.
    """
    if not url_str:
        return 'postgresql://postgres:postgres@localhost:5432/tfg_db'
    
    # Convertir bytes a str si es necesario
    if isinstance(url_str, bytes):
        try:
            url_str = url_str.decode('utf-8')
        except UnicodeDecodeError:
            url_str = url_str.decode('latin-1', errors='replace')
    
    # Asegurar que es un string
    url_str = str(url_str).strip()
    
    # Intenta limpiar caracteres problemáticos
    try:
        # Decodificar bytes sueltos o caracteres malformados
        url_str = url_str.encode('utf-8', errors='replace').decode('utf-8')
    except:
        pass
    
    return url_str

class Config:
    """Clase base de configuración."""
    
    # Clave secreta para proteger los formularios y sesiones
    # ¡Debe ser un valor aleatorio y secreto!
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'una-clave-secreta-muy-dificil-de-adivinar'

    # Configuración de la Base de Datos PostgreSQL
    # Lee la URL desde las variables de entorno, o usa una local por defecto.
    # Formato: postgresql://usuario:contraseña@host:puerto/nombre_db
    # Nota: Si hay problemas de encoding, la función _clean_database_url los maneja automáticamente
    _db_url = os.environ.get('DATABASE_URL')
    if not _db_url:
        # Construir URL manualmente para evitar problemas de encoding
        _db_url = 'postgresql://postgres:postgres@localhost:5432/tfg_db'
    SQLALCHEMY_DATABASE_URI = _clean_database_url(_db_url)
    
    # Desactiva una advertencia de SQLAlchemy
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Modo debug (desactivado por defecto en producción)
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'


class ProductionConfig(Config):
    """Configuración específica para producción."""
    DEBUG = False
    # En producción, siempre usa la URL de la variable de entorno
    # Si no está configurada, SQLAlchemy dará un error claro al intentar conectar
    # Nota: Asegúrate de configurar DATABASE_URL y SECRET_KEY como variables de entorno
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')


class DevelopmentConfig(Config):
    """Configuración específica para desarrollo."""
    DEBUG = True