# Proyecto Erco

Este proyecto utiliza Docker Compose para configurar y ejecutar un entorno con una base de datos PostgreSQL. Sigue los pasos a continuación para iniciar el proyecto correctamente.

## Requisitos
- Docker
- Docker Compose

## Configuración
Antes de ejecutar el proyecto, es necesario crear un archivo `.env` en la raíz del proyecto con las siguientes variables de entorno:

```env
DB_NAME=mydatabase
DB_USER=admin
DB_PASSWORD=admin
DB_HOST=pt-postgres
```

## Instrucciones para ejecutar el proyecto

1. Clona el repositorio:
   ```sh
   git clone <URL_DEL_REPOSITORIO>
   cd <NOMBRE_DEL_PROYECTO>
   ```

2. Crea el archivo `.env` con las variables mencionadas anteriormente.

3. Levanta los contenedores con Docker Compose:
   ```sh
   docker compose up -d
   ```
   Esto iniciará los servicios en segundo plano.

4. Verifica que los contenedores estén corriendo:
   ```sh
   docker ps
   ```
5. Accede desde el navegador al puerto localhost:8080 aqui podrás probar cada endpoint para cada proceso.

6. De ser necesario para bajar los contenedores puede utilizar desde una poweshel:
    ```sh
   .\scripts\reload.ps1
   ```

7. Para detener los contenedores, ejecuta:
   ```sh
   docker compose down
   ```

## Notas adicionales
- Asegúrate de tener los puertos necesarios disponibles antes de ejecutar los contenedores.
- Puedes modificar la configuración en el archivo `docker-compose.yml` si necesitas ajustar algún parámetro.

---


