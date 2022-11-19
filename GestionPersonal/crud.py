from sqlalchemy.orm import Session
from . import model
from . import schema

from passlib.context import CryptContext
from jose import JWTError, jwt
from typing import List
import requests

CLAVE_SECRETA = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITMO = "HS256"

def decodeToken(token: str):
    return jwt.decode(token, CLAVE_SECRETA, algorithms=[ALGORITMO])


# Metodos GET

def getUserCorreo(db: Session, correo: str):
    return db.query(model.Usuario).filter(model.Usuario.correo == correo).first()

def getAdministrador(db: Session, idAdministrador: int):
    return db.query(model.Administrador).filter(model.Administrador.id == idAdministrador).first()

def getConductor(db: Session, idConductor: int):
    return db.query(model.Conductor).filter(model.Conductor.id == idConductor).first()

def getConductorDNI(db: Session, dni: str):
    return db.query(model.Conductor).filter(model.Conductor.dni == dni).first()

def getConductorCorreo(db: Session, correo: str):
    return db.query(model.Conductor).filter(model.Conductor.correo == correo).first()

def getAdministradorCorreo(db: Session, correo: str):
    return db.query(model.Administrador).filter(model.Administrador.correo == correo).first()

def getConductores(db: Session, skip: int = 0, limit: int = 100):
    return db.query(model.Conductor).offset(skip).limit(limit).all()

def getViajesConductor(db: Session, idConductor: int, skip: int, limit: int):
    response = requests.get("http://billetes:8000/viajes/conductor/"+str(idConductor)+"/skip/"+str(skip)+"/limit/"+str(limit))
    return response.json()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
def getPasswordHash(password):
    return pwd_context.hash(password)

# Metodos POST

def crearAdministrador(db: Session, administrador: schema.AdministradorBase):
    administrador.password = getPasswordHash(administrador.password)
    db_administrador = model.Administrador(**administrador.dict())
    db.add(db_administrador)
    db.commit()
    db.refresh(db_administrador)
    return db_administrador

def crearConductor(db: Session, conductor: schema.ConductorBase):
    conductor.password = getPasswordHash(conductor.password)
    db_conductor = model.Conductor(**conductor.dict())
    db_conductor.rol = 'conductor'
    db.add(db_conductor)
    db.commit()
    db.refresh(db_conductor)
    return db_conductor


# Metodos PATCH

def updateAdministrador(db: Session, idAdministrador: int, newAdministrador: schema.AdministradorSet):
    db_admin = getAdministrador(db, idAdministrador)
    update_data = newAdministrador.dict(exclude_unset=True)
    for key in update_data:
        setattr(db_admin, key, update_data[key])
    if newAdministrador.password is not None: db_admin.password = getPasswordHash(newAdministrador.password)
    db.commit()
    db.refresh(db_admin)
    return db_admin

def updateConductor(db: Session, idConductor: int, newConductor: schema.ConductorSet):
    db_conductor = getConductor(db, idConductor)
    update_data = newConductor.dict(exclude_unset=True)
    for key in update_data:
        setattr(db_conductor, key, update_data[key])
    if newConductor.password is not None: db_conductor.password = getPasswordHash(newConductor.password)
    db.commit()
    db.refresh(db_conductor)
    return db_conductor


# Metodos DELETE

def deleteAdministrador(db: Session, idAdministrador: int):
    administrador = getAdministrador(db, idAdministrador)
    db.delete(administrador)
    db.commit()

def deleteConductor(db: Session, idConductor: int):
    conductor = getConductor(db, idConductor)
    deleteViajesConductor(db, idConductor)
    db.delete(conductor)
    db.commit()

def deleteAutobus(db: Session, idAutobus: int):
    response = requests.delete("http://autobuses:8000/autobus/"+str(idAutobus)+"/borrar")
    return response.status_code

def deleteRuta(db: Session, idRuta: int):
    response = requests.delete("http://autobuses:8000/ruta/"+str(idRuta)+"/borrar")
    return response.status_code

def deleteViaje(db: Session, idViaje: int):
    return requests.delete("http://billetes:8000/viaje/"+str(idViaje)+"/borrar")

def deleteViajesConductor(db: Session, idConductor: int):
    requests.delete("http://billetes:8000/viajes/conductor/"+str(idConductor)+"/borrar")

def rollback(db: Session):
    db.rollback
    requests.get("http://billetes:8000/billetes/rollback")

