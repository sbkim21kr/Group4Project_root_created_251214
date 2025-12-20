ROBOT_CONFIGS = {
    "R1": {
        "name": "R1",
        "port": "COM3",        # verify actual COM port
        "bits": {
            "start": "M100",
            "busy":  "M101",
            "done":  "M102",
        },
        "waypoints_file": "data/waypoints_r1.csv",
        "end_effector": "suction",
    },
    "R2": {
        "name": "R2",
        "port": "COM4",        # verify actual COM port
        "bits": {
            "start": "M200",
            "busy":  "M201",
            "done":  "M202",
        },
        "waypoints_file": "data/waypoints_r2.csv",
        "end_effector": "gripper",
    },
    "R3": {
        "name": "R3",
        "port": "COM5",        # verify actual COM port
        "bits": {
            "start": "M300",
            "busy":  "M301",
            "done":  "M302",
        },
        "flags": {
            "p_flag": "M403",
            "f_flag": "M404",
        },
        "waypoints_file": "data/waypoints_r3.csv",
        "end_effector": "suction",
        "p_variants": 4,   # configurable number of P variants
        "f_variants": 4,   # configurable number of F variants
    },
}

PLC_CONFIG = {
    "ip": "192.168.0.1",   # adjust to your PLC IP
    "port": 502,           # adjust to your PLC port
}
