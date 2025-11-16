# Guía de Configuración y Ejecución del Proyecto

## 📋 Resumen del Proyecto

Este es un proyecto Flask para un sistema de asistencia y análisis de riesgo académico (TFG). La aplicación utiliza:
- **Flask** como framework web
- **PostgreSQL** como base de datos
- **Flask-Login** para autenticación
- **Flask-Migrate** para migraciones de base de datos
- **Pandas y Scikit-learn** para análisis de datos
- **WeasyPrint** para generación de reportes PDF

## ✅ Estado Actual del Proyecto

**El proyecto está parcialmente funcional** pero necesita configuración antes de ejecutarse.

### Problemas Corregidos:
- ✅ Blueprint de `main` ahora está registrado
- ✅ Archivo `models.py` creado (estaba vacío)

### Configuración Necesaria:
- ⚠️ Base de datos PostgreSQL debe estar instalada y configurada
- ⚠️ Archivo `.env` debe ser creado con las variables de entorno
- ⚠️ Migraciones de base de datos deben ejecutarse

---

## 🔧 Requisitos Previos

### 1. Software Necesario

#### Python 3.11+
- Verifica que tienes Python instalado:
  ```bash
  python --version
  ```
- Si no lo tienes, descárgalo desde [python.org](https://www.python.org/downloads/)

#### PostgreSQL
- **Descarga e instala PostgreSQL** desde [postgresql.org](https://www.postgresql.org/download/windows/)
- Durante la instalación, recuerda la contraseña que configures para el usuario `postgres`
- Por defecto, PostgreSQL se ejecuta en el puerto `5432`

#### Git (opcional)
- Para control de versiones

---

## 📦 Instalación y Configuración

### Paso 1: Activar el Entorno Virtual

El proyecto ya tiene un entorno virtual creado (`venv`). Actívalo:

**En PowerShell:**
```powershell
.\venv\Scripts\Activate.ps1
```

**Si PowerShell muestra un error de política de ejecución**, ejecuta primero:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**En CMD:**
```cmd
venv\Scripts\activate.bat
```

Si ves `(venv)` al inicio de tu línea de comandos, el entorno está activado.

**⚠️ Alternativa si la activación no funciona:**
Puedes usar el Python del entorno virtual directamente sin activarlo:
```powershell
# En lugar de "flask" usa:
.\venv\Scripts\python.exe -m flask [comando]

# Ejemplo:
.\venv\Scripts\python.exe -m flask --version
.\venv\Scripts\python.exe -m flask db upgrade
.\venv\Scripts\python.exe -m flask run
```

### Paso 2: Instalar Dependencias

Las dependencias ya están instaladas en el `venv`, pero si necesitas reinstalarlas:

```bash
pip install -r requirements.txt
```

### Paso 3: Configurar PostgreSQL

1. **Abre pgAdmin** (interfaz gráfica de PostgreSQL) o usa la línea de comandos

2. **Crea la base de datos:**
   - Abre pgAdmin
   - Conecta al servidor PostgreSQL (usuario: `postgres`)
   - Click derecho en "Databases" → "Create" → "Database"
   - Nombre: `tfg_db`
   - Click en "Save"

   **O usando línea de comandos:**
   ```sql
   CREATE DATABASE tfg_db;
   ```

3. **Verifica la conexión:**
   - Usuario: `postgres` (o el que hayas configurado)
   - Contraseña: (la que configuraste durante la instalación)
   - Host: `localhost`
   - Puerto: `5432`
   - Base de datos: `tfg_db`

### Paso 4: Crear Archivo `.env`

Crea un archivo llamado `.env` en la raíz del proyecto (al mismo nivel que `run.py`) con el siguiente contenido:

```env
# Clave secreta para Flask (cámbiala por una clave segura)
SECRET_KEY=tu-clave-secreta-muy-dificil-de-adivinar-cambiala-por-algo-seguro

# URL de conexión a PostgreSQL
# Formato: postgresql://usuario:contraseña@host:puerto/nombre_db
DATABASE_URL=postgresql://postgres:TU_CONTRASEÑA@localhost:5432/tfg_db
```

**⚠️ IMPORTANTE:**
- Reemplaza `TU_CONTRASEÑA` con la contraseña real de PostgreSQL
- Si usas un usuario diferente a `postgres`, cámbialo también
- Si PostgreSQL está en otro host o puerto, ajusta la URL

### Paso 5: Inicializar la Base de Datos

Ejecuta las migraciones para crear las tablas en la base de datos:

**Si el entorno virtual está activado:**
```bash
# Inicializar el sistema de migraciones (solo la primera vez)
flask db init

# Crear la primera migración
flask db migrate -m "Initial migration"

# Aplicar las migraciones a la base de datos
flask db upgrade
```

**Si el entorno virtual NO está activado (usa Python del venv directamente):**
```powershell
# Inicializar el sistema de migraciones (solo la primera vez)
.\venv\Scripts\python.exe -m flask db init

# Crear la primera migración
.\venv\Scripts\python.exe -m flask db migrate -m "Initial migration"

# Aplicar las migraciones a la base de datos
.\venv\Scripts\python.exe -m flask db upgrade
```

**Nota:** Si ya tienes migraciones en `migrations/versions/`, puedes saltar `flask db init` y solo ejecutar `flask db upgrade`.

---

## 🚀 Ejecutar la Aplicación

### Opción 1: Usando `run.py` (Recomendado)

**Si el entorno virtual está activado:**
```bash
python run.py
```

**Si el entorno virtual NO está activado:**
```powershell
.\venv\Scripts\python.exe run.py
```

### Opción 2: Usando Flask CLI

**Si el entorno virtual está activado:**
```bash
flask run
```

O con modo debug y recarga automática:

```bash
flask run --debug
```

**Si el entorno virtual NO está activado:**
```powershell
.\venv\Scripts\python.exe -m flask run
```

O con modo debug:

```powershell
.\venv\Scripts\python.exe -m flask run --debug
```

### Acceder a la Aplicación

Una vez que el servidor esté corriendo, verás algo como:

```
 * Running on http://127.0.0.1:5000
```

Abre tu navegador y ve a:
- **http://localhost:5000** o
- **http://127.0.0.1:5000**

---

## 📁 Estructura del Proyecto

```
AsistenciaParaTFG/
├── app/                    # Aplicación principal
│   ├── __init__.py        # Factory de la aplicación
│   ├── models.py          # Modelos de base de datos
│   ├── auth/              # Módulo de autenticación
│   │   └── routes.py      # Rutas de login/logout
│   ├── main/              # Módulo principal
│   │   └── routes.py      # Rutas del dashboard, alumnos, etc.
│   └── templates/         # Plantillas HTML
│       ├── auth/
│       └── main/
├── migrations/            # Migraciones de base de datos (Alembic)
├── venv/                  # Entorno virtual de Python
├── config.py             # Configuración de la aplicación
├── run.py                # Punto de entrada para ejecutar
├── requirements.txt       # Dependencias del proyecto
└── .env                  # Variables de entorno (crear tú)
```

---

## 🐛 Solución de Problemas

### Error: "No module named 'flask'"
**Solución:** Activa el entorno virtual primero:
```bash
.\venv\Scripts\Activate.ps1
```

### Error: "Connection refused" o "could not connect to server"
**Solución:** 
- Verifica que PostgreSQL esté ejecutándose
- Revisa que la URL en `.env` sea correcta
- Verifica usuario y contraseña

### Error: "database 'tfg_db' does not exist"
**Solución:** Crea la base de datos en PostgreSQL (ver Paso 3)

### Error: "Missing user_loader"
**Solución:** Ya está corregido. El archivo `models.py` ahora tiene el `user_loader`.

### Error: "Blueprint 'main' is not registered"
**Solución:** Ya está corregido. El blueprint de `main` ahora está registrado.

### Las rutas `/dashboard` o `/usuarios` no funcionan
**Solución:** Verifica que el blueprint de `main` esté registrado en `app/__init__.py` (ya está corregido).

---

## 📝 Próximos Pasos

1. **Implementar autenticación real:**
   - Crear modelo `Usuario` en `models.py`
   - Implementar validación de credenciales en `app/auth/routes.py`
   - Conectar con la base de datos

2. **Crear modelos de datos:**
   - Modelo `Alumno`
   - Modelo `Curso`
   - Modelo `Asistencia`
   - Etc.

3. **Implementar funcionalidades:**
   - Carga de datos de alumnos
   - Análisis de riesgo con scikit-learn
   - Generación de reportes PDF con WeasyPrint

---

## 🆘 Comandos Útiles

**Con entorno virtual activado:**
```bash
# Activar entorno virtual
.\venv\Scripts\Activate.ps1

# Instalar dependencias
pip install -r requirements.txt

# Crear migración
flask db migrate -m "Descripción del cambio"

# Aplicar migraciones
flask db upgrade

# Revertir última migración
flask db downgrade

# Ejecutar aplicación
python run.py
```

**Sin activar entorno virtual (usando Python del venv directamente):**
```powershell
# Instalar dependencias
.\venv\Scripts\python.exe -m pip install -r requirements.txt

# Crear migración
.\venv\Scripts\python.exe -m flask db migrate -m "Descripción del cambio"

# Aplicar migraciones
.\venv\Scripts\python.exe -m flask db upgrade

# Revertir última migración
.\venv\Scripts\python.exe -m flask db downgrade

# Ejecutar aplicación
.\venv\Scripts\python.exe run.py
```

---

## ✅ Checklist de Configuración

- [ ] PostgreSQL instalado y ejecutándose
- [ ] Base de datos `tfg_db` creada
- [ ] Archivo `.env` creado con `SECRET_KEY` y `DATABASE_URL`
- [ ] Entorno virtual activado
- [ ] Dependencias instaladas (`pip install -r requirements.txt`)
- [ ] Migraciones ejecutadas (`flask db upgrade`)
- [ ] Aplicación ejecutándose (`python run.py`)
- [ ] Navegador accede a http://localhost:5000

---

**¿Problemas?** Revisa la sección "Solución de Problemas" o verifica los logs de error en la consola.

