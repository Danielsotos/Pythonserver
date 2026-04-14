from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse
from pydantic import BaseModel, Field

from clases import RobotDataManager
from logger import logger


class RobotRequest(BaseModel):
    id: str
    comment: str = ""


class AuthRequest(BaseModel):
    username: str
    password: str


class AdminUserRequest(BaseModel):
    username: str
    password: str
    role: str


class RoleUpdateRequest(BaseModel):
    role: str


class IncidentRequest(BaseModel):
    section: str
    robot_id: str
    error_type: str
    priority: int = Field(ge=1, le=3)
    description: str = ""


class IncidentCommentRequest(BaseModel):
    comment: str


class ResolveRequest(BaseModel):
    comment: str = ""


class RobotAPI:
    def __init__(self, data_manager: RobotDataManager):
        self.data_manager = data_manager
        self.router = APIRouter()
        self.config_routes()

    def _current_user(self, request: Request):
        username = request.session.get("username")
        role = request.session.get("role")
        if not username or not role:
            raise HTTPException(status_code=401, detail="Sesión no válida")
        return {"username": username, "role": role}

    def _require_roles(self, request: Request, allowed_roles):
        user = self._current_user(request)
        if user["role"] not in allowed_roles:
            raise HTTPException(status_code=403, detail="No tienes permisos para esta acción")
        return user

    def _protect_page(self, request: Request, allowed_roles=None):
        username = request.session.get("username")
        role = request.session.get("role")
        if not username or not role:
            return RedirectResponse(url="/login", status_code=303)
        if allowed_roles and role not in allowed_roles:
            return RedirectResponse(url="/index", status_code=303)
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
        def index_page(request: Request):
            redirect = self._protect_page(request)
            if redirect:
                return redirect
            return FileResponse("templates/index.html")

        @self.router.get("/FLR")
        def flr_page(request: Request):
            redirect = self._protect_page(request)
            if redirect:
                return redirect
            return FileResponse("templates/FLR.html")

        @self.router.get("/SBS")
        def sbs_page(request: Request):
            redirect = self._protect_page(request)
            if redirect:
                return redirect
            return FileResponse("templates/SBS.html")

        @self.router.get("/incidencias")
        def incidents_page(request: Request):
            redirect = self._protect_page(request)
            if redirect:
                return redirect
            return FileResponse("templates/incidents.html")

        @self.router.get("/admin")
        def admin_page(request: Request):
            redirect = self._protect_page(request, {"admin"})
            if redirect:
                return redirect
            return FileResponse("templates/admin.html")

        @self.router.post("/register")
        def register(auth: AuthRequest):
            username = auth.username.strip()
            password = auth.password.strip()
            if not username or not password:
                raise HTTPException(status_code=400, detail="Usuario y contraseña son obligatorios")

            try:
                user = self.data_manager.create_user(username, password, role="operador")
                return {
                    "message": "Usuario registrado correctamente",
                    "user": user["username"],
                    "role": user["role"],
                }
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
            request.session["role"] = user["role"]
            return {"message": "Inicio de sesión correcto", "user": user["username"], "role": user["role"]}

        @self.router.post("/logout")
        def logout(request: Request):
            request.session.clear()
            return {"message": "Sesión cerrada"}

        @self.router.get("/me")
        def me(request: Request):
            user = self._current_user(request)
            return user

        @self.router.get("/health")
        def health():
            try:
                return {"status": "ok", "database": self.data_manager.healthcheck()}
            except Exception as exc:
                logger.error("Healthcheck falló: %s", exc)
                raise HTTPException(status_code=503, detail="Database unavailable") from exc

        @self.router.get("/datos")
        def datos(request: Request):
            self._current_user(request)
            try:
                return JSONResponse(content=self.data_manager.get_all())
            except Exception as exc:
                logger.error("Error en /datos: %s", exc)
                raise HTTPException(status_code=500, detail="Error interno del servidor") from exc

        @self.router.post("/FLR")
        def guardar_flr(robot: RobotRequest, request: Request):
            user = self._current_user(request)
            self.data_manager.add_robot("robotsFLR", robot.id.strip(), user["username"], robot.comment)
            return {
                "message": "Datos guardados correctamente",
                "section": "robotsFLR",
                "id": robot.id.strip(),
                "comment": robot.comment,
                "created_by": user["username"],
            }

        @self.router.post("/SBS")
        def guardar_sbs(robot: RobotRequest, request: Request):
            user = self._current_user(request)
            self.data_manager.add_robot("robotsSBS", robot.id.strip(), user["username"], robot.comment)
            return {
                "message": "Datos guardados correctamente",
                "section": "robotsSBS",
                "id": robot.id.strip(),
                "comment": robot.comment,
                "created_by": user["username"],
            }

        @self.router.get("/api/incidencias")
        def list_incidents(request: Request):
            self._current_user(request)
            try:
                return self.data_manager.list_incidents()
            except Exception as exc:
                logger.error("Error en /api/incidencias: %s", exc)
                raise HTTPException(status_code=500, detail="No fue posible cargar incidencias") from exc

        @self.router.post("/api/incidencias")
        def create_incident(payload: IncidentRequest, request: Request):
            user = self._current_user(request)

            normalized_type = payload.error_type.strip().lower()
            fixed_priorities = {
                "lidar": 1,
                "choque": 1,
                "parada de emergencia": 3,
            }
            if normalized_type in fixed_priorities:
                payload.priority = fixed_priorities[normalized_type]

            try:
                incident = self.data_manager.create_incident(
                    payload.section.strip(),
                    payload.robot_id.strip(),
                    payload.error_type.strip(),
                    payload.priority,
                    payload.description,
                    user["username"],
                )
                return {"message": "Incidencia registrada", "incident": incident}
            except Exception as exc:
                logger.error("Error creando incidencia: %s", exc)
                raise HTTPException(status_code=500, detail="No fue posible registrar la incidencia") from exc

        @self.router.post("/api/incidencias/{incident_id}/comentarios")
        def add_incident_comment(incident_id: int, payload: IncidentCommentRequest, request: Request):
            user = self._require_roles(request, {"tecnico", "admin"})
            if not payload.comment.strip():
                raise HTTPException(status_code=400, detail="El comentario es obligatorio")
            try:
                comment = self.data_manager.add_incident_comment(incident_id, user["username"], payload.comment)
                return {"message": "Comentario agregado", "comment": comment}
            except ValueError as exc:
                raise HTTPException(status_code=404, detail=str(exc)) from exc

        @self.router.post("/api/incidencias/{incident_id}/resolver")
        def resolve_incident(incident_id: int, payload: ResolveRequest, request: Request):
            user = self._require_roles(request, {"tecnico", "admin"})
            try:
                result = self.data_manager.resolve_incident(incident_id, user["username"], payload.comment)
                return {"message": "Incidencia resuelta", "incident": result}
            except ValueError as exc:
                raise HTTPException(status_code=404, detail=str(exc)) from exc

        @self.router.get("/api/usuarios")
        def users(request: Request):
            self._require_roles(request, {"admin"})
            return {"users": self.data_manager.list_users()}

        @self.router.post("/api/usuarios")
        def create_user(payload: AdminUserRequest, request: Request):
            self._require_roles(request, {"admin"})
            if not payload.username.strip() or not payload.password.strip():
                raise HTTPException(status_code=400, detail="Usuario, contraseña y rol son obligatorios")
            try:
                user = self.data_manager.create_user(payload.username, payload.password, payload.role)
                return {"message": "Usuario creado", "user": user}
            except ValueError as exc:
                raise HTTPException(status_code=400, detail=str(exc)) from exc

        @self.router.patch("/api/usuarios/{username}/role")
        def update_role(username: str, payload: RoleUpdateRequest, request: Request):
            current = self._require_roles(request, {"admin"})
            if username == current["username"] and payload.role != "admin":
                raise HTTPException(status_code=400, detail="No puedes quitarte el rol admin a ti mismo")
            try:
                return {
                    "message": "Rol actualizado",
                    "user": self.data_manager.update_user_role(username, payload.role),
                }
            except ValueError as exc:
                raise HTTPException(status_code=400, detail=str(exc)) from exc

        @self.router.delete("/api/usuarios/{username}")
        def delete_user(username: str, request: Request):
            current = self._require_roles(request, {"admin"})
            if username == current["username"]:
                raise HTTPException(status_code=400, detail="No puedes eliminar tu propio usuario")
            try:
                self.data_manager.delete_user(username)
                return {"message": "Usuario eliminado"}
            except ValueError as exc:
                raise HTTPException(status_code=404, detail=str(exc)) from exc
