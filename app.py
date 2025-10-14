#!/usr/bin/env python3
"""
Proofreading Tool — Manual proofreading tool for 2D images and 3D TIFF stacks.

Features (MVP):
- Load a local image (png/jpg) or a 3D stack (.tif/.tiff).
- Optional: load an existing mask (png/jpg for 2D, .tif for 3D) to continue editing.
- Brush-based add/erase per slice.
- Export the edited mask (png for 2D, .tif for 3D).

Run:
    python app.py
Then open: http://localhost:5002
"""

import os
from flask import Flask
from routes.landing import register_landing_routes
from routes.editor import register_editor_routes
from backend.session_manager import SessionManager

def create_app() -> Flask:
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.environ.get("ProofreadingTool_SECRET", "dev-secret")
    # Attach a global session manager to app
    app.session_manager = SessionManager()
    # Register routes
    register_landing_routes(app)
    register_editor_routes(app)
    return app

if __name__ == "__main__":
    host = os.environ.get("ProofreadingTool_HOST", "0.0.0.0")
    port = int(os.environ.get("ProofreadingTool_PORT", "5002"))
    debug = os.environ.get("FLASK_DEBUG", "1") == "1"
    app = create_app()
    print(f"✅ Proofreading Tool running on http://{host}:{port}  (debug={debug})")
    app.run(host=host, port=port, debug=debug)