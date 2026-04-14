from datetime import datetime
import hashlib
import os

from sqlalchemy import Column, DateTime, Integer, String, Text, create_engine, inspect, text
from sqlalchemy.orm import declarative_base, sessionmaker

# PASO 1: Crear la base para los modelos
Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(64), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


# PASO 2: Definir el modelo de la tabla
class RobotRegistro(Base):
    __tablename__ = "robots"

    id = Column(Integer, primary_key=True)
    section = Column(String(50), nullable=False)  # Sección: "robotsFLR" o "robotsSBS"
    robot_id = Column(String(100), nullable=False)  # ID del robot
    comment = Column(Text, nullable=True)  # Comentario del operador
    created_by = Column(String(50), nullable=False)  # Usuario que registró el robot
    timestamp = Column(DateTime, nullable=False)  # Fecha y hora


# PASO 3: Gestor de la base de datos
class RobotDataManager:
    def __init__(self, db_url=None):
        default_db_url = "postgresql+psycopg://postgres:postgres@localhost:5432/robotsdb"
        db_url = db_url or os.getenv("DATABASE_URL", default_db_url)

        # PASO 4: Conectar con la base de datos
        self.engine = create_engine(db_url)

        # PASO 5: Crear las tablas
        Base.metadata.create_all(self.engine)
        self._ensure_schema_updates()

        # PASO 6: Crear el generador de sesiones
        self.Session = sessionmaker(bind=self.engine)

    def _ensure_schema_updates(self):
        inspector = inspect(self.engine)
        table_names = inspector.get_table_names()

        if "robots" in table_names:
            columns = {column["name"] for column in inspector.get_columns("robots")}
            with self.engine.begin() as connection:
                if "comment" not in columns:
                    connection.execute(text("ALTER TABLE robots ADD COLUMN comment TEXT"))
                if "created_by" not in columns:
                    connection.execute(text("ALTER TABLE robots ADD COLUMN created_by VARCHAR(50) DEFAULT 'sistema'"))

    def _hash_password(self, password):
        return hashlib.sha256(password.encode("utf-8")).hexdigest()

    def create_user(self, username, password):
        session = self.Session()

        try:
            existing_user = session.query(User).filter_by(username=username).first()
            if existing_user:
                raise ValueError("El usuario ya existe")

            new_user = User(
                username=username,
                password_hash=self._hash_password(password),
            )
            session.add(new_user)
            session.commit()
            return {"username": new_user.username}
        finally:
            session.close()

    def authenticate_user(self, username, password):
        session = self.Session()

        try:
            user = session.query(User).filter_by(username=username).first()
            if not user:
                return None

            if user.password_hash != self._hash_password(password):
                return None

            return {"username": user.username}
        finally:
            session.close()

    # ========== CREAR UN ROBOT ==========
    def add_robot(self, section, robot_id, created_by, comment=""):
        """Añade un nuevo robot a la base de datos"""

        session = self.Session()

        try:
            nuevo_robot = RobotRegistro(
                section=section,
                robot_id=robot_id,
                comment=comment.strip() or None,
                created_by=created_by,
                timestamp=datetime.now(),
            )

            session.add(nuevo_robot)
            session.commit()

            return nuevo_robot.id
        finally:
            session.close()

    # ========== OBTENER TODOS LOS ROBOTS ==========
    def get_all(self):
        """Obtiene todos los robots organizados por sección"""

        session = self.Session()

        try:
            robots = session.query(RobotRegistro).order_by(RobotRegistro.timestamp.asc()).all()

            datos = {}
            for robot in robots:
                if robot.section not in datos:
                    datos[robot.section] = []

                datos[robot.section].append({
                    "id": robot.robot_id,
                    "comment": robot.comment or "",
                    "created_by": robot.created_by,
                    "timestamp": str(robot.timestamp),
                })

            return datos
        finally:
            session.close()

    def healthcheck(self):
        session = self.Session()

        try:
            session.execute(text("SELECT 1"))
            return True
        finally:
            session.close()
