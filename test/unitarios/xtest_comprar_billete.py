from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import timedelta, datetime
import pytest

from ..database import Base
from ..main import app, get_db
from ..crud import getPasswordHash, autenticarUsuario, crearToken
from .aux_func import setup_client, setup_login, setup_token


# Datos de los usuarios sobre los que se realizan las pruebas
cliente_ejemplo = {"nombre": "ClienteBillete", "apellidos": "Cliente Billete", "dni": "11223344A", "correo": "clienteBillete@email.com", 
            "password": "billete", "telefono": "666666666", "rol": "cliente"} #666333999

admin_ejemplo = {"id": -1, "nombre": "AdminBillete", "apellidos": "Admin Billete", "dni": "11223344B", "correo": "adminBillete@email.com", 
            "password": "billete", "telefono": "666666666", "rol": "administrador"}

conductor_ejemplo = {"id": -1, "nombre": "ConductorBillete", "apellidos": "Conductor Billete", "dni": "11223344C", "correo": "conductorBillete@email.com", 
            "password": "billete", "telefono": "666666666", "rol": "conductor"}

autobus_ejemplo = {"modelo": "autobusBillete", "asientos": 45}

autobus_ejemplo_lleno = {"modelo": "autobusLleno", "asientos": 1}

ruta_ejemplo = {"ciudades": "Salamanca Zamora Leon"}

viaje_ejemplo = {"conductor": 1, "autobus": 1, "ruta": 1, "precio": 11.60}

# Billete que el usuario va a comprar
billete_ejemplo = {"cliente": -1, "viaje": 1, "fechaSalida": "2022-05-08T10:30:00", 
        "fechaLlegada": "2022-05-08T14:30:00", "asiento": 20}

# id que el usuario va a tener una vez se haya creado
id_billete = {"id": "-1"}

# Campos del usuario que se han de verificar
campos_verificables = ["nombre", "apellidos", "dni", "correo", "telefono", "rol"]

# Campos del billete que se han de verificar
campos_billete = ["cliente", "viaje", "fechaSalida", "fechaLlegada", "asiento"]

# Función que verifica si dos JSON son iguales en los campos especificados
# saltándose los que se especifiquen en exclude
def verificar_igualdad(user1, user2, campos=campos_verificables, exclude=[]):
    for k in campos:
        if k in exclude:
            continue
        assert user1[k] == user2[k]



def testCrearAdministrador(setup_client):
    client=setup_client
    response = client.post(
        "/administrador/nuevo",
        #headers={"accept": "application/json", "Content-type": "application/x-www-form-urlencoded"},
        json=admin_ejemplo
    )
    print(response.json())
    assert response.status_code == 200 or response.status_code == 400
    admin_ejemplo["id"] = response.json()["id"]
    verificar_igualdad(response.json(), admin_ejemplo, exclude=["id"])

def testCrearConductor(setup_client):
    client=setup_client
    response = client.post(
        "/conductor/nuevo",
        #headers={"accept": "application/json", "Content-type": "application/x-www-form-urlencoded"},
        json=conductor_ejemplo
    )
    print(response.json())
    assert response.status_code == 200 or response.status_code == 400
    conductor_ejemplo["id"] = response.json()["id"]
    verificar_igualdad(response.json(), conductor_ejemplo, exclude=["telefono"])

def testLoginAdmin(setup_client):
    client=setup_client
    #token = 
    setup_login(admin_ejemplo["correo"], admin_ejemplo["password"], admin_ejemplo["rol"])
    #print("Token Login Admin ", token)
    response = client.post(
        "/token",
        headers={"accept": "application/json", "Content-type": "application/x-www-form-urlencoded"},
        data={"grant_type": "", "username": admin_ejemplo["correo"], "password": admin_ejemplo["password"], "scope": "", 
            "client_id": "", "client_secret": ""}
    )
    print(response.json())
    
    #response_header = {"Authorization": "Bearer "+response.json()["access_token"], "token_type": "bearer"}
    

