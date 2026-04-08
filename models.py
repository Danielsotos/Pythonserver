from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from database import Base

class RobotModel(Base):
    __tablename__ = "robots"
    id = Column(Integer, primary_key=True, index=True)
    robot_id = Column(String, unique=True, index=True)
    section = Column(String, index=True)
    timestamp = Column(DateTime, default=datetime.now)

    def to_dict(self):
        return {
            "id": self.id,
            "robot_id": self.robot_id,
            "section": self.section,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
        }
