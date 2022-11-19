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

def testCrearAutobus():
    response = client.post(
        "/autobus/",
        #headers={"X-Token": "coneofsilence"},
        json={"modelo": "AutobusTest1", "asientos": "45", "asientosLibres": "45"}
    )
    assert response.status_code == 200
    assert response.json() == {
        "modelo": "AutobusTest1",
        "asientos": "45",
        "asientosLibres": "45"
    }

def testCrearAutobusAsientosMal():
    response = client.post(
        "/autobus/",
        #headers={"X-Token": "coneofsilence"},
        json={"modelo": "AutobusTest1", "asientos": "-7", "asientosLibres": "45"}
    )
    assert response.status_code == 400

def testCrearAutobusAsientosLibresMal():
    response = client.post(
        "/autobus/",
        #headers={"X-Token": "coneofsilence"},
        json={"modelo": "AutobusTest1", "asientos": "45", "asientosLibres": "-8"}
    )
    assert response.status_code == 400

def testCrearAutobusAsientosLibresMayorAsientos():
    response = client.post(
        "/autobus/",
        #headers={"X-Token": "coneofsilence"},
        json={"modelo": "AutobusTest1", "asientos": "45", "asientosLibres": "50"}
    )
    assert response.status_code == 400

def TestSetModelo():
    client.patch(
        "/autobus/3/editar",
        json={"modelo": "Toyota"}
    )
    assert response.status_code == 200
    assert response.json()=={"modelo": "Toyota"}

def TestSetAsientos():
    client.patch(
        "/autobus/2/editar",
        json={"asientos": "40"}
    )
    assert response.status_code == 200
    assert response.json()=={"asientos": "40"}

def TestSetAsientosLibres():
    client.patch(
        "/autobus/3/editar",
        json={"asientosLibres": "40"}
    )
    assert response.status_code == 200
    assert response.json()=={"asientosLibres": "40"}
