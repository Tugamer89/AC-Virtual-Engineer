import time
import threading
import pyttsx3
import logging
import queue
import platform

logger = logging.getLogger("VirtualEngineer")

class VirtualEngineerLogic:
    """Il cervello. Analizza la telemetria pulita e gestisce la sintesi vocale asincrona."""
    
    def __init__(self):
        self.last_warning_time = 0
        self.COOLDOWN_SECONDS = 15
        self.speech_queue = queue.Queue()
        
        threading.Thread(target=self._audio_worker, daemon=True).start()
        logger.info("Thread Audio Avviato.")
        
    def _audio_worker(self):
        """Questo thread vive per sempre, preleva le frasi dalla coda e le legge ad alta voce."""
        engine = pyttsx3.init()
        engine.setProperty('rate', 155)
        
        voices = engine.getProperty('voices')
        for voice in voices:
            if "IT" in voice.id or "Italian" in voice.name:
                engine.setProperty('voice', voice.id)
                break
        
        # Il loop infinito che ascolta la coda
        while True:
            text = self.speech_queue.get()
            logger.info(f"[VOCE]: {text}")
            engine.say(text)
            engine.runAndWait()
            self.speech_queue.task_done()

    def speak(self, text: str):
        """Invia un messaggio alla coda per farlo pronunciare al worker."""
        self.speech_queue.put(text)

    def analyze(self, telemetry: dict):
        """Riceve il dizionario telemetrico pulito e decide se intervenire."""
        if not telemetry:
            return

        current_time = time.time()
        if current_time - self.last_warning_time < self.COOLDOWN_SECONDS:
            return

        # Estraiamo i dati che ci servono dalla telemetria
        slip = telemetry.get('slip_angle', [0,0,0,0])
        speed = telemetry.get('speed_kmh', 0)
        gear = telemetry.get('gear', 0)

        # Calcolo medie (0,1 = Anteriori | 2,3 = Posteriori)
        avg_front_slip = (abs(slip[0]) + abs(slip[1])) / 2
        avg_rear_slip = (abs(slip[2]) + abs(slip[3])) / 2

        if avg_front_slip > 0.12 and avg_rear_slip < 0.05 and speed > 50:
            self.speak("Rilevato sottosterzo in curva. Valuta di ammorbidire la barra antirollio anteriore.")
            self.last_warning_time = current_time
            
        elif avg_rear_slip > 0.15 and avg_front_slip < 0.06 and speed > 50 and gear > 1:
            self.speak("Perdita del posteriore rilevata. Attento in uscita. Potrebbe servire abbassare il precarico differenziale.")
            self.last_warning_time = current_time
