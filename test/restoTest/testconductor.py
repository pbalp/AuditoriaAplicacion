def testCrearConductor():
    response = client.post(
        "/conductor/nuevo",
        #headers={"X-Token": "coneofsilence"},
        json={"nombre": "ConductorTest1", "apellidos": "Conductor Test1", "dni": "12345678C", "correo": "conductorTest1@email.com", 
            "contraseña": "test1", "telefono": "639528417", "rol": "conductor"}
    )
    assert response.status_code == 200
    #assert response.json() == {
    #    "nombre": "ConductorTest1", 
    #    "apellidos": "Conductor Test1", 
    #    "dni": "12345678C", 
    #    "correo": "conductorTest1@email.com", 
    #    "contraseña": "test1", 
    #    "telefono": "639528417"
    #}

def testCrearConductorMismoDNI():
    response = client.post(
        "/conductor/",
        #headers={"X-Token": "coneofsilence"},
        json={"nombre": "ConductorTest2", "apellidos": "Conductor Test2", "dni": "12345678C", 
            "correo": "conductorTest2@email.com", "contraseña": "test2", "telefono": "681230450"}
    )
    assert response.status_code == 400
