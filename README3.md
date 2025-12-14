# MES Project – Dobot Demo Integration

## 📖 Overview
This repository contains my **Manufacturing Execution System (MES) project**.  
I initially completed one cycle of development, but I wasn’t satisfied with the structure.  
To improve clarity and maintainability, I decided to **restart from scratch**, beginning with the **Dobot demo project** provided by my teacher.  

The demo project comes pre‑stacked with the necessary **Dobot SDK libraries** (`DobotDll.dll`, `DobotDllType.py`, etc.), which serve as the foundation for robotic control and integration.

---

## 🎯 Goals
- Build a clean, modular MES project from the ground up.
- Use the Dobot SDK to control robotic arms for demo tasks.
- Establish a framework that can be extended into full MES functionality later.

---

## 📂 Project Structure

```
Group4Project_root_created_251214/
├── 1211DobotSample.py       # Main demo script (waypoint sequence)
├── DobotControl.py          # Example control script (home, PTP motions)
├── DobotDll.dll             # Core C++ SDK library
├── DobotDll.h               # Header file for SDK
├── DobotDllType.py          # Python wrapper for the DLL
├── images/                  # Supporting images
├── __pycache__/             # Python cache
├── .venv/                   # Virtual environment
├── pyproject.toml           # Project configuration
└── README.md                # Project documentation
```