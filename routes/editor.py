"""
Proofreading Tool - Mask Editor Routes
----------------------------------
Handles mask visualization, editing, and saving.
Supports both 2D and 3D images.
"""

import io
import os
import base64
import numpy as np
import cv2
import tifffile
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
    shape_str = " × ".join(map(str, volume.shape))

    return render_template(
        "mask_editor.html",
        mode3d=mode3d,
        num_slices=num_slices,
        shape=shape_str,
        image_path=st.get("image_path", ""),
        mask_path=st.get("mask_path", "")
    )

# ---------------------------------------------------------
# Utility: convert grayscale array to RGB
# ---------------------------------------------------------
def _to_rgb(arr2d):
    arr = np.asarray(arr2d)
    if arr.ndim == 3 and arr.shape[-1] == 3:
        return arr.astype(np.uint8)
    arr = (arr / arr.max() * 255.0) if arr.max() > 0 else arr
    arr = np.clip(arr, 0, 255).astype(np.uint8)
    return np.stack([arr] * 3, axis=-1)

# ---------------------------------------------------------
# API: image slice
# ---------------------------------------------------------
@bp.get("/api/slice/<int:z>")
def api_slice(z: int):
    volume = current_app.config.get("CURRENT_VOLUME")
    if volume is None:
        return jsonify(error="No volume loaded"), 404
    if volume.ndim == 2:
        sl = volume
    else:
        z = int(np.clip(z, 0, volume.shape[0] - 1))
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
    volume = current_app.config.get("CURRENT_VOLUME")

    # if no mask loaded but an image exists, create a blank one
    if mask is None and volume is not None:
        if volume.ndim == 2:
            mask = np.zeros_like(volume, dtype=np.uint8)
        elif volume.ndim == 3:
            mask = np.zeros_like(volume, dtype=np.uint8)
        current_app.config["CURRENT_MASK"] = mask

    if mask is None:
        return jsonify(error="No mask loaded"), 404

    if mask.ndim == 2:
        sl = mask
    else:
        z = int(np.clip(z, 0, mask.shape[0] - 1))
        sl = mask[z]
    im = Image.fromarray((sl > 0).astype(np.uint8) * 255)
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
    volume = current_app.config.get("CURRENT_VOLUME")

    # --- ensure mask exists for 2D/3D cases ---
    if mask is None and volume is not None:
        if volume.ndim == 2:
            mask = np.zeros_like(volume, dtype=np.uint8)
        elif volume.ndim == 3:
            mask = np.zeros_like(volume, dtype=np.uint8)
        current_app.config["CURRENT_MASK"] = mask
    elif mask is None:
        return jsonify(success=False, error="No mask or image loaded"), 404

    # --- Batch updates ---
    if "full_batch" in data:
        for item in data["full_batch"]:
            z = int(item["z"])
            png_bytes = base64.b64decode(item["png"])
            img = Image.open(io.BytesIO(png_bytes)).convert("L")
            arr = (np.array(img) > 127).astype(np.uint8)

            if mask.ndim == 2:
                arr = cv2.resize(arr, (mask.shape[1], mask.shape[0]), interpolation=cv2.INTER_NEAREST)
                mask[:, :] = arr
            else:
                arr = cv2.resize(arr, (mask.shape[2], mask.shape[1]), interpolation=cv2.INTER_NEAREST)
                mask[z] = arr
        current_app.config["CURRENT_MASK"] = mask
        print(f"✅ Batch updated {len(data['full_batch'])} slice(s)")
        return jsonify(success=True)

    # --- Single slice update ---
    if "full_png" in data:
        z = int(data.get("z", 0))
        png_bytes = base64.b64decode(data["full_png"])
        img = Image.open(io.BytesIO(png_bytes)).convert("L")
        arr = (np.array(img) > 127).astype(np.uint8)

        if mask.ndim == 2:
            arr = cv2.resize(arr, (mask.shape[1], mask.shape[0]), interpolation=cv2.INTER_NEAREST)
            mask[:, :] = arr
        else:
            arr = cv2.resize(arr, (mask.shape[2], mask.shape[1]), interpolation=cv2.INTER_NEAREST)
            mask[z] = arr

        current_app.config["CURRENT_MASK"] = mask
        print(f"✅ Replaced full slice {z}")
        return jsonify(success=True)

    return jsonify(success=False, error="Invalid data"), 400

# ---------------------------------------------------------
# API: save mask (handles 2D, 3D, upload/path modes)
# ---------------------------------------------------------
@bp.post("/api/save")
def api_save():
    sm = current_app.session_manager
    st = sm.snapshot()
    mask = current_app.config.get("CURRENT_MASK")
    volume = current_app.config.get("CURRENT_VOLUME")

    if mask is None and volume is not None:
        if volume.ndim == 2:
            mask = np.zeros_like(volume, dtype=np.uint8)
        elif volume.ndim == 3:
            mask = np.zeros_like(volume, dtype=np.uint8)
        current_app.config["CURRENT_MASK"] = mask
    elif mask is None:
        return jsonify(success=False, error="No mask or image loaded"), 404

    img_path = st.get("image_path")
    mask_path = st.get("mask_path")
    load_mode = st.get("load_mode", "path")

    # Determine save directory and filename
    if load_mode == "upload" or not img_path or not os.path.exists(img_path):
        base_dir = os.path.abspath("./_uploads")
        os.makedirs(base_dir, exist_ok=True)
        base_name = os.path.splitext(os.path.basename(st.get("image_name", "image")))[0]
    else:
        base_dir = os.path.dirname(img_path)
        base_name = os.path.splitext(os.path.basename(img_path))[0]

    # Detect extension
    ext = ".tif"
    if img_path:
        _, src_ext = os.path.splitext(img_path.lower())
        if src_ext in [".png", ".jpg", ".jpeg"]:
            ext = src_ext

    mask_path = os.path.join(base_dir, f"{base_name}_mask{ext}")

    # Save according to extension
    if ext in [".tif", ".tiff"]:
        tifffile.imwrite(mask_path, mask.astype(np.uint8))
    else:
        im = Image.fromarray((mask > 0).astype(np.uint8) * 255)
        im.save(mask_path)

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

# ---------------------------------------------------------
# API: get image dimensions (2D or 3D)
# ---------------------------------------------------------
@bp.post("/api/dims")
def api_dims():
    """
    Accepts: multipart/form-data with 'file'
    Returns: {"shape": [depth?, height, width]} for TIFF stacks or 2D images
    """
    file = request.files.get("file")
    if not file:
        return jsonify({"error": "No file uploaded"}), 400

    fname = file.filename.lower()
    try:
        if fname.endswith((".tif", ".tiff")):
            arr = tifffile.imread(file)
            shape = arr.shape
        else:
            img = Image.open(file)
            shape = img.size[::-1]

        return jsonify({"shape": list(shape)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
