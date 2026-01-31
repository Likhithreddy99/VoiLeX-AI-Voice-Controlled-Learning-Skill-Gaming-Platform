import speech_recognition as sr
import pyttsx3
import threading
import queue
import time

# =======================
# TEXT TO SPEECH (SAFE)
# =======================

_engine = pyttsx3.init()
_engine.setProperty("rate", 170)

_tts_queue = queue.Queue()

def _tts_worker():
    while True:
        text = _tts_queue.get()
        if text is None:
            break
        try:
            print("SYSTEM:", text)
            _engine.say(text)
            _engine.runAndWait()
        except Exception as e:
            print("TTS ERROR:", e)
        _tts_queue.task_done()

threading.Thread(target=_tts_worker, daemon=True).start()


def speak(text: str):
    """Thread-safe speak"""
    if text:
        _tts_queue.put(text)


# =======================
# SPEECH RECOGNITION CORE
# =======================

_recognizer = sr.Recognizer()
_recognizer.pause_threshold = 0.6
_recognizer.energy_threshold = 300
_recognizer.dynamic_energy_threshold = True


def _listen(timeout, phrase_time_limit):
    with sr.Microphone() as source:
        try:
            _recognizer.adjust_for_ambient_noise(source, duration=0.3)
            audio = _recognizer.listen(
                source,
                timeout=timeout,
                phrase_time_limit=phrase_time_limit
            )
        except sr.WaitTimeoutError:
            return ""

    try:
        return _recognizer.recognize_google(audio).lower().strip()
    except:
        return ""


# =======================
# MENU LISTENER
# =======================

def listen_menu():
    text = _listen(timeout=5, phrase_time_limit=3)

    if not text:
        return ""

    print("YOU (menu):", text)
    t = text.lower()

    if any(w in t for w in ["learning", "learn in", "lurning", "quiz", "study"]):
        return "learning"
    if any(w in t for w in ["maze", "maize", "mayz", "mays"]):
        return "maze"
    if any(w in t for w in ["exit", "quit", "stop", "end"]):
        return "exit"

    return ""


# =======================
# GAME LISTENER (MAZE)
# =======================

def listen():
    text = _listen(timeout=2, phrase_time_limit=1.2)

    if not text:
        return ""

    print("YOU:", text)

    if "up" in text:
        return "up"
    if "down" in text:
        return "down"
    if "left" in text:
        return "left"
    if "right" in text:
        return "right"
    if "exit" in text or "stop" in text:
        return "exit"

    return ""


# =======================
# QUIZ LISTENER (FREE)
# =======================

def listen_quiz():
    text = _listen(timeout=5, phrase_time_limit=3)

    if not text:
        return ""

    print("YOU (quiz):", text)
    return text
