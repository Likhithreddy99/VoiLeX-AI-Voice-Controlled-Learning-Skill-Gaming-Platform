import json
import os
from .voice_engine import speak, listen



def start_learning():
    speak("Welcome to learning mode")

    # Correct path to questions.json
    base_dir = os.path.dirname(__file__)
    data_path = os.path.join(base_dir, "..", "data", "questions.json")

    with open(data_path, "r") as f:
        questions = json.load(f)

    score = 0

    for q in questions:
        speak(q["question"])
        answer = listen()

        if q["answer"] in answer:
            speak("Correct")
            score += 1
        else:
            speak(f"Wrong. Correct answer is {q['answer']}")

    speak(f"Learning completed. Your score is {score}")
