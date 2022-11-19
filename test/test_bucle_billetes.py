# coding=utf-8
import requests
import time

# Para estas pruebas se elige el cliente con id número 3
cliente_bucle = {"id": -1, "nombre": "ClienteBilletes", "apellidos": "Cliente Billetes", "dni": "14785236L", "correo": "clienteBilletes@email.com", 
            "password": "1234", "telefono": "600511844", "rol": "cliente"}


# Administrador para crear un autobús con una sola plaza
admin_bucle = {"id": 1, "nombre": "Admin", "apellidos": "Admin Admin", "dni": "12345678Z", "correo": "admin@email.com", 
            "password": "admin", "telefono": "641002835", "rol": "administrador"}

# Autobús de una sola plaza
autobus_bucle = {"modelo": "AutobusBucle", "asientos": 100}

# Viaje con el autobús lleno
viaje_bucle = {"conductor": -1, "autobus": -1, "ruta": -1, "precio": 13.10}

# Billete del autobús lleno que va a comprar el cliente
billete_bucle = {"cliente": -1, "viaje": -1, "fechaSalida": "2022-08-15T10:00:00", 
        "fechaLlegada": "2022-08-15T15:00:00", "asiento": 0}

# Conductor que se crea para realizar comprobaciones de listas
conductor_bucle = {"id": -1, "nombre": "ConductorBucle", "apellidos": "Conductor Bucle", "dni": "15975364M", "correo": "conductorBucle@email.com", 
        "password": "1234", "telefono": "698700223", "rol": "conductor"}

# Ruta que el administrador crea para realizar comprobaciones de listas
ruta_bucle = {"ciudades": "Madrid Guadalajara Zaragoza Barcelona"}

campos_verificables = ["nombre", "apellidos", "dni", "correo", "telefono", "rol"]

campos_billete = ["cliente", "viaje", "fechaSalida", "fechaLlegada", "asiento"]

print("?????????")

def verificar_igualdad(user1, user2, campos=campos_verificables, exclude=[]):
    for k in campos:
        if k in exclude:
            continue
        assert user1[k] == user2[k]


# Función que simula el inicio de sesión del cliente
def login(user, client): #, request
    response = client.post(
        "http://127.0.0.1:8000/token",
        headers={"accept": "application/json", "Content-type": "application/x-www-form-urlencoded"},
        data={"grant_type": "", "username": user["correo"], "password": user["password"], "scope": "", 
            "client_id": "", "client_secret": ""}
    )
    token = response.json()["access_token"]
    return token

# Se crea cliente_bucle
response = requests.post(
    "http://127.0.0.1:8000/cliente/nuevo",
    json=cliente_bucle
)
print("Response cliente_bucle status", response.status_code)
print("Response cliente_bucle ", response.json())
cliente_bucle["id"] = response.json()["id"]
assert response.status_code == 200
verificar_igualdad(response.json(), cliente_bucle)

# El administrador inicia sesión
access_token = login(admin_bucle, requests)

# Se crea conductor_ejemplo
response = requests.post(
    "http://127.0.0.1:8000/conductor/nuevo",
    json=conductor_bucle,
    headers={"Authorization": "Bearer "+access_token}
)
conductor_bucle["id"] = response.json()["id"]
assert response.status_code == 200
verificar_igualdad(response.json(), conductor_bucle)

# Se crea autobus_bucle
response = requests.post(
    "http://127.0.0.1:8000/autobus/nuevo",
    headers={"accept": "application/json", "Authorization": "Bearer "+access_token},
    json=autobus_bucle
)
print("Autobus Request ", response.json())
autobus_bucle["id"] = response.json()["id"]
assert response.status_code == 200

# Se crea ruta_bucle
response = requests.post(
    "http://127.0.0.1:8000/ruta/nueva",
    headers={"accept": "application/json", "Authorization": "Bearer "+access_token},
    json=ruta_bucle
)
ruta_bucle["id"] = response.json()["id"]
assert response.status_code == 200


# Se cambian los atributos de los viajes con los ids del conductor, el autobus y las rutas
viaje_bucle["conductor"] = conductor_bucle["id"]
viaje_bucle["autobus"] = autobus_bucle["id"]
viaje_bucle["ruta"] = ruta_bucle["id"]

# Se cambian los atributos del billete con los ids del cliente y del viaje
billete_bucle["cliente"] = cliente_bucle["id"]
#billete_bucle["viaje"] = viaje_bucle["id"]


# Se crea viaje_bucle
response = requests.post(
    "http://127.0.0.1:8000/viaje/nuevo",
    headers={"accept": "application/json", "Authorization": "Bearer "+access_token},
    json=viaje_bucle
)
viaje_bucle["id"] = response.json()["id"]
billete_bucle["viaje"] = response.json()["id"]
assert response.status_code == 200


# cliente_bucle incia sesión
access_token = login(cliente_bucle, requests)

listaID = []

