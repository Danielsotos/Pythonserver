from fastapi import APIRouter
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

from clases import RobotDataManager
from logger import logger


# Modelo de solicitud (lo que espera recibir del cliente)
class RobotRequest(BaseModel):
    id: str


class RobotAPI:
    def __init__(self, data_manager: RobotDataManager):
        self.data_manager = data_manager
        self.router = APIRouter()
        
        # Rutas GET (para obtener páginas y datos)
        self.router.add_api_route("/", self.root, methods=["GET"])
        self.router.add_api_route("/FLR", self.flr, methods=["GET"])
        self.router.add_api_route("/SBS", self.sbs, methods=["GET"])
        self.router.add_api_route("/datos", self.datos, methods=["GET"])
        
        # Rutas POST (para guardar datos)
        self.router.add_api_route("/FLR", self.guardar_flr, methods=["POST"])
        self.router.add_api_route("/SBS", self.guardar_sbs, methods=["POST"])

    # ========== RUTAS GET (mostrar páginas) ==========
    
    def root(self):
        """Mostrar la página principal"""
        return FileResponse("templates/index.html")

    def flr(self):
        """Mostrar página FLR"""
        return FileResponse("templates/FLR.html")

    def sbs(self):
        """Mostrar página SBS"""
        return FileResponse("templates/SBS.html")

    def datos(self):
        """Obtener todos los datos como JSON"""
        try:
            datos = self.data_manager.get_all()
            return JSONResponse(content=datos)
        except Exception as e:
            logger.error("Error en /datos: %s", e)
            return JSONResponse(
                content={"error": str(e)}, 
                status_code=500
            )

    # ========== RUTAS POST (guardar datos) ==========
    
    def guardar_flr(self, robot: RobotRequest):
        """Guardar robot en sección FLR"""
        logger.info("POST /FLR - robot_id=%s", robot.id)
        
        self.data_manager.add_robot("robotsFLR", robot.id)
        
        return {
            "message": "Datos guardados correctamente",
            "section": "robotsFLR",
            "id": robot.id
        }

    def guardar_sbs(self, robot: RobotRequest):
        """Guardar robot en sección SBS"""
        logger.info("POST /SBS - robot_id=%s", robot.id)
        
        self.data_manager.add_robot("robotsSBS", robot.id)
        
        return {
            "message": "Datos guardados correctamente",
            "section": "robotsSBS",
            "id": robot.id
        }
