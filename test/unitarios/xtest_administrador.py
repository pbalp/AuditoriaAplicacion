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

#import unittest

from .aux_func import setup_client, setup_token, setup_login

# IDs de todos los datos de ejemplo
ids_ejemplo = {"admin": 0, "conductor1": 0, "conductor2": 0, "ruta1": 0, "ruta2": 0, "autobus1": 0, "autobus2": 0, "viaje1": 0, "viaje2": 0}

# Datos de los usuarios sobre los que se realizan las pruebas
# Conductores
conductor_ejemplo1 = {"nombre": "ConductorLista1", "apellidos": "Conductor Lista1", "dni": "01234567A", "correo": "conductorLista1@email.com", 
            "password": "lista1", "telefono": '666333999', "rol": "conductor"}
conductor_ejemplo2 = {"nombre": "ConductorLista2", "apellidos": "Conductor Lista2", "dni": "01234567B", "correo": "conductorLista2@email.com", 
            "password": "lista2", "telefono": "666222888", "rol": "conductor"}

# Administrador
admin_ejemplo = {"nombre": "AdminTest", "apellidos": "Admin Test", "dni": "00123456A", "correo": "administradorTest@email.com", 
            "password": "test", "telefono": "663399852", "rol": "administrador"}

# Rutas
ruta_ejemplo1 = {"ciudades": "Gijon Oviedo Leon Madrid"}
ruta_ejemplo2 = {"ciudades": "Valencia Alicante Murcia"}

# Autobuses
autobus_ejemplo1 = {"modelo": "AutobusTest1", "asientos": 45}
autobus_ejemplo2 = {"modelo": "AutobusTest2", "asientos": 35}

# Viajes
viaje_ejemplo1 = {"conductor": 1, "autobus": 1, "ruta": 1, "precio": 12.50}
viaje_ejemplo2 = {"conductor": 2, "autobus": 2, "ruta": 2, "precio": 11.00} 

# Campos del usuario que se han de verificar
campos_verificables = ["nombre", "apellidos", "dni", "correo", "telefono", "rol"]

# Función que verifica si dos JSON son iguales en los campos especificados
# saltándose los que se especifiquen en exclude
def verificar_igualdad(user1, user2, campos=campos_verificables, exclude=[]):
    for k in campos:
        if k in exclude:
            continue
        assert user1[k] == user2[k]

# Función que crea la lista conductor_ejemplo1
def testCrearConductor1(setup_client):
    client=setup_client
    response = client.post(
        "/conductor/nuevo",
        #headers={"accept": "application/json", "Content-type": "application/x-www-form-urlencoded"},
        json=conductor_ejemplo1
    )
    assert response.status_code == 200
    verificar_igualdad(response.json(), conductor_ejemplo1)
    ids_ejemplo["conductor1"] = response.json()["id"]

# Función que crea la lista conductor_ejemplo2
def testCrearConductor2(setup_client):
    client=setup_client
    response = client.post(
        "/conductor/nuevo",
        #headers={"accept": "application/json", "Content-type": "application/x-www-form-urlencoded"},
        json=conductor_ejemplo2
    )
    assert response.status_code == 200
    verificar_igualdad(response.json(), conductor_ejemplo2)
    ids_ejemplo["conductor2"] = response.json()["id"]

# Función que crea la lista admin_ejemplo
def testCrearAdministrador(setup_client):
    client=setup_client
    response = client.post(
        "/administrador/nuevo",
        #headers={"accept": "application/json", "Content-type": "application/x-www-form-urlencoded"},
        json=admin_ejemplo
    )
    assert response.status_code == 200
    verificar_igualdad(response.json(), admin_ejemplo)
    ids_ejemplo["admin"] = response.json()["id"]

# Función que comprueba el inicio de sesión del administrador admin_ejemplo
def testLoginAdministrador(setup_client):
    client=setup_client
    setup_login(admin_ejemplo["correo"], admin_ejemplo["password"], admin_ejemplo["rol"])
    response = client.post(
        "/token",
        headers={"accept": "application/json", "Content-type": "application/x-www-form-urlencoded"},
        data={"grant_type": "", "username": admin_ejemplo["correo"], "password": admin_ejemplo["password"], "scope": "", 
            "client_id": "", "client_secret": ""}
    )
    assert response.status_code == 200

# Función que crea la lista ruta_ejemplo1
def testCrearRuta1(setup_client, setup_token):
    client=setup_client
    access_token = setup_token

    response = client.post(
        "/ruta/nueva",
        headers={"accept": "application/json", "Authorization": "Bearer "+access_token},
        json=ruta_ejemplo1
    )
    assert response.status_code == 200
    verificar_igualdad(response.json(), ruta_ejemplo1, campos=["ciudades"])
    ids_ejemplo["ruta1"] = response.json()["id"]

