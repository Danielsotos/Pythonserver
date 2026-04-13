from fastapi import APIRouter # Importamos APIRouter para organizar nuestras rutas
from fastapi.responses import FileResponse, JSONResponse # Importamos FileResponse para servir archivos HTML y JSONResponse para respuestas JSON
from pydantic import BaseModel # Importamos BaseModel para definir modelos de datos de entrada
from fastapi import HTTPException  # Importamos HTTPException para manejar errores HTTP

from clases import RobotDataManager # Importamos la clase RobotDataManager para manejar la lógica de datos
from logger import logger # Importamos el logger para registrar eventos y errores


# Modelo de entrada
class RobotRequest(BaseModel): # Definimos un modelo de datos para las solicitudes POST, con un campo "id" que es una cadena
    id: str


class RobotAPI: # Definimos la clase RobotAPI que manejará las rutas de nuestra API
    def __init__(self, data_manager: RobotDataManager): # El constructor recibe una instancia de RobotDataManager para manejar la lógica de datos
        self.data_manager = data_manager  # Guardamos la instancia de RobotDataManager en un atributo de la clase
        self.router = APIRouter() # Creamos una instancia de APIRouter para organizar nuestras rutas
        self.config_routes()# Llamamos al método _setup_routes para definir las rutas de la API

    def config_routes(self):

        @self.router.get("/") # Definimos una ruta GET para la raíz ("/") que servirá el archivo index.html
        def root():
            return FileResponse("templates/index.html")

        @self.router.get("/FLR")
        def flr():
            return FileResponse("templates/FLR.html")

        @self.router.get("/SBS")
        def sbs():
            return FileResponse("templates/SBS.html")

        @self.router.get("/datos")
        def datos():
            try:
                datos = self.data_manager.get_all() # Obtenemos todos los datos utilizando el método get_all de RobotDataManager
                return JSONResponse(content=datos) # Devolvemos los datos en formato JSON utilizando JSONResponse
            except ValueError as e: # Si ocurre un error de valor, lo registramos como una advertencia y devolvemos un error HTTP 400 con el mensaje del error
                logger.warning("Error en /datos: %s", e)
                raise HTTPException(status_code=400, detail=str(e))
            
            except Exception as e: # Si ocurre cualquier otro tipo de error, lo registramos como un error y devolvemos un error HTTP 500 con un mensaje genérico
                logger.error("Error en /datos: %s", e)
                raise HTTPException(status_code=500, detail="Error interno del servidor")

        @self.router.post("/FLR")
        def guardar_flr(robot: RobotRequest): # Definimos una ruta POST para "/FLR" que recibe un objeto RobotRequest en el cuerpo de la solicitud
            logger.info("POST /FLR - robot_id=%s", robot.id) # Registramos un mensaje de información con el ID del robot recibido en la solicitud

            self.data_manager.add_robot("robotsFLR", robot.id) # Llamamos al método add_robot de RobotDataManager para agregar el ID del robot a la sección "robotsFLR"

            return {
                "message": "Datos guardados correctamente",
                "section": "robotsFLR",
                "id": robot.id
            }

        @self.router.post("/SBS") # Definimos una ruta POST para "/SBS" que recibe un objeto RobotRequest en el cuerpo de la solicitud
        def guardar_sbs(robot: RobotRequest): # Registramos un mensaje de información con el ID del robot recibido en la solicitud
            logger.info("POST /SBS - robot_id=%s", robot.id) # Llamamos al método add_robot de RobotDataManager para agregar el ID del robot a la sección "robotsSBS"

            self.data_manager.add_robot("robotsSBS", robot.id)

            return {
                "message": "Datos guardados correctamente",
                "section": "robotsSBS",
                "id": robot.id
            }