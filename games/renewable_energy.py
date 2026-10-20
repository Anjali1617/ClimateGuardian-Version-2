import pygame
import random
import sys

def run_game():
    """Run the Renewable Energy Puzzle game - FULLY WORKING VERSION"""
    pygame.init()
    WIDTH, HEIGHT = 600, 600
    GRID_SIZE = 5
    CELL = 80
    GRID_OFFSET_Y = 150  # Space for UI at top
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("🌍 Renewable Energy Puzzle - ClimateGuardian AI")
    clock = pygame.time.Clock()

    # Fonts
    title_font = pygame.font.SysFont('Arial', 40, bold=True)
    button_font = pygame.font.SysFont('Arial', 24, bold=True)
    info_font = pygame.font.SysFont('Arial', 20)

    # 0=empty, 1=Solar (needs sunny), 2=Wind (needs windy), 3=Hydro (needs river)
    map_grid = [
        [0, 1, 0, 1, 0],
        [2, 0, 2, 0, 2],
        [0, 3, 0, 3, 0],
        [2, 0, 2, 0, 2],
        [0, 1, 0, 1, 0]
    ]

    # Button class for better interaction
    class Button:
        def __init__(self, x, y, width, height, color, hover_color, text, value):
            self.rect = pygame.Rect(x, y, width, height)
            self.color = color
            self.hover_color = hover_color
            self.text = text
            self.value = value
            self.is_hovered = False
            self.is_selected = False
        
        def draw(self, screen):
            # Choose color based on state
            if self.is_selected:
                # Draw selection border
                border_rect = self.rect.inflate(10, 10)
                pygame.draw.rect(screen, (255, 255, 255), border_rect, border_radius=12)
                pygame.draw.rect(screen, self.color, self.rect, border_radius=10)
                # Draw text with contrasting color
                text_surface = button_font.render(self.text, True, (255, 255, 255))
                text_rect = text_surface.get_rect(center=self.rect.center)
                screen.blit(text_surface, text_rect)
                # Draw thick border
                pygame.draw.rect(screen, (0, 0, 0), self.rect, 4, border_radius=10)
            elif self.is_hovered:
                pygame.draw.rect(screen, self.hover_color, self.rect, border_radius=10)
                text_surface = button_font.render(self.text, True, (255, 255, 255))
                text_rect = text_surface.get_rect(center=self.rect.center)
                screen.blit(text_surface, text_rect)
                pygame.draw.rect(screen, (100, 100, 100), self.rect, 3, border_radius=10)
            else:
                pygame.draw.rect(screen, self.color, self.rect, border_radius=10)
                text_surface = button_font.render(self.text, True, (255, 255, 255))
                text_rect = text_surface.get_rect(center=self.rect.center)
                screen.blit(text_surface, text_rect)
                pygame.draw.rect(screen, (50, 50, 50), self.rect, 3, border_radius=10)
        
        def check_hover(self, mouse_pos):
            self.is_hovered = self.rect.collidepoint(mouse_pos)
        
        def check_click(self, mouse_pos):
            return self.rect.collidepoint(mouse_pos)

    # Create buttons
    buttons = [
        Button(50, 70, 140, 60, (255, 193, 7), (255, 220, 100), "☀️ SOLAR", 1),
        Button(220, 70, 140, 60, (33, 150, 243), (100, 181, 246), "💨 WIND", 2),
        Button(390, 70, 140, 60, (0, 188, 212), (77, 208, 225), "💧 HYDRO", 3)
    ]

    selected = None
    emissions = 500
    correct_placements = 0
    wrong_placements = 0
    game_over = False

    # Particle effect for correct placement
    particles = []

    class Particle:
        def __init__(self, x, y, color):
            self.x = x
            self.y = y
            self.color = color
            self.size = 10
            self.lifetime = 30
            self.vel_x = random.uniform(-2, 2)
            self.vel_y = random.uniform(-3, -1)
        
        def update(self):
            self.x += self.vel_x
            self.y += self.vel_y
            self.lifetime -= 1
            self.size = max(0, self.size - 0.3)
        
        def draw(self, screen):
            if self.size > 0:
                pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), int(self.size))

    running = True

    # Main game loop
    while running:
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.MOUSEBUTTONDOWN and not game_over:
                # Check button clicks
                for button in buttons:
                    if button.check_click(mouse_pos):
                        selected = button.value
                        # Update selected state
                        for b in buttons:
                            b.is_selected = (b.value == selected)
                        print(f"Selected energy type: {selected}")  # Debug
                
                # Check grid clicks
                if mouse_pos[0] >= 100 and mouse_pos[1] >= GRID_OFFSET_Y:
                    grid_x = (mouse_pos[0] - 100) // CELL
                    grid_y = (mouse_pos[1] - GRID_OFFSET_Y) // CELL
                    
                    if 0 <= grid_x < GRID_SIZE and 0 <= grid_y < GRID_SIZE and selected is not None:
                        cell_value = map_grid[grid_y][grid_x]
                        print(f"Clicked cell [{grid_y}][{grid_x}] = {cell_value}, Selected = {selected}")  # Debug
                        
                        if cell_value == selected:
                            # CORRECT MATCH!
                            emissions -= 50
                            correct_placements += 1
                            map_grid[grid_y][grid_x] = 0  # Clear the cell
                            
                            # Add green particles
                            particle_x = 100 + grid_x * CELL + CELL // 2
                            particle_y = GRID_OFFSET_Y + grid_y * CELL + CELL // 2
                            for _ in range(15):
                                particles.append(Particle(particle_x, particle_y, (0, 255, 0)))
                            
                            print(f"✅ CORRECT! Emissions: {emissions}")
                            
                        elif cell_value != 0:
                            # WRONG MATCH!
                            emissions += 30
                            wrong_placements += 1
                            
                            # Add red particles
                            particle_x = 100 + grid_x * CELL + CELL // 2
                            particle_y = GRID_OFFSET_Y + grid_y * CELL + CELL // 2
                            for _ in range(8):
                                particles.append(Particle(particle_x, particle_y, (255, 0, 0)))
                            
                            print(f"❌ WRONG! Emissions: {emissions}")
        
        # Update button hover states
        for button in buttons:
            button.check_hover(mouse_pos)
        
        # Update particles
        for particle in particles[:]:
            particle.update()
            if particle.lifetime <= 0:
                particles.remove(particle)
        
        # ==================== DRAWING ====================
        
        # Background gradient
        for i in range(HEIGHT):
            color_value = int(135 + (i / HEIGHT) * 100)
            pygame.draw.line(screen, (color_value, 206, 235), (0, i), (WIDTH, i))
        
        # Title with shadow
        shadow = title_font.render("🌍 Save The Planet!", True, (0, 50, 0))
        screen.blit(shadow, (WIDTH // 2 - shadow.get_width() // 2 + 3, 18))
        title = title_font.render("🌍 Save The Planet!", True, (0, 150, 0))
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 15))
        
        # Draw buttons
        for button in buttons:
            button.draw(screen)
        
        # Instructions
        if selected is None:
            instruction = info_font.render("👆 Select an energy source above!", True, (50, 50, 50))
            screen.blit(instruction, (WIDTH // 2 - instruction.get_width() // 2, 140))
        else:
            energy_names = {1: "Solar ☀️", 2: "Wind 💨", 3: "Hydro 💧"}
            instruction = info_font.render(f"👇 Click matching colored tiles!", True, (50, 50, 50))
            screen.blit(instruction, (WIDTH // 2 - instruction.get_width() // 2, 140))
        
        # Draw Grid with shadow
        shadow_offset = 5
        pygame.draw.rect(screen, (100, 100, 100), 
                         (100 + shadow_offset, GRID_OFFSET_Y + shadow_offset, 
                          GRID_SIZE * CELL, GRID_SIZE * CELL), border_radius=10)
        
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                color = (240, 240, 240)  # Default gray
                icon = ""
                
                if map_grid[row][col] == 1: 
                    color = (255, 235, 59)   # Solar = Bright Yellow
                    icon = "☀️"
                elif map_grid[row][col] == 2: 
                    color = (33, 150, 243)   # Wind = Blue
                    icon = "💨"
                elif map_grid[row][col] == 3: 
                    color = (0, 188, 212)    # Hydro = Cyan
                    icon = "💧"
                
                cell_rect = pygame.Rect(100 + col * CELL, GRID_OFFSET_Y + row * CELL, CELL, CELL)
                pygame.draw.rect(screen, color, cell_rect, border_radius=5)
                pygame.draw.rect(screen, (80, 80, 80), cell_rect, 2, border_radius=5)
                
                # Draw icon
                if icon:
                    icon_surface = button_font.render(icon, True, (50, 50, 50))
                    icon_rect = icon_surface.get_rect(center=cell_rect.center)
                    screen.blit(icon_surface, icon_rect)
        
        # Draw particles
        for particle in particles:
            particle.draw(screen)
        
        # Stats Panel
        stats_y = GRID_OFFSET_Y + GRID_SIZE * CELL + 20
        
        # Emissions bar background
        pygame.draw.rect(screen, (200, 200, 200), (50, stats_y, 500, 30), border_radius=15)
        
        # Emissions bar fill
        emissions_width = max(0, int((emissions / 500) * 500))
        if emissions <= 100:
            bar_color = (0, 200, 0)  # Green
        elif emissions <= 300:
            bar_color = (255, 165, 0)  # Orange
        else:
            bar_color = (255, 0, 0)  # Red
        
        pygame.draw.rect(screen, bar_color, (50, stats_y, emissions_width, 30), border_radius=15)
        
        # Emissions text
        emissions_text = info_font.render(f"💨 Emissions: {emissions} tons CO2", True, (0, 0, 0))
        screen.blit(emissions_text, (WIDTH // 2 - emissions_text.get_width() // 2, stats_y + 5))
        
        # Score
        score_text = info_font.render(f"✅ Correct: {correct_placements}  ❌ Wrong: {wrong_placements}", True, (50, 50, 50))
        screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, stats_y + 40))
        
        # Win condition
        if emissions <= 0 and not game_over:
            game_over = True
            print("🎉 GAME WON!")
            
        if game_over:
            # Overlay
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.set_alpha(220)
            overlay.fill((0, 150, 0))
            screen.blit(overlay, (0, 0))
            
            # Win message
            win_text = title_font.render("🎉 NET-ZERO ACHIEVED! 🎉", True, (255, 255, 255))
            screen.blit(win_text, (WIDTH // 2 - win_text.get_width() // 2, HEIGHT // 2 - 80))
            
            # Final score
            final_score = correct_placements * 100 - wrong_placements * 30
            final_score_text = title_font.render(f"Score: {final_score} points", True, (255, 255, 255))
            screen.blit(final_score_text, (WIDTH // 2 - final_score_text.get_width() // 2, HEIGHT // 2 - 20))
            
            # Stats
            stats_text = info_font.render(f"Perfect Matches: {correct_placements} | Mistakes: {wrong_placements}", True, (255, 255, 255))
            screen.blit(stats_text, (WIDTH // 2 - stats_text.get_width() // 2, HEIGHT // 2 + 30))
            
            # Exit instruction
            exit_text = info_font.render("Press any key or close window to exit...", True, (255, 255, 255))
            screen.blit(exit_text, (WIDTH // 2 - exit_text.get_width() // 2, HEIGHT // 2 + 70))
            
            # Check for exit
            keys = pygame.key.get_pressed()
            if any(keys):
                pygame.time.wait(500)
                running = False
        
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    run_game()
