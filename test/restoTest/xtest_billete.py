from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Crear database
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://uo258740:rom31abi@localhost:3306/db"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

def testCrearBillete():
    response = client.post(
        "/billete/",
        #headers={"X-Token": "coneofsilence"},
        json={"usuario": "2", "viaje": "1", "fechaSalida": "2022-04-18T17:00:00.000Z", "fechaLlegada": "2022-04-18T21:00:00.000Z", "asiento": "28"}
    )
    assert response.status_code == 200
    assert response.json() == {
        "usuario": "2",
        "viaje": "1",
        "fechaLlegada": "AutobusTest1",
        "fechaSalida": "45",
        "asiento": "45"
    }

def testBilleteAsientoReservado():
    response = client.post(
        "/billete/",
        json={"usuario": "4", "viaje": "5", "fechaSalida": "2022-04-22T23:00:00.000Z", "fechaLlegada": "2022-04-23T03:00:00.000Z", "asiento": "40"}
    )
    assert response.status_code == 400

def testBilleteFechasErroneas1():
    response = client.post(
        "/billete/",
        json={"usuario": "1", "viaje": "2", "fechaSalida": "2022-01-10T15:00:00.000Z", "fechaLlegada": "2022-01-10T18:00:00.000Z", "asiento": "9"}
    )
    assert response.status_code == 400

def testBilleteFechasErroneas2():
    response = client.post(
        "/billete/",
        json={"usuario": "3", "viaje": "4", "fechaSalida": "2022-06-10T10:30:00.000Z", "fechaLlegada": "2022-05-10T15:30:00.000Z", "asiento": "35"}
    )
    assert response.status_code == 400

def testBilleteSinAsiento():
    response = client.post(
        "/billete/"
        json={"usuario": "2", "viaje": "1", "fechaSalida": "2022-05-03T17:00:00.000Z", "fechaLlegada": "2022-05-03T22:00:00.000Z", "asiento": "70"}
    )
    assert response.status_code = 400

def testCrearAutobusLleno():
    response = client.post(
        "/autobus/nuevo",
        json={"modelo": "AutobusTestLleno", "asientosLibres": "1"}
    )
    assert response.status_code == 200
    assert response.json() == {
        "modelo": "AutobusTestLleno", 
        "asientosLibres": "1"
    }

def testCrearViajeAutobusLleno():
    response = client.post(
        "/viaje/nuevo",
        json={"conductor": "1", "autobus": "5", "ruta": "3", "precio": "10,00"}
    )
    assert response.status_code == 200
    assert response.json() == {
        "conductor": "1", 
        "autobus": "5",
        "ruta": "3", 
        "precio": "10,00"
    }

def testLlenarAutobus():
    response = client.post(
        "/billete/nuevo/",
        json={"usuario": "1", "viaje": "5", "fechaSalida": "2022-05-15T19:00:00.000Z", "fechaLlegada": "2022-05-15T23:00:00.000Z", "asiento": "1"}
    )
    assert response.status_code == 200
    assert response.json() == {
        "usuario": "1",
        "viaje": "5",
        "fechaSalida": "2022-05-15T19:00:00.000Z",
        "fechaLlegada": "2022-05-15T23:00:00.000Z",
        "asiento": "1"
    }

def testBilleteAutobusLleno():
    response = client.post(
        "/billete/nuevo/",
        json={"usuario": "3", "viaje": "5", "fechaSalida": "2022-05-15T19:00:00.000Z", "fechaLlegada": "2022-05-15T23:00:00.000Z", "asiento": "1"}
    )
    assert response.status_code == 400

def testCambiarFechaSalida():
    response = client.patch(
        "/billete/6/editar",
        json={"fechaSalida": "2022-03-04T12:30:00.000Z"}
    )
    assert response.status_code = 200
    assert response.json() == {
        "fechaSalida": "2022-03-04T12:30:00.000Z"
    }

def testCambiarFechaLlegada():
    response = client.patch(
        "/billete/6/editar",
        json={"fechaLlegada": "2022-03-09T18:00:00.000Z"}
    )
    assert response.status_code = 200
    assert response.json() == {
        "fechaLlegada": "2022-03-09T18:00:00.000Z"
    }

def testCambiarAsiento():
    response = client.patch(
        "/billete/6/editar",
        json={"asiento": "43"}
    )
    assert response.status_code = 200
    assert response.json() == {
        "asiento": "43"
    }

def testBorrarBillete():
    response = client.delete(
        "/billete/borrar/6"
    )
    assert response.status_code = 200

