# Ruta: authentication/my-project/apps/services/src/totp/adapters/http/flask_controller.py

import os
import sys
from flask import Flask, Response, request, jsonify, session, make_response
from application.generate_qr_usecase import GenerateQRUseCase
from application.validate_otp_usecase import ValidateOTPUseCase
from application.register_user_usecase import RegisterUserUseCase
from adapters.http.qr_generator_adapter import QRGeneratorAdapter
from infraestructure.mongo_user_repository import MongoUserRepository
from flask_cors import CORS

# --- IMPORTACIÓN FACE ID ---
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
if src_path not in sys.path:
    sys.path.insert(0, src_path)
    print(f"Añadido al path (raíz de servicios): {src_path}")

try:
    from faceid.adapters.http.faceid_controller import faceid_api
    print("✅ Blueprint de Face ID cargado exitosamente.")
except ImportError as e:
    print(f"⚠️  ADVERTENCIA: No se pudo cargar el Blueprint de Face ID. Error: {e}")
    faceid_api = None
except Exception as e:
    print(f"❌ ERROR INESPERADO al cargar Face ID: {e}")
    faceid_api = None

# --- FIN IMPORTACIÓN ---

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("FLASK_SECRET_KEY", "clave-local-segura")

app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="None",
    SESSION_COOKIE_SECURE=True,
    PERMANENT_SESSION_LIFETIME=3600
)

CORS(app, resources={
    r"/*": {
        "origins": [  
            "https://authentication-system-sigma-five.vercel.app",
            "https://authentication-system-xp73.onrender.com",
            "https://authentication-system-8jpe.onrender.com",
        ],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True
    }
})

# Registrar blueprint de Face ID si está disponible
if faceid_api:
    app.register_blueprint(faceid_api, url_prefix='/api/faceid')
    print("✅ Blueprint de Face ID registrado correctamente.")

user_repo = MongoUserRepository()
qr_adapter = QRGeneratorAdapter()
generate_qr_usecase = GenerateQRUseCase(qr_adapter)
register_usecase = RegisterUserUseCase(user_repo)

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    first_name = data.get('first_name')
    auth_method = data.get('auth_method', 'totp')
    phone_number = data.get('phone_number')

    if not email or not password:
        return jsonify({'error': 'Email y contraseña requeridos'}), 400

    if auth_method == 'sms' and not phone_number:
        return jsonify({'error': 'Número de teléfono requerido para verificación SMS'}), 400

    try:
        if auth_method == 'totp':
            uri = register_usecase.execute(email, password, first_name)
            session['email'] = email
            session['first_name'] = first_name
            session['auth_method'] = 'totp'
            return jsonify({'otp_uri': uri, 'requires_otp': True}), 200
        else:
            # Para método SMS - redirigir al servicio SMS OTP
            return jsonify({
                'error': 'Para registro SMS, use el servicio SMS OTP directamente',
                'redirect_to_sms': True
            }), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    print("=" * 50)
    print("🔐 LOGIN TOTP - Datos recibidos:")
    print(f"   Email: {email}")
    print("=" * 50)

    user = user_repo.collection.find_one({"email": email})
    
    if user and user.get("password") == password:
        session['email'] = email
        session['first_name'] = user.get("first_name", "")
        auth_method = user.get("auth_method", "totp")
        session['auth_method'] = auth_method
        
        print(f"✅ Login TOTP exitoso para: {email}")
        print(f"📋 Método de autenticación: {auth_method}")
        
        if auth_method == "sms":
            # USUARIO ES SMS - Redirigir al servicio SMS OTP
            session['phone_number'] = user.get("phone_number")
            print(f"📱 Usuario SMS detectado, redirigiendo a servicio SMS OTP")
            
            return jsonify({
                "success": True, 
                "requires_otp": True,
                "auth_method": "sms",
                "message": "Usuario SMS, redirigir a servicio SMS OTP",
                "redirect_to_sms": True
            }), 200
        else:
            # USUARIO ES TOTP - Continuar con flujo normal
            requires_otp = bool(user.get("secret"))
            print(f"🔐 Usuario TOTP, requiere OTP: {requires_otp}")
            
            return jsonify({
                "success": True, 
                "requires_otp": requires_otp,
                "auth_method": "totp"
            }), 200
    else:
        print(f"❌ Login TOTP fallido para: {email}")
        return jsonify({"success": False, "error": "Credenciales inválidas"}), 401

