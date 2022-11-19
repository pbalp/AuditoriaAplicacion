from re import I
from typing import List

from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy.orm import  Session

from . import model
from . import crud
from . import schema

from .database import SessionLocal, engine
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from jose import JWTError, jwt


model.Base.metadata.create_all(bind=engine)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
TIEMPO_EXPIRACION = 30

app = FastAPI(docs_url="/billetes/docs", redoc_url="/billetes/redocs", openapi_url="/billetes/openapi.json") # docs_url="/billetes/docs"

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

async def get_cliente_activo(clienteActivo: schema.ClienteFull = Depends(get_usuario_login)):
    tokenData = schema.TokenData(usuario=clienteActivo.correo, rol="cliente")
    if tokenData is None:
        raise HTTPException(status_code=400, detail="Cliente inactivo")
    if not isinstance(clienteActivo, model.Cliente):
        raise HTTPException(status_code=400, detail="Cliente no identificado")
    return clienteActivo

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

@app.post("/viaje/nuevo", response_model=schema.ViajeFull)
def crear_viaje(viaje: schema.ViajeBase, user: Session = Depends(get_administrador_activo), db: Session = Depends(get_db)):
    autobus = crud.getAutobus(db=db, idAutobus=viaje.autobus)
    ruta = crud.getRuta(db=db, idRuta=viaje.ruta)
    conductor = crud.getConductor(db=db, idConductor=viaje.conductor)
    if autobus is None:
        raise HTTPException(status_code=404, detail="Autobus no encontrado")
    if ruta is None:
        raise HTTPException(status_code=404, detail="Ruta no encontrada")
    if conductor is None:
        raise HTTPException(status_code=404, detail="Conductor no encontrado")
    if autobus.asientosLibres==0:
        raise HTTPException(status_code=400, detail="Autobus completo")
    if viaje.precio<=0:
        raise HTTPException(status_code=422, detail="El precio no puede ser negativo")
    if hasattr(viaje, "id"):
        db_viaje = crud.getViaje(db, id=viaje.id)
        if db_viaje:
            raise HTTPException(status_code=400, detail="Viaje ya creado")
    try:
        return crud.crearViaje(db=db, viaje=viaje)
    except:
        raise HTTPException(status_code=500, detail="Fallo interno del servidor")

@app.post("/billete/nuevo", response_model=schema.BilleteFull)
def crear_billete(billete: schema.BilleteBase, user: Session = Depends(get_cliente_activo), db: Session = Depends(get_db)):
    if str(billete.cliente)!=str(user.id):
        raise HTTPException(status_code=401, detail="Perfil no autorizado")
    if hasattr(billete, "id"):
        db_billete = crud.getBillete(db, id=billete.id)
        if db_billete:
            raise HTTPException(status_code=400, detail="Billete ya creado")
    db_viaje = crud.getViaje(db, billete.viaje)
    if db_viaje is None:
        raise HTTPException(status_code=400, detail="El viaje selecionado no existe")
    if crud.comprobarAutobusLleno(db, db_viaje.autobus) is False:
        raise HTTPException(status_code=400, detail="Autobús completo")
    if crud.comprobarAsiento(db, billete, billete.asiento) is False:
        raise HTTPException(status_code=422, detail="Asiento no disponible")
    if crud.comprobarAsientoAutobus(db, db_viaje.autobus, billete.asiento) is False:
        raise HTTPException(status_code=422, detail="Número de asiento mayor que asientos del autobús")
    if crud.comprobarFechas(db, billete.fechaSalida, billete.fechaLlegada) is False:
        raise HTTPException(status_code=422, detail="Fechas erróneas")
    try:
        return crud.crearBillete(db=db, billete=billete)
    except:
        raise HTTPException(status_code=500, detail="Fallo interno del servidor")

@app.post("/viaje/rollback/nuevo", response_model=schema.ViajeFull, include_in_schema=False)
def crear_viaje_rollback(viaje: schema.ViajeBase, db: Session = Depends(get_db)):
    if hasattr(viaje, "id"):
        db_viaje = crud.getViaje(db, id=viaje.id)
        if db_viaje:
            raise HTTPException(status_code=400, detail="Viaje ya creado")
    return crud.crearViaje(db=db, viaje=viaje)


# Metodos GET

@app.get("/viajes/", response_model=List[schema.ViajeFull])
def get_viajes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    try:
        viajes = crud.getViajes(db, skip=skip, limit=limit)
        return viajes
    except:
        raise HTTPException(status_code=500, detail="Fallo interno del servidor")

