from fastapi import APIRouter
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

from clases import RobotDataManager
from logger import logger

class RobotRequest(BaseModel):
    id: str

class RobotAPI:
    def __init__(self, data_manager: RobotDataManager):
        self.data_manager = data_manager
        self.router = APIRouter()
        self.router.add_api_route("/", self.root, methods=["GET"])
        self.router.add_api_route("/FLR", self.flr, methods=["GET"])
        self.router.add_api_route("/SBS", self.sbs, methods=["GET"])
        self.router.add_api_route("/datos", self.datos, methods=["GET"])
        self.router.add_api_route("/FLR", self.guardar_flr, methods=["POST"])
        self.router.add_api_route("/SBS", self.guardar_sbs, methods=["POST"])
        self.router.add_api_route("/robot", self.guardar_robot_query, methods=["POST"])
        self.router.add_api_route("/robot/{section}/{robot_id}", self.guardar_robot_path, methods=["POST"])

    def root(self):
        return FileResponse("templates/index.html")

    def flr(self):
        return FileResponse("templates/FLR.html")

    def sbs(self):
        return FileResponse("templates/SBS.html")

    def datos(self):
        try:
            return JSONResponse(content=self.data_manager.get_all())
        except Exception as e:
            logger.error("Error en /datos: %s", e)
            return JSONResponse(content={"error": str(e)}, status_code=500)

    async def guardar_flr(self, robot: RobotRequest):
        logger.info("FLR BOT id=%s", robot.id)
        self.data_manager.add_robot("robotsFLR", robot.id)
        return {"message": "Datos guardados correctamente", "id": robot.id}

    async def guardar_sbs(self, robot: RobotRequest):
        logger.info("SBS BOT id=%s", robot.id)
        self.data_manager.add_robot("robotsSBS", robot.id)
        return {"message": "Datos guardados correctamente", "id": robot.id}

    async def guardar_robot_query(self, section: str = "robotsFLR", id: str | None = None):
        if not id:
            return {"error": "Falta el parámetro 'id'"}
        logger.info("POST /robot section=%s id=%s", section, id)
        self.data_manager.add_robot(section, id)
        return {"message": "Datos guardados con query", "section": section, "id": id}

    async def guardar_robot_path(self, section: str, robot_id: str):
        logger.info("POST /robot/%s/%s", section, robot_id)
        self.data_manager.add_robot(section, robot_id)
        return {"message": "Datos guardados por ruta", "section": section, "id": robot_id}
