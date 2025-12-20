import csv
import DobotDllType as dType
import time
from utils.logger import log

class RobotBase:
    def __init__(self, cfg, plc_client):
        self.cfg = cfg
        self.name = cfg["name"]
        self.port = cfg["port"]
        self.bits = cfg["bits"]
        self.plc = plc_client
        self.api = dType.load()
        self.connected = False
        self.waypoints = []

    def connect(self):
        state = dType.ConnectDobot(self.api, self.port, 115200)[0]
        if state == dType.DobotConnect.DobotConnect_NoError:
            log(f"[{self.name}] Connected on {self.port}")
            self.connected = True
        else:
            log(f"[{self.name}] Connection failed: {state}")
        return self.connected

    def disconnect(self):
        if self.connected:
            dType.DisconnectDobot(self.api)
            log(f"[{self.name}] Disconnected")
            self.connected = False

    def clear_queue(self):
        dType.SetQueuedCmdClear(self.api)

    def set_motion_params(self):
        dType.SetHOMEParams(self.api, 200,200,200,200, isQueued=1)
        dType.SetPTPJointParams(self.api,
                                200,200,200,200,
                                200,200,200,200,
                                isQueued=1)
        dType.SetPTPCommonParams(self.api, 100, 100, isQueued=1)

    def home(self):
        dType.SetHOMECmd(self.api, temp=0, isQueued=1)

    def load_waypoints_from_csv(self, csv_path):
        waypoints = []
        with open(csv_path, newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                x = float(row["x"])
                y = float(row["y"])
                z = float(row["z"])
                r = float(row["r"])
                vel = float(row["vel"])
                accel = float(row["accel"])
                suction = int(row["suction_gripper"])
                dwell = float(row["dwell_time"])
                move_type = row["move_type"]
                waypoints.append((x,y,z,r,vel,accel,suction,dwell,move_type))
        self.waypoints = waypoints
        log(f"[{self.name}] Loaded {len(waypoints)} waypoints from {csv_path}")

    def run_waypoints(self, waypoints):
        last_index = -1
        for (x,y,z,r,vel,accel,suction,dwell,move_type) in waypoints:
            dType.SetPTPCommonParams(self.api, vel, accel)
            mode = dType.PTPMode.PTPMOVLXYZMode if move_type == "MOVL" else dType.PTPMode.PTPMOVJXYZMode
            last_index = dType.SetPTPCmd(self.api, mode, x,y,z,r, isQueued=1)[0]

            # End effector control based on config
            if self.cfg.get("end_effector") == "suction":
                dType.SetEndEffectorSuctionCup(self.api, 1, suction, 1)
            elif self.cfg.get("end_effector") == "gripper":
                dType.SetEndEffectorGripper(self.api, 1, suction, 1)

            if dwell > 0:
                time.sleep(dwell)

            log(f"[{self.name}] Queued waypoint: X={x},Y={y},Z={z},R={r},Suc={suction},Dw={dwell},Mode={move_type}")
        return last_index

    def execute_queue(self, last_index):
        dType.SetQueuedCmdStartExec(self.api)
        while last_index > dType.GetQueuedCmdCurrentIndex(self.api)[0]:
            dType.dSleep(100)
        dType.SetQueuedCmdStopExec(self.api)
        log(f"[{self.name}] Finished executing queue")

    def run_cycle(self, waypoints=None):
        if not self.connect():
            return
        try:
            # Reset and prepare
            self.clear_queue()
            self.set_motion_params()
            self.home()

            # Run waypoints (from CSV or passed in)
            last_index = self.run_waypoints(waypoints or self.waypoints)

            # Execute queued commands
            self.execute_queue(last_index)

            # Ensure end effector OFF at end of cycle
            if self.cfg.get("end_effector") == "suction":
                dType.SetEndEffectorSuctionCup(self.api, 1, 0, 1)
            elif self.cfg.get("end_effector") == "gripper":
                dType.SetEndEffectorGripper(self.api, 1, 0, 1)

            log(f"[{self.name}] End effector OFF at end of cycle")

            # Optionally report final pose
            pose = dType.GetPose(self.api)
            log(f"[{self.name}] Final coordinates: X={pose[0]}, Y={pose[1]}, Z={pose[2]}, R={pose[3]}")

        finally:
            self.disconnect()
            log(f"[{self.name}] Cycle finished.")