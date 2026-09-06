import sys

import pyttsx3


def speak(text: str):
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


if __name__ == "__main__" and len(sys.argv) > 1:
    text = sys.argv[1]
    speak(text)
