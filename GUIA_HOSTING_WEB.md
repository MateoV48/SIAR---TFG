# 🌐 Guía de Hosting Web - Sistema de Asistencia TFG

Esta guía te mostrará cómo hostear tu aplicación Flask en internet de forma gratuita o con planes económicos.

---

## 📋 Índice

1. [Requisitos Previos](#requisitos-previos)
2. [Opción 1: Render.com (Recomendado - Gratis)](#opción-1-rendercom-recomendado---gratis)
3. [Opción 2: Railway.app (Muy Fácil)](#opción-2-railwayapp-muy-fácil)
4. [Opción 3: Fly.io (Gratis con Contenedores)](#opción-3-flyio-gratis-con-contenedores)
5. [Opción 4: PythonAnywhere (Especializado en Python)](#opción-4-pythonanywhere-especializado-en-python)
6. [Opción 5: DigitalOcean App Platform](#opción-5-digitalocean-app-platform)
7. [Configuración de Producción](#configuración-de-producción)
8. [Solución de Problemas](#solución-de-problemas)

---

## ⚙️ Requisitos Previos

Antes de hostear tu aplicación, asegúrate de tener:

1. ✅ Tu código en un repositorio Git (GitHub, GitLab, o Bitbucket)
2. ✅ Tu aplicación funcionando localmente
3. ✅ Las migraciones de base de datos listas
4. ✅ Un archivo `.env` con las variables de entorno (no lo subas a Git)

---

## 🚀 Opción 1: Render.com (Recomendado - Gratis)

**Render.com** es una excelente opción gratuita con PostgreSQL incluido.

### Ventajas:
- ✅ Plan gratuito disponible (con limitaciones)
- ✅ Base de datos PostgreSQL gratuita incluida
- ✅ SSL/HTTPS automático
- ✅ Despliegue automático desde GitHub
- ✅ Muy fácil de configurar

### Desventajas:
- ⚠️ El servicio gratuito se "duerme" después de 15 minutos de inactividad
- ⚠️ Puede tardar 30-50 segundos en "despertar"

### Pasos para Desplegar:

#### 1. Preparar el Proyecto

Ya tienes los archivos necesarios. Solo necesitas asegurarte de tener:

- ✅ `requirements.txt` (ya lo tienes)
- ✅ `Procfile` o `render.yaml` (los crearemos)
- ✅ Variables de entorno configuradas

#### 2. Subir a GitHub

Si no tienes tu código en GitHub:

```bash
# Inicializar git (si no está inicializado)
git init

# Agregar todos los archivos
git add .

# Hacer commit
git commit -m "Preparado para deployment"

# Crear repositorio en GitHub y luego:
git remote add origin https://github.com/TU_USUARIO/TU_REPO.git
git branch -M main
git push -u origin main
```

**⚠️ IMPORTANTE**: Asegúrate de agregar `.env` al `.gitignore` para no subir tus secretos.

#### 3. Crear Servicio Web en Render

1. Ve a [render.com](https://render.com) y crea una cuenta (puedes usar GitHub)

2. Click en **"New +"** → **"Web Service"**

3. Conecta tu repositorio de GitHub

4. Configura el servicio:
   - **Name**: `asistencia-tfg` (o el nombre que prefieras)
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt && python -m flask db upgrade`
   - **Start Command**: `gunicorn "run:app"` (o usa el Procfile)
   - **Instance Type**: `Free`

5. Agregar variables de entorno:
   - Click en **"Environment"**
   - Agrega:
     ```
     SECRET_KEY=tu-clave-secreta-muy-larga-y-aleatoria
     FLASK_APP=run.py
     PYTHON_VERSION=3.11.0
     ```

#### 4. Crear Base de Datos PostgreSQL

1. En Render, click **"New +"** → **"PostgreSQL"**

2. Configura:
   - **Name**: `asistencia-tfg-db`
   - **Database**: `tfg_db`
   - **User**: Se crea automáticamente
   - **Region**: Elige el más cercano
   - **Plan**: `Free`

3. Una vez creada, copia la **"Internal Database URL"**

4. En tu servicio web, agrega la variable de entorno:
   ```
   DATABASE_URL=[pega la URL interna aquí]
   ```

#### 5. Ejecutar Migraciones

Render ejecutará las migraciones automáticamente si configuraste el Build Command correctamente.

Si necesitas ejecutarlas manualmente, puedes usar el **"Shell"** de Render o agregar en el Build Command:
```bash
pip install -r requirements.txt && flask db upgrade
```

#### 6. Desplegar

Click en **"Manual Deploy"** → **"Deploy latest commit"**

Tu aplicación estará disponible en: `https://asistencia-tfg.onrender.com`

---

## 🚂 Opción 2: Railway.app (Muy Fácil)

**Railway** es muy fácil de usar y tiene un plan gratuito generoso.

### Ventajas:
- ✅ Muy fácil de configurar
- ✅ PostgreSQL incluido
- ✅ $5 de crédito gratis mensual
- ✅ Sin necesidad de archivos de configuración complejos

### Pasos:

1. Ve a [railway.app](https://railway.app) y crea cuenta con GitHub

2. Click **"New Project"** → **"Deploy from GitHub repo"**

3. Selecciona tu repositorio

4. Railway detectará automáticamente que es una app Python

5. Agrega una base de datos PostgreSQL:
   - Click **"+ New"** → **"Database"** → **"Add PostgreSQL"**

6. Agrega variables de entorno en la pestaña **"Variables"**:
   ```
   SECRET_KEY=tu-clave-secreta-muy-larga-y-aleatoria
   DATABASE_URL=${{Postgres.DATABASE_URL}}
   FLASK_APP=run.py
   ```

7. Railway automáticamente:
   - Instalará dependencias
   - Ejecutará las migraciones (si configuras un script)
   - Desplegará la app

8. Tu app estará en: `https://TU-PROYECTO.up.railway.app`

---

## ✈️ Opción 3: Fly.io (Gratis con Contenedores)

**Fly.io** es excelente si quieres usar Docker y tener más control.

### Ventajas:
- ✅ Plan gratuito generoso
- ✅ Usa Docker (más control)
- ✅ Muy rápido

### Pasos:

1. Instala Fly CLI:
   ```bash
   # Windows (PowerShell)
   powershell -Command "iwr https://fly.io/install.ps1 -useb | iex"
   ```

2. Login:
   ```bash
   fly auth login
   ```

3. En la raíz de tu proyecto, ejecuta:
   ```bash
   fly launch
   ```
   
   Esto creará automáticamente:
   - `Dockerfile`
   - `fly.toml` (configuración)

4. Agrega base de datos PostgreSQL:
   ```bash
   fly postgres create --name asistencia-tfg-db
   fly postgres attach asistencia-tfg-db
   ```

5. Agrega variables de entorno:
   ```bash
   fly secrets set SECRET_KEY="tu-clave-secreta-muy-larga"
   ```

6. Despliega:
   ```bash
   fly deploy
   ```

---

## 🐍 Opción 4: PythonAnywhere (Especializado en Python)

**PythonAnywhere** está especializado en aplicaciones Python.

### Ventajas:
- ✅ Muy fácil para Python
- ✅ Plan gratuito disponible
- ✅ Interfaz web completa

### Desventajas:
- ⚠️ Requiere configuración manual más detallada
- ⚠️ El plan gratis tiene limitaciones

### Pasos:

1. Ve a [pythonanywhere.com](https://www.pythonanywhere.com) y crea cuenta

2. En el **Dashboard**, ve a **"Web"** tab

3. Click **"Add a new web app"**

4. Elige **Flask** y la versión de Python

5. Sube tu código (puedes usar Git o subir archivos)

6. Configura el **WSGI file** para apuntar a tu aplicación

7. Configura variables de entorno en el archivo WSGI

8. Crea una base de datos PostgreSQL (o usa MySQL que viene incluido)

---

## 💧 Opción 5: DigitalOcean App Platform

**DigitalOcean App Platform** es una buena opción de pago.

### Ventajas:
- ✅ Muy confiable
- ✅ Buen soporte
- ✅ Escalable

### Desventajas:
- ⚠️ Plan más costoso (desde $5/mes)
- ⚠️ No tiene plan completamente gratis

### Pasos:

1. Ve a [digitalocean.com](https://www.digitalocean.com)

2. Crea cuenta y ve a **App Platform**

3. **"Create App"** → Conecta GitHub

4. Configura:
   - Framework: Flask
   - Build command: `pip install -r requirements.txt`
   - Run command: `gunicorn run:app`

5. Agrega base de datos PostgreSQL

6. Configura variables de entorno

7. Despliega

---

## 🔧 Configuración de Producción

Para que tu aplicación funcione correctamente en producción, necesitas hacer algunos ajustes:

### 1. Actualizar `config.py`

El archivo `config.py` debe tener configuraciones para producción. Ya está preparado, pero puedes mejorarlo agregando:

```python
import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    """Clase base de configuración."""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'una-clave-secreta-muy-dificil-de-adivinar'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'postgresql://postgres:postgres@localhost:5432/tfg_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Para producción, desactiva debug
    DEBUG = os.environ.get('FLASK_DEBUG', 'False') == 'True'

class ProductionConfig(Config):
    """Configuración para producción."""
    DEBUG = False
    # En producción, siempre usa la URL de la variable de entorno
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    
    if not SQLALCHEMY_DATABASE_URI:
        raise ValueError("DATABASE_URL debe estar configurada en producción")
```

### 2. Usar Gunicorn en Producción

El servidor de desarrollo de Flask NO es seguro para producción. Usa **Gunicorn**:

**Agregar a `requirements.txt`:**
```
gunicorn
```

**Crear `Procfile` (para Render/Railway):**
```
web: gunicorn "run:app" --bind 0.0.0.0:$PORT
```

O para Render específicamente, en el Start Command:
```
gunicorn "run:app"
```

### 3. Variables de Entorno Importantes

En producción, configura estas variables:

```env
SECRET_KEY=una-clave-super-secreta-y-larga-minimo-32-caracteres
DATABASE_URL=postgresql://usuario:contraseña@host:puerto/db
FLASK_APP=run.py
FLASK_ENV=production
FLASK_DEBUG=False
```

### 4. Crear `.gitignore`

Asegúrate de que tu `.gitignore` incluya:

```
.env
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
venv/
env/
*.db
*.sqlite3
```

---

## 🐛 Solución de Problemas

### Error: "Application failed to respond"

**Solución**: Verifica que el comando de inicio sea correcto:
- Render: `gunicorn "run:app"`
- Railway: Se detecta automáticamente
- Fly.io: Configurado en `fly.toml`

### Error: "Database connection failed"

**Solución**: 
1. Verifica que `DATABASE_URL` esté configurada correctamente
2. Asegúrate de usar la URL interna (no externa) si Render/Railway la proporciona
3. Verifica que la base de datos esté creada y corriendo

### Error: "Module not found"

**Solución**:
1. Verifica que todas las dependencias estén en `requirements.txt`
2. Asegúrate de que el Build Command instale las dependencias
3. Revisa los logs de build para ver qué falta

### Error: "500 Internal Server Error"

**Solución**:
1. Revisa los logs de la aplicación en el dashboard
2. Verifica que las migraciones se hayan ejecutado
3. Revisa que todas las variables de entorno estén configuradas

### La aplicación se "duerme" (Render gratuito)

**Solución**:
- Es normal en el plan gratuito de Render
- La primera petición después de 15 min puede tardar 30-50 segundos
- Considera usar Railway o Fly.io para evitar esto
- O actualiza a un plan de pago

---

## 📊 Comparación de Opciones

| Plataforma | Gratis | PostgreSQL | Facilidad | Velocidad |
|------------|--------|------------|-----------|-----------|
| **Render.com** | ✅ Sí* | ✅ Incluido | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Railway.app** | ✅ $5/mes crédito | ✅ Incluido | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Fly.io** | ✅ Sí | ✅ Incluido | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **PythonAnywhere** | ✅ Sí* | ⚠️ Manual | ⭐⭐⭐ | ⭐⭐⭐ |
| **DigitalOcean** | ❌ No | ✅ Incluido | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |

*Con limitaciones

---

## 🎯 Recomendación

**Para empezar rápidamente**: Usa **Railway.app** o **Render.com**

**Para máxima facilidad**: **Railway.app**

**Para aprender Docker**: **Fly.io**

**Para producción seria**: **DigitalOcean** o **Railway** con plan de pago

---

## 📝 Checklist Pre-Deployment

- [ ] Código subido a GitHub/GitLab
- [ ] `.env` agregado a `.gitignore`
- [ ] `requirements.txt` actualizado con `gunicorn`
- [ ] `Procfile` creado (si usas Render/Railway)
- [ ] Variables de entorno configuradas en la plataforma
- [ ] Base de datos PostgreSQL creada
- [ ] Migraciones ejecutadas
- [ ] `SECRET_KEY` generada y configurada
- [ ] Aplicación probada localmente

---

## 🔒 Seguridad en Producción

1. **Nunca** subas `.env` a Git
2. Usa `SECRET_KEY` fuerte (mínimo 32 caracteres aleatorios)
3. Usa HTTPS (las plataformas lo proporcionan automáticamente)
4. Configura `DEBUG=False` en producción
5. Usa variables de entorno para secretos

---

¿Necesitas ayuda con alguna plataforma específica? ¡Avísame y te ayudo a configurarla paso a paso!


