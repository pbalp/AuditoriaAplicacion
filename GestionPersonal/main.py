from re import I
from typing import List

from fastapi import Depends, FastAPI, HTTPException, status
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

app = FastAPI(docs_url="/administrador/docs", redoc_url="/administrador/redocs", openapi_url="/administrador/openapi.json")

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


async def get_conductor_activo(conductorActivo: schema.ConductorFull = Depends(get_usuario_login)):
    tokenData = schema.TokenData(usuario=conductorActivo.correo, rol="conductor")
    if tokenData is None:
        raise HTTPException(status_code=400, detail="Conductor inactivo")
    if not isinstance(conductorActivo, model.Conductor):
        raise HTTPException(status_code=400, detail="Conductor no identificado")
    return conductorActivo

async def get_administrador_activo(administradorActivo: schema.AdministradorFull = Depends(get_usuario_login)):
    tokenData = schema.TokenData(usuario=administradorActivo.correo, rol="administrador")
    if tokenData is None:
        raise HTTPException(status_code=400, detail="Administrador inactivo")
    if not isinstance(administradorActivo, model.Administrador):
        raise HTTPException(status_code=400, detail="Administrador no identificado")
    return administradorActivo


# Metodos POST

@app.post("/administrador/nuevo", response_model=schema.AdministradorFull, include_in_schema=False)
def crear_administrador(administrador: schema.AdministradorBase, user: Session = Depends(get_administrador_activo), db: Session = Depends(get_db)):
    if hasattr(administrador, "id"):
        db_administrador = crud.getAdministrador(db, id=administrador.id)
        if db_administrador:
            raise HTTPException(status_code=400, detail="Administrador ya creado")
    try:
        return crud.crearAdministrador(db=db, administrador=administrador)
    except:
        raise HTTPException(status_code=500, detail="Fallo interno del servidor")

@app.post("/conductor/nuevo", response_model=schema.ConductorFull)
def crear_conductor(conductor: schema.User, user: Session = Depends(get_administrador_activo), db: Session = Depends(get_db)):
    if hasattr(conductor, "id"):
        db_conductor = crud.getConductor(db, id=conductor.id)
        if db_conductor:
            raise HTTPException(status_code=400, detail="Conductor ya creado")
    if len(conductor.dni)!=9:
        raise HTTPException(status_code=400, detail="DNI erróneo")  
    try:
        return crud.crearConductor(db=db, conductor=conductor)
    except:
        raise HTTPException(status_code=500, detail="Fallo interno del servidor")

# Metodos GET

@app.get("/administradores/{idAdministrador}/perfil", response_model=schema.AdministradorFull)
def get_admninistrador(idAdministrador, user: Session = Depends(get_administrador_activo), db: Session = Depends(get_db)):
    if str(idAdministrador)!=str(user.id):
        raise HTTPException(status_code=401, detail="Perfil no autorizado")
    try:
        db_administrador = crud.getAdministrador(db, idAdministrador=idAdministrador)
    except:
        raise HTTPException(status_code=500, detail="Fallo interno del servidor")
    if db_administrador is None:
        raise HTTPException(status_code=404, detail="Administrador no encontrado")
    return db_administrador

@app.get("/conductores/{idConductor}/perfil", response_model=schema.ConductorFull)
def get_conductor(idConductor, user: Session = Depends(get_conductor_activo), db: Session = Depends(get_db)):
    if str(idConductor)!=str(user.id):
        raise HTTPException(status_code=401, detail="Perfil no autorizado")
    try:
        db_conductor = crud.getConductor(db, idConductor=idConductor)
    except:
        raise HTTPException(status_code=500, detail="Fallo interno del servidor")
    if db_conductor is None:
        raise HTTPException(status_code=404, detail="Conductor no encontrado")
    return db_conductor

@app.get("/conductor/{idConductor}", response_model=schema.ConductorFull, include_in_schema=False)
def get_conductor(idConductor, db: Session = Depends(get_db)):
    try:
        db_conductor = crud.getConductor(db, idConductor=idConductor)
    except:
        raise HTTPException(status_code=500, detail="Fallo interno del servidor")
    if db_conductor is None:
        raise HTTPException(status_code=404, detail="Conductor no encontrado")
    return db_conductor

