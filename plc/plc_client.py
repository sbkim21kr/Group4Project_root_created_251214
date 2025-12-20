import pymcprotocol
import time
from utils.logger import log

class PLCClient:
    def __init__(self, ip, port, timeout=3, reconnect_interval=5):
        self.mc = pymcprotocol.Type3E()
        self.mc.timeout = timeout
        self.ip = ip
        self.port = port
        self.reconnect_interval = reconnect_interval
        self._connect_with_retry()

    def _connect_with_retry(self):
        """Try to connect, retrying until success."""
        while True:
            log(f"[PLC] Connecting to {self.ip}:{self.port}...")
            try:
                self.mc.connect(self.ip, self.port)
                log("[PLC] Connected.")
                break
            except Exception as e:
                log(f"[PLC] Connection failed: {e}. Retrying in {self.reconnect_interval}s...")
                time.sleep(self.reconnect_interval)

    def set_bit(self, address, value):
        """Write a single bit ON/OFF to the PLC."""
        try:
            self.mc.batchwrite_bitunits(headdevice=address, values=[value])
            log(f"[PLC] {address} = {'ON' if value else 'OFF'}")
        except Exception as e:
            log(f"[PLC] Failed to set {address}: {e}")
            self._connect_with_retry()  # attempt reconnect

    def read_bit(self, address):
        """Read a single bit from the PLC."""
        try:
            return int(self.mc.batchread_bitunits(headdevice=address, readsize=1)[0])
        except Exception as e:
            log(f"[PLC] Failed to read {address}: {e}")
            self._connect_with_retry()  # attempt reconnect
            return 0  # safe fallback

    def pulse_bit(self, address, on_time=0.2, off_time=0.2):
        """Momentarily set a bit ON then OFF."""
        try:
            self.set_bit(address, 1)
            time.sleep(on_time)
            self.set_bit(address, 0)
            time.sleep(off_time)
            log(f"[PLC] Pulsed {address}")
        except Exception as e:
            log(f"[PLC] Failed to pulse {address}: {e}")
            self._connect_with_retry()

    def detect_rising_edge(self, prev_bits: dict, robot_map: dict):
        """
        Detect rising edges for PLC start bits.
        Returns a list of robot keys that triggered.
        """
        triggered = []
        for key, cfg in robot_map.items():
            start_bit = cfg["bits"]["start"]
            current_val = self.read_bit(start_bit)
            if prev_bits.get(start_bit, 0) == 0 and current_val == 1:
                triggered.append(key)
            prev_bits[start_bit] = current_val
        return triggered