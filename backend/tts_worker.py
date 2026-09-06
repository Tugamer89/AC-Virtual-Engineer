import logging
import sys
from typing import Optional
import pyttsx3

logger = logging.getLogger(__name__)


def init_engine() -> pyttsx3.Engine:
    """Inizializza e configura l'engine vocale pyttsx3."""
    engine = pyttsx3.init()
    engine.setProperty("rate", 155)
    for voice in engine.getProperty("voices"):
        if "EN" in voice.id or "English" in voice.name:
            engine.setProperty("voice", voice.id)
            break
    return engine


def speak(text: str, engine: Optional[pyttsx3.Engine] = None) -> None:
    """Pronuncia il testo; se l'engine non è passato ne crea uno temporaneo."""
    try:
        if engine is None:
            engine = init_engine()

        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        logger.exception("TTS Worker Error: %s", e)


def main_single(text: str) -> None:
    """Esecuzione singola (supporto retrocompatibilità)."""
    speak(text)


def main() -> None:
    """Modalità persistente: legge da stdin riga per riga."""
    try:
        engine = init_engine()

        for line in sys.stdin:
            text = line.strip()
            if text:
                speak(text, engine)
    except Exception as e:
        print(f"TTS Worker Error: {e}", file=sys.stderr)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Modalità a riga di comando con unione degli argomenti multipli
        text = " ".join(sys.argv[1:])
        speak(text)
    else:
        # Modalità persistente in ascolto su stdin
        main()
