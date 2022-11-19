from sqlalchemy.orm import Session
from typing import List
from . import model
from . import schema

from passlib.context import CryptContext
from jose import JWTError, jwt
from typing import Optional
from datetime import datetime, timedelta
import requests
import time


CLAVE_SECRETA = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITMO = "HS256"

def decodeToken(token: str):
    return jwt.decode(token, CLAVE_SECRETA, algorithms=[ALGORITMO])

def getUserCorreo(db: Session, correo: str):
    response = requests.get("http://personal:8000/user/correo/"+str(correo))
    if response.json()["rol"]=="administrador":
        return model.Administrador(**response.json())
    if response.json()["rol"]=="conductor":
        return model.Conductor(**response.json())
    #return db.query(model.Usuario).filter(model.Usuario.correo == correo).first()


# Metodos GET

def getAutobus(db: Session, idAutobus: int):
    return db.query(model.Autobus).filter(model.Autobus.id == idAutobus).first()

def getRuta(db: Session, idRuta: int):
    return db.query(model.Ruta).filter(model.Ruta.id == idRuta).first()

def getAutobuses(db: Session, skip: int = 0, limit: int = 100):
    return db.query(model.Autobus).offset(skip).limit(limit).all()

def getRutas(db: Session, skip: int = 0, limit: int = 100):
    return db.query(model.Ruta).offset(skip).limit(limit).all()


# Metodos POST

def crearAutobus(db: Session, autobus: schema.AutobusBase):
    db_autobus = model.Autobus(**autobus.dict())
    db_autobus.asientosLibres = autobus.asientos
    db.add(db_autobus)
    db.commit()
    db.refresh(db_autobus)
    return db_autobus

def crearRuta(db: Session, ruta: schema.RutaBase):
    db_ruta = model.Ruta(**ruta.dict())
    ciudadesRuta = ruta.ciudades.split()
    numeroCiudadesRuta = 0
    for i in range(len(ciudadesRuta)):
        numeroCiudadesRuta = numeroCiudadesRuta+1
    db_ruta.numeroCiudades = numeroCiudadesRuta
    db.add(db_ruta)
    db.commit()
    db.refresh(db_ruta)
    return db_ruta


# Metodos PATCH

def updateAutobusAsientos(db: Session, idAutobus: int):
    autobus = getAutobus(db, idAutobus)
    if autobus.asientosLibres>0: autobus.asientosLibres = autobus.asientosLibres-1
    db.commit()
    db.refresh(autobus)

def updateAutobus(db: Session, idAutobus: int, newAutobus: schema.AutobusFull):
    db_autobus = getAutobus(db, idAutobus)
    update_data = newAutobus.dict(exclude_unset=True)
    for key in update_data:
        setattr(db_autobus, key, update_data[key])
    db.commit()
    db.refresh(db_autobus)
    return db_autobus


def updateRuta(db: Session, idRuta: int, newRuta: schema.RutaSet):
    db_ruta = getRuta(db, idRuta)
    update_data = newRuta.dict(exclude_unset=True)
    if newRuta.ciudades is not None:
        ciudadesRuta = newRuta.ciudades.split()
        db_ruta.numeroCiudades = len(ciudadesRuta)
    for key in update_data:
        setattr(db_ruta, key, update_data[key])
        db.commit()
        db.refresh(db_ruta)
    return db_ruta


# Metodos DELETE

def deleteAutobus(db: Session, idAutobus: int):
    autobus = getAutobus(db, idAutobus)
    print("AUTOBUS DELETE ", autobus)
    response = deleteViajesAutobus(db, idAutobus)
    if response==500:
        return 500
    db.delete(autobus)
    db.commit()

def deleteRuta(db: Session, idRuta: int):
    ruta = getRuta(db, idRuta)
    response = deleteViajesRuta(db, idRuta)
    if response==500:
        return 500
    db.delete(ruta)
    db.commit()

def deleteViajesAutobus(db: Session, idAutobus: int):
    requests.delete("http://billetes:8000/viajes/autobus/"+str(idAutobus)+"/borrar")

def deleteViajesRuta(db: Session, idRuta: int):
    requests.delete("http://billetes:8000/viajes/ruta/"+str(idRuta)+"/borrar")

def rollback(db: Session):
    db.rollback()