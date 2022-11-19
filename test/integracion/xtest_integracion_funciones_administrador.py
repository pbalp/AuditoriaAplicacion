from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pytest
from datetime import timedelta

import csv, sqlite3

from ..database import Base
from ..main import app, get_db
from .aux_func import setup_data
from ..crud import crearToken, getPasswordHash, getClientes

# Nuevo administrador que se va a registrar en el sistema
nuevo_admin = {"nombre": "Marina", "apellidos": "Méndez Granados", "dni": "71566429H", "correo": "marinamg@email.com", 
            "password": "marinamg", "telefono": "677741225", "rol": "administrador"}
id_admin = {"id": ""}

# Parámetros que van a ser modificados del administrador
set_admin = {"nombre": "Natalia", "apellidos": "Castro Jerez", "dni": "71562248I",
            "password": "nataliacj", "telefono": "622335840"}

# Administrador que va a iniciar sesión en la aplicación (administrador con id 1)
administrador = {"id": 1, "nombre": "Admin", "apellidos": "Admin Admin", "dni": "12345678A", "correo": "admin@email.com", 
            "password": "admin", "telefono": "641002835", "rol": "administrador"}

# Autobus que se va a añadir al sistema
nuevo_autobus = {"modelo": "Irizar", "asientos": 45}
id_autobus = {"id": -1}

# Ruta que se va a añadir al sistema
nueva_ruta = {"ciudades": "Coruña Oviedo Gijon Santander Bilbao"}
id_ruta = {"id": -1}

# Viaje que se va a añadir al sistema
nuevo_viaje = {"conductor": 3, "autobus": 2, "ruta": 4, "precio": 14.30}
id_viaje = {"id": -1}

# Clases erróneas
autobus_erroneo_0 = {"modelo": "Error", "asientos": 0}
autobus_erroneo_menor = {"modelo": "Error", "asientos": -45}

ruta_erronea = {"ciudades": ""}

viaje_erroneo = {"conductor": 3, "autobus": 2, "ruta": 4, "precio": -12.80}

campos_verificables = ["nombre", "apellidos", "dni", "correo", "telefono", "rol"]

def verificar_igualdad(user1, user2, campos=campos_verificables, exclude=[]):
    for k in campos:
        if k in exclude:
            continue
        assert user1[k] == user2[k]

# Función que simula el inicio de sesión de un usuario
def login(user, client):
    response = client.post(
        "/token",
        headers={"accept": "application/json", "Content-type": "application/x-www-form-urlencoded"},
        data={"grant_type": "", "username": user["correo"], "password": user["password"], "scope": "", 
            "client_id": "", "client_secret": ""}
    )
    token = response.json()["access_token"]
    return token

# Función en la que se registra y se modifica el nuevo administrador
def testCrearModificarAdministrador(setup_data):
    client=setup_data
    
    # Se crea el administrador
    response = client.post(
        "/administrador/nuevo",
        json=nuevo_admin
    )
    print(response.json())
    id_admin["id"] = response.json()["id"]
    assert response.status_code == 200
    verificar_igualdad(response.json(), nuevo_admin)

    # El administrador inicia sesión
    access_token = login(nuevo_admin, client)

    # Se muestra el perfil del nuevo administrador
    response = client.get(
        "/administradores/"+str(id_admin["id"])+"/perfil",
        headers={"Authorization": "Bearer "+access_token})
    assert response.status_code == 200
    verificar_igualdad(response.json(), nuevo_admin)

    # Se modifican los atributos del neuvo administrador
    response = client.patch(
        "/administrador/"+str(id_admin["id"])+"/editar",
        headers={"accept": "application/json", "Authorization": "Bearer "+access_token},
        json=set_admin
    )
    print("ID admin ", id_admin["id"])
    print("Response ", response.json())
    assert response.status_code == 200
    verificar_igualdad(response.json(), set_admin, exclude=["correo", "rol"])

    # Se elimina el nuevo administrador
    response = client.delete("/administrador/"+str(id_admin["id"])+"/borrar", 
        headers={"accept": "application/json", "Authorization": "Bearer "+access_token}
    )
    assert response.status_code == 200
    