@app.route('/user-info', methods=['GET'])
def user_info():
    email = session.get('email')
    if not email:
        return jsonify({'error': 'No hay sesión activa'}), 401

    user = user_repo.collection.find_one({"email": email}, {"_id": 0, "first_name": 1, "auth_method": 1})
    if not user:
        return jsonify({'error': 'Usuario no encontrado'}), 404

    return jsonify({
        'email': email,
        'first_name': user.get('first_name', ''),
        'auth_method': user.get('auth_method', 'totp')
    }), 200

@app.route('/qr')
def qr():
    print(f"DEBUG: Accediendo a /qr. Contenido de la sesión: {session}")
    email = session.get('email')
    if not email:
        print("DEBUG: No hay email en la sesión para /qr. Devolviendo 401.")
        return jsonify({'error': 'No hay sesión activa'}), 401
    
    print(f"DEBUG: Email en sesión para /qr: {email}")

    secret = user_repo.get_secret_by_email(email)
    if not secret:
        print(f"DEBUG: No se encontró secreto para el email {email}. Devolviendo 404.")
        return jsonify({'error': 'Usuario no registrado'}), 404
    print(f"DEBUG: Secreto encontrado para {email}. Generando QR.")
    img_bytes = generate_qr_usecase.execute(secret, email, 'MyApp')
    return Response(img_bytes, mimetype='image/png')

@app.route('/validate', methods=['POST'])
def validate():
    data = request.get_json()
    code = data.get('code')
    email = session.get('email')

    if not email:
        return jsonify({'valid': False, 'error': 'Sesión no activa'}), 401

    if not code or len(code) != 6:
        return jsonify({'valid': False, 'error': 'Código inválido'}), 400

    secret = user_repo.get_secret_by_email(email)
    if not secret:
        return jsonify({'valid': False, 'error': 'Usuario no registrado'}), 404

    validate_usecase = ValidateOTPUseCase(secret)
    is_valid = validate_usecase.execute(code)
    return jsonify({'valid': is_valid})

@app.after_request
def add_no_cache_headers(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    resp = make_response(jsonify({"success": True}))
    cookie_name = app.config.get("SESSION_COOKIE_NAME", "session")
    resp.delete_cookie(cookie_name, httponly=True, samesite='Lax')
    return resp

@app.route('/session-check', methods=['GET'])
def session_check():
    return jsonify({
        "logged_in": bool(session.get('email')),
        "email": session.get('email'),
        "auth_method": session.get('auth_method', 'totp')
    })

@app.route('/ping-db')
def ping_db():
    try:
        user_repo.collection.insert_one({"test": "ok"})
        return jsonify({"status": "MongoDB conectado correctamente"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    users_count = user_repo.collection.count_documents({})
    return jsonify({
        'status': 'OK', 
        'service': 'TOTP Service',
        'mongo_connected': True,
        'total_users': users_count,
        'faceid_loaded': faceid_api is not None
    }), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print("=" * 60)
    print("🚀 Starting TOTP Service - VERSIÓN MEJORADA")
    print(f"📡 Server: https://0.0.0.0:{port}")
    print("💾 MongoDB: Atlas")
    print("🔐 Endpoints available:")
    print("   - POST /register")
    print("   - POST /login") 
    print("   - POST /validate")
    print("   - GET  /qr")
    print("   - GET  /user-info")
    print("   - GET  /session-check")
    print("   - GET  /health")
    print("=" * 60)
    app.run(debug=False, host='0.0.0.0', port=port)