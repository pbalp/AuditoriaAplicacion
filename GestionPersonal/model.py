from sqlalchemy import Column, ForeignKey, Integer, String
#from sqlalchemy.orm import relationship
#from sqlalchemy.sql import func
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

class Conductor(Usuario):
    __tablename__ = "conductor"
    __mapper_args__ = {'polymorphic_identity': 'conductor'}
    id = Column(Integer, ForeignKey('usuario.id'), primary_key=True, index=True)
    experiencia = Column(Integer)

    #viajes = relationship("Viaje")

