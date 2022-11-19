from re import I
from typing import List

from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy.orm import Session

from . import model
from . import crud
from . import schema

from .database import SessionLocal, engine
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from datetime import timedelta, datetime
import datetime

import requests
from jose import JWTError, jwt


model.Base.metadata.create_all(bind=engine)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
TIEMPO_EXPIRACION = 30

app = FastAPI(docs_url="/clientes/docs", redoc_url="/clientes/redocs", openapi_url="/clientes/openapi.json")

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_usuario_login(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciales erróneas",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
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


async def get_cliente_activo(clienteActivo: schema.ClienteFull = Depends(get_usuario_login)):
    tokenData = schema.TokenData(usuario=clienteActivo.correo, rol="cliente")
    if tokenData is None:
        raise HTTPException(status_code=400, detail="Cliente inactivo")
    if not isinstance(clienteActivo, model.Cliente):
        raise HTTPException(status_code=400, detail="Cliente no identificado")
    return clienteActivo

async def get_administrador_activo(administradorActivo: schema.AdministradorFull = Depends(get_usuario_login)):
    tokenData = schema.TokenData(usuario=administradorActivo.correo, rol="administrador")
    if tokenData is None:
        raise HTTPException(status_code=400, detail="Administrador inactivo")
    if not isinstance(administradorActivo, model.Administrador):
        raise HTTPException(status_code=400, detail="Administrador no identificado")
    return administradorActivo


# Metodos POST

@app.post("/cliente/nuevo", response_model=schema.ClienteFull)
def crear_cliente(cliente: schema.User, db: Session = Depends(get_db)):
    try:
        db_cliente = crud.getClienteDNI(db, dni=cliente.dni)
    except:
        raise HTTPException(status_code=500, detail="Fallo interno del servidor")
    if cliente.telefono is None: cliente.telefono = "666666666"
    if db_cliente:
        raise HTTPException(status_code=400, detail="Cliente ya creado")
    if len(cliente.dni)!=9:
        raise HTTPException(status_code=400, detail="DNI erróneo")
    try:
        return crud.crearCliente(db=db, cliente=cliente)
    except:
        raise HTTPException(status_code=500, detail="Fallo interno del servidor")

# Metodos GET

@app.get("/clientes/{idCliente}/perfil", response_model=schema.ClienteFull)
def get_cliente(idCliente, user: Session = Depends(get_cliente_activo), db: Session = Depends(get_db)):
    if str(idCliente)!=str(user.id):
        raise HTTPException(status_code=401, detail="Perfil no autorizado")
    try:
        db_cliente = crud.getCliente(db, idCliente=idCliente)
    except:
        raise HTTPException(status_code=500, detail="Fallo interno del servidor")
    if db_cliente is None:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return db_cliente

@app.get("/clientes/", response_model=List[schema.ClienteFull])
def get_clientes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    try:
        clientes = crud.getClientes(db, skip=skip, limit=limit)
    except:
        raise HTTPException(status_code=500, detail="Fallo interno del servidor")
    return clientes

@app.get("/cliente/{idCliente}/puntos")
def get_puntos(idCliente, user: Session = Depends(get_cliente_activo), db: Session = Depends(get_db)):
    cliente = crud.getCliente(db=db, idCliente=idCliente)
    if str(cliente.id)!=str(user.id):
        raise HTTPException(status_code=401, detail="Acceso no autorizado")
    if cliente.puntos is None:
        raise HTTPException(status_code=400, detail="Puntos no disponibles")
    try:
        return crud.getPuntosCliente(db=db, idCliente=idCliente)
    except:
        raise HTTPException(status_code=500, detail="Fallo interno del servidor")

@app.get("/user/correo/{correo}", include_in_schema=False)
def get_user_correo(correo, db: Session = Depends(get_db)):
    try:
        return crud.getUserCorreo(db, correo)
    except:
        raise HTTPException(status_code=500, detail="Fallo interno del servidor")

# Metodos GET billetes y viajes

@app.get("/cliente/{idCliente}/billete/{idBillete}", response_model=schema.BilleteFull)
def get_billete(idCliente, idBillete, user: Session = Depends(get_cliente_activo), db: Session = Depends(get_db)):
    if str(idCliente)!=str(user.id):
        raise HTTPException(status_code=401, detail="Acceso no autorizado")
    try:
        return crud.getBillete(db=db, idBillete=idBillete)
    except:
        raise HTTPException(status_code=500, detail="Fallo interno del servidor")

@app.get("/cliente/{idCliente}/billetes/", response_model=List[schema.BilleteFull])
def get_billetes_cliente(idCliente, skip: int = 0, limit: int = 100, user: Session = Depends(get_cliente_activo), db: Session = Depends(get_db)):
    if str(idCliente)!=str(user.id):
        raise HTTPException(status_code=401, detail="Acceso no autorizado")
    try:
        return crud.getBilletesCliente(db=db, idCliente=idCliente, skip=skip, limit=limit)
    except:
        raise HTTPException(status_code=500, detail="Fallo interno del servidor")

@app.get("/cliente/billete/{idBillete}/duracion")
def get_duracion(idBillete, user: Session = Depends(get_cliente_activo), db: Session = Depends(get_db)):
    billete = crud.getBillete(db=db, idBillete=idBillete)
    if str(billete.cliente)!=str(user.id):
        raise HTTPException(status_code=401, detail="Acceso no autorizado")
    if billete is None:
        raise HTTPException(status_code=404, detail="Billete no encontrado")
    cliente = crud.getCliente(db, billete.cliente)
    if str(cliente.correo) != str(user.correo):
        raise HTTPException(status_code=400, detail="El billete no pertenece al cliente")
    try:
        return crud.getDuracion(db=db, idBillete=idBillete)
    except:
        raise HTTPException(status_code=500, detail="Fallo interno del servidor")


# Metodos PATCH

@app.patch("/clientes/{idCliente}/editar", response_model=schema.ClienteFull)
def set_cliente(idCliente, newCliente: schema.ClienteSet, user: Session = Depends(get_cliente_activo), db: Session = Depends(get_db)):
    if str(idCliente)!=str(user.id):
        raise HTTPException(status_code=401, detail="Acceso no autorizado")
    db_cliente = crud.getCliente(db, idCliente=idCliente)
    if db_cliente is None:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    if newCliente.dni is not None:
        if len(newCliente.dni) != 9:
            raise HTTPException(status_code=400, detail="DNI incorrecto")
    if newCliente.correo is not None:
        raise HTTPException(status_code=422, detail="No se puede modificar el correo")
    if newCliente.rol is not None:
        raise HTTPException(status_code=422, detail="No se puede modificar el rol")

    try:
        return crud.updateCliente(db, idCliente, newCliente)
    except:
        raise HTTPException(status_code=500, detail="Fallo interno del servidor")

@app.patch("/cliente/{idCliente}/puntos/{newPuntos}", include_in_schema=False)
def set_cliente_puntos(idCliente, newPuntos, db: Session = Depends(get_db)):
    try:
        return crud.updateClientePuntos(db, idCliente, newPuntos)
    except:
        raise HTTPException(status_code=500, detail="Fallo interno del servidor")

# Metodos DELETE

@app.delete("/cliente/{idCliente}/borrar")
def delete_cliente(idCliente, user: Session = Depends(get_cliente_activo), db: Session = Depends(get_db)):
    if str(idCliente)!=str(user.id):
        raise HTTPException(status_code=401, detail="Acceso no autorizado")
    try:   
        crud.deleteCliente(db, idCliente)
    except:
        crud.rollback(db)
        raise HTTPException(status_code=500, detail="Fallo interno del servidor")

# Metodos DELETE billetes y viajes

@app.delete("/cliente/{idCliente}/billete/{idBillete}/borrar")
def delete_billete(idCliente, idBillete, user: Session = Depends(get_cliente_activo), db: Session = Depends(get_db)):
    billete = crud.getBillete(db, idBillete)
    if str(billete.cliente)!=str(user.id):
        raise HTTPException(status_code=401, detail="Acceso no autorizado")
    if billete is None:
        raise HTTPException(status_code=400, detail="Billete no encontrado")
    if str(billete.cliente)!=str(idCliente):
        raise HTTPException(status_code=422, detail="El billete no corresponde al cliente")
    try:
        crud.deleteBillete(db, idBillete)
        crud.commitBillete()
    except:
        raise HTTPException(status_code=500, detail="Fallo interno de la base de datos")

