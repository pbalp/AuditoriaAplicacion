import requests


nuevo_admin = {"id": 1, "nombre": "Admin", "apellidos": "Admin Admin", "dni": "12345678A", "correo": "admin@email.com", 
            "password": "admin", "telefono": "641002835", "rol": "administrador"}
#id_admin = {"id": -1}
password_admin  = {"password": ""}

# Parámetros que van a ser modificados del administrador
set_admin = {"nombre": "Natalia", "apellidos": "Castro Jerez", "dni": "71562248I",
            "password": "nataliacj", "telefono": "622335840"}


# Autobus que se va a añadir al sistema
nuevo_autobus = {"modelo": "Irizar", "asientos": 45}
id_autobus = {"id": -1}

# Conductor que se va a aladir al sistema
nuevo_conductor = {"id": -1, "nombre": "Alberto", "apellidos": "Hernandez Sanchez", "dni": "70769381F", "correo": "albertohs@email.com", 
            "password": "albertohs", "telefono": "604749270", "rol": "conductor"}

# Ruta que se va a añadir al sistema
nueva_ruta = {"ciudades": "Coruña Oviedo Gijon Santander Bilbao"}
id_ruta = {"id": -1}

# Viaje que se va a añadir al sistema
nuevo_viaje = {"conductor": -1, "autobus": id_autobus["id"], "ruta": id_ruta["id"], "precio": 14.30}
id_viaje = {"id": -1}

# Clases erróneas
autobus_erroneo_0 = {"modelo": "Error", "asientos": 0}
autobus_erroneo_menor = {"modelo": "Error", "asientos": -45}

ruta_erronea = {"ciudades": ""}

viaje_erroneo = {"conductor": -1, "autobus": -1, "ruta": -1, "precio": -12.80}

campos_verificables = ["nombre", "apellidos", "dni", "correo", "telefono", "rol"]

def verificar_igualdad(user1, user2, campos=campos_verificables, exclude=[]):
    for k in campos:
        if k in exclude:
            continue
        assert user1[k] == user2[k]

# Función que simula el inicio de sesión de un usuario
def login(user, client):
    response = client.post(
        "http://127.0.0.1:8000/token",
        headers={"accept": "application/json", "Content-type": "application/x-www-form-urlencoded"},
        data={"grant_type": "", "username": user["correo"], "password": user["password"], "scope": "", 
            "client_id": "", "client_secret": ""}
    )
    token = response.json()["access_token"]
    return token

# Función en la que se registra y se modifica el nuevo administrador
def testCrearModificarAdministrador():
    #client=setup_data
    client=requests

    # El administrador inicia sesión
    access_token = login(nuevo_admin, client)

    # Se muestra el perfil del nuevo administrador
    response = client.get(
        "http://127.0.0.1:8000/administradores/"+str(nuevo_admin["id"])+"/perfil",
        headers={"Authorization": "Bearer "+access_token})
    assert response.status_code == 200
    verificar_igualdad(response.json(), nuevo_admin)

    # Se modifican los atributos del neuvo administrador
    response = client.patch(
        "http://127.0.0.1:8000/administrador/"+str(nuevo_admin["id"])+"/editar",
        headers={"accept": "application/json", "Authorization": "Bearer "+access_token},
        json=set_admin
    )
    print("ID admin ", nuevo_admin["id"])
    print("Response ", response.json())
    assert response.status_code == 200
    verificar_igualdad(response.json(), set_admin, exclude=["correo", "rol"])

    # Se reestablecen los atributos del neuvo administrador
    response = client.patch(
        "http://127.0.0.1:8000/administrador/"+str(nuevo_admin["id"])+"/editar",
        headers={"accept": "application/json", "Authorization": "Bearer "+access_token},
        json=nuevo_admin
    )
    print("ID admin ", nuevo_admin["id"])
    print("Response ", response.json())
    assert response.status_code == 200
    verificar_igualdad(response.json(), nuevo_admin, exclude=["correo", "rol"])
    

