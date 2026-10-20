"""
╔══════════════════════════════════════════════════════════════════════════╗
║               🌿  E C O   S N A K E   3 D  🌿                          ║
║         A Pseudo-3D Sustainability Snake Game built with Pygame         ║
╠══════════════════════════════════════════════════════════════════════════╣
║  ARCHITECTURE OVERVIEW:                                                  ║
║   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ║
║   │    Snake    │  │  WasteItem  │  │   PowerUp   │  │ Environment │  ║
║   │  (player)   │  │ (bio/nonbio)│  │ (boost/heal)│  │ (eco system)│  ║
║   └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘  ║
║   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ║
║   │  Renderer   │  │ AudioManager│  │    HUD      │  │  AIHint     │  ║
║   │ (pseudo-3D) │  │ (sfx/music) │  │  (overlay)  │  │ (best move) │  ║
║   └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘  ║
║   ┌─────────────────────────────────────────────────────────────────┐   ║
║   │                    EcoSnakeGame  (main loop)                    │   ║
║   └─────────────────────────────────────────────────────────────────┘   ║
║                                                                          ║
║  PSEUDO-3D TECHNIQUE:                                                    ║
║   • Grid rows converge toward a vanishing point at the top-centre       ║
║   • Objects at smaller row-index (far) → smaller, dimmer, desaturated   ║
║   • Objects at larger row-index (near) → larger, brighter, vivid        ║
║   • Snake segments smoothly interpolated between grid steps              ║
║                                                                          ║
║  HOW TO RUN:                                                             ║
║   pip install pygame                                                     ║
║   python eco_snake.py                                                    ║
║                                                                          ║
║  STREAMLIT:                                                              ║
║   pip install streamlit                                                  ║
║   streamlit run eco_snake.py                                             ║
╚══════════════════════════════════════════════════════════════════════════╝
"""

# ═══════════════════════════════════════════════════════════════
# SECTION 1 — IMPORTS
# ═══════════════════════════════════════════════════════════════
import pygame
import sys
import random
import math
import time
import json
import os
import threading
from collections import deque
from typing import List, Tuple, Optional, Dict, Any

def save_score(score):
    """Save the final score to a JSON file to integrate with Streamlit."""
    score_file = os.path.join(os.path.dirname(__file__), 'eco_snake_score.json')
    try:
        with open(score_file, 'w') as f:
            json.dump({'score': score}, f)
    except Exception:
        pass

# ═══════════════════════════════════════════════════════════════
# SECTION 2 — GLOBAL CONSTANTS
# ═══════════════════════════════════════════════════════════════

# ── Window ──────────────────────────────────────────────────────
SCREEN_W, SCREEN_H = 960, 700
FPS = 60

# ── Grid (play field) ───────────────────────────────────────────
GRID_COLS = 22          # columns across
GRID_ROWS = 17          # rows down
CELL = SCREEN_W // GRID_COLS   # nominal cell size in pixels ≈ 43

# ── Layout ──────────────────────────────────────────────────────
HUD_H   = 80            # pixels reserved at top for HUD
PLAY_Y  = HUD_H         # play-area top edge
PLAY_H  = SCREEN_H - HUD_H
PLAY_W  = SCREEN_W

# ── Pseudo-3D vanishing point (top-centre of play area) ─────────
VP_X = SCREEN_W // 2
VP_Y = PLAY_Y           # horizon sits right at the HUD border

# ── Colour palette (earthy + neon accents) ──────────────────────
C_BG_CLEAN    = ( 14,  38,  20)   # deep forest green
C_BG_POLLUTED = ( 22,  16,   8)   # murky brown-black
C_GRID_CLEAN  = ( 28,  70,  34)
C_GRID_POLL   = ( 38,  26,  12)
C_SNAKE_HEAD  = ( 72, 224,  96)
C_SNAKE_BODY  = ( 44, 164,  64)
C_SNAKE_SHINE = (140, 255, 160)
C_BIO_WASTE   = (180, 230,  70)   # yellow-green  → good
C_NONBIO      = (220,  54,  36)   # hot red       → bad
C_POWERUP     = ( 70, 190, 255)   # sky blue
C_TREE_LEAF   = ( 34, 140,  36)
C_TREE_TRUNK  = (100,  64,  28)
C_WHITE       = (255, 255, 255)
C_BLACK       = (  0,   0,   0)
C_GOLD        = (255, 200,  50)
C_HEALTH_HI   = ( 80, 220,  80)
C_HEALTH_LO   = (220,  50,  50)
C_ECO_COLOR   = ( 80, 200, 100)
C_HINT        = (255, 230,  80)

# ── Game-play tuning ────────────────────────────────────────────
INITIAL_MOVE_DELAY = 180          # ms between snake steps (lower = faster)
MIN_MOVE_DELAY     = 60
SPEED_STEP         = 8            # ms faster per level
LEVEL_SCORE_GAP    = 50           # score points to gain a level
HEALTH_MAX         = 100
NONBIO_DAMAGE      = 22           # HP lost per non-bio pickup
BIO_SCORE          = 2
BIO_ECO            = 3
NONBIO_PENALTY     = 1            # points subtracted
POWER_DURATION_S   = 6.0          # seconds power-ups last
TREE_ECO_THRESHOLD = 15           # eco points between tree rewards
NUM_WASTE_ITEMS    = 6
LEADERBOARD_FILE   = "eco_leaderboard.json"


# ═══════════════════════════════════════════════════════════════
# SECTION 3 — MATHS / GEOMETRY HELPERS
# ═══════════════════════════════════════════════════════════════

def lerp(a: float, b: float, t: float) -> float:
    """Linear interpolation between a and b."""
    return a + (b - a) * t

def lerp_color(c1: tuple, c2: tuple, t: float) -> tuple:
    """Per-channel lerp between two RGB tuples."""
    t = max(0.0, min(1.0, t))
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))

def clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))

def perspective_scale(row: float) -> float:
    """
    Maps a grid row [0 = far/top, GRID_ROWS = near/bottom]
    to a scale factor [0.38 = tiny/far … 1.0 = full-size/near].
    This is the heart of our pseudo-3D illusion.
    """
    t = row / GRID_ROWS
    return lerp(0.38, 1.0, t)

def screen_pos(col: float, row: float) -> Tuple[int, int]:
    """
    Project a (possibly fractional) grid position onto the screen,
    pulling it toward the vanishing point based on perspective_scale.
    """
    s  = perspective_scale(row)
    fx = PLAY_W * col / GRID_COLS + CELL / 2.0
    fy = PLAY_Y + PLAY_H * row / GRID_ROWS + CELL / 2.0
    px = int(VP_X + (fx - VP_X) * s)
    py = int(VP_Y + (fy - VP_Y) * s + PLAY_Y * (1 - s) * 0.4)
    return px, py

def cell_radius(row: float) -> int:
    """Visual radius of a grid cell at this row (perspective-scaled)."""
    return max(7, int(CELL * 0.48 * perspective_scale(row)))

