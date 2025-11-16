# Archivo: /app/models.py
# Modelos de base de datos para la aplicación

from app import db
from flask_login import UserMixin
from datetime import datetime


class Usuario(UserMixin, db.Model):
    """Modelo de usuario para autenticación"""
    __tablename__ = 'usuarios'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    nombre = db.Column(db.String(80), nullable=False)
    apellido = db.Column(db.String(80), nullable=False)
    rol = db.Column(db.String(50), nullable=False, default='Docente')  # Admin, Docente, Preceptor, etc.
    activo = db.Column(db.Boolean, default=True, nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Usuario {self.email}>'


class Curso(db.Model):
    """Modelo de curso/grado"""
    __tablename__ = 'cursos'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False, unique=True)  # Ej: "5to A", "4to B"
    nivel = db.Column(db.String(20), nullable=False)  # Ej: "5to", "4to"
    division = db.Column(db.String(10), nullable=False)  # Ej: "A", "B", "C"
    activo = db.Column(db.Boolean, default=True, nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relaciones
    alumnos = db.relationship('Alumno', backref='curso_obj', lazy=True)
    
    def __repr__(self):
        return f'<Curso {self.nombre}>'


class Alumno(db.Model):
    """Modelo de alumno con datos académicos"""
    __tablename__ = 'alumnos'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(80), nullable=False)
    apellido = db.Column(db.String(80), nullable=False)
    dni = db.Column(db.String(20), unique=True, nullable=True)
    curso_id = db.Column(db.Integer, db.ForeignKey('cursos.id'), nullable=False)
    
    # Datos académicos para análisis de riesgo
    promedio_g2 = db.Column(db.Float, nullable=True)  # Promedio período anterior (G2)
    materias_previas = db.Column(db.Integer, default=0, nullable=False)  # Número de materias reprobadas
    inasistencias = db.Column(db.Integer, default=0, nullable=False)  # Total de inasistencias
    tiempo_estudio_semanal = db.Column(db.String(50), nullable=True)  # Ej: "< 2 horas", "2-5 horas"
    
    # Resultados del análisis de riesgo
    nivel_riesgo = db.Column(db.String(20), nullable=True)  # Alto, Medio, Bajo
    precision_prediccion = db.Column(db.Float, nullable=True)  # Precisión del modelo (0-100)
    factores_riesgo = db.Column(db.Text, nullable=True)  # JSON o texto con factores identificados
    recomendacion = db.Column(db.Text, nullable=True)  # Recomendación basada en el análisis
    
    # Metadatos
    activo = db.Column(db.Boolean, default=True, nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_actualizacion = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    asistencias = db.relationship('Asistencia', backref='alumno', lazy=True, cascade='all, delete-orphan')
    registros_academicos = db.relationship('RegistroAcademico', backref='alumno', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Alumno {self.apellido}, {self.nombre}>'
    
    @property
    def nombre_completo(self):
        return f"{self.apellido}, {self.nombre}"


class Asistencia(db.Model):
    """Registro de asistencias de alumnos"""
    __tablename__ = 'asistencias'
    
    id = db.Column(db.Integer, primary_key=True)
    alumno_id = db.Column(db.Integer, db.ForeignKey('alumnos.id'), nullable=False)
    fecha = db.Column(db.Date, nullable=False)
    presente = db.Column(db.Boolean, default=True, nullable=False)  # True = presente, False = ausente
    justificada = db.Column(db.Boolean, default=False, nullable=False)
    observaciones = db.Column(db.Text, nullable=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Asistencia {self.alumno_id} - {self.fecha}>'


class RegistroAcademico(db.Model):
    """Registro académico detallado del alumno"""
    __tablename__ = 'registros_academicos'
    
    id = db.Column(db.Integer, primary_key=True)
    alumno_id = db.Column(db.Integer, db.ForeignKey('alumnos.id'), nullable=False)
    periodo = db.Column(db.String(50), nullable=False)  # Ej: "G1 2024", "G2 2024"
    promedio = db.Column(db.Float, nullable=True)
    materias_aprobadas = db.Column(db.Integer, default=0, nullable=False)
    materias_desaprobadas = db.Column(db.Integer, default=0, nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<RegistroAcademico {self.alumno_id} - {self.periodo}>'


# Esta función es requerida por Flask-Login para cargar usuarios
from app import login_manager

@login_manager.user_loader
def load_user(user_id):
    """Carga un usuario desde la base de datos usando su ID"""
    return Usuario.query.get(int(user_id))

