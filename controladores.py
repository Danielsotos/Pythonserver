from fastapi import APIRouter
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

from clases import RobotDataManager


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

    def root(self) -> FileResponse:
        return FileResponse("templates/index.html")

    def flr(self) -> FileResponse:
        return FileResponse("templates/FLR.html")

    def sbs(self) -> FileResponse:
        return FileResponse("templates/SBS.html")

    def datos(self) -> JSONResponse:
        try:
            return JSONResponse(content=self.data_manager.get_all())
        except Exception as e:
            return JSONResponse(content={"error": str(e)}, status_code=500)

    async def guardar_flr(self, robot: RobotRequest) -> dict[str, str]:
        self.data_manager.add_robot("robotsFLR", robot.id)
        return {"message": "Datos guardados correctamente", "id": robot.id}

    async def guardar_sbs(self, robot: RobotRequest) -> dict[str, str]:
        self.data_manager.add_robot("robotsSBS", robot.id)
        return {"message": "Datos guardados correctamente", "id": robot.id}