def row_brightness(row: float, eco: float) -> float:
    """
    Near rows are brighter; eco_factor shifts overall luminosity.
    Returns a multiplier [0..1].
    """
    depth   = lerp(0.35, 1.0, row / GRID_ROWS)
    eco_dim = lerp(0.55, 1.0, eco)
    return depth * eco_dim

def tint(color: tuple, factor: float) -> tuple:
    """Multiply every RGB channel by factor, clamping to [0, 255]."""
    return tuple(int(clamp(c * factor, 0, 255)) for c in color)

def distance(a: Tuple[int,int], b: Tuple[int,int]) -> float:
    return math.hypot(a[0]-b[0], a[1]-b[1])


# ═══════════════════════════════════════════════════════════════
# SECTION 4 — AUDIO MANAGER
# ═══════════════════════════════════════════════════════════════

class AudioManager:
    """
    Generates synthetic 8-bit-style sound effects procedurally
    (no audio files required).  Background music is a simple
    arpeggiated chord loop synthesised on the fly.
    Optionally fires espeak TTS for voice feedback.
    """

    SAMPLE_RATE = 44100

    def __init__(self):
        self.ok = False
        self._tts_busy = False
        try:
            pygame.mixer.pre_init(self.SAMPLE_RATE, -16, 1, 512)
            pygame.mixer.init()
            self.ok = True
            self._build_sounds()
            self._start_music()
        except Exception:
            pass   # audio unavailable — game still runs

    # ── Sound synthesis ─────────────────────────────────────────
    def _synth(self, freq: float, dur: float, vol: float = 0.4,
               shape: str = "sine", decay: float = 0.8) -> Optional[pygame.mixer.Sound]:
        """Generate a single waveform sample as a pygame Sound."""
        if not self.ok:
            return None
        n   = int(self.SAMPLE_RATE * dur)
        buf = bytearray(n * 2)
        for i in range(n):
            t     = i / self.SAMPLE_RATE
            phase = 2 * math.pi * freq * t
            if shape == "sine":
                v = math.sin(phase)
            elif shape == "square":
                v = 1.0 if math.sin(phase) >= 0 else -1.0
            elif shape == "saw":
                v = 2 * (freq * t % 1) - 1
            else:
                v = math.sin(phase)
            env   = math.exp(-decay * t / dur)   # exponential envelope
            sample = int(clamp(v * vol * env * 32767, -32768, 32767))
            buf[i*2]     =  sample & 0xFF
            buf[i*2 + 1] = (sample >> 8) & 0xFF
        try:
            return pygame.mixer.Sound(buffer=bytes(buf))
        except Exception:
            return None

    def _build_sounds(self):
        self.sfx: Dict[str, Optional[pygame.mixer.Sound]] = {
            "bio":     self._synth(660, 0.15, 0.35, "sine",   1.5),
            "nonbio":  self._synth(180, 0.25, 0.45, "square", 1.0),
            "powerup": self._synth(880, 0.28, 0.35, "sine",   0.8),
            "levelup": self._synth(1047,0.35, 0.40, "sine",   0.6),
            "hurt":    self._synth(140, 0.30, 0.50, "square", 1.2),
            "gameover":self._synth(120, 0.55, 0.55, "saw",    0.6),
            "tree":    self._synth(523, 0.40, 0.35, "sine",   0.5),
        }

    def _start_music(self):
        """Create a short looping ambient track and play it."""
        # Build a 2-second arpeggiated loop
        notes = [261.6, 329.6, 392.0, 523.2, 392.0, 329.6]
        note_dur = 0.33
        total    = len(notes) * note_dur
        n        = int(self.SAMPLE_RATE * total)
        buf      = bytearray(n * 2)
        for ni, freq in enumerate(notes):
            start = int(ni * note_dur * self.SAMPLE_RATE)
            end   = int(start + note_dur * self.SAMPLE_RATE)
            for i in range(start, min(end, n)):
                t     = (i - start) / self.SAMPLE_RATE
                phase = 2 * math.pi * freq * t
                env   = math.exp(-3 * t / note_dur)
                v     = math.sin(phase) * 0.18 * env
                s     = int(clamp(v * 32767, -32768, 32767))
                buf[i*2]     =  s & 0xFF
                buf[i*2 + 1] = (s >> 8) & 0xFF
        try:
            snd = pygame.mixer.Sound(buffer=bytes(buf))
            snd.set_volume(0.25)
            snd.play(loops=-1)
        except Exception:
            pass

    # ── Public API ──────────────────────────────────────────────
    def play(self, name: str):
        if self.ok and name in self.sfx and self.sfx[name]:
            try:
                self.sfx[name].play()
            except Exception:
                pass

    def speak(self, text: str):
        """Fire espeak TTS in a background thread (no-op if unavailable)."""
        if self._tts_busy:
            return
        def _run():
            self._tts_busy = True
            try:
                os.system(f'espeak -s 150 "{text}" 2>/dev/null')
            except Exception:
                pass
            self._tts_busy = False
        threading.Thread(target=_run, daemon=True).start()


# ═══════════════════════════════════════════════════════════════
# SECTION 5 — WASTE ITEM  (food replacement)
# ═══════════════════════════════════════════════════════════════

