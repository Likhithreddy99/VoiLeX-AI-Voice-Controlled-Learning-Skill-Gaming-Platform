from .voice_engine import speak
from .maze_game_pseudo3d import MazeGame
from .quiz_game import QuizGame


def main_menu():
    speak("Welcome to the learning and gaming system.")

    print("\n===================================")
    print("VOICE CONTROLLED LEARNING GAME")
    print("===================================")
    print("0 → Learning Quiz")
    print("1 → Maze Game")
    print("2 → Exit")
    print("===================================\n")

    while True:
        choice = input("Enter your choice (0 / 1 / 2): ").strip()

        if choice == "0":
            speak("Starting learning quiz.")
            QuizGame()
            break

        elif choice == "1":
            speak("Starting maze game.")
            MazeGame()
            break

        elif choice == "2":
            speak("Exiting system.")
            break

        else:
            print("❌ Invalid input. Please enter 0, 1, or 2.")


if __name__ == "__main__":
    main_menu()
