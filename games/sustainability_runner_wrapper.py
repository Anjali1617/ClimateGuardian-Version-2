"""
🌿 SUSTAINABILITY RUNNER 🌿
A Subway Surfer-style endless runner focused on biodiversity & sustainability.

This file is a wrapper to integrate the game into the ClimateGuardian Streamlit app.

Controls:
  - LEFT / A      : Move left lane
  - RIGHT / D     : Move right lane
  - UP / W / SPACE: Jump
  - DOWN / S      : Slide / Sweep
"""

import pygame
import random
import math
import sys

# ── Constants ─────────────────────────────────────────────────────────────────
SCREEN_W, SCREEN_H = 900, 600
FPS = 60
LANES = [220, 450, 680]          # x-centres for 3 lanes
LANE_COUNT = 3
GROUND_Y = 470                   # y where the player stands

# Colours
SKY_TOP    = (135, 206, 235)
SKY_BOT    = (200, 240, 200)
GROUND_COL = (86, 125, 70)
PATH_COL   = (180, 160, 120)
PATH_EDGE  = (140, 120, 90)
WHITE      = (255, 255, 255)
BLACK      = (0,   0,   0)
GREEN      = (60,  180,  75)
DARK_GREEN = (34,  139,  34)
YELLOW     = (255, 215,   0)
RED        = (220,  50,  50)
BROWN      = (139,  90,  43)
CYAN       = (0,   200, 200)
ORANGE     = (255, 140,   0)
GREY       = (150, 150, 150)
LIGHT_GREY = (200, 200, 200)
PURPLE     = (150,  50, 200)
PINK       = (255, 105, 180)
TEAL       = (0,   128, 128)

# Scoring
GOOD_SCORE  =  2     # per good item collected
BAD_PENALTY =  1     # score penalty for hitting bad item
LIVES_START =   3

# Physics
GRAVITY      =  0.8
JUMP_VEL     = -16
SLIDE_FRAMES =  40

# ── Utility helpers ────────────────────────────────────────────────────────────

def lerp_color(c1, c2, t):
    return tuple(int(c1[i] + (c2[i]-c1[i])*t) for i in range(3))


def draw_rounded_rect(surf, color, rect, radius=10):
    pygame.draw.rect(surf, color, rect, border_radius=radius)


def draw_text_center(surf, text, font, color, cx, cy):
    img = font.render(text, True, color)
    r = img.get_rect(center=(cx, cy))
    surf.blit(img, r)


# ── Sprite drawing helpers (no image files needed) ────────────────────────────