@app.get("/conductores/", response_model=List[schema.ConductorFull])
def get_conductores(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    try:
        conductores = crud.getConductores(db, skip=skip, limit=limit)
        return conductores
    except:
        raise HTTPException(status_code=500, detail="Fallo interno del servidor")

@app.get("/user/correo/{correo}", include_in_schema=False)
def get_user_correo(correo, db: Session = Depends(get_db)):
    try:
        return crud.getUserCorreo(db, correo)
    except:
        raise HTTPException(status_code=500, detail="Fallo interno del servidor")


# Metodos GET billetes y viajes

@app.get("/conductor/{idConductor}/viajes/", response_model=List[schema.ViajeFull])
def get_viajes_conductor(idConductor, skip: int = 0, limit = 100, user: Session = Depends(get_conductor_activo), db: Session = Depends(get_db)):
    if str(idConductor)!=str(user.id):
        raise HTTPException(status_code=401, detail="Acceso no autorizado")
    try:
        return crud.getViajesConductor(db=db, idConductor=idConductor, skip=skip, limit=limit)
    except:
        raise HTTPException(status_code=500, detail="Fallo interno del servidor")


# Metodos PATCH

@app.patch("/administrador/{idAdministrador}/editar", response_model=schema.AdministradorFull)
def set_administrador(idAdministrador, newAdministrador: schema.AdministradorSet, user: Session = Depends(get_administrador_activo), db: Session = Depends(get_db)):
    if str(idAdministrador)!=str(user.id):
        raise HTTPException(status_code=401, detail="Acceso no autorizado")
    db_administrador = crud.getAdministrador(db, idAdministrador=idAdministrador)
    if db_administrador is None:
        raise HTTPException(status_code=404, detail="Administrador no encontrado")
    try:
        return crud.updateAdministrador(db, idAdministrador, newAdministrador)
    except:
        raise HTTPException(status_code=500, detail="Fallo interno del servidor")

@app.patch("/conductores/{idConductor}/editar", response_model=schema.ConductorFull)
def set_conductor(idConductor, newConductor: schema.ConductorSet, user: Session = Depends(get_conductor_activo), db: Session = Depends(get_db)):
    if str(idConductor)!=str(user.id):
        raise HTTPException(status_code=401, detail="Acceso no autorizado")
    db_conductor = crud.getConductor(db, idConductor=idConductor)
    if db_conductor is None:
        raise HTTPException(status_code=404, detail="Conductor no encontrado")
    try:
        return crud.updateConductor(db, idConductor, newConductor)
    except:
        raise HTTPException(status_code=500, detail="Fallo interno del servidor")

# Metodos DELETE

@app.delete("/administrador/{idAdministrador}/borrar")
def delete_administrador(idAdministrador, user: Session = Depends(get_administrador_activo), db: Session = Depends(get_db)):
    if str(idAdministrador)!=str(user.id):
        raise HTTPException(status_code=401, detail="Acceso no autorizado")
    try:
        crud.deleteAdministrador(db, idAdministrador)
    except:
        raise HTTPException(status_code=500, detail="Fallo interno del servidor")

@app.delete("/conductor/{idConductor}/borrar")
def delete_conductor(idConductor, user: Session = Depends(get_conductor_activo), db: Session = Depends(get_db)):
    if str(idConductor)!=str(user.id):
        raise HTTPException(status_code=401, detail="Acceso no autorizado")
    try:
        crud.deleteConductor(db, idConductor)
    except:
        crud.rollback(db)
        raise HTTPException(status_code=500, detail="Fallo interno del servidor")


# Metodos DELETE billetes y viajes

@app.delete("/administrador/{idAdministrador}/viaje/{idViaje}/borrar")
def delete_viaje(idAdministrador, idViaje, user: Session = Depends(get_administrador_activo), db: Session = Depends(get_db)):
    if str(idAdministrador)!=str(user.id):
        raise HTTPException(status_code=401, detail="Acceso no autorizado")
    try:
        crud.deleteViaje(db, idViaje)
    except:
        raise HTTPException(status_code=500, detail="Fallo interno del servidor")


# Metodos DELETE autobuses y rutas

@app.delete("/administrador/{idAdministrador}/autobus/{idAutobus}/borrar")
def delete_autobus(idAdministrador, idAutobus, user: Session = Depends(get_administrador_activo), db: Session = Depends(get_db)):
    if str(idAdministrador)!=str(user.id):
        raise HTTPException(status_code=401, detail="Acceso no autorizado")
    try:
        status_code = crud.deleteAutobus(db, idAutobus)
        if status_code!=200:
            raise HTTPException(status_code=500, detail="Fallo interno del servidor")
    except:
        crud.rollback()
        raise HTTPException(status_code=500, detail="Fallo interno del servidor")

@app.delete("/administrador/{idAdministrador}/ruta/{idRuta}/borrar")
def delete_ruta(idAdministrador, idRuta, user: Session = Depends(get_administrador_activo), db: Session = Depends(get_db)):
    if str(idAdministrador)!=str(user.id):
        raise HTTPException(status_code=401, detail="Acceso no autorizado")
    try:
        status_code = crud.deleteRuta(db, idRuta)
        if status_code!=200:
            raise HTTPException(status_code=500, detail="Fallo interno del servidor")
    except:
        crud.rollback()
        raise HTTPException(status_code=500, detail="Fallo interno del servidor")

