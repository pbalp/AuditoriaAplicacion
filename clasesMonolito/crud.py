"""
from sqlalchemy.orm import Session
from . import model
from . import schema

from passlib.context import CryptContext
from jose import JWTError, jwt
from typing import Optional
from datetime import datetime, timedelta

CLAVE_SECRETA = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITMO = "HS256"


def getAdministrador(db: Session, idAdministrador: int):
    return db.query(model.Administrador).filter(model.Administrador.id == idAdministrador).first()

def getCliente(db: Session, idCliente: int):
    return db.query(model.Cliente).filter(model.Cliente.id == idCliente).first()

def getConductor(db: Session, idConductor: int):
    return db.query(model.Conductor).filter(model.Conductor.id == idConductor).first()

def getAutobus(db: Session, idAutobus: int):
    return db.query(model.Autobus).filter(model.Autobus.id == idAutobus).first()

def getBillete(db: Session, idBillete: int):
    return db.query(model.Billete).filter(model.Billete.id == idBillete).first()

def getViaje(db: Session, idViaje: int):
    return db.query(model.Viaje).filter(model.Viaje.id == idViaje).first()

def getRuta(db: Session, idRuta: int):
    return db.query(model.Ruta).filter(model.Ruta.id == idRuta).first()

def getClienteDNI(db: Session, dni: str):
    return db.query(model.Cliente).filter(model.Cliente.dni == dni).first()

def getConductorDNI(db: Session, dni: str):
    return db.query(model.Conductor).filter(model.Conductor.dni == dni).first()

def getClienteCorreo(db: Session, correo: str):
    return db.query(model.Cliente).filter(model.Cliente.correo == correo).first()

def getConductorCorreo(db: Session, correo: str):
    return db.query(model.Conductor).filter(model.Conductor.correo == correo).first()

def getAdministradorCorreo(db: Session, correo: str):
    return db.query(model.Administrador).filter(model.Administrador.correo == correo).first()

def getUserCorreo(db: Session, correo: str):
    return db.query(model.Usuario).filter(model.Usuario.correo == correo).first()



pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verificarPassword(password, hash):
    return pwd_context.verify(password, hash)

def getPasswordHash(password):
    return pwd_context.hash(password)

def autenticarUsuario(db: Session, correo: str, password: str):
    usuario = getUserCorreo(db, correo)
    #usuarios = getClientes(db, 0, 100)
    if not usuario:
        return False
    if not verificarPassword(password, usuario.password):
        return False
    return usuario

def crearToken(data: dict, expires_delta: Optional[timedelta] = None):
    codificar = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    token = jwt.encode(codificar, CLAVE_SECRETA, algorithm=ALGORITMO)
    return token

def decodeToken(token: str):
    return jwt.decode(token, CLAVE_SECRETA, algorithms=[ALGORITMO])

def getClienteLogin(db: Session, token: str):
    payload = jwt.decode(token, CLAVE_SECRETA, algorithms=[ALGORITMO])
    cliente: str = payload.get("sub")
    if cliente is None:
        raise credentials_exception
    token_data = schema.TokenData(cliente=cliente)
    return token_data
    


def getClientes(db: Session, skip: int = 0, limit: int = 100):
    return db.query(model.Cliente).offset(skip).limit(limit).all()

def getConductores(db: Session, skip: int = 0, limit: int = 100):
    return db.query(model.Conductor).offset(skip).limit(limit).all()

def getAutobuses(db: Session, skip: int = 0, limit: int = 100):
    return db.query(model.Autobus).offset(skip).limit(limit).all()

def getRutas(db: Session, skip: int = 0, limit: int = 100):
    return db.query(model.Ruta).offset(skip).limit(limit).all()

def getBilletes(db: Session, skip: int = 0, limit: int = 100):
    return db.query(model.Billete).offset(skip).limit(limit).all()

def getViajes(db: Session, skip: int = 0, limit: int = 100):
    return db.query(model.Viaje).offset(skip).limit(limit).all()

def getBilletesCliente(db: Session, idCliente: int, skip: int, limit: int):
    #print("QUERY ", db.query(model.Billete).filter(model.Billete.cliente == idCliente).offset(skip).limit(limit).all())
    return db.query(model.Billete).filter(model.Billete.cliente == idCliente).offset(skip).limit(limit).all()

def getPuntosCliente(db: Session, idCliente: int):
    cliente = getCliente(db, idCliente)
    return cliente.puntos

def getAsientosOcupados(db: Session, idViaje: int, skip: int, limit: int):
    return db.query(model.Billete).filter(model.Billete.viaje == idViaje).offset(skip).limit(limit).all()

def getAsientosLibres(db: Session, idViaje: int, skip: int, limit: int):
    db_viaje = getViaje(db, idViaje)
    db_autobus = getAutobus(db, db_viaje.autobus)
    asientos = list(range(1, db_autobus.asientos+1))
    lista_billetes = getAsientosOcupados(db, idViaje, skip, limit)
    for billete in lista_billetes:
        print("Remove asiento ", billete.asiento)
        asientos.remove(billete.asiento)
    print("Asientos Libres ", asientos)
    return asientos

def getViajesConductor(db: Session, idConductor: int, skip: int, limit: int):
    return db.query(model.Viaje).filter(model.Viaje.conductor == idConductor).offset(skip).limit(limit).all()

def getDuracion(db: Session, idBillete: int):
    billete = getBillete(db, idBillete)
    duracion = billete.fechaLlegada - billete.fechaSalida
    #time = datetime.strftime(str(duracion), "%H:%M:%S")
    return (datetime.min+duracion).time()

def getViajesOrigenDestino(db:Session, origen: str, destino: str, skip: int, limit: int):
    rutas = getRutasOrigenDestino(db, origen, destino, skip, limit)
    print("Rutas ", rutas)
    for numero in rutas:
        print("Numero Ruta ", numero)
        print("Ruta elegida ", getRuta(db, numero).ciudades)
    lista = []
    i = 0
    for ruta in rutas:
        print("Ruta ", ruta)
        viajes = db.query(model.Viaje).filter(model.Viaje.ruta == ruta).all()
        for v in viajes:
            print("Viaje ", v)
            lista.append(v)
        print("Lista ", lista)
        i=i+1
    for viaje in lista:
        print("Viaje ", viaje)
    return lista

def getRutasOrigenDestino(db: Session, origen: str, destino: str, skip: int, limit: int):
    listaRutas = db.query(model.Ruta).offset(skip).limit(limit).all()
    print("Lista Rutas 1 ", listaRutas)
    rutas = []
    k = 0

    index = 1
    for ruta in listaRutas:
        checkOrigen = False
        checkDestino = False
        print("Lista Rutas 2 ", ruta)
        ciudades = ruta.ciudades.split()
        for ciudad in ciudades:
            print("Ciudad ", ciudad)
            if ciudad==origen: 
                print("TRUE origen ", ciudad)
                print(origen)
                checkOrigen = True
            if ciudad==destino and checkOrigen: 
                print("TRUE destino ", ciudad)
                print(destino)
                checkDestino = True
        if checkOrigen and checkDestino: rutas.append(ruta.id)
        index = index+1
    return rutas

def crearAdministrador(db: Session, administrador: schema.AdministradorBase):
    administrador.password = getPasswordHash(administrador.password)
    db_administrador = model.Administrador(**administrador.dict())
    db.add(db_administrador)
    db.commit()
    db.refresh(db_administrador)
    return db_administrador

def crearCliente(db: Session, cliente: schema.ClienteBase):
    cliente.password = getPasswordHash(cliente.password)
    db_cliente = model.Cliente(**cliente.dict())
    db_cliente.puntos = 0
    db_cliente.rol = 'cliente'
    db.add(db_cliente)
    db.commit()
    db.refresh(db_cliente)
    return db_cliente

def crearConductor(db: Session, conductor: schema.ConductorBase):
    conductor.password = getPasswordHash(conductor.password)
    db_conductor = model.Conductor(**conductor.dict())
    db_conductor.rol = 'conductor'
    db.add(db_conductor)
    db.commit()
    db.refresh(db_conductor)
    return db_conductor

def crearAutobus(db: Session, autobus: schema.AutobusBase):
    db_autobus = model.Autobus(**autobus.dict())
    db_autobus.asientosLibres = autobus.asientos
    db.add(db_autobus)
    db.commit()
    db.refresh(db_autobus)
    return db_autobus

def crearViaje(db: Session, viaje: schema.ViajeBase):
    db_viaje = model.Viaje(**viaje.dict())
    db.add(db_viaje)
    db.commit()
    db.refresh(db_viaje)
    return db_viaje

def crearBillete(db: Session, billete: schema.BilleteBase):
    db_billete = model.Billete(**billete.dict())
    db_viaje = getViaje(db, db_billete.viaje)
    updateClientePuntos(db, billete.cliente, round(db_viaje.precio, 1)*10)
    db_autobus = getAutobus(db, db_viaje.autobus)

    updateAutobusAsientos(db, db_viaje.autobus)
    db.add(db_billete)
    db.commit()
    db.refresh(db_billete)
    return db_billete

def crearRuta(db: Session, ruta: schema.RutaBase):
    db_ruta = model.Ruta(**ruta.dict())
    ciudadesRuta = ruta.ciudades.split()
    numeroCiudadesRuta = 0
    for i in range(len(ciudadesRuta)):
        numeroCiudadesRuta = numeroCiudadesRuta+1
    db_ruta.numeroCiudades = numeroCiudadesRuta
    #db_itinerario = model.Itinerario(numeroCiudades=itinerario.numeroCiudades, ciudades=itinerario.ciudades)
    db.add(db_ruta)
    db.commit()
    db.refresh(db_ruta)
    return db_ruta


def updateAdministrador(db: Session, idAdministrador: int, newAdministrador: schema.AdministradorSet):
    db_admin = getAdministrador(db, idAdministrador)
    update_data = newAdministrador.dict(exclude_unset=True)
    for key in update_data:
        setattr(db_admin, key, update_data[key])
    if newAdministrador.password is not None: db_admin.password = getPasswordHash(newAdministrador.password)
    db.commit()
    db.refresh(db_admin)
    return db_admin

def updateClientePuntos(db: Session, idCliente: int, newPuntos: int):
    cliente = getCliente(db, idCliente)
    cliente.puntos += newPuntos
    db.commit()
    db.refresh(cliente)
    return cliente

def updateCliente(db: Session, idCliente: int, newCliente: schema.ClienteSet):
    db_cliente = getCliente(db, idCliente)
    update_data = newCliente.dict(exclude_unset=True)
    for key in update_data:
        setattr(db_cliente, key, update_data[key])
    if newCliente.password is not None: db_cliente.password = getPasswordHash(newCliente.password)
    db.commit()
    db.refresh(db_cliente)
    return db_cliente


def updateConductor(db: Session, idConductor: int, newConductor: schema.ConductorSet):
    db_conductor = getConductor(db, idConductor)
    update_data = newConductor.dict(exclude_unset=True)
    for key in update_data:
        setattr(db_conductor, key, update_data[key])
    if newConductor.password is not None: db_conductor.password = getPasswordHash(newConductor.password)
    db.commit()
    db.refresh(db_conductor)
    return db_conductor

def updateAutobusAsientos(db: Session, idAutobus: int):
    autobus = getAutobus(db, idAutobus)
    if autobus.asientosLibres>0: autobus.asientosLibres = autobus.asientosLibres-1
    db.commit()
    db.refresh(autobus)

def updateAutobus(db: Session, idAutobus: int, newAutobus: schema.AutobusFull):
    db_autobus = getAutobus(db, idAutobus)
    update_data = newAutobus.dict(exclude_unset=True)
    for key in update_data:
        setattr(db_autobus, key, update_data[key])
    db.commit()
    db.refresh(db_autobus)
    return db_autobus


def updateRuta(db: Session, idRuta: int, newRuta: schema.RutaSet):
    db_ruta = getRuta(db, idRuta)
    update_data = newRuta.dict(exclude_unset=True)
    if newRuta.ciudades is not None:
        ciudadesRuta = newRuta.ciudades.split()
        db_ruta.numeroCiudades = len(ciudadesRuta)
    for key in update_data:
        setattr(db_ruta, key, update_data[key])
        db.commit()
        db.refresh(db_ruta)
    return db_ruta

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
    print("Billete CRUD ", db_billete)
    update_data = newBillete.dict(exclude_unset=True)

    for key in update_data:
        setattr(db_billete, key, update_data[key])
    db.commit()
    db.refresh(db_billete)
    return db_billete

def comprobarAsientoAutobus(db: Session, idAutobus: int, asiento: int):
    autobus = getAutobus(db, idAutobus)
    if autobus.asientos<asiento: return False
    else: return True

def comprobarAutobusLleno(db: Session, idAutobus):
    autobus = getAutobus(db, idAutobus)
    if autobus.asientosLibres==0: return False
    else: return True

def comprobarAsiento(db: Session, billete: schema.BilleteBase, asiento: int):
    asientoOcupado = db.query(model.Billete).filter(model.Billete.viaje == billete.viaje).filter(model.Billete.asiento == asiento).first()
    if asientoOcupado is None: return True
    else: return False

def comprobarFechas(db: Session, newFechaSalida: datetime, newFechaLlegada: datetime):
    if newFechaSalida < datetime.now() or newFechaLlegada < datetime.now() or newFechaSalida > newFechaLlegada:
        return False
    else:
        return True

def parseFechas(fechaSalida: str, fechaLlegada: str, fechaSalidaNone: bool, fechaLlegadaNone: bool):
    if not fechaSalidaNone:
        fechaSalidaSplit = fechaSalida.split('T')
        fechaSalidaArray = fechaSalidaSplit[0] + " " + fechaSalidaSplit[1]
        fechaSalidaDate = datetime.strptime(fechaSalidaArray, "%Y-%m-%d %H:%M:%S")
        fechaSalidaDate = fechaSalidaDate.isoformat(timespec='seconds')
    if not fechaLlegadaNone:
        fechaLlegadaSplit = fechaLlegada.split('T')
        fechaLlegadaArray = fechaLlegadaSplit[0] + " " + fechaLlegadaSplit[1]
        fechaLlegadaDate = datetime.strptime(fechaLlegadaArray, "%Y-%m-%d %H:%M:%S")
        fechaLlegadaDate = fechaLlegadaDate.isoformat(timespec='seconds')
    return {"fechaSalida": fechaSalidaDate, "fechaLlegada": fechaLlegadaDate}


def deleteAdministrador(db: Session, idAdministrador: int):
    administrador = getAdministrador(db, idAdministrador)
    db.delete(administrador)
    db.commit()

def deleteCliente(db: Session, idCliente: int):
    cliente = getCliente(db, idCliente)
    db.delete(cliente)
    db.commit()

def deleteConductor(db: Session, idConductor: int):
    conductor = getConductor(db, idConductor)
    db.delete(conductor)
    db.commit()

def deleteAutobus(db: Session, idAutobus: int):
    autobus = getAutobus(db, idAutobus)
    db.delete(autobus)
    db.commit()

def deleteViaje(db: Session, idViaje: int):
    viaje = getViaje(db, idViaje)
    db.delete(viaje)
    db.commit()

def deleteBillete(db: Session, idBillete: int):
    billete = getBillete(db, idBillete)
    viaje = getViaje(db, billete.viaje)
    autobus = getAutobus(db, viaje.autobus)
    autobus.asientosLibres = autobus.asientos 
    db.delete(billete)
    db.commit()

def deleteRuta(db: Session, idRuta: int):
    ruta = getRuta(db, idRuta)
    db.delete(ruta)
    db.commit()
"""