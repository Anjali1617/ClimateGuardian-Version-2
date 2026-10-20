import pygame
import random
import sys
import math
import io
import wave
import struct
import json
import os

def save_score(score):
    """Save the final score to a JSON file to integrate with Streamlit."""
    score_file = os.path.join(os.path.dirname(__file__), 'eco_puzzle_score.json')
    try:
        with open(score_file, 'w') as f:
            json.dump({'score': score}, f)
    except Exception:
        pass

# ─────────────────────────────────────────────────────────────
# 🔊 SOUND ENGINE
# ─────────────────────────────────────────────────────────────
def generate_wav(freq, duration_ms, volume=0.5):
    buf = io.BytesIO()
    sample_rate = 44100
    num_samples = int(sample_rate * duration_ms / 1000)
    with wave.open(buf, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        for i in range(num_samples):
            t = i / sample_rate
            fade = 1 - (i / num_samples) * 0.5
            val = int(32767 * volume * math.sin(2 * math.pi * freq * t) * fade)
            wf.writeframes(struct.pack('<h', val))
    buf.seek(0)
    return buf

def generate_success_sound():
    buf = io.BytesIO()
    sample_rate = 44100
    duration = 0.4
    num_samples = int(sample_rate * duration)
    with wave.open(buf, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        for i in range(num_samples):
            t = i / sample_rate
            freq = 523 + (i / num_samples) * 300
            val = int(20000 * 0.4 * math.sin(2 * math.pi * freq * t))
            wf.writeframes(struct.pack('<h', val))
    buf.seek(0)
    return buf

def load_sounds():
    try:
        pygame.mixer.init()
        return {
            "click": pygame.mixer.Sound(generate_wav(600, 50, 0.3)),
            "match": pygame.mixer.Sound(generate_wav(880, 150, 0.4)),
            "wrong": pygame.mixer.Sound(generate_wav(200, 150, 0.3)),
            "success": pygame.mixer.Sound(generate_success_sound()),
            "flip": pygame.mixer.Sound(generate_wav(400, 80, 0.2)),
            "slide": pygame.mixer.Sound(generate_wav(300, 60, 0.2)),
            "complete": pygame.mixer.Sound(generate_wav(523, 500, 0.4)),
        }
    except:
        return {k: None for k in ["click", "match", "wrong", "success", "flip", "slide", "complete"]}

# ─────────────────────────────────────────────────────────────
# 🌿 SUSTAINABILITY DATA
# ─────────────────────────────────────────────────────────────
ECO_ICONS = [
    {"icon": "☀️", "name": "Solar", "desc": "Solar energy is renewable and clean"},
    {"icon": "💨", "name": "Wind", "desc": "Wind turbines generate clean electricity"},
    {"icon": "💧", "name": "Water", "desc": "Conserve water - every drop counts"},
    {"icon": "🌳", "name": "Trees", "desc": "Trees absorb CO2 and produce oxygen"},
    {"icon": "♻️", "name": "Recycle", "desc": "Recycling reduces waste in landfills"},
    {"icon": "🚲", "name": "Bike", "desc": "Cycling reduces carbon emissions"},
    {"icon": "🌱", "name": "Plant", "desc": "Growing plants helps the environment"},
    {"icon": "🔋", "name": "Battery", "desc": "Rechargeable batteries reduce waste"},
    {"icon": "💡", "name": "LED", "desc": "LED bulbs use 75% less energy"},
    {"icon": "🌊", "name": "Ocean", "desc": "Oceans regulate Earth's climate"},
    {"icon": "🐝", "name": "Bees", "desc": "Bees pollinate 75% of crops"},
    {"icon": "🌿", "name": "Nature", "desc": "Biodiversity keeps ecosystems healthy"},
    {"icon": "🏠", "name": "Eco Home", "desc": "Green homes save energy"},
    {"icon": "🚃", "name": "Train", "desc": "Public transport reduces emissions"},
    {"icon": "🥗", "name": "Vegan", "desc": "Plant-based diets have lower impact"},
    {"icon": "🛒", "name": "Local", "desc": "Buy local to reduce transport emissions"},
]

ECO_FACTS = [
    "🌍 The Earth's temperature has risen 1.1°C since pre-industrial times",
    "🌳 One tree can absorb 22 kg of CO2 per year",
    "💧 Only 3% of Earth's water is freshwater",
    "♻️ Recycling one aluminum can saves energy to run a TV for 3 hours",
    "☀️ The sun provides enough energy in 1 hour to power Earth for a year",
    "🐝 If bees disappeared, humans would have 4 years to live",
    "🌊 Oceans absorb 30% of human-produced CO2",
    "🚲 Cycling 10 km saves 1.5 kg of CO2 compared to driving",
    "💡 Switching to LED saves 80% energy vs incandescent bulbs",
    "🥗 A vegan diet reduces your carbon footprint by up to 73%",
    "🌱 Composting reduces methane emissions from landfills",
    "🏠 Buildings account for 40% of global energy consumption",
    "🚃 A full train emits 10x less CO2 per passenger than cars",
    "🔋 Electric vehicles produce 50% less emissions over lifetime",
    "🌿 Forests cover 31% of Earth's land surface",
    "💨 Wind energy capacity has grown 75x in the last 20 years",
]

QUIZ_QUESTIONS = [
    {"q": "What percentage of Earth's water is freshwater?", "options": ["3%", "25%", "50%", "75%"], "answer": 0},
    {"q": "Which energy source is NOT renewable?", "options": ["Solar", "Wind", "Coal", "Hydro"], "answer": 2},
    {"q": "How much CO2 can one tree absorb per year?", "options": ["5 kg", "22 kg", "50 kg", "100 kg"], "answer": 1},
    {"q": "What percentage of crops do bees pollinate?", "options": ["25%", "50%", "75%", "90%"], "answer": 2},
    {"q": "Which transport has lowest emissions per person?", "options": ["Car", "Bus", "Train", "Plane"], "answer": 2},
    {"q": "LED bulbs save how much energy vs incandescent?", "options": ["20%", "50%", "80%", "95%"], "answer": 2},
    {"q": "What is the main cause of climate change?", "options": ["Volcanoes", "Sun", "Greenhouse gases", "Oceans"], "answer": 2},
    {"q": "Which material takes longest to decompose?", "options": ["Paper", "Plastic", "Glass", "Food"], "answer": 2},
    {"q": "How much of global energy do buildings use?", "options": ["10%", "20%", "40%", "60%"], "answer": 2},
    {"q": "What's the best way to reduce food waste?", "options": ["Freeze it", "Compost", "Plan meals", "All of these"], "answer": 3},
]

WORD_SCRAMBLES = [
    {"word": "SOLAR", "hint": "Energy from the sun"},
    {"word": "RECYCLE", "hint": "Turn waste into new products"},
    {"word": "COMPOST", "hint": "Organic waste decomposition"},
    {"word": "CARBON", "hint": "Element in CO2"},
    {"word": "ENERGY", "hint": "Power to do work"},
    {"word": "NATURE", "hint": "The natural world"},
    {"word": "FOREST", "hint": "Large area of trees"},
    {"word": "CLIMATE", "hint": "Long-term weather patterns"},
    {"word": "ORGANIC", "hint": "Grown without chemicals"},
    {"word": "SUSTAIN", "hint": "Maintain over time"},
    {"word": "GREEN", "hint": "Color of plants"},
    {"word": "EARTH", "hint": "Our planet"},
]

# ─────────────────────────────────────────────────────────────
# 🎨 UTILITY FUNCTIONS
# ─────────────────────────────────────────────────────────────
def clamp(val, min_val=0, max_val=255):
    return max(min_val, min(max_val, int(val)))

# ─────────────────────────────────────────────────────────────
# ✨ PARTICLE SYSTEM
# ─────────────────────────────────────────────────────────────
class Particle:
    def __init__(self, x, y, color, size=5, life=30, vx=None, vy=None):
        self.x, self.y = x, y
        self.color = color
        self.size = size
        self.life = life
        self.max_life = life
        self.vx = vx if vx is not None else random.uniform(-3, 3)
        self.vy = vy if vy is not None else random.uniform(-5, -1)
        
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.15
        self.life -= 1
        self.size = max(1, self.size * 0.95)
        
    def draw(self, surface):
        if self.life > 0:
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), int(self.size))