# Función en la que el administrador ya registrado inicia sesión en la aplicación
def testCrearViaje(setup_data):
    client=setup_data

    # Se inicia la sesión del administrador
    access_token = login(administrador, setup_data)

    # Se crea un autobus erróneo cuyo número de asientos es igual a 0
    response = client.post(
        "/autobus/nuevo",
        headers={"accept": "application/json", "Authorization": "Bearer "+access_token},
        json=autobus_erroneo_0
    )
    assert response.status_code == 422

    # Se crea un autobus erróneo cuyo número de asientos es menor que 0
    response = client.post(
        "/autobus/nuevo",
        headers={"accept": "application/json", "Authorization": "Bearer "+access_token},
        json=autobus_erroneo_menor
    )
    assert response.status_code == 422

    # Se crea un autobus
    response = client.post(
        "/autobus/nuevo",
        headers={"accept": "application/json", "Authorization": "Bearer "+access_token},
        json=nuevo_autobus
    )
    id_autobus["id"] = response.json()["id"]
    assert response.status_code == 200
    verificar_igualdad(response.json(), nuevo_autobus, campos=["modelo", "asientos"])

    # Se crea una ruta que no tiene ciudades
    response = client.post(
        "/ruta/nueva",
        headers={"accept": "application/json", "Authorization": "Bearer "+access_token},
        json=ruta_erronea
    )
    assert response.status_code == 422

    # Se crea una ruta
    response = client.post(
        "/ruta/nueva",
        headers={"accept": "application/json", "Authorization": "Bearer "+access_token},
        json=nueva_ruta
    )
    id_ruta["id"] = response.json()["id"]
    assert response.status_code == 200
    verificar_igualdad(response.json(), nueva_ruta, campos=["ciudades"])
    assert response.json()["numeroCiudades"] == 5

    # Se crea un viaje cuyo precio tiene un valor negativo
    response = client.post(
        "/viaje/nuevo",
        headers={"accept": "application/json", "Authorization": "Bearer "+access_token},
        json=viaje_erroneo
    )
    assert response.status_code == 422

    # Se crea un viaje
    response = client.post(
        "/viaje/nuevo",
        headers={"accept": "application/json", "Authorization": "Bearer "+access_token},
        json=nuevo_viaje
    )
    id_viaje["id"] = response.json()["id"]
    print("Viaje ", response.json())
    assert response.status_code == 200
    verificar_igualdad(response.json(), nuevo_viaje, campos=["autobus", "conductor", "ruta", "precio"])

    # El autobus creado modifica el número de asientos a 0 y el número de asientos libres también
    response = client.patch(
        "/autobuses/"+str(id_autobus["id"])+"/editar",
        headers={"accept": "application/json", "Authorization": "Bearer "+access_token},
        json={"asientos": 0, "asientosLibres": 0}
    )
    print("Response ", response.json())
    assert response.status_code == 422

    # El autobus creado modifica el número de asientos por -45 y el número de asientos libres también
    response = client.patch(
        "/autobuses/"+str(id_autobus["id"])+"/editar",
        headers={"accept": "application/json", "Authorization": "Bearer "+access_token},
        json={"asientos": -45, "asientosLibres": -45}
    )
    print("Response ", response.json())
    assert response.status_code == 422

    # El autobus creado modifica el número de asientos por 50 y el número de asientos libres por 60
    response = client.patch(
        "/autobuses/"+str(id_autobus["id"])+"/editar",
        headers={"accept": "application/json", "Authorization": "Bearer "+access_token},
        json={"asientos": 50, "asientosLibres": 60}
    )
    print("Response ", response.json())
    assert response.status_code == 422

    # Se modifica el autobus creado
    response = client.patch(
        "/autobuses/"+str(id_autobus["id"])+"/editar",
        headers={"accept": "application/json", "Authorization": "Bearer "+access_token},
        json={"modelo": "Pegaso", "asientos": 60}
    )
    print("Response ", response.json())
    assert response.status_code == 200
    assert response.json()["modelo"] == "Pegaso"
    assert response.json()["asientos"] == 60

    # La ruta creada se modifica con un campos de ciudades vacío
    response = client.patch(
        "/rutas/"+str(id_ruta["id"])+"/editar",
        headers={"accept": "application/json", "Authorization": "Bearer "+access_token},
        json={"ciudades": ""}
    )
    assert response.status_code == 422

    # Se modifica la ruta creada
    response = client.patch(
        "/rutas/"+str(id_ruta["id"])+"/editar",
        headers={"accept": "application/json", "Authorization": "Bearer "+access_token},
        json={"ciudades": "Coruña Lugo Oviedo Gijon Santander Bilbao Vitoria"}
    )
    print("ID Ruta ", id_ruta["id"])
    print("Response ruta ", response.json())
    assert response.status_code == 200
    assert response.json()["ciudades"] == "Coruña Lugo Oviedo Gijon Santander Bilbao Vitoria"
    assert response.json()["numeroCiudades"] == 7

    # El viaje creado se modifica con el precio negativo
    response = client.patch(
        "/viajes/"+str(id_viaje["id"])+"/editar",
        headers={"accept": "application/json", "Authorization": "Bearer "+access_token},
        json={"precio": -14.80}
    )
    assert response.status_code == 422

    # Se modifica el viaje creado
    response = client.patch(
        "/viajes/"+str(id_viaje["id"])+"/editar",
        headers={"accept": "application/json", "Authorization": "Bearer "+access_token},
        json={"autobus": id_autobus["id"], "ruta": id_ruta["id"], "precio": 14.80}
    )
    assert response.status_code == 200
    verificar_igualdad(response.json(), {"autobus": id_autobus["id"], "ruta": id_ruta["id"], "precio": 14.80}, campos=["autobus", "ruta", "precio"])

    # Se elimina el autobus creado
    response = client.delete(
        "administrador/"+str(administrador["id"])+"/autobus/"+str(id_autobus["id"])+"/borrar",
        headers={"accept": "application/json", "Authorization": "Bearer "+access_token}
    )
    assert response.status_code == 200

    # Se elimina la ruta creada
    response = client.delete(
        "administrador/"+str(administrador["id"])+"/ruta/"+str(id_ruta["id"])+"/borrar",
        headers={"accept": "application/json", "Authorization": "Bearer "+access_token}
    )
    assert response.status_code == 200

    # Se elimina el viaje creado
    response = client.delete(
        "administrador/"+str(administrador["id"])+"/viaje/"+str(id_viaje["id"])+"/borrar",
        headers={"accept": "application/json", "Authorization": "Bearer "+access_token}
    )
    assert response.status_code == 200

