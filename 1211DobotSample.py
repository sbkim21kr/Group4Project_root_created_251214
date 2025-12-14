import DobotDllType as dType

# === User Config ===
END_EFFECTOR = "suction"   # or "gripper"

# === Waypoints (x, y, z, r, vel, accel, effector_flag, dwelltime, motion) ===
waypoints = [
    (193.0993,-111.9225,-36.4286,-30.0970,0.0,0.0,0,1.0,"J"),
    (6.5021,-226.9309,-31.4505,-88.3588,0.0,0.0,0,1.0,"J"),
    (6.5021,-226.9316,-54.1859,-88.3588,0.5,0.5,0,1.0,"L"),
    (6.5021,-226.9316,-54.1859,-88.3588,0.5,0.5,1,1.0,"L"),
    (6.5021,-226.9316,-30.0000,-88.3588,0.0,0.0,1,1.0,"L"),
    (4.0303,-140.6619,9.6728,-88.3588,0.0,0.0,1,1.0,"J"),
    (6.0301,-210.4582,143.4884,-88.3588,0.0,0.0,1,1.0,"J"),
    (205.0473,47.7979,143.4884,13.1217,0.0,0.0,1,1.0,"J"),
    (269.9973,59.5663,130.0000,12.4412,0.0,0.0,1,1.0,"J"),
    (269.9973,59.5663,112.1037,12.4412,0.5,0.5,1,1.0,"L"),
    (269.9973,59.5663,112.1037,12.4412,0.5,0.5,0,1.0,"L"),
    (269.9973,59.5663,130.0000,12.4412,0.0,0.0,0,1.0,"L"),
    (205.0473,47.7979,143.4884,13.1217,0.0,0.0,0,1.0,"J"),
    (197.4314,-73.1428,143.4884,-20.3282,0.0,0.0,0,1.0,"J"),
    (193.0993,-111.9225,-36.4286,-30.0970,0.0,0.0,0,1.0,"J")
]

# === Main Dobot Control ===
def run_dobot_sequence(waypoints):
    api = dType.load()
    state = dType.ConnectDobot(api, "COM3", 115200)[0]
    print("Connection state:", state)

    if state == dType.DobotConnect.DobotConnect_NoError:
        dType.SetQueuedCmdClear(api)

        # ✅ Safe speed/acceleration settings
        dType.SetPTPJointParams(api, 100,100,100,100,100,100,100,100)
        dType.SetPTPCoordinateParams(api, 100,100,100,100)
        dType.SetPTPCommonParams(api, 50,50)

        # ✅ Force effector OFF at the beginning
        if END_EFFECTOR == "suction":
            dType.SetEndEffectorSuctionCup(api, 1, 0, isQueued=1)
        elif END_EFFECTOR == "gripper":
            dType.SetEndEffectorGripper(api, 1, 0, isQueued=1)

        dType.SetQueuedCmdStartExec(api)

        lastIndex = 0

        for i, (x, y, z, r, vel, accel, effector_flag, dwelltime, motion) in enumerate(waypoints):
            print(f"Waypoint {i}: ({x}, {y}, {z}, {r}) mode={motion} effector={effector_flag} dwell={dwelltime}s")

            # Choose motion style
            if motion == "J":
                mode = dType.PTPMode.PTPMOVJXYZMode
            else:
                mode = dType.PTPMode.PTPMOVLXYZMode

            lastIndex = dType.SetPTPCmd(api, mode, x, y, z, r, isQueued=1)[0]

            # End effector control
            if END_EFFECTOR == "suction":
                dType.SetEndEffectorSuctionCup(api, 1, effector_flag, isQueued=1)
            elif END_EFFECTOR == "gripper":
                dType.SetEndEffectorGripper(api, 1, effector_flag, isQueued=1)

            # Dwell time
            if dwelltime > 0:
                dType.dSleep(int(dwelltime * 1000))

        # ✅ Force effector OFF at the end of the cycle
        if END_EFFECTOR == "suction":
            dType.SetEndEffectorSuctionCup(api, 1, 0, isQueued=1)
        elif END_EFFECTOR == "gripper":
            dType.SetEndEffectorGripper(api, 1, 0, isQueued=1)

        # Wait until last command is done
        while lastIndex > dType.GetQueuedCmdCurrentIndex(api)[0]:
            dType.dSleep(100)

        dType.SetQueuedCmdStopExec(api)

        pose = dType.GetPose(api)
        print("Final coordinates (X, Y, Z, R):", pose[0], pose[1], pose[2], pose[3])

        dType.DisconnectDobot(api)
        print("Finished waypoint sequence.")
    else:
        print("Failed to connect to Dobot. Check COM port and device status.")

# === Run ===
if __name__ == "__main__":
    run_dobot_sequence(waypoints)
