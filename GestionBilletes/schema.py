from typing import List, Optional
from pydantic import BaseModel, Field
from fastapi import FastAPI, Header
from pydantic import validator
import datetime


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

    @validator('dni')
    def dni_must_be_valid(cls, v):
        letras = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        numeros = "1234567890"
        if len(v)!=9:
            raise ValueError("El DNI debe tener 9 caracteres")
        if v[8] not in letras:
            raise ValueError("DNI sin letra")
        for n in v[:8]:
            if n not in numeros:
                raise ValueError("DNI erróneo: {n} no es un número")
        return v

    @validator('telefono')
    def telefono_must_be_valid(cls, v):
        numeros = "6789"
        if len(v)!=9:
            raise ValueError("El teléfono debe tener 9 caracteres")
        if v[0] not in numeros:
            raise ValueError("Número de teléfono erróneo")
        return v

class AdministradorBase(User):
    pass

class ClienteBase(User):
    pass

class ConductorBase(User):
    pass

class ViajeBase(BaseModel):
    conductor: int
    autobus: int
    ruta: int
    precio: float

class BilleteBase(BaseModel):
    cliente: int
    viaje: int
    fechaSalida: datetime.datetime
    fechaLlegada: datetime.datetime
    asiento: int

class ViajeSet(ViajeBase):
    conductor: Optional[int] = None
    autobus: Optional[int] = None
    ruta: Optional[int] = None
    precio: Optional[float] = None

class BilleteSet(BilleteBase):
    cliente: Optional[int] = None
    viaje: Optional[int] = None
    fechaSalida: Optional[datetime.datetime] = None
    fechaLlegada: Optional[datetime.datetime] = None
    asiento: Optional[int] = None

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

class ConductorFull(ConductorBase):
    id: Optional[int] = Field(default=None, hidden=True)
    nombre: Optional[str] = None
    apellidos: Optional[str] = None
    dni: Optional[str] = None
    correo: Optional[str] = None
    telefono: Optional[str] = None
    rol: Optional[str] = Header(None, include_in_schema=False)
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

class BilleteFull(BilleteBase):
    id: Optional[int] = Field(default=None, hidden=True)
    cliente: Optional[int] = None
    viaje: Optional[int] = None
    fechaSalida: Optional[datetime.datetime] = None
    fechaLlegada: Optional[datetime.datetime] = None
    asiento: Optional[int] = None
    class Config:
        orm_mode = True