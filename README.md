# 🧠 ProofreadingTool — Online 2D/3D Mask Editor

An interactive **web-based proofreading tool** for biomedical image segmentation.  
It allows users to load 2D images or 3D TIFF stacks, visualize masks, and perform **online correction** (painting, erasing, and slice navigation) directly from a browser.

---

## 🚀 Features

- **2D and 3D TIFF stack support**  
  Load single-plane `.png`/`.jpg` images or multi-slice `.tif`/`.tiff` volumes.

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

🌐 Usage

1. Open http://localhost:5000 in your browser.

2. Choose to load via path (server-side images) or upload files.

3. For 3D datasets, scroll or use navigation buttons to move through slices.

4. Paint, erase, undo/redo edits, and save your corrected masks.

All interactions are performed on a lightweight web frontend built with pure HTML/JS and Flask backend routes (`/api/slice`, `/api/mask/update`, `/api/save`, etc.).
