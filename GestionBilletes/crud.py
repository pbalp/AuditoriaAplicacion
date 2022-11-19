from sqlalchemy.orm import Session
from typing import List
from . import model
from . import schema

from passlib.context import CryptContext
from jose import JWTError, jwt
from typing import Optional
from datetime import datetime, timedelta
import requests
import asyncio


CLAVE_SECRETA = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITMO = "HS256"

def decodeToken(token: str):
    return jwt.decode(token, CLAVE_SECRETA, algorithms=[ALGORITMO])

def getUserCorreo(db: Session, correo: str):
    response = requests.get("http://clientes:8000/user/correo/"+str(correo))
    if response.status_code!=200 or response.json() is None:
        response = requests.get("http://personal:8000/user/correo/"+str(correo))
        user = model.Administrador(**response.json())
    else:
        user = model.Cliente(**response.json())
    return user


# Metodos GET

def getBillete(db: Session, idBillete: int, idCliente: int):
    return db.query(model.Billete).filter(model.Billete.id == idBillete).filter(model.Billete.cliente == idCliente).first()

def getBillete(db: Session, idBillete: int):
    return db.query(model.Billete).filter(model.Billete.id == idBillete).first()

def getViaje(db: Session, idViaje: int):
    return db.query(model.Viaje).filter(model.Viaje.id == idViaje).first()

def getBilletes(db: Session, skip: int = 0, limit: int = 100):
    return db.query(model.Billete).offset(skip).limit(limit).all()

def getViajes(db: Session, skip: int = 0, limit: int = 100):
    return db.query(model.Viaje).offset(skip).limit(limit).all()

def getBilletesViaje(db: Session, idViaje: int, skip: int = 0, limit: int = 100):
    return db.query(model.Billete).filter(model.Billete.viaje == idViaje).offset(skip).limit(limit).all()

def getViajesAutobus(db: Session, idAutobus: int, skip: int = 0, limit: int = 100):
    return db.query(model.Viaje).filter(model.Viaje.autobus == idAutobus).offset(skip).limit(limit).all()

def getViajesRuta(db: Session, idRuta: int, skip: int = 0, limit: int = 100):
    return db.query(model.Viaje).filter(model.Viaje.ruta == idRuta).offset(skip).limit(limit).all()


def getAutobus(db: Session, idAutobus: int):
    response = requests.get("http://autobuses:8000/autobuses/"+str(idAutobus))
    autobus = model.Autobus(**response.json())
    return autobus

def getRuta(db: Session, idRuta: int):
    response = requests.get("http://autobuses:8000/rutas/"+str(idRuta))
    ruta = model.Ruta(**response.json())
    return ruta

def getCliente(db: Session, idCliente: int):
    response = requests.get("http://clientes:8000/clientes/"+str(idCliente)+"/perfil")
    cliente = model.Cliente(**response.json())
    return cliente

def getConductor(db: Session, idConductor: int):
    response = requests.get("http://personal:8000/conductor/"+str(idConductor))
    conductor = model.Conductor(**response.json())
    return conductor

def getAsientosOcupados(db: Session, idViaje: int, skip: int, limit: int):
    return db.query(model.Billete).filter(model.Billete.viaje == idViaje).offset(skip).limit(limit).all()

def getAsientosLibres(db: Session, idViaje: int, skip: int, limit: int):
    db_viaje = getViaje(db, idViaje)
    db_autobus = getAutobus(db, db_viaje.autobus)
    asientos = list(range(1, db_autobus.asientos+1))
    lista_billetes = getAsientosOcupados(db, idViaje, skip, limit)
    for billete in lista_billetes:
        asientos.remove(billete.asiento)
    return asientos


def getBilletesCliente(db: Session, idCliente: int, skip: int, limit: int):
    return db.query(model.Billete).filter(model.Billete.cliente == idCliente).offset(skip).limit(limit).all()

