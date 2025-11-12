from faceid.domain.face_recognizer import decode_image, get_face_encoding, serialize_encoding
from faceid.ports.user_repository_port import FaceIDUserRepositoryPort

class RegisterFaceUseCase:
    def __init__(self, user_repository: FaceIDUserRepositoryPort):
        self.user_repository = user_repository

    def execute(self, email, password, first_name, image_data_base64):
        if not email or not password or not first_name or not image_data_base64:
            raise ValueError("Todos los campos son requeridos (email, password, first_name, image)")
        
        image = decode_image(image_data_base64)
        if image is None:
            raise ValueError("Error al procesar la imagen")
        
        encoding, error = get_face_encoding(image)
        if error:
            raise ValueError(error)
            
        encoding_str = serialize_encoding(encoding)
        
        # Verificamos si el email ya existe
        existing_user = self.user_repository.get_user_by_email(email)
        if existing_user:
            raise ValueError("El email ya está registrado")

        success = self.user_repository.save_user_with_encoding(
            email, password, first_name, encoding_str
        )
        
        if not success:
            raise Exception("No se pudo guardar el usuario en la base de datos")
        
        return {"success": True, "message": f"Usuario {first_name} registrado exitosamente"}