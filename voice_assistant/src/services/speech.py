from typing import Optional

import speech_recognition as sr


def listen_for_text(recognizer: Optional[sr.Recognizer] = None) -> Optional[str]:
    recognizer = recognizer or sr.Recognizer()

    try:
        with sr.Microphone() as source:
            print("Listening... (speak now)")
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=12)
        return recognizer.recognize_google(audio)
    except Exception as exc:
        print(f"Microphone not available or speech recognition failed ({exc}).")
        try:
            return input("Type instead (or press Enter to skip): ").strip() or None
        except EOFError:
            return None