# Funcion que comprueba que el administrador puede obtener los listados de todos los usuarios, rutas, autobuses y billetes
def testListasAdministrador(setup_data):
    client=setup_data

    # Se inicia la sesión del administrador
    access_token = login(administrador, setup_data)

    # Obtener un listado de todos los clientes de la aplicación
    response = client.get(
        "/clientes/",
        headers={"Authorization": "Bearer "+access_token})
    assert response.status_code == 200
    #verificar_igualdad(response.json(), nuevo_admin)

    # Obtener un listado de todos los conductores de la aplicación
    response = client.get(
        "/conductores/",
        headers={"Authorization": "Bearer "+access_token})
    assert response.status_code == 200
    #verificar_igualdad(response.json(), nuevo_admin)

    # Obtener un listado de todos los autobuses de la aplicación
    response = client.get(
        "/autobuses/",
        headers={"Authorization": "Bearer "+access_token})
    assert response.status_code == 200
    #verificar_igualdad(response.json(), nuevo_admin)

    # Obtener un listado de todos las rutas de la aplicación
    response = client.get(
        "/rutas/",
        headers={"Authorization": "Bearer "+access_token})
    assert response.status_code == 200
    #verificar_igualdad(response.json(), nuevo_admin)

    # Obtener un listado de todos los billetes de la aplicación
    response = client.get(
        "/billetes/",
        headers={"Authorization": "Bearer "+access_token})
    assert response.status_code == 200
    #verificar_igualdad(response.json(), nuevo_admin)