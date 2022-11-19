from re import I
from typing import List

from fastapi import Depends, FastAPI, HTTPException, status, Header
from sqlalchemy.orm import Session

from . import model
from . import crud
from . import schema

from .database import SessionLocal, engine
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt


model.Base.metadata.create_all(bind=engine)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
TIEMPO_EXPIRACION = 30

app = FastAPI(docs_url="/autobuses/docs", redoc_url="/autobuses/redocs", openapi_url="/autobuses/openapi.json")

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_usuario_login(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    print("token antes decode: ", token)
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciales erróneas",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        print("token decode: ", token)
        payload = crud.decodeToken(token)
        usuario: str = payload.get("sub")
        rol: str = payload.get("rol")
        if usuario is None:
            raise credentials_exception
        token_data = schema.TokenData(usuario=usuario)
    except JWTError:
        raise credentials_exception
    user = crud.getUserCorreo(db, correo=token_data.usuario)
    if user is None:
        raise credentials_exception
    return user


async def get_administrador_activo(administradorActivo: schema.AdministradorFull = Depends(get_usuario_login)):
    tokenData = schema.TokenData(usuario=administradorActivo.correo, rol="administrador")
    if tokenData is None:
        raise HTTPException(status_code=400, detail="Administrador inactivo")
    if not isinstance(administradorActivo, model.Administrador):
        raise HTTPException(status_code=400, detail="Administrador no identificado")
    return administradorActivo


# Metodos POST

@app.post("/autobus/nuevo", response_model=schema.AutobusFull)
def crear_autobus(autobus: schema.AutobusBase, user: Session = Depends(get_administrador_activo), db: Session = Depends(get_db)):
    print("Autobus ", autobus)
    if autobus.asientos <= 0:
        raise HTTPException(status_code=422, detail="Número de asientos menor o igual que 0")
    if hasattr(autobus, "id"):
        db_autobus = crud.getAutobus(db, id=autobus.id)
        if db_autobus:
            raise HTTPException(status_code=400, detail="Autobus ya creado")
    try:
        return crud.crearAutobus(db=db, autobus=autobus)
    except:
        raise HTTPException(status_code=500, detail="Fallo interno del servidor")

@app.post("/ruta/nueva", response_model=schema.RutaFull)
def crear_ruta(ruta: schema.RutaBase, user: Session = Depends(get_administrador_activo), db: Session = Depends(get_db)):
    if ruta.ciudades == "":
        raise HTTPException(status_code=422, detail="No se han introducido ciudades")
    if hasattr(ruta, "id"):
        db_ruta = crud.getRuta(db, id=ruta.id)
        if db_ruta:
            raise HTTPException(status_code=400, detail="Ruta ya creada")
    try:
        return crud.crearRuta(db=db, ruta=ruta)
    except:
        raise HTTPException(status_code=500, detail="Fallo interno del servidor")

# Metodos GET

@app.get("/rutas/{idRuta}", response_model=schema.RutaFull)
def get_ruta(idRuta, db: Session = Depends(get_db)): #, user: Session = Depends(get_cliente_activo)
    try:
        db_ruta = crud.getRuta(db, idRuta)
    except:
        raise HTTPException(status_code=500, detail="Fallo interno del servidor")
    if db_ruta is None:
        raise HTTPException(status_code=404, detail="Ruta no encontrada")
    return db_ruta

@app.get("/autobuses/{idAutobus}", response_model=schema.AutobusFull, include_in_schema=False)
def get_autobus(idAutobus, db: Session = Depends(get_db)):
    try:
        return crud.getAutobus(db, idAutobus)
    except:
        raise HTTPException(status_code=500, detail="Fallo interno del servidor")

@app.get("/autobuses/", response_model=List[schema.AutobusFull])
def get_autobuses(skip: int = 0, limit: int = 100, user: Session = Depends(get_administrador_activo), db: Session = Depends(get_db)):
    try:
        autobuses = crud.getAutobuses(db, skip=skip, limit=limit)
        return autobuses
    except:
        raise HTTPException(status_code=500, detail="Fallo interno del servidor")

@app.get("/rutas/", response_model=List[schema.RutaFull])
def get_rutas(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    try:
        rutas = crud.getRutas(db, skip=skip, limit=limit)
        return rutas
    except:
        raise HTTPException(status_code=500, detail="Fallo interno del servidor")


# Metodos PATCH

@app.patch("/autobuses/{idAutobus}/editar", response_model=schema.AutobusFull)
def set_autobus(idAutobus, newAutobus: schema.AutobusSet, user: Session = Depends(get_administrador_activo), db: Session = Depends(get_db)):
    if str(user.rol)!="administrador":
        raise HTTPException(status_code=401, detail="Acceso no autorizado")
    db_autobus = crud.getAutobus(db, idAutobus=idAutobus)
    if newAutobus.asientos is not None and newAutobus.asientosLibres is not None:
        if newAutobus.asientos<=0 or newAutobus.asientosLibres<=0:
            raise HTTPException(status_code=422, detail="Número de asientos erróneo")
        if newAutobus.asientosLibres > newAutobus.asientos:
            raise HTTPException(status_code=422, detail="No puede haber más asientos libres que asientos")
        if db_autobus is None:
            raise HTTPException(status_code=404, detail="Autobus no encontrado")
    try:
        return crud.updateAutobus(db, idAutobus, newAutobus)
    except:
        raise HTTPException(status_code=500, detail="Fallo interno del servidor")

@app.patch("/rutas/{idRuta}/editar", response_model=schema.RutaFull)
def set_ruta(idRuta, newRuta: schema.RutaSet, user: Session = Depends(get_administrador_activo), db: Session = Depends(get_db)):
    if str(user.rol)!="administrador":
        raise HTTPException(status_code=401, detail="Acceso no autorizado")
    db_ruta = crud.getRuta(db, idRuta=idRuta)
    print("New Ruta ", newRuta)
    print("Ruta Main ", db_ruta)
    if db_ruta is None:
        raise HTTPException(status_code=404, detail="Ruta no encontrada")
    if newRuta.ciudades == "":
        raise HTTPException(status_code=422, detail="No hay ciudades")
    try:
        return crud.updateRuta(db, idRuta, newRuta)
    except:
        raise HTTPException(status_code=500, detail="Fallo interno del servidor")

@app.patch("/autobuses/{idAutobus}/asientos", include_in_schema=False)
def set_autobus_asientos(idAutobus, db: Session = Depends(get_db)):
    return crud.updateAutobusAsientos(db, idAutobus)

# Metodos DELETE

@app.delete("/autobus/{idAutobus}/borrar", response_model=schema.AutobusFull, include_in_schema=False)
def delete_autobus(idAutobus, db: Session = Depends(get_db)):
    try:
        crud.deleteAutobus(db, idAutobus)
        #crud.commit(db)
    except:
        crud.rollback(db)
        raise HTTPException(status_code=500, detail="Fallo interno del servidor")

@app.delete("/ruta/{idRuta}/borrar", response_model=schema.RutaFull, include_in_schema=False)
def delete_ruta(idRuta, db: Session = Depends(get_db)):
    try:
        crud.deleteRuta(db, idRuta)
        #crud.commit(db)
    except:
        crud.rollback(db)
        raise HTTPException(status_code=500, detail="Fallo interno del servidor")