class WasteItem:
    """
    A waste item sitting on the grid.
    • bio=True  → biodegradable  (leaf-green) → collect for points
    • bio=False → non-biodegradable (red)     → avoid / damages health
    """

    # Rule-based waste classification vocabulary
    BIO_VOCAB    = ["Banana Peel", "Apple Core", "Leaves",
                    "Egg Shell",   "Coffee Grd", "Bread Crust"]
    NONBIO_VOCAB = ["Plastic Btl", "Old Battery", "Tin Can",
                    "Broken Glass","Plastic Bag", "E-Waste"]

    def __init__(self, col: int, row: int, bio: bool):
        self.col  = col
        self.row  = row
        self.bio  = bio
        seed      = (col * 7 + row * 13) % 6
        self.label = (self.BIO_VOCAB if bio else self.NONBIO_VOCAB)[seed]
        self._anim = random.uniform(0, math.pi * 2)   # bobbing phase offset

    @property
    def pos(self) -> Tuple[int, int]:
        return (self.col, self.row)

    def update(self, dt: float):
        self._anim += dt * 3.0

    def draw(self, surf: pygame.Surface, eco: float):
        px, py = screen_pos(self.col, self.row)
        r      = cell_radius(self.row)
        br     = row_brightness(self.row, eco)
        bob    = int(math.sin(self._anim) * 3 * perspective_scale(self.row))

        base_col = C_BIO_WASTE if self.bio else C_NONBIO
        col      = tint(base_col, br)
        glow_col = tint(base_col, br * 0.4)

        # ── shadow ellipse ───────────────────────────────────────
        pygame.draw.ellipse(surf, tint((0,0,0), 0.5),
                            (px - r, py + r//2, r*2, r//3))

        # ── glow rings ───────────────────────────────────────────
        for dr in range(r + 6, r, -2):
            pygame.draw.circle(surf, glow_col, (px, py - bob), dr)

        # ── body ─────────────────────────────────────────────────
        pygame.draw.circle(surf, col, (px, py - bob), r)

        # ── icon: leaf (bio) or skull (non-bio) ──────────────────
        icon_col = tint(C_WHITE, br * 0.9)
        icon_r   = max(3, r // 2)
        if self.bio:
            # simple leaf shape: two arcs
            pts = []
            for a in range(0, 360, 20):
                ang = math.radians(a)
                lx  = px + int(icon_r * 0.7 * math.cos(ang) * math.cos(math.radians(45)))
                ly  = py - bob + int(icon_r * math.sin(ang))
                pts.append((lx, ly))
            if len(pts) > 2:
                pygame.draw.polygon(surf, icon_col, pts)
        else:
            # X marks the spot
            d = icon_r // 2
            pygame.draw.line(surf, icon_col,
                             (px - d, py - bob - d), (px + d, py - bob + d), 2)
            pygame.draw.line(surf, icon_col,
                             (px + d, py - bob - d), (px - d, py - bob + d), 2)


# ═══════════════════════════════════════════════════════════════
# SECTION 6 — POWER-UP
# ═══════════════════════════════════════════════════════════════

class PowerUp:
    """
    Three flavours:
      "recycle" → invincibility to non-bio waste
      "slow"    → halves movement speed
      "heal"    → restores +30 HP
    """
    KINDS  = ["recycle", "slow", "heal"]
    ICONS  = {"recycle": "R", "slow": "S", "heal": "H"}
    COLORS = {"recycle": C_POWERUP,
               "slow":   (200, 255,  80),
               "heal":   (255, 120, 180)}

    def __init__(self, col: int, row: int):
        self.col   = col
        self.row   = row
        self.kind  = random.choice(self.KINDS)
        self._anim = random.uniform(0, math.pi * 2)

    @property
    def pos(self) -> Tuple[int, int]:
        return (self.col, self.row)

    def update(self, dt: float):
        self._anim += dt * 4.0

    def draw(self, surf: pygame.Surface, eco: float):
        px, py = screen_pos(self.col, self.row)
        r      = cell_radius(self.row)
        br     = row_brightness(self.row, eco)
        bob    = int(math.sin(self._anim) * 5 * perspective_scale(self.row))
        spin   = self._anim * 0.6

        col  = tint(self.COLORS[self.kind], br)
        gcol = tint(self.COLORS[self.kind], br * 0.3)

        # glow
        for dr in range(r + 8, r, -2):
            pygame.draw.circle(surf, gcol, (px, py - bob), dr)

        # rotating diamond
        pts = []
        for i in range(4):
            ang = spin + i * math.pi / 2
            pts.append((px + int(r * math.cos(ang)),
                         py - bob + int(r * math.sin(ang))))
        pygame.draw.polygon(surf, col, pts)
        pygame.draw.polygon(surf, tint(C_WHITE, br * 0.6), pts, 2)

        # letter label in centre
        try:
            fnt = pygame.font.SysFont("consolas", max(8, r // 2), bold=True)
            lbl = fnt.render(self.ICONS[self.kind], True, tint(C_WHITE, br))
            surf.blit(lbl, (px - lbl.get_width()//2, py - bob - lbl.get_height()//2))
        except Exception:
            pass


# ═══════════════════════════════════════════════════════════════
# SECTION 7 — SNAKE
# ═══════════════════════════════════════════════════════════════

class Snake:
    """
    The player entity.

    Movement model:
      • Grid-based stepping (step() called at a timed interval)
      • Between steps, anim_t [0→1] interpolates segments for
        buttery-smooth sub-grid motion.
      • grow_pending queues tail growth after collecting waste.
    """

    # Arrow keys + WASD
    DIR_MAP = {
        pygame.K_UP:    ( 0, -1), pygame.K_w: ( 0, -1),
        pygame.K_DOWN:  ( 0,  1), pygame.K_s: ( 0,  1),
        pygame.K_LEFT:  (-1,  0), pygame.K_a: (-1,  0),
        pygame.K_RIGHT: ( 1,  0), pygame.K_d: ( 1,  0),
    }

    def __init__(self):
        self.reset()

    def reset(self):
        mc, mr = GRID_COLS // 2, GRID_ROWS // 2
        # segments[0] = head, stored as (col, row) deque
        self.segments: deque = deque([
            (mc,     mr),
            (mc - 1, mr),
            (mc - 2, mr),
        ])
        self.direction    = (1, 0)
        self.next_dir     = (1, 0)
        self.prev_segs    = list(self.segments)
        self.anim_t       = 0.0          # interpolation progress 0→1
        self.health       = HEALTH_MAX
        self.grow_pending = 0
        self.alive        = True
        # active power-up state
        self.invincible   = False
        self.slowed       = False
        self.pw_timer: Dict[str, float] = {}

    # ── Input ────────────────────────────────────────────────────
    def handle_key(self, key: int):
        if key in self.DIR_MAP:
            nd = self.DIR_MAP[key]
            # disallow reversing directly
            if (nd[0] + self.direction[0], nd[1] + self.direction[1]) != (0, 0):
                self.next_dir = nd

    # ── Step (called on timer) ───────────────────────────────────
    def step(self):
        self.direction = self.next_dir
        self.prev_segs = list(self.segments)
        hc, hr = self.segments[0]
        nc, nr = hc + self.direction[0], hr + self.direction[1]
        self.segments.appendleft((nc, nr))
        if self.grow_pending > 0:
            self.grow_pending -= 1
        else:
            self.segments.pop()
        self.anim_t = 0.0

    def advance_anim(self, dt: float, move_delay_ms: float):
        """Push anim_t toward 1.0 so motion is smooth between steps."""
        self.anim_t = min(1.0, self.anim_t + dt / (move_delay_ms / 1000.0))

    def update_powerups(self, dt: float):
        for kind in list(self.pw_timer.keys()):
            self.pw_timer[kind] -= dt
            if self.pw_timer[kind] <= 0:
                del self.pw_timer[kind]
        self.invincible = "recycle" in self.pw_timer
        self.slowed     = "slow"    in self.pw_timer

    def apply_powerup(self, kind: str):
        if kind == "heal":
            self.health = min(HEALTH_MAX, self.health + 30)
        else:
            self.pw_timer[kind] = POWER_DURATION_S

    # ── Collision queries ────────────────────────────────────────
    @property
    def head(self) -> Tuple[int, int]:
        return self.segments[0]

    def hits_wall(self) -> bool:
        c, r = self.head
        return not (0 <= c < GRID_COLS and 0 <= r < GRID_ROWS)

    def hits_self(self) -> bool:
        body = list(self.segments)
        return self.head in body[1:]

    # ── Smooth interpolated position for a segment ───────────────
    def _seg_pos(self, idx: int) -> Tuple[float, float]:
        cur = self.segments[idx]
        prv = self.prev_segs[idx] if idx < len(self.prev_segs) else cur
        t   = self.anim_t
        return (lerp(prv[0], cur[0], t),
                lerp(prv[1], cur[1], t))

    # ── Draw ─────────────────────────────────────────────────────
    def draw(self, surf: pygame.Surface, eco: float, show_hint: bool,
             hint_dir: Optional[Tuple[int,int]]):
        segs = list(self.segments)
        n    = len(segs)

        # ── Draw tail → head (painter's order so head is on top) ──
        for i in range(n - 1, -1, -1):
            col_f, row_f = self._seg_pos(i)
            px,    py    = screen_pos(col_f, row_f)
            r            = cell_radius(row_f)
            br           = row_brightness(row_f, eco)
            fade         = (n - i) / n   # 1=head, →0 at tail tip

            if i == 0:
                # ── Head ───────────────────────────────────────────
                base = tint(C_SNAKE_HEAD, br)

                # invincibility glow
                if self.invincible:
                    for gr in range(r + 14, r, -3):
                        pygame.draw.circle(surf, tint(C_GOLD, 0.25),
                                           (px, py), gr)

                # shadow
                pygame.draw.ellipse(surf, tint((0,0,0), 0.5),
                                    (px - r, py + r - 2, r*2, r//3))
                # head body
                pygame.draw.circle(surf, base, (px, py), r)
                # shine
                pygame.draw.circle(surf,
                                   tint(C_SNAKE_SHINE, br * 0.5),
                                   (px - r//3, py - r//3),
                                   max(1, r // 3))

                # eyes — positioned in direction of travel
                dc, dr  = self.direction
                eye_r   = max(2, r // 4)
                perp    = (-dr, dc)
                for sign in (+1, -1):
                    ex = px + dc * (r // 2) + sign * perp[0] * (r // 3)
                    ey = py + dr * (r // 2) + sign * perp[1] * (r // 3)
                    pygame.draw.circle(surf, C_WHITE, (ex, ey), eye_r)
                    pygame.draw.circle(surf, C_BLACK,
                                       (ex + dc, ey + dr), max(1, eye_r//2))

                # AI hint arrow
                if show_hint and hint_dir:
                    hd_c, hd_r  = hint_dir
                    arrow_len   = r + 10
                    ax = px + int(hd_c * arrow_len)
                    ay = py + int(hd_r * arrow_len)
                    pygame.draw.line(surf, C_HINT, (px, py), (ax, ay), 2)
                    pygame.draw.circle(surf, C_HINT, (ax, ay), 4)

            else:
                # ── Body segment ────────────────────────────────────
                seg_r = max(5, int(r * (0.40 + 0.38 * fade)))
                c     = tint(C_SNAKE_BODY, br * fade)
                # shadow
                pygame.draw.ellipse(surf, tint((0,0,0), 0.4),
                                    (px - seg_r, py + seg_r - 1, seg_r*2, seg_r//2))
                pygame.draw.circle(surf, c, (px, py), seg_r)
                # highlight
                pygame.draw.circle(surf,
                                   tint(C_SNAKE_SHINE, br * fade * 0.3),
                                   (px - seg_r//3, py - seg_r//3),
                                   max(1, seg_r // 3))


# ═══════════════════════════════════════════════════════════════
# SECTION 8 — ENVIRONMENT
# ═══════════════════════════════════════════════════════════════

class Environment:
    """
    Tracks the eco-system state:
      eco_factor: 0.0 = fully polluted, 1.0 = pristine
    Manages trees, particles, and floating notification texts.
    """

    def __init__(self):
        self.score      = 0
        self.eco_score  = 0
        self.pollution  = 0       # internal pollution counter
        self.eco_factor = 1.0
        self.trees: List[Tuple[int,int]] = []
        self._next_tree_eco = TREE_ECO_THRESHOLD
        self.particles: List[Dict] = []
        self.notifs:    List[Dict] = []

    # ── Eco bookkeeping ─────────────────────────────────────────
    def on_bio_collect(self):
        self.score     += BIO_SCORE
        self.eco_score += BIO_ECO
        self.pollution  = max(0, self.pollution - 8)
        self._recalc()
        self._try_plant_tree()
        self._notify(f"+{BIO_SCORE} pts  🌱", C_BIO_WASTE, 2.0)

    def on_nonbio_collect(self, invincible: bool) -> bool:
        """Returns True if health damage should be applied."""
        self.pollution += 18
        self.score      = max(0, self.score - NONBIO_PENALTY)
        self._recalc()
        if invincible:
            self._notify("♻ Recycled!  No damage!", C_POWERUP, 1.8)
            return False
        self._notify(f"☠ -{NONBIO_DAMAGE} HP", C_NONBIO, 2.0)
        return True

    def on_powerup(self, kind: str):
        labels = {"recycle": "♻ Recycle Shield ON!",
                  "slow":    "🐢 Time Slow ON!",
                  "heal":    "💚 +30 HP!"}
        self._notify(labels.get(kind, "Power-up!"), C_POWERUP, 2.2)

    def on_level_up(self, level: int):
        self._notify(f"⬆ Level {level}!  Speed UP!", C_GOLD, 2.5)

    def _recalc(self):
        self.eco_factor = clamp(1.0 - self.pollution / 220.0, 0.0, 1.0)

    def _try_plant_tree(self):
        if self.eco_score >= self._next_tree_eco:
            self._next_tree_eco += TREE_ECO_THRESHOLD
            # find a free grid cell near an edge
            for _ in range(40):
                c = random.randint(0, GRID_COLS - 1)
                r = random.randint(0, GRID_ROWS - 1)
                if (c, r) not in self.trees:
                    self.trees.append((c, r))
                    self._notify("🌳 Tree Planted!", C_TREE_LEAF, 2.8)
                    return

    # ── Particles ────────────────────────────────────────────────
    def spawn_particles(self, px: int, py: int, color: tuple, count: int = 10):
        for _ in range(count):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(1.5, 4.5)
            self.particles.append({
                "x": float(px), "y": float(py),
                "vx": math.cos(angle) * speed,
                "vy": math.sin(angle) * speed - 1,
                "color": color,
                "life": 1.0,
            })

    # ── Floating notification texts ───────────────────────────────
    def _notify(self, text: str, color: tuple, duration: float):
        self.notifs.append({
            "text": text, "color": color,
            "ttl": duration, "age": 0.0,
        })

    # ── Update per-frame ─────────────────────────────────────────
    def update(self, dt: float):
        # particles
        for p in self.particles[:]:
            p["x"]  += p["vx"]
            p["y"]  += p["vy"]
            p["vy"] += 0.12   # gravity
            p["life"] -= dt * 1.8
            if p["life"] <= 0:
                self.particles.remove(p)
        # notifications
        for n in self.notifs[:]:
            n["age"] += dt
            if n["age"] >= n["ttl"]:
                self.notifs.remove(n)

    # ── Draw helpers ─────────────────────────────────────────────
    def draw_trees(self, surf: pygame.Surface):
        for (c, r) in self.trees:
            px, py = screen_pos(c, r)
            cr     = cell_radius(r)
            br     = row_brightness(r, self.eco_factor)
            # trunk
            tw = max(2, cr // 5)
            th = int(cr * 0.55)
            pygame.draw.rect(surf, tint(C_TREE_TRUNK, br),
                             (px - tw//2, py - th, tw, th))
            # foliage (3 layered circles)
            for layer in range(3):
                lbr = br * (0.55 + 0.15 * layer)
                lr  = int(cr * (0.42 - 0.09 * layer))
                ly  = py - th - layer * (lr // 2)
                pygame.draw.circle(surf, tint(C_TREE_LEAF, lbr), (px, ly), lr)

    def draw_particles(self, surf: pygame.Surface):
        for p in self.particles:
            a = int(clamp(p["life"] * 255, 0, 255))
            c = tint(p["color"], p["life"])
            r = max(1, int(3 * p["life"]))
            pygame.draw.circle(surf, c, (int(p["x"]), int(p["y"])), r)

    def draw_notifs(self, surf: pygame.Surface, font: pygame.font.Font):
        y = PLAY_Y + 18
        for n in self.notifs:
            progress = n["age"] / n["ttl"]
            alpha    = int((1 - max(0, progress - 0.7) / 0.3) * 255)
            rise     = int(progress * -22)
            label    = font.render(n["text"], True, n["color"])
            label.set_alpha(alpha)
            surf.blit(label, (SCREEN_W // 2 - label.get_width() // 2, y + rise))
            y += label.get_height() + 5


# ═══════════════════════════════════════════════════════════════
# SECTION 9 — RENDERER (Pseudo-3D Grid & Background)
# ═══════════════════════════════════════════════════════════════

class Renderer:
    """
    Draws the perspective-projected grid and the atmospheric sky.
    Also handles the star-field for the background glow.
    """

    def __init__(self):
        self._stars = [(random.randint(0, SCREEN_W),
                         random.randint(PLAY_Y, PLAY_Y + PLAY_H // 3),
                         random.uniform(0.3, 1.0)) for _ in range(60)]

    def draw_sky(self, surf: pygame.Surface, eco: float, frame: int):
        """Gradient sky that shifts green↔brown with eco level."""
        top_col = lerp_color(C_BG_POLLUTED, C_BG_CLEAN, eco)
        bot_col = lerp_color((30, 22, 10), (20, 55, 28), eco)
        for y in range(PLAY_Y, SCREEN_H):
            t = (y - PLAY_Y) / PLAY_H
            c = lerp_color(top_col, bot_col, t)
            pygame.draw.line(surf, c, (0, y), (SCREEN_W, y))

        # stars visible when polluted (eerie sky)
        if eco < 0.7:
            for sx, sy, br in self._stars:
                a = int((0.7 - eco) / 0.7 * br * 180)
                if a > 0:
                    pygame.draw.circle(surf, tint(C_WHITE, br), (sx, sy), 1)

        # fog overlay when very polluted
        if eco < 0.45:
            intensity = int((0.45 - eco) / 0.45 * 130)
            fog = pygame.Surface((SCREEN_W, PLAY_H), pygame.SRCALPHA)
            fog.fill((28, 18, 6, intensity))
            surf.blit(fog, (0, PLAY_Y))

    def draw_grid(self, surf: pygame.Surface, eco: float):
        """
        Draw the converging perspective grid:
        • Horizontal stripes at each row.
        • Vertical lines all radiate from the vanishing point VP.
        """
        gc = lerp_color(C_GRID_POLL, C_GRID_CLEAN, eco)

        # ── Horizontal grid lines ────────────────────────────────
        for row in range(GRID_ROWS + 1):
            s  = perspective_scale(row)
            y  = int(VP_Y + (PLAY_Y + PLAY_H * row / GRID_ROWS - VP_Y) * s
                     + PLAY_Y * (1 - s) * 0.4)
            x0 = int(VP_X + (0        - VP_X) * s)
            x1 = int(VP_X + (PLAY_W   - VP_X) * s)
            alpha = int(lerp(35, 130, row / GRID_ROWS) * (0.4 + 0.6 * eco))
            lc    = tint(gc, alpha / 180.0)
            pygame.draw.line(surf, lc, (x0, y), (x1, y))

        # ── Vertical lines (radiate from VP) ─────────────────────
        for col in range(GRID_COLS + 1):
            bx = int(PLAY_W * col / GRID_COLS)
            by = PLAY_Y + PLAY_H
            alpha = int(55 * (0.4 + 0.6 * eco))
            lc    = tint(gc, alpha / 120.0)
            pygame.draw.line(surf, lc, (VP_X, PLAY_Y), (bx, by))

        # Horizon line
        hz_col = lerp_color((60, 38, 18), (36, 120, 55), eco)
        pygame.draw.line(surf, hz_col, (0, PLAY_Y + 2), (SCREEN_W, PLAY_Y + 2), 2)

    def draw_sun(self, surf: pygame.Surface, eco: float, frame: int):
        """Animated sun / haze orb in top-right corner."""
        sun_col = lerp_color((80, 58, 26), (255, 240, 160), eco)
        cx, cy  = SCREEN_W - 70, PLAY_Y + 55
        pulse   = int(math.sin(frame * 0.04) * 3)
        for rr in range(38 + pulse, 0, -4):
            a  = int(eco * 40 * (rr / 38))
            ct = tint(sun_col, a / 40.0)
            pygame.draw.circle(surf, ct, (cx, cy), rr)


# ═══════════════════════════════════════════════════════════════
# SECTION 10 — AI HINT ENGINE
# ═══════════════════════════════════════════════════════════════

class AIHint:
    """
    Rule-based move suggester.
    Scores each legal direction by:
      +proximity to bio waste
      -proximity to non-bio waste
      -proximity to body segments
      -distance from safe centre
    Returns the direction with the highest score.
    """

    def compute(self, snake: Snake,
                wastes: List[WasteItem],
                powerups: List[PowerUp]) -> Optional[Tuple[int,int]]:
        hc, hr  = snake.head
        body_set= set(list(snake.segments)[1:])
        dirs    = [(0,-1),(0,1),(-1,0),(1,0)]
        best    = None
        best_sc = -1e9

        for dc, dr in dirs:
            if (-dc, -dr) == snake.direction:
                continue   # no reversing
            nc, nr = hc + dc, hr + dr
            if not (0 <= nc < GRID_COLS and 0 <= nr < GRID_ROWS):
                continue
            if (nc, nr) in body_set:
                continue
            score = 0.0
            for w in wastes:
                d = abs(nc - w.col) + abs(nr - w.row)
                if w.bio:
                    score += max(0, 22 - d) * 1.5
                else:
                    score -= max(0, 12 - d) * 2.0
            for seg in list(snake.segments)[1:]:
                d = abs(nc - seg[0]) + abs(nr - seg[1])
                score -= max(0, 5 - d) * 3.0
            score -= abs(nc - GRID_COLS // 2) * 0.3
            if score > best_sc:
                best_sc = score
                best    = (dc, dr)
        return best


# ═══════════════════════════════════════════════════════════════
# SECTION 11 — LEADERBOARD
# ═══════════════════════════════════════════════════════════════

class Leaderboard:
    """Persists top-10 scores to a local JSON file."""

    def __init__(self):
        self.entries: List[Dict] = []
        self._load()

    def _load(self):
        try:
            with open(LEADERBOARD_FILE) as f:
                self.entries = json.load(f)
        except Exception:
            self.entries = []

    def add(self, name: str, score: int, eco: int, level: int):
        self.entries.append({
            "name":  name,
            "score": score,
            "eco":   eco,
            "level": level,
            "date":  time.strftime("%Y-%m-%d"),
        })
        self.entries.sort(key=lambda e: e["score"], reverse=True)
        self.entries = self.entries[:10]
        try:
            with open(LEADERBOARD_FILE, "w") as f:
                json.dump(self.entries, f, indent=2)
        except Exception:
            pass

    def draw(self, surf: pygame.Surface, fonts: Dict[str, pygame.font.Font]):
        overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        overlay.fill((0, 8, 0, 215))
        surf.blit(overlay, (0, 0))

        title = fonts["title"].render("🏆  ECO  LEADERBOARD", True, C_GOLD)
        surf.blit(title, (SCREEN_W//2 - title.get_width()//2, 55))
        pygame.draw.line(surf, C_GOLD, (80, 110), (SCREEN_W - 80, 110), 1)

        hdr = fonts["med"].render(
            f"{'#':<3}  {'NAME':<14} {'SCORE':>7}  {'ECO':>5}  {'LVL':>4}  {'DATE'}",
            True, C_ECO_COLOR)
        surf.blit(hdr, (80, 125))
        pygame.draw.line(surf, C_ECO_COLOR, (80, 150), (SCREEN_W - 80, 150), 1)

        y = 160
        rank_cols = [C_GOLD, (192,192,192), (205,127,50)]
        for i, e in enumerate(self.entries):
            c = rank_cols[i] if i < 3 else C_WHITE
            row = fonts["small"].render(
                f"{'#'+str(i+1):<3}  {e['name']:<14} {e['score']:>7}  "
                f"{e['eco']:>5}  {e['level']:>4}  {e['date']}",
                True, c)
            surf.blit(row, (80, y))
            y += 30

        hint = fonts["small"].render("Press  ENTER  to play again", True, C_WHITE)
        surf.blit(hint, (SCREEN_W//2 - hint.get_width()//2, SCREEN_H - 55))


# ═══════════════════════════════════════════════════════════════
# SECTION 12 — HUD
# ═══════════════════════════════════════════════════════════════

class HUD:
    """Draws the top status bar (score, eco, health, level, power-up timer)."""

    def __init__(self, fonts: Dict[str, pygame.font.Font]):
        self.fonts = fonts

    def draw(self, surf: pygame.Surface, snake: Snake,
             env: Environment, level: int):
        # ── Semi-transparent black strip ─────────────────────────
        bg = pygame.Surface((SCREEN_W, HUD_H), pygame.SRCALPHA)
        bg.fill((0, 0, 0, 190))
        surf.blit(bg, (0, 0))

        fm  = self.fonts["med"]
        fsm = self.fonts["small"]

        # ── Left column: score & eco ──────────────────────────────
        surf.blit(fm.render(f"SCORE  {env.score:>6}", True, C_WHITE),      (12, 8))
        surf.blit(fm.render(f"🌱 ECO  {env.eco_score:>5}", True, C_ECO_COLOR), (12, 38))

        # ── Centre: level & trees ─────────────────────────────────
        lv_text = self.fonts["large"].render(f"LVL {level}", True, C_GOLD)
        surf.blit(lv_text, (SCREEN_W//2 - lv_text.get_width()//2, 6))
        tr_text = fsm.render(f"🌳 × {len(env.trees)}", True, C_TREE_LEAF)
        surf.blit(tr_text, (SCREEN_W//2 - tr_text.get_width()//2, 46))

        # ── Right column: health bar, eco bar, power-up timers ───
        bx, bw, bh = SCREEN_W - 230, 210, 16

        # Health bar
        by = 10
        pygame.draw.rect(surf, (50, 15, 15), (bx, by, bw, bh), border_radius=4)
        hw  = int(bw * snake.health / HEALTH_MAX)
        hc  = lerp_color(C_HEALTH_LO, C_HEALTH_HI,
                         snake.health / HEALTH_MAX)
        pygame.draw.rect(surf, hc, (bx, by, hw, bh), border_radius=4)
        pygame.draw.rect(surf, C_WHITE, (bx, by, bw, bh), 1, border_radius=4)
        surf.blit(fsm.render(f"❤  {snake.health}/{HEALTH_MAX}", True, C_WHITE),
                  (bx, by + bh + 2))

        # Eco / environment bar
        by2 = 46
        pygame.draw.rect(surf, (15, 35, 15), (bx, by2, bw, bh - 4), border_radius=3)
        ew  = int(bw * env.eco_factor)
        pygame.draw.rect(surf, C_ECO_COLOR, (bx, by2, ew, bh - 4), border_radius=3)
        pygame.draw.rect(surf, C_WHITE,     (bx, by2, bw, bh - 4), 1, border_radius=3)
        surf.blit(fsm.render("🌍 ENV", True, C_ECO_COLOR),
                  (bx - 52, by2 - 1))

        # Active power-up timers
        pu_x = bx
        pu_y = SCREEN_H - 22 if False else 0   # unused branch
        icons = {"recycle": ("♻", C_POWERUP), "slow": ("🐢", (200,255,80)),
                 "heal": ("💚", (255,120,180))}
        for kind, remaining in snake.pw_timer.items():
            ico, col = icons.get(kind, ("?", C_WHITE))
            txt = fsm.render(f"{ico} {remaining:.1f}s", True, col)
            surf.blit(txt, (pu_x, 68))
            pu_x += txt.get_width() + 14


# ═══════════════════════════════════════════════════════════════
# SECTION 13 — MENU OVERLAY
# ═══════════════════════════════════════════════════════════════

def draw_menu_overlay(surf: pygame.Surface, fonts: Dict, state: str,
                      env: Optional[Environment] = None,
                      level: int = 1):
    """
    Renders translucent menus for: "start", "paused", "dead".
    state == "dead" shows final score before leaderboard.
    """
    overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
    overlay.fill((4, 16, 8, 225))
    surf.blit(overlay, (0, 0))

    cx = SCREEN_W // 2

    if state == "start":
        lines = [
            (fonts["title"], "🌿  ECO  SNAKE  3D",              C_ECO_COLOR, 80),
            (fonts["med"],   "Clean the planet. Grow your snake.", C_WHITE,   160),
            (fonts["small"], "🌱  Collect biodegradable waste → +points",
                              C_BIO_WASTE,  230),
            (fonts["small"], "☠   Avoid non-biodegradable waste → -HP",
                              C_NONBIO,     265),
            (fonts["small"], "♻   Power-ups boost your abilities",
                              C_POWERUP,    300),
            (fonts["small"], "🌳   Plant trees by raising your Eco Score",
                              C_TREE_LEAF,  335),
            (fonts["small"], "Arrow keys / WASD to move  •  H = toggle hint",
                              C_WHITE,      390),
            (fonts["large"], "Press  SPACE  to start",          C_GOLD,     460),
        ]

    elif state == "paused":
        lines = [
            (fonts["title"], "⏸  PAUSED",     C_GOLD,  200),
            (fonts["med"],   "Press  P  to resume",
                              C_WHITE, 290),
            (fonts["med"],   "Press  R  to restart",
                              C_WHITE, 330),
        ]

    else:   # dead
        score_txt = f"Score: {env.score}   Eco: {env.eco_score}   Level: {level}"
        lines = [
            (fonts["title"], "💀  GAME  OVER",  C_NONBIO, 170),
            (fonts["med"],   score_txt,          C_WHITE,  270),
            (fonts["med"],   "Press  ENTER  for leaderboard",
                              C_GOLD,  340),
            (fonts["med"],   "Press  R  to restart",
                              C_WHITE, 385),
        ]

    for (font, text, color, y) in lines:
        rendered = font.render(text, True, color)
        surf.blit(rendered, (cx - rendered.get_width() // 2, y))


# ═══════════════════════════════════════════════════════════════
# SECTION 14 — MAIN GAME CONTROLLER
# ═══════════════════════════════════════════════════════════════

class EcoSnakeGame:
    """
    Top-level controller.  Owns the Pygame window, clock, all
    subsystems, and drives the main loop.

    States:
      "start"   → title/instruction screen
      "playing" → active gameplay
      "paused"  → pause overlay
      "dead"    → game-over overlay
      "board"   → leaderboard view
    """

    def __init__(self):
        pygame.init()
        pygame.display.set_caption("🌿 Eco Snake 3D")
        self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        self.clock  = pygame.time.Clock()

        # ── Fonts ────────────────────────────────────────────────
        self.fonts = self._load_fonts()

        # ── Sub-systems ──────────────────────────────────────────
        self.audio    = AudioManager()
        self.renderer = Renderer()
        self.board    = Leaderboard()
        self.ai       = AIHint()

        # ── Game objects (initialised in _new_game) ──────────────
        self.snake:   Snake
        self.env:     Environment
        self.wastes:  List[WasteItem] = []
        self.powerups: List[PowerUp]  = []
        self.hud:     HUD

        # ── State ────────────────────────────────────────────────
        self.state        = "start"
        self.level        = 1
        self.frame        = 0
        self.move_delay   = INITIAL_MOVE_DELAY   # ms
        self.last_move_ms = 0
        self.show_hint    = False
        self.hint_dir: Optional[Tuple[int,int]] = None
        self.hint_timer   = 0.0       # seconds until next hint refresh

        # ── Leaderboard name entry ────────────────────────────────
        self._player_name = "Player"

        self._new_game()

    # ── Font loader ─────────────────────────────────────────────
    def _load_fonts(self) -> Dict[str, pygame.font.Font]:
        candidates = ["consolas", "couriernew", "dejavusansmono",
                      "lucidasanstypewriter", "monospace", None]
        def best(size: int, bold: bool = False) -> pygame.font.Font:
            for name in candidates:
                try:
                    return pygame.font.SysFont(name, size, bold=bold)
                except Exception:
                    pass
            return pygame.font.Font(None, size)

        return {
            "title": best(52, bold=True),
            "large": best(36, bold=True),
            "med":   best(24),
            "small": best(18),
            "tiny":  best(14),
        }

    # ── New game reset ───────────────────────────────────────────
    def _new_game(self):
        self.snake    = Snake()
        self.env      = Environment()
        self.wastes   = []
        self.powerups = []
        self.hud      = HUD(self.fonts)
        self.level    = 1
        self.move_delay   = INITIAL_MOVE_DELAY
        self.last_move_ms = pygame.time.get_ticks()
        self.hint_dir     = None
        self.hint_timer   = 0.0
        self._spawn_waste_batch()

    # ── Spawn helpers ────────────────────────────────────────────
    def _free_cells(self) -> List[Tuple[int,int]]:
        occupied = (set(self.snake.segments)
                    | {w.pos for w in self.wastes}
                    | {p.pos for p in self.powerups}
                    | set(self.env.trees))
        return [(c, r) for c in range(GRID_COLS)
                        for r in range(GRID_ROWS)
                        if (c, r) not in occupied]

    def _spawn_waste_batch(self):
        needed = NUM_WASTE_ITEMS - len(self.wastes)
        free   = self._free_cells()
        random.shuffle(free)
        for i in range(min(needed, len(free))):
            c, r = free[i]
            # 60 % bio, 40 % non-bio
            bio = random.random() < 0.60
            self.wastes.append(WasteItem(c, r, bio))

    def _maybe_spawn_powerup(self):
        """Spawn a power-up roughly every 8 bio collects (random chance)."""
        if len(self.powerups) < 1 and random.random() < 0.12:
            free = self._free_cells()
            if free:
                c, r = random.choice(free)
                self.powerups.append(PowerUp(c, r))

    # ── Level progression ────────────────────────────────────────
    def _check_level_up(self):
        new_level = 1 + self.env.score // LEVEL_SCORE_GAP
        if new_level > self.level:
            self.level      = new_level
            self.move_delay = max(MIN_MOVE_DELAY,
                                   INITIAL_MOVE_DELAY - (self.level - 1) * SPEED_STEP)
            self.env.on_level_up(self.level)
            self.audio.play("levelup")
            if self.level % 3 == 0:
                self.audio.speak(f"Level {self.level}. Keep going!")

    # ── AI hint refresh ──────────────────────────────────────────
    def _refresh_hint(self, dt: float):
        self.hint_timer -= dt
        if self.hint_timer <= 0:
            self.hint_timer = 0.4    # recompute 2.5× per second
            if self.show_hint:
                self.hint_dir = self.ai.compute(
                    self.snake, self.wastes, self.powerups)

    # ── Main step (called on move timer) ─────────────────────────
    def _do_step(self):
        self.snake.step()

        # ── Wall / self collision ─────────────────────────────────
        if self.snake.hits_wall() or self.snake.hits_self():
            self._kill_snake()
            return

        head = self.snake.head

        # ── Check waste collisions ────────────────────────────────
        for w in self.wastes[:]:
            if w.pos == head:
                px, py = screen_pos(*head)
                if w.bio:
                    self.env.on_bio_collect()
                    self.env.spawn_particles(px, py, C_BIO_WASTE, 12)
                    self.snake.grow_pending += 1
                    self.audio.play("bio")
                    if self.env.eco_score % 9 == 0:
                        self.audio.speak("Great! You cleaned waste!")
                else:
                    damage = self.env.on_nonbio_collect(self.snake.invincible)
                    self.env.spawn_particles(px, py, C_NONBIO, 10)
                    if damage:
                        self.snake.health -= NONBIO_DAMAGE
                        self.audio.play("hurt")
                        if self.snake.health <= 0:
                            self._kill_snake()
                            return
                    else:
                        self.audio.play("powerup")

                self.wastes.remove(w)
                self._spawn_waste_batch()
                self._maybe_spawn_powerup()
                self._check_level_up()
                break

        # ── Check power-up collisions ─────────────────────────────
        for pu in self.powerups[:]:
            if pu.pos == head:
                self.snake.apply_powerup(pu.kind)
                self.env.on_powerup(pu.kind)
                self.powerups.remove(pu)
                self.audio.play("powerup")
                if pu.kind == "tree":
                    self.audio.play("tree")
                break

        # ── Tree obstacle collision (walk through = lose HP) ──────
        for (tc, tr) in self.env.trees:
            if (tc, tr) == head and not self.snake.invincible:
                self.snake.health = max(0, self.snake.health - 5)
                if self.snake.health == 0:
                    self._kill_snake()
                break

    def _kill_snake(self):
        self.snake.alive = False
        self.state = "dead"
        self.audio.play("gameover")
        self.audio.speak("Game over. You tried your best!")

    # ── Event handling ────────────────────────────────────────────
    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_score(self.env.score)
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                k = event.key

                # Universal
                if k == pygame.K_ESCAPE:
                    save_score(self.env.score)
                    pygame.quit(); sys.exit()

                # State-specific
                if self.state == "start":
                    if k == pygame.K_SPACE:
                        self.state = "playing"

                elif self.state == "playing":
                    self.snake.handle_key(k)
                    if k == pygame.K_p:
                        self.state = "paused"
                    if k == pygame.K_r:
                        self._new_game(); self.state = "playing"
                    if k == pygame.K_h:
                        self.show_hint = not self.show_hint

                elif self.state == "paused":
                    if k == pygame.K_p:
                        self.state = "playing"
                        self.last_move_ms = pygame.time.get_ticks()
                    if k == pygame.K_r:
                        self._new_game(); self.state = "playing"

                elif self.state == "dead":
                    if k == pygame.K_RETURN:
                        self.board.add(self._player_name,
                                       self.env.score,
                                       self.env.eco_score,
                                       self.level)
                        self.state = "board"
                    if k == pygame.K_r:
                        self._new_game(); self.state = "playing"

                elif self.state == "board":
                    if k == pygame.K_RETURN or k == pygame.K_r:
                        self._new_game(); self.state = "playing"

    # ── Draw everything ──────────────────────────────────────────
    def _draw(self):
        eco = self.env.eco_factor

        # ── Background & grid ─────────────────────────────────────
        self.renderer.draw_sky(self.screen, eco, self.frame)
        self.renderer.draw_grid(self.screen, eco)
        self.renderer.draw_sun(self.screen, eco, self.frame)

        # ── Trees ─────────────────────────────────────────────────
        self.env.draw_trees(self.screen)

        # ── Waste items ───────────────────────────────────────────
        for w in self.wastes:
            w.draw(self.screen, eco)

        # ── Power-ups ─────────────────────────────────────────────
        for pu in self.powerups:
            pu.draw(self.screen, eco)

        # ── Snake ─────────────────────────────────────────────────
        if self.snake.alive or self.state in ("dead",):
            self.snake.draw(self.screen, eco,
                            self.show_hint, self.hint_dir)

        # ── Particles & notifications ─────────────────────────────
        self.env.draw_particles(self.screen)
        self.env.draw_notifs(self.screen, self.fonts["med"])

        # ── HUD ───────────────────────────────────────────────────
        self.hud.draw(self.screen, self.snake, self.env, self.level)

        # ── Hint label ────────────────────────────────────────────
        if self.show_hint:
            ht = self.fonts["tiny"].render("AI HINT ON  [H]", True, C_HINT)
            self.screen.blit(ht, (SCREEN_W - ht.get_width() - 8, HUD_H - 16))

        # ── Menu overlays ─────────────────────────────────────────
        if self.state == "start":
            draw_menu_overlay(self.screen, self.fonts, "start")
        elif self.state == "paused":
            draw_menu_overlay(self.screen, self.fonts, "paused")
        elif self.state == "dead":
            draw_menu_overlay(self.screen, self.fonts, "dead",
                              self.env, self.level)
        elif self.state == "board":
            self.board.draw(self.screen, self.fonts)

        pygame.display.flip()

    # ── Main loop ─────────────────────────────────────────────────
    def run(self):
        while True:
            dt = self.clock.tick(FPS) / 1000.0   # seconds
            self.frame += 1

            self._handle_events()

            if self.state == "playing":
                now = pygame.time.get_ticks()

                # Slowed power-up doubles move delay
                effective_delay = (self.move_delay * 2
                                   if self.snake.slowed
                                   else self.move_delay)

                # Step snake on timer
                if now - self.last_move_ms >= effective_delay:
                    self.last_move_ms = now
                    self._do_step()

                # Animate sub-step
                self.snake.advance_anim(dt, effective_delay)
                self.snake.update_powerups(dt)

                # Update waste & power-up bobbing animations
                for w  in self.wastes:   w.update(dt)
                for pu in self.powerups: pu.update(dt)

                # Environment tick
                self.env.update(dt)

                # AI hint
                self._refresh_hint(dt)

            self._draw()


# ═══════════════════════════════════════════════════════════════
# SECTION 15 — STREAMLIT INTEGRATION
# ═══════════════════════════════════════════════════════════════

def run_streamlit():
    """
    Streamlit entry point.
    Displays game info and a button that launches the Pygame window
    as a subprocess (since Pygame cannot render inside a browser tab).
    """
    import streamlit as st
    import subprocess

    st.set_page_config(
        page_title="🌿 Eco Snake 3D",
        page_icon="🌿",
        layout="centered",
    )

    st.title("🌿 Eco Snake 3D")
    st.markdown("""
    **A Sustainability-Themed Snake Game built with Pygame**

    | Feature | Details |
    |---|---|
    | 🌱 **Biodegradable waste** | Collect for +points & eco score |
    | ☠️ **Non-biodegradable waste** | Avoid — reduces health |
    | ♻️ **Power-ups** | Recycle shield, speed slow, healing |
    | 🌳 **Tree planting** | Automatic reward at eco milestones |
    | 📈 **Dynamic difficulty** | Speed increases every level |
    | 🤖 **AI hint** | Press **H** to toggle move suggestions |
    | 🏆 **Leaderboard** | Top 10 saved locally |

    **Controls:** Arrow keys / WASD · P = pause · H = hint · ESC = quit
    """)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🎮  Launch Game Window", type="primary", use_container_width=True):
            subprocess.Popen([sys.executable, __file__, "--pygame"])
            st.success("Game launched in a separate window!")
    with col2:
        if st.button("📋  View Leaderboard", use_container_width=True):
            try:
                with open(LEADERBOARD_FILE) as f:
                    data = json.load(f)
                st.dataframe(data, use_container_width=True)
            except FileNotFoundError:
                st.info("No games played yet. Play first!")

    st.markdown("---")
    st.caption("pip install pygame  •  python eco_snake.py  to run directly")


# ═══════════════════════════════════════════════════════════════
# SECTION 16 — ENTRY POINT
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    # Check if we are running inside a Streamlit app context (not just a subprocess)
    is_streamlit = False
    try:
        from streamlit.runtime.scriptrunner import get_script_run_ctx
        if get_script_run_ctx() is not None:
            is_streamlit = True
    except ImportError:
        pass
        
    # If launched with --pygame flag or via direct python/subprocess, run Pygame
    if "--pygame" in sys.argv or not is_streamlit:
        game = EcoSnakeGame()
        game.run()
    else:
        # Launched directly via `streamlit run eco_snake.py`
        run_streamlit()