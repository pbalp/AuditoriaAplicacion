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
#from .. import database, main # Hacer test de integracion (los test de las historias de usuario)

from .aux_func import setup_client

#import unittest

# Datos del usuario sobre el que se realizan las pruebas
datos_ejemplo = {"nombre": "UsuarioTestSet", "apellidos": "Usuario Set", "dni": "12345678S", "correo": "usuarioSet@email.com", 
            "password": "set", "telefono": "666555444", "rol": "cliente"}

# Campos del usuario que se han de verificar
campos_verificables = ["nombre", "apellidos", "dni", "correo", "telefono", "rol"]

# Función que verifica si dos JSON son iguales en los campos especificados
# saltándose los que se especifiquen en exclude
def verificar_igualdad(user1, user2, campos=campos_verificables, exclude=[]):
    for k in campos:
        if k in exclude:
            continue
        assert user1[k] == user2[k]

# Función que añade el cliente creado a la base de datos
def testCrearCliente(setup_client):
    client = setup_client
    response = client.post(
        "/cliente/nuevo",
        #headers={"accept": "application/json", "Content-type": "application/x-www-form-urlencoded"},
        json=datos_ejemplo
    )
    print(response.json())
    assert response.status_code == 200 or response.status_code == 400
    verificar_igualdad(response.json(), datos_ejemplo)

# Función que comprueba el inicio de sesión correcto del cliente
def testLoginCliente(setup_client):
    client = setup_client
    response = client.post(
        "/token",
        headers={"accept": "application/json", "Content-type": "application/x-www-form-urlencoded"},
        data={"grant_type": "", "username": datos_ejemplo["correo"], "password": datos_ejemplo["password"], 
        "scope": "", "client_id": "", "client_secret": ""}
    )
    print(response.json())
    response_header = {"Authorization": "Bearer "+response.json()["access_token"], "token_type": "bearer"}
    assert response.status_code == 200

# Función que modifica el nombre del cliente y comprueba que se ha modificado correctamente
def testSetNombre(setup_client):
    client = setup_client
    access_token_expires = timedelta(minutes=30)
    access_token = crearToken(
    data={"sub": datos_ejemplo["correo"], "rol": "cliente"}, expires_delta=access_token_expires)

    response = client.patch(
        "/clientes/1/editar",
        headers={"accept": "application/json", "Authorization": "Bearer "+access_token},
        json={"nombre": "UsuarioCambio"}
    )
    print("Response ", response.content)
    assert response.status_code == 200
    verificar_igualdad(response.json(), datos_ejemplo, exclude=["nombre"])
    datos_ejemplo["nombre"] = response.json()["nombre"]

# Función que modifica los apellidos del cliente y comprueba que se han modificado correctamente
def testSetApellidos(setup_client):
    client = setup_client
    access_token_expires = timedelta(minutes=30)
    access_token = crearToken(
    data={"sub": datos_ejemplo["correo"], "rol": "cliente"}, expires_delta=access_token_expires)

    response = client.patch(
        "/clientes/1/editar",
        headers={"accept": "application/json", "Authorization": "Bearer "+access_token},
        json={"apellidos": "Usuario Cambio"}
    )
    print("Response ", response.content)
    assert response.status_code == 200
    verificar_igualdad(response.json(), datos_ejemplo, exclude=["apellidos"])
    datos_ejemplo["apellidos"] = response.json()["apellidos"]

# Función que modifica el dni del cliente y comprueba que se ha modificado correctamente
def testSetDNI(setup_client):
    client = setup_client
    access_token_expires = timedelta(minutes=30)
    access_token = crearToken(
    data={"sub": datos_ejemplo["correo"], "rol": "cliente"}, expires_delta=access_token_expires)

    response = client.patch(
        "/clientes/1/editar",
        headers={"accept": "application/json", "Authorization": "Bearer "+access_token},
        json={"dni": "87654321S"}
    )
    print("Response ", response.content)
    assert response.status_code == 200
    verificar_igualdad(response.json(), datos_ejemplo, exclude=["dni"])
    datos_ejemplo["dni"] = response.json()["dni"]

# Función que modifica el dni del cliente por un dni con la letra en mitad de la cadena (erróneo)
def testSetDNIErroneo(setup_client):
    client = setup_client
    access_token_expires = timedelta(minutes=30)
    access_token = crearToken(
    data={"sub": datos_ejemplo["correo"], "rol": "cliente"}, expires_delta=access_token_expires)

    response = client.patch(
        "/clientes/1/editar",
        headers={"accept": "application/json", "Authorization": "Bearer "+access_token},
        json={"dni": "12345L78"}
    )
    assert response.status_code == 422

# Función que modifica el dni del cliente por un dni sin letra (erróneo)
def testSetDNISinLetra(setup_client):
    client = setup_client
    access_token_expires = timedelta(minutes=30)
    access_token = crearToken(
    data={"sub": datos_ejemplo["correo"], "rol": "cliente"}, expires_delta=access_token_expires)

    response = client.patch(
        "/clientes/1/editar",
        headers={"accept": "application/json", "Authorization": "Bearer "+access_token},
        json={"dni": "12345678"}
    )
    print("Response ", response.content)
    assert response.status_code == 422

# Función que elimina al cliente de la base de datos
def testDeleteCliente(setup_client):
    client = setup_client
    access_token_expires = timedelta(minutes=30) #A traves de patch no se cambia la contraseña, se cambia por otro mecanismo
    access_token = crearToken( #Cuando cambia la contraseña se invalida la sesion para iniciar sesion otra vez
    data={"sub": datos_ejemplo["correo"], "rol": "cliente"}, expires_delta=access_token_expires) #Comprobar el flujo de la sesion

    response = client.delete("/cliente/1/borrar", 
        headers={"accept": "application/json", "Authorization": "Bearer "+access_token}
    )
    assert response.status_code == 200
    