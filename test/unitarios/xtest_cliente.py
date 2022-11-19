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
from ..main import app, get_db
from ..crud import getPasswordHash, autenticarUsuario, crearToken
#import database.Base
#import main.app
#import main.get_db
#from .. import database, main

#import unittest

from .aux_func import setup_client

# Crear database
#SQLALCHEMY_DATABASE_URL = "mysql+pymysql://uo258740:rom31abi@localhost:3306/dbPruebas"
#SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"

#engine = create_engine(SQLALCHEMY_DATABASE_URL)
#TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

#Base.metadata.create_all(bind=engine)

#def override_get_db():
#    try:
#        db = TestingSessionLocal()
#        yield db
#    finally:
#        db.close()

#app.dependency_overrides[get_db] = override_get_db

#client = TestClient(app)

#token = ""
#response_header = {}

# Datos del usuario sobre el que se realizan las pruebas
datos_ejemplo = {"nombre": "ClienteTest1", "apellidos": "Cliente Test1", "dni": "12345678C", "correo": "clienteTest1@email.com", 
            "password": "test1", "telefono": "654987324", "rol": "cliente"}

# Campos del usuario que se han de verificar
campos_verificables = ["nombre", "apellidos", "dni", "correo", "telefono", "rol"]

# Función que verifica si dos JSON son iguales en los campos especificados
# saltándose los que se especifiquen en exclude
def verificar_igualdad(user1, user2, campos=campos_verificables, exclude=[]):
    for k in campos:
        if k in exclude:
            continue
        assert user1[k] == user2[k]


# Función que crea el cliente de ejemplo y lo inserta en la base de datos
def testCrearCliente(setup_client):
    client=setup_client
    response = client.post(
        "/cliente/nuevo",
        #headers={"accept": "application/json", "Content-type": "application/x-www-form-urlencoded"},
        json=datos_ejemplo
    )
    print(response.json())
    assert response.status_code == 200 or response.status_code == 400
    verificar_igualdad(response.json(), datos_ejemplo)

# Función que crea un cliente con el mismo dni que el cliente de ejemplo y lo inserta en la base de datos
def testCrearClienteMismoDNI(setup_client):
    client=setup_client
    response = client.post(
        "/cliente/nuevo",
        #headers={"accept": "application/json", "Content-type": "application/x-www-form-urlencoded"},
        json={"nombre": "ClienteTest2", "apellidos": "Cliente Test2", "dni": "12345678C", "correo": "clienteTest2@email.com", 
            "password": "test2", "telefono": "697410253", "rol": "cliente"}
    )
    print("Response ", response.json())
    assert response.status_code == 400

# Función que comprueba el inicio de sesión correcto del cliente de ejemplo
def testLoginCliente(setup_client):
    client=setup_client
    response = client.post(
        "/token",
        headers={"accept": "application/json", "Content-type": "application/x-www-form-urlencoded"},
        data={"grant_type": "", "username": datos_ejemplo["correo"], "password": datos_ejemplo["password"], "scope": "", 
            "client_id": "", "client_secret": ""}
    )
    print(response.json())
    response_header = {"Authorization": "Bearer "+response.json()["access_token"], "token_type": "bearer"}
    assert response.status_code == 200

# Función que comprueba que los datos del cliente de ejemplo son correctos
def testVerPerfil(setup_client):
    client=setup_client
    access_token_expires = timedelta(minutes=30)
    access_token = crearToken(
    data={"sub": datos_ejemplo["correo"], "rol": "cliente"}, expires_delta=access_token_expires)

    response = client.get(
        "/clientes/1/perfil",
        headers={"Authorization": "Bearer "+access_token})
    assert response.status_code == 200
    verificar_igualdad(response.json(), datos_ejemplo)

# Función que comprueba que el cliente que ha iniciado sesión no puede ver los datos de otro cliente
def testVerPerfilDistinto(setup_client):
    client=setup_client
    access_token_expires = timedelta(minutes=30)
    access_token = crearToken(
    data={"sub": datos_ejemplo["correo"], "rol": "cliente"}, expires_delta=access_token_expires)
    
    response = client.post(
        "/cliente/nuevo",
        #headers={"accept": "application/json", "Content-type": "application/x-www-form-urlencoded"},
        json={"nombre": "ClienteTest2", "apellidos": "Cliente Test2", "dni": "12345678F", "correo": "clienteTest2@email.com", 
            "password": "test2", "telefono": "697410253", "rol": "cliente"}
    )
    assert response.status_code == 200

    response = client.get(
        "/clientes/2/perfil",
        headers={"Authorization": "Bearer "+access_token})
    print(response.status_code)
    assert response.status_code == 401
    
# Función que comprueba los billetes que ha comprado el cliente que ha iniciado sesión
def testBilletesCliente(setup_client):
    client=setup_client
    access_token_expires = timedelta(minutes=30)
    access_token = crearToken(
    data={"sub": datos_ejemplo["correo"], "rol": "cliente"}, expires_delta=access_token_expires)

    response = client.get("/cliente/1/billetes/",
            headers={"Authorization": "Bearer "+access_token})
    assert response.status_code == 200
    assert response.json()==[]

def testDeleteClientes(setup_client):
    client=setup_client
    access_token_expires = timedelta(minutes=30)
    access_token = crearToken(
    data={"sub": datos_ejemplo["correo"], "rol": "cliente"}, expires_delta=access_token_expires)
    response = client.delete("/cliente/1/borrar",
            headers={"Authorization": "Bearer "+access_token})
    assert response.status_code == 200

    access_token = crearToken(
    data={"sub": "clienteTest2@email.com", "rol": "cliente"}, expires_delta=access_token_expires)
    response = client.delete("/cliente/2/borrar",
            headers={"Authorization": "Bearer "+access_token})
    assert response.status_code == 200
