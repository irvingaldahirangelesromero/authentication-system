# Ruta: autentication/my-project/apps/services/src/faceid/application/login_face_usecase.py
from faceid.domain.face_recognizer import decode_image, get_face_encoding, deserialize_encoding, compare_face
from faceid.ports.user_repository_port import FaceIDUserRepositoryPort
from typing import Dict, Any

class LoginFaceUseCase:
    def __init__(self, user_repository: FaceIDUserRepositoryPort):
        self.user_repository = user_repository

    def execute(self, image_data_base64: str) -> Dict[str, Any]:
        if not image_data_base64:
            raise ValueError("No se proporcionó imagen")
            
        image = decode_image(image_data_base64)
        if image is None:
            raise ValueError("Error al procesar la imagen")

        unknown_encoding, error = get_face_encoding(image)
        if error:
            raise ValueError(error)

        all_users = self.user_repository.get_all_users_with_encodings()
        if not all_users:
            raise ValueError("No hay usuarios registrados con Face ID")

        best_match = None
        best_confidence = 0
        
        for user in all_users:
            try:
                known_encoding = deserialize_encoding(user['face_encoding'])
                confidence = compare_face(known_encoding, unknown_encoding)
                
                # Umbral de confianza (ajusta según tus pruebas)
                CONFIDENCE_THRESHOLD = 55.0 
                
                if confidence > CONFIDENCE_THRESHOLD and confidence > best_confidence:
                    best_confidence = confidence
                    best_match = user
            except Exception:
                # Ignorar error al deserializar un encoding
                continue
        
        if best_match:
            return {
                "success": True,
                "message": f"Bienvenido {best_match['first_name']}",
                "user": {
                    "id": str(best_match['_id']), # Convertir ObjectId a string
                    "email": best_match['email'],
                    "first_name": best_match['first_name']
                },
                "confidence": round(best_confidence, 2)
            }
        else:
            raise ValueError("Rostro no reconocido. Intenta nuevamente.")