# Bucle que crea billetes
contador = 1
while contador<=autobus_bucle["asientos"]:
    billete_bucle["asiento"] = contador
    response = requests.post(
        "http://127.0.0.1:8000/billete/nuevo",
        headers={"accept": "application/json", "Authorization": "Bearer "+access_token},
        json=billete_bucle
    )
    print("Response Billete Bucle ", response.json())
    print("Response status code ", response.status_code)
    #assert response.status_code == 200
    #billete_bucle["id"] = response.json()["id"]
    verificar_igualdad(response.json(), billete_bucle, campos=campos_billete)
    contador = contador+1
    time.sleep(1)
    listaID.append(response.json()["id"])

# Se borran los billetes que se han creado
for id in listaID:
    response = requests.delete(
        "http://127.0.0.1:8000/cliente/"+str(cliente_bucle["id"])+"/billete/"+str(id)+"/borrar",
        headers={"accept": "application/json", "Authorization": "Bearer "+access_token}
    )
    print("Response Delete Billete", response.json())
    print("Response Delete status code ", response.status_code)

response = requests.delete(
        "http://127.0.0.1:8000/cliente/"+str(cliente_bucle["id"])+"/borrar",
        headers={"accept": "application/json", "Authorization": "Bearer "+access_token}
    )
print("Response Delete Cliente", response.json())
print("Response Delete status code ", response.status_code)

# Función bucle billetes
#def bucle_billetes():
"""
    client = requests

    # Se crea cliente_ejemplo
    response = client.post(
        "http://127.0.0.1:8000/cliente/nuevo",
        json=cliente_ejemplo
    )
    print("Response cliente_ejemplo status", response.status_code)
    print("Response cliente_ejemplo ", response.json())
    cliente_ejemplo["id"] = response.json()["id"]
    assert response.status_code == 200
    verificar_igualdad(response.json(), cliente_ejemplo)

    # El administrador inicia sesión
    access_token = login(admin_ejemplo, client)

    # Se crea conductor_ejemplo
    response = client.post(
        "http://127.0.0.1:8000/conductor/nuevo",
        json=conductor_ejemplo,
        headers={"Authorization": "Bearer "+access_token}
    )
    conductor_ejemplo["id"] = response.json()["id"]
    assert response.status_code == 200
    verificar_igualdad(response.json(), conductor_ejemplo)

    # Se crea autobus_bucle
    response = client.post(
        "http://127.0.0.1:8000/autobus/nuevo",
        headers={"accept": "application/json", "Authorization": "Bearer "+access_token},
        json=autobus_bucle
    )
    print("Autobus Request ", response.json())
    autobus_bucle["id"] = response.json()["id"]
    assert response.status_code == 200
    #verificar_igualdad(response.json(), autobus_ejemplo)

    # Se crea ruta_bucle
    response = client.post(
        "http://127.0.0.1:8000/ruta/nueva",
        headers={"accept": "application/json", "Authorization": "Bearer "+access_token},
        json=ruta_bucle
    )
    ruta_bucle["id"] = response.json()["id"]
    assert response.status_code == 200
    #verificar_igualdad(response.json(), ruta_bucle)

    # Se cambian los atributos de los viajes con los ids del conductor, el autobus y las rutas
    viaje_bucle["conductor"]=conductor_ejemplo["id"]
    viaje_bucle["autobus"]=autobus_bucle["id"]
    viaje_bucle["ruta"]=ruta_bucle["id"]

    # Se crea viaje_bucle
    response = client.post(
        "http://127.0.0.1:8000/viaje/nuevo",
        headers={"accept": "application/json", "Authorization": "Bearer "+access_token},
        json=viaje_bucle
    )
    viaje_bucle["id"] = response.json()["id"]
    billete_bucle["viaje"] = response.json()["id"]
    assert response.status_code == 200
    #verificar_igualdad(response.json(), viaje1)

    # El nuevo cliente inicia sesión
    access_token = login(cliente_ejemplo, client)

    listaID = []

    # Bucle que crea billetes
    contador = 1
    while contador<=autobus_bucle["asientos"]:
        billete_bucle["asiento"] = contador
        response = client.post(
            "http://127.0.0.1:8000/billete/nuevo",
            headers={"accept": "application/json", "Authorization": "Bearer "+access_token},
            json=billete_bucle
        )
        print("Response Billete Bucle ", response.json())
        print("Response status code ", response.status_code)
        #assert response.status_code == 200
        #billete_bucle["id"] = response.json()["id"]
        verificar_igualdad(response.json(), billete_bucle, campos=campos_billete)
        contador = contador+1
        time.sleep(1)
        listaID.append(response.json()["id"])

    for id in listaID:
        response = client.delete(
            "http://127.0.0.1:8000/cliente/"+str(cliente_ejemplo["id"])+"/billete/"+str(id)+"/borrar",
            headers={"accept": "application/json", "Authorization": "Bearer "+access_token}
        )
        print("Response Delete Billete", response.json())
        print("Response Delete status code ", response.status_code)

    response = client.delete(
        "http://127.0.0.1:8000/cliente/"+str(cliente_ejemplo["id"])+"/borrar",
        headers={"accept": "application/json", "Authorization": "Bearer "+access_token}
    )
    print("Response Delete Cliente", response.json())
    print("Response Delete status code ", response.status_code)
"""