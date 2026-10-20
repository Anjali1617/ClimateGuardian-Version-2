"""
╔══════════════════════════════════════════════════════════════════╗
║        SKY PATROL: WASTE HUNT  v2  —  Full Python Game           ║
║        Requires: Python 3.8+  and  pygame >= 2.0                 ║
║        Run:  python sky_patrol_waste_hunt_v2.py                  ║
║                                                                  ║
║  CONTROLS:                                                       ║
║   WASD / Arrow Keys  — Move Eco-Cop                              ║
║   LEFT CLICK         — Shoot toward mouse cursor                 ║
║   SPACE              — Auto-shoot nearest waste entity           ║
║   E                  — Scanner pulse (reveals hidden waste)      ║
║   R                  — Reload ammo                               ║
║   ESC                — Quit                                      ║
╚══════════════════════════════════════════════════════════════════╝
"""

import pygame, sys, math, random, struct, array
import json, os

def save_score(score):
    """Save the final score to a JSON file to integrate with Streamlit."""
    score_file = os.path.join(os.path.dirname(__file__), 'sky_patrol_score.json')
    try:
        with open(score_file, 'w') as f:
            json.dump({'score': score}, f)
    except Exception:
        pass

W, H = 1280, 720
FPS  = 60

C = {
    "ground":    (20,  60,  20),
    "tree_dark": (15,  80,  15),
    "tree_mid":  (30, 120,  30),
    "tree_light":(60, 180,  40),
    "river":     (20, 100, 180),
    "rock":      (80,  80,  70),
    "cop":       (40, 200, 220),
    "cop_dark":  (20, 120, 140),
    "bullet":    (255, 255,  80),
    "waste_s":   (140, 255,  30),
    "waste_m":   (220, 130,   0),
    "waste_b":   (255,  40,  40),
    "plane":     (200, 220, 255),
    "ui_accent": (0,  230, 160),
    "ui_dark":   (10,  30,  20),
    "white":     (255, 255, 255),
    "yellow":    (255, 220,  30),
    "red":       (255,  50,  50),
    "green":     (50,  230,  80),
}

WAVES          = 3
WAVE_TIMINGS   = [60, 45, 30]   # seconds per level: L1=60s, L2=45s, L3=30s
WASTE_PER_WAVE = [6,  10,  15]

SAMPLE_RATE = 44100


# ══════════════════════════════════════════════════════════════════
#  SOUND SYNTHESIS  (zero external files — pure math)
# ══════════════════════════════════════════════════════════════════
def _make_sound(samples):
    """Convert a list of floats [-1,1] into a pygame.Sound."""
    # Clamp
    samples = [max(-1.0, min(1.0, s)) for s in samples]
    # Pack as 16-bit signed stereo
    buf = array.array('h')
    for s in samples:
        v = int(s * 32767)
        buf.append(v)   # left
        buf.append(v)   # right
    snd = pygame.sndarray.make_sound(
        __import__('numpy').array(buf, dtype='int16').reshape(-1, 2)
    )
    return snd


def _env(t, attack=0.005, decay=0.05, sustain=0.6, release=0.1, total=1.0):
    """ADSR envelope value at time t (seconds), total = duration."""
    if t < attack:
        return t / attack
    t -= attack
    if t < decay:
        return 1.0 - (1.0 - sustain) * (t / decay)
    t -= decay
    hold = total - attack - decay - release
    if t < hold:
        return sustain
    t -= hold
    if t < release:
        return sustain * (1.0 - t / release)
    return 0.0


def make_gunshot_sound():
    """Sharp crack + low thud."""
    dur = 0.18
    n   = int(SAMPLE_RATE * dur)
    samples = []
    for i in range(n):
        t  = i / SAMPLE_RATE
        # White noise burst (crack)
        noise  = random.uniform(-1, 1)
        crack  = noise * math.exp(-t * 60) * 1.2
        # Low thud sine
        thud   = math.sin(2 * math.pi * 80 * t) * math.exp(-t * 25) * 0.6
        # High tick
        tick   = math.sin(2 * math.pi * 1800 * t) * math.exp(-t * 120) * 0.4
        samples.append(crack + thud + tick)
    return _make_sound(samples)


def make_hit_sound():
    """Squelchy toxic hit."""
    dur = 0.22
    n   = int(SAMPLE_RATE * dur)
    samples = []
    for i in range(n):
        t    = i / SAMPLE_RATE
        freq = 300 * math.exp(-t * 8)          # falling pitch
        wave = math.sin(2 * math.pi * freq * t)
        noise= random.uniform(-0.3, 0.3)
        env  = math.exp(-t * 18)
        samples.append((wave * 0.7 + noise) * env)
    return _make_sound(samples)


def make_waste_death_sound():
    """'Oh No!' — two descending tones mimicking a groan."""
    dur  = 0.55
    n    = int(SAMPLE_RATE * dur)
    samples = []
    # Syllable 1: "Oh"  — 250 Hz → 180 Hz  (0 to 0.25s)
    # Syllable 2: "No"  — 320 Hz → 120 Hz  (0.25 to 0.55s)
    for i in range(n):
        t = i / SAMPLE_RATE
        if t < 0.25:
            freq = 250 - (250 - 180) * (t / 0.25)
            env  = _env(t, 0.02, 0.05, 0.8, 0.08, 0.25)
        else:
            t2   = t - 0.25
            freq = 320 - (320 - 120) * (t2 / 0.30)
            env  = _env(t2, 0.01, 0.04, 0.7, 0.10, 0.30)
        # Vowel formants: fundamental + 2nd harmonic + vibrato
        vibrato = 1 + 0.015 * math.sin(2 * math.pi * 5.5 * t)
        wave    = (  0.6 * math.sin(2 * math.pi * freq * vibrato * t)
                   + 0.25 * math.sin(2 * math.pi * freq * 2 * vibrato * t)
                   + 0.1  * math.sin(2 * math.pi * freq * 3 * vibrato * t))
        samples.append(wave * env * 0.85)
    return _make_sound(samples)


