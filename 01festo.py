import time
import pymcprotocol

# --- Configuration for PLC devices ---
PLC_CONFIG = {
    "connection": {
        "ip": "192.168.3.39",
        "port": 4001,
    },
    "devices": {
        "start_trigger": "M400",   # Start trigger
        "end_pass": "M401",        # End pulse for PASS
        "end_fail": "M402",        # End pulse for FAIL
        "flag_success": "M403",    # Success flag
        "flag_fail": "M404",       # Fail flag
    },
    "io": {
        "bit_switch2": "Y6A",      # Switch ON at connection
        "trigger": "Y6E",          # Trigger pulse
        "result_job2": "X08",      # Result bit (1=pass, 0=fail)
    }
}


class SimpleWorker:
    def __init__(self, config=PLC_CONFIG):
        self.config = config
        self.PLC_IP = config["connection"]["ip"]
        self.PLC_PORT = config["connection"]["port"]
        self.io = config["io"]
        self.devices = config["devices"]

    def pulse_bit(self, address, on_time=0.5, off_time=0.5):
        """Pulse a PLC bit: set 1 then back to 0."""
        self.plc.batchwrite_bitunits(address, [1])
        time.sleep(on_time)
        self.plc.batchwrite_bitunits(address, [0])
        time.sleep(off_time)

    def set_bit(self, address):
        """Set a PLC bit to 1 (latched)."""
        self.plc.batchwrite_bitunits(address, [1])

    def run(self):
        print("[Worker] Starting...")
        self.plc = pymcprotocol.Type3E()
        try:
            self.plc.connect(self.PLC_IP, self.PLC_PORT)
            print("[PLC] Connected")
        except Exception as e:
            print(f"[PLC] Connection failed: {e}")
            return

        # On connection, set Y6A ON
        self.plc.batchwrite_bitunits(self.io["bit_switch2"], [1])
        print("[PLC] bit_switch2 (Y6A) set ON")

        while True:
            try:
                trigger_val = int(self.plc.batchread_bitunits(self.devices["start_trigger"], 1)[0])
            except Exception as e:
                print(f"[PLC] Read error: {e}")
                time.sleep(1)
                continue

            if trigger_val == 1:
                print(f"\n[PLC] Trigger received ({self.devices['start_trigger']}=1)")

                # Pulse trigger Y6E
                self.pulse_bit(self.io["trigger"], 0.5, 0.5)
                print("[PLC] Trigger pulsed (Y6E)")

                # Small wait before reading result
                time.sleep(0.5)

                # Read result X08
                result_val = int(self.plc.batchread_bitunits(self.io["result_job2"], 1)[0])
                print(f"[PLC] Result (X08)={result_val}")

                if result_val == 1:
                    # PASS
                    self.pulse_bit(self.devices["end_pass"], 0.5, 0.5)   # M401 pulse
                    self.set_bit(self.devices["flag_success"])           # M403 set
                    print("[PLC] PASS → Pulsed M401, set M403")
                else:
                    # FAIL
                    self.pulse_bit(self.devices["end_fail"], 0.5, 0.5)   # M402 pulse
                    self.set_bit(self.devices["flag_fail"])              # M404 set
                    print("[PLC] FAIL → Pulsed M402, set M404")

                print("[PLC] Cycle complete → waiting for next trigger...")
            else:
                print(f"\r[PLC] Waiting for {self.devices['start_trigger']}=1...", end="", flush=True)
                time.sleep(1)


# --- Harness ---
if __name__ == "__main__":
    worker = SimpleWorker()
    try:
        worker.run()
    except KeyboardInterrupt:
        print("\nStopping worker...")
