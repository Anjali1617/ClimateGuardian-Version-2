"""
Eco Defender: Forest Rescue - Option B (Python Version)
A fun educational game about protecting nature and cleaning waste!

Controls:
- Mouse Click: Shoot waste objects
- ESC: Quit game

Scoring:
- Click Waste: +5 points
- Miss Waste (escapes): -2 points and lose 1 life
- Click Nature: No penalty (just disappears)
- You have 6 lives - game ends when all lives are lost!

Requirements: pip install pygame
"""

import pygame
import random
import sys
from datetime import datetime
import json
import os

def save_score(data):
    """Save the final score to a JSON file to integrate with Streamlit."""
    score_file = os.path.join(os.path.dirname(__file__), 'eco_defender_score.json')
    temp_file = score_file + '.tmp'
    try:
        with open(temp_file, 'w') as f:
            json.dump(data, f)
        # Atomically move the file to prevent race conditions
        os.rename(temp_file, score_file)
    except Exception as e:
        print(f"Eco Defender: Error saving score file: {e}", file=sys.stderr)
        # Clean up temp file if it exists
        if os.path.exists(temp_file):
            try:
                os.remove(temp_file)
            except Exception:
                pass

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (34, 197, 94)
RED = (239, 68, 68)
BLUE = (59, 130, 246)
YELLOW = (234, 179, 8)
PURPLE = (168, 85, 247)
DARK_GREEN = (21, 128, 61)
LIGHT_GREEN = (220, 252, 231)
SKY_BLUE = (135, 206, 235)

# Game States
STATE_MENU = "menu"
STATE_PLAYING = "playing"
STATE_PAUSED = "paused"
STATE_GAME_OVER = "game_over"
STATE_WIN = "win"

class GameObject:
    """Base class for all game objects"""
    def __init__(self, x, y, speed, obj_type, emoji):
        self.x = x
        self.y = y
        self.speed = speed
        self.type = obj_type  # 'waste' or 'nature'
        self.emoji = emoji
        self.size = 50
        self.clicked = False
        
    def update(self):
        """Move object down the screen"""
        self.y += self.speed
        
    def draw(self, screen, font):
        """Draw the object"""
        text = font.render(self.emoji, True, BLACK)
        text_rect = text.get_rect(center=(self.x, self.y))
        screen.blit(text, text_rect)
        
    def is_clicked(self, mouse_pos):
        """Check if object was clicked"""
        mx, my = mouse_pos
        distance = ((self.x - mx)**2 + (self.y - my)**2)**0.5
        return distance < self.size / 2
        
    def is_off_screen(self):
        """Check if object is off screen"""
        return self.y > SCREEN_HEIGHT + 50


