# Ruta: authentication/my-project/apps/services
import os
import sys

# Configurar paths
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from adapters.http.flask_controller import app

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print("🚀 Starting TOTP Service on port", port)
    app.run(debug=False, host='0.0.0.0', port=port)