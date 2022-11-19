EJECUCIÓN DE LA APLICACIÓN MICROSERVICIOS

1.- Situarse en el directorio donde están los ficheros ejecutarDocker.sh y docker-compose.yml

2.- Ejecutar el fichero ejecutarDocker.sh para crear las imágenes y compilar los contenedores
    sudo ./ejecutarDocker.sh

3.- Ejecutar el fichero docker-compose.yml para ejecutar los contenedores
    sudo docker-compose up

4.- Esperar a que docker despliegue los contenedores

5.- En una nueva terminal, cargar el administrador en la base de datos dbPersonal

    5.1: Copiar el fichero cargarAdmin.sql al contenedor dbPersonal
    sudo docker cp cargarAdmin.sql dbPersonal:.

    5.2: Acceder al contenedor dbPersonal
    sudo docker exec -it dbPersonal bash

    5.3: Acceder al sistema MariaDB
    mariadb --user=<usuario> --password=<contraseña>

    5.4: Ejecutar el fichero cargarAdmin.sql
    source cargarAdmin.sql;

    5.5: Salir de MariaDB
    exit;

    5.6: Salir del contenedor dbPersonal
    exit;

    NOTA: Las credenciales del admin son las siguientes:
        - correo: admin@email.com
        - password: admin

6.- En el navegador introducir las siguientes URLs para ver las documentaciones de cada servicio:
    - Autenticación: http://127.0.0.1:8000/token/docs
    - Clientes: http://127.0.0.1:8000/clientes/docs
    - Personal: http://127.0.0.1:8000/administrador/docs
    - Billetes: http://127.0.0.1:8000/billetes/docs
    - Autobuses: http://127.0.0.1:8000/autobuses/docs