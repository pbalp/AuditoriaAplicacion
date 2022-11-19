from sqlalchemy.orm import Session
from . import model
from . import schema

from passlib.context import CryptContext
from jose import JWTError, jwt
from typing import List
from datetime import datetime
import requests


CLAVE_SECRETA = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITMO = "HS256"

def decodeToken(token: str):
    return jwt.decode(token, CLAVE_SECRETA, algorithms=[ALGORITMO])


# Metodos GET

def getUserCorreo(db: Session, correo: str):
    return db.query(model.Usuario).filter(model.Usuario.correo == correo).first()

def getCliente(db: Session, idCliente: int):
    return db.query(model.Cliente).filter(model.Cliente.id == idCliente).first()

def getClienteDNI(db: Session, dni: str):
    return db.query(model.Cliente).filter(model.Cliente.dni == dni).first()

def getClienteCorreo(db: Session, correo: str):
    return db.query(model.Cliente).filter(model.Cliente.correo == correo).first()

def getClientes(db: Session, skip: int = 0, limit: int = 100):
    return db.query(model.Cliente).offset(skip).limit(limit).all()

def getBillete(db: Session, idBillete: int):
    response = requests.get("http://billetes:8000/billete/"+str(idBillete))
    billete = model.Billete(**response.json())
    return billete

def getBilletesCliente(db: Session, idCliente: int, skip: int, limit: int):
    response = requests.get("http://billetes:8000/billetes/cliente/"+str(idCliente)+"/skip/"+str(skip)+"/limit/"+str(limit))
    return response.json()

def getDuracion(db: Session, idBillete: int):
    billete = getBillete(db, idBillete)
    fechas = parseFechas(billete.fechaSalida, billete.fechaLlegada, False, False)
    duracion = fechas["fechaLlegada"]-fechas["fechaSalida"]
    return (datetime.min+duracion).time()

def parseFechas(fechaSalida: str, fechaLlegada: str, fechaSalidaNone: bool, fechaLlegadaNone: bool):
    if not fechaSalidaNone:
        fechaSalidaSplit = fechaSalida.split('T')
        fechaSalidaArray = fechaSalidaSplit[0] + " " + fechaSalidaSplit[1]
        fechaSalidaDate = datetime.strptime(fechaSalidaArray, "%Y-%m-%d %H:%M:%S")
    if not fechaLlegadaNone:
        fechaLlegadaSplit = fechaLlegada.split('T')
        fechaLlegadaArray = fechaLlegadaSplit[0] + " " + fechaLlegadaSplit[1]
        fechaLlegadaDate = datetime.strptime(fechaLlegadaArray, "%Y-%m-%d %H:%M:%S")
    return {"fechaSalida": fechaSalidaDate, "fechaLlegada": fechaLlegadaDate}

def getPuntosCliente(db: Session, idCliente: int):
    cliente = getCliente(db, idCliente)
    return cliente.puntos

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
def getPasswordHash(password):
    return pwd_context.hash(password)


# Metodos POST

def crearCliente(db: Session, cliente: schema.ClienteBase):
    cliente.password = getPasswordHash(cliente.password)
    db_cliente = model.Cliente(**cliente.dict())
    db_cliente.puntos = 0
    db_cliente.rol = 'cliente'
    db.add(db_cliente)
    db.commit()
    db.refresh(db_cliente)
    return db_cliente


# Metodos PATCH

def updateCliente(db: Session, idCliente: int, newCliente: schema.ClienteSet):
    db_cliente = getCliente(db, idCliente)
    update_data = newCliente.dict(exclude_unset=True)
    for key in update_data:
        setattr(db_cliente, key, update_data[key])
    if newCliente.password is not None: db_cliente.password = getPasswordHash(newCliente.password)
    db.commit()
    db.refresh(db_cliente)
    return db_cliente

def updateClientePuntos(db: Session, idCliente: int, newPuntos: int):
    cliente = getCliente(db, idCliente)
    cliente.puntos += int(newPuntos)
    db.commit()
    db.refresh(cliente)
    return cliente


# Metodos DELETE

def deleteCliente(db: Session, idCliente: int):
    cliente = getCliente(db, idCliente)
    response = deleteBilletesCliente(db, idCliente)
    if response==500:
        return 500
    db.delete(cliente)
    db.commit()

def deleteBillete(db: Session, idBillete: int):
    response = requests.delete("http://billetes:8000/billete/"+str(idBillete)+"/borrar/")
    return response.status_code

def deleteBilletesCliente(db: Session, idCliente: int):
    requests.delete("http://billetes:8000/billetes/cliente/"+str(idCliente)+"/borrar")

def commitBillete():
    response = requests.delete("http://billetes:8000/billete/commit")

def rollback(db: Session):
    db.rollback()
    response = requests.delete("http://billetes:8000/billetes/rollback")

