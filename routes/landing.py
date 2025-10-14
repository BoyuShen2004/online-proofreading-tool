"""
Proofreading Tool - Landing Page Routes
-----------------------------------
Handles initial image and mask loading from either:
- Local absolute paths (recommended for HPC)
- File uploads via browser

Automatically validates and loads 2D/3D TIFF stacks using
backend.volume_manager.load_image_or_stack() and aligns masks
with automatic orientation correction.

After successful load, stays on the same page and shows inline
warnings if paths are invalid, instead of redirecting.
"""

from flask import (
    Blueprint,
    render_template,
    request,
    current_app,
    flash,
    jsonify
)
import os
import numpy as np
from werkzeug.utils import secure_filename

from backend.volume_manager import load_image_or_stack, load_mask_like

bp = Blueprint("landing", __name__)

def register_landing_routes(app):
    app.register_blueprint(bp)


@bp.route("/", methods=["GET", "POST"])
def index():
    """
    Landing page:
    - Loads 2D or 3D image stack
    - Optionally loads an existing mask
    - Displays inline warning instead of redirecting
    """
    warning = None
    img_path = ""
    mask_path = ""

    if request.method == "POST":
        sm = current_app.session_manager
        load_mode = request.form.get("load_mode", "path")

        # ----------------------------
        # 1. Handle file upload mode
        # ----------------------------
        if load_mode == "upload":
            img_file = request.files.get("image_file")
            mask_file = request.files.get("mask_file")

            if not img_file or img_file.filename == "":
                warning = "⚠️ Please choose an image or stack file."
                return render_template(
                    "mask_editor.html",
                    warning=warning,
                    mode3d=False,
                    num_slices=1
                )

            workdir = os.path.abspath("./_uploads")
            os.makedirs(workdir, exist_ok=True)
            img_path = os.path.join(workdir, secure_filename(img_file.filename))
            img_file.save(img_path)

            mask_path = None
            if mask_file and mask_file.filename:
                mask_path = os.path.join(workdir, secure_filename(mask_file.filename))
                mask_file.save(mask_path)

        # ----------------------------
        # 2. Handle local file path mode
        # ----------------------------
        else:
            img_path = request.form.get("image_path", "").strip()
            mask_path = request.form.get("mask_path", "").strip() or None

            if not img_path or not os.path.exists(img_path):
                warning = f"⚠️ Image/stack not found: {img_path}"
                return render_template(
                    "mask_editor.html",
                    warning=warning,
                    mode3d=False,
                    num_slices=1,
                    image_path=img_path,
                    mask_path=mask_path
                )

            if mask_path and not os.path.exists(mask_path):
                warning = f"⚠️ Mask file not found: {mask_path}"
                return render_template(
                    "mask_editor.html",
                    warning=warning,
                    mode3d=False,
                    num_slices=1,
                    image_path=img_path,
                    mask_path=mask_path
                )

        # ----------------------------
        # 3. Load image and mask
        # ----------------------------
        try:
            volume = load_image_or_stack(img_path)
            mask = load_mask_like(mask_path, volume)
            mode3d = isinstance(volume, np.ndarray) and volume.ndim == 3
        except Exception as e:
            warning = f"⚠️ Error loading data: {e}"
            return render_template(
                "mask_editor.html",
                warning=warning,
                mode3d=False,
                num_slices=1,
                image_path=img_path,
                mask_path=mask_path
            )

        # ----------------------------
        # 4. Update session (keep values)
        # ----------------------------
        sm.update(mode3d=mode3d, image_path=img_path, mask_path=mask_path)
        current_app.config["CURRENT_VOLUME"] = volume
        current_app.config["CURRENT_MASK"] = mask

        num_slices = volume.shape[0] if mode3d else 1
        return render_template(
            "mask_editor.html",
            mode3d=mode3d,
            num_slices=num_slices,
            image_path=img_path,
            mask_path=mask_path,
            warning=None
        )

    # Default GET
    return render_template("index.html")