@app.get("/billetes/", response_model=List[schema.BilleteFull])
def get_billetes(skip: int = 0, limit: int = 100, user: Session = Depends(get_administrador_activo), db: Session = Depends(get_db)):
    try:
        billetes = crud.getBilletes(db, skip=skip, limit=limit)
        return billetes
    except:
        raise HTTPException(status_code=500, detail="Fallo interno del servidor")

@app.get("/viaje/{idViaje}/billetes/", response_model=List[schema.BilleteFull])
def get_asientos_ocupados(idViaje, skip: int = 0, limit: int = 100, user: Session = Depends(get_cliente_activo), db: Session = Depends(get_db)):
    db_viaje = crud.getViaje(db, idViaje)
    if db_viaje is None:
        raise HTTPException(status_code=404, detail="Viaje no encontrado")
    try:
        return crud.getAsientosOcupados(db=db, idViaje=idViaje, skip=skip, limit=limit)
    except:
        raise HTTPException(status_code=500, detail="Fallo interno del servidor")

@app.get("/viaje/{idViaje}/asientos/", response_model=List[int])
def get_asientos_libres(idViaje, skip: int = 0, limit = 100, user: Session = Depends(get_cliente_activo), db: Session = Depends(get_db)):
    db_viaje = crud.getViaje(db, idViaje)
    if db_viaje is None:
        raise HTTPException(status_code=404, detail="Viaje no encontrado")
    try:
        return crud.getAsientosLibres(db=db, idViaje=idViaje, skip=skip, limit=limit)
    except:
        raise HTTPException(status_code=500, detail="Fallo interno del servidor")



@app.get("/viajes/origen/{origen}/destino/{destino}", response_model=List[schema.ViajeFull])
def get_viajes_origen_destino(origen, destino, skip: int = 0, limit: int = 100, user: Session = Depends(get_cliente_activo), db: Session = Depends(get_db)):
    if origen is None:
        raise HTTPException(status_code=400, detail="Origen erróneo")
    if destino is None:
        raise HTTPException(status_code=400, detail="Destino erróneo")
    if origen==destino:
        raise HTTPException(status_code=400, detail="Origen y Destino iguales")
    try:
        return crud.getViajesOrigenDestino(db, origen, destino, skip, limit)
    except:
        raise HTTPException(status_code=500, detail="Fallo interno del servidor")

@app.get("/billetes/cliente/{idCliente}/skip/{skip}/limit/{limit}", response_model=List[schema.BilleteFull], include_in_schema=False)
def get_billetes_cliente(idCliente, skip, limit, db: Session = Depends(get_db)):
        return crud.getBilletesCliente(db=db, idCliente=idCliente, skip=skip, limit=limit)

@app.get("/viajes/conductor/{idConductor}/skip/{skip}/limit/{limit}", response_model=List[schema.ViajeFull], include_in_schema=False)
def get_viajes_conductor(idConductor, skip, limit, db: Session = Depends(get_db)):
        return crud.getViajesConductor(db=db, idConductor=idConductor, skip=skip, limit=limit)

@app.get("/billete/{idBillete}/cliente/{idCliente}", response_model=schema.BilleteFull, include_in_schema=False)
def get_billete(idBillete, idCliente, db: Session = Depends(get_db)):
        return crud.getBillete(db=db, idBillete=idBillete, idCliente=idCliente)

@app.get("/billete/{idBillete}", response_model=schema.BilleteFull, include_in_schema=False)
def get_billete(idBillete, db: Session = Depends(get_db)):
    return crud.getBillete(db=db, idBillete=idBillete)

@app.get("/viajes/autobus/{idAutobus}/skip/{skip}/limit/{limit}", response_model=List[schema.ViajeFull], include_in_schema=False)
def get_viajes_autobus(idAutobus, skip, limit, db: Session = Depends(get_db)):
        return crud.getViajesAutobus(db=db, idAutobus=idAutobus, skip=skip, limit=limit)

@app.get("/viajes/ruta/{idRuta}/skip/{skip}/limit/{limit}", response_model=List[schema.ViajeFull], include_in_schema=False)
def get_viajes_ruta(idRuta, skip, limit, db: Session = Depends(get_db)):
    return crud.getViajesRuta(db=db, idRuta=idRuta, skip=skip, limit=limit)


# Metodos PATCH

@app.patch("/viajes/{idViaje}/editar", response_model=schema.ViajeFull)
def set_viaje(idViaje, newViaje: schema.ViajeSet, user: Session = Depends(get_administrador_activo), db: Session = Depends(get_db)):
    if str(user.rol)!="administrador":
        raise HTTPException(status_code=401, detail="Acceso no autorizado")
    if newViaje.precio<=0:
        raise HTTPException(status_code=422, detail="El precio no puede ser negativo")
    db_viaje = crud.getViaje(db, idViaje=idViaje)
    if db_viaje is None:
        raise HTTPException(status_code=404, detail="Viaje no encontrado")
    try:
        return crud.updateViaje(db, idViaje, newViaje)
    except:
        raise HTTPException(status_code=500, detail="Fallo interno del servidor")

