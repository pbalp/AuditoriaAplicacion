
USE dbPersonal;
INSERT INTO usuario(id, nombre, apellidos, dni, correo, password, telefono, rol) VALUES 
(1, "Admin", "Admin Admin", "12345678A", "admin@email.com", "$2b$12$k7CRafYOhNtd6J5cKKFm8.bknhfZbqkS4pHhD/OwnUoDwD/ObIUCy", "641002835", "administrador");
INSERT INTO administrador(id, informacion) VALUES (1, "admin");
