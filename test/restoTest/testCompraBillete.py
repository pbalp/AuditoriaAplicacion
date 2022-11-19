from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ..database import Base
from ..main import app, get_db

import unittest

SQLALCHEMY_DATABASE_URL = "mysql+pymysql://uo258740:rom31abi@localhost:3306/dbPruebas"

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



def testCrearUsuario():
    response = client.post(
        "/cliente/nuevo/",
        #headers={"X-Token": "coneofsilence"},
        json={"nombre": "ClienteTest", "apellidos": "Comprar Billete", "dni": "12345678B", "correo": "clienteBillete@email.com", 
            "password": "billete", "telefono": "654987321", "rol": "cliente"}
    )
    assert response.status_code == 200
    #assert response.json() == {
    #    "nombre": "UsuarioTest", 
    #    "apellidos": "Comprar Billete", 
    #    "dni": "12345678B", 
    #    "correo": "usuarioBillete@email.com", 
    #    "contraseña": "billete", 
    #    "telefono": "654987321"
    #}

def testCrearConductor():
    response = client.post(
        "/conductor/nuevo/",
        #headers={"X-Token": "coneofsilence"},
        json={"nombre": "ConductorTest", "apellidos": "Comprar Billete", "dni": "12345678D", "correo": "conductorBillete@email.com", 
            "contraseña": "billete", "telefono": "639528417", "rol": }
    )
    assert response.status_code == 200
    #assert response.json() == {
    #    "nombre": "ConductorTest", 
    #    "apellidos": "Comprar Billete", 
    #    "dni": "12345678D", 
    #    "correo": "conductorBillete@email.com", 
    #    "contraseña": "billete", 
    #    "telefono": "639528417"
    #}

def testCrearAutobus():
    response = client.post(
        "/autobus/",
        #headers={"X-Token": "coneofsilence"},
        json={"modelo": "AutobusBillete", "asientosLibres": "45"}
    )
    assert response.status_code == 200
    assert response.json() == {
        "modelo": "AutobusBillete", 
        "asientosLibres": "45"
    }
