import os
import threading
from typing import Dict, Any

class SessionManager:
    """
    Minimal in-memory state for the current dataset.
    Tracks image/mask paths, load mode, and metadata for saving.
    Not multi-user persistent — suitable for single-user HPC or local use.
    """

    def __init__(self):
        self._lock = threading.RLock()
        self.state: Dict[str, Any] = {
            "mode3d": False,        # whether current dataset is 3D
            "image_path": None,     # absolute path to loaded image or stack
            "mask_path": None,      # absolute path to loaded mask (optional)
            "export_dir": None,     # export directory (unused for now)
            "load_mode": "path",    # "upload" or "path"
            "image_name": None,     # filename of uploaded image (if applicable)
            "image_ext": None,      # extension of current image (.tif, .png, etc.)
        }

    # -----------------------------------------------------
    # Update one or more session fields atomically
    # -----------------------------------------------------
    def update(self, **kwargs):
        with self._lock:
            for k, v in kwargs.items():
                self.state[k] = v

    # -----------------------------------------------------
    # Get a session value safely
    # -----------------------------------------------------
    def get(self, key: str, default=None):
        with self._lock:
            return self.state.get(key, default)

    # -----------------------------------------------------
    # Return a full copy of session state (thread-safe)
    # -----------------------------------------------------
    def snapshot(self) -> Dict[str, Any]:
        with self._lock:
            return dict(self.state)

    # -----------------------------------------------------
    # Utility: populate metadata when a new image is loaded
    # -----------------------------------------------------
    def set_image_info(self, image_path: str, load_mode: str = "path"):
        """
        Automatically extracts filename and extension from the image path.
        Called in landing.py after a new dataset is loaded.
        """
        with self._lock:
            if image_path:
                base_name = os.path.basename(image_path)
                _, ext = os.path.splitext(base_name)
                self.state["image_name"] = base_name
                self.state["image_ext"] = ext.lower()
            else:
                self.state["image_name"] = None
                self.state["image_ext"] = None
            self.state["load_mode"] = load_mode
