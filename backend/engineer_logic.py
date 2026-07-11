import time
import threading
import pyttsx3
import logging

logger = logging.getLogger("VirtualEngineer")

class VirtualEngineerLogic:
    """Il cervello. Analizza la telemetria pulita e gestisce la sintesi vocale asincrona."""
    
    def __init__(self):
        self.last_warning_time = 0
        self.COOLDOWN_SECONDS = 15 # Non parlare di continuo
        
        # Setup TTS (Isolato nel suo ecosistema)
        self.tts_engine = pyttsx3.init()
        self.tts_engine.setProperty('rate', 155)
        
        voices = self.tts_engine.getProperty('voices')
        for voice in voices:
            if "IT" in voice.id or "Italian" in voice.name:
                self.tts_engine.setProperty('voice', voice.id)
                break
        
        self.speech_lock = threading.Lock()
        logger.info("Motore Sintesi Vocale Inizializzato.")

    def speak(self, text: str):
        """Metodo per parlare senza bloccare il thread principale (Socket/Websocket)"""
        def _speak_thread():
            with self.speech_lock:
                logger.info(f"[VOCE]: {text}")
                self.tts_engine.say(text)
                self.tts_engine.runAndWait()
                
        threading.Thread(target=_speak_thread, daemon=True).start()

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

        # Analisi Base (Da ampliare in futuro con temperature, usura, ecc.)
        if avg_front_slip > 0.12 and avg_rear_slip < 0.05 and speed > 50:
            self.speak("Rilevato sottosterzo in curva. Valuta di ammorbidire la barra antirollio anteriore.")
            self.last_warning_time = current_time
            
        elif avg_rear_slip > 0.15 and avg_front_slip < 0.06 and speed > 50 and gear > 1:
            self.speak("Perdita del posteriore rilevata. Attento in uscita. Potrebbe servire abbassare il precarico differenziale.")
            self.last_warning_time = current_time
