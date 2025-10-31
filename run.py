# Archivo: /run.py

from app import create_app

# Creamos la aplicación llamando a nuestra fábrica
app = create_app()

if __name__ == '__main__':
    # Iniciamos el servidor en modo "debug" (se reinicia solo con cambios)
    app.run(debug=True)