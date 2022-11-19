import requests


nuevo_cliente = {"nombre": "Sergio", "apellidos": "López Serrano", "dni": "32006995Q", "correo": "sergiols@email.com", 
            "password": "sergiols", "telefono": "610885239", "rol": "cliente"}

nuevo_cliente2 = {"nombre": "UserPrueba", "apellidos": "User Prueba", "dni": "00000001A", "correo": "userPrueba@email.com", 
            "password": "test", "telefono": "630224558", "rol": "cliente"}

id_cliente = {"id": ""}
set_cliente = {"nombre": "Marcos", "apellidos": "Martínez Berjón", 
            "password": "marcosmb", "telefono": "699852004"}

campos_verificables = ["nombre", "apellidos", "dni", "correo", "telefono", "rol"]

def verificar_igualdad(user1, user2, campos=campos_verificables, exclude=[]):
    for k in campos:
        if k in exclude:
            continue
        assert user1[k] == user2[k]


# Función que simula el inicio de sesión del cliente
def login(user, client):
    response = client.post(
        "http://127.0.0.1:8000/token",
        headers={"accept": "application/json", "Content-type": "application/x-www-form-urlencoded"},
        data={"grant_type": "", "username": user["correo"], "password": user["password"], "scope": "", 
            "client_id": "", "client_secret": ""}
    )
    token = response.json()["access_token"]
    return token

# Función en la que un nuevo cliente se registra y se modifica en la aplicación
def testCrearModificarCliente(): # setup_data
    #client=setup_data
    client = requests

    # Se crea el nuevo cliente
    response = client.post(
        "http://127.0.0.1:8000/cliente/nuevo",
        json=nuevo_cliente
    )
    print("Response Requests ", response.json())
    id_cliente["id"] = response.json()["id"]
    #print("ID Cliente ", id_cliente["id"])
    assert response.status_code == 200
    verificar_igualdad(response.json(), nuevo_cliente)

    # El nuevo cliente inicia sesión
    access_token = login(nuevo_cliente, client)
    print("Access Token ", access_token)

    # Se muestra el perfil del nuevo cliente
    response = client.get(
        "http://127.0.0.1:8000/clientes/"+str(id_cliente["id"])+"/perfil",
        headers={"Authorization": "Bearer "+access_token})
    print("Response Perfil ", response.json())
    assert response.status_code == 200
    verificar_igualdad(response.json(), nuevo_cliente)

    # Se modifican los atributos del nuevo cliente
    response = client.patch(
        "http://127.0.0.1:8000/clientes/"+str(id_cliente["id"])+"/editar",
        headers={"accept": "application/json", "Authorization": "Bearer "+access_token},
        json=set_cliente
    )
    print("Response ", response.content)
    assert response.status_code == 200
    verificar_igualdad(response.json(), set_cliente, exclude=["dni", "correo", "rol"])

    # Se elimina el nuevo cliente
    response = client.delete(
        "http://127.0.0.1:8000/cliente/"+str(id_cliente["id"])+"/borrar", 
        headers={"accept": "application/json", "Authorization": "Bearer "+access_token}
    )
    assert response.status_code == 200