import json
from datetime import datetime
from pathlib import Path
from pydantic import BaseModel


class RunRecord(BaseModel):
    thread_id: str
    goal: str
    created_at: datetime


class RunRegistryRepository:
    def __init__(self, storage_path: str):
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self._data: dict[str, dict] = self._load()

    def _load(self) -> dict:
        if self.storage_path.exists():
            with open(self.storage_path, "r") as f:
                return json.load(f)
        return {}

    def _save(self) -> None:
        with open(self.storage_path, "w") as f:
            json.dump(self._data, f, indent=2, default=str)

    def record(self, thread_id: str, goal: str) -> None:
        self._data[thread_id] = RunRecord(
            thread_id=thread_id, goal=goal, created_at=datetime.utcnow()
        ).model_dump(mode="json")
        self._save()

    def list_all(self) -> list[RunRecord]:
        records = [RunRecord(**r) for r in self._data.values()]
        return sorted(records, key=lambda r: r.created_at, reverse=True)
