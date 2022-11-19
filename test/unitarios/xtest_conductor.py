#import sys,os
#sys.path.append(os.path.join(os.path.dirname(__file__),os.pardir,"modeloDatos"))
#import myapplib

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import timedelta
import pytest

from ..database import Base
from ..main import app, get_db
from ..crud import getPasswordHash, autenticarUsuario, crearToken

from .aux_func import setup_client, setup_token, setup_login

# Datos del usuario sobre el que se realizan las pruebas
datos_ejemplo = {"nombre": "ConductorTest1", "apellidos": "Conductor Test1", "dni": "01234567A", "correo": "conductorTest1@email.com", 
            "password": "test1", "telefono": "639639639", "rol": "conductor"}
id_conductor = {"id": -1}

# Campos del usuario que se han de verificar
campos_verificables = ["nombre", "apellidos", "dni", "correo", "telefono", "rol"]

# Función que verifica si dos JSON son iguales en los campos especificados
# saltándose los que se especifiquen en exclude
def verificar_igualdad(user1, user2, campos=campos_verificables, exclude=[]):
    for k in campos:
        if k in exclude:
            continue
        assert user1[k] == user2[k]


# Función que inserta el conductor de datos_ejemplo en la base de datos
def testCrearConductor(setup_client):
    client = setup_client
    response = client.post(
        "/conductor/nuevo",
        #headers={"accept": "application/json", "Content-type": "application/x-www-form-urlencoded"},
        json=datos_ejemplo
    )
    print(response.json())
    id_conductor["id"] = response.json()["id"]
    assert response.status_code == 200 or response.status_code == 400
    verificar_igualdad(response.json(), datos_ejemplo)

# Función que comprueba el inicio de sesión correcto del conductor creado anteriormente
def testLoginConductor(setup_client):
    client = setup_client
    setup_login(datos_ejemplo["correo"], datos_ejemplo["password"], datos_ejemplo["rol"])

    response = client.post(
        "/token",
        headers={"accept": "application/json", "Content-type": "application/x-www-form-urlencoded"},
        data={"grant_type": "", "username": datos_ejemplo["correo"], "password": datos_ejemplo["password"], "scope": "", 
            "client_id": "", "client_secret": ""}
    )
    print(response.json())
    response_header = {"Authorization": "Bearer "+response.json()["access_token"], "token_type": "bearer"}
    assert response.status_code == 200

# Función que comprueba que los daltos del conductor son correctos
def testVerPerfil(setup_client, setup_token):
    client = setup_client
    access_token = setup_token

    response = client.get(
        "/conductores/"+str(id_conductor["id"])+"/perfil",
        headers={"Authorization": "Bearer "+access_token})
    assert response.status_code == 200
    verificar_igualdad(response.json(), datos_ejemplo)

# Función que comprueba los viajes asignados que tiene el conductor
def testViajesConductor(setup_client, setup_token):
    client = setup_client
    access_token = setup_token

    response = client.get("/conductor/"+str(id_conductor["id"])+"/viajes/",
            headers={"Authorization": "Bearer "+access_token})
    assert response.status_code == 200
    assert response.json()==[]

# Función que comprueba que el nombre del conductor se ha modificado correctamente
def testSetNombre(setup_client, setup_token):
    client = setup_client
    access_token = setup_token

    response = client.patch(
        "/conductores/"+str(id_conductor["id"])+"/editar",
        headers={"accept": "application/json", "Authorization": "Bearer "+access_token},
        json={"nombre": "ConductorCambio"}
    )
    print("Response ", response.json())
    print("ID Conductor ", id_conductor["id"])
    assert response.status_code == 200
    verificar_igualdad(response.json(), datos_ejemplo, exclude=["nombre"])
    assert response.json()["nombre"] == "ConductorCambio"
    datos_ejemplo["nombre"] = response.json()["nombre"]

# Función que comprueba que los apellidos del conductor se han modificado correctamente
def testSetApellidos(setup_client,setup_token):
    client = setup_client
    access_token = setup_token

    response = client.patch(
        "/conductores/"+str(id_conductor["id"])+"/editar",
        headers={"accept": "application/json", "Authorization": "Bearer "+access_token},
        json={"apellidos": "Conductor Cambio"}
    )
    assert response.status_code == 200
    verificar_igualdad(response.json(), datos_ejemplo, exclude=["apellidos"])
    assert response.json()["apellidos"] == "Conductor Cambio"
    datos_ejemplo["apellidos"] = response.json()["apellidos"]

# Función que comprueba que el dni del conductor se ha modificado correctamente
def testSetDNI(setup_client, setup_token):
    client = setup_client
    access_token = setup_token

    response = client.patch(
        "/conductores/"+str(id_conductor["id"])+"/editar",
        headers={"accept": "application/json", "Authorization": "Bearer "+access_token},
        json={"dni": "44332211C"}
    )
    assert response.status_code == 200
    verificar_igualdad(response.json(), datos_ejemplo, exclude=["dni"])
    assert response.json()["dni"] == "44332211C"
    datos_ejemplo["dni"] = response.json()["dni"]

# Función que comprueba que el dni del conductor no se modifica por un dni erróneo
def testSetDNIErroneo(setup_client, setup_token):
    client = setup_client
    access_token = setup_token

    response = client.patch(
        "/conductores/"+str(id_conductor["id"])+"/editar",
        headers={"accept": "application/json", "Authorization": "Bearer "+access_token},
        json={"dni": "112233449"}
    )
    assert response.status_code == 422

# Función que compriueba que el dni del conductor no se modifica por uno que no tiene letra
def testSetDNISinLetra(setup_client, setup_token):
    client = setup_client
    access_token = setup_token

    response = client.patch(
        "/conductores/"+str(id_conductor["id"])+"/editar",
        headers={"accept": "application/json", "Authorization": "Bearer "+access_token},
        json={"dni": "55332211"}
    )
    assert response.status_code == 422

# Función que comprueba que el conductor se elimina de la base de datos correctamente
def testDeleteConductor(setup_client, setup_token):
    client = setup_client
    access_token = setup_token

    response = client.delete("/conductor/"+str(id_conductor["id"])+"/borrar", 
        headers={"accept": "application/json", "Authorization": "Bearer "+access_token}
    )
    assert response.status_code == 200