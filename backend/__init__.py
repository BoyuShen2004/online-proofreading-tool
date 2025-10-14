"""
MitoMate Lite - Backend package initializer
-------------------------------------------
This package provides the core backend logic for the MitoMate Lite
proofreading tool. It centralizes imports for convenience.

Modules included:
- session_manager.py   → Manages current app/session state.
- volume_manager.py    → Handles image/volume and mask I/O.
- utils.py             → Helper utilities (string formatting, etc.).
- neuroglancer_manager.py (optional) → For 3D visualization, unused in Lite mode.

No Google Cloud or CloudVolume dependencies are required in this version.
"""

# Session state manager
from backend.session_manager import SessionManager

# Image and volume loading utilities
from backend.volume_manager import (
    load_image_or_stack,
    load_mask_like,
    save_mask,
    Volume,
)

# Optional: utility helpers (safe to remove if you don’t have backend/utils.py)
try:
    from backend.utils import get_display_name
except ImportError:
    def get_display_name(name: str) -> str:
        """Fallback if utils.py is missing."""
        return str(name)

# Optional: if Neuroglancer integration exists, expose the manager symbolically
try:
    from backend.neuroglancer_manager import NeuroglancerManager
except ImportError:
    NeuroglancerManager = None

__all__ = [
    "SessionManager",
    "load_image_or_stack",
    "load_mask_like",
    "save_mask",
    "Volume",
    "get_display_name",
    "NeuroglancerManager",
]