# Función que crea la lista ruta_ejemplo2
def testCreaRuta2(setup_client, setup_token):
    client=setup_client
    access_token = setup_token

    response = client.post(
        "/ruta/nueva",
        headers={"accept": "application/json", "Authorization": "Bearer "+access_token},
        json=ruta_ejemplo2
    )
    assert response.status_code == 200
    verificar_igualdad(response.json(), ruta_ejemplo2, campos=["ciudades"])
    ids_ejemplo["ruta2"] = response.json()["id"]

# Función que crea la lista autobus_ejemplo1
def testCrearAutobus1(setup_client,setup_token):
    client=setup_client
    access_token = setup_token

    response = client.post(
        "/autobus/nuevo",
        headers={"accept": "application/json", "Authorization": "Bearer "+access_token},
        json=autobus_ejemplo1
    )
    assert response.status_code == 200
    verificar_igualdad(response.json(), autobus_ejemplo1, campos=["modelo", "asientos"], exclude=["asientosLibres"])
    ids_ejemplo["autobus1"] = response.json()["id"]

# Función que crea la lista autobus_ejemplo2
def testCrearAutobus2(setup_client, setup_token):
    client=setup_client
    access_token = setup_token

    response = client.post(
        "/autobus/nuevo",
        headers={"accept": "application/json", "Authorization": "Bearer "+access_token},
        json=autobus_ejemplo2
    )
    assert response.status_code == 200
    verificar_igualdad(response.json(), autobus_ejemplo2, campos=["modelo", "asientos"], exclude=["asientosLibres"])
    ids_ejemplo["autobus2"] = response.json()["id"]

# Función que crea la lista viaje_ejemplo1
def testCrearViaje1(setup_client, setup_token):
    client=setup_client
    access_token = setup_token

    response = client.post(
        "/viaje/nuevo",
        headers={"accept": "application/json", "Authorization": "Bearer "+access_token},
        json=viaje_ejemplo1
    )
    assert response.status_code == 200
    verificar_igualdad(response.json(), viaje_ejemplo1, campos=["conductor", "autobus", "ruta", "precio"])
    ids_ejemplo["viaje1"] = response.json()["id"]

# Función que crea la lista viaje_ejemplo2
def testCrearViaje2(setup_client, setup_token):
    client=setup_client
    access_token = setup_token

    response = client.post(
        "/viaje/nuevo",
        headers={"accept": "application/json", "Authorization": "Bearer "+access_token},
        json=viaje_ejemplo2
    )
    assert response.status_code == 200
    verificar_igualdad(response.json(), viaje_ejemplo2, campos=["conductor", "autobus", "ruta", "precio"])
    ids_ejemplo["viaje2"] = response.json()["id"]

# Función que devuelve al administrador la lista de los conductores registrados en la aplicación
def testGetConductores(setup_client, setup_token):
    client=setup_client
    access_token = setup_token

    response = client.get(
        "/conductores/",
        headers={"accept": "application/json", "Authorization": "Bearer "+access_token}
    )
    assert response.status_code == 200
    conductores = {"conductor_ejemplo1": conductor_ejemplo1, "conductor_ejemplo2": conductor_ejemplo2}
    array_conductores = ["conductor_ejemplo1", "conductor_ejemplo2"]
    cont = 0
    for conductor in response.json():
        verificar_igualdad(conductor, conductores[array_conductores[cont]], campos=campos_verificables, exclude=["id"])
        cont = cont+1

# Función que devuelve al administrador la lista de las rutas creadas en la aplicación
def testGetRutas(setup_client, setup_token):
    client=setup_client
    access_token = setup_token

    response = client.get(
        "/rutas/",
        headers={"accept": "application/json", "Authorization": "Bearer "+access_token}
    )
    assert response.status_code == 200
    rutas = {"ruta_ejemplo1": ruta_ejemplo1, "ruta_ejemplo2": ruta_ejemplo2}
    array_rutas = ["ruta_ejemplo1", "ruta_ejemplo2"]
    array_ciudades = [4, 3]
    cont = 0
    for ruta in response.json():
        verificar_igualdad(ruta, rutas[array_rutas[cont]], campos={"ciudades"}, exclude=["id", "numeroCiudades"])
        assert ruta["numeroCiudades"] == array_ciudades[cont]
        cont = cont+1

# Función que elimina del sistema el viaje viaje_ejemplo1
def testDeleteViaje1(setup_client, setup_token):
    client=setup_client
    access_token = setup_token

    response = client.delete(
        "/administrador/"+str(ids_ejemplo["admin"])+"/viaje/"+str(ids_ejemplo["viaje1"])+"/borrar",
        headers={"accept": "application/json", "Authorization": "Bearer "+access_token}
    )
    assert response.status_code == 200