# Función en la que el administrador ya registrado inicia sesión en la aplicación
def testCrearViaje(): # setup_data
    #client=setup_data
    client=requests

    # Se inicia la sesión del administrador
    access_token = login(nuevo_admin, client)

    # Se crea el nuevo conductor para realizar las pruebas con requests
    response = client.post(
        "http://127.0.0.1:8000/conductor/nuevo",
        headers={"accept": "application/json", "Authorization": "Bearer "+access_token},
        json=nuevo_conductor
    )
    print(response.json())
    nuevo_conductor["id"] = response.json()["id"]
    nuevo_viaje["conductor"] = response.json()["id"]
    viaje_erroneo["conductor"] = response.json()["id"]
    assert response.status_code == 200
    verificar_igualdad(response.json(), nuevo_conductor)

    print("Nuevo Admin ", nuevo_admin)
    print("Contraseña Antigua Admin ", password_admin["password"])
    print("Contraseña Nueva Admin ", nuevo_admin["password"])

    # Se crea un autobus erróneo cuyo número de asientos es igual a 0
    response = client.post(
        "http://127.0.0.1:8000/autobus/nuevo",
        headers={"accept": "application/json", "Authorization": "Bearer "+access_token},
        json=autobus_erroneo_0
    )
    assert response.status_code == 422

    # Se crea un autobus erróneo cuyo número de asientos es menor que 0
    response = client.post(
        "http://127.0.0.1:8000/autobus/nuevo",
        headers={"accept": "application/json", "Authorization": "Bearer "+access_token},
        json=autobus_erroneo_menor
    )
    assert response.status_code == 422

    # Se crea un autobus
    response = client.post(
        "http://127.0.0.1:8000/autobus/nuevo",
        headers={"accept": "application/json", "Authorization": "Bearer "+access_token},
        json=nuevo_autobus
    )
    print("Autobus Request ", response.json())
    id_autobus["id"] = response.json()["id"]
    nuevo_viaje["autobus"] = response.json()["id"]
    viaje_erroneo["autobus"] = response.json()["id"]
    assert response.status_code == 200
    verificar_igualdad(response.json(), nuevo_autobus, campos=["modelo", "asientos"])

    # Se crea una ruta que no tiene ciudades
    response = client.post(
        "http://127.0.0.1:8000/ruta/nueva",
        headers={"accept": "application/json", "Authorization": "Bearer "+access_token},
        json=ruta_erronea
    )
    assert response.status_code == 422

    # Se crea una ruta
    response = client.post(
        "http://127.0.0.1:8000/ruta/nueva",
        headers={"accept": "application/json", "Authorization": "Bearer "+access_token},
        json=nueva_ruta
    )
    print("Ruta Request ", response.json())
    id_ruta["id"] = response.json()["id"]
    nuevo_viaje["ruta"] = response.json()["id"]
    viaje_erroneo["ruta"] = response.json()["id"]
    assert response.status_code == 200
    verificar_igualdad(response.json(), nueva_ruta, campos=["ciudades"])
    assert response.json()["numeroCiudades"] == 5

    # Se crea un viaje cuyo precio tiene un valor negativo
    response = client.post(
        "http://127.0.0.1:8000/viaje/nuevo",
        headers={"accept": "application/json", "Authorization": "Bearer "+access_token},
        json=viaje_erroneo
    )
    assert response.status_code == 422

    # Se crea un viaje
    response = client.post(
        "http://127.0.0.1:8000/viaje/nuevo",
        headers={"accept": "application/json", "Authorization": "Bearer "+access_token},
        json=nuevo_viaje
    )
    print("Viaje ", response.text)
    id_viaje["id"] = response.json()["id"]
    assert response.status_code == 200
    verificar_igualdad(response.json(), nuevo_viaje, campos=["autobus", "conductor", "ruta", "precio"])

    # El autobus creado modifica el número de asientos a 0 y el número de asientos libres también
    response = client.patch(
        "http://127.0.0.1:8000/autobuses/"+str(id_autobus["id"])+"/editar",
        headers={"accept": "application/json", "Authorization": "Bearer "+access_token},
        json={"asientos": 0, "asientosLibres": 0}
    )
    print("Response ", response.json())
    assert response.status_code == 422

    # El autobus creado modifica el número de asientos por -45 y el número de asientos libres también
    response = client.patch(
        "http://127.0.0.1:8000/autobuses/"+str(id_autobus["id"])+"/editar",
        headers={"accept": "application/json", "Authorization": "Bearer "+access_token},
        json={"asientos": -45, "asientosLibres": -45}
    )
    print("Response ", response.json())
    assert response.status_code == 422

    # El autobus creado modifica el número de asientos por 50 y el número de asientos libres por 60
    response = client.patch(
        "http://127.0.0.1:8000/autobuses/"+str(id_autobus["id"])+"/editar",
        headers={"accept": "application/json", "Authorization": "Bearer "+access_token},
        json={"asientos": 50, "asientosLibres": 60}
    )
    print("Response ", response.json())
    assert response.status_code == 422

    # Se modifica el autobus creado
    response = client.patch(
        "http://127.0.0.1:8000/autobuses/"+str(id_autobus["id"])+"/editar",
        headers={"accept": "application/json", "Authorization": "Bearer "+access_token},
        json={"modelo": "Pegaso", "asientos": 60}
    )
    print("Response ", response.json())
    assert response.status_code == 200
    assert response.json()["modelo"] == "Pegaso"
    assert response.json()["asientos"] == 60

    # La ruta creada se modifica con un campos de ciudades vacío
    response = client.patch(
        "http://127.0.0.1:8000/rutas/"+str(id_ruta["id"])+"/editar",
        headers={"accept": "application/json", "Authorization": "Bearer "+access_token},
        json={"ciudades": ""}
    )
    assert response.status_code == 422

    # Se modifica la ruta creada
    response = client.patch(
        "http://127.0.0.1:8000/rutas/"+str(id_ruta["id"])+"/editar",
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
        "http://127.0.0.1:8000/viajes/"+str(id_viaje["id"])+"/editar",
        headers={"accept": "application/json", "Authorization": "Bearer "+access_token},
        json={"precio": -14.80}
    )
    assert response.status_code == 422

    # Se modifica el viaje creado
    response = client.patch(
        "http://127.0.0.1:8000/viajes/"+str(id_viaje["id"])+"/editar",
        headers={"accept": "application/json", "Authorization": "Bearer "+access_token},
        json={"autobus": id_autobus["id"], "ruta": id_ruta["id"], "precio": 14.80}
    )
    assert response.status_code == 200
    verificar_igualdad(response.json(), {"autobus": id_autobus["id"], "ruta": id_ruta["id"], "precio": 14.80}, campos=["autobus", "ruta", "precio"])

    # Se elimina el autobus creado
    response = client.delete(
        "http://127.0.0.1:8000/administrador/"+str(nuevo_admin["id"])+"/autobus/"+str(id_autobus["id"])+"/borrar",
        headers={"accept": "application/json", "Authorization": "Bearer "+access_token}
    )
    assert response.status_code == 200

    # Se elimina la ruta creada
    response = client.delete(
        "http://127.0.0.1:8000/administrador/"+str(nuevo_admin["id"])+"/ruta/"+str(id_ruta["id"])+"/borrar",
        headers={"accept": "application/json", "Authorization": "Bearer "+access_token}
    )
    assert response.status_code == 200

    # Se elimina el viaje creado
    response = client.delete(
        "http://127.0.0.1:8000/administrador/"+str(nuevo_admin["id"])+"/viaje/"+str(id_viaje["id"])+"/borrar",
        headers={"accept": "application/json", "Authorization": "Bearer "+access_token}
    )
    assert response.status_code == 200