def make_evolve_sound():
    """Menacing rising hum when waste evolves."""
    dur = 0.5
    n   = int(SAMPLE_RATE * dur)
    samples = []
    for i in range(n):
        t    = i / SAMPLE_RATE
        freq = 100 + 400 * (t / dur)
        wave = math.sin(2 * math.pi * freq * t)
        wave += 0.3 * math.sin(2 * math.pi * freq * 2.01 * t)   # slightly detuned
        noise= random.uniform(-0.1, 0.1)
        env  = _env(t, 0.05, 0.1, 0.6, 0.15, dur)
        samples.append((wave * 0.7 + noise) * env)
    return _make_sound(samples)


def make_reload_sound():
    """Mechanical clunk-click."""
    dur = 0.30
    n   = int(SAMPLE_RATE * dur)
    samples = []
    for i in range(n):
        t = i / SAMPLE_RATE
        # clunk
        c1 = math.sin(2 * math.pi * 220 * t) * math.exp(-t * 40)
        # click at 0.18s
        c2 = 0.0
        if t > 0.18:
            t2 = t - 0.18
            c2 = math.sin(2 * math.pi * 1200 * t2) * math.exp(-t2 * 80)
        noise = random.uniform(-0.15, 0.15) * math.exp(-t * 20)
        samples.append(c1 * 0.6 + c2 * 0.5 + noise)
    return _make_sound(samples)


def make_scan_sound():
    """Rising ping for scanner."""
    dur = 0.35
    n   = int(SAMPLE_RATE * dur)
    samples = []
    for i in range(n):
        t    = i / SAMPLE_RATE
        freq = 600 + 1400 * (t / dur)
        wave = math.sin(2 * math.pi * freq * t)
        env  = _env(t, 0.01, 0.05, 0.5, 0.20, dur)
        samples.append(wave * env * 0.5)
    return _make_sound(samples)


def make_wave_start_sound():
    """Energetic ascending fanfare."""
    dur = 0.7
    n   = int(SAMPLE_RATE * dur)
    notes = [261, 329, 392, 523]   # C E G C
    samples = []
    note_dur = dur / len(notes)
    for i in range(n):
        t   = i / SAMPLE_RATE
        ni  = min(int(t / note_dur), len(notes) - 1)
        nt  = t - ni * note_dur
        freq = notes[ni]
        wave = (  math.sin(2 * math.pi * freq * t)
                + 0.4 * math.sin(2 * math.pi * freq * 2 * t)
                + 0.15 * math.sin(2 * math.pi * freq * 3 * t))
        env  = _env(nt, 0.01, 0.02, 0.7, 0.08, note_dur)
        samples.append(wave * env * 0.5)
    return _make_sound(samples)


def make_empty_click():
    """Dry click when ammo is empty."""
    dur = 0.08
    n   = int(SAMPLE_RATE * dur)
    samples = []
    for i in range(n):
        t = i / SAMPLE_RATE
        samples.append(
            math.sin(2 * math.pi * 800 * t) * math.exp(-t * 100) * 0.4
        )
    return _make_sound(samples)


# ══════════════════════════════════════════════════════════════════
#  UTILITY
# ══════════════════════════════════════════════════════════════════
def clamp(v, lo, hi): return max(lo, min(hi, v))
def lerp(a, b, t):    return a + (b - a) * t
def dist(a, b):       return math.hypot(a[0]-b[0], a[1]-b[1])
def angle_to(s, d):   return math.atan2(d[1]-s[1], d[0]-s[0])
def vfa(a, sp):       return math.cos(a)*sp, math.sin(a)*sp

def rand_edge():
    s = random.randint(0, 3)
    if s == 0: return random.randint(0, W), -40
    if s == 1: return W+40, random.randint(0, H)
    if s == 2: return random.randint(0, W), H+40
    return -40, random.randint(0, H)


# ══════════════════════════════════════════════════════════════════
#  PARTICLES
# ══════════════════════════════════════════════════════════════════
class Particle:
    def __init__(self, x, y, col, vx=0, vy=0, life=40, r=4):
        self.x=x; self.y=y; self.col=col[:3]
        self.vx=vx; self.vy=vy; self.life=life; self.ml=life; self.r=r

    def update(self):
        self.x+=self.vx; self.y+=self.vy; self.vy+=0.12
        self.life-=1; self.r=max(1, self.r-0.05)

    def draw(self, surf):
        al = int(255*self.life/self.ml)
        s  = pygame.Surface((int(self.r*2+2), int(self.r*2+2)), pygame.SRCALPHA)
        pygame.draw.circle(s, (*self.col, al),
                           (int(self.r+1), int(self.r+1)), int(self.r))
        surf.blit(s, (int(self.x-self.r), int(self.y-self.r)))


class PSystem:
    def __init__(self): self.p = []

    def boom(self, x, y, col, n=18):
        for _ in range(n):
            a  = random.uniform(0, math.tau)
            sp = random.uniform(1, 5)
            self.p.append(Particle(x, y, col,
                           math.cos(a)*sp, math.sin(a)*sp,
                           random.randint(25, 50), random.uniform(2, 6)))

    def toxic(self, x, y):
        for _ in range(3):
            a  = random.uniform(0, math.tau)
            sp = random.uniform(.3, 1.5)
            self.p.append(Particle(x, y, (80, 255, 60),
                           math.cos(a)*sp, math.sin(a)*sp-0.4, 40, 3))

    def drop(self, x, y):
        for _ in range(5):
            self.p.append(Particle(x, y, (150, 200, 255),
                           random.uniform(-1, 1), random.uniform(-3, -1), 30, 2))

    def update(self):
        self.p = [p for p in self.p if p.life > 0]
        for p in self.p: p.update()

    def draw(self, surf):
        for p in self.p: p.draw(surf)