def testCrearAutobus(setup_client, setup_token):
    client=setup_client
    #access_token_expires = timedelta(minutes=30)
    #access_token = crearToken(
    #data={"sub": admin_ejemplo["correo"], "rol": admin_ejemplo["rol"]}, expires_delta=access_token_expires)

    access_token=setup_token
    print("Access Token ", access_token)
    response = client.post(
        "/autobus/nuevo",
        headers={"accept": "application/json", "Authorization": "Bearer "+access_token},
        json=autobus_ejemplo
    )
    print("Autobus ", response.json())
    assert response.status_code == 200 or response.status_code ==400
    verificar_igualdad(response.json(), autobus_ejemplo, campos=["modelo", "asientos"])

def testCrearAutobusLleno(setup_client, setup_token):
    client=setup_client
    #access_token_expires = timedelta(minutes=30)
    #access_token = crearToken(
    #data={"sub": admin_ejemplo["correo"], "rol": admin_ejemplo["rol"]}, expires_delta=access_token_expires)

    access_token=setup_token
    print("Access Token ", access_token)
    response = client.post(
        "/autobus/nuevo",
        headers={"accept": "application/json", "Authorization": "Bearer "+access_token},
        json=autobus_ejemplo_lleno
    )
    assert response.status_code == 200 or response.status_code == 400
    verificar_igualdad(response.json(), autobus_ejemplo_lleno, campos=["modelo", "asientos"])

def testCrearRuta(setup_client, setup_token):
    client=setup_client
    #access_token_expires = timedelta(minutes=30)
    #access_token = crearToken(
    #data={"sub": admin_ejemplo["correo"], "rol": admin_ejemplo["rol"]}, expires_delta=access_token_expires)

    access_token=setup_token
    response = client.post(
        "/ruta/nueva",
        headers={"accept": "application/json", "Authorization": "Bearer "+access_token},
        json=ruta_ejemplo
    )
    assert response.status_code == 200 or response.status_code ==400
    verificar_igualdad(response.json(), ruta_ejemplo, campos=["ciudades"])
    assert response.json()["numeroCiudades"] == 3

def testCrearViaje(setup_client, setup_token):
    client=setup_client
    #access_token_expires = timedelta(minutes=30)
    #access_token = crearToken(
    #data={"sub": admin_ejemplo["correo"], "rol": admin_ejemplo["rol"]}, expires_delta=access_token_expires)

    access_token=setup_token
    response = client.post(
        "/viaje/nuevo",
        headers={"accept": "application/json", "Authorization": "Bearer "+access_token},
        json=viaje_ejemplo
    )
    print("Viaje ", response.json())
    assert response.status_code == 200 or response.status_code ==400
    verificar_igualdad(response.json(), viaje_ejemplo, campos=["autobus", "conductor", "ruta", "precio"])
    

def testCrearCliente(setup_client):
    client=setup_client
    response = client.post(
        "/cliente/nuevo",
        #headers={"accept": "application/json", "Content-type": "application/x-www-form-urlencoded"},
        json=cliente_ejemplo
    )
    print(response.json())
    billete_ejemplo["cliente"] = response.json()["id"]
    id_cliente = billete_ejemplo["cliente"]
    print("id Cliente ", id_cliente)
    assert response.status_code == 200 or response.status_code == 400
    verificar_igualdad(response.json(), cliente_ejemplo)

def testLoginCliente(setup_client):
    client=setup_client
    #token = 
    setup_login(cliente_ejemplo["correo"], cliente_ejemplo["password"], cliente_ejemplo["rol"])
    #print("Token Login Cliente ", token)
    response = client.post(
        "/token",
        headers={"accept": "application/json", "Content-type": "application/x-www-form-urlencoded"},
        data={"grant_type": "", "username": cliente_ejemplo["correo"], "password": cliente_ejemplo["password"], "scope": "", 
            "client_id": "", "client_secret": ""}
    )
    print(response.json())
    response_header = {"Authorization": "Bearer "+response.json()["access_token"], "token_type": "bearer"}
    
    assert response.status_code == 200