# Funcion que comprueba que el administrador puede obtener los listados de todos los usuarios, rutas, autobuses y billetes
def testListasAdministrador(): # setup_data
    #client=setup_data
    client=requests

    # Se inicia la sesión del administrador
    access_token = login(nuevo_admin, client)

    # Obtener un listado de todos los clientes de la aplicación
    response = client.get(
        "http://127.0.0.1:8000/clientes/",
        headers={"Authorization": "Bearer "+access_token})
    print("Response Lista Clientes ", response.text)
    assert response.status_code == 200
    #verificar_igualdad(response.json(), nuevo_admin)

    # Obtener un listado de todos los conductores de la aplicación
    response = client.get(
        "http://127.0.0.1:8000/conductores/",
        headers={"Authorization": "Bearer "+access_token})
    assert response.status_code == 200
    #verificar_igualdad(response.json(), nuevo_admin)

    # Obtener un listado de todos los autobuses de la aplicación
    response = client.get(
        "http://127.0.0.1:8000/autobuses/",
        headers={"Authorization": "Bearer "+access_token})
    assert response.status_code == 200
    #verificar_igualdad(response.json(), nuevo_admin)

    # Obtener un listado de todos las rutas de la aplicación
    response = client.get(
        "http://127.0.0.1:8000/rutas/",
        headers={"Authorization": "Bearer "+access_token})
    assert response.status_code == 200
    #verificar_igualdad(response.json(), nuevo_admin)

    # Obtener un listado de todos los billetes de la aplicación
    response = client.get(
        "http://127.0.0.1:8000/billetes/",
        headers={"Authorization": "Bearer "+access_token})
    assert response.status_code == 200
    #verificar_igualdad(response.json(), nuevo_admin)

