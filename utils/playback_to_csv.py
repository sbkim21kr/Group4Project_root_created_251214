import csv
import xml.etree.ElementTree as ET
from utils.logger import log

def convert_playback_xml_to_csv(xml_path: str, csv_path: str):
    """
    Parse Dobot Studio playback XML and export waypoints to CSV with 10 parameters:
    x, y, z, r, vel, accel, suction/gripper, dwell_time, move_type, label
    Returns: (written_count, skipped_count)
    """

    headers = [
        "x", "y", "z", "r",
        "vel", "accel",
        "suction_gripper", "dwell_time",
        "move_type", "label"
    ]

    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
    except Exception as e:
        log(f"[CSV] Failed to parse XML {xml_path}: {e}")
        return 0, 0

    written_count = 0
    skipped_count = 0

    try:
        with open(csv_path, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(headers)

            # Iterate over all children whose tag starts with "row"
            for row in root:
                if row.tag.startswith("row"):
                    items = {child.tag: child.text for child in row}

                    # ✅ Skip rows missing coordinate fields
                    if not all(k in items for k in ("item_2", "item_3", "item_4", "item_5")):
                        skipped_count += 1
                        log(f"[CSV] Skipped row without coordinates in {xml_path}")
                        continue

                    try:
                        x = float(items.get("item_2"))
                        y = float(items.get("item_3"))
                        z = float(items.get("item_4"))
                        r = float(items.get("item_5"))

                        vel = float(items.get("item_6", 100.0))
                        accel = float(items.get("item_7", 100.0))
                        dwell = float(items.get("item_10", 0.0))
                        suction = int(items.get("item_12", 0))

                        move_type_raw = items.get("item_1", "MOVJ").upper()
                        move_type = "MOVL" if "MOVL" in move_type_raw else "MOVJ"

                        label = items.get("item_1", "").strip()

                        writer.writerow([x, y, z, r, vel, accel, suction, dwell, move_type, label])
                        written_count += 1

                    except Exception as e:
                        skipped_count += 1
                        log(f"[CSV] Skipped malformed row in {xml_path}: {e}")

        log(f"[CSV] Finished writing {csv_path} → {written_count} waypoints, {skipped_count} skipped")
        return written_count, skipped_count

    except Exception as e:
        log(f"[CSV] Failed to write CSV {csv_path}: {e}")
        return 0, 0
