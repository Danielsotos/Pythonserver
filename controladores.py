from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse
from pydantic import BaseModel

from clases import RobotDataManager
from logger import logger


class RobotRequest(BaseModel):
    id: str
    comment: str = ""


class AuthRequest(BaseModel):
    username: str
    password: str


class RobotAPI:
    def __init__(self, data_manager: RobotDataManager):
        self.data_manager = data_manager
        self.router = APIRouter()
        self.config_routes()

    def _get_current_user(self, request: Request):
        username = request.session.get("username")
        if not username:
            raise HTTPException(status_code=401, detail="Sesión no válida")
        return username

    def _require_page_user(self, request: Request):
        if not request.session.get("username"):
            return RedirectResponse(url="/login", status_code=303)
        return None

    def config_routes(self):
        @self.router.get("/")
        def root(request: Request):
            if request.session.get("username"):
                return RedirectResponse(url="/index", status_code=303)
            return RedirectResponse(url="/login", status_code=303)

        @self.router.get("/login")
        def login_page(request: Request):
            if request.session.get("username"):
                return RedirectResponse(url="/index", status_code=303)
            return FileResponse("templates/login.html")

        @self.router.get("/index")
        def index(request: Request):
            redirect = self._require_page_user(request)
            if redirect:
                return redirect
            return FileResponse("templates/index.html")

        @self.router.get("/FLR")
        def flr(request: Request):
            redirect = self._require_page_user(request)
            if redirect:
                return redirect
            return FileResponse("templates/FLR.html")

        @self.router.get("/SBS")
        def sbs(request: Request):
            redirect = self._require_page_user(request)
            if redirect:
                return redirect
            return FileResponse("templates/SBS.html")

        @self.router.post("/register")
        def register(auth: AuthRequest):
            username = auth.username.strip()
            password = auth.password.strip()

            if not username or not password:
                raise HTTPException(status_code=400, detail="Usuario y contraseña son obligatorios")

            try:
                user = self.data_manager.create_user(username, password)
                return {"message": "Usuario registrado correctamente", "user": user["username"]}
            except ValueError as exc:
                raise HTTPException(status_code=400, detail=str(exc)) from exc

        @self.router.post("/login")
        def login(auth: AuthRequest, request: Request):
            username = auth.username.strip()
            password = auth.password.strip()

            if not username or not password:
                raise HTTPException(status_code=400, detail="Usuario y contraseña son obligatorios")

            user = self.data_manager.authenticate_user(username, password)
            if not user:
                raise HTTPException(status_code=401, detail="Credenciales inválidas")

            request.session["username"] = user["username"]
            return {"message": "Inicio de sesión correcto", "user": user["username"]}

        @self.router.post("/logout")
        def logout(request: Request):
            request.session.clear()
            return {"message": "Sesión cerrada"}

        @self.router.get("/me")
        def me(request: Request):
            username = request.session.get("username")
            if not username:
                raise HTTPException(status_code=401, detail="No autenticado")
            return {"username": username}

        @self.router.get("/health")
        def health():
            try:
                db_ok = self.data_manager.healthcheck()
                return {"status": "ok", "database": db_ok}
            except Exception as exc:
                logger.error("Healthcheck falló: %s", exc)
                raise HTTPException(status_code=503, detail="Database unavailable") from exc

        @self.router.get("/datos")
        def datos(request: Request):
            self._get_current_user(request)

            try:
                datos = self.data_manager.get_all()
                return JSONResponse(content=datos)
            except ValueError as exc:
                logger.warning("Error en /datos: %s", exc)
                raise HTTPException(status_code=400, detail=str(exc)) from exc
            except Exception as exc:
                logger.error("Error en /datos: %s", exc)
                raise HTTPException(status_code=500, detail="Error interno del servidor") from exc

        @self.router.post("/FLR")
        def guardar_flr(robot: RobotRequest, request: Request):
            current_user = self._get_current_user(request)
            logger.info("POST /FLR - robot_id=%s user=%s", robot.id, current_user)

            self.data_manager.add_robot("robotsFLR", robot.id, current_user, robot.comment)

            return {
                "message": "Datos guardados correctamente",
                "section": "robotsFLR",
                "id": robot.id,
                "comment": robot.comment,
                "created_by": current_user,
            }

        @self.router.post("/SBS")
        def guardar_sbs(robot: RobotRequest, request: Request):
            current_user = self._get_current_user(request)
            logger.info("POST /SBS - robot_id=%s user=%s", robot.id, current_user)

            self.data_manager.add_robot("robotsSBS", robot.id, current_user, robot.comment)

            return {
                "message": "Datos guardados correctamente",
                "section": "robotsSBS",
                "id": robot.id,
                "comment": robot.comment,
                "created_by": current_user,
            }