class ParticleSystem:
    def __init__(self):
        self.particles = []
        
    def emit(self, x, y, color, count=10):
        for _ in range(count):
            self.particles.append(Particle(x, y, color, random.randint(3, 8), 40))
    
    def emit_confetti(self, x, y):
        colors = [(255,100,100), (100,255,100), (100,100,255), (255,255,100), (255,100,255)]
        for _ in range(30):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(3, 10)
            self.particles.append(Particle(x, y, random.choice(colors), 
                                          random.randint(4, 10), 60,
                                          math.cos(angle) * speed, math.sin(angle) * speed - 5))
    
    def update(self):
        for p in self.particles[:]:
            p.update()
            if p.life <= 0:
                self.particles.remove(p)
    
    def draw(self, surface):
        for p in self.particles:
            p.draw(surface)

# ─────────────────────────────────────────────────────────────
# 🎨 3D RENDERING
# ─────────────────────────────────────────────────────────────
def draw_3d_tile(surface, x, y, w, h, color, depth=15, highlight=False):
    """Draw a 3D isometric tile"""
    r, g, b = color
    if highlight:
        r, g, b = clamp(r+40), clamp(g+40), clamp(b+40)
    
    d = depth
    top = (clamp(r+50), clamp(g+50), clamp(b+50))
    right = (clamp(r-30), clamp(g-30), clamp(b-30))
    front = (r, g, b)
    
    # Front face
    pygame.draw.rect(surface, front, (x, y, w, h), border_radius=5)
    
    # Top face
    pygame.draw.polygon(surface, top, [
        (x+5, y), (x + w-5, y), (x + w + d-5, y - d), (x + d+5, y - d)
    ])
    
    # Right face
    pygame.draw.polygon(surface, right, [
        (x + w, y+5), (x + w + d, y - d+5), (x + w + d, y + h - d-5), (x + w, y + h-5)
    ])
    
    # Borders
    pygame.draw.rect(surface, (0,0,0), (x, y, w, h), 2, border_radius=5)

