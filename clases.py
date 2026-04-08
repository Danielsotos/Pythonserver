from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Any


@dataclass
class Robot:
    id: str
    timestamp: str

    @classmethod
    def create(cls, id: str) -> "Robot":
        return cls(id=id, timestamp=datetime.now().isoformat())

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


class RobotDataManager:
    def __init__(self, file_path: str | Path = "data/datos.json"):
        self.file_path = Path(file_path)

    def _read_data(self) -> dict[str, Any]:
        with self.file_path.open("r", encoding="utf-8") as f:
            return json.load(f)

    def _write_data(self, data: dict[str, Any]) -> None:
        with self.file_path.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def get_all(self) -> dict[str, Any]:
        return self._read_data()

    def add_robot(self, section: str, robot_id: str) -> dict[str, str]:
        data = self._read_data()
        if section not in data or not isinstance(data[section], list):
            data[section] = []

        nuevo_robot = Robot.create(robot_id)
        data[section].append(nuevo_robot.to_dict())
        self._write_data(data)
        return nuevo_robot.to_dict()
