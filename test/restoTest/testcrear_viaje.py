#import sys,os
#sys.path.append(os.path.join(os.path.dirname(__file__),os.pardir,"modeloDatos"))
#import myapplib

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import timedelta
import pytest

#from .. import database, main, crud
from ..database import Base
rom ..main import app, get_db
#from ..crud import getPasswordHash, autenticarUsuario, crearToken
#import database.Base
#import main.app
#import main.get_db
#from .. import database, main
from aux_func import setup_client

#import unittest

# Crear database
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://uo258740:rom31abi@localhost:3306/dbPruebas"
#SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

def testCrearConductor():
    response = client.post(
        "/conductor/nuevo",
        #headers={"accept": "application/json", "Content-type": "application/x-www-form-urlencoded"},
        json={"nombre": "ConductorTest", "apellidos": "Conductor Billete", "dni": "01234567C", "correo": "conductorBillete@email.com", 
            "password": "billete", "telefono": "682031147", "rol": "conductor"}
    )
    print(response.json())
    assert response.status_code == 200 or response.status_code == 400

def testCrearAdministrador():
    response = client.post(
        "/administrador/nuevo",
        #headers={"accept": "application/json", "Content-type": "application/x-www-form-urlencoded"},
        json={"nombre": "AdminTest", "apellidos": "Admin Billete", "dni": "00123456A", "correo": "administradorBillete@email.com", 
            "password": "billete", "telefono": "663332589", "rol": "administrador"}
    )
    print(response.json())
    assert response.status_code == 200 or response.status_code == 400

def testLoginAdministrador():
    response = client.post(
        "/token",
        headers={"accept": "application/json", "Content-type": "application/x-www-form-urlencoded"},
        data={"grant_type": "", "username": "administradorBillete@email.com", "password": "billete", "scope": "", 
            "client_id": "", "client_secret": ""}
    )
    print(response.json())
    response_header = {"Authorization": "Bearer "+response.json()["access_token"], "token_type": "bearer"}
    assert response.status_code == 200

def testCrearAutobus():
    access_token_expires = timedelta(minutes=30)
    access_token = crearToken(
    data={"sub": "administradorBillete@email.com", "rol": "administrador"}, expires_delta=access_token_expires)

    response = client.post(
        "/ruta/nueva",
        headers={"accept": "application/json", "Authorization": "Bearer "+access_token},
        json={"ciudades": "Gijon Oviedo Leon Madrid"}
    )
    assert response.status_code == 200

#@pytest.fixture()
def testCrearRuta(): #db: sessionmaker
    #if autenticarUsuario(db, "administradorBillete@email.com", "billete"):
    access_token_expires = timedelta(minutes=30)
    access_token = crearToken(
    data={"sub": "administradorBillete@email.com", "rol": "administrador"}, expires_delta=access_token_expires)

    response = client.post(
        "/autobus/nuevo",
        headers={"accept": "application/json", "Authorization": "Bearer "+access_token},
        json={"modelo": "AutobusBillete", "asientos": "40"}
    )
    assert response.status_code == 200

#@pytest.fixture()
def testCrearViaje(): #db: sessionmaker
    #if autenticarUsuario(db, "administradorBillete@email.com", "billete"):
    access_token_expires = timedelta(minutes=30)
    access_token = crearToken(
    data={"sub": "administradorBillete@email.com", "rol": "administrador"}, expires_delta=access_token_expires)

    response = client.post(
        "/viaje/nuevo",
        headers={"accept": "application/json", "Authorization": "Bearer "+access_token},
        json={"conductor": "2", "autobus": "1", "ruta": "1", "precio": "10.50"}
    )
    assert response.status_code == 200

