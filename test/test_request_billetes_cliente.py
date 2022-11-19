import requests


# Para estas pruebas se elige el cliente con id número 3
cliente_ejemplo = {"id": 3, "nombre": "Ana", "apellidos": "Fernandez Perez", "dni": "71863220L", "correo": "anafp@email.com", 
            "password": "anafp", "telefono": "632587441", "rol": "cliente"}

#cliente_ejemplo2 = {"id": 1, "nombre": "UsuarioTest", "apellidos": "Usuario Test", "dni": "12345678A", "correo": "usuariotest@email.com", 
#            "password": "test", "telefono": "654321987", "rol": "cliente"}

# Administrador para crear un autobús con una sola plaza
admin_ejemplo = {"id": 1, "nombre": "Admin", "apellidos": "Admin Admin", "dni": "12345678A", "correo": "admin@email.com", 
            "password": "admin", "telefono": "641002835", "rol": "administrador"}

# Autobús de una sola plaza
autobus_lleno = {"modelo": "AutobusLleno", "asientos": 1}

# Viaje con el autobús lleno
viaje_lleno = {"conductor": -1, "autobus": -1, "ruta": -1, "precio": 13.10}

# Billete del autobús lleno que va a comprar el cliente
billete_lleno = {"cliente": -1, "viaje": -1, "fechaSalida": "2022-08-15T10:00:00", 
        "fechaLlegada": "2022-08-15T15:00:00", "asiento": 1}

# Nuevo billete que va a comprar el cliente
nuevo_billete = {"id": -1, "cliente": -1, "viaje": -1, "fechaSalida": "2022-06-20T16:30:00", 
        "fechaLlegada": "2022-06-20T19:30:00", "asiento": 16}

# Billetes erróneos
billete_fechaSalida_menor = {"cliente": -1, "viaje": 2, "fechaSalida": "2022-01-20T16:30:00", 
        "fechaLlegada": "2022-06-20T19:30:00", "asiento": 16}

billete_fechaLlegada_menor = {"cliente": -1, "viaje": 2, "fechaSalida": "2022-07-20T16:30:00", 
        "fechaLlegada": "2022-01-20T19:30:00", "asiento": 16}

billete_fechas_erroneas = {"cliente": -1, "viaje": 2, "fechaSalida": "2022-08-20T16:30:00", 
        "fechaLlegada": "2022-06-20T19:30:00", "asiento": 16}

billete_asiento_erroneo = {"cliente": -1, "viaje": 2, "fechaSalida": "2022-08-17T18:00:00", 
        "fechaLlegada": "2022-08-17T20:00:00", "asiento": 40}


# Billete modificado
set_billete = {"id": -1, "cliente": -1, "viaje": 2, "fechaSalida": "2022-08-20T16:30:00", 
        "fechaLlegada": "2022-08-20T19:30:00", "asiento": 10}

# Billetes que el cliente ha comprado y que se encuentran registados en la base de datos
billete1 = {"id": 2, "cliente": -1, "viaje": 2, "fechaSalida": "2022-07-15T15:00:00", 
        "fechaLlegada": "2022-07-15T17:00:00", "asiento": 5}
billete2 = {"id": 7, "cliente": -1, "viaje": 2, "fechaSalida": "2022-07-17T05:00:00", 
        "fechaLlegada": "2022-07-17T09:00:00", "asiento": 31}
billete3 = {"id": 9, "cliente": -1, "viaje": 2, "fechaSalida": "2022-09-02T17:00:00", 
        "fechaLlegada": "2022-09-02T20:30:00", "asiento": 28}

# Conductor que se crea para realizar comprobaciones de listas
conductor_ejemplo = {"id": -1, "nombre": "Rosa", "apellidos": "Cuesta Juarez", "dni": "02544113U", "correo": "rosacj@email.com", 
        "password": "rosacj", "telefono": "647852015", "rol": "conductor"}

# Ruta que el administrador crea para realizar comprobaciones de listas
ruta1 = {"ciudades": "Madrid Guadalajara Zaragoza Barcelona"}
ruta2 = {"ciudades": "Leon Zamora Salamanca Caceres Merida"}

# Autobús que el administrador crea para realizar comprobaciones de listas
autobus_ejemplo = {"modelo": "Mercedes", "asientos": 35}

