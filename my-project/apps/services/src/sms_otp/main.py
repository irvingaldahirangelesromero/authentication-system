# Ruta: authentication/my-project/apps/services/src/sms_otp/main.py
import sys
import os
import secrets
from flask import Flask, request, jsonify, session
from flask_cors import CORS
from datetime import timedelta

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

try:
    from application.sms_otp_usecases import SendOTPUseCase, VerifyOTPUseCase
    from infrastructure.twilio_sms_adapter import TwilioSMSAdapter
    from infrastructure.mongo_repository import MongoDBUserRepository
    print("✅ Módulos importados correctamente")
except ImportError as e:
    print(f"❌ Error importando módulos: {e}")
    exit(1)

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

# CONFIGURACIÓN MEJORADA DE SESIÓN Y CORS
app.config.update(
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='None',
    PERMANENT_SESSION_LIFETIME=timedelta(minutes=30),
    #SESSION_COOKIE_DOMAIN='.onrender.com'  # IMPORTANTE: Dominio compartido
)

# CONFIGURACIÓN CORS COMPLETA PARA PRODUCCIÓN
CORS(app, 
     origins=[
         "https://authentication-system-sigma-five.vercel.app",
         "https://authentication-system-xp73.onrender.com",
         "https://authentication-system-8jpe.onrender.com",
     ],
     supports_credentials=True,
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
     allow_headers=["Content-Type", "Authorization", "X-Requested-With"]
)

# INICIALIZAR MONGODB
print("🔄 Conectando a MongoDB...")
try:
    mongo_repo = MongoDBUserRepository()
    sms_service = TwilioSMSAdapter()
    send_otp_use_case = SendOTPUseCase(sms_service, mongo_repo)
    verify_otp_use_case = VerifyOTPUseCase(mongo_repo)
    print("✅ MongoDB y servicios inicializados correctamente")
except Exception as e:
    print(f"❌ Error crítico: {e}")
    exit(1)

# Solo pending_verifications en memoria (sesiones activas)
pending_verifications = {}

@app.route('/health', methods=['GET'])
def health_check():
    users_count = mongo_repo.collection.count_documents({})
    return jsonify({
        'status': 'OK', 
        'service': 'SMS OTP Service',
        'mongo_connected': True,
        'total_users': users_count,
        'pending_sessions': len(pending_verifications)
    }), 200

