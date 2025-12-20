from multiprocessing import Process, Semaphore
from config import PLC_CONFIG, ROBOT_CONFIGS
from plc.plc_client import PLCClient   # ✅ only import PLCClient now
from robot.robot_r1 import RobotR1
from robot.robot_r2 import RobotR2
from robot.robot_r3 import RobotR3
from utils.logger import log
from utils.auto_convert import auto_convert_all
import time

# Limit concurrent robot processes (adjust as needed)
semaphore = Semaphore(3)   # allow up to 3 robots in parallel

def run_robot(robot_class, cfg):
    """Run a robot cycle with waypoints (if applicable)."""
    with semaphore:  # block if too many robots running
        robot = robot_class(cfg, port=cfg["port"])
        waypoints = None if cfg["name"] == "R3" else robot.load_waypoints_from_csv(cfg["waypoints_file"])
        robot.run_cycle(waypoints)

def main():
    # Convert XMLs to CSVs at startup
    auto_convert_all("data")

    # Single PLC client for triggers + resets
    plc = PLCClient(**PLC_CONFIG)

    # Track previous bit states for rising-edge detection
    prev_bits = {
        ROBOT_CONFIGS["R1"]["bits"]["start"]: 0,
        ROBOT_CONFIGS["R2"]["bits"]["start"]: 0,
        ROBOT_CONFIGS["R3"]["bits"]["start"]: 0,
    }

    log("[SYSTEM] Waiting for PLC triggers...")

    try:
        while True:
            triggered = plc.detect_rising_edge(prev_bits, ROBOT_CONFIGS)

            for key in triggered:
                if key == "R1":
                    Process(target=run_robot, args=(RobotR1, ROBOT_CONFIGS["R1"])).start()
                    plc.set_bit(ROBOT_CONFIGS["R1"]["bits"]["start"], 0)  # reset start bit
                elif key == "R2":
                    Process(target=run_robot, args=(RobotR2, ROBOT_CONFIGS["R2"])).start()
                    plc.set_bit(ROBOT_CONFIGS["R2"]["bits"]["start"], 0)  # reset start bit
                elif key == "R3":
                    Process(target=run_robot, args=(RobotR3, ROBOT_CONFIGS["R3"])).start()
                    plc.set_bit(ROBOT_CONFIGS["R3"]["flags"]["p_flag"], 0)
                    plc.set_bit(ROBOT_CONFIGS["R3"]["flags"]["f_flag"], 0)
                    log("[R3] Reset PLC flags M403/M404 after cycle")

            time.sleep(0.1)  # small delay to avoid busy loop

    except KeyboardInterrupt:
        log("[SYSTEM] Shutting down gracefully...")
        try:
            plc.mc.close()
        except Exception as e:
            log(f"[PLC] Error closing connection: {e}")

if __name__ == "__main__":
    main()