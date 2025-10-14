import threading
from typing import Dict, Any

class SessionManager:
    """
    Minimal in-memory state for the current dataset.
    Not multi-user persistent — perfect for single-user HPC or local use.
    """
    def __init__(self):
        self._lock = threading.RLock()
        self.state: Dict[str, Any] = {
            "mode3d": False,
            "image_path": None,     # 2D image path or 3D stack path
            "mask_path": None,      # optional pre-existing mask to edit
            "export_dir": None,     # where to save exports
        }

    def update(self, **kwargs):
        with self._lock:
            self.state.update(kwargs)

    def get(self, key: str, default=None):
        with self._lock:
            return self.state.get(key, default)

    def snapshot(self) -> Dict[str, Any]:
        with self._lock:
            return dict(self.state)