@app.route('/register', methods=['POST', 'OPTIONS'])
def register():
    if request.method == "OPTIONS":
        return jsonify({"status": "ok"}), 200
    
    try:
        data = request.get_json()
        print("=" * 50)
        print("📝 REGISTRO - Datos recibidos:")
        print(f"   Email: {data.get('email')}")
        print(f"   Teléfono: {data.get('phone_number')}")
        print("=" * 50)
        
        email = data.get('email')
        password = data.get('password')
        first_name = data.get('first_name', '')
        auth_method = data.get('auth_method', 'sms')
        phone_number = data.get('phone_number')
        
        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400
        
        if mongo_repo.user_exists(email):
            return jsonify({'error': 'User already exists'}), 400
        
        if auth_method == 'sms' and not phone_number:
            return jsonify({'error': 'Phone number is required for SMS authentication'}), 400
        
        # Guardar usuario en MONGODB
        user_data = {
            'email': email,
            'password': password,
            'first_name': first_name,
            'auth_method': auth_method,
            'phone_number': phone_number,
            'verified': False,
            'secret': None
        }
        
        success = mongo_repo.save_user(email, user_data)
        
        if not success:
            return jsonify({'error': 'Failed to save user'}), 500
        
        print(f"✅ Usuario guardado en MongoDB: {email}")
        
        # Si es SMS, enviar OTP INMEDIATAMENTE
        if auth_method == 'sms':
            print(f"📤 ENVIANDO OTP a: {phone_number}")
            otp_sent = send_otp_use_case.execute(phone_number)
            
            if otp_sent:
                # MEJORA: Configurar sesión correctamente antes de enviar respuesta
                session.permanent = True
                session['email'] = email
                session['phone_number'] = phone_number
                session['pending_2fa'] = True
                session['user_authenticated'] = False
                session['auth_method'] = 'sms'
                
                # Guardar también en pending_verifications para backup
                pending_verifications[email] = {
                    'phone_number': phone_number,
                    'timestamp': os.times().elapsed
                }
                
                print(f"✅ OTP enviado exitosamente a {phone_number}")
                print(f"📋 Sesión creada para: {email}")
                
                return jsonify({
                    'success': True,
                    'message': 'User registered. OTP sent to phone.',
                    'requires_otp': True,
                    'auth_method': 'sms',
                    'email': email
                }), 200
            else:
                print("❌ Falló el envío de OTP")
                return jsonify({'error': 'Failed to send OTP'}), 500
        
        # Para TOTP
        return jsonify({
            'success': True,
            'message': 'User registered successfully',
            'requires_qr': True
        }), 200
        
    except Exception as e:
        print(f"❌ Error in register: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/login', methods=['POST', 'OPTIONS'])
def login():
    if request.method == "OPTIONS":
        return jsonify({"status": "ok"}), 200
    
    try:
        data = request.get_json()
        print("=" * 50)
        print("🔐 LOGIN SMS OTP - Datos recibidos:")
        print(f"   Email: {data.get('email')}")
        print("=" * 50)
        
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400
        
        # BUSCAR EN MONGODB
        user = mongo_repo.get_user(email)
        
        if not user:
            print(f"❌ Usuario no encontrado: {email}")
            return jsonify({'error': 'User not found'}), 404
        
        if user['password'] != password:
            print(f"❌ Contraseña incorrecta para: {email}")
            return jsonify({'error': 'Invalid password'}), 401
        
        # VERIFICAR MÉTODO DE AUTENTICACIÓN
        auth_method = user.get('auth_method', 'sms')
        print(f"📋 Método de autenticación detectado: {auth_method}")
        
        if auth_method != 'sms':
            print(f"⚠️ Usuario {email} no es SMS, es: {auth_method}")
            return jsonify({'error': 'User authentication method mismatch'}), 400
        
        # MEJORA: Configurar sesión correctamente
        session.permanent = True
        session['email'] = email
        session['phone_number'] = user['phone_number']
        session['pending_2fa'] = True
        session['user_authenticated'] = False
        session['auth_method'] = 'sms'
        
        print(f"✅ Login SMS OTP exitoso para: {email}")
        print(f"📋 Sesión configurada: {dict(session)}")
        
        # ENVIAR OTP AUTOMÁTICAMENTE
        phone_number = user['phone_number']
        print(f"📤 ENVIANDO OTP AUTOMÁTICO a: {phone_number}")
        
        success = send_otp_use_case.execute(phone_number)
        
        if success:
            pending_verifications[email] = {
                'phone_number': phone_number,
                'timestamp': os.times().elapsed
            }
            print(f"✅ OTP enviado exitosamente a {phone_number}")
            
            return jsonify({
                'success': True,
                'requires_otp': True,
                'auth_method': 'sms',
                'message': 'OTP sent to your phone',
                'email': email
            }), 200
        else:
            print("❌ Falló el envío de OTP")
            return jsonify({'error': 'Failed to send OTP'}), 500
        
    except Exception as e:
        print(f"❌ Error in login: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/resend-otp', methods=['POST', 'OPTIONS'])
def resend_otp():
    if request.method == "OPTIONS":
        return jsonify({"status": "ok"}), 200
    
    try:
        data = request.get_json()
        print("=" * 50)
        print("🔄 RESEND OTP - Datos recibidos:")
        print(f"   Email en body: {data.get('email')}")
        print(f"   Email en sesión: {session.get('email')}")
        print("=" * 50)
        
        # BUSCAR EMAIL EN BODY O SESIÓN
        email = data.get('email') or session.get('email')
        
        if not email:
            return jsonify({'error': 'Email is required'}), 400
        
        print(f"🔍 Buscando teléfono para: {email}")
        
        # BUSCAR PHONE_NUMBER
        phone_number = None
        
        # 1. Buscar en sesión primero
        if session.get('email') == email:
            phone_number = session.get('phone_number')
            print(f"📱 Teléfono encontrado en sesión: {phone_number}")
        # 2. Buscar en pending_verifications
        elif email in pending_verifications:
            phone_number = pending_verifications[email]['phone_number']
            print(f"📱 Teléfono encontrado en pending: {phone_number}")
        # 3. Buscar en MONGODB (usuario registrado)
        else:
            user = mongo_repo.get_user(email)
            if user and user.get('phone_number'):
                phone_number = user['phone_number']
                # Actualizar sesión y pending_verifications
                session['email'] = email
                session['phone_number'] = phone_number
                session['pending_2fa'] = True
                session['auth_method'] = user.get('auth_method', 'sms')
                pending_verifications[email] = {
                    'phone_number': phone_number,
                    'timestamp': os.times().elapsed
                }
                print(f"📱 Teléfono encontrado en MongoDB: {phone_number}")
            else:
                print(f"❌ Usuario no encontrado en MongoDB: {email}")
                return jsonify({'error': 'No pending verification found for this email'}), 400
        
        print(f"📤 REENVIANDO OTP a: {phone_number}")
        success = send_otp_use_case.execute(phone_number)
        
        if success:
            print(f"✅ OTP reenviado exitosamente")
            return jsonify({'message': 'OTP resent successfully'}), 200
        else:
            print(f"❌ Falló el reenvío de OTP")
            return jsonify({'error': 'Failed to resend OTP'}), 500
            
    except Exception as e:
        print(f"❌ Error in resend_otp: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/verify-otp', methods=['POST', 'OPTIONS'])
def verify_otp():
    if request.method == "OPTIONS":
        return jsonify({"status": "ok"}), 200
    
    try:
        data = request.get_json()
        print("=" * 50)
        print("🔍 VERIFICACIÓN OTP:")
        print(f"   OTP recibido: {data.get('otp')}")
        print(f"   Email en sesión: {session.get('email')}")
        print(f"   Sesión completa: {dict(session)}")
        print("=" * 50)
        
        otp = data.get('otp')
        
        if not otp:
            return jsonify({'error': 'OTP is required'}), 400
        
        # MEJORA: Múltiples formas de obtener el email
        email = session.get('email')
        
        if not email:
            # Intentar obtener de pending_verifications usando el OTP como referencia
            # o buscar en el cuerpo de la solicitud
            email = data.get('email')
            if not email:
                return jsonify({'error': 'No active session. Please login again.'}), 400
            else:
                # Si tenemos email pero no sesión, intentar recuperar la sesión
                session['email'] = email
                user = mongo_repo.get_user(email)
                if user:
                    session['phone_number'] = user.get('phone_number')
                    session['auth_method'] = user.get('auth_method', 'sms')
        
        # Obtener phone_number de la sesión o de la base de datos
        phone_number = session.get('phone_number')
        if not phone_number:
            user = mongo_repo.get_user(email)
            if user and user.get('phone_number'):
                phone_number = user['phone_number']
                session['phone_number'] = phone_number
            else:
                return jsonify({'error': 'No phone number found'}), 400
        
        print(f"🔐 Verificando OTP: {otp} para teléfono: {phone_number}")
        is_valid = verify_otp_use_case.execute(phone_number, otp)
        
        if is_valid:
            # Actualizar usuario en MongoDB
            mongo_repo.update_user(email, {'verified': True})
            
            # MEJORA: Actualizar sesión correctamente
            session['pending_2fa'] = False
            session['authenticated'] = True
            session['user_verified'] = True
            session['user_authenticated'] = True
            
            # Limpiar sesión activa
            if email in pending_verifications:
                del pending_verifications[email]
            
            print("✅ OTP verificado exitosamente")
            print(f"📋 Sesión actualizada: {dict(session)}")
            
            return jsonify({
                'valid': True,
                'message': 'OTP verified successfully',
                'email': email,
                'authenticated': True
            }), 200
        else:
            print("❌ OTP inválido o expirado")
            return jsonify({
                'valid': False,
                'error': 'Invalid or expired OTP'
            }), 400
            
    except Exception as e:
        print(f"❌ Error in verify_otp: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/session-status', methods=['GET'])
def session_status():
    """Endpoint para verificar el estado de la sesión"""
    return jsonify({
        'has_session': bool(session.get('email')),
        'email': session.get('email'),
        'pending_2fa': session.get('pending_2fa', False),
        'authenticated': session.get('authenticated', False),
        'auth_method': session.get('auth_method', 'sms')
    }), 200

@app.route('/user-info', methods=['GET'])
def user_info():
    """Endpoint para obtener información del usuario autenticado"""
    email = session.get('email')
    if not email:
        return jsonify({'error': 'No active session'}), 401
    
    user = mongo_repo.get_user(email)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify({
        'email': user['email'],
        'first_name': user.get('first_name', ''),
        'auth_method': user.get('auth_method', 'sms'),
        'verified': user.get('verified', False)
    }), 200

@app.route('/debug', methods=['GET'])
def debug():
    users_from_mongo = list(mongo_repo.collection.find({}, {'password': 0}))
    return jsonify({
        'mongo_users': [user['email'] for user in users_from_mongo],
        'pending_verifications': pending_verifications,
        'session': dict(session),
        'total_users': len(users_from_mongo)
    }), 200

@app.route('/logout', methods=['POST', 'OPTIONS'])
def logout():
    if request.method == "OPTIONS":
        return jsonify({"status": "ok"}), 200
    
    try:
        email = session.get('email')
        if email and email in pending_verifications:
            del pending_verifications[email]
        
        session.clear()
        print(f"✅ Logout exitoso para: {email}")
        
        resp = jsonify({"success": True, "message": "Logged out successfully"})
        return resp
    except Exception as e:
        print(f"❌ Error in logout: {e}")
        return jsonify({'error': str(e)}), 500

# MEJORA: Middleware para manejar sesiones
@app.before_request
def make_session_permanent():
    session.permanent = True

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    print("=" * 60)
    print("🚀 Starting SMS OTP Service CON MONGODB ATLAS - VERSIÓN MEJORADA")
    print(f"📡 Server: https://0.0.0.0:{port}")
    print("💾 MongoDB: Atlas")
    print("🔐 Endpoints available:")
    print("   - POST /register")
    print("   - POST /login") 
    print("   - POST /verify-otp")
    print("   - POST /resend-otp")
    print("   - GET  /session-status")
    print("   - GET  /user-info")
    print("   - GET  /health")
    print("=" * 60)
    app.run(debug=False, host='0.0.0.0', port=port)