from sqlalchemy.orm import Session
from models import RobotModel

class RobotDataManager:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self):
        robots = self.db.query(RobotModel).all()
        return {"robots": [robot.to_dict() for robot in robots]}

    def add_robot(self, section, robot_id):
        nuevo_robot = RobotModel(robot_id=robot_id, section=section)
        self.db.add(nuevo_robot)
        self.db.commit()
        self.db.refresh(nuevo_robot)
        return nuevo_robot.to_dict()

    def get_by_section(self, section):
        robots = self.db.query(RobotModel).filter(RobotModel.section == section).all()
        return {"section": section, "robots": [robot.to_dict() for robot in robots]}
