from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pytest
from datetime import timedelta


from ..database import Base
from ..main import app, get_db
from .aux_func import setup_login, setup_token, setup_data
from ..crud import crearToken, getPasswordHash, getClientes

# Para estas pruebas se elige el cliente con id número 3
cliente_ejemplo = {"id": 3, "nombre": "Ana", "apellidos": "Fernandez Perez", "dni": "71863220L", "correo": "anafp@email.com", 
            "password": "anafp", "telefono": "632587441", "rol": "cliente"}

# Administrador para crear un autobús con una sola plaza
admin_ejemplo = {"id": 1, "nombre": "Admin", "apellidos": "Admin Admin", "dni": "12345678A", "correo": "admin@email.com", 
            "password": "admin", "telefono": "641002835", "rol": "administrador"}

# Autobús de una sola plaza
autobus_lleno = {"modelo": "AutobusLleno", "asientos": 1}

# Viaje con el autobús lleno
viaje_lleno = {"conductor": 3, "autobus": -1, "ruta": 2, "precio": 13.10}

# Billete del autobús lleno que va a comprar el cliente
billete_lleno = {"cliente": 3, "viaje": -1, "fechaSalida": "2022-08-15T10:00:00", 
        "fechaLlegada": "2022-08-15T15:00:00", "asiento": 1}

# Nuevo billete que va a comprar el cliente
nuevo_billete = {"id": -1, "cliente": 3, "viaje": 1, "fechaSalida": "2022-06-20T16:30:00", 
        "fechaLlegada": "2022-06-20T19:30:00", "asiento": 16}

# Billetes erróneos
billete_fechaSalida_menor = {"cliente": 3, "viaje": 1, "fechaSalida": "2022-01-20T16:30:00", 
        "fechaLlegada": "2022-06-20T19:30:00", "asiento": 16}

billete_fechaLlegada_menor = {"cliente": 3, "viaje": 1, "fechaSalida": "2022-07-20T16:30:00", 
        "fechaLlegada": "2022-01-20T19:30:00", "asiento": 16}

billete_fechas_erroneas = {"cliente": 3, "viaje": 1, "fechaSalida": "2022-08-20T16:30:00", 
        "fechaLlegada": "2022-06-20T19:30:00", "asiento": 16}

billete_asiento_erroneo = {"cliente": 3, "viaje": 5, "fechaSalida": "2022-08-17T18:00:00", 
        "fechaLlegada": "2022-08-17T20:00:00", "asiento": 40}


# Billete modificado
set_billete = {"id": -1, "cliente": 3, "viaje": 2, "fechaSalida": "2022-08-20T16:30:00", 
        "fechaLlegada": "2022-08-20T19:30:00", "asiento": 10}

# Billetes que el cliente ha comprado y que se encuentran registados en la base de datos
billete1 = {"id": 2, "cliente": 3, "viaje": 7, "fechaSalida": "2022-03-15T15:00:00", 
        "fechaLlegada": "2022-03-15T17:00:00", "asiento": 36}
billete2 = {"id": 7, "cliente": 3, "viaje": 5, "fechaSalida": "2022-03-17T05:00:00", 
        "fechaLlegada": "2022-03-17T09:00:00", "asiento": 40}
billete3 = {"id": 9, "cliente": 3, "viaje": 6, "fechaSalida": "2022-05-02T17:00:00", 
        "fechaLlegada": "2022-05-02T20:30:00", "asiento": 28}

campos_verificables = ["nombre", "apellidos", "dni", "correo", "telefono", "rol"]

campos_billete = ["cliente", "viaje", "fechaSalida", "fechaLlegada", "asiento"]


def verificar_igualdad(user1, user2, campos=campos_verificables, exclude=[]):
    for k in campos:
        if k in exclude:
            continue
        assert user1[k] == user2[k]

# Función que simula el inicio de sesión del cliente
def login(user, client):
    response = client.post(
        "/token",
        headers={"accept": "application/json", "Content-type": "application/x-www-form-urlencoded"},
        data={"grant_type": "", "username": user["correo"], "password": user["password"], "scope": "", 
            "client_id": "", "client_secret": ""}
    )
    token = response.json()["access_token"]
    return token


