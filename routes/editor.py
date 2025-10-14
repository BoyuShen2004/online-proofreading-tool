"""
Proofreading Tool - Mask Editor Routes
----------------------------------
Handles mask visualization, editing, and saving.
Supports multi-slice caching (all 3D edits saved together).
"""

import io
import os
import base64
import numpy as np
import cv2
from flask import Blueprint, render_template, request, send_file, current_app, jsonify
from PIL import Image
from backend.volume_manager import save_mask

bp = Blueprint("editor", __name__, url_prefix="")

def register_editor_routes(app):
    app.register_blueprint(bp)

# ---------------------------------------------------------
# Main editor page
# ---------------------------------------------------------
@bp.route("/edit", methods=["GET"])
def editor():
    sm = current_app.session_manager
    st = sm.snapshot()
    if not st["image_path"]:
        from flask import redirect, url_for
        return redirect(url_for("landing.index"))

    volume = current_app.config.get("CURRENT_VOLUME")
    if volume is None:
        from flask import redirect, url_for
        return redirect(url_for("landing.index"))

    mode3d = isinstance(volume, np.ndarray) and volume.ndim == 3
    num_slices = volume.shape[0] if mode3d else 1
    return render_template("mask_editor.html", mode3d=mode3d, num_slices=num_slices)

# ---------------------------------------------------------
# Utility: convert grayscale array to RGB
# ---------------------------------------------------------
def _to_rgb(arr2d):
    arr = np.asarray(arr2d)
    if arr.ndim == 3 and arr.shape[-1] == 3:
        return arr.astype(np.uint8)
    arr = (arr / arr.max() * 255.0) if arr.max() > 0 else arr
    arr = np.clip(arr, 0, 255).astype(np.uint8)
    return np.stack([arr]*3, axis=-1)

# ---------------------------------------------------------
# API: image slice
# ---------------------------------------------------------
@bp.get("/api/slice/<int:z>")
def api_slice(z: int):
    volume = current_app.config.get("CURRENT_VOLUME")
    if volume is None:
        return jsonify(error="No volume loaded"), 404
    if volume.ndim == 2:
        z = 0
        sl = volume
    else:
        z = int(np.clip(z, 0, volume.shape[0]-1))
        sl = volume[z]
    rgb = _to_rgb(sl)
    bio = io.BytesIO()
    Image.fromarray(rgb).save(bio, format="PNG")
    bio.seek(0)
    return send_file(bio, mimetype="image/png")

# ---------------------------------------------------------
# API: mask slice
# ---------------------------------------------------------
@bp.get("/api/mask/<int:z>")
def api_mask(z: int):
    mask = current_app.config.get("CURRENT_MASK")
    if mask is None:
        return jsonify(error="No mask loaded"), 404
    if mask.ndim == 2:
        z = 0
        sl = mask
    else:
        z = int(np.clip(z, 0, mask.shape[0]-1))
        sl = mask[z]
    im = Image.fromarray((sl > 0).astype(np.uint8)*255)
    bio = io.BytesIO()
    im.save(bio, format="PNG")
    bio.seek(0)
    return send_file(bio, mimetype="image/png")

# ---------------------------------------------------------
# API: update mask (multi-slice batch)
# ---------------------------------------------------------
@bp.post("/api/mask/update")
def api_mask_update():
    """
    Accepts:
    - {"full_png": base64str, "z": int}
    - {"full_batch": [{"z": int, "png": base64str}, ...]}
    """
    data = request.get_json(force=True)
    mask = current_app.config.get("CURRENT_MASK")
    if mask is None:
        return jsonify(success=False, error="No mask loaded"), 404

    # --- Batch updates (multiple slices) ---
    if "full_batch" in data:
        from io import BytesIO
        from PIL import Image
        for item in data["full_batch"]:
            z = int(item["z"])
            png_bytes = base64.b64decode(item["png"])
            img = Image.open(BytesIO(png_bytes)).convert("L")
            arr = (np.array(img) > 127).astype(np.uint8)
            if mask.ndim == 2:
                current_app.config["CURRENT_MASK"] = arr
            else:
                arr = cv2.resize(arr, (mask.shape[2], mask.shape[1]), interpolation=cv2.INTER_NEAREST)
                mask[z] = arr
        current_app.config["CURRENT_MASK"] = mask
        print(f"✅ Batch updated {len(data['full_batch'])} slice(s)")
        return jsonify(success=True)

    # --- Single slice update (legacy) ---
    if "full_png" in data:
        z = int(data.get("z", 0))
        png_bytes = base64.b64decode(data["full_png"])
        img = Image.open(io.BytesIO(png_bytes)).convert("L")
        arr = (np.array(img) > 127).astype(np.uint8)
        if mask.ndim == 2:
            current_app.config["CURRENT_MASK"] = arr
        else:
            arr = cv2.resize(arr, (mask.shape[2], mask.shape[1]), interpolation=cv2.INTER_NEAREST)
            mask[z] = arr
            current_app.config["CURRENT_MASK"] = mask
        print(f"✅ Replaced full slice {z}")
        return jsonify(success=True)

    return jsonify(success=False, error="Invalid data"), 400

# ---------------------------------------------------------
# API: save to original mask file
# ---------------------------------------------------------
@bp.post("/api/save")
def api_save():
    sm = current_app.session_manager
    st = sm.snapshot()
    mask_path = st.get("mask_path")

    if not mask_path or not os.path.exists(mask_path):
        img_path = st["image_path"]
        base_dir = os.path.dirname(img_path)
        base_name = os.path.splitext(os.path.basename(img_path))[0]
        mask_path = os.path.join(base_dir, f"{base_name}_mask.tif")

    mask = current_app.config["CURRENT_MASK"]
    save_mask(mask, mask_path)
    print(f"💾 Saved mask to {mask_path}")
    return jsonify(success=True, path=mask_path)

# ---------------------------------------------------------
# API: download current mask
# ---------------------------------------------------------
@bp.get("/api/download")
def api_download():
    sm = current_app.session_manager
    st = sm.snapshot()
    mask_path = st.get("mask_path")
    if not mask_path or not os.path.exists(mask_path):
        return jsonify(success=False, error="Nothing saved yet"), 404
    return send_file(mask_path, as_attachment=True)
