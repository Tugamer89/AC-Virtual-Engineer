import sys
import pyttsx3


def main():
    try:
        engine = pyttsx3.init()
        engine.setProperty("rate", 155)

        for voice in engine.getProperty("voices"):
            if "EN" in voice.id or "English" in voice.name:
                engine.setProperty("voice", voice.id)
                break

        # Read from stdin line by line
        for line in sys.stdin:
            text = line.strip()
            if text:
                engine.say(text)
                engine.runAndWait()
    except Exception as e:
        print(f"TTS Worker Error: {e}", file=sys.stderr)


def main_single(text: str):
    try:
        engine = pyttsx3.init()
        engine.setProperty("rate", 155)

        for voice in engine.getProperty("voices"):
            if "EN" in voice.id or "English" in voice.name:
                engine.setProperty("voice", voice.id)
                break

        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        print(f"TTS Worker Error: {e}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Legacy mode support if needed
        text = " ".join(sys.argv[1:])
        main_single(text)
    else:
        # Persistent mode reading from stdin
        main()
