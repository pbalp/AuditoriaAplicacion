from typing import List, Optional
from pydantic import BaseModel, Field
from fastapi import FastAPI, Header
import datetime


class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    usuario: Optional[str] = None
    rol: Optional[str] = None

class User(BaseModel):
    nombre: str
    apellidos: str
    dni: str
    correo: str
    password: str
    telefono: str
    rol: str
    class Config:
        orm_mode = True

class AdministradorBase(User):
    pass

class ClienteBase(User):
    pass

class BilleteBase(BaseModel):
    cliente: int
    viaje: int
    fechaSalida: datetime.datetime
    fechaLlegada: datetime.datetime
    asiento: int

class AutobusBase(BaseModel):
    modelo: str
    asientos: int

class RutaBase(BaseModel):
    ciudades: str

class ViajeBase(BaseModel):
    conductor: int
    autobus: int
    ruta: int
    precio: float

class AutobusSet(AutobusBase):
    modelo: Optional[str] = None
    asientos: Optional[int] = None
    asientosLibres: Optional[int] = None

class RutaSet(RutaBase):
    ciudades: Optional[str] = None

class AutobusFull(AutobusBase):
    id: Optional[int] = Field(default=None, hidden=True)
    modelo: Optional[str] = None
    asientos: Optional[int] = 1
    asientosLibres: Optional[int] = 1
    class Config:
        orm_mode = True

class RutaFull(RutaBase):
    id: Optional[int] = Field(default=None, hidden=True)
    numeroCiudades: Optional[int] = 0
    ciudades: Optional[str] = None
    class Config:
        orm_mode = True

class AdministradorFull(AdministradorBase):
    id: Optional[int] = Field(None, include_in_schema=False)
    nombre: Optional[str] = None
    apellidos: Optional[str] = None
    correo: Optional[str] = None
    dni: Optional[str] = None
    telefono: Optional[str] = None
    password: Optional[str] = None
    rol: Optional[str] = Header(None, include_in_schema=False, hidden=True)
    class Config:
        orm_mode = True

class ClienteFull(ClienteBase):
    id: Optional[int] = Field(None, hidden=True)
    nombre: Optional[str] = None
    apellidos: Optional[str] = None
    dni: Optional[str] = None
    correo: Optional[str] = None
    telefono: Optional[str] = None
    puntos: Optional[int] = None
    rol: Optional[str] = Header(None, include_in_schema=False, hidden=True)
    class Config:
        orm_mode = True

class ViajeFull(ViajeBase):
    id: Optional[int] = Field(default=None, hidden=True)
    conductor: Optional[int] = None
    autobus: Optional[int] = None
    ruta: Optional[int] = None
    precio: Optional[float] = None
    class Config:
        orm_mode = True