def getViajesConductor(db: Session, idConductor: int, skip: int, limit: int):
    return db.query(model.Viaje).filter(model.Viaje.conductor == idConductor).offset(skip).limit(limit).all()


def comprobarAutobusLleno(db: Session, idAutobus):
    autobus = getAutobus(db, idAutobus)
    if autobus.asientosLibres==0: return False
    else: return True

def comprobarAsiento(db: Session, billete: schema.BilleteBase, asiento: int):
    asientoOcupado = db.query(model.Billete).filter(model.Billete.viaje == billete.viaje).filter(model.Billete.asiento == asiento).first()
    if asientoOcupado is None: return True
    else: return False

def comprobarAsientoAutobus(db: Session, idAutobus: int, asiento: int):
    autobus = getAutobus(db, idAutobus)
    if autobus.asientos<asiento: return False
    else: return True

def getViajesOrigenDestino(db:Session, origen: str, destino: str, skip: int, limit: int):
    rutas = getRutasOrigenDestino(db, origen, destino, skip, limit)

    lista = []
    i = 0
    for ruta in rutas:
        viajes = db.query(model.Viaje).filter(model.Viaje.ruta == ruta).all()
        for v in viajes:
            lista.append(v)
        i=i+1
    return lista

def getRutasOrigenDestino(db: Session, origen: str, destino: str, skip: int, limit: int):
    listaRutas = requests.get("http://autobuses:8000/rutas/").json()
    rutas = []
    k = 0

    index = 1
    for ruta in listaRutas:
        ruta = model.Ruta(**ruta)
        checkOrigen = False
        checkDestino = False
        ciudades = ruta.ciudades.split()
        for ciudad in ciudades:
            if ciudad==origen: 
                checkOrigen = True
            if ciudad==destino and checkOrigen: 
                checkDestino = True
        if checkOrigen and checkDestino: rutas.append(ruta.id)
        index = index+1
    return rutas

def comprobarFechas(db: Session, newFechaSalida: datetime, newFechaLlegada: datetime):
    print("NEW FECHA SALIDA ", newFechaSalida)
    print("NEW FECHA LLEGADA ", newFechaLlegada)
    fechas = parseFechas(str(newFechaSalida), str(newFechaLlegada), False, False)
    print("FECHAS ", fechas)
    if fechas["fechaSalida"] < datetime.now() or fechas["fechaLlegada"] < datetime.now() or newFechaSalida > newFechaLlegada:
        return False
    else:
        return True

def parseFechas(fechaSalida: str, fechaLlegada: str, fechaSalidaNone: bool, fechaLlegadaNone: bool):
    print("FECHA SALIDA PARSE ", fechaSalida)
    print("FECHA LLEGADA PARSE ", fechaLlegada)
    variableSplitSalida = fechaContains(fechaSalida)
    variableSplitLlegada = fechaContains(fechaLlegada)
    print("VARIABLE SPLIT SALIDA ", variableSplitSalida)
    print("VARIABLE SPLIT LLEGADA ", variableSplitLlegada)
    if not fechaSalidaNone:
        fechaSalidaSplit = str(fechaSalida).split(variableSplitSalida)[0]
        print("FECHA SALIDA PARSE ", fechaSalidaSplit)
        fechaSalidaDate = datetime.strptime(fechaSalidaSplit, "%Y-%m-%d %H:%M:%S")
        print("FECHA SALIDA PARSE ", fechaSalidaDate)
    if not fechaLlegadaNone:
        fechaLlegadaSplit = fechaLlegada.split(variableSplitLlegada)[0]
        print("FECHA LLEGADA PARSE ", fechaLlegadaSplit)
        fechaLlegadaDate = datetime.strptime(fechaLlegadaSplit, "%Y-%m-%d %H:%M:%S")
        print("FECHA LLEGADA PARSE ", fechaLlegadaDate)
    return {"fechaSalida": fechaSalidaDate, "fechaLlegada": fechaLlegadaDate}

