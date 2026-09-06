import sys
import pyttsx3


def speak(text: str, engine=None):
    try:
        # If no engine is provided, initialize a single-use one (backward compatibility)
        if engine is None:
            engine = pyttsx3.init()
            engine.setProperty("rate", 155)
            for voice in engine.getProperty("voices"):
                if "EN" in voice.id or "English" in voice.name:
                    engine.setProperty("voice", voice.id)
                    break

        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        print(f"TTS Worker Error: {e}", file=sys.stderr)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Single-shot execution
        text = sys.argv[1]
        speak(text)
    else:
        # Persistent execution mode reading from stdin
        try:
            # Initialize engine once
            engine = pyttsx3.init()
            engine.setProperty("rate", 155)
            for voice in engine.getProperty("voices"):
                if "EN" in voice.id or "English" in voice.name:
                    engine.setProperty("voice", voice.id)
                    break

            # Read lines from stdin until EOF
            for line in sys.stdin:
                text = line.strip()
                if text:
                    speak(text, engine)
        except Exception as e:
            print(f"TTS Worker Init Error: {e}", file=sys.stderr)