# Función en la que el cliente accede a la aplicación
def xtestLoginCliente(setup_data):
    client=setup_data
    # setup_login(cliente["correo"], cliente["password"], cliente["rol"])

    response = client.post(
        "/cliente/nuevo",
        json=cliente_ejemplo
    )
    print("Response Nuevo Cliente ", response.json())
    assert response.status_code == 200

    response = client.post(
        "/token",
        headers={"accept": "application/json", "Content-type": "application/x-www-form-urlencoded"},
        data={"grant_type": "", "username": cliente_ejemplo["correo"], "password": cliente_ejemplo["password"], "scope": "", 
            "client_id": "", "client_secret": ""}
    )
    assert response.status_code == 200

# Función en la que el cliente incia sesión y comprueba los billetes que ha comprado, los puntos que ha ganado 
# y busca viajes con diferentes destinos
def testBilletesCliente(setup_data):
    client=setup_data

    # El cliente inicia sesión en la aplicación
    access_token = login(cliente_ejemplo, client)

    # Se muestra el perfil del cliente
    response = client.get(
        "/clientes/"+str(cliente_ejemplo["id"])+"/perfil",
        headers={"Authorization": "Bearer "+access_token})
    assert response.status_code == 200
    verificar_igualdad(response.json(), cliente_ejemplo)

    # Se muestran los puntos que ha ganado el cliente
    response = client.get(
        "/cliente/"+str(cliente_ejemplo["id"])+"/puntos",
        headers={"accept": "application/json", "Authorization": "Bearer "+access_token})
    #print("Response ", response.json())
    assert response.status_code == 200
    assert response.json() == 120
    
    # Se muestran los billetes que ha comprado el cliente
    response = client.get("/cliente/"+str(cliente_ejemplo["id"])+"/billetes/",
            headers={"Authorization": "Bearer "+access_token})
    assert response.status_code == 200
    print("Response ", response.json())
    print("Billetes ", [billete1, billete2, billete3])
    #assert response.json() == [billete1, billete2, billete3]
    billetes = {"billete1": billete1, "billete2": billete2, "billete3": billete3}
    array_billetes = ["billete1", "billete2", "billete3"]
    cont = 0
    for billete in response.json():
        verificar_igualdad(billete, billetes[array_billetes[cont]], campos=campos_billete)
        cont = cont+1

    # El cliente busca viajes con origen Madrid y destino Almeria
    response = client.get("/viajes/origen/Madrid/destino/Almeria", 
            headers={"Authorization": "Bearer "+access_token})
    #print("Response ", response.json())
    assert response.status_code == 200
    assert response.json() == []

    # El cliente busca viajes con origen Barcelona y destino Madrid
    response = client.get("/viajes/origen/Barcelona/destino/Madrid", 
            headers={"Authorization": "Bearer "+access_token})
    print("Response origen destino", response.json())
    assert response.status_code == 200
    viaje1 = {"id": 2, "conductor": 9, "autobus": 3, "ruta": 4, "precio": 12.5}
    viaje2 = {"id": 2, "conductor": 8, "autobus": 1, "ruta": 4, "precio": 12.6}
    viajes = {"viaje1": viaje1, "viaje2": viaje2}
    array_viajes = ["viaje1", "viaje2"]
    cont = 0
    for viaje in response.json():
        verificar_igualdad(viaje, viajes[array_viajes[cont]], campos={"conductor", "autobus", "ruta", "precio"})
        cont = cont+1
    

    # El cliente busca viajes con origen Leon y destino Salamanca
    response = client.get("/viajes/origen/Leon/destino/Salamanca", 
            headers={"Authorization": "Bearer "+access_token})
    print("Response ", response.json())
    assert response.status_code == 200
    assert response.json() == [
                                {"conductor": 10, "autobus": 2, "ruta": 3, "precio": 11.3, "id": 3}, 
                                {"conductor": 10, "autobus": 4, "ruta": 3, "precio": 14.0, "id": 5}
                              ]


