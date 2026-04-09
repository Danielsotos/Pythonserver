from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import uvicorn

from clases import RobotDataManager
from controladores import RobotAPI

# Crea una instancia de FastAPI con información sobre el servidor
app = FastAPI(
    title="Servidor web con FastAPI",
    description="Servidor con frontend + API",
    version="1.0.0",
)

# Monta las carpetas "static" y "pictures" para servir archivos CSS, JS e imágenes
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/pictures", StaticFiles(directory="pictures"), name="pictures")

# Instancia el administrador de datos y el router de la API
data_manager = RobotDataManager(db_path="data/robots.db", legacy_file_path="data/datos.json")
robot_api = RobotAPI(data_manager)
app.include_router(robot_api.router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)  # Escucha en todas las interfaces
