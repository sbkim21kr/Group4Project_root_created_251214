from robot.robot_base import RobotBase
import DobotDllType as dType
from utils.logger import log
import os

class RobotR3(RobotBase):
    """
    RobotR3 extends RobotBase with variant handling.
    It checks PLC flags (p_flag, f_flag) to decide which waypoint file to run.
    """

    def run_cycle(self, waypoints=None):
        if not self.connect():
            return

        try:
            # Reset and prepare
            self.clear_queue()
            self.set_motion_params()
            self.home()

            # --- Variant selection ---
            p_flag = self.plc.read_bit(self.cfg["flags"]["p_flag"])
            f_flag = self.plc.read_bit(self.cfg["flags"]["f_flag"])

            # Default to base waypoints if none triggered
            selected_waypoints = waypoints or self.waypoints

            if p_flag > 0:
                variant_file = f"data/waypoints_r3_P{p_flag}.csv"
                if os.path.exists(variant_file):
                    selected_waypoints = self.load_waypoints_from_csv(variant_file)
                    log(f"[{self.name}] Selected P variant {p_flag}")
                else:
                    log(f"[{self.name}] P variant {p_flag} file not found, using base waypoints")

            elif f_flag > 0:
                variant_file = f"data/waypoints_r3_F{f_flag}.csv"
                if os.path.exists(variant_file):
                    selected_waypoints = self.load_waypoints_from_csv(variant_file)
                    log(f"[{self.name}] Selected F variant {f_flag}")
                else:
                    log(f"[{self.name}] F variant {f_flag} file not found, using base waypoints")

            # --- Run waypoints ---
            last_index = self.run_waypoints(selected_waypoints)

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
