from datetime import datetime
import hashlib
import os

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    create_engine,
    inspect,
    text,
)
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()

VALID_ROLES = {"admin", "tecnico", "operador"}


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(64), nullable=False)
    role = Column(String(20), nullable=False, default="operador")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class RobotRegistro(Base):
    __tablename__ = "robots"

    id = Column(Integer, primary_key=True)
    section = Column(String(50), nullable=False)
    robot_id = Column(String(100), nullable=False)
    comment = Column(Text, nullable=True)
    created_by = Column(String(50), nullable=False)
    timestamp = Column(DateTime, nullable=False)


class RobotIncident(Base):
    __tablename__ = "robot_incidents"

    id = Column(Integer, primary_key=True)
    section = Column(String(50), nullable=False)
    robot_id = Column(String(100), nullable=False)
    error_type = Column(String(50), nullable=False)
    priority = Column(Integer, nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(20), nullable=False, default="abierto")
    created_by = Column(String(50), nullable=False)
    resolved_by = Column(String(50), nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class IncidentComment(Base):
    __tablename__ = "incident_comments"

    id = Column(Integer, primary_key=True)
    incident_id = Column(Integer, ForeignKey("robot_incidents.id"), nullable=False)
    author = Column(String(50), nullable=False)
    comment = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class RobotDataManager:
    def __init__(self, db_url=None):
        default_db_url = "postgresql+psycopg://postgres:postgres@localhost:5432/robotsdb"
        db_url = db_url or os.getenv("DATABASE_URL", default_db_url)
        self.engine = create_engine(db_url)
        Base.metadata.create_all(self.engine)
        self._ensure_schema_updates()
        self.Session = sessionmaker(bind=self.engine)

    def _ensure_schema_updates(self):
        inspector = inspect(self.engine)
        table_names = inspector.get_table_names()

        with self.engine.begin() as connection:
            if "users" in table_names:
                columns = {column["name"] for column in inspector.get_columns("users")}
                if "role" not in columns:
                    connection.execute(
                        text("ALTER TABLE users ADD COLUMN role VARCHAR(20) DEFAULT 'operador'")
                    )

            if "robots" in table_names:
                columns = {column["name"] for column in inspector.get_columns("robots")}
                if "comment" not in columns:
                    connection.execute(text("ALTER TABLE robots ADD COLUMN comment TEXT"))
                if "created_by" not in columns:
                    connection.execute(
                        text("ALTER TABLE robots ADD COLUMN created_by VARCHAR(50) DEFAULT 'sistema'")
                    )

    def _hash_password(self, password):
        return hashlib.sha256(password.encode("utf-8")).hexdigest()

    def _serialize_incident(self, incident, comments):
        return {
            "id": incident.id,
            "section": incident.section,
            "robot_id": incident.robot_id,
            "error_type": incident.error_type,
            "priority": incident.priority,
            "description": incident.description or "",
            "status": incident.status,
            "created_by": incident.created_by,
            "resolved_by": incident.resolved_by,
            "resolved_at": incident.resolved_at.isoformat() if incident.resolved_at else None,
            "created_at": incident.created_at.isoformat(),
            "comments": comments,
        }

    def _comment_payload(self, row):
        return {
            "id": row.id,
            "author": row.author,
            "comment": row.comment,
            "created_at": row.created_at.isoformat(),
        }

    def create_user(self, username, password, role="operador"):
        username = username.strip()
        role = role.strip().lower()

        if role not in VALID_ROLES:
            raise ValueError("Rol inválido")

        session = self.Session()
        try:
            existing_user = session.query(User).filter_by(username=username).first()
            if existing_user:
                raise ValueError("El usuario ya existe")

            is_first_user = session.query(User).count() == 0
            assigned_role = "admin" if is_first_user else role

            new_user = User(
                username=username,
                password_hash=self._hash_password(password),
                role=assigned_role,
            )
            session.add(new_user)
            session.commit()
            return {"username": new_user.username, "role": new_user.role}
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
            return {"username": user.username, "role": user.role}
        finally:
            session.close()

    def list_users(self):
        session = self.Session()
        try:
            users = session.query(User).order_by(User.username.asc()).all()
            return [
                {
                    "username": user.username,
                    "role": user.role,
                    "created_at": user.created_at.isoformat(),
                }
                for user in users
            ]
        finally:
            session.close()

    def update_user_role(self, username, role):
        role = role.strip().lower()
        if role not in VALID_ROLES:
            raise ValueError("Rol inválido")

        session = self.Session()
        try:
            user = session.query(User).filter_by(username=username).first()
            if not user:
                raise ValueError("Usuario no encontrado")
            user.role = role
            session.commit()
            return {"username": user.username, "role": user.role}
        finally:
            session.close()

    def delete_user(self, username):
        session = self.Session()
        try:
            user = session.query(User).filter_by(username=username).first()
            if not user:
                raise ValueError("Usuario no encontrado")
            session.delete(user)
            session.commit()
        finally:
            session.close()

    def add_robot(self, section, robot_id, created_by, comment=""):
        session = self.Session()
        try:
            nuevo_robot = RobotRegistro(
                section=section,
                robot_id=robot_id,
                comment=comment.strip() or None,
                created_by=created_by,
                timestamp=datetime.utcnow(),
            )
            session.add(nuevo_robot)
            session.commit()
            return nuevo_robot.id
        finally:
            session.close()

    def get_all(self):
        session = self.Session()
        try:
            robots = session.query(RobotRegistro).order_by(RobotRegistro.timestamp.desc()).all()
            data = {}
            for robot in robots:
                data.setdefault(robot.section, []).append(
                    {
                        "record_id": robot.id,
                        "id": robot.robot_id,
                        "comment": robot.comment or "",
                        "created_by": robot.created_by,
                        "timestamp": robot.timestamp.isoformat(),
                    }
                )
            return data
        finally:
            session.close()

    def create_incident(self, section, robot_id, error_type, priority, description, created_by):
        session = self.Session()
        try:
            incident = RobotIncident(
                section=section,
                robot_id=robot_id,
                error_type=error_type,
                priority=priority,
                description=description.strip() or None,
                created_by=created_by,
                status="abierto",
                created_at=datetime.utcnow(),
            )
            session.add(incident)
            session.commit()
            return self._serialize_incident(incident, [])
        finally:
            session.close()

    def list_incidents(self, status=None):
        session = self.Session()
        try:
            query = session.query(RobotIncident)
            if status:
                query = query.filter_by(status=status)

            incidents = query.order_by(
                RobotIncident.status.asc(),
                RobotIncident.priority.asc(),
                RobotIncident.created_at.desc(),
            ).all()
            incident_ids = [incident.id for incident in incidents]
            comment_map = {incident_id: [] for incident_id in incident_ids}

            if incident_ids:
                comments = (
                    session.query(IncidentComment)
                    .filter(IncidentComment.incident_id.in_(incident_ids))
                    .order_by(IncidentComment.created_at.asc())
                    .all()
                )
                for row in comments:
                    comment_map.setdefault(row.incident_id, []).append(self._comment_payload(row))

            return [self._serialize_incident(incident, comment_map.get(incident.id, [])) for incident in incidents]
        finally:
            session.close()

    def add_incident_comment(self, incident_id, author, comment):
        session = self.Session()
        try:
            incident = session.query(RobotIncident).filter_by(id=incident_id).first()
            if not incident:
                raise ValueError("Incidencia no encontrada")

            row = IncidentComment(
                incident_id=incident.id,
                author=author,
                comment=comment.strip(),
                created_at=datetime.utcnow(),
            )
            session.add(row)
            session.commit()
            return self._comment_payload(row)
        finally:
            session.close()

    def resolve_incident(self, incident_id, resolved_by, resolution_comment=""):
        session = self.Session()
        try:
            incident = session.query(RobotIncident).filter_by(id=incident_id).first()
            if not incident:
                raise ValueError("Incidencia no encontrada")

            if resolution_comment.strip():
                row = IncidentComment(
                    incident_id=incident.id,
                    author=resolved_by,
                    comment=resolution_comment.strip(),
                    created_at=datetime.utcnow(),
                )
                session.add(row)

            incident.status = "resuelto"
            incident.resolved_by = resolved_by
            incident.resolved_at = datetime.utcnow()
            session.commit()
            return {
                "id": incident.id,
                "status": incident.status,
                "resolved_by": incident.resolved_by,
                "resolved_at": incident.resolved_at.isoformat(),
            }
        finally:
            session.close()

    def healthcheck(self):
        session = self.Session()
        try:
            session.execute(text("SELECT 1"))
            return True
        finally:
            session.close()