def draw_3d_button(surface, rect, color, text, text_color=(255,255,255), hovered=False):
    """Draw a 3D button"""
    x, y, w, h = rect.x, rect.y, rect.width, rect.height
    r, g, b = color
    if hovered:
        r, g, b = clamp(r+30), clamp(g+30), clamp(b+30)
    
    # Shadow
    pygame.draw.rect(surface, (50,50,50), (x+4, y+4, w, h), border_radius=10)
    
    # Button body
    pygame.draw.rect(surface, (r,g,b), (x, y, w, h), border_radius=10)
    
    # Highlight on top
    pygame.draw.rect(surface, (clamp(r+40), clamp(g+40), clamp(b+40)), 
                    (x+2, y+2, w-4, h//3), border_top_left_radius=10, border_top_right_radius=10)
    
    # Border
    pygame.draw.rect(surface, (0,0,0), (x, y, w, h), 2, border_radius=10)
    
    # Text
    fnt = pygame.font.SysFont("Arial", 20, bold=True)
    txt = fnt.render(text, True, text_color)
    surface.blit(txt, (x + w//2 - txt.get_width()//2, y + h//2 - txt.get_height()//2))

# ─────────────────────────────────────────────────────────────
# 🔘 BUTTON CLASS
# ─────────────────────────────────────────────────────────────
class Button:
    def __init__(self, x, y, w, h, text, color, icon=""):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.color = color
        self.icon = icon
        self.hovered = False
        
    def draw(self, surface):
        draw_3d_button(surface, self.rect, self.color, 
                      f"{self.icon} {self.text}" if self.icon else self.text,
                      hovered=self.hovered)
    
    def check_hover(self, pos):
        self.hovered = self.rect.collidepoint(pos)
        return self.hovered
    
    def check_click(self, pos):
        return self.rect.collidepoint(pos)

# ─────────────────────────────────────────────────────────────
# 🧩 PUZZLE: MEMORY MATCH
# ─────────────────────────────────────────────────────────────
class MemoryMatch:
    def __init__(self, game):
        self.game = game
        self.grid_size = 4
        self.cards = []
        self.flipped = []
        self.matched = []
        self.moves = 0
        self.score = 0
        self.waiting = False
        self.wait_timer = 0
        self.setup()
    
    def setup(self):
        # Create pairs
        icons = random.sample(ECO_ICONS, 8)
        pairs = icons * 2
        random.shuffle(pairs)
        
        self.cards = []
        for i, icon in enumerate(pairs):
            row, col = i // 4, i % 4
            self.cards.append({
                "icon": icon,
                "x": 200 + col * 100,
                "y": 150 + row * 100,
                "flipped": False,
                "matched": False,
                "flip_anim": 0
            })
        
        self.flipped = []
        self.matched = []
        self.moves = 0
        self.score = 0
        self.waiting = False
    
    def handle_click(self, pos):
        if self.waiting:
            return
        
        for i, card in enumerate(self.cards):
            if card["matched"]:
                continue
            rect = pygame.Rect(card["x"], card["y"], 85, 85)
            if rect.collidepoint(pos) and i not in self.flipped:
                card["flipped"] = True
                card["flip_anim"] = 10
                self.flipped.append(i)
                if self.game.sounds["flip"]:
                    self.game.sounds["flip"].play()
                
                if len(self.flipped) == 2:
                    self.moves += 1
                    self.waiting = True
                    self.wait_timer = 45
                break
    
    def update(self):
        # Update flip animations
        for card in self.cards:
            if card["flip_anim"] > 0:
                card["flip_anim"] -= 1
        
        if self.waiting:
            self.wait_timer -= 1
            if self.wait_timer <= 0:
                self.waiting = False
                idx1, idx2 = self.flipped
                if self.cards[idx1]["icon"]["name"] == self.cards[idx2]["icon"]["name"]:
                    # Match!
                    self.cards[idx1]["matched"] = True
                    self.cards[idx2]["matched"] = True
                    self.matched.extend(self.flipped)
                    self.score += 2
                    self.game.particles.emit_confetti(
                        self.cards[idx1]["x"] + 40, self.cards[idx1]["y"] + 40)
                    if self.game.sounds["match"]:
                        self.game.sounds["match"].play()
                else:
                    # No match
                    self.score -= 1
                    self.cards[idx1]["flipped"] = False
                    self.cards[idx2]["flipped"] = False
                    if self.game.sounds["wrong"]:
                        self.game.sounds["wrong"].play()
                self.flipped = []
    
    def is_complete(self):
        return len(self.matched) == len(self.cards)
    
    def draw(self, surface):
        # Title
        title = pygame.font.SysFont("Arial", 32, bold=True).render("🧠 Eco Memory Match", True, (20, 60, 20))
        surface.blit(title, (250, 40))
        
        # Stats
        stats = pygame.font.SysFont("Arial", 20).render(
            f"Moves: {self.moves} | Score: {self.score} | Pairs: {len(self.matched)//2}/8", 
            True, (50, 50, 50))
        surface.blit(stats, (260, 90))
        
        # Draw cards
        for card in self.cards:
            x, y = card["x"], card["y"]
            
            if card["matched"]:
                # Matched card - green
                draw_3d_tile(surface, x, y, 85, 85, (100, 200, 100), 10)
                fnt = pygame.font.SysFont("Segoe UI Emoji", 32)
                txt = fnt.render(card["icon"]["icon"], True, (255, 255, 255))
                surface.blit(txt, (x + 42 - txt.get_width()//2, y + 28))
            elif card["flipped"]:
                # Flipped card - blue
                scale = abs(math.cos(card["flip_anim"] * 0.3))
                w = int(85 * max(0.3, scale))
                draw_3d_tile(surface, x + (85-w)//2, y, w, 85, (200, 220, 255), 10)
                if scale > 0.5:
                    fnt = pygame.font.SysFont("Segoe UI Emoji", 32)
                    txt = fnt.render(card["icon"]["icon"], True, (0, 0, 0))
                    surface.blit(txt, (x + 42 - txt.get_width()//2, y + 28))
            else:
                # Face down - dark green
                draw_3d_tile(surface, x, y, 85, 85, (80, 120, 80), 10)
                pygame.draw.rect(surface, (60, 100, 60), (x+10, y+10, 65, 65), border_radius=8)
                fnt = pygame.font.SysFont("Arial", 28, bold=True)
                txt = fnt.render("?", True, (150, 200, 150))
                surface.blit(txt, (x + 38, y + 28))
        
        # Hint text
        hint = pygame.font.SysFont("Arial", 16).render(
            "Click cards to flip them. Match eco-friendly pairs!", True, (100, 100, 100))
        surface.blit(hint, (230, 560))

# ─────────────────────────────────────────────────────────────
# 🧩 PUZZLE: WORD SCRAMBLE
# ─────────────────────────────────────────────────────────────
class WordScramble:
    def __init__(self, game):
        self.game = game
        self.current_puzzle = None
        self.scrambled = []
        self.selected = []
        self.score = 0
        self.solved = 0
        self.total = 5
        self.letter_positions = []
        self.message = ""
        self.message_timer = 0
        self.answer_y = 200  # Y position for answer area
        self.letters_y = 320  # Y position for scrambled letters
        self.setup()
    
    def setup(self):
        self.puzzles = random.sample(WORD_SCRAMBLES, self.total)
        self.current_index = 0
        self.load_puzzle()
    
    def load_puzzle(self):
        if self.current_index >= len(self.puzzles):
            return
        
        self.current_puzzle = self.puzzles[self.current_index]
        word = self.current_puzzle["word"]
        
        # Scramble the letters
        letters = list(word)
        random.shuffle(letters)
        while ''.join(letters) == word and len(word) > 1:
            random.shuffle(letters)
        
        self.scrambled = letters
        self.selected = []
        
        # Calculate letter positions
        self.letter_positions = []
        start_x = 400 - len(letters) * 35
        for i, letter in enumerate(letters):
            self.letter_positions.append({
                "letter": letter,
                "x": start_x + i * 70,
                "y": self.letters_y,
                "used": False
            })
    
    def handle_click(self, pos):
        if self.current_index >= len(self.puzzles):
            return
            
        # Check scrambled letter clicks
        for i, lp in enumerate(self.letter_positions):
            if lp["used"]:
                continue
            rect = pygame.Rect(lp["x"], lp["y"], 60, 60)
            if rect.collidepoint(pos):
                self.selected.append(lp["letter"])
                lp["used"] = True
                if self.game.sounds["click"]:
                    self.game.sounds["click"].play()
                
                # Check if word complete
                if len(self.selected) == len(self.current_puzzle["word"]):
                    self.check_answer()
                return
        
        # Check selected letters (to remove)
        start_x = 400 - len(self.current_puzzle["word"]) * 35
        for i in range(len(self.selected)):
            rect = pygame.Rect(start_x + i * 70, self.answer_y, 60, 60)
            if rect.collidepoint(pos):
                # Put letter back
                removed_letter = self.selected.pop(i)
                for lp in self.letter_positions:
                    if lp["letter"] == removed_letter and lp["used"]:
                        lp["used"] = False
                        break
                if self.game.sounds["click"]:
                    self.game.sounds["click"].play()
                return
    
    def check_answer(self):
        answer = ''.join(self.selected)
        if answer == self.current_puzzle["word"]:
            self.score += 2
            self.solved += 1
            self.message = f"✅ Correct! {self.current_puzzle['word']}"
            self.message_timer = 90
            self.game.particles.emit_confetti(400, 250)
            if self.game.sounds["success"]:
                self.game.sounds["success"].play()
            
            self.current_index += 1
            if self.current_index < len(self.puzzles):
                pygame.time.set_timer(pygame.USEREVENT + 1, 1500)
        else:
            self.score -= 1
            self.message = "❌ Try again!"
            self.message_timer = 60
            # Reset
            for lp in self.letter_positions:
                lp["used"] = False
            self.selected = []
            if self.game.sounds["wrong"]:
                self.game.sounds["wrong"].play()
    
    def next_puzzle(self):
        self.load_puzzle()
    
    def update(self):
        if self.message_timer > 0:
            self.message_timer -= 1
    
    def is_complete(self):
        return self.solved >= self.total
    
    def draw(self, surface):
        # Title
        title = pygame.font.SysFont("Arial", 32, bold=True).render("🔤 Eco Word Scramble", True, (20, 60, 20))
        surface.blit(title, (240, 40))
        
        # Stats
        stats = pygame.font.SysFont("Arial", 20).render(
            f"Score: {self.score} | Solved: {self.solved}/{self.total}", True, (50, 50, 50))
        surface.blit(stats, (300, 85))
        
        if self.current_index >= len(self.puzzles):
            complete_txt = pygame.font.SysFont("Arial", 28, bold=True).render(
                "🎉 All words completed!", True, (0, 150, 0))
            surface.blit(complete_txt, (250, 300))
            return
        
        # Hint
        hint = pygame.font.SysFont("Arial", 22).render(
            f"💡 Hint: {self.current_puzzle['hint']}", True, (100, 50, 0))
        surface.blit(hint, (280, 130))
        
        # Selected letters (answer area)
        word_len = len(self.current_puzzle["word"])
        start_x = 400 - word_len * 35
        
        for i in range(word_len):
            x = start_x + i * 70
            y = self.answer_y
            
            if i < len(self.selected):
                # Filled slot
                draw_3d_tile(surface, x, y, 60, 60, (100, 180, 100), 10)
                fnt = pygame.font.SysFont("Arial", 32, bold=True)
                txt = fnt.render(self.selected[i], True, (255, 255, 255))
                surface.blit(txt, (x + 30 - txt.get_width()//2, y + 15))
            else:
                # Empty slot
                draw_3d_tile(surface, x, y, 60, 60, (180, 180, 180), 10)
                pygame.draw.rect(surface, (150, 150, 150), (x+15, y+45, 30, 5))
        
        # Scrambled letters
        for lp in self.letter_positions:
            if not lp["used"]:
                draw_3d_tile(surface, lp["x"], lp["y"], 60, 60, (80, 140, 200), 10)
                fnt = pygame.font.SysFont("Arial", 32, bold=True)
                txt = fnt.render(lp["letter"], True, (255, 255, 255))
                surface.blit(txt, (lp["x"] + 30 - txt.get_width()//2, lp["y"] + 15))
        
        # Message
        if self.message_timer > 0:
            color = (0, 150, 0) if "✅" in self.message else (200, 0, 0)
            msg = pygame.font.SysFont("Arial", 28, bold=True).render(self.message, True, color)
            surface.blit(msg, (400 - msg.get_width()//2, 430))
        
        # Instructions
        inst = pygame.font.SysFont("Arial", 16).render(
            "Click letters to spell the eco word. Click selected letters to remove them.", 
            True, (100, 100, 100))
        surface.blit(inst, (180, 560))

# ─────────────────────────────────────────────────────────────
# 🧩 PUZZLE: ECO QUIZ
# ─────────────────────────────────────────────────────────────
class EcoQuiz:
    def __init__(self, game):
        self.game = game
        self.questions = random.sample(QUIZ_QUESTIONS, min(5, len(QUIZ_QUESTIONS)))
        self.current = 0
        self.score = 0
        self.answered = False
        self.selected = -1
        self.message = ""
        self.message_timer = 0
        self.option_buttons = []
        self.setup_question()
    
    def setup_question(self):
        if self.current >= len(self.questions):
            return
        
        q = self.questions[self.current]
        self.option_buttons = []
        colors = [(100, 150, 200), (200, 150, 100), (150, 200, 100), (200, 100, 150)]
        
        for i, opt in enumerate(q["options"]):
            row, col = i // 2, i % 2
            self.option_buttons.append(Button(
                150 + col * 250, 280 + row * 100, 220, 70,
                opt, colors[i]
            ))
        
        self.answered = False
        self.selected = -1
    
    def handle_click(self, pos):
        if self.answered:
            return
        
        for i, btn in enumerate(self.option_buttons):
            if btn.check_click(pos):
                self.selected = i
                self.answered = True
                
                q = self.questions[self.current]
                if i == q["answer"]:
                    self.score += 2
                    self.message = "✅ Correct!"
                    self.game.particles.emit_confetti(400, 300)
                    if self.game.sounds["success"]:
                        self.game.sounds["success"].play()
                else:
                    self.score -= 1
                    correct = q["options"][q["answer"]]
                    self.message = f"❌ Wrong! Answer: {correct}"
                    if self.game.sounds["wrong"]:
                        self.game.sounds["wrong"].play()
                
                self.message_timer = 120
                pygame.time.set_timer(pygame.USEREVENT + 2, 2000)
                break
    
    def next_question(self):
        self.current += 1
        if self.current < len(self.questions):
            self.setup_question()
    
    def update(self):
        if self.message_timer > 0:
            self.message_timer -= 1
    
    def is_complete(self):
        return self.current >= len(self.questions)
    
    def draw(self, surface):
        # Title
        title = pygame.font.SysFont("Arial", 32, bold=True).render("❓ Eco Quiz Challenge", True, (20, 60, 20))
        surface.blit(title, (240, 40))
        
        # Stats
        stats = pygame.font.SysFont("Arial", 20).render(
            f"Score: {self.score} | Question: {min(self.current + 1, len(self.questions))}/{len(self.questions)}", 
            True, (50, 50, 50))
        surface.blit(stats, (290, 85))
        
        if self.current >= len(self.questions):
            complete_txt = pygame.font.SysFont("Arial", 28, bold=True).render(
                f"🎉 Quiz Complete! Score: {self.score}", True, (0, 150, 0))
            surface.blit(complete_txt, (220, 300))
            return
        
        # Question
        q = self.questions[self.current]
        question_fnt = pygame.font.SysFont("Arial", 22, bold=True)
        question = question_fnt.render(q["q"], True, (0, 0, 0))
        surface.blit(question, (400 - question.get_width()//2, 180))
        
        # Options
        mouse_pos = pygame.mouse.get_pos()
        for i, btn in enumerate(self.option_buttons):
            btn.check_hover(mouse_pos)
            
            color = btn.color
            if self.answered:
                if i == q["answer"]:
                    color = (0, 200, 0)
                elif i == self.selected:
                    color = (200, 0, 0)
            
            # Draw button with correct color
            r, g, b = color
            if btn.hovered and not self.answered:
                r, g, b = clamp(r+30), clamp(g+30), clamp(b+30)
            
            x, y, w, h = btn.rect.x, btn.rect.y, btn.rect.width, btn.rect.height
            pygame.draw.rect(surface, (50,50,50), (x+4, y+4, w, h), border_radius=10)
            pygame.draw.rect(surface, (r,g,b), (x, y, w, h), border_radius=10)
            pygame.draw.rect(surface, (0,0,0), (x, y, w, h), 2, border_radius=10)
            
            fnt = pygame.font.SysFont("Arial", 20, bold=True)
            txt = fnt.render(btn.text, True, (255,255,255))
            surface.blit(txt, (x + w//2 - txt.get_width()//2, y + h//2 - txt.get_height()//2))
        
        # Message
        if self.message_timer > 0:
            color = (0, 150, 0) if "✅" in self.message else (200, 0, 0)
            msg = pygame.font.SysFont("Arial", 24, bold=True).render(self.message, True, color)
            surface.blit(msg, (400 - msg.get_width()//2, 500))
        
        # Instructions
        inst = pygame.font.SysFont("Arial", 16).render(
            "Click the correct answer!", True, (100, 100, 100))
        surface.blit(inst, (320, 560))

# ─────────────────────────────────────────────────────────────
# 🧩 PUZZLE: TILE SLIDE (15 Puzzle)
# ─────────────────────────────────────────────────────────────
class TileSlide:
    def __init__(self, game):
        self.game = game
        self.size = 4
        self.tiles = []
        self.empty = (3, 3)
        self.moves = 0
        self.score = 0
        self.solved = False
        self.tile_colors = [
            (100, 180, 100), (120, 200, 120), (80, 160, 80), (140, 220, 140),
            (100, 160, 180), (120, 180, 200), (80, 140, 160), (140, 200, 220),
            (180, 160, 100), (200, 180, 120), (160, 140, 80), (220, 200, 140),
            (180, 100, 160), (200, 120, 180), (160, 80, 140), (220, 140, 200),
        ]
        self.eco_icons = ["🌳", "☀️", "💧", "🌱", "♻️", "🌊", "🐝", "💨",
                         "🌿", "🏠", "🚲", "🔋", "💡", "🌍", "🌺", ""]
        self.setup()
    
    def setup(self):
        # Create solved state first
        self.tiles = [[i * 4 + j for j in range(4)] for i in range(4)]
        self.empty = (3, 3)
        
        # Shuffle by making valid moves
        for _ in range(200):
            moves = self.get_valid_moves()
            if moves:
                move = random.choice(moves)
                self.make_move(move[0], move[1], animate=False)
        
        self.moves = 0
        self.score = 0
        self.solved = False
    
    def get_valid_moves(self):
        moves = []
        ex, ey = self.empty
        for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
            nx, ny = ex + dx, ey + dy
            if 0 <= nx < 4 and 0 <= ny < 4:
                moves.append((nx, ny))
        return moves
    
    def make_move(self, x, y, animate=True):
        ex, ey = self.empty
        if abs(x - ex) + abs(y - ey) == 1:
            self.tiles[ey][ex], self.tiles[y][x] = self.tiles[y][x], self.tiles[ey][ex]
            self.empty = (x, y)
            if animate:
                self.moves += 1
                if self.game.sounds["slide"]:
                    self.game.sounds["slide"].play()
            self.check_solved()
    
    def check_solved(self):
        for i in range(4):
            for j in range(4):
                if self.tiles[i][j] != i * 4 + j:
                    return
        self.solved = True
        self.score = max(5, 50 - self.moves)
        if self.game.sounds["complete"]:
            self.game.sounds["complete"].play()
        self.game.particles.emit_confetti(400, 300)
    
    def handle_click(self, pos):
        if self.solved:
            return
        
        for y in range(4):
            for x in range(4):
                rect = pygame.Rect(200 + x * 100, 150 + y * 100, 90, 90)
                if rect.collidepoint(pos):
                    self.make_move(x, y)
                    return
    
    def update(self):
        pass
    
    def is_complete(self):
        return self.solved
    
    def draw(self, surface):
        # Title
        title = pygame.font.SysFont("Arial", 32, bold=True).render("🧩 Eco Tile Slide", True, (20, 60, 20))
        surface.blit(title, (270, 40))
        
        # Stats
        stats = pygame.font.SysFont("Arial", 20).render(f"Moves: {self.moves}", True, (50, 50, 50))
        surface.blit(stats, (360, 85))
        
        # Draw tiles
        for y in range(4):
            for x in range(4):
                tile_num = self.tiles[y][x]
                px = 200 + x * 100
                py = 150 + y * 100
                
                if tile_num == 15:  # Empty tile
                    pygame.draw.rect(surface, (180, 180, 180), (px, py, 90, 90), border_radius=10)
                    pygame.draw.rect(surface, (150, 150, 150), (px, py, 90, 90), 2, border_radius=10)
                else:
                    color = self.tile_colors[tile_num % len(self.tile_colors)]
                    draw_3d_tile(surface, px, py, 90, 90, color, 10)
                    
                    # Icon
                    fnt = pygame.font.SysFont("Segoe UI Emoji", 28)
                    txt = fnt.render(self.eco_icons[tile_num], True, (255, 255, 255))
                    surface.blit(txt, (px + 45 - txt.get_width()//2, py + 30))
                    
                    # Number
                    num = pygame.font.SysFont("Arial", 14, bold=True).render(str(tile_num + 1), True, (255, 255, 255))
                    surface.blit(num, (px + 8, py + 8))
        
        if self.solved:
            pygame.draw.rect(surface, (0, 150, 0), (250, 520, 300, 50), border_radius=10)
            msg = pygame.font.SysFont("Arial", 28, bold=True).render(f"🎉 SOLVED! Score: {self.score}", True, (255, 255, 255))
            surface.blit(msg, (270, 530))
        else:
            hint = pygame.font.SysFont("Arial", 16).render(
                "Click tiles adjacent to empty space to slide them", True, (100, 100, 100))
            surface.blit(hint, (220, 565))

# ─────────────────────────────────────────────────────────────
# 🧩 PUZZLE: SORTING CHALLENGE
# ─────────────────────────────────────────────────────────────
class SortingChallenge:
    def __init__(self, game):
        self.game = game
        self.items = []
        self.bins = [
            {"name": "♻️ Eco-Friendly", "color": (80, 180, 80), "rect": pygame.Rect(80, 450, 280, 120)},
            {"name": "❌ Harmful", "color": (180, 80, 80), "rect": pygame.Rect(440, 450, 280, 120)}
        ]
        self.score = 0
        self.sorted_count = 0
        self.total = 10
        self.dragging = None
        self.drag_offset = (0, 0)
        self.message = ""
        self.message_timer = 0
        self.setup()
    
    def setup(self):
        eco_items = [
            {"name": "☀️ Solar", "eco": True},
            {"name": "🚲 Bicycle", "eco": True},
            {"name": "🌱 Compost", "eco": True},
            {"name": "♻️ Recycle", "eco": True},
            {"name": "💡 LED", "eco": True},
            {"name": "🚃 Train", "eco": True},
            {"name": "🥗 Local Food", "eco": True},
            {"name": "🔋 Recharge", "eco": True},
        ]
        
        harmful_items = [
            {"name": "🚗 Gas Car", "eco": False},
            {"name": "✈️ Airplane", "eco": False},
            {"name": "🏭 Factory", "eco": False},
            {"name": "🛢️ Oil", "eco": False},
            {"name": "🥩 Fast Food", "eco": False},
            {"name": "📦 Packaging", "eco": False},
            {"name": "🚬 Pollution", "eco": False},
            {"name": "⛽ Gasoline", "eco": False},
        ]
        
        all_items = random.sample(eco_items, 5) + random.sample(harmful_items, 5)
        random.shuffle(all_items)
        
        self.items = []
        for i, item in enumerate(all_items):
            row = i // 5
            col = i % 5
            self.items.append({
                **item,
                "x": 120 + col * 130,
                "y": 180 + row * 100,
                "sorted": False
            })
        
        self.sorted_count = 0
        self.score = 0
    
    def handle_click(self, pos):
        # Start dragging
        for item in self.items:
            if item["sorted"]:
                continue
            rect = pygame.Rect(item["x"], item["y"], 110, 70)
            if rect.collidepoint(pos):
                self.dragging = item
                self.drag_offset = (item["x"] - pos[0], item["y"] - pos[1])
                if self.game.sounds["click"]:
                    self.game.sounds["click"].play()
                break
    
    def handle_release(self, pos):
        if not self.dragging:
            return
        
        # Check if dropped on a bin
        for i, bin_data in enumerate(self.bins):
            if bin_data["rect"].collidepoint(pos):
                correct = (i == 0 and self.dragging["eco"]) or (i == 1 and not self.dragging["eco"])
                
                if correct:
                    self.score += 2
                    self.message = "✅ Correct!"
                    self.game.particles.emit(pos[0], pos[1], bin_data["color"], 15)
                    if self.game.sounds["match"]:
                        self.game.sounds["match"].play()
                else:
                    self.score -= 1
                    self.message = "❌ Wrong bin!"
                    if self.game.sounds["wrong"]:
                        self.game.sounds["wrong"].play()
                
                self.message_timer = 60
                self.dragging["sorted"] = True
                self.sorted_count += 1
                break
        
        self.dragging = None
    
    def handle_motion(self, pos):
        if self.dragging:
            self.dragging["x"] = pos[0] + self.drag_offset[0]
            self.dragging["y"] = pos[1] + self.drag_offset[1]
    
    def update(self):
        if self.message_timer > 0:
            self.message_timer -= 1
    
    def is_complete(self):
        return self.sorted_count >= self.total
    
    def draw(self, surface):
        # Title
        title = pygame.font.SysFont("Arial", 32, bold=True).render("🌍 Eco Sorting", True, (20, 60, 20))
        surface.blit(title, (300, 40))
        
        # Stats
        stats = pygame.font.SysFont("Arial", 20).render(
            f"Score: {self.score} | Sorted: {self.sorted_count}/{self.total}", True, (50, 50, 50))
        surface.blit(stats, (300, 85))
        
        # Draw bins
        for bin_data in self.bins:
            draw_3d_tile(surface, bin_data["rect"].x, bin_data["rect"].y, 
                        bin_data["rect"].w, bin_data["rect"].h, bin_data["color"], 15)
            fnt = pygame.font.SysFont("Arial", 20, bold=True)
            txt = fnt.render(bin_data["name"], True, (255, 255, 255))
            surface.blit(txt, (bin_data["rect"].centerx - txt.get_width()//2, bin_data["rect"].y + 50))
        
        # Draw items (non-dragging first)
        for item in self.items:
            if item["sorted"] or item == self.dragging:
                continue
            
            draw_3d_tile(surface, item["x"], item["y"], 110, 70, (200, 200, 200), 10)
            fnt = pygame.font.SysFont("Arial", 16, bold=True)
            txt = fnt.render(item["name"], True, (0, 0, 0))
            surface.blit(txt, (item["x"] + 55 - txt.get_width()//2, item["y"] + 25))
        
        # Draw dragging item on top
        if self.dragging:
            draw_3d_tile(surface, self.dragging["x"], self.dragging["y"], 110, 70, (150, 220, 150), 10)
            fnt = pygame.font.SysFont("Arial", 16, bold=True)
            txt = fnt.render(self.dragging["name"], True, (0, 0, 0))
            surface.blit(txt, (self.dragging["x"] + 55 - txt.get_width()//2, self.dragging["y"] + 25))
        
        # Message
        if self.message_timer > 0:
            color = (0, 150, 0) if "✅" in self.message else (200, 0, 0)
            msg = pygame.font.SysFont("Arial", 24, bold=True).render(self.message, True, color)
            surface.blit(msg, (360, 130))
        
        # Instructions
        inst = pygame.font.SysFont("Arial", 16).render(
            "Drag items to the correct bin: Eco-Friendly or Harmful", True, (100, 100, 100))
        surface.blit(inst, (210, 580))

# ─────────────────────────────────────────────────────────────
# 🧩 PUZZLE: CONNECT GRID (Energy Path)
# ─────────────────────────────────────────────────────────────
class ConnectGrid:
    def __init__(self, game):
        self.game = game
        self.grid_size = 5
        self.grid = []
        self.selected = None
        self.connections = []
        self.score = 0
        self.pairs_found = 0
        self.total_pairs = 4
        self.setup()
    
    def setup(self):
        # Create grid
        self.grid = [[None for _ in range(self.grid_size)] for _ in range(self.grid_size)]
        
        sources = ["☀️", "💨", "💧", "⚡"]
        targets = ["🏠", "🏢", "🏫", "🏥"]
        
        # Place pairs
        positions = [(i, j) for i in range(self.grid_size) for j in range(self.grid_size)]
        random.shuffle(positions)
        
        self.pairs = []
        for i in range(self.total_pairs):
            src_pos = positions.pop()
            tgt_pos = positions.pop()
            self.grid[src_pos[0]][src_pos[1]] = {"icon": sources[i], "type": "source", "pair": i}
            self.grid[tgt_pos[0]][tgt_pos[1]] = {"icon": targets[i], "type": "target", "pair": i}
            self.pairs.append({"source": src_pos, "target": tgt_pos, "connected": False})
        
        self.connections = []
        self.selected = None
        self.pairs_found = 0
        self.score = 0
    
    def handle_click(self, pos):
        # Find clicked cell
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                x = 220 + col * 75
                y = 160 + row * 75
                rect = pygame.Rect(x, y, 65, 65)
                
                if rect.collidepoint(pos) and self.grid[row][col]:
                    cell = self.grid[row][col]
                    
                    if self.selected is None:
                        if cell["type"] == "source":
                            # Check if not already connected
                            if not self.pairs[cell["pair"]]["connected"]:
                                self.selected = (row, col)
                                if self.game.sounds["click"]:
                                    self.game.sounds["click"].play()
                    else:
                        if cell["type"] == "target":
                            # Check if same pair
                            src_cell = self.grid[self.selected[0]][self.selected[1]]
                            if src_cell["pair"] == cell["pair"]:
                                # Correct connection!
                                self.connections.append((self.selected, (row, col)))
                                self.pairs[cell["pair"]]["connected"] = True
                                self.pairs_found += 1
                                self.score += 2
                                self.game.particles.emit(x + 30, y + 30, (100, 255, 100), 20)
                                if self.game.sounds["match"]:
                                    self.game.sounds["match"].play()
                            else:
                                self.score -= 1
                                if self.game.sounds["wrong"]:
                                    self.game.sounds["wrong"].play()
                        self.selected = None
                    return
    
    def update(self):
        pass
    
    def is_complete(self):
        return self.pairs_found >= self.total_pairs
    
    def draw(self, surface):
        # Title
        title = pygame.font.SysFont("Arial", 32, bold=True).render("⚡ Energy Connect", True, (20, 60, 20))
        surface.blit(title, (280, 40))
        
        # Stats
        stats = pygame.font.SysFont("Arial", 20).render(
            f"Score: {self.score} | Connected: {self.pairs_found}/{self.total_pairs}", 
            True, (50, 50, 50))
        surface.blit(stats, (280, 85))
        
        # Draw connections
        for conn in self.connections:
            src, tgt = conn
            x1 = 220 + src[1] * 75 + 32
            y1 = 160 + src[0] * 75 + 32
            x2 = 220 + tgt[1] * 75 + 32
            y2 = 160 + tgt[0] * 75 + 32
            pygame.draw.line(surface, (100, 200, 100), (x1, y1), (x2, y2), 6)
            pygame.draw.circle(surface, (80, 180, 80), (x1, y1), 8)
            pygame.draw.circle(surface, (80, 180, 80), (x2, y2), 8)
        
        # Draw grid
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                x = 220 + col * 75
                y = 160 + row * 75
                
                cell = self.grid[row][col]
                
                if cell:
                    # Check if connected
                    connected = self.pairs[cell["pair"]]["connected"]
                    
                    if cell["type"] == "source":
                        color = (150, 220, 150) if connected else (100, 200, 255)
                    else:
                        color = (150, 220, 150) if connected else (255, 200, 100)
                    
                    if self.selected == (row, col):
                        color = (255, 255, 100)
                    
                    draw_3d_tile(surface, x, y, 65, 65, color, 8)
                    
                    fnt = pygame.font.SysFont("Segoe UI Emoji", 26)
                    txt = fnt.render(cell["icon"], True, (0, 0, 0))
                    surface.blit(txt, (x + 32 - txt.get_width()//2, y + 18))
                else:
                    pygame.draw.rect(surface, (220, 220, 220), (x, y, 65, 65), border_radius=8)
                    pygame.draw.rect(surface, (180, 180, 180), (x, y, 65, 65), 2, border_radius=8)
        
        # Legend
        legend_y = 540
        pygame.draw.rect(surface, (240, 240, 240), (150, legend_y, 500, 40), border_radius=10)
        legend_fnt = pygame.font.SysFont("Arial", 14)
        surface.blit(legend_fnt.render("☀️💨💧⚡ = Energy Sources", True, (50, 50, 50)), (170, legend_y + 12))
        surface.blit(legend_fnt.render("🏠🏢🏫🏥 = Buildings", True, (50, 50, 50)), (420, legend_y + 12))
        
        # Instructions
        inst = pygame.font.SysFont("Arial", 16).render(
            "Click energy source, then click matching building to connect", 
            True, (100, 100, 100))
        surface.blit(inst, (200, 590))

# ─────────────────────────────────────────────────────────────
# 🎮 MAIN GAME CLASS
# ─────────────────────────────────────────────────────────────
class EcoPuzzleGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("🌍 Eco Puzzle 3D - Learn Sustainability!")
        self.clock = pygame.time.Clock()
        
        self.state = "MENU"
        self.sounds = load_sounds()
        self.particles = ParticleSystem()
        
        self.current_puzzle = None
        self.total_score = 0
        self.puzzles_completed = 0
        
        self.puzzle_modes = [
            {"name": "🧠 Memory Match", "desc": "Match eco pairs", "class": MemoryMatch, "color": (100, 150, 200)},
            {"name": "🔤 Word Scramble", "desc": "Unscramble eco words", "class": WordScramble, "color": (150, 200, 100)},
            {"name": "❓ Eco Quiz", "desc": "Test your knowledge", "class": EcoQuiz, "color": (200, 150, 100)},
            {"name": "🧩 Tile Slide", "desc": "Solve the puzzle", "class": TileSlide, "color": (150, 100, 200)},
            {"name": "🌍 Eco Sorting", "desc": "Sort eco vs harmful", "class": SortingChallenge, "color": (100, 200, 150)},
            {"name": "⚡ Energy Connect", "desc": "Connect power sources", "class": ConnectGrid, "color": (200, 200, 100)},
        ]
        
        self.menu_buttons = []
        self.setup_menu()
        
        self.complete_buttons = []
        
    def setup_menu(self):
        self.menu_buttons = []
        for i, mode in enumerate(self.puzzle_modes):
            row, col = i // 2, i % 2
            self.menu_buttons.append(Button(
                80 + col * 330, 200 + row * 110, 300, 90,
                mode["name"], mode["color"]
            ))
    
    def start_puzzle(self, index):
        self.current_puzzle = self.puzzle_modes[index]["class"](self)
        self.state = "PLAYING"
    
    def draw_menu(self):
        # Background gradient
        for y in range(600):
            g = int(200 + (y/600) * 40)
            b = int(220 + (y/600) * 30)
            pygame.draw.line(self.screen, (180, g, b), (0, y), (800, y))
        
        # Title
        title_shadow = pygame.font.SysFont("Arial", 48, bold=True).render("🌍 ECO PUZZLE 3D", True, (100, 130, 100))
        title = pygame.font.SysFont("Arial", 48, bold=True).render("🌍 ECO PUZZLE 3D", True, (20, 80, 20))
        self.screen.blit(title_shadow, (182, 42))
        self.screen.blit(title, (180, 40))
        
        # Subtitle
        sub = pygame.font.SysFont("Arial", 20).render("Learn Sustainability Through Fun Puzzles!", True, (60, 100, 60))
        self.screen.blit(sub, (240, 100))
        
        # Stats
        if self.total_score > 0:
            stats = pygame.font.SysFont("Arial", 18, bold=True).render(
                f"🏆 Total Score: {self.total_score} | Puzzles: {self.puzzles_completed}", 
                True, (80, 80, 80))
            self.screen.blit(stats, (260, 140))
        
        # Draw puzzle buttons
        mouse_pos = pygame.mouse.get_pos()
        for i, btn in enumerate(self.menu_buttons):
            btn.check_hover(mouse_pos)
            btn.draw(self.screen)
            
            # Description
            desc = pygame.font.SysFont("Arial", 14).render(
                self.puzzle_modes[i]["desc"], True, (80, 80, 80))
            self.screen.blit(desc, (btn.rect.x + 20, btn.rect.y + 65))
        
        # Footer
        footer = pygame.font.SysFont("Arial", 14).render(
            "🖱️ Click a puzzle to start • Learn about environment while having fun!", 
            True, (100, 100, 100))
        self.screen.blit(footer, (180, 560))
    
    def draw_game(self):
        # Background
        for y in range(600):
            color = (220 - y//20, 235 - y//25, 220 - y//30)
            pygame.draw.line(self.screen, color, (0, y), (800, y))
        
        # Draw current puzzle
        if self.current_puzzle:
            self.current_puzzle.draw(self.screen)
        
        # Particles
        self.particles.draw(self.screen)
        
        # Back button
        back_btn = pygame.Rect(10, 10, 100, 40)
        pygame.draw.rect(self.screen, (150, 100, 100), back_btn, border_radius=10)
        pygame.draw.rect(self.screen, (0, 0, 0), back_btn, 2, border_radius=10)
        back_txt = pygame.font.SysFont("Arial", 16, bold=True).render("← Back", True, (255, 255, 255))
        self.screen.blit(back_txt, (30, 18))
    
    def draw_complete(self):
        # Background
        for y in range(600):
            color = (200 + y//20, 220 + y//25, 200 + y//30)
            pygame.draw.line(self.screen, color, (0, y), (800, y))
        
        # Title
        title = pygame.font.SysFont("Arial", 44, bold=True).render("🎉 PUZZLE COMPLETE!", True, (20, 100, 20))
        self.screen.blit(title, (190, 80))
        
        # Score
        score_txt = pygame.font.SysFont("Arial", 30).render(
            f"Score: {self.current_puzzle.score}", True, (50, 50, 50))
        self.screen.blit(score_txt, (330, 160))
        
        total_txt = pygame.font.SysFont("Arial", 22).render(
            f"Total Score: {self.total_score}", True, (80, 80, 80))
        self.screen.blit(total_txt, (330, 210))
        
        # Eco fact box
        pygame.draw.rect(self.screen, (80, 150, 80), (80, 280, 640, 100), border_radius=15)
        pygame.draw.rect(self.screen, (60, 130, 60), (80, 280, 640, 100), 3, border_radius=15)
        
        fact_title = pygame.font.SysFont("Arial", 18, bold=True).render("🌱 Did you know?", True, (255, 255, 255))
        self.screen.blit(fact_title, (100, 295))
        
        fact = random.choice(ECO_FACTS)
        # Word wrap for long facts
        words = fact.split()
        lines = []
        current_line = []
        for word in words:
            current_line.append(word)
            test_line = ' '.join(current_line)
            if pygame.font.SysFont("Arial", 16).size(test_line)[0] > 600:
                current_line.pop()
                lines.append(' '.join(current_line))
                current_line = [word]
        lines.append(' '.join(current_line))
        
        for i, line in enumerate(lines[:2]):  # Max 2 lines
            fact_txt = pygame.font.SysFont("Arial", 16).render(line, True, (255, 255, 255))
            self.screen.blit(fact_txt, (100, 325 + i * 22))
        
        # Buttons
        menu_btn = Button(200, 420, 180, 55, "📋 Menu", (100, 150, 200))
        again_btn = Button(420, 420, 180, 55, "🔄 Again", (100, 200, 100))
        
        mouse_pos = pygame.mouse.get_pos()
        menu_btn.check_hover(mouse_pos)
        again_btn.check_hover(mouse_pos)
        
        menu_btn.draw(self.screen)
        again_btn.draw(self.screen)
        
        self.complete_buttons = [menu_btn, again_btn]
        
        # Particles
        self.particles.draw(self.screen)
    
    def run(self):
        while True:
            mouse_pos = pygame.mouse.get_pos()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    save_score(self.total_score)
                    pygame.quit()
                    sys.exit()
                
                # Timer events for puzzle transitions
                if event.type == pygame.USEREVENT + 1:
                    pygame.time.set_timer(pygame.USEREVENT + 1, 0)
                    if isinstance(self.current_puzzle, WordScramble):
                        self.current_puzzle.next_puzzle()
                
                if event.type == pygame.USEREVENT + 2:
                    pygame.time.set_timer(pygame.USEREVENT + 2, 0)
                    if isinstance(self.current_puzzle, EcoQuiz):
                        self.current_puzzle.next_question()
                
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.state == "MENU":
                        for i, btn in enumerate(self.menu_buttons):
                            if btn.check_click(mouse_pos):
                                self.start_puzzle(i)
                                if self.sounds["click"]:
                                    self.sounds["click"].play()
                    
                    elif self.state == "PLAYING":
                        # Back button
                        if pygame.Rect(10, 10, 100, 40).collidepoint(mouse_pos):
                            self.state = "MENU"
                            self.current_puzzle = None
                            if self.sounds["click"]:
                                self.sounds["click"].play()
                        else:
                            self.current_puzzle.handle_click(mouse_pos)
                    
                    elif self.state == "COMPLETE":
                        if len(self.complete_buttons) >= 2:
                            if self.complete_buttons[0].check_click(mouse_pos):
                                self.state = "MENU"
                                if self.sounds["click"]:
                                    self.sounds["click"].play()
                            elif self.complete_buttons[1].check_click(mouse_pos):
                                puzzle_class = type(self.current_puzzle)
                                self.current_puzzle = puzzle_class(self)
                                self.state = "PLAYING"
                                if self.sounds["click"]:
                                    self.sounds["click"].play()
                
                if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    if self.state == "PLAYING" and isinstance(self.current_puzzle, SortingChallenge):
                        self.current_puzzle.handle_release(mouse_pos)
                
                if event.type == pygame.MOUSEMOTION:
                    if self.state == "PLAYING" and isinstance(self.current_puzzle, SortingChallenge):
                        self.current_puzzle.handle_motion(mouse_pos)
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if self.state == "PLAYING":
                            self.state = "MENU"
                            self.current_puzzle = None
                        elif self.state == "COMPLETE":
                            self.state = "MENU"
            
            # Update
            if self.state == "PLAYING" and self.current_puzzle:
                self.current_puzzle.update()
                
                # Check completion
                if self.current_puzzle.is_complete():
                    self.total_score += self.current_puzzle.score
                    self.puzzles_completed += 1
                    self.particles.emit_confetti(400, 300)
                    if self.sounds["complete"]:
                        self.sounds["complete"].play()
                    self.state = "COMPLETE"
            
            self.particles.update()
            
            # Render
            if self.state == "MENU":
                self.draw_menu()
            elif self.state == "PLAYING":
                self.draw_game()
            elif self.state == "COMPLETE":
                self.draw_complete()
            
            pygame.display.flip()
            self.clock.tick(60)

# ─────────────────────────────────────────────────────────────
# 🚀 RUN GAME
# ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    game = EcoPuzzleGame()
    game.run()