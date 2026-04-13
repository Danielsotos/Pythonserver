from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import uvicorn

from logger import logger
from clases import RobotDataManager
from controladores import RobotAPI

# Crear la aplicación FastAPI
app = FastAPI(
    title="API de Robots",
    description="Servidor web con FastAPI para gestionar robots",
    version="1.0.0",
)

# Servir archivos estáticos (CSS, JS, imágenes)
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/pictures", StaticFiles(directory="pictures"), name="pictures")

# Crear el gestor de datos y la API
data_manager = RobotDataManager(db_path="data/robots.db")
robot_api = RobotAPI(data_manager)
app.include_router(robot_api.router)

# Ejecutar el servidor
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
