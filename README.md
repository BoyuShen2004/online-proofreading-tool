# 🧠 ProofreadingTool — Online 2D/3D Mask Editor

An interactive **web-based proofreading tool** for biomedical image segmentation.  
It allows users to load 2D images or 3D TIFF stacks, visualize masks, and perform **online correction** (painting, erasing, and slice navigation) directly from a browser.

---

## 🚀 Features

- **2D and 3D TIFF stack support**  
  Load single-plane `.png`/`.jpg`/`.jpeg` images or multi-slice `.tif`/`.tiff` volumes.

- **Interactive mask editing**  
  Paint and erase with adjustable brush sizes; supports undo/redo and real-time display.

- **Slice navigation (3D mode)**  
  Step through Z-slices using buttons or keyboard shortcuts (`←/→` or `A/D`).

- **Keyboard shortcuts**
  - ⌘/Ctrl + Z → Undo  
  - ⌘/Ctrl + Shift + Z or Y → Redo  
  - ⌘/Ctrl + Scroll → Zoom  
  - A/D or ←/→ → Navigate slices

- **Integrated dataset management**  
  Switch datasets via path input or file upload directly from the editor page.

- **Lightweight & Portable**  
  Built on **Flask + HTML5 Canvas** — no heavy client installation required.

---

## ⚙️ Setup Guide

### 1. Clone the Repository
```bash
git clone https://github.com/<your-username>/ProofreadingTool.git
cd ProofreadingTool
```

### 2. Create Virtual Environment

From your screenshot, the required environment looks like this:
```bash
conda create -n proofreadingtool python=3.10
conda activate proofreadingtool
pip install flask pillow numpy opencv-python tifffile
```

### 3. Run the Flask Server
```bash
python app.py
```

This will launch a local development server (default: `http://127.0.0.1:5000`).

---

## 🖥️ Running on an HPC Server

You can run the tool on an HPC (e.g., MIT ORCD) and access it from your local machine browser.

### 1. Port Forwarding (on your local terminal)
```bash
ssh -L 5002:127.0.0.1:5002 <username>@orcd-login001.mit.edu
```

### 2. Create Virtual Environment
```bash
conda activate proofreadingtool
```

### 3. Run the Flask Server
```bash
python app.py
```

### 4. Access in Your Browser

Once the server starts, open this on your local machine:
```bash
http://127.0.0.1:5002
```

---

## 📂 File Handling on HPC

When running on the HPC:

- Two ways to load data

  1. Upload from your local computer directly via the browser.

  2. Load existing files from absolute server paths (e.g., `/orcd/data/.../images/sample.tif`).

- Saving behavior

  - If you edit without an existing mask, clicking Save will automatically create a mask file with the same base name as the image and suffix `_mask`.

  - Example:
    Editing worm_stack.tif → Saves as worm_stack_mask.tif

  - The output mask file preserves the original image’s format (.tif, .png, .jpg, .jpeg).
