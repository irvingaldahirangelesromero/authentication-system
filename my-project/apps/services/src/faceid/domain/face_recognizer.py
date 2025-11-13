# Ruta: autentication/my-project/apps/services/src/faceid/domain/face_recognizer.py
import cv2
import face_recognition
import numpy as np
import pickle
import base64
from typing import Tuple, Optional, Any

def decode_image(base64_string: str) -> Optional[np.ndarray]:
    """Convierte imagen base64 a formato numpy array"""
    try:
        img_data = base64.b64decode(base64_string.split(',')[1])
        nparr = np.frombuffer(img_data, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        return img
    except Exception as e:
        print(f"Error decodificando imagen: {e}")
        return None

def get_face_encoding(image: np.ndarray) -> Tuple[Optional[np.ndarray], Optional[str]]:
    """Obtiene el encoding facial de una imagen"""
    try:
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_image)
        
        if len(face_locations) == 0:
            return None, "No se detectó ningún rostro"
        
        if len(face_locations) > 1:
            return None, "Se detectaron múltiples rostros. Asegúrate de que solo haya una persona"
        
        face_encodings = face_recognition.face_encodings(rgb_image, face_locations)
        
        if len(face_encodings) == 0:
            return None, "No se pudo procesar el rostro"
        
        return face_encodings[0], None
    except Exception as e:
        print(f"Error obteniendo encoding: {e}")
        return None, "Error interno al procesar el rostro"

def serialize_encoding(encoding: np.ndarray) -> str:
    """Serializa el encoding facial a un string base64 para guardarlo en la BD"""
    return base64.b64encode(pickle.dumps(encoding)).decode('utf-8')

def deserialize_encoding(encoding_str: str) -> np.ndarray:
    """Deserializa el encoding facial desde un string base64 de la BD"""
    return pickle.loads(base64.b64decode(encoding_str))

def compare_face(known_encoding: np.ndarray, unknown_encoding: np.ndarray) -> float:
    """Compara dos rostros y devuelve la confianza (0-100)"""
    face_distance = face_recognition.face_distance([known_encoding], unknown_encoding)[0]
    # Invertimos la distancia para obtener "confianza"
    confidence = (1 - face_distance) * 100
    return confidence