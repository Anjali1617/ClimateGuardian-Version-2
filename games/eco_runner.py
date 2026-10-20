import pygame
import random
import sys

def run_game():
    """Run the Eco-Runner game with enhanced graphics"""
    pygame.init()
    WIDTH, HEIGHT = 800, 400
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("🏃 Eco-Runner - ClimateGuardian AI")
    clock = pygame.time.Clock()

    # Colors
    WHITE = (255, 255, 255)
    GREEN = (0, 200, 0)
    DARK_GREEN = (34, 139, 34)
    RED = (200, 0, 0)
    BROWN = (139, 69, 19)
    SKIN = (255, 220, 177)
    BLUE = (0, 0, 255)
    BLACK = (0, 0, 0)
    LIGHT_BLUE = (135, 206, 250)
    GRASS_GREEN = (124, 252, 0)

    # Player
    player = pygame.Rect(50, HEIGHT//2 - 25, 50, 50)
    player_speed = 5
    carbon_score = 100  # Goal: get to 0

    # Items & Obstacles
    items = []
    obstacles = []

    font = pygame.font.SysFont('Arial', 36, bold=True)
    small_font = pygame.font.SysFont('Arial', 20)
    
    # Helper functions to draw icons
    def draw_leaf(surface, x, y, size):
        """Draw a leaf icon"""
        # Leaf body
        points = [
            (x + size//2, y),
            (x + size, y + size//3),
            (x + size, y + 2*size//3),
            (x + size//2, y + size),
            (x, y + 2*size//3),
            (x, y + size//3)
        ]
        pygame.draw.polygon(surface, DARK_GREEN, points)
        # Leaf vein
        pygame.draw.line(surface, GREEN, (x + size//2, y), (x + size//2, y + size), 2)
    
    def draw_garbage(surface, x, y, size):
        """Draw a garbage/waste icon"""
        # Trash can body
        pygame.draw.rect(surface, (100, 100, 100), (x, y + size//4, size, 3*size//4))
        # Trash can lid
        pygame.draw.rect(surface, (80, 80, 80), (x - size//8, y, size + size//4, size//4))
        # Waste inside (red)
        pygame.draw.circle(surface, RED, (x + size//2, y + size//2), size//4)
        # X mark on trash
        pygame.draw.line(surface, WHITE, (x + size//4, y + size//3), (x + 3*size//4, y + 2*size//3), 2)
        pygame.draw.line(surface, WHITE, (x + 3*size//4, y + size//3), (x + size//4, y + 2*size//3), 2)
    
    def draw_person(surface, x, y, width, height):
        """Draw a simple person collecting items"""
        # Head
        pygame.draw.circle(surface, SKIN, (x + width//2, y + height//4), height//5)
        # Body
        pygame.draw.rect(surface, BLUE, (x + width//4, y + height//3, width//2, height//2))
        # Arms
        pygame.draw.line(surface, SKIN, (x + width//4, y + height//2), (x, y + height//2), 5)
        pygame.draw.line(surface, SKIN, (x + 3*width//4, y + height//2), (x + width, y + height//2), 5)
        # Legs
        pygame.draw.line(surface, BROWN, (x + width//3, y + 5*height//6), (x + width//4, y + height), 5)
        pygame.draw.line(surface, BROWN, (x + 2*width//3, y + 5*height//6), (x + 3*width//4, y + height), 5)
    
    # Helper functions to draw icons
    def draw_leaf(surface, x, y, size):
        """Draw a leaf icon"""
        # Leaf body
        points = [
            (x + size//2, y),
            (x + size, y + size//3),
            (x + size, y + 2*size//3),
            (x + size//2, y + size),
            (x, y + 2*size//3),
            (x, y + size//3)
        ]
        pygame.draw.polygon(surface, DARK_GREEN, points)
        # Leaf vein
        pygame.draw.line(surface, GREEN, (x + size//2, y), (x + size//2, y + size), 2)
    
    def draw_garbage(surface, x, y, size):
        """Draw a garbage/waste icon"""
        # Trash can body
        pygame.draw.rect(surface, (100, 100, 100), (x, y + size//4, size, 3*size//4))
        # Trash can lid
        pygame.draw.rect(surface, (80, 80, 80), (x - size//8, y, size + size//4, size//4))
        # Waste inside (red)
        pygame.draw.circle(surface, RED, (x + size//2, y + size//2), size//4)
        # X mark on trash
        pygame.draw.line(surface, WHITE, (x + size//4, y + size//3), (x + 3*size//4, y + 2*size//3), 2)
        pygame.draw.line(surface, WHITE, (x + 3*size//4, y + size//3), (x + size//4, y + 2*size//3), 2)
    
    def draw_person(surface, x, y, width, height):
        """Draw a simple person collecting items"""
        # Head
        pygame.draw.circle(surface, SKIN, (x + width//2, y + height//4), height//5)
        # Body
        pygame.draw.rect(surface, BLUE, (x + width//4, y + height//3, width//2, height//2))
        # Arms
        pygame.draw.line(surface, SKIN, (x + width//4, y + height//2), (x, y + height//2), 5)
        pygame.draw.line(surface, SKIN, (x + 3*width//4, y + height//2), (x + width, y + height//2), 5)
        # Legs
        pygame.draw.line(surface, BROWN, (x + width//3, y + 5*height//6), (x + width//4, y + height), 5)
        pygame.draw.line(surface, BROWN, (x + 2*width//3, y + 5*height//6), (x + 3*width//4, y + height), 5)

    running = True
    game_won = False
    final_score = 0
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        if not game_won:
            # Player movement
            keys = pygame.key.get_pressed()
            if keys[pygame.K_UP] and player.top > 0:
                player.y -= player_speed
            if keys[pygame.K_DOWN] and player.bottom < HEIGHT:
                player.y += player_speed

            # Spawn items (green circles) and obstacles (red squares)
            if random.random() < 0.02: 
                items.append(pygame.Rect(WIDTH, random.randint(0, HEIGHT-30), 30, 30))
            if random.random() < 0.01: 
                obstacles.append(pygame.Rect(WIDTH, random.randint(0, HEIGHT-40), 40, 40))

            # Move and check collisions
            for item in items[:]:
                item.x -= 5
                if item.x < 0:
                    items.remove(item)
                if player.colliderect(item):
                    carbon_score = max(0, carbon_score - 10)
                    items.remove(item)
            
            for obs in obstacles[:]:
                obs.x -= 4
                if obs.x < 0:
                    obstacles.remove(obs)
                if player.colliderect(obs):
                    carbon_score += 20
                    obstacles.remove(obs)

            # Win condition
            if carbon_score <= 0:
                game_won = True
                final_score = 50 # Award 50 points for winning

        # Draw everything
        # Background - sky gradient
        for i in range(HEIGHT):
            color_value = int(200 + (i / HEIGHT) * 55)
            pygame.draw.line(screen, (135, 206, color_value), (0, i), (WIDTH, i))
        
        # Ground
        pygame.draw.rect(screen, GRASS_GREEN, (0, HEIGHT - 50, WIDTH, 50))
        
        if not game_won:
            # Draw player (person collecting items)
            draw_person(screen, player.x, player.y, player.width, player.height)
            
            # Draw items (leaves)
            for item in items:
                draw_leaf(screen, item.x, item.y, item.width)
            
            # Draw obstacles (garbage)
            for obs in obstacles:
                draw_garbage(screen, obs.x, obs.y, obs.width)

            # Display Carbon Score
            score_text = font.render(f"Carbon Score: {carbon_score}", True, BLACK)
            screen.blit(score_text, (10, 10))
            
            # Instructions
            inst_text = small_font.render("↑↓ to move | Green = Good | Red = Bad", True, BLACK)
            screen.blit(inst_text, (10, HEIGHT - 30))
        else:
            # Win screen
            screen.fill(GREEN)
            win_text = font.render("🎊 YOU SAVED THE PLANET! 🎊", True, WHITE)
            text_rect = win_text.get_rect(center=(WIDTH//2, HEIGHT//2))
            screen.blit(win_text, text_rect)
            
            congrats_text = small_font.render("Congratulations! Press any key to exit...", True, WHITE)
            congrats_rect = congrats_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 50))
            screen.blit(congrats_text, congrats_rect)
            
            # Check for key press to exit
            keys = pygame.key.get_pressed()
            if any(keys):
                pygame.time.wait(500)
                running = False

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    return final_score

if __name__ == "__main__":
    run_game()
