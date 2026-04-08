from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import uvicorn

from database import engine, Base, SessionLocal
from clases import RobotDataManager
from controladores import RobotAPI

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Servidor web con FastAPI",
    description="Servidor con frontend + API",
    version="1.0.0",
)

app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/pictures", StaticFiles(directory="pictures"), name="pictures")

db = SessionLocal()
data_manager = RobotDataManager(db)
robot_api = RobotAPI(data_manager)
app.include_router(robot_api.router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
