import json
from datetime import datetime
from pathlib import Path

class Robot:
    def __init__(self, id, timestamp):
        self.id = id
        self.timestamp = timestamp

    @classmethod
    def create(cls, id):
        return cls(id, datetime.now().isoformat())

    def to_dict(self):
        return {"id": self.id, "timestamp": self.timestamp}

class RobotDataManager:
    def __init__(self, file_path="data/datos.json"):
        self.file_path = Path(file_path)

    def _read_data(self):
        with self.file_path.open("r", encoding="utf-8") as f:
            return json.load(f)

    def _write_data(self, data):
        with self.file_path.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def get_all(self):
        return self._read_data()

    def add_robot(self, section, robot_id):
        data = self._read_data()
        if section not in data or not isinstance(data[section], list):
            data[section] = []

        nuevo_robot = Robot.create(robot_id)
        data[section].append(nuevo_robot.to_dict())
        self._write_data(data)
        return nuevo_robot.to_dict()