def draw_player(surf, x, y, state, frame):
    """Draw a cute pixel-art style runner."""
    # state: 'run' | 'jump' | 'slide'
    col_skin  = (255, 200, 150)
    col_shirt = (34, 139, 34)   # green eco-warrior
    col_pants = (60,  90, 160)
    col_shoe  = (80,  50,  20)
    col_hair  = (80,  40,  10)

    # Shadow
    shadow_y = GROUND_Y
    if state == 'jump':
        shadow_y = GROUND_Y + (y - GROUND_Y) * 0.2
    
    shadow_w = 30 - (GROUND_Y - y) * 0.2 if state == 'jump' else 30
    shadow_h = 8
    
    shadow_surf = pygame.Surface((shadow_w * 2, shadow_h * 2), pygame.SRCALPHA)
    pygame.draw.ellipse(shadow_surf, (0, 0, 0, 80), (0, 0, shadow_w, shadow_h))
    surf.blit(shadow_surf, (x - shadow_w/2, shadow_y + 10 ))


    bob = int(math.sin(frame * 0.3) * 3) if state == 'run' else 0

    if state == 'slide':
        # Sliding: crouched low
        bx, by = x - 20, y + 10
        # body
        pygame.draw.ellipse(surf, col_shirt, (bx, by, 40, 22))
        # head
        pygame.draw.circle(surf, col_skin, (bx+30, by-4), 13)
        pygame.draw.ellipse(surf, col_hair, (bx+20, by-14, 22, 10))
        # legs stretched back
        pygame.draw.rect(surf, col_pants, (bx-16, by+8, 30, 12), border_radius=4)
        pygame.draw.rect(surf, col_shoe, (bx-20, by+14, 14, 8), border_radius=3)
    elif state == 'jump':
        bx, by = x - 14, y - 10 + bob
        # legs tucked
        pygame.draw.rect(surf, col_pants, (bx,   by+28, 12, 18), border_radius=4)
        pygame.draw.rect(surf, col_pants, (bx+16, by+28, 12, 18), border_radius=4)
        pygame.draw.rect(surf, col_shoe, (bx-2, by+44, 14, 8), border_radius=3)
        pygame.draw.rect(surf, col_shoe, (bx+14, by+44, 14, 8), border_radius=3)
        # body
        pygame.draw.rect(surf, col_shirt, (bx, by+12, 28, 22), border_radius=6)
        # arms up
        pygame.draw.line(surf, col_skin, (bx, by+18), (bx-10, by+6), 5)
        pygame.draw.line(surf, col_skin, (bx+28, by+18), (bx+38, by+6), 5)
        # head
        pygame.draw.circle(surf, col_skin, (bx+14, by+8), 13)
        pygame.draw.ellipse(surf, col_hair, (bx+3, by-4, 24, 12))
    else:
        # Running
        leg_swing = int(math.sin(frame * 0.3) * 12)
        bx, by = x - 14, y - 50 + bob
        # legs alternate
        pygame.draw.rect(surf, col_pants, (bx+4,  by+38, 10, 20+leg_swing), border_radius=4)
        pygame.draw.rect(surf, col_pants, (bx+14, by+38, 10, 20-leg_swing), border_radius=4)
        pygame.draw.rect(surf, col_shoe, (bx+2,  by+56+leg_swing, 14, 8), border_radius=3)
        pygame.draw.rect(surf, col_shoe, (bx+12, by+56-leg_swing, 14, 8), border_radius=3)
        # body
        pygame.draw.rect(surf, col_shirt, (bx, by+16, 28, 24), border_radius=6)
        # arms swing
        pygame.draw.line(surf, col_skin, (bx,    by+22), (bx-10, by+36-leg_swing//2), 5)
        pygame.draw.line(surf, col_skin, (bx+28, by+22), (bx+38, by+36+leg_swing//2), 5)
        # head
        pygame.draw.circle(surf, col_skin, (bx+14, by+10), 14)
        pygame.draw.ellipse(surf, col_hair, (bx+2, by-2, 26, 14))
        # eye
        pygame.draw.circle(surf, BLACK, (bx+20, by+10), 3)
        pygame.draw.circle(surf, WHITE, (bx+21, by+9), 1)
        # smile
        pygame.draw.arc(surf, (180, 100, 60),
                        pygame.Rect(bx+12, by+12, 10, 6), math.pi, 2*math.pi, 2)
        # eco leaf badge
        pygame.draw.polygon(surf, DARK_GREEN,
                            [(bx+5, by+22), (bx+12, by+18), (bx+12, by+28)])


def draw_tree(surf, x, y):
    """A lush green tree."""
    # trunk
    pygame.draw.rect(surf, BROWN, (x-8, y-30, 16, 34), border_radius=3)
    # foliage layers
    pygame.draw.polygon(surf, DARK_GREEN,
                        [(x, y-90), (x-34, y-30), (x+34, y-30)])
    pygame.draw.polygon(surf, GREEN,
                        [(x, y-80), (x-30, y-25), (x+30, y-25)])
    pygame.draw.polygon(surf, (100, 200, 80),
                        [(x, y-105), (x-22, y-60), (x+22, y-60)])


def draw_flower(surf, x, y):
    """A colourful flower."""
    for i in range(6):
        angle = i * math.pi / 3
        px = x + int(math.cos(angle) * 12)
        py = y + int(math.sin(angle) * 12)
        pygame.draw.circle(surf, PINK, (px, py), 8)
    pygame.draw.circle(surf, YELLOW, (x, y), 8)
    pygame.draw.rect(surf, GREEN, (x-3, y+8, 6, 18), border_radius=2)


def draw_fruit_basket(surf, x, y):
    """A basket of fruits (apples + oranges)."""
    pygame.draw.ellipse(surf, BROWN, (x-20, y-10, 40, 22))
    pygame.draw.arc(surf, BROWN, (x-20, y-18, 40, 22), 0, math.pi, 3)
    # fruits
    pygame.draw.circle(surf, RED,    (x-8,  y-18), 10)
    pygame.draw.circle(surf, ORANGE, (x+8,  y-18), 10)
    pygame.draw.circle(surf, GREEN,  (x,    y-28), 9)


def draw_solar_panel(surf, x, y):
    """A shiny solar panel."""
    pygame.draw.rect(surf, (30, 80, 160), (x-22, y-40, 44, 30), border_radius=4)
    pygame.draw.rect(surf, CYAN,          (x-22, y-40, 44, 30), 2, border_radius=4)
    # grid lines
    for i in range(1, 3):
        pygame.draw.line(surf, CYAN, (x-22+i*14, y-40), (x-22+i*14, y-10), 1)
    pygame.draw.line(surf, CYAN, (x-22, y-25), (x+22, y-25), 1)
    # pole
    pygame.draw.rect(surf, GREY, (x-3, y-10, 6, 14))


def draw_water_droplet(surf, x, y):
    """A clean water droplet."""
    pygame.draw.polygon(surf, CYAN,
                        [(x, y-30), (x-14, y-5), (x+14, y-5)])
    pygame.draw.circle(surf, CYAN, (x, y-5), 14)
    # shine
    pygame.draw.circle(surf, WHITE, (x-5, y-12), 4)


def draw_plastic_bottle(surf, x, y):
    """A dirty plastic bottle obstacle."""
    pygame.draw.rect(surf, (200, 230, 255), (x-8, y-40, 16, 36), border_radius=5)
    pygame.draw.rect(surf, (180, 200, 220), (x-5, y-48, 10, 12), border_radius=3)
    # label
    pygame.draw.rect(surf, RED, (x-7, y-30, 14, 12))
    pygame.draw.line(surf, (200, 230, 255), (x-3, y-38), (x-3, y-4), 1)


def draw_dustbin(surf, x, y):
    """An overflowing dustbin."""
    # bin body
    pygame.draw.rect(surf, GREY, (x-18, y-38, 36, 40), border_radius=4)
    # lid slightly open
    pygame.draw.rect(surf, LIGHT_GREY, (x-20, y-44, 40, 10), border_radius=3)
    pygame.draw.rect(surf, DARK_GREEN, (x-4, y-52, 8, 12), border_radius=2)
    # garbage poking out
    pygame.draw.circle(surf, (180, 100, 50), (x-5, y-42), 6)
    pygame.draw.circle(surf, (100, 180, 50), (x+7, y-40), 5)


def draw_smoke_cloud(surf, x, y):
    """A dark smoke/pollution cloud."""
    for ox, oy, r in [(-14,-6,14),(0,-14,16),(14,-6,14),(0,0,12)]:
        pygame.draw.circle(surf, (100, 100, 100), (x+ox, y+oy), r)
    for ox, oy, r in [(-10,-4,10),(2,-10,12),(12,-4,10)]:
        pygame.draw.circle(surf, (130, 130, 130), (x+ox, y+oy), r)


def draw_oil_spill(surf, x, y):
    """A rainbow oil spill on the ground (low obstacle)."""
    for i, c in enumerate([(255,0,0),(255,165,0),(255,255,0),
                            (0,200,0),(0,0,255),(148,0,211)]):
        pygame.draw.ellipse(surf, c,
                            (x-30+i*4, y-6+i*2, 50-i*4, 14-i), 0)


# ── Item class ────────────────────────────────────────────────────────────────

class Item:
    GOOD_TYPES = ['tree', 'flower', 'basket', 'solar', 'water']
    BAD_TYPES  = ['bottle', 'dustbin', 'smoke', 'oil']

    def __init__(self, speed):
        self.lane   = random.randint(0, LANE_COUNT-1)
        self.x      = LANES[self.lane]
        self.kind   = random.choice(self.GOOD_TYPES + self.BAD_TYPES)
        self.is_good = self.kind in self.GOOD_TYPES
        self.speed  = speed
        self._set_y()
        self.collected = False
        self.flash = 0          # flash frames after collection

    def _set_y(self):
        # oil spill is ground-level; smoke floats high; rest at ground
        if self.kind == 'oil':
            self.y = GROUND_Y + 10
            self.hitbox_h = 14
        elif self.kind == 'smoke':
            self.y = GROUND_Y - 60
            self.hitbox_h = 40
        else:
            self.y = GROUND_Y
            self.hitbox_h = 50

    def update(self):
        self.x -= self.speed
        if self.flash > 0:
            self.flash -= 1

    def draw(self, surf):
        if self.collected:
            return
        x, y = int(self.x), int(self.y)
        if   self.kind == 'tree':    draw_tree(surf, x, y)
        elif self.kind == 'flower':  draw_flower(surf, x, y)
        elif self.kind == 'basket':  draw_fruit_basket(surf, x, y)
        elif self.kind == 'solar':   draw_solar_panel(surf, x, y)
        elif self.kind == 'water':   draw_water_droplet(surf, x, y)
        elif self.kind == 'bottle':  draw_plastic_bottle(surf, x, y)
        elif self.kind == 'dustbin': draw_dustbin(surf, x, y)
        elif self.kind == 'smoke':   draw_smoke_cloud(surf, x, y)
        elif self.kind == 'oil':     draw_oil_spill(surf, x, y)

    def get_rect(self):
        return pygame.Rect(self.x - 22, self.y - 55, 44, 55)

    def off_screen(self):
        return self.x < -60


# ── Particle system ───────────────────────────────────────────────────────────

class Particle:
    def __init__(self, x, y, color):
        self.x, self.y = x, y
        self.color = color
        angle = random.uniform(0, 2*math.pi)
        speed = random.uniform(2, 7)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed - 3
        self.life = random.randint(20, 40)
        self.max_life = self.life
        self.r = random.randint(4, 10)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.2
        self.life -= 1

    def draw(self, surf):
        alpha = self.life / self.max_life
        r = int(self.r * alpha)
        if r > 0:
            pygame.draw.circle(surf, self.color, (int(self.x), int(self.y)), r)


# ── Background scenery ────────────────────────────────────────────────────────

class Cloud:
    def __init__(self, x=None):
        self.x = x if x else random.randint(0, SCREEN_W)
        self.y = random.randint(30, 140)
        self.speed = random.uniform(0.4, 1.0)
        self.w = random.randint(80, 160)

    def update(self):
        self.x -= self.speed
        if self.x < -200:
            self.x = SCREEN_W + 50
            self.y = random.randint(30, 140)

    def draw(self, surf):
        for ox, oy, r in [(0,0,self.w//4),(self.w//4,-10,self.w//5),
                          (self.w//2,0,self.w//4),(self.w//4,5,self.w//5)]:
            pygame.draw.circle(surf, WHITE, (int(self.x)+ox, self.y+oy), r)


class BGTree:
    def __init__(self, x=None, side='left'):
        self.side = side
        self.x = x if x else (random.randint(-200, 0) if side=='left'
                               else random.randint(SCREEN_W, SCREEN_W+200))
        self.y = GROUND_Y - random.randint(0, 20)
        self.scale = random.uniform(0.5, 0.9)
        self.speed = 3.5

    def update(self):
        self.x -= self.speed
        if self.x < -120:
            self.x = SCREEN_W + 80

    def draw(self, surf):
        x, y = int(self.x), int(self.y)
        s = self.scale
        h = int(30 * s)
        pygame.draw.rect(surf, BROWN, (x-int(7*s), y-h, int(14*s), h), border_radius=2)
        pygame.draw.polygon(surf, DARK_GREEN,
                            [(x, y-h-int(55*s)),
                             (x-int(28*s), y-h),
                             (x+int(28*s), y-h)])
        pygame.draw.polygon(surf, GREEN,
                            [(x, y-h-int(45*s)),
                             (x-int(22*s), y-h+int(10*s)),
                             (x+int(22*s), y-h+int(10*s))])


# ── HUD elements ──────────────────────────────────────────────────────────────

def draw_hud(surf, score, lives, collected, distance, missed_good, font_big, font_med, font_sm):
    # Top bar background
    pygame.draw.rect(surf, (0, 60, 0, 180), (0, 0, SCREEN_W, 60))
    pygame.draw.line(surf, GREEN, (0, 60), (SCREEN_W, 60), 2)

    # Score
    score_txt = font_big.render(f"🌿 {score}", True, YELLOW)
    surf.blit(score_txt, (20, 10))

    # Lives (leaf icons)
    for i in range(LIVES_START):
        col = DARK_GREEN if i < lives else (80, 80, 80)
        pygame.draw.polygon(surf, col,
                            [(SCREEN_W-40-i*36, 20),
                             (SCREEN_W-55-i*36, 40),
                             (SCREEN_W-25-i*36, 40)])
        if i < lives:
            pygame.draw.line(surf, (100, 255, 100),
                             (SCREEN_W-40-i*36, 20),
                             (SCREEN_W-40-i*36, 40), 2)

    # Distance
    dist_txt = font_med.render(f"{int(distance)}m", True, CYAN)
    surf.blit(dist_txt, (SCREEN_W//2 - dist_txt.get_width()//2, 14))

    # Eco counter
    eco_txt = font_sm.render(f"Eco items: {collected}", True, (180, 255, 180))
    surf.blit(eco_txt, (20, 42))

    # Missed items counter
    missed_txt = font_sm.render(f"Missed: {missed_good}/5", True, (255, 180, 180))
    surf.blit(missed_txt, (180, 42))


# ── Main Game class ───────────────────────────────────────────────────────────

class SustainabilityRunner:

    def __init__(self):
        pygame.init()
        pygame.display.set_caption("🌿 Sustainability Runner — Eco Edition")
        self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        self.clock  = pygame.time.Clock()

        # Fonts
        self.font_title  = pygame.font.SysFont("comicsansms", 52, bold=True)
        self.font_big    = pygame.font.SysFont("comicsansms", 30, bold=True)
        self.font_med    = pygame.font.SysFont("comicsansms", 24)
        self.font_small  = pygame.font.SysFont("comicsansms", 18)
        self.font_tiny   = pygame.font.SysFont("comicsansms", 14)

        self._reset()
        self.state = 'menu'   # 'menu' | 'play' | 'gameover'
        self.high_score = 0
        self.lane_change_effect = 0
        self.running = True

    def _reset(self):
        self.score      = 0
        self.lives      = LIVES_START
        self.distance   = 0
        self.collected  = 0
        self.missed_good_items = 0
        self.game_over_reason = ""
        self.frame      = 0
        self.speed      = 6.0
        self.invincible = 0     # invincibility frames after hit

        # Player
        self.lane       = 1
        self.target_lane = 1
        self.px         = LANES[1]
        self.py         = GROUND_Y
        self.vy         = 0
        self.on_ground  = True
        self.player_state = 'run'
        self.slide_timer  = 0
        self.lane_change_effect = 0

        # Items & effects
        self.items      = []
        self.particles  = []
        self.popup_texts = []   # [(text, x, y, life, color)]
        self.spawn_timer = 0

        # Scenery
        self.clouds  = [Cloud(random.randint(0, SCREEN_W)) for _ in range(6)]
        self.bg_trees_l = [BGTree(random.randint(0, 130), 'left')  for _ in range(4)]
        self.bg_trees_r = [BGTree(random.randint(SCREEN_W-130, SCREEN_W), 'right') for _ in range(4)]

        # Ground scroll
        self.ground_x = 0

    # ── Input ──────────────────────────────────────────────────────────────────

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                if self.state == 'menu':
                    self.state = 'play'
                elif self.state == 'gameover':
                    if event.key == pygame.K_r:
                        self._reset()
                        self.state = 'play'
                    elif event.key == pygame.K_m:
                        self._reset()
                        self.state = 'menu'
                    elif event.key == pygame.K_q:
                        self.running = False
                elif self.state == 'play':
                    if event.key in (pygame.K_LEFT, pygame.K_a):
                        if self.lane > 0:
                            self.lane -= 1
                            self.lane_change_effect = 15  # Trigger effect
                    elif event.key in (pygame.K_RIGHT, pygame.K_d):
                        if self.lane < LANE_COUNT - 1:
                            self.lane += 1
                            self.lane_change_effect = -15 # Trigger effect
                    elif event.key in (pygame.K_UP, pygame.K_w, pygame.K_SPACE):
                        if self.on_ground:
                            self.vy = JUMP_VEL
                            self.on_ground = False
                            self.player_state = 'jump'
                    elif event.key in (pygame.K_DOWN, pygame.K_s):
                        if self.on_ground and self.player_state != 'slide':
                            self.player_state = 'slide'
                            self.slide_timer  = SLIDE_FRAMES

    # ── Update ─────────────────────────────────────────────────────────────────

    def update(self):
        if self.state != 'play':
            return

        self.frame  += 1
        self.distance += self.speed / 60
        self.speed   = 6.0 + self.distance * 0.012   # ramp up
        self.speed   = min(self.speed, 18)

        # Update lane change effect
        if self.lane_change_effect > 0:
            self.lane_change_effect -= 1
        elif self.lane_change_effect < 0:
            self.lane_change_effect += 1

        # Smooth lane change
        tx = LANES[self.lane]
        self.px += (tx - self.px) * 0.22

        # Gravity / jump
        if not self.on_ground:
            self.vy += GRAVITY
            self.py += self.vy
            if self.py >= GROUND_Y:
                self.py = GROUND_Y
                self.vy = 0
                self.on_ground = True
                self.player_state = 'run'

        # Slide timer
        if self.slide_timer > 0:
            self.slide_timer -= 1
            self.player_state = 'slide'
        elif self.on_ground and self.player_state == 'slide' and self.slide_timer == 0:
            self.player_state = 'run'

        # Invincibility cooldown
        if self.invincible > 0:
            self.invincible -= 1

        # Ground scroll
        self.ground_x = (self.ground_x - self.speed) % 80

        # Clouds & BG trees
        for c in self.clouds:   c.update()
        for t in self.bg_trees_l + self.bg_trees_r: t.update()

        # Spawn items
        self.spawn_timer -= 1
        if self.spawn_timer <= 0:
            self.items.append(Item(self.speed))
            # ensure variety: 60% good, 40% bad
            if random.random() < 0.4:
                self.items[-1].kind    = random.choice(Item.BAD_TYPES)
                self.items[-1].is_good = False
            else:
                self.items[-1].kind    = random.choice(Item.GOOD_TYPES)
                self.items[-1].is_good = True
            self.items[-1]._set_y()
            interval = max(35, int(90 - self.distance * 0.3))
            self.spawn_timer = random.randint(interval//2, interval)

        # Update items
        for item in self.items:
            item.speed = self.speed
            item.update()

        # Collision
        self._check_collisions()

        if self.state == 'gameover':
            return

        # Check for missed good items before removing
        for item in self.items:
            if item.off_screen() and not item.collected and item.is_good:
                self.missed_good_items += 1

        # Remove off-screen or collected items
        self.items = [i for i in self.items if not i.off_screen() and not i.collected]

        # Particles
        for p in self.particles: p.update()
        self.particles = [p for p in self.particles if p.life > 0]

        # Popup texts
        self.popup_texts = [(t, x, y-1, l-1, c)
                            for (t,x,y,l,c) in self.popup_texts if l > 0]

        # New game over condition
        if self.missed_good_items >= 5:
            self.high_score = max(self.high_score, self.score)
            self.state = 'gameover'
            self.game_over_reason = "You missed 5 sustainable items!"

    def _check_collisions(self):
        # Player hitbox depends on state
        if self.player_state == 'slide':
            pr = pygame.Rect(self.px - 28, self.py - 14, 56, 24)
        elif self.player_state == 'jump':
            pr = pygame.Rect(self.px - 18, self.py - 60, 36, 60)
        else:
            pr = pygame.Rect(self.px - 14, self.py - 60, 28, 60)

        for item in self.items:
            if item.collected:
                continue
            ir = item.get_rect()
            if pr.colliderect(ir):
                item.collected = True
                if item.is_good:
                    self.score += GOOD_SCORE
                    self.collected += 1
                    # Burst green/yellow particles
                    for _ in range(18):
                        self.particles.append(
                            Particle(item.x, item.y - 30,
                                     random.choice([GREEN, YELLOW, CYAN, (180,255,120)])))
                    self.popup_texts.append(
                        (f"+{GOOD_SCORE}  🌿", item.x, item.y-60, 55, YELLOW))
                else:
                    if self.invincible == 0:
                        self.lives -= 1
                        self.invincible = 90
                        # Burst red/grey particles
                        for _ in range(18):
                            self.particles.append(
                                Particle(item.x, item.y - 20,
                                         random.choice([RED, GREY, ORANGE, (180,80,80)])))
                        self.popup_texts.append(
                            (f"-{BAD_PENALTY} ☠", item.x, item.y-60, 55, RED))
                        self.score = max(0, self.score - BAD_PENALTY)
                        if self.lives <= 0:
                            self.high_score = max(self.high_score, self.score)
                            self.state = 'gameover'
                            self.game_over_reason = "You hit too many obstacles!"

    # ── Draw ───────────────────────────────────────────────────────────────────

    def draw_background(self):
        # Sky gradient
        for y in range(SCREEN_H):
            t = y / SCREEN_H
            c = lerp_color(SKY_TOP, SKY_BOT, t)
            pygame.draw.line(self.screen, c, (0, y), (SCREEN_W, y))

        # Clouds
        for c in self.clouds: c.draw(self.screen)

        # Far background trees
        for t in self.bg_trees_l + self.bg_trees_r: t.draw(self.screen)

        # Ground strip
        pygame.draw.rect(self.screen, GROUND_COL, (0, GROUND_Y+4, SCREEN_W, SCREEN_H))

        # 3-lane path
        path_x1 = LANES[0] - 100
        path_x2 = LANES[-1] + 100
        pygame.draw.rect(self.screen, PATH_COL,
                         (path_x1, GROUND_Y - 10, path_x2 - path_x1, SCREEN_H))
        
        # Path edges
        pygame.draw.line(self.screen, PATH_EDGE, (path_x1, GROUND_Y-10), (path_x1, SCREEN_H), 5)
        pygame.draw.line(self.screen, PATH_EDGE, (path_x2, GROUND_Y-10), (path_x2, SCREEN_H), 5)

    def draw_lane_boundaries(self):
        # Lane dividers (dashed)
        lane_width = LANES[1] - LANES[0]
        for i in range(1, LANE_COUNT):
            lx = LANES[i-1] + lane_width / 2
            for dash_y in range(GROUND_Y, SCREEN_H, 40):
                y1 = dash_y + int(self.ground_x*2.5) % 40
                y2 = y1 + 25
                if y1 > SCREEN_H: y1 -=40
                if y2 > SCREEN_H: y2 = SCREEN_H

                pygame.draw.line(self.screen, (255, 255, 255, 100),
                                     (lx, y1), (lx, y2), 3)
    def draw_play(self):
        self.draw_background()
        self.draw_lane_boundaries()

        # Lane change effect
        if self.lane_change_effect != 0:
            alpha = abs(self.lane_change_effect) * 12
            color = (255, 255, 255, alpha)
            s = pygame.Surface((80, 15), pygame.SRCALPHA)
            s.fill(color)
            for i in range(5):
                pos_x = self.px - self.lane_change_effect * i * 0.2
                self.screen.blit(s, (pos_x - 40, GROUND_Y - 10 + i*3))


        # Items
        for item in self.items:
            item.draw(self.screen)

        # Particles
        for p in self.particles:
            p.draw(self.screen)

        # Player (flash when invincible)
        if self.invincible == 0 or (self.invincible // 6) % 2 == 0:
            draw_player(self.screen, int(self.px), int(self.py),
                        self.player_state, self.frame)

        # Popup texts
        for (text, x, y, life, color) in self.popup_texts:
            alpha = min(255, life * 8)
            s = self.font_med.render(text, True, color)
            self.screen.blit(s, (int(x) - s.get_width()//2, int(y)))

        # HUD
        draw_hud(self.screen, self.score, self.lives, self.collected,
                 self.distance, self.missed_good_items, self.font_big, self.font_med, self.font_small)

        # Speed indicator
        spd = self.font_tiny.render(f"Speed: {self.speed:.1f}", True, LIGHT_GREY)
        self.screen.blit(spd, (SCREEN_W - spd.get_width() - 12, 44))

    def draw_menu(self):
        self.draw_background()
        # Title card
        card_rect = pygame.Rect(SCREEN_W//2 - 280, 80, 560, 400)
        pygame.draw.rect(self.screen, (0, 40, 0), card_rect, border_radius=20)
        pygame.draw.rect(self.screen, GREEN, card_rect, 3, border_radius=20)

        # Title
        t1 = self.font_title.render("🌿 Sustainability", True, (100, 255, 100))
        t2 = self.font_title.render("Runner  🌍", True, YELLOW)
        self.screen.blit(t1, t1.get_rect(center=(SCREEN_W//2, 150)))
        self.screen.blit(t2, t2.get_rect(center=(SCREEN_W//2, 210)))

        # Instructions
        lines = [
            ("← → / A D", "Change Lane"),
            ("↑ / W / SPACE", "Jump"),
            ("↓ / S", "Slide under obstacles"),
            ("", ""),
            ("🌳 Collect trees, flowers, solar", "panels & clean water = +10"),
            ("♻️  Avoid plastic, dustbins,", "smoke & oil spills"),
        ]
        y = 270
        for k, v in lines:
            if k == "":
                y += 8; continue
            kt = self.font_small.render(k, True, CYAN)
            vt = self.font_small.render(v, True, WHITE)
            self.screen.blit(kt, (SCREEN_W//2 - 230, y))
            self.screen.blit(vt, (SCREEN_W//2 + 10, y))
            y += 24

        # Start prompt (blink)
        if (self.frame // 25) % 2 == 0:
            st = self.font_big.render("Press ANY KEY to start!", True, YELLOW)
            self.screen.blit(st, st.get_rect(center=(SCREEN_W//2, 470)))

        self.frame += 1

    def draw_gameover(self):
        self.draw_background()
        overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 140))
        self.screen.blit(overlay, (0, 0))

        card_rect = pygame.Rect(SCREEN_W//2 - 240, 100, 480, 380)
        pygame.draw.rect(self.screen, (30, 0, 0), card_rect, border_radius=18)
        pygame.draw.rect(self.screen, RED, card_rect, 3, border_radius=18)

        draw_text_center(self.screen, "GAME OVER 🌫️", self.font_title, RED, SCREEN_W//2, 140)

        if hasattr(self, 'game_over_reason') and self.game_over_reason:
            draw_text_center(self.screen, self.game_over_reason, self.font_med, (255, 200, 200), SCREEN_W//2, 180)

        draw_text_center(self.screen, f"Score: {self.score}", self.font_big, YELLOW, SCREEN_W//2, 220)
        draw_text_center(self.screen, f"High Score: {self.high_score}", self.font_med, CYAN, SCREEN_W//2, 260)
        draw_text_center(self.screen, f"Distance: {int(self.distance)} m", self.font_med, WHITE, SCREEN_W//2, 290)

        draw_text_center(self.screen, f"Eco Items Collected: {self.collected}",
                         self.font_med, GREEN, SCREEN_W//2, 320)

        draw_text_center(self.screen, f"Eco Items Missed: {self.missed_good_items}",
                         self.font_med, (255, 150, 150), SCREEN_W//2, 350)

        eco_rating = ("🌍 Earth Champion!" if self.collected >= 20 else
                      "🌿 Eco Warrior"    if self.collected >= 10 else
                      "🌱 Budding Green Hero")
        draw_text_center(self.screen, eco_rating, self.font_med, (150, 255, 150), SCREEN_W//2, 390)

        draw_text_center(self.screen, "[R] Restart   [M] Menu   [Q] Quit", self.font_small, LIGHT_GREY, SCREEN_W//2, 450)

    # ── Run ────────────────────────────────────────────────────────────────────

    def run(self):
        while self.running:
            self.handle_input()
            self.update()

            if self.state == 'menu':
                self.draw_menu()
            elif self.state == 'play':
                self.draw_play()
            elif self.state == 'gameover':
                self.draw_gameover()
                pygame.display.flip()
                pygame.time.wait(4000)
                self.running = False

            if self.running:
                pygame.display.flip()
            self.clock.tick(FPS)
        
        return self.score

def run_game():
    """Initializes and runs the game, returning the final score."""
    game = SustainabilityRunner()
    final_score = game.run()
    pygame.quit()
    return final_score

if __name__ == "__main__":
    score = run_game()
    print(f"Game finished with score: {score}")