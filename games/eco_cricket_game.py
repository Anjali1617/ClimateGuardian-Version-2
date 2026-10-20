"""
╔══════════════════════════════════════════════════════════╗
║        🌿  ECO CRICKET – Sustainability Game  🌿         ║
║  Hit the ball → Grow Nature → Save the Planet!          ║
╚══════════════════════════════════════════════════════════╝

INSTALL & RUN:
    pip install pygame
    python eco_cricket_game.py

CONTROLS:
    SPACE / LEFT CLICK  → Swing bat (when ball is near)
    R                   → Restart
    ESC                 → Quit
"""

import pygame
import random
import math
import sys
import json
import os

def save_score(score):
    """Save the final score to a JSON file to integrate with Streamlit."""
    score_file = os.path.join(os.path.dirname(__file__), 'eco_cricket_score.json')
    try:
        with open(score_file, 'w') as f:
            json.dump({'score': score}, f)
    except Exception:
        pass

# ─────────────────────────────────────────────
#  INIT
# ─────────────────────────────────────────────
pygame.init()
pygame.font.init()

W, H = 1100, 650
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("🌿 ECO CRICKET – Sustainability Game")
clock = pygame.time.Clock()
FPS = 60

# ─────────────────────────────────────────────
#  FONTS
# ─────────────────────────────────────────────
font_big   = pygame.font.SysFont("segoeuiemoji", 42, bold=True)
font_med   = pygame.font.SysFont("segoeuiemoji", 28)
font_sm    = pygame.font.SysFont("segoeuiemoji", 20)
font_slogan= pygame.font.SysFont("segoeuiemoji", 17, italic=True)

# ─────────────────────────────────────────────
#  COLOURS
# ─────────────────────────────────────────────
SKY_TOP    = (135, 206, 250)
SKY_BOT    = (200, 230, 180)
GROUND     = (80,  160,  60)
PITCH      = (210, 180, 100)
BROWN      = (120,  80,  40)
WHITE      = (255, 255, 255)
BLACK      = (10,   10,  10)
YELLOW     = (255, 220,  50)
RED        = (220,  60,  60)
GREEN_D    = ( 34, 139,  34)
BLUE_POND  = ( 64, 164, 223)
ORANGE     = (255, 140,   0)
PINK       = (255, 105, 180)
GREY       = (180, 180, 180)
TEAL       = ( 32, 178, 170)

# ─────────────────────────────────────────────
#  BIO-DIVERSITY OBJECTS
#  Each entry: (emoji_label, slogan, color, is_waste)
# ─────────────────────────────────────────────
BIO_OBJECTS = [
    # Good objects – nature grows!
    ("🌳 Tree",        "Trees are the lungs of our Earth – plant more!",           GREEN_D, False),
    ("🌸 Flower Bed",  "Flowers feed bees – biodiversity in every bloom!",          PINK,    False),
    ("💧 Pond",        "Water is life – every drop counts for ecosystems!",          BLUE_POND, False),
    ("🌱 Sapling",     "A sapling today is a forest tomorrow!",                     (100,200,80), False),
    ("🍀 Meadow",      "Meadows support 3× more insects than lawns – go wild!",     (120,200,60), False),
    ("🦋 Butterfly Garden","Butterflies are nature's pollinators – protect them!",  (220,160,220), False),
    ("🐝 Beehive",     "Bees pollinate 70% of our food – save the bees!",           YELLOW,  False),
    ("🌾 Wheat Field", "Sustainable farming feeds the world without harming it!",   (210,170,80), False),
    ("🍄 Mushroom Patch","Fungi recycle nutrients – the forest's hidden internet!", (190,130,90), False),
    ("🌊 Wetland",     "Wetlands filter water & shelter thousands of species!",     TEAL,    False),
    ("🌵 Cactus",      "Cacti survive with minimal water – nature's efficiency!",   (100,170,80), False),
    ("🦚 Bird Sanctuary","Protect bird habitats – they keep our skies alive!",      (80,200,180), False),
    # Waste objects – destroyed with particle burst
    ("🗑️ Trash",       "Reduce, Reuse, Recycle – keep waste out of nature!",        GREY,    True),
    ("🧪 Toxic Waste", "Say NO to chemical dumping – protect our soil!",            (160,220,40), True),
    ("🛢️ Oil Drum",    "Oil spills devastate ecosystems – switch to clean energy!", (60,60,60),   True),
    ("🚬 Cigarette",   "Cigarette butts are the #1 beach pollutant – bin them!",    (200,200,180),True),
    ("🔋 Dead Battery","Batteries contain heavy metals – recycle them properly!",   (140,140,220),True),
    ("🛍️ Plastic Bag", "Plastic bags kill marine life – use cloth bags!",           (220,220,240),True),
]

