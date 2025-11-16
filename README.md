# SIAR - TFG

**Sistema Inteligente de Análisis de Riesgo Académico**

Aplicación web para gestión y análisis de riesgo académico de alumnos, desarrollada en Flask con integración de Machine Learning y generación de reportes en PDF.

## ¿Cómo ejecutar el proyecto?

1. **Clona el repositorio:**
   ```pwsh
   git clone https://github.com/MateoV48/SIAR-TFG.git
   cd SIAR-TFG
   ```

2. **Crea y activa el entorno virtual:**
   ```pwsh
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

3. **Instala las dependencias:**
   ```pwsh
   pip install -r requirements.txt
   ```

4. **Configura la base de datos (PostgreSQL):**
   - Por defecto, el proyecto usa:  
     `postgresql://postgres:postgres@localhost:5432/tfg_db`
   - Puedes cambiar la URL en el archivo `.env` o en `config.py`.

5. **Aplica las migraciones:**
   ```pwsh
   $env:FLASK_APP='run.py'
   flask db upgrade
   ```

6. **Ejecuta la aplicación:**
   ```pwsh
   python run.py
   ```
   Accede a la web en [http://localhost:5000](http://localhost:5000)

7. **Primer login:**  
   El primer usuario admin se crea automáticamente:  
   - Usuario: `admin@colegio.edu.ar`  
   - Contraseña: `admin123`

## Estructura del proyecto

- `app/` — Código principal (rutas, modelos, lógica ML)
- `requirements.txt` — Dependencias
- `.gitignore` — Archivos ignorados por Git
- `README.md` — Instructivo
- `migrations/` — Migraciones de base de datos
- `templates/` — Plantillas HTML

