import logging
import math
import os
import subprocess
import sys
import threading
import time
from typing import Any, Dict, Optional

from ac_udp_client import TelemetryData

logger = logging.getLogger("VirtualEngineer")


class VirtualEngineerLogic:
    """Advanced virtual race engineer for real-time telemetry analysis."""

    def __init__(self) -> None:
        # Cooldowns per warning type to prevent audio spam
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

        # Exponential Moving Average (EMA) and Event Trackers
        self.ema_alpha = 0.15  # Smoothing factor (lower = smoother but slower reaction)
        self.ema_state = {
            "front_slip": 0.0,
            "rear_slip": 0.0,
            "brake": 0.0
        }
        self.event_durations = {
            "lockup_start": 0.0,
            "understeer_start": 0.0,
            "oversteer_start": 0.0
        }

        self.worker_script: str = os.path.join(
            os.path.dirname(__file__), "tts_worker.py"
        )

        # State tracker for AI tool calling
        self.latest_telemetry: Optional[TelemetryData] = None

        logger.info("Virtual Engineer Brain Initialized with advanced Temporal Heuristics.")

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

    def _update_ema(self, key: str, current_val: float) -> float:
        """Updates the Exponential Moving Average for a given telemetry key."""
        self.ema_state[key] = (self.ema_alpha * current_val) + ((1 - self.ema_alpha) * self.ema_state[key])
        return self.ema_state[key]

    def _handle_sustained_event(
        self, 
        event_key: str, 
        condition: bool, 
        sustain_time: float, 
        message: str, 
        current_time: float
    ) -> None:
        """Helper to manage sustained telemetry events, reducing cognitive complexity."""
        start_key = f"{event_key}_start"
        
        if condition:
            # Event just started
            if math.isclose(self.event_durations[start_key], 0.0, abs_tol=1e-4):
                self.event_durations[start_key] = current_time
            # Event has been sustained past the threshold
            elif current_time - self.event_durations[start_key] > sustain_time and self._can_warn(event_key, current_time):
                self.speak(message)
                self._update_cooldown(event_key, current_time)
        else:
            # Condition broken, reset tracker
            self.event_durations[start_key] = 0.0

    def analyze(self, telemetry: TelemetryData) -> None:
        """Analyzes real-time telemetry and provides actionable driving feedback."""
        if not telemetry:
            return

        self.latest_telemetry = telemetry
        current_time = time.time()

        # Extract telemetry data safely
        slip = telemetry.get("slip_angle", [0.0, 0.0, 0.0, 0.0])
        speed = telemetry.get("speed_kmh", 0.0)
        gear = telemetry.get("gear", 0)
        brake = telemetry.get("brake", 0.0)
        rpm = telemetry.get("engine_rpm", 0.0)
        max_rpm = telemetry.get("max_rpm", 8000.0)

        # Raw Average slip calculations (0,1 = Front | 2,3 = Rear)
        raw_front_slip = (abs(slip[0]) + abs(slip[1])) / 2.0
        raw_rear_slip = (abs(slip[2]) + abs(slip[3])) / 2.0

        # Smoothed values via EMA to filter out 60Hz noise
        ema_front_slip = self._update_ema("front_slip", raw_front_slip)
        ema_rear_slip = self._update_ema("rear_slip", raw_rear_slip)
        ema_brake = self._update_ema("brake", brake)

        # 1. Brake Lockup Detection
        self._handle_sustained_event(
            event_key="lockup",
            condition=(ema_brake > 0.75 and ema_front_slip > 0.12 and speed > 40),
            sustain_time=0.35,
            message="Watch your braking, locking the fronts. Trail off the pedal sooner.",
            current_time=current_time
        )

        # 2. Understeer Detection
        self._handle_sustained_event(
            event_key="understeer",
            condition=(ema_front_slip > 0.12 and ema_rear_slip < 0.05 and speed > 50),
            sustain_time=0.5,
            message="Understeer detected mid-corner. Ease off the throttle or reduce entry speed.",
            current_time=current_time
        )

        # 3. Snap Oversteer Detection
        self._handle_sustained_event(
            event_key="oversteer",
            condition=(ema_rear_slip > 0.15 and ema_front_slip < 0.06 and speed > 50 and gear > 1),
            sustain_time=0.4,
            message="Rear grip is snapping. Smooth out your throttle application on exit.",
            current_time=current_time
        )

        # 4. Over-revving Detection (Immediate trigger, no sustain tracking required)
        if rpm > max_rpm * 0.98 and gear > 0 and self._can_warn("overrev", current_time):
            self.speak("Engine is over-revving. Check your shift points to protect the engine.")
            self._update_cooldown("overrev", current_time)

    def get_llm_context(self) -> str:
        """Formats a human-readable telemetry summary for the LLM prompt."""
        if not self.latest_telemetry:
            return "No telemetry data available. The car might be offline or in the pits."

        t = self.latest_telemetry
        speed = round(t.get("speed_kmh", 0))
        gear = t.get("gear", 0)
        
        # Helper to convert ms to standard m:s.ms timing
        def format_time(ms_val):
            if ms_val <= 0: return "N/A"
            mins = int(ms_val // 60000)
            secs = (ms_val % 60000) / 1000.0
            return f"{mins}:{secs:.3f}"

        lap_time = format_time(t.get("lap_time", 0))
        last_lap = format_time(t.get("last_lap", 0))
        best_lap = format_time(t.get("best_lap", 0))

        context = (
            f"Vehicle: {t.get('car_name', 'Unknown')} | Track: {t.get('track_name', 'Unknown')}.\n"
            f"Current Status: Gear {gear}, Speed {speed} km/h.\n"
            f"Session Times -> Current Lap: {lap_time}, Last Lap: {last_lap}, Best Lap: {best_lap}.\n"
            f"Controls -> Gas: {round(t.get('gas', 0)*100)}%, Brake: {round(t.get('brake', 0)*100)}%.\n"
            f"Engine -> {round(t.get('engine_rpm', 0))} RPM (Max limit: {round(t.get('max_rpm', 8000))}).\n"
        )
        return context
