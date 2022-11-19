from sqlalchemy.orm import Session
from . import model
from . import schema

from passlib.context import CryptContext
from jose import JWTError, jwt
from typing import Optional
from datetime import datetime, timedelta
import requests

CLAVE_SECRETA = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITMO = "HS256"


# Autenticacion

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verificarPassword(password, hash):
    return pwd_context.verify(password, hash)

def getPasswordHash(password):
    return pwd_context.hash(password)

def autenticarUsuario(db: Session, correo: str, password: str):
    usuario = getUserCorreo(db, correo)
    if not usuario:
        return False
    if not verificarPassword(password, usuario.password):
        return False
    return usuario

def crearToken(data: dict, expires_delta: Optional[timedelta] = None):
    codificar = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    token = jwt.encode(codificar, CLAVE_SECRETA, algorithm=ALGORITMO)
    return token

def decodeToken(token: str):
    return jwt.decode(token, CLAVE_SECRETA, algorithms=[ALGORITMO])

def getUserCorreo(db: Session, correo: str):
    response = requests.get("http://clientes:8000/user/correo/"+str(correo))
    print("RESPONSE AUTENTICACION ", response.json())
    if response.json() is None:
        response = requests.get("http://personal:8000/user/correo/"+str(correo))
    user = model.Usuario(**response.json())
    return user