# Función que elimina del sistema el viaje viaje_ejemplo2
def testDeleteViaje2(setup_client, setup_token):
    client=setup_client
    access_token = setup_token

    response = client.delete(
        "/administrador/"+str(ids_ejemplo["admin"])+"/viaje/"+str(ids_ejemplo["viaje2"])+"/borrar",
        headers={"accept": "application/json", "Authorization": "Bearer "+access_token}
    )
    assert response.status_code == 200

# Función que elimina del sistema la ruta ruta_ejemplo1
def testDeleteRuta1(setup_client, setup_token):
    client=setup_client
    access_token = setup_token

    response = client.delete(
        "/administrador/"+str(ids_ejemplo["admin"])+"/ruta/"+str(ids_ejemplo["ruta1"])+"/borrar",
        headers={"accept": "application/json", "Authorization": "Bearer "+access_token}
    )
    assert response.status_code == 200

# Función que elimina del sistema la ruta ruta_ejemplo2
def testDeleteRuta2(setup_client, setup_token):
    client=setup_client
    access_token = setup_token

    response = client.delete(
        "/administrador/"+str(ids_ejemplo["admin"])+"/ruta/"+str(ids_ejemplo["ruta2"])+"/borrar",
        headers={"accept": "application/json", "Authorization": "Bearer "+access_token}
    )
    assert response.status_code == 200

# Función que elimina del sistema el autobus autobus_ejemplo1
def testDeleteAutobus1(setup_client, setup_token):
    client=setup_client
    access_token = setup_token

    response = client.delete(
        "/administrador/"+str(ids_ejemplo["admin"])+"/autobus/"+str(ids_ejemplo["autobus1"])+"/borrar",
        headers={"accept": "application/json", "Authorization": "Bearer "+access_token}
    )
    assert response.status_code == 200

# Función que elimina del sistema el autobus autobus_ejemplo2
def testDeleteAutobus2(setup_client, setup_token):
    client=setup_client
    access_token = setup_token

    response = client.delete(
        "/administrador/"+str(ids_ejemplo["admin"])+"/autobus/"+str(ids_ejemplo["autobus2"])+"/borrar",
        headers={"accept": "application/json", "Authorization": "Bearer "+access_token}
    )
    assert response.status_code == 200

# Función que elimina del sistema el administrador admin_ejemplo
def testDeleteAdministrador(setup_client, setup_token):
    client=setup_client
    access_token = setup_token

    response = client.delete(
        "/administrador/"+str(ids_ejemplo["admin"])+"/borrar",
        headers={"accept": "application/json", "Authorization": "Bearer "+access_token}
    )
    print("Reponse json Delete Admin ", response.json())
    assert response.status_code == 200

# Función que inicia la sesión del conductor conductor_ejemplo1
def testLoginConductor1(setup_client):
    client=setup_client
    setup_login(conductor_ejemplo1["correo"], conductor_ejemplo1["password"], conductor_ejemplo1["rol"])
    response = client.post(
        "/token",
        headers={"accept": "application/json", "Content-type": "application/x-www-form-urlencoded"},
        data={"grant_type": "", "username": conductor_ejemplo1["correo"], "password": conductor_ejemplo1["password"], "scope": "", 
            "client_id": "", "client_secret": ""}
    )
    assert response.status_code == 200

# Función que elimina del sistema el conductor conductor_ejemplo1
def testDeleteConductor1(setup_client, setup_token):
    client=setup_client
    access_token = setup_token

    response = client.delete(
        "/conductor/"+str(ids_ejemplo["conductor1"])+"/borrar",
        headers={"accept": "application/json", "Authorization": "Bearer "+access_token}
    )
    print("Reponse json Delete Conductor1 ", response.json())
    assert response.status_code == 200

# Función que inicia la sesión del conductor conductor_ejemplo2
def testLoginConductor2(setup_client):
    client=setup_client
    setup_login(conductor_ejemplo2["correo"], conductor_ejemplo2["password"], conductor_ejemplo2["rol"])
    response = client.post(
        "/token",
        headers={"accept": "application/json", "Content-type": "application/x-www-form-urlencoded"},
        data={"grant_type": "", "username": conductor_ejemplo2["correo"], "password": conductor_ejemplo2["password"], "scope": "", 
            "client_id": "", "client_secret": ""}
    )
    assert response.status_code == 200

# Función que elimina del sistema el conductor conductor_ejemplo2
def testDeleteConductor2(setup_client, setup_token):
    client=setup_client
    setup_login(conductor_ejemplo2["correo"], conductor_ejemplo2["password"], conductor_ejemplo2["rol"])
    access_token = setup_token

    response = client.delete(
        "/conductor/"+str(ids_ejemplo["conductor2"])+"/borrar",
        headers={"accept": "application/json", "Authorization": "Bearer "+access_token}
    )
    print("Reponse json Delete Conductor2 ", response.json())
    assert response.status_code == 200

