import pygame
import random
import math
import sys
import time
import json
import os

def save_score(score):
    """Save the final score to a JSON file to integrate with Streamlit."""
    score_file = os.path.join(os.path.dirname(__file__), 'eco_sorter_score.json')
    try:
        with open(score_file, 'w') as f:
            json.dump({'score': score}, f)
    except Exception:
        pass

# ─────────────────────────────────────────────
#  CONSTANTS
# ─────────────────────────────────────────────
SCREEN_W, SCREEN_H = 480, 680
FPS = 60
GAME_DURATION = 60          # seconds before game ends naturally
GAME_OVER_SCORE = -30       # instant game-over if score drops here

# ── Colour palette (earthy + vibrant) ──
C_BG_TOP      = (15,  40,  20)   # deep forest night
C_BG_BOT      = (30,  80,  40)   # rich grass green
C_GROUND      = (60,  35,  10)   # soil brown
C_BASKET      = (180, 120,  40)  # wicker tan
C_BASKET_RIM  = (220, 160,  60)
C_SCORE_GOOD  = ( 80, 230, 120)
C_SCORE_BAD   = (240,  80,  80)
C_WHITE       = (255, 255, 255)
C_SHADOW      = (  0,   0,   0, 80)
C_HUD_BG      = ( 10,  25,  15, 180)

# ── Item definitions ──
#   (label, emoji-label, color, is_biodegradable)
ITEMS = [
    # Biodegradable — green/warm tones
    ("Apple",     "🍎", (220,  60,  60), True),
    ("Leaf",      "🍃", ( 60, 180,  60), True),
    ("Bread",     "🍞", (210, 160,  70), True),
    ("Banana",    "🍌", (240, 210,  40), True),
    ("Carrot",    "🥕", (230, 130,  40), True),
    # Non-biodegradable — grey/cold tones
    ("Bottle",    "🧴", ( 80, 160, 210), False),
    ("Can",       "🥫", (170,  80,  80), False),
    ("Bag",       "🛍️", (160,  90, 200), False),
    ("Battery",   "🔋", ( 80, 200, 180), False),
    ("Wrapper",   "📦", (160, 160,  80), False),
]


# ─────────────────────────────────────────────
#  HELPER: draw a rounded rectangle (Pygame < 2.0 compat)
# ─────────────────────────────────────────────
def draw_rounded_rect(surface, color, rect, radius, alpha=255):
    """Draw an anti-aliased rounded rectangle."""
    if alpha < 255:
        surf = pygame.Surface((rect[2], rect[3]), pygame.SRCALPHA)
        pygame.draw.rect(surf, (*color, alpha), (0, 0, rect[2], rect[3]), border_radius=radius)
        surface.blit(surf, (rect[0], rect[1]))
    else:
        pygame.draw.rect(surface, color, rect, border_radius=radius)


# ─────────────────────────────────────────────
#  PARTICLE EFFECT
# ─────────────────────────────────────────────
class ParticleEffect:
    """Small burst of coloured dots on item catch."""

    def __init__(self, x, y, color, good):
        self.particles = []
        count = 12 if good else 8
        for _ in range(count):
            angle = random.uniform(0, math.tau)
            speed = random.uniform(1.5, 4.5)
            life  = random.randint(20, 40)
            self.particles.append({
                "x": x, "y": y,
                "vx": math.cos(angle) * speed,
                "vy": math.sin(angle) * speed - 2,
                "life": life, "max_life": life,
                "color": color,
                "size": random.uniform(3, 7),
            })

    def update(self):
        for p in self.particles:
            p["x"]  += p["vx"]
            p["y"]  += p["vy"]
            p["vy"] += 0.15   # gravity
            p["life"] -= 1
        self.particles = [p for p in self.particles if p["life"] > 0]

    def draw(self, surface):
        for p in self.particles:
            alpha = int(255 * p["life"] / p["max_life"])
            r = max(1, int(p["size"] * p["life"] / p["max_life"]))
            color = (*p["color"], alpha)
            surf = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
            pygame.draw.circle(surf, color, (r, r), r)
            surface.blit(surf, (int(p["x"]) - r, int(p["y"]) - r))

    @property
    def alive(self):
        return len(self.particles) > 0


