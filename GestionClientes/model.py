from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, BigInteger, DateTime, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import datetime

from .database import Base


class Usuario(Base):

    __tablename__ = "usuario"
    

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(30))
    apellidos = Column(String(100))
    dni = Column(String(9), unique=True)
    correo = Column(String(30), unique=True)
    password = Column(String(100))
    telefono = Column(String(9))
    rol = Column(String(15))

    __mapper_args__ = {'polymorphic_identity': 'usuario', 'polymorphic_on':rol}

class Administrador(Usuario):

    __tablename__ = "administrador"
    __mapper_args__ = {'polymorphic_identity': 'administrador'}

    id = Column(Integer, ForeignKey('usuario.id'), primary_key=True, index=True)
    informacion = Column(String(100))

class Cliente(Usuario):

    __tablename__ = "cliente"
    __mapper_args__ = {'polymorphic_identity': 'cliente'}

    id = Column(Integer, ForeignKey('usuario.id'), primary_key=True, index=True)
    puntos = Column(BigInteger)
    #billetes = relationship("Billete")

class Billete(Base):

    __tablename__ = "billete"

    id = Column(Integer, primary_key=True, index=True)
    cliente = Column(Integer) #, ForeignKey("cliente.id")
    viaje = Column(Integer) #, ForeignKey("viaje.id")
    fechaSalida = Column(DateTime(timezone=True), server_default=func.now())
    fechaLlegada = Column(DateTime(timezone=True), server_default=func.now())
    asiento = Column(Integer)

