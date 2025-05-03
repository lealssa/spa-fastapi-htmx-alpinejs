import bcrypt
import jwt

from config import settings
from schemas import UserJwt

class NotAuthenticatedError(Exception):
    pass    

def decrypt_access_token(access_token: str | None) -> dict[str, str | int] | None:
    try:
        _, token = access_token.split()
        data = jwt.decode(token, settings.jwt_key, [settings.jwt_algorithm])
    except Exception:
        data = None
    return data

def create_access_token(user_jwt: UserJwt) -> str:
    payload = {"sub": user_jwt.id, "name": user_jwt.first_name}
    token = jwt.encode(
        payload,
        settings.jwt_key,
        settings.jwt_algorithm,
    ) 
    return token   

def create_password_hash(plain_text_password: str) -> str:    
    if not isinstance(plain_text_password, str):
        raise TypeError("A senha deve ser uma string.")    
    password_bytes = plain_text_password.encode('utf-8')    
    hashed_password_bytes = bcrypt.hashpw(password_bytes, bcrypt.gensalt())    
    hashed_password = hashed_password_bytes.decode('utf-8')    
    return hashed_password

def check_password_hash(plain_text_password: str, password_hash: str) -> bool:
    senha_plana_bytes = plain_text_password.encode('utf-8')
    senha_hash_bytes = password_hash.encode('utf-8')
    return bcrypt.checkpw(senha_plana_bytes, senha_hash_bytes)