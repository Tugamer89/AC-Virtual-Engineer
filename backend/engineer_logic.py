import logging
import os
import subprocess
import sys
import threading
import time
from typing import Any, Dict

from ac_udp_client import TelemetryData

logger = logging.getLogger("VirtualEngineer")


class VirtualEngineerLogic:
    """Advanced virtual race engineer for real-time telemetry analysis."""

    def __init__(self) -> None:
        # Separate cooldowns per warning type to prevent suppressing crucial data
        self.cooldowns: Dict[str, float] = {
            "understeer": 0.0,
            "oversteer": 0.0,
            "lockup": 0.0,
            "shift": 0.0,
            "overrev": 0.0,
        }

        # Base cooldown durations in seconds
        self.TIMEOUTS = {
            "understeer": 15.0,
            "oversteer": 12.0,
            "lockup": 10.0,
            "shift": 5.0,
            "overrev": 8.0,
        }

        self.worker_script: str = os.path.join(
            os.path.dirname(__file__), "tts_worker.py"
        )
        logger.info("Virtual Engineer Brain Initialized with advanced heuristics.")

    def speak(self, text: str) -> None:
        """Dispatches text-to-speech to a background worker."""
        logger.info(f"[ENGINEER COMMS]: {text}")

        def _run_tts() -> None:
            kwargs: Dict[str, Any] = {}
            if sys.platform == "win32":
                kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW

            try:
                subprocess.run([sys.executable, self.worker_script, text], **kwargs)
            except Exception as e:
                logger.exception(f"TTS Worker execution failed: {e}")

        threading.Thread(target=_run_tts, daemon=True).start()

    def _can_warn(self, warning_type: str, current_time: float) -> bool:
        """Checks if a specific warning type is off cooldown."""
        if current_time - self.cooldowns.get(warning_type, 0) > self.TIMEOUTS.get(
            warning_type, 15
        ):
            return True
        return False

    def _update_cooldown(self, warning_type: str, current_time: float) -> None:
        self.cooldowns[warning_type] = current_time

    def analyze(self, telemetry: TelemetryData) -> None:
        """Analyzes real-time telemetry and provides actionable driving feedback."""
        if not telemetry:
            return

        current_time = time.time()

        # Extract telemetry data safely
        slip = telemetry.get("slip_angle", [0.0, 0.0, 0.0, 0.0])
        speed = telemetry.get("speed_kmh", 0.0)
        gear = telemetry.get("gear", 0)
        brake = telemetry.get("brake", 0.0)
        rpm = telemetry.get("engine_rpm", 0.0)
        max_rpm = telemetry.get("max_rpm", 8000.0)

        # Average slip calculations (0,1 = Front | 2,3 = Rear)
        avg_front_slip = (abs(slip[0]) + abs(slip[1])) / 2.0
        avg_rear_slip = (abs(slip[2]) + abs(slip[3])) / 2.0

        # 1. Brake Lockup Detection (High braking + front slip spike)
        if (
            brake > 0.8
            and avg_front_slip > 0.15
            and speed > 40
            and self._can_warn("lockup", current_time)
        ):
            self.speak(
                "Watch your braking, locking the fronts. Trail off the pedal sooner."
            )
            self._update_cooldown("lockup", current_time)
            return  # Prioritize lockup warning over cornering warnings

        # 2. Over-revving Detection (Downshifting too early or missing upshift)
        if (
            rpm > max_rpm * 0.98
            and gear > 0
            and self._can_warn("overrev", current_time)
        ):
            self.speak(
                "Engine is over-revving. Check your shift points to protect the engine."
            )
            self._update_cooldown("overrev", current_time)
            return

        # 3. Understeer Detection
        if (
            avg_front_slip > 0.12
            and avg_rear_slip < 0.05
            and speed > 50
            and self._can_warn("understeer", current_time)
        ):
            self.speak(
                "Understeer detected mid-corner. Consider softening the front anti-roll bar or reducing entry speed."
            )
            self._update_cooldown("understeer", current_time)

        # 4. Snap Oversteer / Loss of rear grip Detection
        elif (
            avg_rear_slip > 0.15
            and avg_front_slip < 0.06
            and speed > 50
            and gear > 1
            and self._can_warn("oversteer", current_time)
        ):
            self.speak(
                "Rear grip is snapping. Smooth out your throttle application on exit. Consider lowering differential preload."
            )
            self._update_cooldown("oversteer", current_time)
