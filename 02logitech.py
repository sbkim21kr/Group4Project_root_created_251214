import cv2
from ultralytics import YOLO
from datetime import datetime
import os
import time
import csv
import threading
import pymcprotocol
import torch   # for CUDA checks

# ==========================
# --- CONFIGURATION BLOCK ---
# ==========================
PLC_IP   = "192.168.3.39"   # PLC IP address
PLC_PORT = 4003             # PLC Port

YOLO_MODEL_PATH = r"C:\Users\windows11\Desktop\Group4Project\251214DefectClassification.v2i.yolov8_new\train_new\weights\best.pt"

SAVE_DIR = "captures"
CSV_FILE = os.path.join(SAVE_DIR, "detections_log.csv")

START_DEVICE = "M402"   # Start trigger device (pulse)
END_DEVICE   = "M401"   # End signal device (pulse)
# ==========================

# --- CUDA check ---
if torch.cuda.is_available():
    DEVICE = "cuda:0"
    gpu_name = torch.cuda.get_device_name(0)
    print(f"[System] CUDA available → GPU detected: {gpu_name}")
else:
    DEVICE = "cpu"
    print("[System] CUDA not available → using CPU")

# --- YOLO model ---
model = YOLO(YOLO_MODEL_PATH)
model.to(DEVICE)   # force model onto chosen device
print(f"[System] YOLO model loaded on {model.device}")

# --- Safety check ---
if torch.cuda.is_available() and str(model.device) == "cpu":
    print("[Warning] CUDA is available but YOLO is running on CPU!")
    print("→ Check your PyTorch/Ultralytics installation or GPU drivers.")

# --- Camera ---
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: Could not open camera.")
    exit()

# --- Save dirs ---
os.makedirs(SAVE_DIR, exist_ok=True)

# --- Initialize CSV ---
if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, mode="w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "filename", "class", "confidence", "x1", "y1", "x2", "y2"])


def capture_frame():
    """Capture one frame and save it immediately (raw)."""
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame.")
        return None, None

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    filename = datetime.now().strftime("%y%m%d_%Hhr%Mmin%Ssec.jpg")
    filepath = os.path.join(SAVE_DIR, filename)

    cv2.imwrite(filepath, frame)
    print(f"[Camera] Photo captured → {filepath}")

    return frame, (timestamp, filename, filepath)


def log_gpu_usage():
    """Log current GPU memory usage if CUDA is available."""
    if torch.cuda.is_available():
        allocated = torch.cuda.memory_allocated(0) / (1024**2)  # MB
        reserved = torch.cuda.memory_reserved(0) / (1024**2)    # MB
        print(f"[GPU] Memory allocated: {allocated:.2f} MB | reserved: {reserved:.2f} MB")


def infer_and_log(frame, meta, plc):
    """Run YOLO inference and log results (async thread)."""
    if frame is None:
        return

    print(f"[YOLO] Starting inference on {DEVICE}...")
    results = model(frame, device=DEVICE, verbose=False)  # force device here too

    # Log GPU usage after inference
    log_gpu_usage()

    annotated_frame = frame.copy()
    detections = []

    h, w = annotated_frame.shape[:2]
    for box in results[0].boxes:
        x1, y1, x2, y2 = box.xyxy[0].int().tolist()
        conf = float(box.conf[0])
        cls_id = int(box.cls[0])
        cls_name = model.names[cls_id]

        # Clamp coords
        x1 = max(0, min(x1, w - 1))
        y1 = max(0, min(y1, h - 1))
        x2 = max(0, min(x2, w - 1))
        y2 = max(0, min(y2, h - 1))

        cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), (0,255,0), 3)
        label = f"{cls_name} {conf:.2f}"
        cv2.putText(annotated_frame, label, (10, h - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 2)

        detections.append((cls_name, conf, x1, y1, x2, y2))

    # Save annotated image
    _, filename, filepath = meta
    cv2.imwrite(filepath, annotated_frame)

    # Log CSV
    with open(CSV_FILE, mode="a", newline="") as f:
        writer = csv.writer(f)
        for det in detections:
            cls_name, conf, x1, y1, x2, y2 = det
            writer.writerow([meta[0], filename, cls_name, f"{conf:.2f}", x1, y1, x2, y2])

    print(f"[YOLO] Inference complete → {filepath}")
    # No need to set M404 here — Festo already handles FAIL flag.


def pulse_bit(plc, device, on_time=0.5, off_time=0.5):
    """Pulse a PLC bit device (set 1 then 0)."""
    plc.batchwrite_bitunits(device, [1])
    time.sleep(on_time)
    plc.batchwrite_bitunits(device, [0])
    time.sleep(off_time)


def main():
    print("[System] Worker started")

    plc = pymcprotocol.Type3E()
    try:
        plc.connect(PLC_IP, PLC_PORT)
        print(f"[PLC] Connected to {PLC_IP}:{PLC_PORT}")
    except Exception as e:
        print(f"[PLC] Initial connect error: {e}")
        return

    try:
        while True:
            trigger_val = int(plc.batchread_bitunits(START_DEVICE, 1)[0])

            if trigger_val == 1:
                print(f"\n[PLC] Trigger received ({START_DEVICE}=1) → capturing image")

                # --- Capture immediately ---
                frame, meta = capture_frame()

                # --- Pulse END_DEVICE right after capture ---
                pulse_bit(plc, END_DEVICE, on_time=0.2, off_time=0.2)
                print("[PLC] END_DEVICE pulsed immediately after capture")

                # --- Run inference asynchronously ---
                t = threading.Thread(target=infer_and_log, args=(frame, meta, plc))
                t.daemon = True
                t.start()

                print("[PLC] Job run complete → waiting for next trigger...")

            time.sleep(0.5)

    except KeyboardInterrupt:
        print("\nStopping worker...")
        cap.release()
        cv2.destroyAllWindows()
        plc.close()
        print("[PLC] Disconnected")


if __name__ == "__main__":
    main()