# Viajes que el administrador crea para comprobar listas
viaje1 = {"id": -1, "conductor": -1, "autobus": -1, "ruta": -1, "precio": 12.5}
viaje2 = {"id": -1, "conductor": -1, "autobus": -1, "ruta": -1, "precio": 12.6}
viaje3 = {"id": -1, "conductor": -1, "autobus": -1, "ruta": -1, "precio": 11.3}
viaje4 = {"id": -1, "conductor": -1, "autobus": -1, "ruta": -1, "precio": 14.0}

campos_verificables = ["nombre", "apellidos", "dni", "correo", "telefono", "rol"]

campos_billete = ["cliente", "viaje", "fechaSalida", "fechaLlegada", "asiento"]


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


# Función que introduce en la base de datos las siguientes listas:
#    cliente_ejemplo, billete1, billete2, billete3
#    conductor_ejemplo, autobus_ejemplo, viaje1, viaje2, viaje3, viaje4, ruta1, ruta2
def setup_data(client):

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

    # Se cambian el id asociado al cliente en cada billete
    billete_lleno["cliente"] = response.json()["id"]
    nuevo_billete["cliente"] = response.json()["id"]
    billete_fechaSalida_menor["cliente"] = response.json()["id"]
    billete_fechaLlegada_menor["cliente"] = response.json()["id"]
    billete_fechas_erroneas["cliente"] = response.json()["id"]
    billete_asiento_erroneo["cliente"] = response.json()["id"]
    set_billete["cliente"] = response.json()["id"]
    billete1["cliente"] = response.json()["id"]
    billete2["cliente"] = response.json()["id"]
    billete3["cliente"] = response.json()["id"]


    # El administrador inicia sesión
    access_token = login(admin_ejemplo, client)

    # Se crea conductor_ejemplo
    response = client.post(
        "http://127.0.0.1:8000/conductor/nuevo",
        headers={"accept": "application/json", "Authorization": "Bearer "+access_token},
        json=conductor_ejemplo
    )
    conductor_ejemplo["id"] = response.json()["id"]
    assert response.status_code == 200
    verificar_igualdad(response.json(), conductor_ejemplo)

    # Se crea autobus_ejemplo
    response = client.post(
        "http://127.0.0.1:8000/autobus/nuevo",
        headers={"accept": "application/json", "Authorization": "Bearer "+access_token},
        json=autobus_ejemplo
    )
    print("Autobus Request ", response.json())
    autobus_ejemplo["id"] = response.json()["id"]
    assert response.status_code == 200
    #verificar_igualdad(response.json(), autobus_ejemplo)

    # Se crea ruta1
    response = client.post(
        "http://127.0.0.1:8000/ruta/nueva",
        headers={"accept": "application/json", "Authorization": "Bearer "+access_token},
        json=ruta1
    )
    ruta1["id"] = response.json()["id"]
    assert response.status_code == 200
    #verificar_igualdad(response.json(), ruta1)

    # Se crea ruta2
    response = client.post(
        "http://127.0.0.1:8000/ruta/nueva",
        headers={"accept": "application/json", "Authorization": "Bearer "+access_token},
        json=ruta2
    )
    ruta2["id"] = response.json()["id"]
    assert response.status_code == 200
    #verificar_igualdad(response.json(), ruta2)

    # Se cambian los atributos de los viajes con los ids del conductor, el autobus y las rutas
    viaje_lleno["conductor"]=conductor_ejemplo["id"]
    viaje_lleno["autobus"]=autobus_ejemplo["id"]
    viaje_lleno["ruta"]=ruta1["id"]
    viaje1["conductor"]=conductor_ejemplo["id"]
    viaje1["autobus"]=autobus_ejemplo["id"]
    viaje1["ruta"]=ruta1["id"]
    viaje2["conductor"]=conductor_ejemplo["id"]
    viaje2["autobus"]=autobus_ejemplo["id"]
    viaje2["ruta"]=ruta1["id"]
    viaje3["conductor"]=conductor_ejemplo["id"]
    viaje3["autobus"]=autobus_ejemplo["id"]
    viaje3["ruta"]=ruta2["id"]
    viaje4["conductor"]=conductor_ejemplo["id"]
    viaje4["autobus"]=autobus_ejemplo["id"]
    viaje4["ruta"]=ruta2["id"]

    # Se crea viaje1
    response = client.post(
        "http://127.0.0.1:8000/viaje/nuevo",
        headers={"accept": "application/json", "Authorization": "Bearer "+access_token},
        json=viaje1
    )
    viaje1["id"] = response.json()["id"]
    billete1["viaje"] = response.json()["id"]
    assert response.status_code == 200
    #verificar_igualdad(response.json(), viaje1)

    # Se crea viaje2
    response = client.post(
        "http://127.0.0.1:8000/viaje/nuevo",
        headers={"accept": "application/json", "Authorization": "Bearer "+access_token},
        json=viaje2
    )
    viaje2["id"] = response.json()["id"]
    nuevo_billete["viaje"] = response.json()["id"]
    billete2["viaje"] = response.json()["id"]
    assert response.status_code == 200
    #verificar_igualdad(response.json(), viaje2)

    # Se crea viaje3
    response = client.post(
        "http://127.0.0.1:8000/viaje/nuevo",
        headers={"accept": "application/json", "Authorization": "Bearer "+access_token},
        json=viaje3
    )
    viaje3["id"] = response.json()["id"]
    billete3["viaje"] = response.json()["id"]
    assert response.status_code == 200
    #verificar_igualdad(response.json(), viaje3)

    # Se crea viaje4
    response = client.post(
        "http://127.0.0.1:8000/viaje/nuevo",
        headers={"accept": "application/json", "Authorization": "Bearer "+access_token},
        json=viaje4
    )
    viaje4["id"] = response.json()["id"]
    assert response.status_code == 200
    #verificar_igualdad(response.json(), viaje4)

    print("Viaje1 ", viaje1)
    print("Viaje2 ", viaje2)
    print("Viaje3 ", viaje3)
    print("Viaje4 ", viaje4)

    # El nuevo cliente inicia sesión
    access_token = login(cliente_ejemplo, client)

    # Se crea billete1
    response = client.post(
        "http://127.0.0.1:8000/billete/nuevo",
        headers={"accept": "application/json", "Authorization": "Bearer "+access_token},
        json=billete1
    )
    print("Response Billete1 ", response.json())
    assert response.status_code == 200
    billete1["id"] = response.json()["id"]
    verificar_igualdad(response.json(), billete1, campos=campos_billete)

    # Se crea billete2
    response = client.post(
        "http://127.0.0.1:8000/billete/nuevo",
        headers={"accept": "application/json", "Authorization": "Bearer "+access_token},
        json=billete2
    )
    assert response.status_code == 200
    billete2["id"] = response.json()["id"]
    verificar_igualdad(response.json(), billete2, campos=campos_billete)

    # Se crea billete3
    response = client.post(
        "http://127.0.0.1:8000/billete/nuevo",
        headers={"accept": "application/json", "Authorization": "Bearer "+access_token},
        json=billete3
    )
    assert response.status_code == 200
    billete3["id"] = response.json()["id"]
    verificar_igualdad(response.json(), billete3, campos=campos_billete)

