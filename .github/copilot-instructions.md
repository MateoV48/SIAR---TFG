## Purpose

This file gives concise, project-specific guidance for AI coding agents working on this repository.

**Big Picture**:
- **App type**: A Flask web app following the Application Factory pattern (`app.create_app` in `app/__init__.py`).
- **Major components**: Blueprints under `app/` — `auth`, `main`, `alumnos`, `reportes`; models in `app/models.py`; ML logic in `app/analisis.py`.
- **Data flow**: HTTP requests → blueprint route (e.g. `app/main/routes.py`) → ORM (`SQLAlchemy` models) → optional ML with `AnalizadorRiesgo` → templates or PDF generation (`WeasyPrint`).

**How to run locally (Windows PowerShell)**:
- Create a venv and install dependencies:
  ```pwsh
  python -m venv .venv
  .\.venv\Scripts\Activate.ps1
  pip install -r requirements.txt
  ```
- Recommended quick run (uses defaults from `config.py` which point to a local Postgres):
  ```pwsh
  $env:FLASK_DEBUG='True'
  # If you have a local Postgres, optionally set DATABASE_URL
  # $env:DATABASE_URL='postgresql://postgres:postgres@localhost:5432/tfg_db'
  python run.py
  ```
- For `flask` CLI (migrations):
  ```pwsh
  $env:FLASK_APP='run.py'
  $env:FLASK_ENV='development'
  flask db upgrade        # apply existing migrations
  flask db migrate -m 'msg'
  flask db upgrade
  ```

**Project-specific conventions & important notes**:
- `create_app(config_class=Config)` in `app/__init__.py` is the entry point — read this file first to understand extension initialization and blueprint registration.
- The code intentionally imports `from app import models` at the end of `create_app` — this prevents circular imports and is essential for Flask-Login's `user_loader` to work.
- Blueprints are registered with `url_prefix='/'`; route names are referenced as e.g. `main.dashboard`, `auth.login`.
- Templates live under `app/templates/` matching blueprints (see `templates/main/*`, `templates/alumnos/*`, `templates/auth/*`). Use these patterns when adding views.
- The app uses `Flask-Migrate` + `SQLAlchemy`. Database URL default is defined in `config.py` and falls back to `postgresql://postgres:postgres@localhost:5432/tfg_db`.
- Admin user: first successful login attempt creates a default admin user (`admin@colegio.edu.ar / admin123`) if the `usuarios` table is empty — see `app/auth/routes.py`.

**ML and models**:
- ML logic is encapsulated in `app/analisis.py` via `AnalizadorRiesgo`:
  - Model persistence: saved under `models/` as `modelo_riesgo.pkl` and `label_encoder.pkl` (relative to project root).
  - Training requirement: the method `entrenar_modelo(min_muestras=15)` requires at least 15 labeled historical samples. The UI enforces this check; expect training to fail if there are fewer.
  - Fallback behavior: when no trained model is available, `analizar_alumno` will use `calcular_riesgo_simple` (deterministic rule-based fallback).
- When adding features to the ML pipeline, update both `preparar_datos` and the saving/loading logic (joblib) in `analisis.py`.

**Integration points & external dependencies to be aware of**:
- Database: PostgreSQL (config via `DATABASE_URL` env var). Migrations folder exists (`migrations/`).
- PDF reports: `WeasyPrint` is used in `app/reportes/routes.py` and requires system deps (GTK / CSS fonts) on Windows. Routes will gracefully flash an error if WeasyPrint is missing — test locally before enabling PDF CI.
- ML libs: `scikit-learn`, `pandas`, `joblib` — heavy CPU and binary deps; prefer running training in a prepared environment.

**Common developer tasks & examples (explicit)**:
- Create DB + apply migrations (PowerShell):
  ```pwsh
  $env:FLASK_APP='run.py'
  flask db upgrade
  ```
- Create a user via web UI: visit `/login` — on first login the default admin is auto-created if no users exist.
- Retrain model from UI: log in as `Admin` → Dashboard → press train (POST `/entrenar-modelo`). Programmatic equivalent: call `AnalizadorRiesgo().entrenar_modelo()`.
- Analyze all students: Admin POST `/analizar-todos` (calls `AnalizadorRiesgo().analizar_todos()`).

**Developer pitfalls discovered in the codebase**:
- Circular import risk: importing models too early breaks Flask-Login. Do not move `from app import models` higher in `create_app`.
- WeasyPrint errors are platform-specific; tests or CI that generate PDFs must install system libraries (not just `pip` libs).
- ML training expects at least 15 labeled entries — if you add tests that create synthetic data, ensure you populate `Alumno.nivel_riesgo` values.

**Files to inspect first when starting work**:
- `app/__init__.py` — app factory, extensions, blueprint registration
- `app/models.py` — DB schema and `user_loader` implementation
- `app/analisis.py` — ML pipeline, model save/load locations
- `app/main/routes.py`, `app/alumnos/routes.py`, `app/auth/routes.py`, `app/reportes/routes.py` — endpoint behavior
- `config.py` — environment & DB defaults

If any of the above sections are unclear or you want me to expand examples (migration commands, a minimal local Docker Compose for Postgres, or a small script to seed training data), tell me which part and I will iterate.