@app.patch("/billetes/{idBillete}/editar", response_model=schema.BilleteFull)
def set_billete(idBillete, newBillete: schema.BilleteSet, user: Session = Depends(get_cliente_activo), db: Session = Depends(get_db)):
    db_billete = crud.getBillete(db, idBillete=idBillete)
    if db_billete is None:
        raise HTTPException(status_code=404, detail="Billete no encontrado")
    set_billete = newBillete.dict()
    if set_billete["fechaSalida"] is None: 
        set_billete["fechaSalida"] = db_billete.fechaSalida
    if set_billete["fechaLlegada"] is None: 
        set_billete["fechaLlegada"] = db_billete.fechaLlegada

    if str(db_billete.cliente)!=str(user.id):
        raise HTTPException(status_code=401, detail="Acceso no autorizado")
    if set_billete["asiento"] is not None:
        if newBillete.viaje is None: newBillete.viaje = db_billete.viaje
        if crud.comprobarAsiento(db, newBillete, set_billete["asiento"]) is False:
            raise HTTPException(status_code=400, detail="Asiento no disponible")
        db_viaje = crud.getViaje(db, db_billete.viaje)
        if crud.comprobarAsientoAutobus(db, db_viaje.autobus, set_billete["asiento"]) is False:
            raise HTTPException(status_code=422, detail="Asiento no válido")
    if crud.comprobarFechas(db, set_billete["fechaSalida"], set_billete["fechaLlegada"]) is False:
            raise HTTPException(status_code=422, detail="Fechas erróneas")

    try:
        return crud.updateBillete(db, idBillete, newBillete)
    except:
        raise HTTPException(status_code=500, detail="Fallo interno del servidor")

# Metodos DELETE

@app.delete("/billete/{idBillete}/borrar", include_in_schema=False)
def delete_billete(idBillete, db: Session = Depends(get_db)): #, user: Session = Depends(get_cliente_activo)
    try:
        response = crud.deleteBillete(db, idBillete)
        crud.commit(db)
        return response
    except:
        crud.rollback(db)
        raise HTTPException(status_code=500, detail="Fallo interno del servidor")

@app.delete("/viaje/{idViaje}/borrar", include_in_schema=False)
def delete_viaje(idViaje, db: Session = Depends(get_db)):
    try:
        response = crud.deleteViaje(db, idViaje)
        crud.commit(db)
    except:
        crud.rollback(db)
        raise HTTPException(status_code=500, detail="Fallo interno del servidor")

@app.delete("/billetes/cliente/{idCliente}/borrar", include_in_schema=False)
def delete_billetes_cliente(idCliente, db: Session = Depends(get_db)):
    try:
        return crud.deleteBilletesCliente(db, idCliente)
    except:
        crud.rollback(db)
        raise HTTPException(status_code=500, detail="Fallo interno del servidor")

@app.delete("/viajes/autobus/{idAutobus}/borrar", include_in_schema=False)
def delete_viajes_autobus(idAutobus, db: Session = Depends(get_db)):
    try:
        return crud.deleteViajesAutobus(db, idAutobus)
    except:
        crud.rollback(db)
        raise HTTPException(status_code=500, detail="Fallo interno del servidor")

@app.delete("/viajes/ruta/{idRuta}/borrar", include_in_schema=False)
def delete_viajes_ruta(idRuta, db: Session = Depends(get_db)):
    try:
        return crud.deleteViajesRuta(db, idRuta)
    except:
        crud.rollback(db)
        raise HTTPException(status_code=500, detail="Fallo interno del servidor")

@app.delete("/viajes/conductor/{idConductor}/borrar", include_in_schema=False)
def delete_viajes_conductor(idConductor, db: Session = Depends(get_db)):
    try:
        return crud.deleteViajesConductor(db, idConductor)
    except:
        crud.rollback(db)
        raise HTTPException(status_code=500, detail="Fallo interno del servidor")

@app.get("/billetes/rollback", include_in_schema=False)
def rollback(db: Session = Depends(get_db)):
    try:
        crud.rollback(db)
        return 200
    except:
        raise HTTPException(status_code=500, detail="Fallo interno de la base de datos")

@app.get("/billetes/commit", include_in_schema=False)
def commit(db: Session = Depends(get_db)):
    try:
        crud.commit(db)
        return 200
    except:
        raise HTTPException(status_code=500, detail="Fallo interno de la base de datos")