def testComprarBillete(setup_client, setup_token):
    client=setup_client
    #access_token_expires = timedelta(minutes=30)
    #access_token = crearToken(
    #data={"sub": cliente_ejemplo["correo"], "rol": "cliente"}, expires_delta=access_token_expires)
    
    access_token=setup_token
    response = client.post(
        "/billete/nuevo",
        headers={"accept": "application/json", "Authorization": "Bearer "+access_token},
        json=billete_ejemplo
    )
    assert response.status_code == 200
    id_billete["id"] = response.json()["id"]
    print("id billete ", id_billete["id"])
    verificar_igualdad(response.json(), billete_ejemplo, campos=campos_billete)

def testBilletesCliente(setup_client, setup_token):
    client=setup_client
    #access_token_expires = timedelta(minutes=30)
    #access_token = crearToken(
    #data={"sub": cliente_ejemplo["correo"], "rol": "cliente"}, expires_delta=access_token_expires)

    access_token=setup_token
    cadena = "/cliente/"+str(billete_ejemplo["cliente"])+"/billetes/"
    print("Cadena ", cadena)
    response = client.get("/cliente/"+str(billete_ejemplo["cliente"])+"/billetes/",
            headers={"Authorization": "Bearer "+access_token})
    print("Billete id cliente ", billete_ejemplo["cliente"])
    print("Billete cliente ", billete_ejemplo)
    print("Billetes cliente ", response.json())
    print("Billetes cliente ejemplo ", [billete_ejemplo])
    assert response.status_code == 200
    for billete in response.json():
        verificar_igualdad(billete, billete_ejemplo, campos=campos_billete, exclude=["id"])
    

def testSetFechaSalida(setup_client, setup_token):
    client=setup_client
    #access_token_expires = timedelta(minutes=30)
    #access_token = crearToken(
    #data={"sub": cliente_ejemplo["correo"], "rol": "cliente"}, expires_delta=access_token_expires)

    access_token=setup_token
    response = client.patch(
        "/billetes/"+str(id_billete["id"])+"/editar",
        headers={"accept": "application/json", "Authorization": "Bearer "+access_token},
        json={"newFechaSalida": "2022-05-08 09:30:00"}
    )
    print("id billete ", id_billete["id"])
    print("Response ", response.json())
    assert response.status_code == 200
    verificar_igualdad(response.json(), billete_ejemplo, campos=campos_billete, exclude=["fechaSalida"])
    billete_ejemplo["fechaSalida"] = response.json()["fechaSalida"]

def testSetFechaSalidaMenor(setup_client, setup_token):
    client=setup_client
    #access_token_expires = timedelta(minutes=30)
    #access_token = crearToken(
    #data={"sub": cliente_ejemplo["correo"], "rol": "cliente"}, expires_delta=access_token_expires)

    access_token=setup_token
    response = client.patch(
        "/billetes/"+str(id_billete["id"])+"/editar",
        headers={"accept": "application/json", "Authorization": "Bearer "+access_token},
        json={"fechaSalida": "2022-01-08 09:30:00"}
    )
    print("id billete ", id_billete["id"])
    print("Response ", response.json())
    assert response.status_code == 422

def testSetFechaLlegada(setup_client, setup_token):
    client=setup_client
    #access_token_expires = timedelta(minutes=30)
    #access_token = crearToken(
    #data={"sub": cliente_ejemplo["correo"], "rol": "cliente"}, expires_delta=access_token_expires)

    access_token=setup_token
    response = client.patch(
        "/billetes/"+str(id_billete["id"])+"/editar",
        headers={"accept": "application/json", "Authorization": "Bearer "+access_token},
        json={"fechaLlegada": "2022-05-12 19:00:00"}
    )
    assert response.status_code == 200
    verificar_igualdad(response.json(), billete_ejemplo, campos=campos_billete, exclude=["fechaLlegada"])
    billete_ejemplo["fechaLlegada"] = response.json()["fechaLlegada"]

