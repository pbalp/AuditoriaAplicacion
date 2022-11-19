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

