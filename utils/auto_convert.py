import os
from config import ROBOT_CONFIGS
from utils.playback_to_csv import convert_playback_xml_to_csv
from utils.logger import log

def find_playback_file(data_dir, base_name):
    xml_path = os.path.join(data_dir, f"{base_name}.xml")
    playback_path = os.path.join(data_dir, f"{base_name}.playback")
    if os.path.exists(xml_path):
        return xml_path
    elif os.path.exists(playback_path):
        return playback_path
    return None

def convert_variant(data_dir, base_name, csv_path):
    xml_path = find_playback_file(data_dir, base_name)
    if xml_path:
        written, skipped = convert_playback_xml_to_csv(xml_path, csv_path)
        log(f"[AUTO-CONVERT] {os.path.basename(xml_path)} → {written} waypoints, {skipped} skipped")
        return written, skipped   # ✅ return counts so caller can unpack
    else:
        log(f"[AUTO-CONVERT] Skipped {base_name} (not found)")
        return 0, 0               # ✅ safe default return

def auto_convert_all(data_dir="data"):
    total_written = 0
    total_skipped = 0

    for robot_key, cfg in ROBOT_CONFIGS.items():
        if robot_key in ["R1", "R2"]:
            written, skipped = convert_variant(data_dir, robot_key.lower(), cfg["waypoints_file"])
            total_written += written
            total_skipped += skipped
        elif robot_key == "R3":
            for i in range(1, cfg.get("p_variants", 0) + 1):
                written, skipped = convert_variant(
                    data_dir,
                    f"r3_P{i}",
                    os.path.join(data_dir, f"waypoints_r3_P{i}.csv")
                )
                total_written += written
                total_skipped += skipped
            for i in range(1, cfg.get("f_variants", 0) + 1):
                written, skipped = convert_variant(
                    data_dir,
                    f"r3_F{i}",
                    os.path.join(data_dir, f"waypoints_r3_F{i}.csv")
                )
                total_written += written
                total_skipped += skipped

    log(f"[AUTO-CONVERT] Finished batch conversion → {total_written} waypoints total, {total_skipped} skipped")

if __name__ == "__main__":
    auto_convert_all()