# Función que simula la compra de un billete por parte del cliente, su posterior modificación y su eliminación
def testComprarBillete(setup_data):
    client=setup_data

    # Inicio de sesión del cliente
    access_token=login(cliente_ejemplo, client)

    # Compra de billetes con fecha de salida menor que la actual
    response = client.post(
        "/billete/nuevo",
        headers={"accept": "application/json", "Authorization": "Bearer "+access_token},
        json=billete_fechaSalida_menor
    )
    print("Response Fecha Salida Menor ", response.json())
    assert response.status_code == 422

    # Compra de billetes con fecha de llegada menor que la actual
    response = client.post(
        "/billete/nuevo",
        headers={"accept": "application/json", "Authorization": "Bearer "+access_token},
        json=billete_fechaLlegada_menor
    )
    assert response.status_code == 422

    # Compra de billetes con fecha de llegada menor que la fecha de salida
    response = client.post(
        "/billete/nuevo",
        headers={"accept": "application/json", "Authorization": "Bearer "+access_token},
        json=billete_fechas_erroneas
    )
    assert response.status_code == 422

    # Compra de billetes con el asiento no disponible
    response = client.post(
        "/billete/nuevo",
        headers={"accept": "application/json", "Authorization": "Bearer "+access_token},
        json=billete_asiento_erroneo
    )
    assert response.status_code == 422

    # Compra del billete
    response = client.post(
        "/billete/nuevo",
        headers={"accept": "application/json", "Authorization": "Bearer "+access_token},
        json=nuevo_billete
    )
    assert response.status_code == 200
    nuevo_billete["id"] = response.json()["id"]
    set_billete["id"] = response.json()["id"]
    #print("id billete ", nuevo_billete["id"])
    verificar_igualdad(response.json(), nuevo_billete, campos=campos_billete)

    # Comprobar la actualización de los puntos del cliente
    response = client.get(
        "/cliente/"+str(cliente_ejemplo["id"])+"/puntos",
        headers={"accept": "application/json", "Authorization": "Bearer "+access_token})
    #print("Response ", response.json())
    assert response.status_code == 200
    assert response.json() == 270

    # El cliente busca los asientos ocupados del viaje relacionado con el nuevo billete
    response = client.get(
        "/viaje/"+str(nuevo_billete["viaje"])+"/billetes/", 
    headers={"accept": "application/json", "Authorization": "Bearer "+access_token})
    print("Response Asientos Ocupados ", response.json())
    assert response.status_code == 200
    otro_billete = {"id": 5, "cliente": 2, "viaje": 1, "fechaSalida": "2022-04-10T16:30:00", 
                    "fechaLlegada": "2022-04-10T21:00:00", "asiento": 30}
    billetes = {"nuevo_billete": nuevo_billete, "otro_billete": otro_billete}
    array_billetes = ["otro_billete", "nuevo_billete"]
    cont = 0
    for billete in response.json():
        verificar_igualdad(billete, billetes[array_billetes[cont]], campos=campos_billete, exclude=["id"])
        cont = cont+1

     # El cliente busca los asientos libres del viaje relacionado con el nuevo billete
    response = client.get(
        "/viaje/"+str(nuevo_billete["viaje"])+"/asientos/", 
    headers={"accept": "application/json", "Authorization": "Bearer "+access_token})
    print("Response Asientos Libres ", response.json())
    assert response.status_code == 200
    assert response.json() == [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 17, 18, 
                                19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 31, 32, 33, 34, 35]

    # Modificación del billete con fecha de salida menor que la fecha actual
    response = client.patch(
        "/billetes/"+str(nuevo_billete["id"])+"/editar",
        headers={"accept": "application/json", "Authorization": "Bearer "+access_token},
        json={"fechaSalida": "2022-01-20T16:30:00"}
    )
    assert response.status_code == 422

    # Modificación del billete con fecha de llegada menor que la fecha actual
    response = client.patch(
        "/billetes/"+str(nuevo_billete["id"])+"/editar",
        headers={"accept": "application/json", "Authorization": "Bearer "+access_token},
        json={"fechaLlegada": "2022-01-20T16:30:00"}
    )
    assert response.status_code == 422

    # Modificación del billete con fecha de llegada menor que fecha de salida
    response = client.patch(
        "/billetes/"+str(nuevo_billete["id"])+"/editar",
        headers={"accept": "application/json", "Authorization": "Bearer "+access_token},
        json={"fechaSalida": "2022-08-20T19:30:00", "fechaLlegada": "2022-08-20T16:30:00"}
    )
    assert response.status_code == 422

    # Modificación del billete con un asiento ya reservado
    response = client.patch(
        "/billetes/"+str(nuevo_billete["id"])+"/editar",
        headers={"accept": "application/json", "Authorization": "Bearer "+access_token},
        json={"asiento": 30}
    )
    print("Billete Set Asiento ", nuevo_billete)
    print("Response Set Asiento ", response.json())
    assert response.status_code == 400

    # Modificación del billete
    response = client.patch(
        "/billetes/"+str(nuevo_billete["id"])+"/editar",
        headers={"accept": "application/json", "Authorization": "Bearer "+access_token},
        json=set_billete
    )
    assert response.status_code == 200
    verificar_igualdad(response.json(), set_billete, campos=campos_billete)

    # Observar la duración del viaje
    response = client.get(
        "/cliente/billete/"+str(nuevo_billete["id"])+"/duracion",
        headers={"accept": "application/json", "Authorization": "Bearer "+access_token})
    #print ("Response Duracion ", response.json())
    assert response.status_code == 200
    assert str(response.json()) == "03:00:00"    

    # Eliminar el billete que el cliente ha creado
    response = client.delete(
        "/cliente/"+str(nuevo_billete["cliente"])+"/billete/"+str(nuevo_billete["id"])+"/borrar",
        headers={"accept": "application/json", "Authorization": "Bearer "+access_token}
    )
    assert response.status_code == 200

    # Observar los billetes que ha comprado el cliente
    response = client.get("/cliente/"+str(cliente_ejemplo["id"])+"/billetes/",
            headers={"Authorization": "Bearer "+access_token})
    assert response.status_code == 200
    print("Response billetes ", response.json())