def testSetFechaLlegadaMenor(setup_client, setup_token):
    client=setup_client
    #access_token_expires = timedelta(minutes=30)
    #access_token = crearToken(
    #data={"sub": cliente_ejemplo["correo"], "rol": "cliente"}, expires_delta=access_token_expires)

    access_token=setup_token
    response = client.patch(
        "/billetes/"+str(id_billete["id"])+"/editar",
        headers={"accept": "application/json", "Authorization": "Bearer "+access_token},
        json={"fechaLlegada": "2022-01-12 19:00:00"}
    )
    assert response.status_code == 422

def testSetFechasErroneas(setup_client, setup_token):
    client=setup_client
    #access_token_expires = timedelta(minutes=30)
    #access_token = crearToken(
    #data={"sub": cliente_ejemplo["correo"], "rol": "cliente"}, expires_delta=access_token_expires)

    access_token=setup_token
    response = client.patch(
        "/billetes/"+str(id_billete["id"])+"/editar",
        headers={"accept": "application/json", "Authorization": "Bearer "+access_token},
        json={"fechaSalida": "2022-06-12 19:00:00", "fechaLlegada": "2022-06-12 16:00:00"}
    )
    assert response.status_code == 422


def testSetAsiento(setup_client, setup_token):
    client=setup_client
    #access_token_expires = timedelta(minutes=30)
    #access_token = crearToken(
    #data={"sub": cliente_ejemplo["correo"], "rol": cliente_ejemplo["rol"]}, expires_delta=access_token_expires)

    access_token=setup_token
    response = client.patch(
        "/billetes/"+str(id_billete["id"])+"/editar",
        headers={"accept": "application/json", "Authorization": "Bearer "+access_token},
        json={"asiento": 30}
    )
    print("Response ", response.json())
    assert response.status_code == 200
    verificar_igualdad(response.json(), billete_ejemplo, campos=campos_billete, exclude=["asiento"])
    assert response.json()["asiento"] == 30

def testSetAsientoErroneo(setup_client, setup_token):
    client=setup_client
    #access_token_expires = timedelta(minutes=30)
    #access_token = crearToken(
    #data={"sub": cliente_ejemplo["correo"], "rol": cliente_ejemplo["rol"]}, expires_delta=access_token_expires)

    access_token=setup_token
    response = client.patch(
        "/billetes/"+str(id_billete["id"])+"/editar",
        headers={"accept": "application/json", "Authorization": "Bearer "+access_token},
        json={"asiento": 65}
    )
    assert response.status_code == 422


def testDuracionBillete(setup_client, setup_token):
    client=setup_client
    #access_token_expires = timedelta(minutes=30)
    #access_token = crearToken(
    #data={"sub": cliente_ejemplo["correo"], "rol": cliente_ejemplo["rol"]}, expires_delta=access_token_expires)

    access_token=setup_token
    response = client.get(
        "/cliente/billete/"+str(id_billete["id"])+"/duracion",
        headers={"accept": "application/json", "Authorization": "Bearer "+access_token}
    )
    assert response.status_code == 200

def testDeleteCliente(setup_client, setup_token):
    client = setup_client
    #access_token_expires = timedelta(minutes=30) #A traves de patch no se cambia la contraseña, se cambia por otro mecanismo
    #access_token = crearToken( #Cuando cambia la contraseña se invalida la sesion para iniciar sesion otra vez
    #data={"sub": cliente_ejemplo["correo"], "rol": cliente_ejemplo["rol"]}, expires_delta=access_token_expires) #Comprobar el flujo de la sesion

    access_token=setup_token
    response = client.delete("/cliente/"+str(billete_ejemplo["cliente"])+"/borrar", 
        headers={"accept": "application/json", "Authorization": "Bearer "+access_token}
    )
    assert response.status_code == 200

