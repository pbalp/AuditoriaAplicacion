# Imagen base
FROM python

# Directorio de trabajo donde se ejecuta el microservicio
WORKDIR /

# Se copia primero el fichero requirements.txt para optimizar el Dockerfile y agilizar la creación
COPY ./requirements.txt /GestionClientes/requirements.txt

# Ejecutar pip para instalar las dependencias del fichero requirements.txt en el contenedor
RUN pip install --no-cache-dir --upgrade -r /GestionClientes/requirements.txt

# Copiar los archivos que se van a ejecutar al directorio
COPY . /GestionClientes

# Indicar el puerto por el que se comunica el contenedor
EXPOSE 8002

# Ejecutar el fichero main con las siguientes características
CMD ["uvicorn", "GestionClientes.main:app", "--host", "0.0.0.0", "--port", "8000"] 
