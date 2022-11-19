import requests


# Nuevo conductor que se va a registrar en el sistema
nuevo_conductor = {"nombre": "Victor", "apellidos": "Gutierrez Sánchez", "dni": "10000658M", "correo": "victorgs@email.com", 
            "password": "victorgs", "telefono": "666523017", "rol": "conductor"}
id_conductor = {"id": ""}
# Parámetros que van a ser modificados del conductor
set_conductor = {"apellidos": "Villafranca Berjón", "dni": "10052669W",
            "password": "victorvb", "telefono": "620111775"}

# Conductor que va a iniciar sesión en la aplicación (conductor con id 8)
conductor = {"id": 8, "nombre": "Carlos", "apellidos": "Sevilla Perez", "dni": "78933254T", "correo": "carlossp@email.com", 
            "password": "carlossp", "telefono": "644752331", "rol": "conductor"}

admin = {"id": 1, "nombre": "Admin", "apellidos": "Admin Admin", "dni": "12345678A", "correo": "admin@email.com", 
            "password": "admin", "telefono": "641002835", "rol": "administrador"}

# Viajes que el conductor tiene asignados
viaje1 = {"id": 1, "conductor": 8, "autobus": 4, "ruta": 2, "precio": 15}
viaje2 = {"id": 6, "conductor": 8, "autobus": 1, "ruta": 4, "precio": 12.60}
viaje3 = {"id": 8, "conductor": 8, "autobus": 3, "ruta": 1, "precio": 13.90}

viajes = {"viaje1": viaje1, "viaje2": viaje2, "viaje3": viaje3}

campos_verificables = ["nombre", "apellidos", "dni", "correo", "telefono", "rol"]
campos_viajes = ["conductor", "autobus", "ruta", "precio"]


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

# Función en la que se registra y modifica un nuevo conductor
def testCrearModificarConductor(): # setup_data
    #client=setup_data
    client=requests

    # El nuevo conductor inicia sesión
    access_token = login(admin, client)

    # Se registra el nuevo conductor
    response = client.post(
        "http://127.0.0.1:8000/conductor/nuevo",
        headers={"Authorization": "Bearer "+access_token},
        json=nuevo_conductor
    )
    print(response.json())
    id_conductor["id"] = response.json()["id"]
    assert response.status_code == 200
    verificar_igualdad(response.json(), nuevo_conductor)

    # El nuevo conductor inicia sesión
    access_token = login(nuevo_conductor, client)

    # Se muestra el perfil del nuevo conductor
    response = client.get(
        "http://127.0.0.1:8000/conductores/"+str(id_conductor["id"])+"/perfil",
        headers={"Authorization": "Bearer "+access_token})
    assert response.status_code == 200
    verificar_igualdad(response.json(), nuevo_conductor)

    # Se modifican los atributos del nuevo conductor
    response = client.patch(
        "http://127.0.0.1:8000/conductores/"+str(id_conductor["id"])+"/editar",
        headers={"accept": "application/json", "Authorization": "Bearer "+access_token},
        json=set_conductor
    )
    assert response.status_code == 200
    verificar_igualdad(response.json(), set_conductor, exclude=["nombre", "correo", "rol"])

    # Se elimina el nuevo conductor
    response = client.delete(
        "http://127.0.0.1:8000/conductor/"+str(id_conductor["id"])+"/borrar", 
        headers={"accept": "application/json", "Authorization": "Bearer "+access_token}
    )
    assert response.status_code == 200

# Función que simula las funciones que realiza un conductor ya registrado en la aplicación
def testFuncionesConductor(): # setup_data
    #client=setup_data
    client=requests

    # El administrador inicia sesión
    access_token = login(admin, client)

    # Se registra el nuevo conductor
    response = client.post(
        "http://127.0.0.1:8000/conductor/nuevo",
        headers={"Authorization": "Bearer "+access_token},
        json=conductor
    )
    print(response.json())
    conductor["id"] = response.json()["id"]
    assert response.status_code == 200
    verificar_igualdad(response.json(), conductor)

    # El conductor inicia sesión
    access_token = login(conductor, client)

    # Se muestra el perfil del conductor ya registrado
    response = client.get(
        "http://127.0.0.1:8000/conductores/"+str(conductor["id"])+"/perfil",
        headers={"Authorization": "Bearer "+access_token})
    assert response.status_code == 200
    verificar_igualdad(response.json(), conductor)

    # Se muestran los viajes asignados al conductor
    response = client.get(
        "http://127.0.0.1:8000/conductor/"+str(conductor["id"])+"/viajes/",
            headers={"Authorization": "Bearer "+access_token})
    print("Response viajes ", response.json())
    assert response.status_code == 200
    cont = 1
    for viaje in response.json():
        verificar_igualdad(viaje, viajes["viaje"+str(cont)], campos=campos_viajes)
        cont = cont+1



    