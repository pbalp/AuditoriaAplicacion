"""
from re import I
from typing import List, Optional

from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy.orm import Session

#import crud, model, schema
#import crud
#import model
#import schema

#import crud, model, schema
from . import crud # DEJARLO CON EL PUNTO Y EJECUTAR uvicorn modeloDatos.main:app --reload
from . import model # EL USUARIO NO PUEDE MODIFICAR SU EMAIL
from . import schema

from .database import SessionLocal, engine
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm # QUITAR OAUTH2
from datetime import timedelta, datetime

from jose import JWTError, jwt

model.Base.metadata.create_all(bind=engine)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
TIEMPO_EXPIRACION = 30

app = FastAPI()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# FUNCIONES DE LOGIN
#@app.get("/token/cliente", response_model = schema.ClienteFull)
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
    #if user is None:
    #    user = crud.getConductorCorreo(db, correo=token_data.usuario)
    #    if user is None:
    #        user = crud.getAdministradorCorreo(db, correo=token_data.usuario)
    if user is None:
        raise credentials_exception
    return user


# FUNCIONES DE CREAR
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


@app.post("/token", response_model=schema.Token)
async def comprobar_login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    usuario = crud.autenticarUsuario(db, form_data.username, form_data.password)
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Correo o password incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=TIEMPO_EXPIRACION)
    access_token = crud.crearToken(
        data={"sub": usuario.correo, "rol": usuario.rol}, expires_delta=access_token_expires
    )
    print("access_token: ", access_token)
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/administrador/nuevo", response_model=schema.AdministradorFull)
def crear_administrador(administrador: schema.AdministradorBase, db: Session = Depends(get_db)): # AdministradorBase
    #if administrador.telefono is None: administrador.telefono = "666666666"
    if hasattr(administrador, "id"):
        db_administrador = crud.getAdministrador(db, id=administrador.id)
        if db_administrador:
            raise HTTPException(status_code=400, detail="Administrador ya creado")
    return crud.crearAdministrador(db=db, administrador=administrador)

@app.post("/cliente/nuevo", response_model=schema.ClienteFull)
def crear_cliente(cliente: schema.User, db: Session = Depends(get_db)): #
    db_cliente = crud.getClienteDNI(db, dni=cliente.dni)
    if cliente.telefono is None: cliente.telefono = "666666666"
    print("Cliente telefono ", cliente.telefono)
    if db_cliente:
        raise HTTPException(status_code=400, detail="Cliente ya creado")
    if len(cliente.dni)!=9:
        raise HTTPException(status_code=400, detail="DNI erróneo")
    return crud.crearCliente(db=db, cliente=cliente)

@app.post("/conductor/nuevo", response_model=schema.ConductorFull)
def crear_conductor(conductor: schema.User, db: Session = Depends(get_db)): # ConductorBase
    print("Telefono Conductor 1 main ", conductor.telefono)
    if conductor.telefono is None: conductor.telefono = "666666666"
    print("Conductor main ", conductor)
    if hasattr(conductor, "id"):
        print("Conductor con id")
        db_conductor = crud.getConductor(db, id=conductor.id)
        if db_conductor:
            raise HTTPException(status_code=400, detail="Conductor ya creado")
    if len(conductor.dni)!=9:
        raise HTTPException(status_code=400, detail="DNI erróneo")  
    return crud.crearConductor(db=db, conductor=conductor)

@app.post("/autobus/nuevo", response_model=schema.AutobusFull)
def crear_autobus(autobus: schema.AutobusBase, user: Session = Depends(get_administrador_activo), db: Session = Depends(get_db)):
    print("Autobus ", autobus)
    if autobus.asientos <= 0:
        raise HTTPException(status_code=422, detail="Número de asientos menor o igual que 0")
    #if autobus.asientosLibres > autobus.asientos:
    #    raise HTTPException(status_code=400, detail="No puede haber más asientos libres que asientos")
    if hasattr(autobus, "id"):
        db_autobus = crud.getAutobus(db, id=autobus.id)
        if db_autobus:
            raise HTTPException(status_code=400, detail="Autobus ya creado")
    return crud.crearAutobus(db=db, autobus=autobus)

@app.post("/viaje/nuevo", response_model=schema.ViajeFull)
def crear_viaje(viaje: schema.ViajeBase, user: Session = Depends(get_administrador_activo), db: Session = Depends(get_db)):
    autobus = crud.getAutobus(db=db, idAutobus=viaje.autobus)
    print("Viaje Main ", viaje)
    print("ID autobus ", viaje.autobus)
    print("Autobus ", autobus.modelo)
    if autobus.asientosLibres==0:
        raise HTTPException(status_code=400, detail="Autobus completo")
    if viaje.precio<=0:
        raise HTTPException(status_code=422, detail="El precio no puede ser negativo")
    if hasattr(viaje, "id"):
        db_viaje = crud.getViaje(db, id=viaje.id)
        #crud.updateAutobus(db=db, newModelo=autobus.modelo, newAsientosLibres=autobus.asientosLibres)
        if db_viaje:
            raise HTTPException(status_code=400, detail="Viaje ya creado")
    return crud.crearViaje(db=db, viaje=viaje)

@app.post("/billete/nuevo", response_model=schema.BilleteFull)
def crear_billete(billete: schema.BilleteBase, user: Session = Depends(get_cliente_activo), db: Session = Depends(get_db)):
    print("ID Cliente ", user.id)
    print("Billete Cliente ", billete.cliente)
    if str(billete.cliente)!=str(user.id):
        raise HTTPException(status_code=401, detail="Perfil no autorizado")
    print("Billete Main ", billete)
    if hasattr(billete, "id"):
        db_billete = crud.getBillete(db, id=billete.id)
        if db_billete:
            raise HTTPException(status_code=400, detail="Billete ya creado")
    db_viaje = crud.getViaje(db, billete.viaje) # Mirar códigos de error (409) y cambiar los 400 por 422
    if db_viaje is None:
        raise HTTPException(status_code=400, detail="El viaje selecionado no existe")
    if crud.comprobarAutobusLleno(db, db_viaje.autobus) is False:
        raise HTTPException(status_code=400, detail="Autobús completo")
    if crud.comprobarAsiento(db, billete, billete.asiento) is False:
        raise HTTPException(status_code=422, detail="Asiento no disponible")
    if crud.comprobarAsientoAutobus(db, db_viaje.autobus, billete.asiento) is False:
        raise HTTPException(status_code=422, detail="Número de asiento mayor que asientos del autobús")
    print("Fecha Salida Main ", billete.fechaSalida) # Para asientos de autobus que no tiene el autobus retornar error 404
    print("Fecha Llegada Main ", billete.fechaLlegada)
    if crud.comprobarFechas(db, billete.fechaSalida, billete.fechaLlegada) is False:
        raise HTTPException(status_code=422, detail="Fechas erróneas")
    return crud.crearBillete(db=db, billete=billete)

@app.post("/ruta/nueva", response_model=schema.RutaFull)
def crear_ruta(ruta: schema.RutaBase, user: Session = Depends(get_administrador_activo), db: Session = Depends(get_db)):
    if ruta.ciudades == "":
        raise HTTPException(status_code=422, detail="No se han introducido ciudades")
    if hasattr(ruta, "id"):
        db_ruta = crud.getRuta(db, id=ruta.id)
        if db_ruta:
            raise HTTPException(status_code=400, detail="Ruta ya creada")
    return crud.crearRuta(db=db, ruta=ruta)

# FUNCIONES DE GET (LISTAR)
@app.get("/administradores/{idAdministrador}/perfil", response_model=schema.AdministradorFull)
def get_admninistrador(idAdministrador, user: Session = Depends(get_administrador_activo), db: Session = Depends(get_db)):
    print("id administrador ", idAdministrador)
    print("user id ", user.id)
    if str(idAdministrador)!=str(user.id):
        raise HTTPException(status_code=401, detail="Perfil no autorizado")
    db_administrador = crud.getAdministrador(db, idAdministrador=idAdministrador)
    if db_administrador is None:
        raise HTTPException(status_code=404, detail="Administrador no encontrado")
    return db_administrador

@app.get("/clientes/{idCliente}/perfil", response_model=schema.ClienteFull)
def get_cliente(idCliente, user: Session = Depends(get_cliente_activo), db: Session = Depends(get_db)):
    print("id cliente ", idCliente)
    print("user id ", user.id)
    if str(idCliente)!=str(user.id):
        raise HTTPException(status_code=401, detail="Perfil no autorizado")
    db_cliente = crud.getCliente(db, idCliente=idCliente)
    if db_cliente is None:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return db_cliente

@app.get("/conductores/{idConductor}/perfil", response_model=schema.ConductorFull)
def get_conductor(idConductor, user: Session = Depends(get_conductor_activo), db: Session = Depends(get_db)):
    if str(idConductor)!=str(user.id):
        raise HTTPException(status_code=401, detail="Perfil no autorizado")
    db_conductor = crud.getConductor(db, idConductor=idConductor)
    if db_conductor is None:
        raise HTTPException(status_code=404, detail="Conductor no encontrado")
    return db_conductor

@app.get("/clientes/", response_model=List[schema.ClienteFull])
def get_clientes(skip: int = 0, limit: int = 100, user: Session = Depends(get_administrador_activo), db: Session = Depends(get_db)):
    clientes = crud.getClientes(db, skip=skip, limit=limit)
    for cliente in clientes:
        print("Cliente Correo ", cliente.correo)
        print("Cliente DNI ", cliente.dni)
        print("Cliente Telefono ", cliente.telefono)
    return clientes

@app.get("/conductores/", response_model=List[schema.ConductorFull])
def get_conductores(skip: int = 0, limit: int = 100, user: Session = Depends(get_administrador_activo), db: Session = Depends(get_db)):
    conductores = crud.getConductores(db, skip=skip, limit=limit)
    return conductores

@app.get("/autobuses/", response_model=List[schema.AutobusFull])
def get_autobuses(skip: int = 0, limit: int = 100, user: Session = Depends(get_administrador_activo), db: Session = Depends(get_db)):
    autobuses = crud.getAutobuses(db, skip=skip, limit=limit)
    return autobuses

@app.get("/rutas/", response_model=List[schema.RutaFull])
def get_rutas(skip: int = 0, limit: int = 100, user: Session = Depends(get_administrador_activo), db: Session = Depends(get_db)):
    rutas = crud.getRutas(db, skip=skip, limit=limit)
    return rutas

@app.get("/viajes/", response_model=List[schema.ViajeFull])
def get_viajes(skip: int = 0, limit: int = 100, user: Session = Depends(get_cliente_activo), db: Session = Depends(get_db)):
    viajes = crud.getViajes(db, skip=skip, limit=limit)
    return viajes

@app.get("/billetes/", response_model=List[schema.BilleteFull])
def get_billetes(skip: int = 0, limit: int = 100, user: Session = Depends(get_administrador_activo), db: Session = Depends(get_db)):
    billetes = crud.getBilletes(db, skip=skip, limit=limit)
    return billetes

@app.get("/rutas/{idRuta}", response_model=schema.RutaFull)
def get_ruta(idRuta, user: Session = Depends(get_cliente_activo), db: Session = Depends(get_db)):
    db_ruta = crud.getRuta(db, idRuta)
    if db_ruta is None:
        raise HTTPException(status_code=404, detail="Ruta no encontrada")
    return db_ruta

# FUNCIONES DE GET (CONSULTAS)
@app.get("/viaje/{idViaje}/billetes/", response_model=List[schema.BilleteFull])
def get_asientos_ocupados(idViaje, skip: int = 0, limit: int = 100, user: Session = Depends(get_cliente_activo), db: Session = Depends(get_db)):
    print("ID Viaje ", idViaje)
    db_viaje = crud.getViaje(db, idViaje)
    print("Viaje Main ", db_viaje)
    if db_viaje is None:
        raise HTTPException(status_code=404, detail="Viaje no encontrado")
    return crud.getAsientosOcupados(db=db, idViaje=idViaje, skip=skip, limit=limit)

@app.get("/viaje/{idViaje}/asientos/", response_model=List[int])
def get_asientos_libres(idViaje, skip: int = 0, limit = 100, user: Session = Depends(get_cliente_activo), db: Session = Depends(get_db)):
    db_viaje = crud.getViaje(db, idViaje)
    if db_viaje is None:
        raise HTTPException(status_code=404, detail="Viaje no encontrado")
    return crud.getAsientosLibres(db=db, idViaje=idViaje, skip=skip, limit=limit)

@app.get("/cliente/{idCliente}/billetes/", response_model=List[schema.BilleteFull])
def get_billetes_cliente(idCliente, skip: int = 0, limit: int = 100, user: Session = Depends(get_cliente_activo), db: Session = Depends(get_db)):
    print("id cliente ", str(idCliente))
    print("id user ", str(user.id))
    print("QUERY MAIN ", crud.getBilletesCliente(db=db, idCliente=idCliente, skip=skip, limit=limit))
    if str(idCliente)!=str(user.id):
        raise HTTPException(status_code=401, detail="Acceso no autorizado")
    return crud.getBilletesCliente(db=db, idCliente=idCliente, skip=skip, limit=limit)

@app.get("/conductor/{idConductor}/viajes/", response_model=List[schema.ViajeFull])
def get_viajes_conductor(idConductor, skip: int = 0, limit = 100, user: Session = Depends(get_conductor_activo), db: Session = Depends(get_db)):
    if str(idConductor)!=str(user.id):
        raise HTTPException(status_code=401, detail="Acceso no autorizado")
    return crud.getViajesConductor(db=db, idConductor=idConductor, skip=skip, limit=limit)

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
    return crud.getDuracion(db=db, idBillete=idBillete)

@app.get("/cliente/{idCliente}/puntos")
def get_puntos(idCliente, user: Session = Depends(get_cliente_activo), db:Session = Depends(get_db)):
    cliente = crud.getCliente(db=db, idCliente=idCliente)
    if str(cliente.id)!=str(user.id):
        raise HTTPException(status_code=401, detail="Acceso no autorizado")
    if cliente.puntos is None:
        raise HTTPException(status_code=400, detail="Puntos no disponibles")
    return crud.getPuntosCliente(db=db, idCliente=idCliente)

@app.get("/viajes/origen/{origen}/destino/{destino}", response_model=List[schema.ViajeFull])
def get_viajes_origen_destino(origen, destino, skip: int = 0, limit: int = 100, user: Session = Depends(get_cliente_activo), db: Session = Depends(get_db)):
    if origen is None:
        raise HTTPException(status_code=400, detail="Origen erróneo")
    if destino is None:
        raise HTTPException(status_code=400, detail="Destino erróneo")
    if origen==destino:
        raise HTTPException(status_code=400, detail="Origen y Destino iguales")
    return crud.getViajesOrigenDestino(db, origen, destino, skip, limit)


# FUNCIONES DE DELETE
@app.delete("/administrador/{idAdministrador}/borrar")
def delete_administrador(idAdministrador, user: Session = Depends(get_administrador_activo), db: Session = Depends(get_db)):
    if str(idAdministrador)!=str(user.id):
        raise HTTPException(status_code=401, detail="Acceso no autorizado")
    crud.deleteAdministrador(db, idAdministrador)

@app.delete("/cliente/{idCliente}/borrar")
def delete_cliente(idCliente, user: Session = Depends(get_cliente_activo), db: Session = Depends(get_db)):
    if str(idCliente)!=str(user.id):
        raise HTTPException(status_code=401, detail="Acceso no autorizado")
    crud.deleteCliente(db, idCliente)

@app.delete("/conductor/{idConductor}/borrar")
def delete_conductor(idConductor, user: Session = Depends(get_conductor_activo), db: Session = Depends(get_db)):
    if str(idConductor)!=str(user.id):
        raise HTTPException(status_code=401, detail="Acceso no autorizado")
    crud.deleteConductor(db, idConductor)

@app.delete("/administrador/{idAdministrador}/autobus/{idAutobus}/borrar")
def delete_autobus(idAdministrador, idAutobus, user: Session = Depends(get_administrador_activo), db: Session = Depends(get_db)):
    if str(idAdministrador)!=str(user.id):
        raise HTTPException(status_code=401, detail="Acceso no autorizado")
    crud.deleteAutobus(db, idAutobus)

@app.delete("/administrador/{idAdministrador}/viaje/{idViaje}/borrar")
def delete_viaje(idAdministrador, idViaje, user: Session = Depends(get_administrador_activo), db: Session = Depends(get_db)):
    if str(idAdministrador)!=str(user.id):
        raise HTTPException(status_code=401, detail="Acceso no autorizado")
    crud.deleteViaje(db, idViaje)

@app.delete("/cliente/{idCliente}/billete/{idBillete}/borrar")
def delete_billete(idCliente, idBillete, user: Session = Depends(get_cliente_activo), db: Session = Depends(get_db)):
    billete = crud.getBillete(db, idBillete)
    if str(billete.cliente)!=str(user.id):
        raise HTTPException(status_code=401, detail="Acceso no autorizado")
    if billete is None:
        raise HTTPException(status_code=400, detail="Billete no encontrado")
    if str(billete.cliente)!=str(idCliente):
        raise HTTPException(status_code=422, detail="El billete no corresponde al cliente")
    crud.deleteBillete(db, idBillete)

@app.delete("/administrador/{idAdministrador}/ruta/{idRuta}/borrar")
def delete_ruta(idAdministrador, idRuta, user: Session = Depends(get_administrador_activo), db: Session = Depends(get_db)):
    if str(idAdministrador)!=str(user.id):
        raise HTTPException(status_code=401, detail="Acceso no autorizado")
    crud.deleteRuta(db, idRuta)


# FUNCIONES DE SET
@app.patch("/administrador/{idAdministrador}/editar", response_model=schema.AdministradorFull)
def set_administrador(idAdministrador, newAdministrador: schema.AdministradorSet, user: Session = Depends(get_administrador_activo), db: Session = Depends(get_db)):
    if str(idAdministrador)!=str(user.id):
        raise HTTPException(status_code=401, detail="Acceso no autorizado")
    db_administrador = crud.getAdministrador(db, idAdministrador=idAdministrador)
    if db_administrador is None:
        raise HTTPException(status_code=404, detail="Administrador no encontrado")
    return crud.updateAdministrador(db, idAdministrador, newAdministrador)

@app.patch("/clientes/{idCliente}/editar", response_model=schema.ClienteFull)
def set_cliente(idCliente, newCliente: schema.ClienteSet, user: Session = Depends(get_cliente_activo), db: Session = Depends(get_db)):
    if str(idCliente)!=str(user.id):
        raise HTTPException(status_code=401, detail="Acceso no autorizado")
    db_cliente = crud.getCliente(db, idCliente=idCliente)
    print("New nombre ", newCliente.nombre)
    print("New apellidos ", newCliente.apellidos)
    print("New dni ", newCliente.dni)
    if db_cliente is None:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    if newCliente.dni is not None:
        print("len DNI ", len(newCliente.dni))
        if len(newCliente.dni) != 9:
            raise HTTPException(status_code=400, detail="DNI incorrecto")
    if newCliente.correo is not None:
        raise HTTPException(status_code=422, detail="No se puede modificar el correo")
    if newCliente.rol is not None:
        raise HTTPException(status_code=422, detail="No se puede modificar el rol")
    return crud.updateCliente(db, idCliente, newCliente)


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
    return crud.updateAutobus(db, idAutobus, newAutobus)


@app.patch("/conductores/{idConductor}/editar", response_model=schema.ConductorFull)
def set_conductor(idConductor, newConductor: schema.ConductorSet, user: Session = Depends(get_conductor_activo), db: Session = Depends(get_db)):
    if str(idConductor)!=str(user.id):
        raise HTTPException(status_code=401, detail="Acceso no autorizado")
    db_conductor = crud.getConductor(db, idConductor=idConductor)
    if db_conductor is None:
        raise HTTPException(status_code=404, detail="Conductor no encontrado")
    return crud.updateConductor(db, idConductor, newConductor)


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
    return crud.updateRuta(db, idRuta, newRuta)


@app.patch("/viajes/{idViaje}/editar", response_model=schema.ViajeFull)
def set_viaje(idViaje, newViaje: schema.ViajeSet, user: Session = Depends(get_administrador_activo), db: Session = Depends(get_db)):
    if str(user.rol)!="administrador":
        raise HTTPException(status_code=401, detail="Acceso no autorizado")
    if newViaje.precio<=0:
        raise HTTPException(status_code=422, detail="El precio no puede ser negativo")
    db_viaje = crud.getViaje(db, idViaje=idViaje)
    if db_viaje is None:
        raise HTTPException(status_code=404, detail="Viaje no encontrado") # CAMBIAR RELACIONES ENTRE RUTAS Y LAS OTRAS TABLAS (HECHO)
    return crud.updateViaje(db, idViaje, newViaje) # MIRAR DOCUMENTACION FASTAPI PARA AUTENTICACION (HAY QUE PROBARLO)

@app.patch("/billetes/{idBillete}/editar", response_model=schema.BilleteFull) # REVISAR Recibe un objeto como en los post
def set_billete(idBillete, newBillete: schema.BilleteSet, user: Session = Depends(get_cliente_activo), db: Session = Depends(get_db)):
    db_billete = crud.getBillete(db, idBillete=idBillete)
    print("db billete ", db_billete) # Mirar documentacion de FastAPI de partial updates con patch
    if db_billete is None:
        raise HTTPException(status_code=404, detail="Billete no encontrado")
    set_billete = newBillete.dict()
    if set_billete["fechaSalida"] is None: 
        print("Fecha Salida None ")
        set_billete["fechaSalida"] = db_billete.fechaSalida
    if set_billete["fechaLlegada"] is None: 
        set_billete["fechaLlegada"] = db_billete.fechaLlegada
    print("Fecha Salida ", set_billete["fechaSalida"])
    print("Fecha Llegada ", set_billete["fechaLlegada"])
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
    return crud.updateBillete(db, idBillete, newBillete)
"""
