# Imagen base
FROM python

# Directorio de trabajo donde se ejecuta el microservicio
WORKDIR /

# Copiar los archivos que se van a ejecutar al directorio
#COPY . .
COPY ./requirements.txt /GestionBilletes/requirements.txt

# Ejecutar pip para instalar las dependencias del fichero requirements.txt en el contenedor
RUN pip install --no-cache-dir --upgrade -r /GestionBilletes/requirements.txt

COPY . /GestionBilletes 

# Indicar el puerto por el que se comunica el contenedor
EXPOSE 8004

# Ejecutar el fichero main con las siguientes características
CMD ["uvicorn", "GestionBilletes.main:app", "--host", "0.0.0.0", "--port", "8000"] 
# , "--host", "127.0.0.1", "--port", "8000"