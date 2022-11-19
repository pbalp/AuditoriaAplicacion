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

def testCrearRuta():
    response = client.post(
        "/ruta/",
        #headers={"X-Token": "coneofsilence"},
        json={"numerociudades": "3", "ciudades": "Barcelona Valencia Alicante"}
    )
    assert response.status_code == 200
    assert response.json() == {
        "numerociudades": "3", 
        "ciudades": "Barcelona Valencia Alicante"
    }