# IMPORTANTE!! Ejecutar este fichero desde el directorio /home/uo528740/aplicaciontfg/microservicios

# Gestion de Autenticacion (Servicio 1)
cd ./GestionAutenticacion
docker build -t autenticacion:latest .

# Gestion de Clientes (Servicio 2)
cd ../GestionClientes
docker build -t clientes:latest .

# Gestion de Personal (Servicio 3)
cd ../GestionPersonal
docker build -t personal:latest .

# Gestion de Billetes (Servicio 4)
cd ../GestionBilletes
docker build -t billetes:latest .

# Gestion de Autobuses (Servicio 5)
cd ../GestionAutobuses
docker build -t autobuses:latest .