def testLoginAdmin2(setup_client):
    client=setup_client
    response = client.post(
        "/token",
        headers={"accept": "application/json", "Content-type": "application/x-www-form-urlencoded"},
        data={"grant_type": "", "username": admin_ejemplo["correo"], "password": admin_ejemplo["password"], "scope": "", 
            "client_id": "", "client_secret": ""}
    )
    print(response.json())
    setup_login(admin_ejemplo["correo"], admin_ejemplo["password"], admin_ejemplo["rol"])
    response_header = {"Authorization": "Bearer "+response.json()["access_token"], "token_type": "bearer"}

def testDeleteRuta(setup_client, setup_token):
    client = setup_client
    #access_token_expires = timedelta(minutes=30) 
    #access_token = crearToken( 
    #data={"sub": admin_ejemplo["correo"], "rol": admin_ejemplo["rol"]}, expires_delta=access_token_expires)

    access_token=setup_token
    response = client.delete("/administrador/"+str(admin_ejemplo["id"])+"/ruta/1/borrar", 
        headers={"accept": "application/json", "Authorization": "Bearer "+access_token}
    )
    assert response.status_code == 200

def testDeleteAutobus(setup_client, setup_token):
    client = setup_client
    #access_token_expires = timedelta(minutes=30) 
    #access_token = crearToken( 
    #data={"sub": admin_ejemplo["correo"], "rol": admin_ejemplo["rol"]}, expires_delta=access_token_expires)

    access_token=setup_token
    response = client.delete("/administrador/"+str(admin_ejemplo["id"])+"/autobus/1/borrar", 
        headers={"accept": "application/json", "Authorization": "Bearer "+access_token}
    )
    assert response.status_code == 200

def testDeleteViaje(setup_client, setup_token):
    client = setup_client
    #access_token_expires = timedelta(minutes=30) 
    #access_token = crearToken( 
    #data={"sub": admin_ejemplo["correo"], "rol": admin_ejemplo["rol"]}, expires_delta=access_token_expires)

    access_token=setup_token
    response = client.delete("/administrador/"+str(admin_ejemplo["id"])+"/viaje/1/borrar", 
        headers={"accept": "application/json", "Authorization": "Bearer "+access_token}
    )
    assert response.status_code == 200

def testDeleteAdmin(setup_client, setup_token):
    client = setup_client
    #access_token_expires = timedelta(minutes=30) 
    #access_token = crearToken( 
    #data={"sub": admin_ejemplo["correo"], "rol": admin_ejemplo["rol"]}, expires_delta=access_token_expires)

    access_token=setup_token
    response = client.delete("/administrador/"+str(admin_ejemplo["id"])+"/borrar", 
        headers={"accept": "application/json", "Authorization": "Bearer "+access_token}
    )
    assert response.status_code == 200

def testLoginConductor(setup_client):
    client=setup_client
    response = client.post(
        "/token",
        headers={"accept": "application/json", "Content-type": "application/x-www-form-urlencoded"},
        data={"grant_type": "", "username": conductor_ejemplo["correo"], "password": conductor_ejemplo["password"], "scope": "", 
            "client_id": "", "client_secret": ""}
    )
    print(response.json())
    setup_login(conductor_ejemplo["correo"], conductor_ejemplo["password"], conductor_ejemplo["rol"])
    response_header = {"Authorization": "Bearer "+response.json()["access_token"], "token_type": "bearer"}

def testDeleteConductor(setup_client, setup_token):
    client = setup_client
    #access_token_expires = timedelta(minutes=30) 
    #access_token = crearToken( 
    #data={"sub": conductor_ejemplo["correo"], "rol": conductor_ejemplo["rol"]}, expires_delta=access_token_expires)

    access_token=setup_token
    response = client.delete("/conductor/"+str(conductor_ejemplo["id"])+"/borrar", 
        headers={"accept": "application/json", "Authorization": "Bearer "+access_token}
    )
    assert response.status_code == 200