import pygame
import random
import sys
import math

# --- Settings ---
WIDTH, HEIGHT = 950, 800
GRID_SIZE = 8
TILE_SIZE = 75
OFFSET_X, OFFSET_Y = 50, 150
MOVE_LIMIT = 20

# Colors
BG_COLOR = (245, 250, 245)
PANEL_COLOR = (26, 44, 26)
WHITE = (255, 255, 255)
GOLD = (241, 196, 15)

# Icon Themes & Messages
THEMES = {
    1: {"color": (34, 139, 34), "msg": "PLANT A TREE, BREATHE FREE!"},
    2: {"color": (52, 152, 219), "msg": "WATER IS LIFE, SAVE IT!"},
    3: {"color": (127, 140, 141), "msg": "RECYCLE FOR A CLEANER WORLD!"},
    4: {"color": (241, 196, 15), "msg": "SOLAR ENERGY: PURE & BRIGHT!"},
    5: {"color": (46, 204, 113), "msg": "GO GREEN, SAVE THE PLANET!"},
    6: {"color": (236, 240, 241), "msg": "WIND POWER: CLEAN MOTION!"}
}

class FloatingText:
    def __init__(self, x, y, text, color):
        self.x, self.y = x, y
        self.text, self.color = text, color
        self.alpha = 255
    def draw(self, screen, font):
        if self.alpha > 0:
            s = font.render(self.text, True, self.color)
            s.set_alpha(self.alpha)
            screen.blit(s, (self.x - s.get_width()//2, self.y))
            self.y -= 0.7  # Slow "Floating" speed
            self.alpha -= 3 # Gentle Fade
            return True
        return False

class EcoCrushPro:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Eco-Crush: Environmental Protection")
        self.font_ui = pygame.font.SysFont("Verdana", 38, bold=True)
        self.font_pop = pygame.font.SysFont("Verdana", 22, bold=True)
        self.score, self.moves = 0, MOVE_LIMIT
        self.popups, self.selected = [], None
        self.generate_clean_board()

    def generate_clean_board(self):
        while True:
            self.grid = [[random.randint(1, 6) for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
            if not self.check_matches(dry_run=True): break

    def draw_real_icon(self, r, c, val):
        x = OFFSET_X + c * TILE_SIZE
        y = OFFSET_Y + r * TILE_SIZE
        center = (x + TILE_SIZE//2, y + TILE_SIZE//2)
        color = THEMES[val]["color"]

        # Tile Background
        rect = pygame.Rect(x+4, y+4, TILE_SIZE-8, TILE_SIZE-8)
        pygame.draw.rect(self.screen, WHITE, rect, border_radius=15)
        if self.selected == (r, c):
            pygame.draw.rect(self.screen, (0, 0, 0), rect, 4, border_radius=15)

        # Drawing Detailed Icons
        if val == 1: # TREE
            pygame.draw.rect(self.screen, (101, 67, 33), (center[0]-4, center[1], 8, 20)) # Trunk
            pygame.draw.circle(self.screen, color, (center[0], center[1]-5), 18) # Leaves
            pygame.draw.circle(self.screen, color, (center[0]-10, center[1]+5), 12)
            pygame.draw.circle(self.screen, color, (center[0]+10, center[1]+5), 12)
        elif val == 2: # WATER DROP
            pygame.draw.circle(self.screen, color, (center[0], center[1]+5), 16)
            pygame.draw.polygon(self.screen, color, [(center[0], center[1]-22), (center[0]-14, center[1]+5), (center[0]+14, center[1]+5)])
            pygame.draw.circle(self.screen, WHITE, (center[0]-6, center[1]+2), 4) # Reflection
        elif val == 3: # BIN
            pygame.draw.rect(self.screen, color, (center[0]-15, center[1]-10, 30, 32), border_radius=2)
            pygame.draw.rect(self.screen, color, (center[0]-18, center[1]-15, 36, 5)) # Lid
            for i in range(-8, 9, 8): pygame.draw.line(self.screen, WHITE, (center[0]+i, center[1]-5), (center[0]+i, center[1]+15), 2)
        elif val == 4: # SUN
            pygame.draw.circle(self.screen, color, center, 15)
            for i in range(8):
                ang = i * (math.pi/4)
                px, py = center[0]+math.cos(ang)*22, center[1]+math.sin(ang)*22
                pygame.draw.line(self.screen, color, center, (px, py), 4)
        elif val == 5: # LEAF
            pygame.draw.ellipse(self.screen, color, (center[0]-20, center[1]-12, 40, 24))
            pygame.draw.line(self.screen, WHITE, (center[0]-20, center[1]), (center[0]+20, center[1]), 2)
        elif val == 6: # TURBINE
            pygame.draw.rect(self.screen, (100, 100, 100), (center[0]-2, center[1]-5, 4, 30)) # Pole
            for i in range(3):
                ang = i * (2*math.pi/3)
                px, py = center[0]+math.cos(ang)*20, center[1]+math.sin(ang)*20
                pygame.draw.line(self.screen, color, center, (px, py), 5)

    def check_matches(self, dry_run=False):
        to_remove = set()
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                if c < GRID_SIZE - 2 and self.grid[r][c] == self.grid[r][c+1] == self.grid[r][c+2]:
                    to_remove.update([(r,c), (r,c+1), (r,c+2)])
                if r < GRID_SIZE - 2 and self.grid[r][c] == self.grid[r+1][c] == self.grid[r+2][c]:
                    to_remove.update([(r,c), (r+1,c), (r+2,c)])
        
        if to_remove and not dry_run:
            m_type = self.grid[list(to_remove)[0][0]][list(to_remove)[0][1]]
            self.popups.append(FloatingText(WIDTH//2 - 120, OFFSET_Y - 60, THEMES[m_type]["msg"], THEMES[m_type]["color"]))
            for r, c in to_remove: self.grid[r][c] = 0
            self.score += 5 # STRICT 5 POINT INCREASE
            self.refill()
            return True
        return len(to_remove) > 0

    def refill(self):
        for c in range(GRID_SIZE):
            for r in range(GRID_SIZE-1, -1, -1):
                if self.grid[r][c] == 0:
                    for r_above in range(r-1, -1, -1):
                        if self.grid[r_above][c] != 0:
                            self.grid[r][c], self.grid[r_above][c] = self.grid[r_above][c], 0
                            break
                    if self.grid[r][c] == 0: self.grid[r][c] = random.randint(1, 6)

    def run(self):
        clock = pygame.time.Clock()
        running = True
        while self.moves > 0 and running:
            self.screen.fill(BG_COLOR)
            # Dashboard Panel
            pygame.draw.rect(self.screen, PANEL_COLOR, (720, 0, 230, HEIGHT))
            lbl_score = self.font_ui.render("SCORE", True, WHITE)
            val_score = self.font_ui.render(str(self.score), True, GOLD)
            lbl_moves = self.font_ui.render("MOVES", True, WHITE)
            val_moves = self.font_ui.render(str(self.moves), True, (255, 100, 100))
            
            self.screen.blit(lbl_score, (740, 180))
            self.screen.blit(val_score, (740, 240))
            self.screen.blit(lbl_moves, (740, 420))
            self.screen.blit(val_moves, (740, 480))

            for r in range(GRID_SIZE):
                for c in range(GRID_SIZE): self.draw_real_icon(r, c, self.grid[r][c])

            self.popups = [p for p in self.popups if p.draw(self.screen, self.font_pop)]

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = pygame.mouse.get_pos()
                    c, r = (mx - OFFSET_X) // TILE_SIZE, (my - OFFSET_Y) // TILE_SIZE
                    if 0 <= r < GRID_SIZE and 0 <= c < GRID_SIZE:
                        if not self.selected: self.selected = (r, c)
                        else:
                            r2, c2 = self.selected
                            if abs(r-r2) + abs(c-c2) == 1:
                                self.grid[r][c], self.grid[r2][c2] = self.grid[r2][c2], self.grid[r][c]
                                if self.check_matches(): self.moves -= 1
                                else: self.grid[r][c], self.grid[r2][c2] = self.grid[r2][c2], self.grid[r][c]
                            self.selected = None
            self.check_matches()

            pygame.display.flip()
            clock.tick(60)

        # EXIT SCREEN
        self.screen.fill((34, 139, 34))
        finish = self.font_ui.render(f"FINAL SCORE: {self.score}", True, WHITE)
        self.screen.blit(finish, (WIDTH//2 - finish.get_width()//2, HEIGHT//2))
        pygame.display.flip()
        pygame.time.wait(3000)
        pygame.quit()
        return self.score

def run_game():
    """Wrapper function to be called from Streamlit."""
    game = EcoCrushPro()
    score = game.run()
    return score

if __name__ == "__main__":
    final_score = run_game()
    print(f"Game finished with score: {final_score}")