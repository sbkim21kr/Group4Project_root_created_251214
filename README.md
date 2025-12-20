# VisionFlip

Multi-robot PLC and vision integration project using Dobot arms, Festo sensors, and YOLOv8 camera.

---

## 🚀 Overview
This project demonstrates how to integrate **industrial robots, PLC systems, and vision AI** into a single workflow.  
It was developed as a trade school project to showcase automation concepts and can serve as a demo platform for sales technicians or engineers.

---

## ✨ Features
- **PLC Integration**: Communication with Mitsubishi PLC using `pymcprotocol`.
- **Robot Control**: Playback file parsing and waypoint execution for Dobot arms.
- **Vision System**: Logitech camera + YOLOv8 inference for defect detection.
- **GPU Acceleration**: Automatic CUDA detection and logging of GPU memory usage.
- **Reproducible Environment**: Clean dependency management with `pyproject.toml` and `uv sync`.

---

## 🛠️ Requirements
- Python **3.13.7**
- [uv package manager](https://github.com/astral-sh/uv)
- Windows 10/11 (tested)
- NVIDIA GPU with CUDA drivers (optional, for YOLO acceleration)

---

## 📦 Installation
Clone the repository and install dependencies:

```bash
uv sync
```

---

## ▶️ Running the Project
```bash
uv run python 00main.py     # Orchestrates PLC + robots
uv run python 01festo.py    # Festo sensor worker
uv run python 02logitech.py # Vision worker with YOLOv8
```

---

## 📊 Output
- PLC ladder logic triggers robot actions.
- Vision worker logs GPU usage and defect classification.
- Results are printed to console and can be extended to dashboards or reports.

---

## 📄 License
MIT License.

---

## 👤 Authors
Sangbum Kim
Contact: sbkim21@gmail.com
```
