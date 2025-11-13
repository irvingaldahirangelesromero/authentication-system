# Ruta: authentication/my-project/apps/services
from adapters.http.flask_controller import app

# Cambia esta parte al final del archivo:
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print("🚀 Starting TOTP Service on port", port)
    app.run(debug=False, host='0.0.0.0', port=port)