# ─────────────────────────────────────────────
#  FALLING OBJECT
# ─────────────────────────────────────────────
class FallingObject:
    """
    A single item falling from the top of the screen.
    Has a label, colour, biodegradability flag, and
    a gentle horizontal sway (sine wave drift).
    """

    RADIUS = 22

    def __init__(self, speed_multiplier=1.0):
        item = random.choice(ITEMS)
        self.label, self.emoji, self.color, self.biodegradable = item

        # Starting position: random X, above screen
        self.x = random.randint(self.RADIUS + 20, SCREEN_W - self.RADIUS - 20)
        self.y = -self.RADIUS

        # Speed: base 2–4 px/frame, scaled by difficulty
        base_speed = random.uniform(2.0, 4.0)
        self.speed = base_speed * speed_multiplier

        # Sway parameters
        self.sway_amp   = random.uniform(0.3, 1.2)
        self.sway_freq  = random.uniform(0.03, 0.07)
        self.sway_phase = random.uniform(0, math.tau)
        self.tick = 0

        # Visual: small rotation angle
        self.angle    = random.uniform(0, 360)
        self.spin     = random.uniform(-2, 2)

        # Glow pulse
        self.pulse = 0.0

        # Whether item has been caught (prevent double-score)
        self.caught = False
        self.alive  = True

    def update(self):
        self.tick += 1
        # Vertical fall
        self.y += self.speed
        # Gentle horizontal sway
        self.x += math.sin(self.tick * self.sway_freq + self.sway_phase) * self.sway_amp
        # Clamp to screen edges
        self.x = max(self.RADIUS, min(SCREEN_W - self.RADIUS, self.x))
        # Spin
        self.angle = (self.angle + self.spin) % 360
        # Pulse glow
        self.pulse = (math.sin(self.tick * 0.1) + 1) / 2

        # Off-screen = gone
        if self.y > SCREEN_H + self.RADIUS:
            self.alive = False

    def draw(self, surface, font_med, font_small):
        cx, cy = int(self.x), int(self.y)
        r = self.RADIUS

        # Shadow
        shadow_surf = pygame.Surface((r * 2 + 8, r * 2 + 8), pygame.SRCALPHA)
        pygame.draw.circle(shadow_surf, (0, 0, 0, 60), (r + 4, r + 4), r)
        surface.blit(shadow_surf, (cx - r, cy - r + 4))

        # Glow halo for non-biodegradable (warning glow)
        if not self.biodegradable:
            glow_r = int(r + 6 + self.pulse * 4)
            glow_surf = pygame.Surface((glow_r * 2, glow_r * 2), pygame.SRCALPHA)
            alpha = int(60 + self.pulse * 40)
            pygame.draw.circle(glow_surf, (*C_SCORE_BAD, alpha), (glow_r, glow_r), glow_r)
            surface.blit(glow_surf, (cx - glow_r, cy - glow_r))

        # Main circle body
        pygame.draw.circle(surface, self.color, (cx, cy), r)
        # Shine highlight
        pygame.draw.circle(surface, (255, 255, 255, 80), (cx - r // 3, cy - r // 3), r // 4)
        # Border
        border_col = C_SCORE_GOOD if self.biodegradable else C_SCORE_BAD
        pygame.draw.circle(surface, border_col, (cx, cy), r, 2)

        # Label (first 3 chars of name — fits in circle)
        short = self.label[:4]
        txt = font_small.render(short, True, C_WHITE)
        surface.blit(txt, (cx - txt.get_width() // 2, cy - txt.get_height() // 2))

        # Type indicator dot (top of circle)
        dot_col = C_SCORE_GOOD if self.biodegradable else C_SCORE_BAD
        pygame.draw.circle(surface, dot_col, (cx, cy - r - 5), 5)

    def get_rect(self):
        """Return bounding rect for collision detection."""
        return pygame.Rect(self.x - self.RADIUS, self.y - self.RADIUS,
                           self.RADIUS * 2, self.RADIUS * 2)


# ─────────────────────────────────────────────
#  BASKET
# ─────────────────────────────────────────────
class Basket:
    """
    Player-controlled basket at the bottom of the screen.
    Moves left/right with keyboard arrow keys OR mouse/touchpad.
    """

    WIDTH  = 90
    HEIGHT = 36

    def __init__(self):
        self.x = SCREEN_W // 2           # centre x
        self.y = SCREEN_H - 60           # fixed y near bottom
        self.speed = 7                   # keyboard move speed px/frame
        self.use_mouse = False           # toggled if mouse moves
        self._last_mouse_x = SCREEN_W // 2
        # Wobble on catch
        self.wobble = 0.0
        self.wobble_dir = 1

    def update(self, keys):
        # ── Keyboard control ──
        if keys[pygame.K_LEFT]  or keys[pygame.K_a]:
            self.x -= self.speed
            self.use_mouse = False
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.x += self.speed
            self.use_mouse = False

        # ── Mouse / touchpad control ──
        mx, _ = pygame.mouse.get_pos()
        if abs(mx - self._last_mouse_x) > 2:
            self.use_mouse = True
        self._last_mouse_x = mx
        if self.use_mouse:
            # Smooth follow
            self.x += (mx - self.x) * 0.18

        # Clamp to screen
        half = self.WIDTH // 2
        self.x = max(half, min(SCREEN_W - half, self.x))

        # Decay wobble
        if self.wobble > 0:
            self.wobble -= 0.5

    def trigger_wobble(self):
        self.wobble = 8.0

    def draw(self, surface):
        cx = int(self.x)
        cy = int(self.y + math.sin(self.wobble * 0.4) * self.wobble * 0.5)
        w, h = self.WIDTH, self.HEIGHT
        half = w // 2

        # Shadow under basket
        shadow_surf = pygame.Surface((w + 10, 14), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow_surf, (0, 0, 0, 60), (0, 0, w + 10, 14))
        surface.blit(shadow_surf, (cx - half - 5, cy + h - 4))

        # Basket body (trapezoid via polygon)
        top_w = int(w * 0.85)
        pts = [
            (cx - top_w // 2, cy),           # top-left
            (cx + top_w // 2, cy),           # top-right
            (cx + half,       cy + h),       # bottom-right
            (cx - half,       cy + h),       # bottom-left
        ]
        pygame.draw.polygon(surface, C_BASKET, pts)

        # Weave lines (horizontal)
        for i in range(1, 4):
            frac = i / 4
            lx1 = cx - int((top_w // 2) * (1 - frac) + half * frac)
            lx2 = cx + int((top_w // 2) * (1 - frac) + half * frac)
            ly  = cy + int(h * frac)
            pygame.draw.line(surface, C_BASKET_RIM, (lx1, ly), (lx2, ly), 1)

        # Rim (top edge)
        rim_rect = pygame.Rect(cx - top_w // 2 - 3, cy - 5, top_w + 6, 12)
        draw_rounded_rect(surface, C_BASKET_RIM, rim_rect, 4)

        # Outline
        pygame.draw.polygon(surface, C_BASKET_RIM, pts, 2)

        # Small eco-leaf icon on basket
        leaf_pts = [
            (cx, cy + h // 2 - 8),
            (cx + 7, cy + h // 2),
            (cx, cy + h // 2 + 8),
            (cx - 7, cy + h // 2),
        ]
        pygame.draw.polygon(surface, C_SCORE_GOOD, leaf_pts)

    def get_rect(self):
        return pygame.Rect(self.x - self.WIDTH // 2, self.y - 4,
                           self.WIDTH, self.HEIGHT + 4)


# ─────────────────────────────────────────────
#  SCORE POPUP (floating text)
# ─────────────────────────────────────────────
class ScorePopup:
    def __init__(self, x, y, text, color):
        self.x = float(x)
        self.y = float(y)
        self.text = text
        self.color = color
        self.life = 55
        self.max_life = 55

    def update(self):
        self.y -= 1.2
        self.life -= 1

    def draw(self, surface, font):
        alpha = int(255 * self.life / self.max_life)
        scale = 1.0 + 0.3 * (1 - self.life / self.max_life)
        txt = font.render(self.text, True, self.color)
        # Scale surface
        w, h = txt.get_size()
        sw, sh = int(w * scale), int(h * scale)
        scaled = pygame.transform.scale(txt, (sw, sh))
        # Apply alpha
        scaled.set_alpha(alpha)
        surface.blit(scaled, (int(self.x) - sw // 2, int(self.y) - sh // 2))

    @property
    def alive(self):
        return self.life > 0


# ─────────────────────────────────────────────
#  BACKGROUND RENDERER
# ─────────────────────────────────────────────
class Background:
    """Draws a gradient sky + ground strip + animated stars."""

    def __init__(self):
        self._build_gradient()
        self.stars = [
            (random.randint(0, SCREEN_W), random.randint(0, SCREEN_H - 120),
             random.uniform(0.3, 1.0))
            for _ in range(40)
        ]
        self.star_tick = 0

    def _build_gradient(self):
        self.gradient = pygame.Surface((SCREEN_W, SCREEN_H))
        for y in range(SCREEN_H):
            t = y / SCREEN_H
            r = int(C_BG_TOP[0] + (C_BG_BOT[0] - C_BG_TOP[0]) * t)
            g = int(C_BG_TOP[1] + (C_BG_BOT[1] - C_BG_TOP[1]) * t)
            b = int(C_BG_TOP[2] + (C_BG_BOT[2] - C_BG_TOP[2]) * t)
            pygame.draw.line(self.gradient, (r, g, b), (0, y), (SCREEN_W, y))

    def draw(self, surface):
        surface.blit(self.gradient, (0, 0))

        # Twinkling stars
        self.star_tick += 1
        for (sx, sy, phase) in self.stars:
            brightness = int(100 + 80 * math.sin(self.star_tick * 0.04 + phase * 10))
            col = (brightness, brightness, brightness)
            pygame.draw.circle(surface, col, (sx, sy), 1)

        # Ground strip
        ground_rect = pygame.Rect(0, SCREEN_H - 48, SCREEN_W, 48)
        draw_rounded_rect(surface, C_GROUND, ground_rect, 0)
        # Ground highlight line
        pygame.draw.line(surface, (90, 55, 20), (0, SCREEN_H - 48), (SCREEN_W, SCREEN_H - 48), 2)

        # Grass tufts
        for gx in range(10, SCREEN_W, 28):
            h = random.randint(6, 12) if gx % 56 == 10 else 8
            pygame.draw.line(surface, (50, 140, 50),
                             (gx, SCREEN_H - 48),
                             (gx + random.randint(-3, 3), SCREEN_H - 48 - h), 2)


# ─────────────────────────────────────────────
#  HUD
# ─────────────────────────────────────────────
def draw_hud(surface, score, time_left, caught, missed, font_big, font_med, font_small):
    """Draws score panel, timer bar, and legend at top."""

    # ── Top panel background ──
    hud_surf = pygame.Surface((SCREEN_W, 72), pygame.SRCALPHA)
    hud_surf.fill((10, 28, 16, 210))
    surface.blit(hud_surf, (0, 0))

    # ── Title ──
    title = font_med.render("🌍 ECO SORTER", True, C_SCORE_GOOD)
    surface.blit(title, (SCREEN_W // 2 - title.get_width() // 2, 6))

    # ── Score ──
    score_col = C_SCORE_GOOD if score >= 0 else C_SCORE_BAD
    score_txt = font_big.render(f"Score: {score:+d}", True, score_col)
    surface.blit(score_txt, (10, 36))

    # ── Caught / Missed ──
    stat = font_small.render(f"✅{caught}  ❌{missed}", True, C_WHITE)
    surface.blit(stat, (SCREEN_W - stat.get_width() - 10, 48))

    # ── Timer bar ──
    bar_x, bar_y = 10, 60
    bar_w, bar_h = SCREEN_W - 20, 7
    frac = max(0, time_left / GAME_DURATION)
    bar_col = (
        int(C_SCORE_BAD[0] + (C_SCORE_GOOD[0] - C_SCORE_BAD[0]) * frac),
        int(C_SCORE_BAD[1] + (C_SCORE_GOOD[1] - C_SCORE_BAD[1]) * frac),
        int(C_SCORE_BAD[2] + (C_SCORE_GOOD[2] - C_SCORE_BAD[2]) * frac),
    )
    pygame.draw.rect(surface, (50, 50, 50), (bar_x, bar_y, bar_w, bar_h), border_radius=3)
    if frac > 0:
        pygame.draw.rect(surface, bar_col, (bar_x, bar_y, int(bar_w * frac), bar_h), border_radius=3)

    # ── Legend strip at sides ──
    lg = font_small.render("🌱 Bio +2", True, C_SCORE_GOOD)
    lb = font_small.render("☠ Non -1",  True, C_SCORE_BAD)
    surface.blit(lg, (SCREEN_W - lg.get_width() - 8, 6))
    surface.blit(lb, (SCREEN_W - lb.get_width() - 8, 24))


# ─────────────────────────────────────────────
#  GAME CLASS
# ─────────────────────────────────────────────
class Game:
    """
    Main game controller.
    Manages the game loop, spawning, scoring, difficulty,
    and all rendering layers.
    """

    def __init__(self, screen, clock):
        self.screen = screen
        self.clock  = clock

        # Fonts
        pygame.font.init()
        self.font_big   = pygame.font.SysFont("Arial", 26, bold=True)
        self.font_med   = pygame.font.SysFont("Arial", 20, bold=True)
        self.font_small = pygame.font.SysFont("Arial", 14)
        self.font_huge  = pygame.font.SysFont("Arial", 52, bold=True)
        self.font_sub   = pygame.font.SysFont("Arial", 22)

        # Game objects
        self.background  = Background()
        self.basket      = Basket()
        self.objects     = []        # active FallingObjects
        self.particles   = []        # active ParticleEffects
        self.popups      = []        # score popup texts

        # State
        self.score       = 0
        self.caught_bio  = 0         # biodegradable caught
        self.caught_bad  = 0         # non-bio caught (penalty)
        self.missed      = 0
        self.running     = True
        self.game_over   = False
        self.start_time  = time.time()

        # Spawning
        self.spawn_timer    = 0
        self.spawn_interval = 90     # frames between spawns (starts at 1.5s at 60fps)

        # Difficulty ramp
        self.speed_mult  = 1.0

        # Sound (optional — graceful fallback)
        self._init_sounds()

    # ── Sound init ──────────────────────────────
    def _init_sounds(self):
        """Generate simple beep sounds using pygame's synth (no audio files needed)."""
        self.sound_good = None
        self.sound_bad  = None
        try:
            pygame.mixer.init(frequency=22050, size=-16, channels=1, buffer=256)
            # Good catch: short ascending tone
            self.sound_good = self._make_beep(880, 80)
            # Bad catch: low buzzer
            self.sound_bad  = self._make_beep(220, 120)
        except Exception:
            pass   # silently skip if audio unavailable

    @staticmethod
    def _make_beep(frequency, duration_ms):
        """Synthesise a simple sine-wave tone as a pygame Sound object."""
        import array as arr
        sample_rate = 22050
        n_samples   = int(sample_rate * duration_ms / 1000)
        buf = arr.array('h', [0] * n_samples)
        for i in range(n_samples):
            t = i / sample_rate
            envelope = math.sin(math.pi * i / n_samples)    # fade in/out
            val = int(32767 * 0.4 * envelope * math.sin(2 * math.pi * frequency * t))
            buf[i] = val
        sound = pygame.sndarray.make_sound(buf)
        return sound

    def _play(self, sound):
        if sound:
            try:
                sound.play()
            except Exception:
                pass

    # ── Difficulty ────────────────────────────
    def _update_difficulty(self, elapsed):
        """Gradually increase speed and reduce spawn interval over time."""
        # Every 10 seconds: +0.12 speed, spawn 5 frames faster
        stage = int(elapsed / 10)
        self.speed_mult     = 1.0 + stage * 0.12
        self.spawn_interval = max(30, 90 - stage * 5)

    # ── Spawn ─────────────────────────────────
    def _maybe_spawn(self):
        self.spawn_timer += 1
        if self.spawn_timer >= self.spawn_interval:
            self.spawn_timer = 0
            self.objects.append(FallingObject(self.speed_mult))

    # ── Collision ────────────────────────────
    def _check_collisions(self):
        basket_rect = self.basket.get_rect()
        for obj in self.objects:
            if obj.caught or not obj.alive:
                continue
            if basket_rect.colliderect(obj.get_rect()):
                obj.caught = True
                obj.alive  = False
                bx, by = int(self.basket.x), int(self.basket.y)

                if obj.biodegradable:
                    self.score += 2
                    self.caught_bio += 1
                    self._play(self.sound_good)
                    self.particles.append(ParticleEffect(obj.x, obj.y, C_SCORE_GOOD, True))
                    self.popups.append(ScorePopup(bx, by - 20, "+2", C_SCORE_GOOD))
                else:
                    self.score -= 1
                    self.caught_bad += 1
                    self._play(self.sound_bad)
                    self.particles.append(ParticleEffect(obj.x, obj.y, C_SCORE_BAD, False))
                    self.popups.append(ScorePopup(bx, by - 20, "-1", C_SCORE_BAD))

                self.basket.trigger_wobble()

    # ── Main update ──────────────────────────
    def update(self, keys, elapsed):
        if self.game_over:
            return

        self._update_difficulty(elapsed)
        self._maybe_spawn()

        # Update basket
        self.basket.update(keys)

        # Update falling objects
        for obj in self.objects:
            obj.update()
        # Count missed (fell off screen, not caught)
        for obj in self.objects:
            if not obj.alive and not obj.caught:
                self.missed += 1
        self.objects = [o for o in self.objects if o.alive]

        # Collisions
        self._check_collisions()

        # Update effects
        for pe in self.particles:
            pe.update()
        self.particles = [pe for pe in self.particles if pe.alive]

        for pop in self.popups:
            pop.update()
        self.popups = [pop for pop in self.popups if pop.alive]

        # Game-over conditions
        if self.score <= GAME_OVER_SCORE:
            self.game_over = True
        if elapsed >= GAME_DURATION:
            self.game_over = True

    # ── Draw ─────────────────────────────────
    def draw(self, elapsed):
        s = self.screen

        # Background
        self.background.draw(s)

        # Falling objects
        for obj in self.objects:
            obj.draw(s, self.font_med, self.font_small)

        # Particles
        for pe in self.particles:
            pe.draw(s)

        # Basket
        self.basket.draw(s)

        # Score popups
        for pop in self.popups:
            pop.draw(s, self.font_big)

        # HUD
        time_left = max(0, GAME_DURATION - elapsed)
        draw_hud(s, self.score, time_left,
                 self.caught_bio, self.caught_bad,
                 self.font_big, self.font_med, self.font_small)

        # Difficulty badge
        diff_txt = self.font_small.render(
            f"Lv {int((self.speed_mult - 1.0) / 0.12) + 1}  |  Speed ×{self.speed_mult:.1f}",
            True, (180, 230, 180)
        )
        s.blit(diff_txt, (10, 10))

        # ── Game Over overlay ──
        if self.game_over:
            self._draw_game_over(s)

    def _draw_game_over(self, surface):
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 170))
        surface.blit(overlay, (0, 0))

        # Decide win/lose message
        if self.score > 0:
            title_str = "🌿 WELL DONE!"
            title_col = C_SCORE_GOOD
        else:
            title_str = "💀 GAME OVER"
            title_col = C_SCORE_BAD

        title = self.font_huge.render(title_str, True, title_col)
        surface.blit(title, (SCREEN_W // 2 - title.get_width() // 2, SCREEN_H // 2 - 110))

        lines = [
            f"Final Score: {self.score:+d}",
            f"Biodegradable caught: {self.caught_bio}",
            f"Non-bio caught (penalty): {self.caught_bad}",
            "",
            "Press  R  to Restart",
            "Press  Q  to Quit",
        ]
        y = SCREEN_H // 2 - 30
        for line in lines:
            col = C_WHITE if "caught" not in line.lower() and "press" not in line.lower() else (200, 200, 200)
            if "Restart" in line or "Quit" in line:
                col = C_SCORE_GOOD
            txt = self.font_sub.render(line, True, col)
            surface.blit(txt, (SCREEN_W // 2 - txt.get_width() // 2, y))
            y += 30

    # ── Reset ────────────────────────────────
    def reset(self):
        self.basket     = Basket()
        self.objects    = []
        self.particles  = []
        self.popups     = []
        self.score      = 0
        self.caught_bio = 0
        self.caught_bad = 0
        self.missed     = 0
        self.game_over  = False
        self.start_time = time.time()
        self.spawn_timer    = 0
        self.spawn_interval = 90
        self.speed_mult = 1.0


# ─────────────────────────────────────────────
#  SPLASH SCREEN
# ─────────────────────────────────────────────
def draw_splash(surface, font_huge, font_med, font_small, tick):
    """Show a start screen until user presses SPACE or ENTER."""
    surface.fill(C_BG_TOP)

    # Animated gradient circles (decorative)
    for i in range(6):
        r = 60 + i * 20
        alpha = int(30 + 15 * math.sin(tick * 0.04 + i))
        circ_surf = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
        pygame.draw.circle(circ_surf, (*C_SCORE_GOOD, alpha),
                           (r, r), r)
        surface.blit(circ_surf,
                     (SCREEN_W // 2 - r, SCREEN_H // 3 - r))

    title  = font_huge.render("ECO SORTER", True, C_SCORE_GOOD)
    sub    = font_med.render("Catch biodegradable items, avoid non-bio!", True, C_WHITE)
    hint1  = font_med.render("← → Arrow Keys  or  Mouse / Touchpad", True, (180, 255, 180))
    hint2  = font_small.render("+2 pts  🌱 Food/Leaf/Paper    -1 pt  ☠ Plastic/Can/Bag", True, (200, 200, 200))
    press  = font_med.render("PRESS  SPACE  TO START", True,
                              C_SCORE_GOOD if (tick // 30) % 2 == 0 else (50, 120, 50))

    surface.blit(title, (SCREEN_W // 2 - title.get_width() // 2, 90))
    surface.blit(sub,   (SCREEN_W // 2 - sub.get_width() // 2,   190))
    surface.blit(hint1, (SCREEN_W // 2 - hint1.get_width() // 2, 260))
    surface.blit(hint2, (SCREEN_W // 2 - hint2.get_width() // 2, 300))
    surface.blit(press, (SCREEN_W // 2 - press.get_width() // 2, 400))

    # Item preview dots
    preview_items = [i for i in ITEMS]
    for idx, item in enumerate(preview_items):
        px = 48 + idx * 40
        py = 480
        pygame.draw.circle(surface, item[2], (px, py), 16)
        border = C_SCORE_GOOD if item[3] else C_SCORE_BAD
        pygame.draw.circle(surface, border, (px, py), 16, 2)
        lab = font_small.render(item[0][:3], True, C_WHITE)
        surface.blit(lab, (px - lab.get_width() // 2, py + 20))

    info = font_small.render("Game Over if score ≤ −30  |  60 second time limit", True, (160, 160, 160))
    surface.blit(info, (SCREEN_W // 2 - info.get_width() // 2, SCREEN_H - 40))


# ─────────────────────────────────────────────
#  MAIN ENTRY POINT
# ─────────────────────────────────────────────
def run_game():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    pygame.display.set_caption("🌍 Eco Sorter — Climate Guardian")
    clock = pygame.time.Clock()

    font_huge  = pygame.font.SysFont("Arial", 52, bold=True)
    font_med   = pygame.font.SysFont("Arial", 20, bold=True)
    font_small = pygame.font.SysFont("Arial", 14)

    game = Game(screen, clock)
    on_splash = True
    splash_tick = 0

    while True:
        # ── Event handling ──
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_score(game.score)
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if on_splash:
                    if event.key in (pygame.K_SPACE, pygame.K_RETURN):
                        on_splash = False
                        game.start_time = time.time()
                else:
                    if game.game_over:
                        if event.key == pygame.K_r:
                            game.reset()
                        elif event.key == pygame.K_q:
                            save_score(game.score)
                            pygame.quit()
                            sys.exit()

        # ── Splash screen ──
        if on_splash:
            draw_splash(screen, font_huge, font_med, font_small, splash_tick)
            splash_tick += 1
            pygame.display.flip()
            clock.tick(FPS)
            continue

        # ── Game update ──
        keys    = pygame.key.get_pressed()
        elapsed = time.time() - game.start_time
        game.update(keys, elapsed)

        # ── Draw ──
        game.draw(elapsed)
        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    run_game()