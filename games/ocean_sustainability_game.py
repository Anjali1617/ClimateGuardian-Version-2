"""
=============================================================
  🌊  OCEAN GUARDIAN — Sustainability Mission Game  🌊
=============================================================
  A Python / Pygame game where you captain a ship fitted
  with a detector ray.  Scan the ocean, collect waste,
  plant seagrass, and restore ocean biodiversity!

  HOW TO INSTALL & RUN
  --------------------
  1.  pip install pygame
  2.  python ocean_sustainability_game.py

  CONTROLS
  --------
  ← → Arrow Keys  :  Move ship left / right
  SPACE           :  Fire detector ray downward
  R               :  Restart after Game Over / Win screen
  ESC             :  Quit
=============================================================
"""

import pygame
import random
import math
import sys
import json
import os

def save_score(score):
    """Save the final score to a JSON file to integrate with Streamlit."""
    score_file = os.path.join(os.path.dirname(__file__), 'ocean_guardian_score.json')
    try:
        with open(score_file, 'w') as f:
            json.dump({'score': score}, f)
    except Exception:
        pass

# ──────────────────────────────────────────────
#  CONSTANTS
# ──────────────────────────────────────────────
W, H          = 900, 650
FPS           = 60
OCEAN_TOP     = 180          # y where the ocean surface starts
SHIP_Y        = OCEAN_TOP - 55

# Colours
C_SKY         = (135, 206, 235)
C_OCEAN_DEEP  = (0,  80, 140)
C_OCEAN_MID   = (0, 105, 180)
C_OCEAN_SURF  = (30, 150, 210)
C_WAVE        = (100, 180, 230)
C_SAND        = (210, 180, 100)
C_RAY         = (0, 255, 180, 160)
C_WHITE       = (255, 255, 255)
C_BLACK       = (10,  10,  20)
C_GREEN       = (30, 200,  80)
C_DARK_GREEN  = (20, 140,  50)
C_RED         = (220,  60,  60)
C_YELLOW      = (255, 210,  50)
C_ORANGE      = (255, 140,  30)
C_GRAY        = (160, 160, 160)
C_BROWN       = (130,  80,  30)
C_HUD_BG      = (0,   30,  60, 200)

# Game settings
WASTE_COUNT   = 12
FISH_COUNT    = 6
PLANT_COUNT   = 5
SCORE_PER_WASTE   = 50
SCORE_PER_PLANT   = 80

# ──────────────────────────────────────────────
#  SLOGANS displayed after each cleanup action
# ──────────────────────────────────────────────
SLOGANS = [
    "🌿  Clean water = Happy fish!",
    "💧  Every drop matters — protect our oceans!",
    "🐟  Fish thrive when oceans are alive!",
    "🌊  A plastic-free sea is a biodiversity key!",
    "🌱  Seagrass planted — oxygen granted!",
    "♻️   Reduce, Reuse, Recycle — save marine life!",
    "🐠  One less bottle = one more fish!",
    "🦈  Biodiversity begins with YOU!",
    "🌍  Healthy oceans, healthy planet!",
    "🐙  Protect aquatic life — pick up the strife!",
    "🌺  Plant seagrass today, save species tomorrow!",
    "🚢  Guardian of the seas — that's you!",
]

# ──────────────────────────────────────────────
#  HELPER — draw rounded rect with alpha
# ──────────────────────────────────────────────
def draw_alpha_rect(surf, colour_rgba, rect, radius=8):
    s = pygame.Surface((rect[2], rect[3]), pygame.SRCALPHA)
    pygame.draw.rect(s, colour_rgba, (0, 0, rect[2], rect[3]), border_radius=radius)
    surf.blit(s, (rect[0], rect[1]))


# ──────────────────────────────────────────────
#  WASTE ITEM
# ──────────────────────────────────────────────
WASTE_TYPES = [
    {"name": "Plastic Bottle", "colour": (200, 230, 255), "shape": "bottle",  "size": 22},
    {"name": "Old Tyre",       "colour": (60,  60,  60),  "shape": "circle",  "size": 20},
    {"name": "Tin Can",        "colour": (180, 180, 160),  "shape": "rect",    "size": 18},
    {"name": "Plastic Bag",    "colour": (230, 230, 255),  "shape": "bag",     "size": 24},
    {"name": "Oil Drum",       "colour": (80,  60,  40),   "shape": "rect",    "size": 26},
    {"name": "Net Fragment",   "colour": (200, 180, 120),  "shape": "net",     "size": 28},
]

