import pygame
import json
import os
import threading
import time
import re
from .voice_engine import speak, listen_quiz

# ---------- CONFIG ----------
WIDTH, HEIGHT = 900, 600
BG_COLOR = (18, 18, 24)
TEXT_COLOR = (230, 230, 240)
CORRECT_COLOR = (0, 200, 120)
WRONG_COLOR = (220, 80, 80)
ACCENT_COLOR = (90, 160, 255)
# ----------------------------


def normalize(text):
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9 ]", "", text)
    return text


# number mappings for voice tolerance
WORD_TO_DIGIT = {
    "zero": "0", "one": "1", "two": "2", "three": "3",
    "four": "4", "five": "5", "six": "6", "seven": "7",
    "eight": "8", "nine": "9", "ten": "10"
}

DIGIT_TO_WORD = {v: k for k, v in WORD_TO_DIGIT.items()}

YES_WORDS = {"yes", "yeah", "yep", "yup", "haa", "haan", "correct", "true"}


class QuizGame:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Voice-Controlled Learning Quiz")

        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()

        self.font_big = pygame.font.SysFont("arial", 36, bold=True)
        self.font_small = pygame.font.SysFont("arial", 24)

        base_dir = os.path.dirname(__file__)
        data_path = os.path.join(base_dir, "..", "data", "quiz_questions.json")

        with open(data_path, "r") as f:
            self.questions = json.load(f)

        self.index = 0
        self.score = 0
        self.feedback = ""
        self.feedback_color = TEXT_COLOR

        self.last_answer = None
        self.listening = True

        threading.Thread(target=self.voice_listener, daemon=True).start()

        speak("Welcome to the learning quiz.")
        self.run()

    # ---------- VOICE THREAD ----------
    def voice_listener(self):
        while self.listening:
            ans = listen_quiz()
            if ans and self.last_answer is None:
                self.last_answer = ans

    # ---------- DRAW ----------
    def draw(self):
        self.screen.fill(BG_COLOR)

        title = self.font_big.render("Learning Quiz", True, ACCENT_COLOR)
        self.screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 40))

        pygame.draw.rect(
            self.screen, (40, 40, 55),
            (80, 140, 740, 200),
            border_radius=12
        )

        question = self.questions[self.index]["question"]
        wrapped = self.wrap_text(question, self.font_small, 700)

        y = 170
        for line in wrapped:
            text = self.font_small.render(line, True, TEXT_COLOR)
            self.screen.blit(text, (100, y))
            y += 30

        feedback = self.font_big.render(self.feedback, True, self.feedback_color)
        self.screen.blit(feedback, (WIDTH // 2 - feedback.get_width() // 2, 380))

        footer = self.font_small.render(
            f"Question {self.index + 1} / {len(self.questions)}   Score: {self.score}",
            True,
            TEXT_COLOR
        )
        self.screen.blit(footer, (WIDTH // 2 - footer.get_width() // 2, 520))

        pygame.display.flip()

    # ---------- TEXT WRAP ----------
    def wrap_text(self, text, font, max_width):
        words = text.split()
        lines = []
        current = ""

        for w in words:
            test = current + w + " "
            if font.size(test)[0] <= max_width:
                current = test
            else:
                lines.append(current)
                current = w + " "
        lines.append(current)
        return lines

    # ---------- CHECK ANSWER ----------
    def handle_answer(self):
        if self.last_answer is None:
            return

        user_answer = normalize(self.last_answer)
        correct_answer = normalize(self.questions[self.index]["answer"])

        print("DEBUG → User:", user_answer, "| Correct:", correct_answer)

        self.last_answer = None

        is_correct = False

        # 1️⃣ Direct / partial match
        if correct_answer in user_answer or user_answer in correct_answer:
            is_correct = True

        # 2️⃣ Word → digit (four → 4)
        if correct_answer in WORD_TO_DIGIT:
            if WORD_TO_DIGIT[correct_answer] in user_answer:
                is_correct = True

        # 3️⃣ Digit → word (4 → four)
        if correct_answer in DIGIT_TO_WORD:
            if DIGIT_TO_WORD[correct_answer] in user_answer:
                is_correct = True

        # 4️⃣ Sentence tolerance (keywords)
        for word in correct_answer.split():
            if word in user_answer:
                is_correct = True

        # 5️⃣ Yes/No tolerance
        if correct_answer == "yes" and any(w in user_answer for w in YES_WORDS):
            is_correct = True

        # ----- RESULT -----
        if is_correct:
            self.score += 1
            self.feedback = "Correct Answer"
            self.feedback_color = CORRECT_COLOR
            speak("Correct answer")
        else:
            self.feedback = "Wrong Answer"
            self.feedback_color = WRONG_COLOR
            speak(f"Wrong answer. The correct answer is {correct_answer}")

        self.draw()
        pygame.time.delay(1500)

        self.feedback = ""
        self.index += 1

        if self.index >= len(self.questions):
            speak(f"Quiz completed. Your score is {self.score}")
            pygame.time.delay(2000)
            pygame.quit()
            return

    # ---------- MAIN LOOP ----------
    def run(self):
        while True:
            self.clock.tick(60)
            self.draw()
            self.handle_answer()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