# ─────────────────────────────────────────────
#  HELPER – gradient sky
# ─────────────────────────────────────────────
def draw_sky(surface):
    for y in range(H):
        t  = y / H
        r  = int(SKY_TOP[0] + (SKY_BOT[0]-SKY_TOP[0])*t)
        g  = int(SKY_TOP[1] + (SKY_BOT[1]-SKY_TOP[1])*t)
        b  = int(SKY_TOP[2] + (SKY_BOT[2]-SKY_TOP[2])*t)
        pygame.draw.line(surface, (r,g,b), (0,y),(W,y))

# ─────────────────────────────────────────────
#  CLOUD
# ─────────────────────────────────────────────
class Cloud:
    def __init__(self):
        self.x  = random.randint(-120, W)
        self.y  = random.randint(20, 120)
        self.sp = random.uniform(0.2, 0.5)
        self.r  = random.randint(30, 55)
    def update(self):
        self.x += self.sp
        if self.x > W + 120:
            self.x = -120
            self.y = random.randint(20, 120)
    def draw(self, surface):
        for dx, dy, r in [(-self.r//2, 10, self.r//2),
                           (0, 0, self.r),
                           (self.r//2, 8, self.r*2//3)]:
            pygame.draw.circle(surface, WHITE, (int(self.x+dx), int(self.y+dy)), r)

# ─────────────────────────────────────────────
#  PARTICLE (for hits / waste destruction)
# ─────────────────────────────────────────────
class Particle:
    def __init__(self, x, y, color, is_waste=False):
        self.x  = x;  self.y = y
        angle   = random.uniform(0, math.tau)
        speed   = random.uniform(2, 8) if not is_waste else random.uniform(3, 10)
        self.vx = math.cos(angle)*speed
        self.vy = math.sin(angle)*speed - 2
        self.life  = random.randint(30, 60)
        self.max_l = self.life
        self.r  = random.randint(3, 8)
        self.color = color
        self.waste = is_waste
    def update(self):
        self.x  += self.vx
        self.vy += 0.2
        self.y  += self.vy
        self.life -= 1
    def draw(self, surface):
        alpha = int(255 * self.life / self.max_l)
        col   = (*self.color[:3], alpha)
        s = pygame.Surface((self.r*2, self.r*2), pygame.SRCALPHA)
        shape = "X" if self.waste else "O"
        if self.waste:
            pygame.draw.line(s, col, (0,0),(self.r*2,self.r*2), 2)
            pygame.draw.line(s, col, (self.r*2,0),(0,self.r*2), 2)
        else:
            pygame.draw.circle(s, col, (self.r,self.r), self.r)
        surface.blit(s, (int(self.x-self.r), int(self.y-self.r)))
    @property
    def alive(self): return self.life > 0

# ─────────────────────────────────────────────
#  NATURE OBJECT (grown at landing spot)
# ─────────────────────────────────────────────
class NatureObj:
    def __init__(self, x, y, kind_idx):
        self.x = x; self.y = y
        self.kind   = BIO_OBJECTS[kind_idx]
        self.label, self.slogan, self.color, self.waste = self.kind
        self.scale  = 0.0          # grows in
        self.slogan_timer = 180    # 3 seconds
        self.pulse  = 0.0
        self.age    = 0
        self.alive  = True
        self.particles = [Particle(x, y, self.color, self.waste)
                          for _ in range(30 if self.waste else 20)]

    def update(self):
        self.age += 1
        self.particles = [p for p in self.particles if p.alive]
        for p in self.particles: p.update()
        if self.slogan_timer > 0: self.slogan_timer -= 1
        if self.waste:
            if self.age > 60:  # blow up waste after 1s
                self.alive = False
        else:
            self.scale = min(1.0, self.scale + 0.03)
            self.pulse = math.sin(self.age * 0.05) * 2

    def draw(self, surface):
        for p in self.particles: p.draw(surface)

        if not self.waste:
            self._draw_nature(surface)

        if self.slogan_timer > 0:
            alpha = min(255, self.slogan_timer * 4)
            self._draw_slogan(surface, alpha)

    def _draw_nature(self, surface):
        s = self.scale
        x, y = int(self.x), int(self.y)
        label = self.label

        if "Tree" in label or "Sapling" in label:
            h_trunk = int(40*s); w_trunk=8
            pygame.draw.rect(surface, BROWN, (x-w_trunk//2, y-h_trunk, w_trunk, h_trunk))
            for layer, (dy, r) in enumerate([(h_trunk, int(30*s)),
                                              (h_trunk+18, int(22*s)),
                                              (h_trunk+32, int(14*s))]):
                pygame.draw.circle(surface, GREEN_D,
                                   (x, y-dy), r+int(self.pulse))

        elif "Pond" in label or "Wetland" in label:
            pygame.draw.ellipse(surface, BLUE_POND,
                                (x-int(40*s), y-int(15*s), int(80*s), int(30*s)))
            pygame.draw.ellipse(surface, (100,200,240),
                                (x-int(30*s), y-int(10*s), int(30*s), int(12*s)))

        elif "Flower" in label or "Butterfly" in label or "Meadow" in label:
            for i in range(6):
                angle = i * math.pi/3
                px = x + int(math.cos(angle)*(12*s))
                py = y + int(math.sin(angle)*(12*s))
                pygame.draw.circle(surface, self.color, (px, py), int(7*s))
            pygame.draw.circle(surface, YELLOW, (x, y), int(5*s))

        elif "Bee" in label:
            # hive
            pygame.draw.ellipse(surface, YELLOW,
                                (x-int(18*s), y-int(22*s), int(36*s), int(44*s)))
            for row in range(3):
                for col in range(2):
                    hx = x - int(10*s) + col*int(18*s)
                    hy = y - int(15*s) + row*int(14*s)
                    pygame.draw.polygon(surface, ORANGE,
                        [(hx, hy-int(4*s)), (hx+int(7*s), hy),
                         (hx+int(7*s), hy+int(4*s)), (hx, hy+int(8*s)),
                         (hx-int(7*s), hy+int(4*s)), (hx-int(7*s), hy)], 1)

        elif "Wheat" in label or "Cactus" in label:
            for i in range(-2, 3):
                stx = x + i*10
                pygame.draw.line(surface, self.color,
                                 (stx, y), (stx, y-int(35*s)), 3)
                pygame.draw.ellipse(surface, self.color,
                                    (stx-5, y-int(40*s), 10, int(15*s)))

        elif "Mush" in label:
            pygame.draw.rect(surface, (200,160,100),
                             (x-5, y-int(20*s), 10, int(20*s)))
            pygame.draw.ellipse(surface, self.color,
                                (x-int(20*s), y-int(30*s), int(40*s), int(20*s)))

        elif "Bird" in label:
            pygame.draw.circle(surface, self.color, (x, y-int(15*s)), int(10*s))
            pygame.draw.polygon(surface, self.color,
                                [(x-int(20*s), y),
                                 (x, y-int(5*s)),
                                 (x+int(20*s), y),
                                 (x, y+int(15*s))])

        else:
            # Generic circle plant
            pygame.draw.circle(surface, self.color, (x, y-int(15*s)), int(15*s))
            pygame.draw.rect(surface, BROWN, (x-3, y-int(5*s), 6, int(5*s)))

    def _draw_slogan(self, surface, alpha):
        words   = self.slogan
        icon    = self.label.split()[0]   # emoji
        col     = self.color if not self.waste else RED

        # Slogan box
        txt_surf = font_slogan.render(f"{icon}  {words}", True, col)
        bx = self.x - txt_surf.get_width()//2
        by = self.y - 90

        box = pygame.Surface((txt_surf.get_width()+14, txt_surf.get_height()+8), pygame.SRCALPHA)
        box.fill((0,0,0,120))
        surface.blit(box, (bx-7, by-4))
        surface.blit(txt_surf, (bx, by))

# ─────────────────────────────────────────────
#  BALL
# ─────────────────────────────────────────────
class Ball:
    RADIUS = 12
    def __init__(self):
        self.reset()

    def reset(self):
        self.x    = 120.0            # bowler side
        self.y    = H - 140.0
        self.vx   = random.uniform(9.0, 13.0)
        self.vy   = random.uniform(-3.0, -1.0)
        self.active  = True
        self.hit     = False
        self.hit_vx  = 0.0
        self.hit_vy  = 0.0
        self.rot     = 0.0
        self.trail   = []
        # randomly pick the object this ball carries
        self.kind_idx = random.randint(0, len(BIO_OBJECTS)-1)

    def update(self):
        if not self.active: return
        self.vy += 0.15           # gravity
        self.x  += self.vx
        self.y  += self.vy
        self.rot = (self.rot + self.vx*2) % 360
        self.trail.append((int(self.x), int(self.y)))
        if len(self.trail) > 12: self.trail.pop(0)

        # bounce on ground
        if self.y >= H - 110:
            self.y  = H - 110
            self.vy = -abs(self.vy) * 0.55
            if abs(self.vy) < 0.8:
                self.active = False

        # out of screen right
        if self.x > W + 50:
            self.active = False

    def draw(self, surface):
        # trail
        for i, (tx, ty) in enumerate(self.trail):
            a = int(80 * i / len(self.trail))
            s = pygame.Surface((8,8), pygame.SRCALPHA)
            pygame.draw.circle(s, (255,60,60,a), (4,4), 4)
            surface.blit(s, (tx-4, ty-4))
        # ball
        if self.active:
            pygame.draw.circle(surface, (220,50,50), (int(self.x), int(self.y)), self.RADIUS)
            pygame.draw.circle(surface, WHITE,       (int(self.x), int(self.y)), self.RADIUS, 2)
            # seam
            angle = math.radians(self.rot)
            ex = int(self.x + math.cos(angle)*self.RADIUS)
            ey = int(self.y + math.sin(angle)*self.RADIUS)
            pygame.draw.line(surface, (200,200,200),
                             (int(self.x - math.cos(angle)*self.RADIUS),
                              int(self.y - math.sin(angle)*self.RADIUS)),
                             (ex, ey), 2)

    def in_bat_zone(self, bat_x, bat_y):
        return (abs(self.x - bat_x) < 60 and abs(self.y - bat_y) < 50)

# ─────────────────────────────────────────────
#  BATSMAN (simple stick figure)
# ─────────────────────────────────────────────
class Batsman:
    def __init__(self):
        self.x = W - 200
        self.y = H - 110
        self.swing    = 0       # swing animation frame
        self.swinging = False

    def start_swing(self):
        if not self.swinging:
            self.swinging = True
            self.swing    = 0

    def update(self):
        if self.swinging:
            self.swing += 4
            if self.swing >= 40:
                self.swinging = False
                self.swing    = 0

    def bat_tip(self):
        """Returns tip of bat for collision."""
        arm_angle = math.radians(-90 + self.swing * 4) if self.swinging else math.radians(-90)
        bx = self.x + int(math.cos(arm_angle)*60)
        by = self.y - 30 + int(math.sin(arm_angle)*60)
        return bx, by

    def draw(self, surface):
        x, y = self.x, self.y
        # legs
        pygame.draw.line(surface, (50,50,120), (x, y-30), (x-12, y+20), 4)
        pygame.draw.line(surface, (50,50,120), (x, y-30), (x+12, y+20), 4)
        # body
        pygame.draw.line(surface, WHITE, (x, y-70), (x, y-30), 4)
        # helmet head
        pygame.draw.circle(surface, (255,200,50), (x, y-78), 14)
        pygame.draw.arc(surface, (200,150,0),
                        (x-14, y-92, 28, 28), 0, math.pi, 4)
        # arms + bat
        arm_angle = math.radians(-90 + self.swing * 4) if self.swinging else math.radians(-90)
        ax = x + int(math.cos(arm_angle)*30)
        ay = y - 55 + int(math.sin(arm_angle)*30)
        pygame.draw.line(surface, WHITE, (x, y-55), (ax, ay), 3)
        # bat
        bat_end_x = x + int(math.cos(arm_angle)*80)
        bat_end_y = y - 55 + int(math.sin(arm_angle)*80)
        pygame.draw.line(surface, BROWN, (ax, ay), (bat_end_x, bat_end_y), 7)
        pygame.draw.line(surface, (210,160,60), (ax, ay), (bat_end_x, bat_end_y), 3)

# ─────────────────────────────────────────────
#  BOWLER (simple stick figure on left)
# ─────────────────────────────────────────────
def draw_bowler(surface, bowling):
    x, y = 100, H - 110
    col  = WHITE
    # run-up lean
    lean = -10 if bowling else 0
    # legs
    pygame.draw.line(surface, (120,50,50), (x, y-30), (x-12+lean, y+20), 4)
    pygame.draw.line(surface, (120,50,50), (x, y-30), (x+12+lean, y+20), 4)
    # body
    pygame.draw.line(surface, col, (x+lean, y-70), (x, y-30), 4)
    # head
    pygame.draw.circle(surface, (255,200,150), (x+lean, y-80), 12)
    # throwing arm
    arm_a = math.radians(-60) if bowling else math.radians(-120)
    ax = x+lean + int(math.cos(arm_a)*30)
    ay = y - 55 + int(math.sin(arm_a)*30)
    pygame.draw.line(surface, col, (x+lean, y-55), (ax, ay), 3)

# ─────────────────────────────────────────────
#  SCOREBOARD
# ─────────────────────────────────────────────
def draw_scoreboard(surface, score, hits, missed_good_balls, streak):
    pygame.draw.rect(surface, (0,0,0,160), (0, 0, W, 50))
    s1 = font_med.render(f"🌿 Eco Score: {score}", True, (100,255,100))
    s2 = font_sm.render(f"Hits: {hits}  Good Misses: {missed_good_balls}/4  Streak: {streak}🔥", True, YELLOW)
    surface.blit(s1, (20, 10))
    surface.blit(s2, (320, 16))

# ─────────────────────────────────────────────
#  LANDING INDICATOR (where ball will fall)
# ─────────────────────────────────────────────
def draw_indicator(surface, x, y):
    pygame.draw.ellipse(surface, (255,255,100,180),
                        (int(x)-18, int(y)-6, 36, 12))

# ─────────────────────────────────────────────
#  DRAW PITCH / FIELD
# ─────────────────────────────────────────────
def draw_field(surface):
    # outfield
    pygame.draw.rect(surface, GROUND, (0, H-200, W, 200))
    # cricket pitch strip
    pygame.draw.rect(surface, PITCH, (W//2-250, H-180, 500, 80))
    # crease lines
    pygame.draw.line(surface, WHITE, (W-220, H-180), (W-220, H-100), 3)
    pygame.draw.line(surface, WHITE, (220, H-180), (220, H-100), 3)
    # stumps – batsman end
    for i in range(3):
        sx = W - 200 + i*8
        pygame.draw.rect(surface, (210,170,80), (sx, H-130, 4, 35))
        pygame.draw.circle(surface, (210,170,80), (sx+2, H-130), 4)
    # stumps – bowler end
    for i in range(3):
        sx = 195 + i*8
        pygame.draw.rect(surface, (210,170,80), (sx, H-130, 4, 35))
        pygame.draw.circle(surface, (210,170,80), (sx+2, H-130), 4)

# ─────────────────────────────────────────────
#  GAME OVER SCREEN
# ─────────────────────────────────────────────
def draw_game_over_screen(surface, score):
    overlay = pygame.Surface((W, H), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    surface.blit(overlay, (0, 0))

    if score >= 0:
        title_text = "Game Over"
        msg_text = f"Your Final Score: {score}"
        title_color = YELLOW
    else:
        title_text = "You Lose!"
        msg_text = "Your score is negative. Better luck next time!"
        title_color = RED

    title_render = font_big.render(title_text, True, title_color)
    msg_render = font_med.render(msg_text, True, WHITE)
    restart_render = font_sm.render("Press 'R' to Restart or ESC to Quit", True, WHITE)

    surface.blit(title_render, (W // 2 - title_render.get_width() // 2, H // 2 - 80))
    surface.blit(msg_render, (W // 2 - msg_render.get_width() // 2, H // 2 - 10))
    surface.blit(restart_render, (W // 2 - restart_render.get_width() // 2, H // 2 + 50))

# ─────────────────────────────────────────────
#  HIT FLASH
# ─────────────────────────────────────────────
class HitFlash:
    def __init__(self, is_waste):
        self.life  = 20
        self.waste = is_waste
    def update(self): self.life -= 1
    def draw(self, surface):
        if self.life <= 0: return
        col = (220,60,60) if self.waste else (100,255,100)
        a   = int(120 * self.life/20)
        s   = pygame.Surface((W,H), pygame.SRCALPHA)
        s.fill((*col, a))
        surface.blit(s, (0,0))

# ─────────────────────────────────────────────
#  MISS TEXT POPUP
# ─────────────────────────────────────────────
class Popup:
    def __init__(self, text, x, y, color):
        self.text  = text
        self.x, self.y = x, y
        self.life  = 60
        self.color = color
    def update(self):
        self.y  -= 1
        self.life -= 1
    def draw(self, surface):
        a   = min(255, self.life*5)
        t   = font_med.render(self.text, True, self.color)
        s   = pygame.Surface(t.get_size(), pygame.SRCALPHA)
        s.blit(t, (0,0))
        s.set_alpha(a)
        surface.blit(s, (int(self.x)-t.get_width()//2, int(self.y)))

# ─────────────────────────────────────────────
#  MAIN GAME
# ─────────────────────────────────────────────
def main():
    clouds   = [Cloud() for _ in range(5)]
    batsman  = Batsman()
    ball     = Ball()
    nature_objs  = []
    particles_ex = []      # extra global particles
    popups   = []
    flash    = None
    score    = 0
    hits     = 0
    streak   = 0
    missed_good_balls = 0
    best_str = 0
    bowl_delay = 60        # frames before next bowl
    bowling    = False
    game_over  = False
    # pre-grown static trees for scenery
    scenery = [(50, H-110, 0), (W-50, H-110, 0),
               (200, H-110, 2), (W-200, H-110, 2)]

    def new_ball():
        nonlocal bowl_delay, bowling
        bowl_delay = 90
        bowling    = False
        ball.reset()

    running = True
    while running:
        dt = clock.tick(FPS)

        # ── EVENTS ──────────────────────────
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                running = False
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    running = False
                if ev.key == pygame.K_r:
                    save_score(score)
                    main(); return
                if ev.key == pygame.K_SPACE and not game_over:
                    batsman.start_swing()
            if ev.type == pygame.MOUSEBUTTONDOWN and not game_over:
                batsman.start_swing()

        # ── UPDATE ──────────────────────────
        if not game_over:
            for c in clouds: c.update()
            batsman.update()

            # Bowling delay
            if bowl_delay > 0:
                bowl_delay -= 1
                if bowl_delay == 0:
                    bowling = True

            if bowling:
                ball.update()

            # Check hit
            if bowling and ball.active and batsman.swinging:
                bx, by = batsman.bat_tip()
                if ball.in_bat_zone(bx, by) and not ball.hit:
                    # HIT! only score once per ball
                    is_waste = BIO_OBJECTS[ball.kind_idx][3]
                    # reflect and send flying
                    ball.vx  = -random.uniform(7, 12)
                    ball.vy  = -random.uniform(5, 9)
                    ball.hit = True
                    hits    += 1

                    if is_waste:
                        # Bad item hit
                        pts = -1  # Penalty for hitting waste
                        streak = 0
                        popup_msg = f"{pts} ☠️ WASTE HIT!"
                        popup_color = RED
                    else:
                        # Good item hit
                        pts = 3  # Reward for hitting a good item
                        streak += 1
                        popup_msg = f"+{pts} 🌱 ECO HIT!"
                        popup_color = (100, 255, 100)

                    score += pts  # Update the main score
                    best_str = max(best_str, streak)
                    flash    = HitFlash(is_waste)
                    # spawn nature/waste object at predicted landing
                    land_x = batsman.x - random.randint(80, 350)
                    land_y = H - 115
                    nature_objs.append(NatureObj(land_x, land_y, ball.kind_idx))
                    popups.append(Popup(popup_msg, W//2, H//2, popup_color))

            # Ball goes past bat (miss)
            if bowling and ball.active and ball.x > batsman.x + 40:
                is_good_ball = not BIO_OBJECTS[ball.kind_idx][3]
                if is_good_ball:
                    missed_good_balls += 1
                    streak = 0
                    popups.append(Popup("MISS! 😬", batsman.x, batsman.y-60, RED))
                    if missed_good_balls >= 4:  # Game over after 4 good misses
                        game_over = True
                ball.active = False

            # Ball settled
            if bowling and not ball.active:
                bowling  = False
                new_ball()

            # Update nature objects
            for n in nature_objs: n.update()
            nature_objs = [n for n in nature_objs if n.alive or n.slogan_timer > 0]

            # Update particles
            for p in particles_ex: p.update()
            particles_ex = [p for p in particles_ex if p.alive]

            # Popups
            for p in popups: p.update()
            popups = [p for p in popups if p.life > 0]

            # Flash
            if flash:
                flash.update()
                if flash.life <= 0: flash = None

        # ── DRAW ────────────────────────────
        draw_sky(screen)
        for c in clouds: c.draw(screen)
        draw_field(screen)

        # Scenery trees
        for sx, sy, ki in scenery:
            n = NatureObj.__new__(NatureObj)
            n.x=sx; n.y=sy; n.scale=1.0; n.pulse=0
            n.kind=(BIO_OBJECTS[ki])
            n.label, n.slogan, n.color, n.waste = n.kind
            n.slogan_timer=0; n.age=999; n.alive=True; n.particles=[]
            n._draw_nature(screen)

        # Nature objects
        for n in nature_objs: n.draw(screen)

        # Particles extra
        for p in particles_ex: p.draw(screen)

        # Flash
        if flash: flash.draw(screen)

        # Bowler
        draw_bowler(screen, bowling)

        # Ball
        if bowling:
            ball.draw(screen)

        # Batsman
        batsman.draw(screen)

        # Scoreboard
        draw_scoreboard(screen, score, hits, missed_good_balls, streak)

        # Popups
        for p in popups: p.draw(screen)

        # Next ball preview
        if not bowling and bowl_delay > 0 and not game_over:
            obj   = BIO_OBJECTS[ball.kind_idx]
            label = obj[0]; is_w = obj[3]
            hint  = font_sm.render(
                f"Next: {'🗑️ Waste – SMASH it!' if is_w else f'🌿 {label}'}", True,
                RED if is_w else (100,255,150))
            screen.blit(hint, (W//2 - hint.get_width()//2, H-50))
            ct  = font_sm.render(f"Bowling in {bowl_delay//30 + 1}s…", True, YELLOW)
            screen.blit(ct, (W//2 - ct.get_width()//2, H-30))

        # Best streak badge
        if best_str >= 3:
            badge = font_sm.render(f"🏆 Best Streak: {best_str}", True, YELLOW)
            screen.blit(badge, (W-200, 10))

        # Instructions
        instr = font_sm.render("SPACE or CLICK to swing bat", True, (200,200,200))
        screen.blit(instr, (W-300, H-25))

        # Game Over Screen
        if game_over:
            draw_game_over_screen(screen, score)

        pygame.display.flip()

    # If the game was completed (4 good misses), save the final score.
    # Otherwise (e.g., quit early), award 0.
    final_score = score if game_over else 0
    save_score(final_score)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()