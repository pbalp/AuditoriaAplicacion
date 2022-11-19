from re import I

from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy.orm import Session

from . import model
from . import schema
from . import crud

from .database import SessionLocal, engine
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import timedelta

from jose import JWTError, jwt


model.Base.metadata.create_all(bind=engine)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
TIEMPO_EXPIRACION = 30

app = FastAPI(docs_url="/token/docs", redoc_url="/token/redocs", openapi_url="/token/openapi.json")


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