# Función que crea un autobús con una sola plaza para comprobar que no se puede comprar un billete
# si el autobús está lleno
def testBilleteAutobusLleno(setup_data):
    client=setup_data

    # El administrador inicia sesión en la aplicación
    access_token = login(admin_ejemplo, client)

    # Se crea el autobús de una plaza
    response = client.post(
        "/autobus/nuevo",
        headers={"accept": "application/json", "Authorization": "Bearer "+access_token},
        json=autobus_lleno
    )
    print("Response Autobus Lleno ", response.json())
    assert response.status_code == 200
    viaje_lleno["autobus"] = response.json()["id"]
    verificar_igualdad(response.json(), autobus_lleno, campos=["modelo", "asientos"], exclude=["id", "asientosLibres"])

    # Se crea el viaje con el autobús lleno
    response = client.post(
        "/viaje/nuevo",
        headers={"accept": "application/json", "Authorization": "Bearer "+access_token},
        json=viaje_lleno
    )
    assert response.status_code == 200
    billete_lleno["viaje"] = response.json()["id"]
    verificar_igualdad(response.json(), viaje_lleno, campos=["conductor", "autobus", "ruta", "precio"], exclude=["id"])

    # El cliente inicia sesión en la aplicación
    access_token = login(cliente_ejemplo, client)

    # El cliente comprar el billete con el autobús lleno
    response = client.post(
        "/billete/nuevo",
        headers={"accept": "application/json", "Authorization": "Bearer "+access_token},
        json=billete_lleno
    )
    assert response.status_code == 200
    verificar_igualdad(response.json(), billete_lleno, campos=campos_billete, exclude=["id"])

    # El cliente vuelve a comprar el mismo billete
    response = client.post(
        "/billete/nuevo",
        headers={"accept": "application/json", "Authorization": "Bearer "+access_token},
        json=billete_lleno
    )
    print("RESPONSE JSON ", response.json())
    assert response.status_code == 400
