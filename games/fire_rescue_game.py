from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
import random
import json
import os

# 1. Initialize the Engine
app = Ursina()

# --- Game Assets & Settings ---
window.title = "Climate Guardian: Fire Rescue"
window.borderless = False
window.fullscreen = False
window.exit_button.visible = False

# Load a sky
Sky()

# 2. Create the Environment
# The Ground
ground = Entity(
    model='plane',
    texture='grass',
    collider='box',
    scale=(100, 1, 100),
    color=color.rgb(30, 100, 30)
)

# The Sacred Tree
# We make these global so we can access them in the update loop
tree_trunk = Entity(model='cube', color=color.brown, scale=(2, 10, 2), position=(0, 5, 20), collider='box')
tree_leaves = Entity(model='sphere', color=color.green, scale=(8, 8, 8), position=(0, 10, 20), collider='box')

# 3. The Player (First Person)
player = FirstPersonController(position=(0, 2, -10))
player.cursor.visible = True
player.cursor.color = color.cyan

# The Gun
gun = Entity(
    parent=camera.ui,
    model='cube',
    scale=(0.3, 0.2, 1),
    position=(0.5, -0.6),
    rotation=(-5, -10, -10),
    color=color.blue,
    texture='white_cube'
)

# UI Text
score = 0
score_text = Text(text=f'Score: {score}', position=(-0.85, 0.45), scale=2, color=color.yellow)
# Center Game Over text, hidden by default
game_over_text = Text(text='', origin=(0,0), scale=3, color=color.red, background=True)

# Exit instruction text (shown when game over)
exit_instruction = Text(text='', origin=(0,-0.15), scale=2, color=color.white, background=True)

# --- Game Logic ---
bullets = []
enemies = []
game_active = True

def shoot():
    if not game_active: return

    # Audio visual effect
    if gun.color == color.blue:
        gun.color = color.cyan
        invoke(setattr, gun, 'color', color.blue, delay=0.1)
    
    # Spawn bullet
    bullet = Entity(
        model='sphere',
        color=color.cyan,
        scale=0.2,
        position=player.position + Vec3(0, 1.5, 0),
        collider='sphere'
    )
    bullet.animate_position(bullet.position + camera.forward * 50, duration=2, curve=curve.linear)
    bullets.append(bullet)
    destroy(bullet, delay=2)

def spawn_enemy():
    if not game_active: return

    # Spawn fire above the general area, slightly randomized
    # We aim slightly towards the tree (z=20) to make it dangerous
    x_pos = random.randint(-15, 15)
    z_pos = random.randint(10, 30) 
    
    enemy = Entity(
        model='sphere',
        color=color.orange,
        scale=2,
        position=(x_pos, 30, z_pos),
        collider='sphere',
        texture='noise'
    )
    enemy.animate_rotation((random.randint(0,360), random.randint(0,360), 0), duration=1, loop=True)
    enemies.append(enemy)
    
    # Make it fall towards the ground
    enemy.animate_position((x_pos, 0, z_pos), duration=5, curve=curve.linear)

def input(key):
    global game_active
    
    if key == 'left mouse down' and game_active:
        shoot()
    
    # Exit game - Multiple ways to exit
    if key == 'escape' or key == 'q' or key == 'e':
        application.quit()

def update():
    global score, game_active
    
    if not game_active: return

    # 1. Bullet Collision (Shooting Fire)
    for b in bullets:
        hit_info = b.intersects()
        if hit_info.hit:
            if hit_info.entity in enemies:
                # Destroy Enemy
                destroy(hit_info.entity)
                if hit_info.entity in enemies: enemies.remove(hit_info.entity)
                
                # Destroy Bullet
                destroy(b)
                if b in bullets: bullets.remove(b)
                
                # Particle Effect
                e = Entity(model='sphere', color=color.yellow, position=hit_info.point, scale=0.5)
                e.animate_scale(0, duration=0.5)
                destroy(e, delay=0.5)
                
                score += 10
                score_text.text = f'Score: {score}'

    # 2. Fire Collision (Hitting Tree or Ground)
    for e in enemies:
        # Check collision with Tree Leaves
        # We use distance() to see if the fire is inside/touching the leaves
        dist_to_tree = distance(e.position, tree_leaves.position)
        
        if dist_to_tree < 5: # 5 is roughly the radius of the leaves + fire
            # --- GAME OVER SCENARIO ---
            game_active = False
            
            # Visual: Tree turns into fire
            tree_leaves.color = color.orange
            tree_trunk.color = color.red
            
            # UI: Show Game Over
            game_over_text.text = "TREE BURNED!\nGAME OVER"
            
            # Show exit instructions
            exit_instruction.text = "Press ESC, Q, or E to exit"
            
            # Stop the game physics
            application.time_scale = 0 
            return

        # Check if hit ground (Missed)
        if e.y <= 0.5:
            destroy(e)
            enemies.remove(e)

    # Spawn logic
    if random.random() < 0.02:
        spawn_enemy()

def save_score():
    """Save the final score to a JSON file."""
    score_file = os.path.join(os.path.dirname(__file__), 'fire_rescue_score.json')
    try:
        with open(score_file, 'w') as f:
            json.dump({'score': score}, f)
        print(f"Score saved: {score}")
    except Exception as e:
        print(f"Error saving score: {e}")

if __name__ == "__main__":
    try:
        app.run()
    finally:
        # Always save score when app closes
        save_score()
