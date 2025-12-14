import os
import xml.etree.ElementTree as ET

def load_playback_file(filename):
    """
    Load playback file (XML format).
    Extract waypoints: x, y, z, r, vel, accel, suction/gripper
    """
    try:
        if not os.path.exists(filename):
            print(f"Error: File not found at '{filename}'")
            return None

        tree = ET.parse(filename)
        root = tree.getroot()
    except ET.ParseError as e:
        print(f"Error: Failed to parse XML file '{filename}'. Details: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred while loading the file: {e}")
        return None

    waypoints = []
    for row in root:
        if row.tag.startswith("row"):
            try:
                x = float(row.find("item_2").text)
                y = float(row.find("item_3").text)
                z = float(row.find("item_4").text)
                r = float(row.find("item_5").text)

                vel = float(row.find("item_10").text) if row.find("item_10") is not None and row.find("item_10").text else 50.0
                accel = vel
                suction_gripper = int(row.find("item_12").text) if row.find("item_12") is not None and row.find("item_12").text else 0

                wp = (x, y, z, r, vel, accel, suction_gripper)
                waypoints.append(wp)
            except Exception as e:
                print(f"Skipping {row.tag} due to error: {e}")
    return waypoints


def export_to_script():
    """
    Ask the user for a playback XML file path,
    load waypoints, and export them to a Python list-of-dicts format.
    """
    filename = input("📝 Please enter the XML or .playback filename (e.g., my_path.xml): ").strip()
    if not filename:
        print("Filename cannot be empty. Exiting.")
        return

    waypoints = load_playback_file(filename)
    if not waypoints:
        print("Cannot export: Waypoints list is empty.")
        return

    base_name = os.path.splitext(filename)[0]
    out_filename = base_name + "_script.py"

    try:
        with open(out_filename, 'w') as f:
            f.write("[\n")
            for i, wp in enumerate(waypoints):
                x, y, z, r, vel, accel, sg = wp
                dwell = 0.0
                mode = "L"
                if i == 0:
                    mode = "J"
                if i == 1:
                    dwell = 0.3

                line = (
                    f'    {{"x":{x:.4f}, "y":{y:.4f}, "z":{z:.4f}, "r":{r:.4f}, '
                    f'"vel":{vel:.4f}, "accel":{accel:.4f}, "ee":{sg}, '
                    f'"dwell":{dwell}, "mode":"{mode}"}},'
                )
                if i == 0:
                    line += "  # soft home start"
                f.write(line + "\n")

            f.write("    # if last waypoint != first, script will auto-append first as soft home end\n")
            f.write("]\n")

        print(f"✅ Successfully exported {len(waypoints)} waypoints to **{out_filename}**")
    except Exception as e:
        print(f"Error writing to file: {e}")


if __name__ == "__main__":
    export_to_script()