# ══════════════════════════════════════════════════════════════════
#  FOREST MAP
# ══════════════════════════════════════════════════════════════════
class Forest:
    def __init__(self):
        random.seed(random.randint(0, 9999))
        self.trees=[]; self.rocks=[]; self.rivers=[]
        self.rivers.append(pygame.Rect(random.randint(100, W-200), 0, 55, H))
        self.rivers.append(pygame.Rect(0, random.randint(150, H-200), W, 45))
        for _ in range(110):
            x = random.randint(10, W-10)
            y = random.randint(90, H-30)
            if not any(r.collidepoint(x, y) for r in self.rivers):
                sz = random.randint(18, 40)
                sh = random.choice([C["tree_dark"], C["tree_mid"], C["tree_light"]])
                self.trees.append((x, y, sz, sh))
        for _ in range(28):
            x = random.randint(20, W-20); y = random.randint(90, H-20)
            w = random.randint(12, 28);   h = random.randint(9, 20)
            self.rocks.append(pygame.Rect(x-w//2, y-h//2, w, h))

    def draw(self, surf):
        surf.fill(C["ground"])
        for r in self.rivers:
            pygame.draw.rect(surf, C["river"], r)
            pygame.draw.rect(surf, (10, 80, 160), r, 2)
        for r in self.rocks:
            pygame.draw.ellipse(surf, C["rock"], r)
            pygame.draw.ellipse(surf, (60, 60, 50), r, 1)
        for x, y, sz, sh in self.trees:
            sh2 = pygame.Surface((sz*2, sz), pygame.SRCALPHA)
            pygame.draw.ellipse(sh2, (0, 0, 0, 50), (0, 0, sz*2, sz))
            surf.blit(sh2, (x-sz, y+sz//3))
            pygame.draw.circle(surf, sh, (x, y), sz)
            lighter = tuple(min(255, c+40) for c in sh)
            pygame.draw.circle(surf, lighter, (x-sz//4, y-sz//4), sz//2)

    def hidden(self, x, y):
        for tx, ty, sz, _ in self.trees:
            if dist((x, y), (tx, ty)) < sz+10: return True
        for r in self.rocks:
            if r.inflate(20, 20).collidepoint(x, y): return True
        for r in self.rivers:
            if r.inflate(8, 8).collidepoint(x, y): return True
        return False


# ══════════════════════════════════════════════════════════════════
#  AIRPLANE
# ══════════════════════════════════════════════════════════════════
class Airplane:
    def __init__(self):
        self.x=-80.0; self.y=55.0; self.spd=1.8; self.dir=1

    def update(self):
        self.x += self.spd * self.dir
        if self.dir== 1 and self.x > W+100:
            self.dir=-1; self.y=min(self.y+25, 85)
        elif self.dir==-1 and self.x < -100:
            self.dir= 1; self.y=min(self.y+25, 85)

    def draw(self, surf):
        x, y = int(self.x), int(self.y)
        flip = self.dir == -1
        wc   = (160, 180, 220)
        if not flip:
            pygame.draw.polygon(surf, wc, [(x-30,y),(x+10,y-8),(x+10,y+8)])
            pygame.draw.polygon(surf, wc, [(x-28,y+5),(x+6,y+14),(x+6,y+5)])
        else:
            pygame.draw.polygon(surf, wc, [(x+30,y),(x-10,y-8),(x-10,y+8)])
            pygame.draw.polygon(surf, wc, [(x+28,y+5),(x-6,y+14),(x-6,y+5)])
        pygame.draw.ellipse(surf, C["plane"], (x-35, y-9, 70, 18))
        wx2 = x-12 if not flip else x-14
        pygame.draw.ellipse(surf, (180,230,255), (wx2, y-6, 22, 12))
        ex = x-38 if not flip else x+20
        pygame.draw.circle(surf, (255,160,40), (ex, y+3), 5)
        pygame.draw.circle(surf, (255,220,100),(ex, y+3), 2)


# ══════════════════════════════════════════════════════════════════
#  ECO-COP  (Player)
# ══════════════════════════════════════════════════════════════════
class Cop:
    SPD = 3.5

    def __init__(self, sounds):
        self.sounds   = sounds
        self.x        = float(W // 2); self.y = 60.0
        self.hp       = 100; self.max_hp = 100
        # Ammo: unlimited magazine — auto-reloads after RELOAD_DELAY frames idle
        self.ammo     = 30; self.max_ammo = 30
        self.reload_t = 0   # counts up; triggers auto-reload when >= RELOAD_DELAY
        self.score    = 0
        self.alive    = True
        self.dropping = True; self.dvy = -8.0
        self.land_y   = float(random.randint(220, H - 90))
        self.bullets  = []
        # shoot_cd: raw frame counter; shoot is allowed only when == 0
        self.shoot_cd = 0
        self.scan_r   = 0; self.scanning = False; self.scan_t = 0
        self.invuln   = 0; self.anim = 0

    SHOOT_COOLDOWN = 10   # frames between shots  (~6 shots/sec at 60 FPS)
    RELOAD_DELAY   = 90   # frames of not-shooting before auto-reload triggers

    # ── Movement & scanner ──────────────────────────────────────
    def update(self, keys, ps):
        self.anim += 0.1
        if self.invuln > 0: self.invuln -= 1

        # Parachute drop phase
        if self.dropping:
            self.dvy = lerp(self.dvy, 2.5, 0.08)
            self.y  += self.dvy
            if self.y >= self.land_y:
                self.y        = self.land_y
                self.dropping = False
                ps.drop(self.x, self.y)
            return

        # Movement
        dx = dy = 0
        if keys[pygame.K_LEFT]  or keys[pygame.K_a]: dx -= 1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: dx += 1
        if keys[pygame.K_UP]    or keys[pygame.K_w]: dy -= 1
        if keys[pygame.K_DOWN]  or keys[pygame.K_s]: dy += 1
        if dx and dy: dx *= 0.707; dy *= 0.707
        self.x = clamp(self.x + dx * self.SPD, 20, W - 20)
        self.y = clamp(self.y + dy * self.SPD, 90, H - 20)

        # Tick down shoot cooldown every frame (this is the ONLY place it decrements)
        if self.shoot_cd > 0:
            self.shoot_cd -= 1

        # Auto-reload: if we have been idle long enough, silently refill ammo
        if self.ammo < self.max_ammo:
            self.reload_t += 1
            if self.reload_t >= self.RELOAD_DELAY:
                self.ammo     = self.max_ammo
                self.reload_t = 0
                self.sounds['reload'].play()
        else:
            self.reload_t = 0

        # Scanner
        if keys[pygame.K_e] and self.scan_t == 0:
            self.scanning = True; self.scan_r = 0; self.scan_t = 80
            self.sounds['scan'].play()
        if self.scan_t > 0:
            self.scan_t -= 1; self.scan_r += 4
            if self.scan_t == 0: self.scanning = False

    # ── Shoot toward (tx, ty) — ALWAYS callable; gate is shoot_cd ──
    def shoot(self, tx, ty, ps):
        if self.dropping:       return   # still falling
        if self.shoot_cd > 0:  return   # rate-limited

        # Auto-reload instantly if completely empty (never permanently silent)
        if self.ammo <= 0:
            self.ammo     = self.max_ammo
            self.reload_t = 0
            self.sounds['reload'].play()
            return   # skip this frame; next press will fire

        a      = angle_to((self.x, self.y), (tx, ty))
        vx, vy = vfa(a, 13)    # bullet speed 13 px/frame — fast & visible
        self.bullets.append({'x': self.x, 'y': self.y,
                              'vx': vx,   'vy': vy, 'age': 0})
        self.ammo      -= 1
        self.shoot_cd   = self.SHOOT_COOLDOWN   # set AFTER appending bullet
        self.reload_t   = 0                     # reset auto-reload idle timer
        self.sounds['gun'].play()
        ps.drop(self.x, self.y)

    # ── Auto-aim at nearest alive waste ─────────────────────────
    def shoot_nearest(self, waste_list, ps):
        if self.dropping: return
        alive = [w for w in waste_list if w.alive]
        if not alive: return
        target = min(alive, key=lambda w: dist((self.x, self.y), (w.x, w.y)))
        self.shoot(target.x, target.y, ps)

    # ── Update bullets, check collisions ────────────────────────
    def update_bullets(self, waste_list, ps):
        hits_this_frame = 0
        kills_this_frame = 0
        misses_this_frame = 0
        alive_bullets = []
        for b in self.bullets:
            b['x']   += b['vx']
            b['y']   += b['vy']
            b['age'] += 1

            # Discard if out of bounds or travelled too long
            if not (0 <= b['x'] <= W and 0 <= b['y'] <= H) or b['age'] > 80:
                misses_this_frame += 1
                continue

            hit_this_bullet = False
            for w in waste_list:
                if not w.alive:
                    continue
                # Generous hit radius so bullets reliably connect
                if dist((b['x'], b['y']), (w.x, w.y)) <= w.rad + 12:
                    hits_this_frame += 1 # A bullet hit a waste entity
                    was_alive = w.alive
                    w.hit(35, ps, self.sounds)
                    hit_this_bullet = True
                    # Play hit-grunt only if NOT killed (death sound handles kill)
                    if was_alive and w.alive:
                        self.sounds['hit'].play()
                    if was_alive and not w.alive:
                        kills_this_frame += 1
                    break   # one bullet hits one target

            if not hit_this_bullet:
                alive_bullets.append(b)

        self.bullets = alive_bullets
        return hits_this_frame, kills_this_frame, misses_this_frame

    # ── Take damage ─────────────────────────────────────────────
    def take_damage(self, d):
        if self.invuln > 0: return
        self.hp    -= d
        self.invuln = 60
        if self.hp <= 0: self.hp = 0; self.alive = False

    # ── Draw ────────────────────────────────────────────────────
    def draw(self, surf):
        x, y = int(self.x), int(self.y)

        # Parachute
        if self.dropping:
            for i in range(5):
                pygame.draw.line(surf, (200,200,200),
                                 (x-30+i*15, y-10), (x, y-40), 1)
            cc = (240,80,80) if (pygame.time.get_ticks()//200)%2==0 else (255,120,120)
            pygame.draw.arc(surf, cc, (x-35, y-70, 70, 50), 0, math.pi, 4)

        # Shadow
        sh = pygame.Surface((30, 10), pygame.SRCALPHA)
        pygame.draw.ellipse(sh, (0,0,0,55), (0,0,30,10))
        surf.blit(sh, (x-15, y+12))

        fl = self.invuln > 0 and (self.invuln//6) % 2 == 0
        bc = (255,255,255) if fl else C["cop"]

        lo = int(math.sin(self.anim*2)*4)
        pygame.draw.line(surf, C["cop_dark"], (x-5,y+8), (x-8,y+18+lo), 3)
        pygame.draw.line(surf, C["cop_dark"], (x+5,y+8), (x+8,y+18-lo), 3)
        pygame.draw.rect(surf, bc, (x-9,y-4,18,14), border_radius=4)
        pygame.draw.circle(surf, bc, (x,y-8), 10)
        pygame.draw.circle(surf, (100,200,230), (x+2,y-10), 4)
        pygame.draw.rect(surf, C["cop_dark"], (x+8,y-2,12,5), border_radius=2)

        # Scanner ring
        if self.scanning and self.scan_r < 200:
            al  = max(0, 180 - self.scan_r)
            rs  = pygame.Surface((self.scan_r*2+4, self.scan_r*2+4), pygame.SRCALPHA)
            pygame.draw.circle(rs, (100,255,200,al),
                               (self.scan_r+2, self.scan_r+2), self.scan_r, 2)
            surf.blit(rs, (x-self.scan_r-2, y-self.scan_r-2))

        # Bullets
        for b in self.bullets:
            bx, by = int(b['x']), int(b['y'])
            # Glow trail
            trail = pygame.Surface((14, 14), pygame.SRCALPHA)
            pygame.draw.circle(trail, (255,255,100,60), (7,7), 7)
            surf.blit(trail, (bx-7, by-7))
            pygame.draw.circle(surf, C["bullet"], (bx, by), 5)
            pygame.draw.circle(surf, (255,255,220), (bx, by), 2)

        # HP bar
        bw = 36
        pygame.draw.rect(surf, (60,20,20), (x-bw//2, y-26, bw, 5))
        hw = int(bw * self.hp / self.max_hp)
        hc = C["green"] if self.hp>50 else C["yellow"] if self.hp>25 else C["red"]
        pygame.draw.rect(surf, hc, (x-bw//2, y-26, hw, 5))


# ══════════════════════════════════════════════════════════════════
#  WASTE ENTITY
# ══════════════════════════════════════════════════════════════════
class Waste:
    STATS = [
        dict(hp=50,  mhp=50,  rad=15, spd=1.5, dmg=8,  col=C["waste_s"], sc=10),
        dict(hp=120, mhp=120, rad=22, spd=1.0, dmg=18, col=C["waste_m"], sc=25),
        dict(hp=300, mhp=300, rad=36, spd=0.6, dmg=35, col=C["waste_b"], sc=80),
    ]

    def __init__(self, x, y, stage=0):
        self.x=float(x); self.y=float(y); self.stage=stage
        self._apply()
        self.alive=True; self.hidden=False
        self.hide_t=0; self.atk_cd=0; self.evo_cd=0
        self.gt = random.uniform(0, math.tau)
        self.pa = random.uniform(0, math.tau)
        self.state = "patrol"
        self.vx = self.vy = 0.0

    def _apply(self):
        s = self.STATS[self.stage]
        self.max_hp=s["mhp"]; self.hp=s["hp"]; self.rad=s["rad"]
        self.spd=s["spd"]; self.dmg=s["dmg"]; self.col=s["col"]; self.sc=s["sc"]

    def update(self, cop, fm, ps):
        if not self.alive: return
        self.gt      += 0.07
        self.atk_cd   = max(0, self.atk_cd-1)
        self.evo_cd   = max(0, self.evo_cd-1)

        d = dist((self.x,self.y), (cop.x,cop.y))

        # Scanner reveal
        if cop.scanning and d < cop.scan_r:
            self.hidden = False; self.state = "flee"

        tx, ty = self.x, self.y

        if self.state == "patrol":
            self.pa += 0.02
            tx = self.x + math.cos(self.pa)*40
            ty = self.y + math.sin(self.pa)*40
            if d < 240: self.state = "hide" if fm.hidden(self.x,self.y) else "chase"

        elif self.state == "hide":
            if fm.hidden(self.x, self.y):
                self.hidden=True; self.hide_t=180
            else:
                tx = self.x+random.uniform(-1,1); ty = self.y+random.uniform(-1,1)
            if d > 310: self.state = "patrol"

        elif self.state == "chase":
            tx = cop.x; ty = cop.y
            if d < self.rad+20 and self.atk_cd==0 and not cop.dropping:
                cop.take_damage(self.dmg); self.atk_cd = 90
            if d > 300 or fm.hidden(self.x,self.y): self.state = "hide"

        elif self.state == "flee":
            a  = angle_to((cop.x,cop.y), (self.x,self.y))
            tx = self.x + math.cos(a)*3
            ty = self.y + math.sin(a)*3

        if self.hide_t > 0:
            self.hide_t -= 1
            if self.hide_t == 0: self.hidden = False
            tx, ty = self.x, self.y

        # Move (unless truly hidden)
        if not (self.state=="hide" and self.hidden):
            a    = angle_to((self.x,self.y), (tx,ty))
            self.vx = lerp(self.vx, math.cos(a)*self.spd, 0.15)
            self.vy = lerp(self.vy, math.sin(a)*self.spd, 0.15)
            self.x  = clamp(self.x+self.vx, 20, W-20)
            self.y  = clamp(self.y+self.vy, 90, H-20)

        if random.random() < 0.05: ps.toxic(self.x, self.y)

        # Evolve when low HP
        if self.hp < self.max_hp*0.3 and self.stage < 2 and self.evo_cd == 0:
            self._evolve(ps)

    def _evolve(self, ps):
        self.stage += 1
        old_hp = self.hp
        self._apply()
        self.hp     = min(self.max_hp, old_hp+50)
        self.evo_cd = 600
        ps.boom(self.x, self.y, self.col, 30)

    def hit(self, dmg, ps, sounds):
        self.hp -= dmg
        self.hidden = False
        self.state  = "flee"
        ps.boom(self.x, self.y, self.col, 8)
        if self.hp <= 0:
            self.alive = False
            ps.boom(self.x, self.y, self.col, 35)
            # "Oh No!" death sound
            sounds['death'].play()

    def draw(self, surf, scanning, scan_r, cop_pos):
        if not self.alive: return
        x, y   = int(self.x), int(self.y)
        in_scan = scanning and dist((self.x,self.y), cop_pos) < scan_r
        al      = 255 if (not self.hidden or in_scan) else 35

        es  = pygame.Surface((self.rad*4, self.rad*4), pygame.SRCALPHA)
        cx = cy = self.rad*2

        # Glow
        gr = self.rad + 8 + int(math.sin(self.gt)*4)
        pygame.draw.circle(es, (*self.col[:3], int(60*al/255)), (cx,cy), gr)
        # Body
        pygame.draw.circle(es, (*self.col[:3], al), (cx,cy), self.rad)

        if self.stage == 0:
            pygame.draw.circle(es, (0,0,0,al), (cx-4,cy-3), 3)
            pygame.draw.circle(es, (0,0,0,al), (cx+4,cy-3), 3)
            pygame.draw.circle(es, (255,255,255,al), (cx-3,cy-4), 1)
            pygame.draw.circle(es, (255,255,255,al), (cx+5,cy-4), 1)
        elif self.stage == 1:
            for i in range(6):
                a  = i*math.pi/3 + self.gt
                sx = cx + int(math.cos(a)*(self.rad+6))
                sy = cy + int(math.sin(a)*(self.rad+6))
                ex2= cx + int(math.cos(a)*(self.rad+1))
                ey2= cy + int(math.sin(a)*(self.rad+1))
                pygame.draw.line(es, (*self.col[:3],al), (ex2,ey2), (sx,sy), 3)
            pygame.draw.circle(es, (255,50,50,al), (cx-6,cy-5), 4)
            pygame.draw.circle(es, (255,50,50,al), (cx+6,cy-5), 4)
            pygame.draw.circle(es, (255,255,0,al),  (cx-6,cy-5), 2)
            pygame.draw.circle(es, (255,255,0,al),  (cx+6,cy-5), 2)
        else:
            rr = self.rad+12
            for i in range(12):
                a  = i*math.pi/6 + self.gt*2
                sx = cx+int(math.cos(a)*rr); sy = cy+int(math.sin(a)*rr)
                pygame.draw.circle(es, (255,60,60,int(al*0.7)), (sx,sy), 4)
            pygame.draw.circle(es, (255,0,0,al),   (cx-8,cy-6), 6)
            pygame.draw.circle(es, (255,0,0,al),   (cx+8,cy-6), 6)
            pygame.draw.circle(es, (255,200,0,al), (cx-8,cy-6), 3)
            pygame.draw.circle(es, (255,200,0,al), (cx+8,cy-6), 3)
            pygame.draw.lines(es, (0,0,0,al), False,
                              [(cx-10,cy+6),(cx-5,cy+12),(cx+5,cy+12),(cx+10,cy+6)], 3)

        surf.blit(es, (x-self.rad*2, y-self.rad*2))

        # HP bar (visible when not truly hidden)
        if not self.hidden or in_scan:
            bw = self.rad*2+6
            pygame.draw.rect(surf, (60,20,20), (x-bw//2, y-self.rad-14, bw, 5))
            hw = int(bw*self.hp/self.max_hp)
            bc = C["green"] if self.hp>60 else C["yellow"] if self.hp>30 else C["red"]
            pygame.draw.rect(surf, bc, (x-bw//2, y-self.rad-14, hw, 5))


# ══════════════════════════════════════════════════════════════════
#  WEATHER
# ══════════════════════════════════════════════════════════════════
class Weather:
    def __init__(self):
        self.mode="clear"; self.timer=300; self.drops=[]

    def update(self):
        self.timer -= 1
        if self.timer <= 0:
            self.mode  = random.choice(["clear","clear","rain","fog","night"])
            self.timer = random.randint(400, 900)
            if self.mode == "rain":
                self.drops = [
                    [random.randint(0,W), random.randint(-20,H), random.uniform(8,14)]
                    for _ in range(200)
                ]
        if self.mode == "rain":
            for d in self.drops:
                d[1] += d[2]
                if d[1] > H: d[0]=random.randint(0,W); d[1]=random.randint(-20,0)

    def draw(self, surf):
        if self.mode == "rain":
            for d in self.drops:
                s = pygame.Surface((3, int(d[2])+1), pygame.SRCALPHA)
                s.fill((150,180,220,100)); surf.blit(s, (int(d[0]),int(d[1])))
        elif self.mode == "fog":
            f=pygame.Surface((W,H),pygame.SRCALPHA); f.fill((180,200,180,55)); surf.blit(f,(0,0))
        elif self.mode == "night":
            n=pygame.Surface((W,H),pygame.SRCALPHA); n.fill((0,0,30,130)); surf.blit(n,(0,0))

    @property
    def label(self):
        return {"clear":"☀ CLEAR","rain":"🌧 RAIN","fog":"🌫 FOG","night":"🌙 NIGHT"}.get(self.mode,"")


# ══════════════════════════════════════════════════════════════════
#  HUD
# ══════════════════════════════════════════════════════════════════
class HUD:
    def __init__(self, f, bf):
        self.f=f; self.bf=bf; self.msgs=[]

    def msg(self, text, col=None, dur=120):
        self.msgs.append([text, dur, col or C["white"]])

    def update(self):
        self.msgs = [[t,d-1,c] for t,d,c in self.msgs if d>1]

    def draw(self, surf, cop, wave, tl, wx, total, killed):
        bar = pygame.Surface((W,64), pygame.SRCALPHA)
        bar.fill((10,20,10,210)); surf.blit(bar,(0,0))

        surf.blit(self.f.render(f"WAVE {wave+1}/{WAVES}", True, C["ui_accent"]), (20,10))
        sc = max(0,int(tl))
        tc = C["red"] if sc<15 else C["yellow"] if sc<30 else C["green"]
        tt = self.bf.render(f"⏱ {sc:02d}s", True, tc)
        surf.blit(tt, (W//2-tt.get_width()//2, 8))
        surf.blit(self.f.render(f"SCORE  {cop.score}", True, C["white"]), (W-200,10))

        # HP
        pygame.draw.rect(surf,(60,20,20),(20,38,160,11),border_radius=3)
        hw = int(160*cop.hp/cop.max_hp)
        hc = C["green"] if cop.hp>50 else C["yellow"] if cop.hp>25 else C["red"]
        pygame.draw.rect(surf,hc,(20,38,hw,11),border_radius=3)
        surf.blit(self.f.render("HP",True,C["white"]),(186,37))

        # Ammo — show reloading bar when empty
        if cop.ammo <= 0:
            ac = C["red"]
            ammo_str = "RELOADING..."
        elif cop.ammo < 8:
            ac = C["yellow"]
            ammo_str = "▪" * cop.ammo
        else:
            ac = C["white"]
            ammo_str = "▪" * min(cop.ammo, 20) if cop.ammo <= 20 else str(cop.ammo)
        surf.blit(self.f.render(f"AMMO  {ammo_str}", True, ac), (20, 52))

        surf.blit(self.f.render(wx.label,True,(180,200,255)),(W-150,38))

        wt = self.f.render(f"WASTE: {total-killed} LEFT", True,(180,255,80))
        surf.blit(wt,(W//2-wt.get_width()//2,38))

        # Floating score messages
        for i,(text,timer,col) in enumerate(self.msgs):
            mt = self.bf.render(text,True,col)
            ms = pygame.Surface(mt.get_size(),pygame.SRCALPHA)
            ms.blit(mt,(0,0)); ms.set_alpha(min(255,timer*3))
            surf.blit(ms,(W//2-mt.get_width()//2, H//2-80-i*42))

        # Controls
        cr = self.f.render(
            "[WASD] Move   [Click] Shoot cursor   [SPACE] Auto-shoot nearest   [E] Scanner   [R] Reload",
            True, (90, 120, 90))
        surf.blit(cr, (W//2 - cr.get_width()//2, H - 20))


# ══════════════════════════════════════════════════════════════════
#  TITLE / GAME-OVER SCREENS
# ══════════════════════════════════════════════════════════════════
def draw_title(surf, f, bf, mf, t):
    for y in range(H):
        r=int(lerp(8,35,y/H)); g=int(lerp(25,75,y/H)); b=int(lerp(8,18,y/H))
        pygame.draw.line(surf,(r,g,b),(0,y),(W,y))
    for i in range(28):
        rx=(i*131+int(t*.4+i*28))%W
        ry=H//2+int(math.sin(t*.05+i)*18)+i*7
        pygame.draw.circle(surf,C["tree_dark"],(rx,ry),16+(i%4)*9)
    for dx in(-2,0,2):
        for dy in(-2,0,2):
            s=mf.render("SKY PATROL",True,(0,70,35))
            surf.blit(s,(W//2-s.get_width()//2+dx, H//4+dy))
    s=mf.render("SKY PATROL",True,C["ui_accent"])
    surf.blit(s,(W//2-s.get_width()//2, H//4))
    s=bf.render("W A S T E   H U N T",True,(180,255,80))
    surf.blit(s,(W//2-s.get_width()//2, H//4+72))
    pulse=int(abs(math.sin(t*.04))*40)
    s=bf.render("[ PRESS  SPACE  TO  PLAY ]",True,(0,180+pulse,100+pulse))
    surf.blit(s,(W//2-s.get_width()//2, H*2//3))
    s=f.render('"Hunt the pollution. Save the planet."',True,(100,200,130))
    surf.blit(s,(W//2-s.get_width()//2, H-58))
    s=f.render("Sky Patrol: Waste Hunt  v2  •  Click / SPACE to shoot  •  Python + Pygame",True,(60,100,60))
    surf.blit(s,(W//2-s.get_width()//2, H-28))


def draw_over(surf, bf, f, cop, win):
    ov=pygame.Surface((W,H),pygame.SRCALPHA); ov.fill((0,0,0,165)); surf.blit(ov,(0,0))
    msg = "✅ FOREST PURIFIED!" if win else "☠ FOREST CONSUMED!"
    col = C["green"] if win else C["red"]
    t=bf.render(msg,True,col); surf.blit(t,(W//2-t.get_width()//2,H//3))
    t=bf.render(f"FINAL SCORE: {cop.score}",True,C["white"])
    surf.blit(t,(W//2-t.get_width()//2,H//3+62))
    edu="Every piece of waste destroyed = real-world awareness. Recycle. Protect nature."
    t=f.render(edu,True,(180,255,130)); surf.blit(t,(W//2-t.get_width()//2,H//3+118))
    t=f.render("[SPACE] Play Again     [ESC] Quit",True,(200,200,200))
    surf.blit(t,(W//2-t.get_width()//2,H*2//3))


# ══════════════════════════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════════════════════════
def main():
    pygame.init()
    pygame.mixer.init(frequency=SAMPLE_RATE, size=-16, channels=2, buffer=512)

    surf  = pygame.display.set_mode((W, H))
    pygame.display.set_caption("Sky Patrol: Waste Hunt  v2")
    clock = pygame.time.Clock()

    try:
        f  = pygame.font.SysFont("consolas", 17)
        bf = pygame.font.SysFont("consolas", 28, bold=True)
        mf = pygame.font.SysFont("consolas", 64, bold=True)
    except Exception:
        f = bf = mf = pygame.font.Font(None, 24)

    # ── Build all sounds ──────────────────────────────────────────
    print("Building sound effects …", end=" ", flush=True)
    sounds = {
        'gun':    make_gunshot_sound(),
        'hit':    make_hit_sound(),
        'death':  make_waste_death_sound(),
        'evolve': make_evolve_sound(),
        'reload': make_reload_sound(),
        'scan':   make_scan_sound(),
        'wave':   make_wave_start_sound(),
        'empty':  make_empty_click(),
    }
    # Set volumes
    sounds['gun'].set_volume(0.7)
    sounds['hit'].set_volume(0.5)
    sounds['death'].set_volume(0.9)
    sounds['evolve'].set_volume(0.6)
    sounds['reload'].set_volume(0.6)
    sounds['scan'].set_volume(0.4)
    sounds['wave'].set_volume(0.8)
    sounds['empty'].set_volume(0.5)
    print("done.")

    # ── Game states ───────────────────────────────────────────────
    TITLE=0; PLAY=1; WAVE_END=2; OVER=3
    state = TITLE; title_t = 0

    cop=None; airplane=None; fm=None
    wl=[]; ps=PSystem(); wx=Weather(); hud=None
    wave=0; wave_t=0; killed=0; win=False

    def new_wave(w):
        nonlocal wave_t, killed
        wave_t = WAVE_TIMINGS[w] * FPS
        killed = 0
        entities = []
        for _ in range(WASTE_PER_WAVE[w]):
            ex, ey = rand_edge()
            st = 0 if w < 2 else random.choices([0,1,2],[5,3,1])[0]
            entities.append(Waste(ex, ey, st))
        return entities

    # ── Main loop ─────────────────────────────────────────────────
    running = True
    while running:
        clock.tick(FPS)

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                running = False

            elif ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    running = False

                # ── SPACE: context-sensitive ──────────────────────
                elif ev.key == pygame.K_SPACE:
                    if state == TITLE:
                        fm=Forest(); airplane=Airplane()
                        cop=Cop(sounds)
                        ps=PSystem(); wx=Weather(); hud=HUD(f,bf)
                        wave=0; wl=new_wave(0); state=PLAY
                        sounds['wave'].play()
                        hud.msg("WAVE 1 — HUNT BEGINS!  60 sec", C["ui_accent"])

                    elif state == PLAY:
                        # SPACE = single shot at nearest waste (event-driven, not held)
                        if cop and not cop.dropping:
                            cop.shoot_nearest(wl, ps)

                    elif state == WAVE_END:
                        wave += 1
                        if wave >= WAVES:
                            win=True; state=OVER
                        else:
                            cop.dropping=True; cop.dvy=-8; cop.y=60
                            cop.land_y=float(random.randint(220,H-90))
                            cop.ammo=cop.max_ammo; cop.shoot_cd=0
                            wl=new_wave(wave); state=PLAY
                            sounds['wave'].play()
                            time_labels = ["", "60 sec", "45 sec", "30 sec"]
                            hud.msg(f"WAVE {wave+1} — GO!  {time_labels[wave+1]}", C["yellow"])

                    elif state == OVER:
                        state = TITLE

                # ── R = instant manual reload ─────────────────────
                elif ev.key == pygame.K_r and state == PLAY:
                    if cop:
                        cop.ammo      = cop.max_ammo
                        cop.shoot_cd  = 0
                        cop.reload_t  = 0
                        sounds['reload'].play()
                        hud.msg("RELOADED!", C["ui_accent"], 60)

            # ── LEFT CLICK = shoot toward cursor ─────────────────
            elif ev.type == pygame.MOUSEBUTTONDOWN:
                if ev.button == 1 and state == PLAY and cop and not cop.dropping:
                    cop.shoot(*ev.pos, ps)

        # ── Update ────────────────────────────────────────────────
        if state == TITLE:
            title_t += 1
            draw_title(surf, f, bf, mf, title_t)
            pygame.display.flip()
            continue

        if state == PLAY:
            wx.update()
            airplane.update()
            # Get a single snapshot of held keys for this frame
            keys_held = pygame.key.get_pressed()
            # cop.update ticks shoot_cd down, handles movement & scanner
            cop.update(keys_held, ps)
            # After update (cooldown already decremented), process held-SPACE fire
            if not cop.dropping and keys_held[pygame.K_SPACE]:
                cop.shoot_nearest(wl, ps)
            
            hits_this_frame, kills_this_frame, misses_this_frame = cop.update_bullets(wl, ps)

            if hits_this_frame > 0:
                # Award +2 points for every successful hit on a waste entity
                points = hits_this_frame * 2
                cop.score += points
                hud.msg(f"+{points} PTS! (Hit)", C["green"], 70)

            if kills_this_frame > 0:
                killed += kills_this_frame

            if misses_this_frame > 0:
                points = misses_this_frame * -1
                cop.score += points
                hud.msg(f"{points} PTS! (Miss)", C["red"], 70)

            ps.update()
            hud.update()
            for w in wl:
                w.update(cop, fm, ps)

            if not cop.alive:
                win=False; state=OVER

            if all(not w.alive for w in wl):
                state = WAVE_END
                hud.msg("WAVE CLEARED!", C["green"])

            wave_t -= 1
            if wave_t <= 0:
                win=False; state=OVER

        # ── Draw ─────────────────────────────────────────────────
        fm.draw(surf)
        airplane.draw(surf)
        for w in wl:
            w.draw(surf, cop.scanning, cop.scan_r, (cop.x, cop.y))
        cop.draw(surf)
        ps.draw(surf)
        wx.draw(surf)
        hud.draw(surf, cop, wave, wave_t/FPS, wx, len(wl), killed)

        if state == WAVE_END:
            ov=pygame.Surface((W,80),pygame.SRCALPHA)
            ov.fill((0,30,0,200)); surf.blit(ov,(0,H//2-40))
            t2=bf.render(f"WAVE {wave+1} CLEARED!   Score: {cop.score}",True,C["green"])
            surf.blit(t2,(W//2-t2.get_width()//2, H//2-26))
            t3=f.render("[SPACE] Next Wave",True,(180,255,130))
            surf.blit(t3,(W//2-t3.get_width()//2, H//2+16))

        if state == OVER:
            draw_over(surf, bf, f, cop, win)

        pygame.display.flip()

    if cop:
        save_score(cop.score)
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()