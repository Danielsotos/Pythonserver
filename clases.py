import json
from datetime import datetime
from pathlib import Path

from sqlalchemy import DateTime, Integer, String, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker


class Base(DeclarativeBase):
    pass


class RobotRegistro(Base):
    __tablename__ = "robots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    section: Mapped[str] = mapped_column(String(100), index=True)
    robot_id: Mapped[str] = mapped_column(String(255))
    timestamp: Mapped[datetime] = mapped_column(DateTime)


class Robot:
    def __init__(self, id, timestamp):
        self.id = id
        self.timestamp = timestamp

    @classmethod
    def create(cls, id):
        return cls(id, datetime.now())

    def to_dict(self):
        return {"id": self.id, "timestamp": self.timestamp.isoformat()}


class RobotDataManager:
    def __init__(self, db_path="data/robots.db", legacy_file_path="data/datos.json"):
        self.db_path = Path(db_path)
        self.legacy_file_path = Path(legacy_file_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        self.engine = create_engine(f"sqlite:///{self.db_path}", future=True)
        self.session_factory = sessionmaker(bind=self.engine, future=True)

        Base.metadata.create_all(self.engine)
        self._migrate_legacy_json()

    def _read_legacy_data(self):
        if not self.legacy_file_path.exists():
            return {}

        with self.legacy_file_path.open("r", encoding="utf-8") as file:
            data = json.load(file)

        return data if isinstance(data, dict) else {}

    def _migrate_legacy_json(self):
        legacy_data = self._read_legacy_data()
        sections = {
            section: items
            for section, items in legacy_data.items()
            if isinstance(items, list)
        }
        if not sections:
            return

        with self.session_factory() as session:
            existing = session.scalar(select(RobotRegistro.id).limit(1))
            if existing is not None:
                return

            for section, items in sections.items():
                for item in items:
                    if not isinstance(item, dict) or "id" not in item:
                        continue

                    raw_timestamp = item.get("timestamp")
                    try:
                        timestamp = (
                            datetime.fromisoformat(raw_timestamp)
                            if raw_timestamp
                            else datetime.now()
                        )
                    except ValueError:
                        timestamp = datetime.now()

                    session.add(
                        RobotRegistro(
                            section=section,
                            robot_id=str(item["id"]),
                            timestamp=timestamp,
                        )
                    )

            session.commit()

    def get_all(self):
        data = {}
        with self.session_factory() as session:
            stmt = select(RobotRegistro).order_by(RobotRegistro.id.asc())
            registros = session.scalars(stmt).all()

        for registro in registros:
            data.setdefault(registro.section, []).append(
                {
                    "id": registro.robot_id,
                    "timestamp": registro.timestamp.isoformat(),
                }
            )

        return data

    def add_robot(self, section, robot_id):
        nuevo_robot = Robot.create(robot_id)

        with self.session_factory() as session:
            session.add(
                RobotRegistro(
                    section=section,
                    robot_id=nuevo_robot.id,
                    timestamp=nuevo_robot.timestamp,
                )
            )
            session.commit()

        return nuevo_robot.to_dict()