class WasteItem:
    def __init__(self):
        self.reset()

    def reset(self):
        wtype      = random.choice(WASTE_TYPES)
        self.name  = wtype["name"]
        self.colour= wtype["colour"]
        self.shape = wtype["shape"]
        self.size  = wtype["size"]
        self.x     = random.randint(40, W - 40)
        self.y     = random.randint(OCEAN_TOP + 60, H - 80)
        self.collected = False
        self.seagrass  = False        # grass planted here
        self.grass_grow= 0            # 0-1 animation
        self.slogan_timer = 0

    def draw(self, surf):
        if self.collected and not self.seagrass:
            return
        if self.seagrass:
            self._draw_grass(surf)
            return
        c = self.colour
        s = self.size
        x, y = int(self.x), int(self.y)
        if self.shape == "bottle":
            pygame.draw.ellipse(surf, c, (x-s//3, y-s, s*2//3, s*2))
            pygame.draw.rect(surf, c, (x-s//6, y-s-8, s//3, 10))
        elif self.shape == "circle":
            pygame.draw.circle(surf, c, (x, y), s)
            pygame.draw.circle(surf, (90, 90, 90), (x, y), s-6, 4)
        elif self.shape == "rect":
            pygame.draw.rect(surf, c, (x-s, y-s//2, s*2, s))
            pygame.draw.line(surf, (200,200,200), (x-s+4, y), (x+s-4, y), 2)
        elif self.shape == "bag":
            pts = [(x, y-s),(x-s//2, y),(x-s//3, y+s//2),(x+s//3, y+s//2),(x+s//2, y)]
            pygame.draw.polygon(surf, c, pts)
        elif self.shape == "net":
            for dx in range(-s//2, s//2+1, 8):
                pygame.draw.line(surf, c, (x+dx, y-s//2), (x+dx, y+s//2), 2)
            for dy in range(-s//2, s//2+1, 8):
                pygame.draw.line(surf, c, (x-s//2, y+dy), (x+s//2, y+dy), 2)

    def _draw_grass(self, surf):
        g = min(1.0, self.grass_grow)
        x, y = int(self.x), int(self.y)
        num_blades = 5
        for i in range(num_blades):
            bx = x - 14 + i * 7
            height = int(22 * g)
            lean   = math.sin(pygame.time.get_ticks()/600 + i) * 4
            colour = C_DARK_GREEN if i % 2 == 0 else C_GREEN
            pygame.draw.line(surf, colour, (bx, y), (bx + int(lean), y - height), 3)
            # leaf tip
            if g > 0.5:
                pygame.draw.ellipse(surf, colour,
                    (bx + int(lean) - 3, y - height - 5, 6, 8))

    def update(self):
        if self.seagrass and self.grass_grow < 1.0:
            self.grass_grow += 0.02
        if self.slogan_timer > 0:
            self.slogan_timer -= 1

    def rect(self):
        return pygame.Rect(self.x - self.size, self.y - self.size,
                           self.size * 2, self.size * 2)


# ──────────────────────────────────────────────
#  FISH
# ──────────────────────────────────────────────
FISH_COLOURS = [(255,100,80),(255,200,50),(100,200,255),(180,255,100),
                (255,140,200),(120,220,180)]

class Fish:
    def __init__(self):
        self.reset()

    def reset(self):
        self.x     = random.randint(-50, W + 50)
        self.y     = random.randint(OCEAN_TOP + 30, H - 60)
        self.vx    = random.choice([-1, 1]) * random.uniform(0.8, 2.2)
        self.vy    = random.uniform(-0.3, 0.3)
        self.colour= random.choice(FISH_COLOURS)
        self.size  = random.randint(10, 20)
        self.scared= False
        self.tail_t= 0

    def update(self, waste_list):
        self.tail_t += 0.18
        # avoid waste
        for w in waste_list:
            if not w.collected:
                d = math.hypot(self.x - w.x, self.y - w.y)
                if d < 60:
                    self.vx += (self.x - w.x) * 0.04
                    self.vy += (self.y - w.y) * 0.04
        self.vx = max(-3, min(3, self.vx))
        self.vy = max(-1.5, min(1.5, self.vy))
        self.x += self.vx
        self.y += self.vy
        if self.y < OCEAN_TOP + 10: self.y = OCEAN_TOP + 10
        if self.y > H - 40:         self.y = H - 40
        if self.x < -60:   self.x = W + 50
        if self.x > W + 60: self.x = -50

    def draw(self, surf):
        x, y = int(self.x), int(self.y)
        s = self.size
        flip = self.vx < 0
        # body
        body = pygame.Surface((s*3, s*2), pygame.SRCALPHA)
        pygame.draw.ellipse(body, (*self.colour, 230), (0, 0, s*3, s*2))
        # tail
        tail_wave = int(math.sin(self.tail_t) * 4)
        if flip:
            pts = [(s*3, s + tail_wave), (s*3+s, s - s//2), (s*3+s, s + s//2 + tail_wave)]
        else:
            pts = [(0, s + tail_wave), (-s, s - s//2), (-s, s + s//2 + tail_wave)]
        pygame.draw.polygon(body, (*self.colour, 200), pts if not flip else
            [(s*3, s + tail_wave), (s*3+s, s - s//2), (s*3+s, s + s//2)])
        surf.blit(body, (x - s, y - s))
        # eye
        ex = x - s//2 if flip else x + s
        pygame.draw.circle(surf, C_WHITE, (ex, y - s//4), 3)
        pygame.draw.circle(surf, C_BLACK, (ex, y - s//4), 2)


# ──────────────────────────────────────────────
#  BUBBLE PARTICLE
# ──────────────────────────────────────────────
class Bubble:
    def __init__(self, x, y):
        self.x  = x + random.randint(-10, 10)
        self.y  = y
        self.r  = random.randint(3, 8)
        self.vy = random.uniform(-1.5, -0.5)
        self.life = 1.0

    def update(self):
        self.y  += self.vy
        self.life -= 0.015
        self.x  += math.sin(self.life * 10) * 0.5

    def draw(self, surf):
        alpha = int(self.life * 180)
        s = pygame.Surface((self.r*2+2, self.r*2+2), pygame.SRCALPHA)
        pygame.draw.circle(s, (200, 230, 255, alpha), (self.r+1, self.r+1), self.r, 2)
        surf.blit(s, (int(self.x)-self.r-1, int(self.y)-self.r-1))


# ──────────────────────────────────────────────
#  SHIP
# ──────────────────────────────────────────────
class Ship:
    SPEED = 4

    def __init__(self):
        self.x       = W // 2
        self.y       = SHIP_Y
        self.ray_active = False
        self.ray_y   = self.y + 30
        self.ray_target_y = H - 60
        self.ray_progress = 0.0   # 0→1→0
        self.ray_phase= 0         # 0=extending, 1=retracting
        self.cooldown = 0
        self.collecting = None    # waste item currently being collected
        self.collect_anim = 0
        self.trail = []

    def move(self, keys):
        if keys[pygame.K_LEFT]:
            self.x = max(50, self.x - self.SPEED)
        if keys[pygame.K_RIGHT]:
            self.x = min(W - 50, self.x + self.SPEED)
        self.trail.append((self.x, self.y))
        if len(self.trail) > 20:
            self.trail.pop(0)

    def fire_ray(self):
        if not self.ray_active and self.cooldown == 0:
            self.ray_active   = True
            self.ray_progress = 0.0
            self.ray_phase    = 0

    def update(self, waste_list, bubbles):
        if self.cooldown > 0:
            self.cooldown -= 1
        if self.ray_active:
            speed = 0.04
            if self.ray_phase == 0:
                self.ray_progress += speed
                if self.ray_progress >= 1.0:
                    self.ray_progress = 1.0
                    self.ray_phase = 1
                    # check hit
                    ray_x = self.x
                    for w in waste_list:
                        if not w.collected:
                            if abs(w.x - ray_x) < 30:
                                w.collected = True
                                self.collecting = w
                                self.collect_anim = 30
                                for _ in range(15):
                                    bubbles.append(Bubble(w.x, w.y))
            else:
                self.ray_progress -= speed
                if self.ray_progress <= 0.0:
                    self.ray_active    = False
                    self.ray_progress  = 0.0
                    self.cooldown      = 30
        if self.collect_anim > 0:
            self.collect_anim -= 1
            if self.collect_anim == 0 and self.collecting:
                self.collecting.seagrass = True
                self.collecting = None

    def draw(self, surf):
        x, y = int(self.x), self.y
        # hull
        hull_pts = [(x-45, y+20),(x+45, y+20),(x+55, y+5),(x-55, y+5)]
        pygame.draw.polygon(surf, (60, 80, 120), hull_pts)
        pygame.draw.polygon(surf, (100, 140, 200), hull_pts, 2)
        # cabin
        pygame.draw.rect(surf, (180, 200, 230), (x-20, y-20, 40, 28), border_radius=4)
        pygame.draw.rect(surf, (100, 160, 220), (x-14, y-14, 14, 14))  # window
        pygame.draw.rect(surf, (100, 160, 220), (x+2,  y-14, 14, 14))
        # chimney + smoke
        pygame.draw.rect(surf, (50, 50, 60), (x-8, y-32, 10, 16))
        smoke_x = x - 3
        smoke_y = y - 34
        for i in range(3):
            alpha = 120 - i * 35
            r = 4 + i * 3
            ss = pygame.Surface((r*2, r*2), pygame.SRCALPHA)
            pygame.draw.circle(ss, (180,180,180,alpha), (r,r), r)
            surf.blit(ss, (smoke_x - r + i*3, smoke_y - i*7 - r))
        # mast + flag
        pygame.draw.line(surf, (80, 60, 40), (x+15, y-20), (x+15, y-55), 3)
        flag_pts = [(x+15, y-55),(x+35, y-47),(x+15, y-40)]
        pygame.draw.polygon(surf, C_GREEN, flag_pts)
        # detector antenna
        pygame.draw.line(surf, C_GRAY, (x, y+5), (x, y+25), 2)
        pygame.draw.circle(surf, C_YELLOW, (x, y+26), 5)
        # ray beam
        if self.ray_active:
            ray_len = int((H - 60 - (y + 25)) * self.ray_progress)
            ray_y_end = y + 26 + ray_len
            beam = pygame.Surface((12, ray_len + 1), pygame.SRCALPHA)
            for i in range(ray_len):
                alpha = int(200 * (1 - i / max(ray_len, 1)))
                pygame.draw.line(beam, (0, 255, 200, alpha), (6, i), (6, i+1), 3)
            surf.blit(beam, (x - 6, y + 26))
            # pulse circle at tip
            pulsed_r = 8 + int(4 * math.sin(pygame.time.get_ticks() / 80))
            pygame.draw.circle(surf, (0, 255, 180), (x, ray_y_end), pulsed_r, 2)

    def get_rect(self):
        return pygame.Rect(self.x - 55, self.y + 5, 110, 15)


# ──────────────────────────────────────────────
#  WAVE  (animated ocean surface)
# ──────────────────────────────────────────────
class WaveSurface:
    def __init__(self):
        self.t = 0

    def update(self):
        self.t += 0.03

    def draw(self, surf):
        # deep ocean background
        for row in range(OCEAN_TOP, H, 40):
            alpha_ratio = (row - OCEAN_TOP) / (H - OCEAN_TOP)
            r = int(0   + alpha_ratio * 0)
            g = int(105 - alpha_ratio * 50)
            b = int(180 - alpha_ratio * 60)
            pygame.draw.rect(surf, (r, g, b), (0, row, W, 41))
        # sand at bottom
        pygame.draw.rect(surf, C_SAND, (0, H - 45, W, 45))
        # pebbles
        random.seed(42)
        for _ in range(25):
            px = random.randint(0, W)
            py = H - random.randint(5, 35)
            pr = random.randint(3, 10)
            pygame.draw.circle(surf, (180, 160, 100), (px, py), pr)
        random.seed()
        # animated surface waves
        pts = [(0, OCEAN_TOP)]
        for px in range(0, W + 5, 5):
            wave_y = OCEAN_TOP + int(6 * math.sin(px / 60 + self.t) +
                                      3 * math.sin(px / 30 + self.t * 1.5))
            pts.append((px, wave_y))
        pts.append((W, OCEAN_TOP - 10))
        pts.append((0, OCEAN_TOP - 10))
        pygame.draw.polygon(surf, C_OCEAN_SURF, pts)
        # highlight line
        for px in range(0, W - 5, 5):
            wy = OCEAN_TOP + int(6 * math.sin(px / 60 + self.t) +
                                  3 * math.sin(px / 30 + self.t * 1.5))
            pygame.draw.line(surf, C_WAVE, (px, wy), (px + 5, wy), 2)


# ──────────────────────────────────────────────
#  FLOATING TEXT (score popup / slogan)
# ──────────────────────────────────────────────
class FloatingText:
    def __init__(self, text, x, y, colour=C_GREEN, size=22, life=120):
        self.text  = text
        self.x, self.y = x, y
        self.colour= colour
        self.size  = size
        self.life  = life
        self.max_life = life

    def update(self):
        self.y -= 0.6
        self.life -= 1

    def draw(self, surf, font):
        alpha = int(255 * (self.life / self.max_life))
        rendered = font.render(self.text, True, self.colour)
        rendered.set_alpha(alpha)
        surf.blit(rendered, (int(self.x) - rendered.get_width()//2, int(self.y)))


# ──────────────────────────────────────────────
#  GAME CLASS
# ──────────────────────────────────────────────
class OceanGame:
    def __init__(self):
        pygame.init()
        self.screen  = pygame.display.set_mode((W, H))
        pygame.display.set_caption("🌊 Ocean Guardian — Sustainability Mission")
        self.clock   = pygame.time.Clock()
        # fonts
        self.font_lg  = pygame.font.SysFont("segoeui", 36, bold=True)
        self.font_md  = pygame.font.SysFont("segoeui", 22)
        self.font_sm  = pygame.font.SysFont("segoeui", 17)
        self.font_hud = pygame.font.SysFont("segoeui", 19, bold=True)
        self.state    = "playing"   # playing | win | gameover
        self._init_game()

    def _init_game(self):
        self.waste   = [WasteItem() for _ in range(WASTE_COUNT)]
        self.fish    = [Fish()      for _ in range(FISH_COUNT)]
        self.ship    = Ship()
        self.waves   = WaveSurface()
        self.bubbles : list[Bubble]       = []
        self.floats  : list[FloatingText] = []
        self.score   = 0
        self.mission_steps: list[str] = []
        self.slogan_display = ""
        self.slogan_timer   = 0
        self.state   = "playing"
        self.stars   = [(random.randint(0,W), random.randint(0, OCEAN_TOP-10),
                         random.randint(1,3)) for _ in range(60)]
        self.clouds  = [(random.randint(0,W), random.randint(20,80),
                         random.randint(60,140)) for _ in range(5)]

    # ── Main loop ──────────────────────────────
    def run(self):
        while True:
            dt = self.clock.tick(FPS)
            self._handle_events()
            if self.state == "playing":
                self._update()
            self._draw()
            pygame.display.flip()

    # ── Events ─────────────────────────────────
    def _handle_events(self):
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                save_score(self.score)
                pygame.quit(); sys.exit()
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    save_score(self.score)
                    pygame.quit(); sys.exit()
                if ev.key == pygame.K_SPACE and self.state == "playing":
                    self.ship.fire_ray()
                if ev.key == pygame.K_r and self.state in ("win", "gameover"):
                    self._init_game()

    # ── Update ─────────────────────────────────
    def _update(self):
        keys = pygame.key.get_pressed()
        self.ship.move(keys)

        prev_states = {id(w): w.collected for w in self.waste}
        self.ship.update(self.waste, self.bubbles)

        # detect newly collected waste
        for w in self.waste:
            if w.collected and not prev_states[id(w)]:
                # score popup
                self.score += SCORE_PER_WASTE
                self.floats.append(
                    FloatingText(f"+{SCORE_PER_WASTE} Waste Collected!", w.x, w.y - 20,
                                 colour=C_ORANGE, size=20))
                step = f"Detected & collected: {w.name}"
                self.mission_steps.append(step)

            if w.seagrass and w.grass_grow >= 0.99:
                if not getattr(w, "_scored_plant", False):
                    w._scored_plant = True
                    self.score += SCORE_PER_PLANT
                    self.floats.append(
                        FloatingText(f"+{SCORE_PER_PLANT} Seagrass Planted! 🌱",
                                     w.x, w.y - 40, colour=C_GREEN, size=20))
                    slogan = random.choice(SLOGANS)
                    self.floats.append(
                        FloatingText(slogan, W//2, OCEAN_TOP + 30,
                                     colour=C_YELLOW, size=18, life=160))
                    self.mission_steps.append(f"Seagrass grown at ({int(w.x)},{int(w.y)})")

        self.waves.update()
        for w in self.waste:
            w.update()
        for f in self.fish:
            f.update(self.waste)
        for b in self.bubbles:
            b.update()
        self.bubbles = [b for b in self.bubbles if b.life > 0]
        for ft in self.floats:
            ft.update()
        self.floats = [ft for ft in self.floats if ft.life > 0]

        # win condition
        if all(w.seagrass for w in self.waste):
            self.state = "win"

    # ── Draw ───────────────────────────────────
    def _draw(self):
        # sky
        self.screen.fill(C_SKY)
        self._draw_sky()
        # ocean
        self.waves.draw(self.screen)
        # underwater objects
        for w in self.waste:
            w.draw(self.screen)
        for b in self.bubbles:
            b.draw(self.screen)
        for f in self.fish:
            f.draw(self.screen)
        # ship
        self.ship.draw(self.screen)
        # floating texts
        for ft in self.floats:
            ft.draw(self.screen, self.font_sm)
        # HUD
        self._draw_hud()
        # overlays
        if self.state == "win":
            self._draw_win()
        elif self.state == "gameover":
            self._draw_gameover()

    def _draw_sky(self):
        # stars / dots
        for sx, sy, sr in self.stars:
            pygame.draw.circle(self.screen, (255,255,255), (sx, sy), sr)
        # sun
        pygame.draw.circle(self.screen, (255, 230, 80), (80, 60), 36)
        pygame.draw.circle(self.screen, (255, 255, 180), (80, 60), 28)
        # clouds
        for cx, cy, cw in self.clouds:
            t = pygame.time.get_ticks() / 8000
            cx2 = int((cx + t * 15) % (W + 150)) - 75
            for off in [(-cw//3, 8), (0, 0), (cw//3, 8)]:
                pygame.draw.ellipse(self.screen, C_WHITE,
                    (cx2 + off[0] - 30, cy + off[1], 60, 34))
        # horizon glow
        for i in range(20):
            alpha = 40 - i * 2
            s = pygame.Surface((W, 3), pygame.SRCALPHA)
            s.fill((255, 200, 100, alpha))
            self.screen.blit(s, (0, OCEAN_TOP - 20 + i))

    def _draw_hud(self):
        # left panel
        draw_alpha_rect(self.screen, (0, 20, 50, 200), (10, 10, 260, 155), radius=10)
        title = self.font_hud.render("🌊 OCEAN GUARDIAN", True, (100, 220, 255))
        self.screen.blit(title, (20, 18))

        collected = sum(1 for w in self.waste if w.collected)
        planted   = sum(1 for w in self.waste if w.seagrass and getattr(w,'_scored_plant',False))

        lines = [
            f"Score     : {self.score}",
            f"Waste Collected : {collected}/{WASTE_COUNT}",
            f"Seagrass Planted: {planted}/{WASTE_COUNT}",
            f"Ray Cooldown: {'Ready!' if self.ship.cooldown==0 else str(self.ship.cooldown//FPS+1)+'s'}",
        ]
        for i, line in enumerate(lines):
            colour = C_GREEN if "Ready" in line else C_WHITE
            surf = self.font_sm.render(line, True, colour)
            self.screen.blit(surf, (20, 46 + i * 26))

        # progress bar
        bar_w = 220
        bar_x, bar_y = 20, 138
        pygame.draw.rect(self.screen, (30, 60, 80), (bar_x, bar_y, bar_w, 14), border_radius=7)
        fill = int(bar_w * planted / WASTE_COUNT)
        if fill > 0:
            pygame.draw.rect(self.screen, C_GREEN, (bar_x, bar_y, fill, 14), border_radius=7)
        pygame.draw.rect(self.screen, C_WAVE, (bar_x, bar_y, bar_w, 14), 2, border_radius=7)

        # controls hint
        hint = self.font_sm.render("← → Move   SPACE Ray   R Restart   ESC Quit", True, (160,180,200))
        self.screen.blit(hint, (W - hint.get_width() - 12, H - 26))

        # mission log (right panel, last 5 steps)
        if self.mission_steps:
            draw_alpha_rect(self.screen, (0, 20, 50, 190), (W-305, 10, 295, 160), radius=10)
            log_title = self.font_hud.render("📋 Mission Log", True, (100,220,255))
            self.screen.blit(log_title, (W-298, 17))
            for i, step in enumerate(self.mission_steps[-5:]):
                step_short = step[:38] + ("…" if len(step)>38 else "")
                s = self.font_sm.render(f"• {step_short}", True, (200,255,200))
                self.screen.blit(s, (W-298, 44 + i * 22))

    def _draw_win(self):
        # dark overlay
        ov = pygame.Surface((W, H), pygame.SRCALPHA)
        ov.fill((0, 20, 50, 210))
        self.screen.blit(ov, (0, 0))
        t = self.font_lg.render(" GAME OVER - YOU WON! 🎉", True, C_GREEN)
        self.screen.blit(t, (W//2 - t.get_width()//2, 120))
        sub_t = self.font_md.render("The ocean has been restored!", True, C_WHITE)
        self.screen.blit(sub_t, (W//2 - sub_t.get_width()//2, 170))
        sc = self.font_md.render(f"Final Score: {self.score}", True, C_YELLOW)
        self.screen.blit(sc, (W//2 - sc.get_width()//2, 210))

        slogans_to_show = random.sample(SLOGANS, min(5, len(SLOGANS)))
        for i, sl in enumerate(slogans_to_show):
            s = self.font_sm.render(sl, True, (180, 255, 180))
            self.screen.blit(s, (W//2 - s.get_width()//2, 260 + i * 32))

        steps_title = self.font_md.render("✅ Mission Log:", True, (100,220,255))
        self.screen.blit(steps_title, (W//2 - steps_title.get_width()//2, 425))
        for i, step in enumerate(self.mission_steps[-6:]):
            s = self.font_sm.render(f"  ✔ {step}", True, C_WHITE)
            self.screen.blit(s, (W//2 - s.get_width()//2, 455 + i * 22))

        r = self.font_md.render("Press R to Play Again or ESC to Quit", True, C_WAVE)
        self.screen.blit(r, (W//2 - r.get_width()//2, H - 50))

    def _draw_gameover(self):
        ov = pygame.Surface((W, H), pygame.SRCALPHA)
        ov.fill((50, 0, 0, 210))
        self.screen.blit(ov, (0, 0))
        t = self.font_lg.render("Mission Failed!", True, C_RED)
        self.screen.blit(t, (W//2 - t.get_width()//2, H//2 - 60))
        r = self.font_md.render("Press R to Try Again", True, C_WHITE)
        self.screen.blit(r, (W//2 - r.get_width()//2, H//2 + 20))


# ──────────────────────────────────────────────
#  ENTRY POINT
# ──────────────────────────────────────────────
if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════╗
║   🌊  OCEAN GUARDIAN — Sustainability Game  🌊  ║
║                                              ║
║  CONTROLS                                    ║
║  ← →   Move ship left / right               ║
║  SPACE  Fire detector ray                   ║
║  R      Restart after win/game-over         ║
║  ESC    Quit                                 ║
║                                              ║
║  GOAL                                        ║
║  Shoot rays to detect & collect all waste.  ║
║  Seagrass auto-grows at each cleanup site.  ║
║  Restore full ocean biodiversity to WIN!    ║
╚══════════════════════════════════════════════╝
    """)
    game = OceanGame()
    game.run()