class Puppy:
    """Puppy feedback system"""
    def __init__(self):
        self.message = ""
        self.visible = False
        self.timer = 0
        self.color = GREEN
        
    def show(self, message, color=GREEN, duration=90):
        """Show a message"""
        self.message = message
        self.color = color
        self.visible = True
        self.timer = duration
        
    def update(self):
        """Update puppy timer"""
        if self.visible:
            self.timer -= 1
            if self.timer <= 0:
                self.visible = False
                
    def draw(self, screen, font, small_font):
        """Draw puppy and message"""
        if self.visible:
            # Draw puppy emoji
            puppy_text = font.render("🐶", True, BLACK)
            puppy_rect = puppy_text.get_rect(center=(SCREEN_WIDTH // 2, 150))
            screen.blit(puppy_text, puppy_rect)
            
            # Draw message background
            msg_surface = small_font.render(self.message, True, WHITE)
            msg_rect = msg_surface.get_rect(center=(SCREEN_WIDTH // 2, 200))
            padding = 20
            bg_rect = pygame.Rect(
                msg_rect.x - padding,
                msg_rect.y - padding // 2,
                msg_rect.width + padding * 2,
                msg_rect.height + padding
            )
            pygame.draw.rect(screen, self.color, bg_rect, border_radius=10)
            pygame.draw.rect(screen, WHITE, bg_rect, 3, border_radius=10)
            screen.blit(msg_surface, msg_rect)


class EcoDefenderGame:
    """Main game class"""
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("🌲 Eco Defender: Forest Rescue 🌲")
        self.clock = pygame.time.Clock()
        
        # Fonts
        self.title_font = pygame.font.Font(None, 72)
        self.font = pygame.font.Font(None, 48)
        self.small_font = pygame.font.Font(None, 32)
        self.tiny_font = pygame.font.Font(None, 24)
        
        # Try to use emoji font if available
        try:
            self.emoji_font = pygame.font.SysFont('segoeuiemoji', 50)
        except:
            self.emoji_font = pygame.font.Font(None, 50)
            
        # Game state
        self.state = STATE_MENU
        self.difficulty = "medium"
        self.reset_game()
        
        # Waste and nature emojis
        self.waste_emojis = ["🧴", "☣️", "🗑️"]
        self.nature_emojis = ["🌳", "🐦", "🦋"]
        
        # Eco facts
        self.eco_facts = [
            "♻️ Plastic takes 100+ years to decompose!",
            "🌳 Recycling 1 ton of paper saves 17 trees!",
            "🌍 Every minute, 1 million plastic bottles are bought!",
            "💧 It takes 3x water to produce a plastic bottle!",
            "🐢 Ocean plastic harms 100,000+ marine animals yearly!",
            "🌱 Composting reduces waste by 30%!"
        ]
        
    def reset_game(self):
        """Reset game to initial state"""
        self.score = 0
        self.high_score = 0
        self.lives = 6  # Add 6 lives system
        self.objects = []
        self.spawn_timer = 0
        self.spawn_rate = 60  # frames between spawns
        self.game_time = 0
        self.correct_hits = 0
        self.puppy = Puppy()
        # New scoring attributes based on difficulty
        self.correct_points = 0
        self.wrong_points = 0 # For clicking wrong items (e.g., nature when it's a penalty)
        self.missed_waste_penalty = 0 # For waste that goes off-screen
        self.game_result = None # Track final outcome (win/loss)
        self.current_fact = None
        self.fact_timer = 0
        
    def set_difficulty(self, difficulty):
        """Set game difficulty"""
        self.difficulty = difficulty
        if difficulty == "easy":
            self.spawn_rate = 80
            self.object_speed = 2
            self.nature_chance = 0.1
            self.correct_points = 2
            self.wrong_points = -1 # Penalty for clicking nature
            self.missed_waste_penalty = -1
        elif difficulty == "medium":
            self.spawn_rate = 60
            self.object_speed = 3
            self.nature_chance = 0.2
            self.correct_points = 3
            self.wrong_points = -1.5 # Penalty for clicking nature
            self.missed_waste_penalty = -1.5
        else:  # hard
            self.spawn_rate = 40
            self.object_speed = 4
            self.nature_chance = 0.4
            self.correct_points = 4
            self.wrong_points = -2 # Penalty for clicking nature
            self.missed_waste_penalty = -2
            
    def spawn_object(self):
        """Spawn a new object"""
        x = random.randint(50, SCREEN_WIDTH - 50)
        y = -50
        
        # Determine if it's waste or nature
        if random.random() < self.nature_chance:
            obj_type = "nature"
            emoji = random.choice(self.nature_emojis)
        else:
            obj_type = "waste"
            emoji = random.choice(self.waste_emojis)
            
        obj = GameObject(x, y, self.object_speed, obj_type, emoji)
        self.objects.append(obj)
        
    def handle_click(self, pos):
        """Handle mouse click"""
        for obj in self.objects[:]:
            if obj.is_clicked(pos) and not obj.clicked:
                obj.clicked = True
                self.objects.remove(obj)
                
                if obj.type == "waste":
                    # Clicked waste - gain points!
                    self.score += self.correct_points
                    self.correct_hits += 1
                    self.puppy.show("🎯 Great job! You saved the forest! 🌿", GREEN)
                    
                    # Show eco fact every 3 hits
                    if self.correct_hits % 3 == 0:
                        self.current_fact = random.choice(self.eco_facts)
                        self.fact_timer = 180
                        
                elif obj.type == "nature":
                    # Clicked nature - apply penalty
                    self.score += self.wrong_points
                    self.lives -= 1 # Also lose a life for clicking nature
                    self.puppy.show(f"❌ Oops! Don't click nature! {self.wrong_points} points! Lives: {self.lives}", RED)
                    
                return True
        return False
        
    def update_game(self):
        """Update game logic"""
        self.game_time += 1
        
        # Spawn new objects
        self.spawn_timer += 1
        if self.spawn_timer >= self.spawn_rate:
            self.spawn_object()
            self.spawn_timer = 0
            
        # Update objects
        for obj in self.objects[:]:
            obj.update()
            
            # Check if object is off screen
            if obj.is_off_screen():
                self.objects.remove(obj)
                
                # Only penalize for missed waste in Option B
                if obj.type == "waste":
                    self.score += self.missed_waste_penalty # missed_waste_penalty is negative
                    self.lives -= 1  # Lose a life
                    self.puppy.show(f"😢 You missed! {self.missed_waste_penalty} points! Lives: {self.lives}", RED)
                    
        # Update puppy
        self.puppy.update()
        
        # Update fact timer
        if self.fact_timer > 0:
            self.fact_timer -= 1
            if self.fact_timer == 0:
                self.current_fact = None
                
        # Update high score
        if self.score > self.high_score:
            self.high_score = self.score
            
        # Check game over condition
        if self.lives <= 0:
            self.state = STATE_GAME_OVER
            self.game_result = 'loss'
            return

        # Check win condition (survive for 60 seconds)
        if self.game_time >= 60 * FPS and self.state == STATE_PLAYING:
            self.state = STATE_WIN
            if self.score > self.high_score:
                self.high_score = self.score
            self.game_result = 'win'
            
    def draw_background(self):
        """Draw game background"""
        # Sky gradient
        for i in range(SCREEN_HEIGHT):
            pygame.draw.line(self.screen, (135, 206, 235), (0, i), (SCREEN_WIDTH, i))
            
        # Ground
        pygame.draw.rect(self.screen, DARK_GREEN, (0, SCREEN_HEIGHT - 100, SCREEN_WIDTH, 100))
        
        # Trees at bottom
        tree_positions = [100, 250, 400, 600, 750, 900]
        for x in tree_positions:
            tree_text = self.emoji_font.render("🌲", True, BLACK)
            tree_rect = tree_text.get_rect(center=(x, SCREEN_HEIGHT - 50))
            self.screen.blit(tree_text, tree_rect)
            
    def draw_menu(self):
        """Draw main menu"""
        self.screen.fill(SKY_BLUE)
        self.draw_background()
        
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(WHITE)
        self.screen.blit(overlay, (0, 0))
        
        # Title
        title = self.title_font.render("🌲 Eco Defender 🌲", True, DARK_GREEN)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 100))
        self.screen.blit(title, title_rect)
        
        subtitle = self.small_font.render("Forest Rescue - Option B", True, GREEN)
        subtitle_rect = subtitle.get_rect(center=(SCREEN_WIDTH // 2, 160))
        self.screen.blit(subtitle, subtitle_rect)
        
        # Instructions
        y_pos = 220
        
        # Dynamic instructions based on difficulty
        current_correct_points = 0
        current_wrong_points = 0
        current_missed_penalty = 0
        
        if self.difficulty == "easy":
            current_correct_points = 2
            current_wrong_points = -1
            current_missed_penalty = -1
        elif self.difficulty == "medium":
            current_correct_points = 3
            current_wrong_points = -1.5
            current_missed_penalty = -1.5
        else: # hard
            current_correct_points = 4
            current_wrong_points = -2
            current_missed_penalty = -2

        instructions = [
            f"🎯 Click on WASTE to clean it up (+{current_correct_points} points)",
            f"❌ Clicking NATURE reduces {abs(current_wrong_points)} points AND 1 life",
            f"🗑️ If WASTE escapes, you lose {abs(current_missed_penalty)} points AND 1 life",
            "❤️  You have 6 lives - game ends when all are lost!",
            "Choose Difficulty:"
        ]
        
        for text in instructions:
            inst = self.tiny_font.render(text, True, BLACK)
            inst_rect = inst.get_rect(center=(SCREEN_WIDTH // 2, y_pos))
            self.screen.blit(inst, inst_rect)
            y_pos += 35
            
        # Difficulty buttons
        button_width = 200
        button_height = 50
        button_y = y_pos + 20
        
        difficulties = [
            ("Easy 🌱", "easy", SCREEN_WIDTH // 2 - 250),
            ("Medium 🌿", "medium", SCREEN_WIDTH // 2),
            ("Hard 🔥", "hard", SCREEN_WIDTH // 2 + 250)
        ]
        
        mouse_pos = pygame.mouse.get_pos()
        
        for label, diff, x in difficulties:
            rect = pygame.Rect(x - button_width // 2, button_y, button_width, button_height)
            
            # Highlight on hover
            if rect.collidepoint(mouse_pos):
                color = YELLOW
            elif self.difficulty == diff:
                color = GREEN
            else:
                color = BLUE
                
            pygame.draw.rect(self.screen, color, rect, border_radius=10)
            pygame.draw.rect(self.screen, BLACK, rect, 3, border_radius=10)
            
            text = self.small_font.render(label, True, WHITE)
            text_rect = text.get_rect(center=rect.center)
            self.screen.blit(text, text_rect)
            
        # Start button
        start_rect = pygame.Rect(SCREEN_WIDTH // 2 - 150, button_y + 100, 300, 60)
        if start_rect.collidepoint(mouse_pos):
            color = YELLOW
        else:
            color = PURPLE
            
        pygame.draw.rect(self.screen, color, start_rect, border_radius=15)
        pygame.draw.rect(self.screen, BLACK, start_rect, 4, border_radius=15)
        
        start_text = self.font.render("START GAME", True, WHITE)
        start_text_rect = start_text.get_rect(center=start_rect.center)
        self.screen.blit(start_text, start_text_rect)
        
        return start_rect, difficulties
        
    def draw_hud(self):
        """Draw HUD (score, time, etc.)"""
        # Score panel
        score_text = self.small_font.render(f"Score: {self.score}", True, WHITE)
        score_bg = pygame.Rect(10, 10, 200, 50)
        pygame.draw.rect(self.screen, PURPLE, score_bg, border_radius=10)
        pygame.draw.rect(self.screen, WHITE, score_bg, 2, border_radius=10)
        self.screen.blit(score_text, (20, 20))
        
        # High score
        high_text = self.tiny_font.render(f"High: {self.high_score}", True, WHITE)
        high_bg = pygame.Rect(220, 10, 180, 50)
        pygame.draw.rect(self.screen, BLUE, high_bg, border_radius=10)
        pygame.draw.rect(self.screen, WHITE, high_bg, 2, border_radius=10)
        self.screen.blit(high_text, (230, 23))
        
        # Time
        seconds = self.game_time // 60
        time_text = self.tiny_font.render(f"⏱️ Time: {seconds}s", True, WHITE)
        time_bg = pygame.Rect(410, 10, 140, 50)
        pygame.draw.rect(self.screen, GREEN, time_bg, border_radius=10)
        pygame.draw.rect(self.screen, WHITE, time_bg, 2, border_radius=10)
        self.screen.blit(time_text, (420, 23))
        
        # Lives display
        lives_text = self.tiny_font.render(f"❤️ Lives: {self.lives}", True, WHITE)
        lives_bg = pygame.Rect(560, 10, 140, 50)
        lives_color = RED if self.lives <= 2 else GREEN
        pygame.draw.rect(self.screen, lives_color, lives_bg, border_radius=10)
        pygame.draw.rect(self.screen, WHITE, lives_bg, 2, border_radius=10)
        self.screen.blit(lives_text, (570, 23))
        
        # Mode indicator
        mode_text = self.tiny_font.render("Mode: Option B", True, WHITE)
        mode_bg = pygame.Rect(SCREEN_WIDTH - 200, 10, 190, 50)
        pygame.draw.rect(self.screen, PURPLE, mode_bg, border_radius=10)
        pygame.draw.rect(self.screen, WHITE, mode_bg, 2, border_radius=10)
        self.screen.blit(mode_text, (SCREEN_WIDTH - 190, 23))
        
        # Eco fact
        if self.current_fact:
            fact_surface = self.tiny_font.render(self.current_fact, True, WHITE)
            fact_rect = fact_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30))
            fact_bg = pygame.Rect(
                fact_rect.x - 15,
                fact_rect.y - 10,
                fact_rect.width + 30,
                fact_rect.height + 20
            )
            pygame.draw.rect(self.screen, DARK_GREEN, fact_bg, border_radius=10)
            pygame.draw.rect(self.screen, YELLOW, fact_bg, 3, border_radius=10)
            self.screen.blit(fact_surface, fact_rect)
            
    def draw_game(self):
        """Draw game screen"""
        self.draw_background()
        
        # Draw objects
        for obj in self.objects:
            obj.draw(self.screen, self.emoji_font)
            
        # Draw HUD
        self.draw_hud()
        
        # Draw puppy feedback
        self.puppy.draw(self.screen, self.emoji_font, self.small_font)
        
        # Draw crosshair cursor
        mouse_pos = pygame.mouse.get_pos()
        pygame.draw.circle(self.screen, RED, mouse_pos, 20, 3)
        pygame.draw.line(self.screen, RED, (mouse_pos[0] - 25, mouse_pos[1]), (mouse_pos[0] + 25, mouse_pos[1]), 3)
        pygame.draw.line(self.screen, RED, (mouse_pos[0], mouse_pos[1] - 25), (mouse_pos[0], mouse_pos[1] + 25), 3)
        
    def draw_game_over(self):
        """Draw game over screen"""
        self.draw_background()
        
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(230)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        # Game Over title
        title = self.title_font.render("🌍 Game Over 🌍", True, RED)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 150))
        self.screen.blit(title, title_rect)
        
        # Puppy sad emoji
        puppy = self.emoji_font.render("🐶💔", True, WHITE)
        puppy_rect = puppy.get_rect(center=(SCREEN_WIDTH // 2, 230))
        self.screen.blit(puppy, puppy_rect)
        
        # Message
        message = self.small_font.render("Forest needs better protection!", True, YELLOW)
        message_rect = message.get_rect(center=(SCREEN_WIDTH // 2, 300))
        self.screen.blit(message, message_rect)
        
        # Stats
        stats_y = 370
        stats = [
            f"Final Score: {self.score}",
            f"High Score: {self.high_score}",
            f"Time Survived: {self.game_time // 60}s",
            f"Waste Cleaned: {self.correct_hits}"
        ]
        
        for stat in stats:
            stat_text = self.small_font.render(stat, True, WHITE)
            stat_rect = stat_text.get_rect(center=(SCREEN_WIDTH // 2, stats_y))
            self.screen.blit(stat_text, stat_rect)
            stats_y += 45
        
        # Buttons
        button_width = 250
        button_height = 60
        retry_rect = pygame.Rect(SCREEN_WIDTH // 2 - 280, 550, button_width, button_height)
        menu_rect = pygame.Rect(SCREEN_WIDTH // 2 + 30, 550, button_width, button_height)
        
        mouse_pos = pygame.mouse.get_pos()
        
        # Retry button
        retry_color = YELLOW if retry_rect.collidepoint(mouse_pos) else GREEN
        pygame.draw.rect(self.screen, retry_color, retry_rect, border_radius=15)
        pygame.draw.rect(self.screen, WHITE, retry_rect, 3, border_radius=15)
        retry_text = self.small_font.render("🔄 Try Again", True, BLACK)
        retry_text_rect = retry_text.get_rect(center=retry_rect.center)
        self.screen.blit(retry_text, retry_text_rect)
        
        # Menu button
        menu_color = YELLOW if menu_rect.collidepoint(mouse_pos) else BLUE
        pygame.draw.rect(self.screen, menu_color, menu_rect, border_radius=15)
        pygame.draw.rect(self.screen, WHITE, menu_rect, 3, border_radius=15)
        menu_text = self.small_font.render("🏠 Main Menu", True, WHITE)
        menu_text_rect = menu_text.get_rect(center=menu_rect.center)
        self.screen.blit(menu_text, menu_text_rect)
        
        return retry_rect, menu_rect
        
    def draw_win(self):
        """Draw win screen"""
        self.draw_background()
        
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(230)
        overlay.fill(DARK_GREEN)
        self.screen.blit(overlay, (0, 0))
        
        # Win title
        title = self.title_font.render("🌲 FOREST SAVED! 🌲", True, GREEN)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 150))
        self.screen.blit(title, title_rect)
        
        # Puppy happy emoji
        puppy = self.emoji_font.render("🐶🎉", True, WHITE)
        puppy_rect = puppy.get_rect(center=(SCREEN_WIDTH // 2, 230))
        self.screen.blit(puppy, puppy_rect)
        
        # Message
        message = self.small_font.render("You are a true Eco Defender!", True, YELLOW)
        message_rect = message.get_rect(center=(SCREEN_WIDTH // 2, 300))
        self.screen.blit(message, message_rect)
        
        # Stats
        stats_y = 370
        stats = [
            f"Final Score: {self.score}",
            f"Difficulty: {self.difficulty.capitalize()}",
            f"Time Survived: {self.game_time // FPS}s",
            f"Waste Cleaned: {self.correct_hits}"
        ]
        
        for stat in stats:
            stat_text = self.small_font.render(stat, True, WHITE)
            stat_rect = stat_text.get_rect(center=(SCREEN_WIDTH // 2, stats_y))
            self.screen.blit(stat_text, stat_rect)
            stats_y += 45
        
        # Buttons
        retry_rect = pygame.Rect(SCREEN_WIDTH // 2 - 280, 550, 250, 60)
        menu_rect = pygame.Rect(SCREEN_WIDTH // 2 + 30, 550, 250, 60)
        
        # Retry button
        pygame.draw.rect(self.screen, GREEN, retry_rect, border_radius=15)
        retry_text = self.small_font.render("🔄 Play Again", True, BLACK)
        self.screen.blit(retry_text, retry_text.get_rect(center=retry_rect.center))
        
        # Menu button
        pygame.draw.rect(self.screen, BLUE, menu_rect, border_radius=15)
        menu_text = self.small_font.render("🏠 Main Menu", True, WHITE)
        self.screen.blit(menu_text, menu_text.get_rect(center=menu_rect.center))
        
        return retry_rect, menu_rect
        
    def handle_menu_click(self, pos, start_rect, difficulties):
        """Handle menu clicks"""
        # Check start button
        if start_rect.collidepoint(pos):
            self.state = STATE_PLAYING
            self.reset_game()
            self.set_difficulty(self.difficulty)
            return
            
        # Check difficulty buttons
        for label, diff, x in difficulties:
            button_width = 200
            button_height = 50
            button_y = 460
            rect = pygame.Rect(x - button_width // 2, button_y, button_width, button_height)
            if rect.collidepoint(pos):
                self.difficulty = diff
                return
                
    def handle_game_over_click(self, pos, retry_rect, menu_rect):
        """Handle game over screen clicks"""
        if retry_rect.collidepoint(pos):
            self.state = STATE_PLAYING
            self.reset_game()
            self.set_difficulty(self.difficulty)
        elif menu_rect.collidepoint(pos):
            self.state = STATE_MENU
                
    def run(self):
        """Main game loop"""
        running = True
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if self.state == STATE_PLAYING:
                            self.state = STATE_MENU
                        else:
                            running = False
                            
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.state == STATE_MENU:
                        start_rect, difficulties = self.draw_menu()
                        self.handle_menu_click(event.pos, start_rect, difficulties)
                    elif self.state == STATE_PLAYING:
                        self.handle_click(event.pos)
                    elif self.state == STATE_GAME_OVER:
                        retry_rect, menu_rect = self.draw_game_over()
                        self.handle_game_over_click(event.pos, retry_rect, menu_rect)
                    elif self.state == STATE_WIN:
                        retry_rect, menu_rect = self.draw_win()
                        self.handle_game_over_click(event.pos, retry_rect, menu_rect)
                        
            # Update
            if self.state == STATE_PLAYING:
                self.update_game()
                
            # Draw
            if self.state == STATE_MENU:
                start_rect, difficulties = self.draw_menu()
            elif self.state == STATE_PLAYING:
                self.draw_game()
            elif self.state == STATE_GAME_OVER:
                retry_rect, menu_rect = self.draw_game_over()
            elif self.state == STATE_WIN:
                retry_rect, menu_rect = self.draw_win()
                
            pygame.display.flip()
            self.clock.tick(FPS)
            
        # Determine result and save
        final_result = self.game_result if self.game_result else 'quit'
            
        save_score({
            'score': self.score,
            'difficulty': self.difficulty,
            'result': final_result
        })
        pygame.quit()
        sys.exit()


# Main entry point
if __name__ == "__main__":
    print("=" * 60)
    print("🌲 ECO DEFENDER: FOREST RESCUE - OPTION B 🌲")
    print("=" * 60)
    print("\nStarting game...")
    print("\nControls:")
    print("  🖱️  Mouse Click: Shoot waste")
    print("  ⌨️  ESC: Quit to menu / Exit game")
    print("\nOption B Scoring:")
    print("  ✅ Click Waste: +5 points")
    print("  ❌ Miss Waste: -2 points and lose 1 life")
    print("  🌳 Click Nature: No penalty")
    print("  ❤️  You have 6 lives - game ends when all lost!")
    print("\n" + "=" * 60)
    
    game = EcoDefenderGame()
    game.run()