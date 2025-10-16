import json
import threading
from pathlib import Path
from typing import Dict, Any, List

_lock = threading.Lock()

class JSONStorage:
    def __init__(self, path: str):
        self.path = Path(path)
        if not self.path.exists():
            self._write([])

    def _read(self) -> List[Dict[str, Any]]:
        with _lock:
            try:
                with open(self.path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return []

    def _write(self, data):
        with _lock:
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

    def append(self, record: Dict[str, Any]):
        data = self._read()
        data.append(record)
        self._write(data)

    def all(self):
        return self._read()
