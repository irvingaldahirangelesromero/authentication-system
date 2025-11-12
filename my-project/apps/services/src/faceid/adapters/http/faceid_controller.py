from flask import Blueprint, request, jsonify
from faceid.infrastructure.mongo_faceid_repository import MongoFaceIDRepository
from faceid.application.register_face_usecase import RegisterFaceUseCase
from faceid.application.login_face_usecase import LoginFaceUseCase
from faceid.application.login_password_usecase import LoginPasswordUseCase
from faceid.application.list_users_usecase import ListUsersUseCase
from faceid.application.delete_user_usecase import DeleteUserUseCase
# Creamos el Blueprint
faceid_api = Blueprint('faceid_api', __name__)

# Instanciamos el repositorio
try:
    repository = MongoFaceIDRepository()
except Exception as e:
    print(f"FALLO AL INICIAR REPOSITORIO FACEID: {e}")
    repository = None

@faceid_api.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'success': True, 
        'service': 'Face ID Service',
        'status': 'OK' if repository else 'REPO_FAILED'
    }), 200

@faceid_api.route('/register', methods=['POST', 'OPTIONS'])  # <--- AÑADIDO 'OPTIONS'
def register():
    if request.method == 'OPTIONS':  # <--- AÑADIDO ESTE BLOQUE
        return jsonify({'status': 'ok'}), 200

    if not repository:
        return jsonify({'success': False, 'message': 'Servicio FaceID no disponible'}), 503
    try:
        data = request.json
        use_case = RegisterFaceUseCase(repository)
        result = use_case.execute(
            data.get('email'),
            data.get('password'),
            data.get('first_name'),
            data.get('image')
        )
        return jsonify(result), 201
    except ValueError as e:
        return jsonify({'success': False, 'message': str(e)}), 400
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error del servidor: {str(e)}'}), 500

@faceid_api.route('/login/face', methods=['POST', 'OPTIONS'])  # <--- AÑADIDO 'OPTIONS'
def login_face():
    if request.method == 'OPTIONS':  # <--- AÑADIDO ESTE BLOQUE
        return jsonify({'status': 'ok'}), 200
        
    if not repository:
        return jsonify({'success': False, 'message': 'Servicio FaceID no disponible'}), 503
    try:
        data = request.json
        use_case = LoginFaceUseCase(repository)
        result = use_case.execute(data.get('image'))
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({'success': False, 'message': str(e)}), 401
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error del servidor: {str(e)}'}), 500

@faceid_api.route('/login/password', methods=['POST', 'OPTIONS'])  # <--- AÑADIDO 'OPTIONS'
def login_password():
    if request.method == 'OPTIONS':  # <--- AÑADIDO ESTE BLOQUE
        return jsonify({'status': 'ok'}), 200

    if not repository:
        return jsonify({'success': False, 'message': 'Servicio FaceID no disponible'}), 503
    try:
        data = request.json
        use_case = LoginPasswordUseCase(repository)
        result = use_case.execute(data.get('email'), data.get('password'))
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({'success': False, 'message': str(e)}), 401
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error del servidor: {str(e)}'}), 500

@faceid_api.route('/users', methods=['GET']) # (GET no necesita OPTIONS)
def get_users():
    if not repository:
        return jsonify({'success': False, 'message': 'Servicio FaceID no disponible'}), 503
    try:
        use_case = ListUsersUseCase(repository)
        result = use_case.execute()
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error del servidor: {str(e)}'}), 500

@faceid_api.route('/users/<user_id>', methods=['DELETE', 'OPTIONS'])  # <--- AÑADIDO 'OPTIONS'
def delete_user(user_id):
    if request.method == 'OPTIONS':  # <--- AÑADIDO ESTE BLOQUE
        return jsonify({'status': 'ok'}), 200

    if not repository:
        return jsonify({'success': False, 'message': 'Servicio FaceID no disponible'}), 503
    try:
        use_case = DeleteUserUseCase(repository)
        result = use_case.execute(user_id)
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({'success': False, 'message': str(e)}), 404
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error del servidor: {str(e)}'}), 500