# Función en la que el cliente incia sesión y comprueba los billetes que ha comprado, los puntos que ha ganado 
# y busca viajes con diferentes destinos
def testBilletesCliente(): # setup_data
    #client=setup_data
    client = requests

    # Se invoca a la función setup_data para que prepare la base de datos con la información necesaria
    setup_data(client)

    # El cliente inicia sesión en la aplicación
    access_token = login(cliente_ejemplo, client)

    # Se muestra el perfil del cliente
    response = requests.get(
        "http://127.0.0.1:8000/clientes/"+str(cliente_ejemplo["id"])+"/perfil",
        headers={"Authorization": "Bearer "+access_token})
    assert response.status_code == 200
    verificar_igualdad(response.json(), cliente_ejemplo)

    # Se muestran los puntos que ha ganado el cliente
    response = client.get(
        "http://127.0.0.1:8000/cliente/"+str(cliente_ejemplo["id"])+"/puntos",
        headers={"accept": "application/json", "Authorization": "Bearer "+access_token})
    print("Response ", response.json())
    assert response.status_code == 200
    assert response.json() == 364
    
    # Se muestran los billetes que ha comprado el cliente
    response = client.get(
        "http://127.0.0.1:8000/cliente/"+str(cliente_ejemplo["id"])+"/billetes/",
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
    response = client.get(
        "http://127.0.0.1:8000/viajes/origen/Madrid/destino/Almeria", 
        headers={"Authorization": "Bearer "+access_token})
    #print("Response ", response.json())
    assert response.status_code == 200
    assert response.json() == []

    # El cliente busca viajes con origen Barcelona y destino Madrid
    response = client.get(
        "http://127.0.0.1:8000/viajes/origen/Barcelona/destino/Madrid", 
        headers={"Authorization": "Bearer "+access_token})
    print("Response origen destino", response.json())
    assert response.status_code == 200
    viajes = {"viaje1": viaje1, "viaje2": viaje2}
    array_viajes = ["viaje1", "viaje2"]
    cont = 0
    for viaje in response.json():
        verificar_igualdad(viaje, viajes[array_viajes[cont]], campos={"conductor", "autobus", "ruta", "precio"})
        cont = cont+1
    

    # El cliente busca viajes con origen Leon y destino Salamanca
    response = client.get(
        "http://127.0.0.1:8000/viajes/origen/Leon/destino/Salamanca", 
        headers={"Authorization": "Bearer "+access_token})
    print("Response ", response.json())
    assert response.status_code == 200
    assert response.json() == [
                                viaje3, 
                                viaje4
                              ]


# Función que simula la compra de un billete por parte del cliente, su posterior modificación y su eliminación
def testComprarBillete():
    #client=setup_data
    client=requests

    # Inicio de sesión del cliente
    access_token=login(cliente_ejemplo, client)

    # Compra de billetes con fecha de salida menor que la actual
    response = client.post(
        "http://127.0.0.1:8000/billete/nuevo",
        headers={"accept": "application/json", "Authorization": "Bearer "+access_token},
        json=billete_fechaSalida_menor
    )
    print("Response Fecha Salida Menor ", response.json())
    assert response.status_code == 422

    # Compra de billetes con fecha de llegada menor que la actual
    response = client.post(
        "http://127.0.0.1:8000/billete/nuevo",
        headers={"accept": "application/json", "Authorization": "Bearer "+access_token},
        json=billete_fechaLlegada_menor
    )
    assert response.status_code == 422

    # Compra de billetes con fecha de llegada menor que la fecha de salida
    response = client.post(
        "http://127.0.0.1:8000/billete/nuevo",
        headers={"accept": "application/json", "Authorization": "Bearer "+access_token},
        json=billete_fechas_erroneas
    )
    assert response.status_code == 422

    # Compra de billetes con el asiento no disponible
    response = client.post(
        "http://127.0.0.1:8000/billete/nuevo",
        headers={"accept": "application/json", "Authorization": "Bearer "+access_token},
        json=billete_asiento_erroneo
    )
    assert response.status_code == 422

    # Compra del billete
    response = client.post(
        "http://127.0.0.1:8000/billete/nuevo",
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
        "http://127.0.0.1:8000/cliente/"+str(cliente_ejemplo["id"])+"/puntos",
        headers={"accept": "application/json", "Authorization": "Bearer "+access_token})
    #print("Response ", response.json())
    assert response.status_code == 200
    assert response.json() == 490

    # El cliente busca los asientos ocupados del viaje relacionado con el nuevo billete
    response = client.get(
        "http://127.0.0.1:8000/viaje/"+str(nuevo_billete["viaje"])+"/billetes/", 
        headers={"accept": "application/json", "Authorization": "Bearer "+access_token})
    print("Response Asientos Ocupados ", response.json())
    assert response.status_code == 200
    #otro_billete = {"id": nuevo_billete["id"]+1, "cliente": cliente_ejemplo["id"], "viaje": 2, "fechaSalida": "2022-04-10T16:30:00", 
    #                "fechaLlegada": "2022-04-10T21:00:00", "asiento": 30}
    billetes = {"billete2": billete2, "nuevo_billete": nuevo_billete}
    array_billetes = ["billete2", "nuevo_billete"]
    cont = 0
    for billete in response.json():
        verificar_igualdad(billete, billetes[array_billetes[cont]], campos=campos_billete, exclude=["id"])
        cont = cont+1

     # El cliente busca los asientos libres del viaje relacionado con el nuevo billete
    response = client.get(
        "http://127.0.0.1:8000/viaje/"+str(nuevo_billete["viaje"])+"/asientos/", 
    headers={"accept": "application/json", "Authorization": "Bearer "+access_token})
    print("Response Asientos Libres ", response.json())
    assert response.status_code == 200
    assert response.json() == [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 17, 18, 
                                19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 32, 33, 34, 35]

    # Modificación del billete con fecha de salida menor que la fecha actual
    response = client.patch(
        "http://127.0.0.1:8000/billetes/"+str(nuevo_billete["id"])+"/editar",
        headers={"accept": "application/json", "Authorization": "Bearer "+access_token},
        json={"fechaSalida": "2022-01-20T16:30:00"}
    )
    assert response.status_code == 422

    # Modificación del billete con fecha de llegada menor que la fecha actual
    response = client.patch(
        "http://127.0.0.1:8000/billetes/"+str(nuevo_billete["id"])+"/editar",
        headers={"accept": "application/json", "Authorization": "Bearer "+access_token},
        json={"fechaLlegada": "2022-01-20T16:30:00"}
    )
    assert response.status_code == 422

    # Modificación del billete con fecha de llegada menor que fecha de salida
    response = client.patch(
        "http://127.0.0.1:8000/billetes/"+str(nuevo_billete["id"])+"/editar",
        headers={"accept": "application/json", "Authorization": "Bearer "+access_token},
        json={"fechaSalida": "2022-08-20T19:30:00", "fechaLlegada": "2022-08-20T16:30:00"}
    )
    assert response.status_code == 422

    # Modificación del billete con un asiento ya reservado
    response = client.patch(
        "http://127.0.0.1:8000/billetes/"+str(nuevo_billete["id"])+"/editar",
        headers={"accept": "application/json", "Authorization": "Bearer "+access_token},
        json={"asiento": 31}
    )
    print("Billete Set Asiento ", nuevo_billete)
    print("Response Set Asiento ", response.json())
    assert response.status_code == 400

    # Modificación del billete
    response = client.patch(
        "http://127.0.0.1:8000/billetes/"+str(nuevo_billete["id"])+"/editar",
        headers={"accept": "application/json", "Authorization": "Bearer "+access_token},
        json=set_billete
    )
    assert response.status_code == 200
    verificar_igualdad(response.json(), set_billete, campos=campos_billete)

    # Observar la duración del viaje
    response = client.get(
        "http://127.0.0.1:8000/cliente/billete/"+str(nuevo_billete["id"])+"/duracion",
        headers={"accept": "application/json", "Authorization": "Bearer "+access_token})
    #print ("Response Duracion ", response.json())
    assert response.status_code == 200
    assert str(response.json()) == "03:00:00"    

    # Eliminar el billete que el cliente ha creado
    response = client.delete(
        "http://127.0.0.1:8000/cliente/"+str(nuevo_billete["cliente"])+"/billete/"+str(nuevo_billete["id"])+"/borrar",
        headers={"accept": "application/json", "Authorization": "Bearer "+access_token}
    )
    assert response.status_code == 200

    # Observar los billetes que ha comprado el cliente
    response = client.get(
        "http://127.0.0.1:8000/cliente/"+str(cliente_ejemplo["id"])+"/billetes/",
        headers={"Authorization": "Bearer "+access_token})
    assert response.status_code == 200
    print("Response billetes ", response.json())

# Función que crea un autobús con una sola plaza para comprobar que no se puede comprar un billete
# si el autobús está lleno
def testBilleteAutobusLleno(): # setup_data
    #client=setup_data
    client=requests

    # El administrador inicia sesión en la aplicación
    access_token = login(admin_ejemplo, client)

    # Se crea el autobús de una plaza
    response = client.post(
        "http://127.0.0.1:8000/autobus/nuevo",
        headers={"accept": "application/json", "Authorization": "Bearer "+access_token},
        json=autobus_lleno
    )
    print("Response Autobus Lleno ", response.json())
    assert response.status_code == 200
    viaje_lleno["autobus"] = response.json()["id"]
    verificar_igualdad(response.json(), autobus_lleno, campos=["modelo", "asientos"], exclude=["id", "asientosLibres"])

    # Se crea el viaje con el autobús lleno
    response = client.post(
        "http://127.0.0.1:8000/viaje/nuevo",
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
        "http://127.0.0.1:8000/billete/nuevo",
        headers={"accept": "application/json", "Authorization": "Bearer "+access_token},
        json=billete_lleno
    )
    assert response.status_code == 200
    verificar_igualdad(response.json(), billete_lleno, campos=campos_billete, exclude=["id"])

    # El cliente vuelve a comprar el mismo billete
    response = client.post(
        "http://127.0.0.1:8000/billete/nuevo",
        headers={"accept": "application/json", "Authorization": "Bearer "+access_token},
        json=billete_lleno
    )
    print("RESPONSE JSON ", response.json())
    assert response.status_code == 400

def xtestBorrado():

    client=requests

    # El cliente inicia sesión en la aplicación
    access_token = login(cliente_ejemplo, client)

    # Se eliminan los billetes de ejemplo que el cliente ha creado
    response = client.delete(
        "http://127.0.0.1:8000/cliente/1/billete/1/borrar",
        headers={"accept": "application/json", "Authorization": "Bearer "+access_token}
    )
    assert response.status_code == 200
    response = client.delete(
        "http://127.0.0.1:8000/cliente/1/billete/2/borrar",
        headers={"accept": "application/json", "Authorization": "Bearer "+access_token}
    )
    assert response.status_code == 200
    response = client.delete(
        "http://127.0.0.1:8000/cliente/1/billete/3/borrar",
        headers={"accept": "application/json", "Authorization": "Bearer "+access_token}
    )
    assert response.status_code == 200
    response = client.delete(
        "http://127.0.0.1:8000/cliente/1/billete/4/borrar",
        headers={"accept": "application/json", "Authorization": "Bearer "+access_token}
    )
    assert response.status_code == 200

    # El administrador inicia sesión en la aplicación
    access_token = login(admin_ejemplo, client)

    # Se eliminan los viajes de ejemplo que el administrador ha creado
    response = client.delete( 
        "http://127.0.0.1:8000/administrador/2/viaje/1/borrar",
        headers={"accept": "application/json", "Authorization": "Bearer "+access_token}
    )
    assert response.status_code == 200
    response = client.delete( 
        "http://127.0.0.1:8000/administrador/2/viaje/2/borrar",
        headers={"accept": "application/json", "Authorization": "Bearer "+access_token}
    )
    assert response.status_code == 200
    response = client.delete( 
        "http://127.0.0.1:8000/administrador/2/viaje/3/borrar",
        headers={"accept": "application/json", "Authorization": "Bearer "+access_token}
    )
    assert response.status_code == 200
    response = client.delete( 
        "http://127.0.0.1:8000/administrador/2/viaje/4/borrar",
        headers={"accept": "application/json", "Authorization": "Bearer "+access_token}
    )
    assert response.status_code == 200
    response = client.delete( 
        "http://127.0.0.1:8000/administrador/2/viaje/5/borrar",
        headers={"accept": "application/json", "Authorization": "Bearer "+access_token}
    )
    assert response.status_code == 200

    # Se eliminan las rutas de ejemplo que el administrador ha creado
    response = client.delete( 
        "http://127.0.0.1:8000/administrador/2/ruta/1/borrar",
        headers={"accept": "application/json", "Authorization": "Bearer "+access_token}
    )
    assert response.status_code == 200
    response = client.delete( 
        "http://127.0.0.1:8000/administrador/2/ruta/2/borrar",
        headers={"accept": "application/json", "Authorization": "Bearer "+access_token}
    )
    assert response.status_code == 200

    # Se eliminan los autobuses de ejemplo que el administrador ha creado
    response = client.delete( 
        "http://127.0.0.1:8000/administrador/2/autobus/1/borrar",
        headers={"accept": "application/json", "Authorization": "Bearer "+access_token}
    )
    assert response.status_code == 200
    response = client.delete( 
        "http://127.0.0.1:8000/administrador/2/autobus/2/borrar",
        headers={"accept": "application/json", "Authorization": "Bearer "+access_token}
    )
    assert response.status_code == 200

    # Se elimina el administrador de ejemplo
    response = client.delete( 
        "http://127.0.0.1:8000/administrador/2/borrar",
        headers={"accept": "application/json", "Authorization": "Bearer "+access_token}
    )
    assert response.status_code == 200

    # Inicia sesión el conductor de ejemplo
    access_token = login(conductor_ejemplo, client)

    # Se elimina el conductor de ejemplo
    response = client.delete( 
        "http://127.0.0.1:8000/conductor/3/borrar",
        headers={"accept": "application/json", "Authorization": "Bearer "+access_token}
    )
    assert response.status_code == 200

    # Inicia sesión el cliente de ejemplo
    access_token = login(cliente_ejemplo, client)

    # Se elimina el cliente de ejemplo
    response = client.delete( 
        "http://127.0.0.1:8000/cliente/1/borrar",
        headers={"accept": "application/json", "Authorization": "Bearer "+access_token}
    )
    assert response.status_code == 200
