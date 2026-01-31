import pygame
import random
import math
import threading
from .voice_engine import speak, listen

# ---------------- CONFIG ----------------
WIDTH, HEIGHT = 900, 700
CELL = 50
ROWS, COLS = 12, 12

BG_COLOR = (15, 15, 20)
WALL_COLOR = (70, 70, 90)
PLAYER_COLOR = (80, 180, 255)
GOAL_COLOR = (0, 200, 120)

PLAYER_RADIUS = 12
# ----------------------------------------


class Cell:
    def __init__(self, r, c):
        self.r = r
        self.c = c
        self.visited = False
        self.walls = {
            "top": True,
            "right": True,
            "bottom": True,
            "left": True
        }


class MazeGame:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Voice-Controlled Pseudo-3D Maze")

        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()

        self.grid = [[Cell(r, c) for c in range(COLS)] for r in range(ROWS)]
        self.generate_maze(0, 0)

        # Player starts at center of (0,0)
        self.player_row = 0
        self.player_col = 0
        self.player_x = CELL // 2
        self.player_y = CELL // 2

        # Goal at bottom-right
        self.goal_row = ROWS - 1
        self.goal_col = COLS - 1
        self.goal_x = self.goal_col * CELL + CELL // 2
        self.goal_y = self.goal_row * CELL + CELL // 2

        # Voice handling (NON-BLOCKING)
        self.last_command = None
        self.listening = True
        threading.Thread(target=self.voice_listener, daemon=True).start()

        speak("Pseudo 3D maze game started")
        speak("Say move up, down, left or right")

        self.run()

    # ---------- BACKGROUND VOICE THREAD ----------
    def voice_listener(self):
        while self.listening:
            try:
                cmd = listen()
                if cmd:
                    self.last_command = cmd
            except:
                pass

    # ---------- MAZE GENERATION ----------
    def generate_maze(self, r, c):
        cell = self.grid[r][c]
        cell.visited = True

        directions = ["top", "right", "bottom", "left"]
        random.shuffle(directions)

        for d in directions:
            nr, nc = r, c
            if d == "top": nr -= 1
            elif d == "bottom": nr += 1
            elif d == "left": nc -= 1
            elif d == "right": nc += 1

            if 0 <= nr < ROWS and 0 <= nc < COLS and not self.grid[nr][nc].visited:
                cell.walls[d] = False
                opposite = {
                    "top": "bottom",
                    "bottom": "top",
                    "left": "right",
                    "right": "left"
                }
                self.grid[nr][nc].walls[opposite[d]] = False
                self.generate_maze(nr, nc)

    # ---------- DRAWING ----------
    def draw_maze(self, cam_x, cam_y):
        wall_thickness = 6
        for r in range(ROWS):
            for c in range(COLS):
                cell = self.grid[r][c]
                x = c * CELL - cam_x
                y = r * CELL - cam_y

                if cell.walls["top"]:
                    pygame.draw.rect(self.screen, WALL_COLOR, (x, y, CELL, wall_thickness))
                if cell.walls["bottom"]:
                    pygame.draw.rect(
                        self.screen, WALL_COLOR,
                        (x, y + CELL - wall_thickness, CELL, wall_thickness)
                    )
                if cell.walls["left"]:
                    pygame.draw.rect(self.screen, WALL_COLOR, (x, y, wall_thickness, CELL))
                if cell.walls["right"]:
                    pygame.draw.rect(
                        self.screen, WALL_COLOR,
                        (x + CELL - wall_thickness, y, wall_thickness, CELL)
                    )

    def draw_player(self, cam_x, cam_y):
        pygame.draw.circle(
            self.screen,
            PLAYER_COLOR,
            (int(self.player_x - cam_x), int(self.player_y - cam_y)),
            PLAYER_RADIUS
        )

    def draw_goal(self, cam_x, cam_y):
        pygame.draw.circle(
            self.screen,
            GOAL_COLOR,
            (int(self.goal_x - cam_x), int(self.goal_y - cam_y)),
            16
        )

    # ---------- MOVEMENT WITH COLLISION ----------
    def move(self, direction):
        cell = self.grid[self.player_row][self.player_col]

        if direction == "up":
            if cell.walls["top"]:
                speak("Wall ahead")
                return
            self.player_row -= 1

        elif direction == "down":
            if cell.walls["bottom"]:
                speak("Wall ahead")
                return
            self.player_row += 1

        elif direction == "left":
            if cell.walls["left"]:
                speak("Wall ahead")
                return
            self.player_col -= 1

        elif direction == "right":
            if cell.walls["right"]:
                speak("Wall ahead")
                return
            self.player_col += 1

        # Clamp safety
        self.player_row = max(0, min(ROWS - 1, self.player_row))
        self.player_col = max(0, min(COLS - 1, self.player_col))

        # Snap to center of cell
        self.player_x = self.player_col * CELL + CELL // 2
        self.player_y = self.player_row * CELL + CELL // 2

    # ---------- HANDLE VOICE (NON-BLOCKING) ----------
    def handle_voice(self):
        if not self.last_command:
            return

        command = self.last_command
        self.last_command = None

        if "up" in command:
            self.move("up")
        elif "down" in command:
            self.move("down")
        elif "left" in command:
            self.move("left")
        elif "right" in command:
            self.move("right")
        elif "exit" in command:
            speak("Exiting maze")
            self.listening = False
            pygame.quit()
            exit()

    # ---------- GAME LOOP ----------
    def run(self):
        while True:
            self.clock.tick(60)
            self.screen.fill(BG_COLOR)

            cam_x = self.player_x - WIDTH // 2
            cam_y = self.player_y - HEIGHT // 2

            self.draw_maze(cam_x, cam_y)
            self.draw_goal(cam_x, cam_y)
            self.draw_player(cam_x, cam_y)

            self.handle_voice()

            # Win condition
            if self.player_row == self.goal_row and self.player_col == self.goal_col:
                speak("Congratulations. Maze completed.")
                pygame.time.delay(2000)
                pygame.quit()
                exit()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()

            pygame.display.flip()


if __name__ == "__main__":
    MazeGame()
