import logging
import os
import subprocess
import sys
import threading
import time

logger = logging.getLogger("VirtualEngineer")


class VirtualEngineerLogic:
    def __init__(self):
        self.last_warning_time = 0
        self.COOLDOWN_SECONDS = 15
        self.worker_script = os.path.join(os.path.dirname(__file__), "tts_worker.py")
        logger.info("Engineer Brain Initialized.")

    def speak(self, text: str):
        logger.info(f"[VOICE]: {text}")

        def _run_tts():
            kwargs = {}
            if sys.platform == "win32":
                kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW

            subprocess.run([sys.executable, self.worker_script, text], **kwargs)

        threading.Thread(target=_run_tts, daemon=True).start()

    def analyze(self, telemetry: dict):
        if not telemetry:
            return

        current_time = time.time()
        if current_time - self.last_warning_time < self.COOLDOWN_SECONDS:
            return

        slip = telemetry.get("slip_angle", [0, 0, 0, 0])
        speed = telemetry.get("speed_kmh", 0)
        gear = telemetry.get("gear", 0)

        # Calculate averages (0,1 = Front | 2,3 = Rear)
        avg_front_slip = (abs(slip[0]) + abs(slip[1])) / 2
        avg_rear_slip = (abs(slip[2]) + abs(slip[3])) / 2

        if avg_front_slip > 0.12 and avg_rear_slip < 0.05 and speed > 50:
            self.speak(
                "Understeer detected in corner. Consider softening the front anti-roll bar."
            )
            self.last_warning_time = current_time

        elif avg_rear_slip > 0.15 and avg_front_slip < 0.06 and speed > 50 and gear > 1:
            self.speak(
                "Loss of rear grip detected. Be careful on exit. You might need to lower the differential preload."
            )
            self.last_warning_time = current_time
