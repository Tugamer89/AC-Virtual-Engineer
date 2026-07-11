import time
import threading
import logging
import subprocess
import sys
import os

logger = logging.getLogger("VirtualEngineer")


class VirtualEngineerLogic:
    """Il cervello. Analizza la telemetria e gestisce la sintesi vocale."""

    def __init__(self):
        self.last_warning_time = 0
        self.COOLDOWN_SECONDS = 15
        self.worker_script = os.path.join(os.path.dirname(__file__), "tts_worker.py")
        logger.info("Cervello Ingegnere Inizializzato.")

    def speak(self, text: str):
        """Usa un micro-processo separato per garantire che pyttsx3 non vada in crash col server asincrono."""
        logger.info(f"[VOCE]: {text}")

        def _run_tts():
            kwargs = {}
            if sys.platform == "win32":
                kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW

            subprocess.run([sys.executable, "-c", text], **kwargs)

        threading.Thread(target=_run_tts, daemon=True).start()

    def analyze(self, telemetry: dict):
        """Riceve il dizionario telemetrico pulito e decide se intervenire."""
        if not telemetry:
            return

        current_time = time.time()
        if current_time - self.last_warning_time < self.COOLDOWN_SECONDS:
            return

        # Estraiamo i dati che ci servono dalla telemetria
        slip = telemetry.get("slip_angle", [0, 0, 0, 0])
        speed = telemetry.get("speed_kmh", 0)
        gear = telemetry.get("gear", 0)

        # Calcolo medie (0,1 = Anteriori | 2,3 = Posteriori)
        avg_front_slip = (abs(slip[0]) + abs(slip[1])) / 2
        avg_rear_slip = (abs(slip[2]) + abs(slip[3])) / 2

        if avg_front_slip > 0.12 and avg_rear_slip < 0.05 and speed > 50:
            self.speak(
                "Rilevato sottosterzo in curva. Valuta di ammorbidire la barra antirollio anteriore."
            )
            self.last_warning_time = current_time

        elif avg_rear_slip > 0.15 and avg_front_slip < 0.06 and speed > 50 and gear > 1:
            self.speak(
                "Perdita del posteriore rilevata. Attento in uscita. Potrebbe servire abbassare il precarico differenziale."
            )
            self.last_warning_time = current_time