def fechaContains(fecha: str):
    if "." in fecha: return '.'
    if "Z" in fecha: return '.'
    if "+" in fecha: return '+'

# Metodos POST

def crearViaje(db: Session, viaje: schema.ViajeBase):
    db_viaje = model.Viaje(**viaje.dict())
    db.add(db_viaje)
    db.commit()
    db.refresh(db_viaje)
    return db_viaje

def crearBillete(db: Session, billete: schema.BilleteBase):
    db_billete = model.Billete(**billete.dict())
    db_viaje = getViaje(db, db_billete.viaje)
    updateClientePuntos(db, billete.cliente, round(db_viaje.precio*10))
    db_autobus = getAutobus(db, db_viaje.autobus)

    updateAutobusAsientos(db, db_viaje.autobus)
    db.add(db_billete)
    db.commit()
    db.refresh(db_billete)
    return db_billete

def updateAutobusAsientos(db: Session, idAutobus: int):
    response = requests.patch("http://autobuses:8000/autobuses/"+str(idAutobus)+"/asientos/")

def updateClientePuntos(db: Session, idCliente: int, newPuntos: int):
    response = requests.patch("http://clientes:8000/cliente/"+str(idCliente)+"/puntos/"+str(newPuntos))
    return response.json()


# Metodos PATCH

def updateViaje(db: Session, idViaje: int, newViaje: schema.ViajeFull):
    db_viaje = getViaje(db, idViaje)
    update_data = newViaje.dict(exclude_unset=True)
    for key in update_data:
        setattr(db_viaje, key, update_data[key])
    db.commit()

    db.refresh(db_viaje)
    return db_viaje

def updateBillete(db: Session, idBillete: int, newBillete: schema.BilleteFull):
    db_billete = getBillete(db, idBillete)
    update_data = newBillete.dict(exclude_unset=True)

    for key in update_data:
        setattr(db_billete, key, update_data[key])
    db.commit()
    db.refresh(db_billete)
    return db_billete


# Metodos DELETE

def deleteViaje(db: Session, idViaje: int):
    viaje = getViaje(db, idViaje)
    deleteBilletesViaje(db, idViaje)
    db.delete(viaje)

def deleteBillete(db: Session, idBillete: int):
    billete = getBillete(db, idBillete)
    viaje = getViaje(db, billete.viaje)
    autobus = getAutobus(db, viaje.autobus)
    autobus.asientosLibres = autobus.asientos 
    db.delete(billete)

def deleteBilletesViaje(db: Session, idViaje: int):
    listaBilletes = getBilletesViaje(db, idViaje)
    for billete in listaBilletes:
        deleteBillete(db, billete.id)
        asyncio.run(asyncEspera())

def deleteViajesAutobus(db: Session, idAutobus: int):
    listaViajes = getViajesAutobus(db, idAutobus, 0, 100)
    for viaje in listaViajes:
        deleteViaje(db, viaje.id)
        asyncio.run(asyncEspera())
    db.commit()

def deleteViajesRuta(db: Session, idRuta: int):
    listaViajes = getViajesRuta(db, idRuta, 0, 100)
    for viaje in listaViajes:
        deleteViaje(db, viaje.id)
        asyncio.run(asyncEspera())
    db.commit()

def deleteViajesConductor(db: Session, idConductor: int):
    listaViajes = getViajesConductor(db, idConductor, 0, 100)
    for viaje in listaViajes:
        deleteViaje(db, viaje.id)
        asyncio.run(asyncEspera())
    db.commit()

def deleteBilletesCliente(db: Session, idCliente: int):
    listaBilletes = getBilletesCliente(db, idCliente, 0, 100)
    for billete in listaBilletes:
        deleteBillete(db, billete.id)
        asyncio.run(asyncEspera())
    db.commit()

async def asyncEspera():
    await asyncio.sleep(5)

def rollback(db: Session):
    db.rollback()

