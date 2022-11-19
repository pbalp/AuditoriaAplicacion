import json
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient
import csv, sqlite3
from sqlite3 import OperationalError
from datetime import timedelta
from pathlib import Path

from ..main import app, get_db
from ..database import Base
from .. import model, schema
from ..crud import crearToken, decodeToken, getClienteLogin

# SQLALCHEMY_DATABASE_URL = "mysql+pymysql://uo258740:rom31abi@localhost:3306/dbPruebas"
SQLALCHEMY_DATABASE_URL = "sqlite:///./test/sql_app.db"
# SQLALCHEMY_DATABASE_URL_2 = "sqlite:///./test/test.db"
SQLALCHEMY_DATABASE_URL_2 = "sqlite:///./test/test.db"  #/./test/test.db" sqlite://
CONNECT_ARGS = {"check_same_thread": False}

user={"correo": "", "password": "", "rol": ""}
token={"access_token": ""}
cont={"cont": 0}

@pytest.fixture(scope='module')
def setup_client():
    """Esta función prepara una base de datos para test, arranca la aplicación y crea un cliente
    para conectar con esa aplicación/base de datos.
    
    Todos los test que vayan a testear la API Rest y por tanto necesiten este cliente
    deben declarar esta función como parámetro. Por ejemplo:
    
    def test_comprar_billetes(setup_client):
        ...

    Pytest se asegurará de que esta función esté ejecutada antes de lanzar ese test y
    pasará como parámetro al test el resultado de esta función (el client), por tanto
    la función puede comenzar haciendo:

        client = setup_client
    """
    print("Fixture setup_client invocado")
    engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args=CONNECT_ARGS)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    model.Base.metadata.create_all(bind=engine)

    def override_get_db():
        try:
            db = TestingSessionLocal()
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)

    # Aqui debería inicializarse la base de datos con datos de ejemplo, 
    # de lo contrario estará vacía
    return client

"""
@pytest.fixture(scope='module')
def setup_client2():
    print("Fixture setup_client invocado")
    engine = create_engine(SQLALCHEMY_DATABASE_URL_2, connect_args=CONNECT_ARGS)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    model.Base.metadata.create_all(bind=engine)

    def override_get_db():
        try:
            db = TestingSessionLocal()
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)

    #if cont["cont"]==0: 
    #    setup_data()
    #    cont["cont"] = 1

    return client
"""

# @pytest.fixture(scope='session')
def setup_login(correo: str, password: str, rol: str):
    print("Fixture setup_login invocado")
    user["correo"] = correo
    user["password"] = password
    user["rol"] = rol

    access_token_expires = timedelta(minutes=30)
    token["access_token"] = crearToken(
    data={"sub": user["correo"], "rol": user["rol"]}, expires_delta=access_token_expires)

    return str(token["access_token"])

@pytest.fixture(scope='class')
def setup_token():
    """ Esta función crea una sesión para el usuario que inicia sesión y 
        mantiene esa sesión hasta que el usuario la cierra """

    print("Fixture setup_token invocado")
    print("Token ", token["access_token"])
    return str(token["access_token"])

@pytest.fixture(scope='module')
def setup_data():

    print("Fixture setup_data invocado")
    engine = create_engine(SQLALCHEMY_DATABASE_URL_2, connect_args=CONNECT_ARGS, poolclass=StaticPool)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    model.Base.metadata.create_all(bind=engine)

    def override_get_db():
        try:
            db = TestingSessionLocal()
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)

    # Aqui debería inicializarse la base de datos con datos de ejemplo, 
    # de lo contrario estará vacía
    db = TestingSessionLocal()
    path = Path("test/datos")

    clases = {
        "cliente": (model.Cliente, schema.ClienteFull),
        "conductor": (model.Conductor, schema.ConductorBase),
        "administrador": (model.Administrador, schema.AdministradorBase),
        "autobus": (model.Autobus, schema.AutobusFull),
        "ruta": (model.Ruta, schema.RutaFull),
        "viaje": (model.Viaje, schema.ViajeBase),
        "billete": (model.Billete, schema.BilleteBase)
    }

    with open(path / Path("datos_ejemplo.json")) as f:
        data = f.read()
        data = json.loads(data)
    for tipo, valores in data.items():
        ModelClass = clases[tipo][0]
        SchemaClass = clases[tipo][1]
        for v in valores:
            objeto = SchemaClass(**v)
            db.add(ModelClass(**objeto.dict()))
    db.commit()
    return client
