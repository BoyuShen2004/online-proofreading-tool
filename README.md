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


