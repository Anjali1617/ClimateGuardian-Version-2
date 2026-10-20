"""
Smart Waste Segregation Game - Desktop Version with OpenCV
Integrated for ClimateGuardian AI

Controls:
- Show your hand to the camera
- Pinch (Index + Thumb) to grab trash items
- Drag to matching colored bin
- Release pinch to drop

Press SPACE to start, P to pause, Q to quit
"""
import cv2
import mediapipe as mp
import random
import math
import time
import numpy as np
import os
import json

# --- Icon asset utilities ---

ASSETS_DIR = os.path.join(os.path.dirname(__file__), '..', 'assets')
ICONS_DIR = os.path.join(ASSETS_DIR, 'icons')


def ensure_icons_exist():
    """Ensure icon PNGs exist; if not, generate placeholder colored icons."""
    os.makedirs(ICONS_DIR, exist_ok=True)

    for key, data in TRASH_TYPES.items():
        path = os.path.join(ICONS_DIR, f"{key}.png")
        # If file exists, skip generation
        if os.path.exists(path):
            continue
        # Generate a simple placeholder icon
        size = 128
        icon_img = 255 * np.ones((size, size, 3), dtype=np.uint8)
        # Use a darker version of the bin color for the icon base
        color = tuple(max(0, c - 40) for c in data['color'])
        cv2.rectangle(icon_img, (0, 0), (size, size), color, -1)
        label = data['label'][:3]
        cv2.putText(icon_img, label, (size//8, size//2 + 12), cv2.FONT_HERSHEY_SIMPLEX, 1.6, (255,255,255), 2)
        cv2.imwrite(path, icon_img)


def load_icons():
    """Load icons into TRASH_TYPES as 'icon_img' (BGR arrays)."""
    ensure_icons_exist()
    for key, data in TRASH_TYPES.items():
        path = os.path.join(ICONS_DIR, f"{key}.png")
        img = cv2.imread(path, cv2.IMREAD_UNCHANGED)
        data['icon_img'] = img


# --- Configuration ---
WIDTH, HEIGHT = 800, 600
BIN_HEIGHT = 100
INITIAL_SPAWN_RATE = 2.0
INITIAL_FALL_SPEED = 3
PINCH_THRESHOLD = 50
MAX_MISSED = 5

# Colors (BGR format for OpenCV)
BLUE = (255, 100, 50)
YELLOW = (0, 215, 255)
RED = (50, 50, 255)
GREEN = (50, 200, 50)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)

# Trash Types Configuration
TRASH_TYPES = {
    'plastic': {'color': BLUE, 'label': 'PLASTIC', 'bin_x': 0, 'icon': '🧴'},
    'paper': {'color': YELLOW, 'label': 'PAPER', 'bin_x': 1, 'icon': '📄'},
    'metal': {'color': RED, 'label': 'METAL', 'bin_x': 2, 'icon': '🥫'},
    'organic': {'color': GREEN, 'label': 'ORGANIC', 'bin_x': 3, 'icon': '🍎'}
}


class GameState:
    """Manages the overall game state."""
    
    def __init__(self):
        self.score = 0
        self.missed = 0
        self.level = 1
        self.falling_items = []
        self.last_spawn_time = time.time()
        self.spawn_rate = INITIAL_SPAWN_RATE
        self.fall_speed = INITIAL_FALL_SPEED
        self.game_over = False
        self.paused = False
        self.show_start_screen = True
        self.hand_detected = False
        
    def reset(self):
        """Reset game to initial state."""
        self.score = 0
        self.missed = 0
        self.level = 1
        self.falling_items = []
        self.last_spawn_time = time.time()
        self.spawn_rate = INITIAL_SPAWN_RATE
        self.fall_speed = INITIAL_FALL_SPEED
        self.game_over = False
        self.paused = False
        self.show_start_screen = True


class TrashItem:
    """Represents a falling trash item."""
    
    def __init__(self, frame_w=WIDTH, frame_h=HEIGHT):
        self.type_key = random.choice(list(TRASH_TYPES.keys()))
        self.data = TRASH_TYPES[self.type_key]
        # Scale size reasonably with frame width
        self.size = int(max(30, frame_w * 0.06))
        self.max_w = frame_w
        self.max_h = frame_h
        self.x = random.randint(50, max(100, frame_w - 100))
        self.y = -self.size
        self.is_dragging = False
        self.vx = 0
        self.vy = INITIAL_FALL_SPEED
    
    def update(self, hand_pos=None, is_pinching=False, current_fall_speed=3):
        """Update item position."""
        if self.is_dragging and hand_pos:
            self.x = hand_pos[0] - self.size // 2
            self.y = hand_pos[1] - self.size // 2
            self.x = max(0, min(self.x, self.max_w - self.size))
            self.y = max(0, min(self.y, self.max_h - self.size))
        else:
            self.vy = current_fall_speed
            self.y += self.vy


class HandTracker:
    """Handles MediaPipe hand tracking."""
    
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        self.hands = self.mp_hands.Hands(
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )
        
    def process_frame(self, frame):
        """Process a frame and return hand tracking results."""
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb_frame)
        return results
    
    def get_hand_info(self, results, frame):
        """Extract hand information from detection results."""
        h, w, _ = frame.shape
        cursor_pos = None
        is_pinching = False
        pinch_distance = 0
        
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                idx_tip = hand_landmarks.landmark[8]
                thm_tip = hand_landmarks.landmark[4]
                
                ix, iy = int(idx_tip.x * w), int(idx_tip.y * h)
                tx, ty = int(thm_tip.x * w), int(thm_tip.y * h)
                
                cursor_pos = ((ix + tx) // 2, (iy + ty) // 2)
                pinch_distance = math.hypot(ix - tx, iy - ty)
                is_pinching = pinch_distance < PINCH_THRESHOLD
                
                return cursor_pos, is_pinching, pinch_distance
        
        return cursor_pos, is_pinching, pinch_distance


def draw_bins(frame):
    """Draw the colored bins at the bottom, scaled to the frame size."""
    h, w = frame.shape[:2]
    bin_w = w // 4
    font_scale = max(0.5, w / 800.0)

    def overlay_icon(center_x, center_y, icon_img, size):
        if icon_img is None:
            return
        try:
            icon = cv2.resize(icon_img, (size, size), interpolation=cv2.INTER_AREA)
            x1 = int(center_x - size // 2)
            y1 = int(center_y - size // 2)
            x2 = x1 + size
            y2 = y1 + size
            # Bounds check
            if x1 < 0 or y1 < 0 or x2 > w or y2 > h:
                return
            if icon.shape[2] == 4:
                alpha = icon[:, :, 3] / 255.0
                for c in range(3):
                    frame[y1:y2, x1:x2, c] = (alpha * icon[:, :, c] + (1 - alpha) * frame[y1:y2, x1:x2, c]).astype(frame.dtype)
            else:
                frame[y1:y2, x1:x2] = icon
        except Exception:
            pass
    for key, data in TRASH_TYPES.items():
        idx = data['bin_x']
        x = idx * bin_w
        y = h - BIN_HEIGHT

        cv2.rectangle(frame, (x, y), (x + bin_w, h), data['color'], -1)
        cv2.rectangle(frame, (x, y), (x + bin_w, h), WHITE, 3)

        # Draw label centered on the bin
        text = data['label']
        text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, font_scale, 2)[0]
        text_x = x + (bin_w - text_size[0]) // 2
        cv2.putText(frame, text, (text_x, y + 35), cv2.FONT_HERSHEY_SIMPLEX, font_scale, WHITE, 2)

        # Arrow under the label
        cv2.putText(frame, "▼", (x + bin_w // 2 - 10, y + 35 + int(30 * font_scale)),
                    cv2.FONT_HERSHEY_SIMPLEX, font_scale * 1.0, WHITE, 2)

        # Draw icon centered above the label (if available)
        icon_img = data.get('icon_img')
        icon_size = max(24, int(40 * font_scale))
        overlay_icon(x + bin_w // 2, y + 12 + icon_size // 2, icon_img, icon_size)


def draw_trash_item(frame, item):
    """Draw a trash item with clear label."""
    x, y = int(item.x), int(item.y)
    size = item.size
    color = item.data['color']
    h, w = frame.shape[:2]
    font_scale = max(0.5, w / 1000.0)

    # Item background
    cv2.rectangle(frame, (x, y), (x + size, y + size), color, -1)
    cv2.rectangle(frame, (x, y), (x + size, y + size), WHITE, 2)

    # Label centered at the bottom of the item
    label = item.data['label']
    text_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, font_scale, 2)[0]
    text_x = x + (size - text_size[0]) // 2
    text_y = y + size - 6
    cv2.putText(frame, label, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, font_scale, BLACK, 2)

    # Draw icon image inside the item if available
    icon_img = item.data.get('icon_img')
    if icon_img is not None:
        # Draw small centered icon near the top of the item
        try:
            icon_size = max(20, int(size * 0.4))
            icon = cv2.resize(icon_img, (icon_size, icon_size), interpolation=cv2.INTER_AREA)
            ix1 = x + (size - icon_size) // 2
            iy1 = y + 6
            ix2 = ix1 + icon_size
            iy2 = iy1 + icon_size
            if 0 <= ix1 < frame.shape[1] and 0 <= iy1 < frame.shape[0] and ix2 <= frame.shape[1] and iy2 <= frame.shape[0]:
                if icon.shape[2] == 4:
                    alpha = icon[:, :, 3] / 255.0
                    for c in range(3):
                        frame[iy1:iy2, ix1:ix2, c] = (alpha * icon[:, :, c] + (1 - alpha) * frame[iy1:iy2, ix1:ix2, c]).astype(frame.dtype)
                else:
                    frame[iy1:iy2, ix1:ix2] = icon
        except Exception:
            pass
    else:
        # Fallback to emoji/text if no icon image
        icon = item.data.get('icon', '')
        if icon:
            try:
                cv2.putText(frame, icon, (x + 6, y + 22), cv2.FONT_HERSHEY_SIMPLEX, font_scale * 0.9, WHITE, 2)
            except Exception:
                pass


def draw_hand_indicator(frame, cursor_pos, is_pinching):
    """Draw hand cursor indicator."""
    if cursor_pos:
        cx, cy = cursor_pos
        
        if is_pinching:
            cv2.circle(frame, (cx, cy), 25, (50, 255, 50), -1)
            cv2.circle(frame, (cx, cy), 25, WHITE, 3)
            cv2.putText(frame, "GRAB", (cx - 25, cy - 35), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (50, 255, 50), 2)
        else:
            cv2.circle(frame, (cx, cy), 15, (50, 50, 255), -1)
            cv2.circle(frame, (cx, cy), 15, WHITE, 2)


def check_bin_drop(item, frame_w, frame_h):
    """Check if item was dropped in a bin, using current frame size."""
    bin_w = frame_w // 4
    center_x = item.x + item.size // 2
    center_y = item.y + item.size // 2

    if center_x < 0 or center_x > frame_w:
        return False, None

    if center_y > frame_h - BIN_HEIGHT:
        col = int(center_x // bin_w)

        target_type = None
        for key, data in TRASH_TYPES.items():
            if data['bin_x'] == col:
                target_type = key
                break

        if target_type:
            return True, target_type

    return False, None


def draw_score_panel(frame, game_state):
    """Draw the score panel at the top, scaled to frame."""
    h, w = frame.shape[:2]
    panel_w = min(320, max(220, w // 4))
    panel_h = 110

    cv2.rectangle(frame, (10, 10), (10 + panel_w, 10 + panel_h), (255, 255, 255), -1)
    cv2.rectangle(frame, (10, 10), (10 + panel_w, 10 + panel_h), GRAY, 2)

    font_scale = max(0.6, w / 1000.0)
    cv2.putText(frame, f"Score: {game_state.score}", (25, 40),
                cv2.FONT_HERSHEY_SIMPLEX, font_scale, BLACK, 2)

    missed_color = (50, 50, 255) if game_state.missed >= 3 else BLACK
    cv2.putText(frame, f"Missed: {game_state.missed}/{MAX_MISSED}", (25, 40 + int(25 * font_scale)),
                cv2.FONT_HERSHEY_SIMPLEX, font_scale, missed_color, 2)

    cv2.putText(frame, f"Level: {game_state.level}", (25, 40 + int(50 * font_scale)),
                cv2.FONT_HERSHEY_SIMPLEX, font_scale, BLACK, 2)


def draw_start_screen(frame):
    """Draw the start screen overlay scaled to frame size."""
    h, w = frame.shape[:2]
    overlay = frame.copy()
    cv2.rectangle(overlay, (0, 0), (w, h), (0, 0, 0), -1)
    cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)

    title_box_w = min(600, w - 80)
    title_box_h = min(360, h - 160)
    title_box_x = (w - title_box_w) // 2
    title_box_y = (h - title_box_h) // 2

    cv2.rectangle(frame, (title_box_x, title_box_y),
                  (title_box_x + title_box_w, title_box_y + title_box_h), (34, 139, 34), -1)
    cv2.rectangle(frame, (title_box_x, title_box_y),
                  (title_box_x + title_box_w, title_box_y + title_box_h), WHITE, 3)

    # Title
    cv2.putText(frame, "SMART WASTE", (w // 2 - 130, title_box_y + 60),
                cv2.FONT_HERSHEY_SIMPLEX, max(0.9, w/900.0), (255, 255, 255), 2)

    instructions = [
        "Show your hand to camera",
        "Pinch to grab trash",
        "Drag to matching bin",
        "Release to drop",
        "",
        "Press SPACE to Start",
        "Press P to Pause",
        "Press Q to Quit"
    ]

    for i, instr in enumerate(instructions):
        color = (144, 238, 144) if i < 5 else WHITE
        cv2.putText(frame, instr, (w // 2 - 150, title_box_y + 150 + int(i * 28 * (w/800.0))),
                    cv2.FONT_HERSHEY_SIMPLEX, max(0.6, w/1100.0), color, 1)

def draw_game_over(frame, game_state):
    """Draw the game over screen using frame dimensions."""
    h, w = frame.shape[:2]
    overlay = frame.copy()
    cv2.rectangle(overlay, (0, 0), (w, h), (0, 0, 0), -1)
    cv2.addWeighted(overlay, 0.8, frame, 0.2, 0, frame)

    box_w = min(500, w - 120)
    box_h = min(300, h - 200)
    box_x = (w - box_w) // 2
    box_y = (h - box_h) // 2

    cv2.rectangle(frame, (box_x, box_y), (box_x + box_w, box_y + box_h), (50, 50, 50), -1)
    cv2.rectangle(frame, (box_x, box_y), (box_x + box_w, box_y + box_h), (50, 50, 255), 3)

    cv2.putText(frame, "GAME OVER", (w // 2 - 120, box_y + 60),
                cv2.FONT_HERSHEY_SIMPLEX, max(1.6, w/700.0), (50, 50, 255), 3)

    cv2.putText(frame, f"Final Score: {game_state.score}", (w // 2 - 110, box_y + 120),
                cv2.FONT_HERSHEY_SIMPLEX, max(1.0, w/1000.0), WHITE, 2)

    cv2.putText(frame, f"Level Reached: {game_state.level}", (w // 2 - 120, box_y + 170),
                cv2.FONT_HERSHEY_SIMPLEX, max(0.9, w/1100.0), (144, 238, 144), 2)

    cv2.putText(frame, "Press R to Restart | Q to Quit", (w // 2 - 160, box_y + 220),
                cv2.FONT_HERSHEY_SIMPLEX, max(0.6, w/1400.0), WHITE, 1)


def draw_paused_screen(frame):
    """Draw the paused screen scaled to the frame."""
    h, w = frame.shape[:2]
    overlay = frame.copy()
    cv2.rectangle(overlay, (0, 0), (w, h), (0, 0, 0), -1)
    cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)

    cv2.putText(frame, "PAUSED", (w // 2 - 80, h // 2),
                cv2.FONT_HERSHEY_SIMPLEX, max(1.2, w/800.0), WHITE, 2)
    cv2.putText(frame, "Press P to Resume", (w // 2 - 110, h // 2 + 50),
                cv2.FONT_HERSHEY_SIMPLEX, max(0.7, w/1200.0), WHITE, 1)

def run_game():
    """Main game function."""
    print("🎮 Starting Smart Waste Segregation Game...")
    cap = None # DEFER INITIALIZATION
    hand_tracker = HandTracker()
    game_state = GameState()
    
    # Load/generate icons before the loop
    load_icons()
    
    print("✅ Game ready! Press SPACE to start!")
    
    while True:
        # If game is running, we need a camera. If not, create a dummy frame.
        if cap and cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            frame = cv2.flip(frame, 1)
        else:
            # Create a dummy black frame for start/game over screens if camera is off
            frame = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)
            if game_state.show_start_screen:
                # A nice green background for the start screen
                frame[:] = (34, 139, 34)
        
        # Current frame dimensions (used so UI aligns with camera resolution)
        frame_h, frame_w = frame.shape[:2]

        # Only process hand tracking if game is active and camera is on
        if not game_state.show_start_screen and not game_state.game_over and not game_state.paused and cap:
            results = hand_tracker.process_frame(frame)
            cursor_pos, is_pinching, _ = hand_tracker.get_hand_info(results, frame)
            game_state.hand_detected = cursor_pos is not None
        else:
            cursor_pos, is_pinching = None, False
            game_state.hand_detected = False
        
        draw_bins(frame)
        
        if not game_state.show_start_screen and not game_state.game_over:
            if not game_state.paused and time.time() - game_state.last_spawn_time > game_state.spawn_rate:
                # Pass current frame dimensions so spawned items are positioned and sized correctly
                game_state.falling_items.append(TrashItem(frame_w, frame_h))
                game_state.last_spawn_time = time.time()
            
            items_to_remove = []
            
            for item in game_state.falling_items:
                if is_pinching and cursor_pos and not item.is_dragging:
                    item_center_x = item.x + item.size // 2
                    item_center_y = item.y + item.size // 2
                    dist = math.hypot(cursor_pos[0] - item_center_x, 
                                     cursor_pos[1] - item_center_y)
                    
                    if dist < 60:
                        if not any(i.is_dragging for i in game_state.falling_items if i != item):
                            item.is_dragging = True
                
                item.update(cursor_pos, is_pinching, game_state.fall_speed)
                draw_trash_item(frame, item)
                
                if not is_pinching and item.is_dragging:
                    dropped, target_type = check_bin_drop(item, frame_w, frame_h)
                    
                    if dropped:
                        if target_type == item.type_key:
                            game_state.score += 10
                            new_level = game_state.score // 50 + 1
                            if new_level > game_state.level:
                                game_state.level = new_level
                                game_state.spawn_rate = max(0.8, INITIAL_SPAWN_RATE - (new_level - 1) * 0.15)
                                game_state.fall_speed = min(7, INITIAL_FALL_SPEED + (new_level - 1) * 0.3)
                        else:
                            game_state.score = max(0, game_state.score - 5)
                        
                        items_to_remove.append(item)
                    else:
                        item.is_dragging = False
                
                if item.y > frame_h and item not in items_to_remove:
                    items_to_remove.append(item)
                    game_state.missed += 1
                    
                    if game_state.missed >= MAX_MISSED:
                        game_state.game_over = True
            
            for item in items_to_remove:
                if item in game_state.falling_items:
                    game_state.falling_items.remove(item)
            
            draw_hand_indicator(frame, cursor_pos, is_pinching)
            draw_score_panel(frame, game_state)
            
            if game_state.paused:
                draw_paused_screen(frame)
        
        elif game_state.show_start_screen:
            draw_start_screen(frame)
        
        elif game_state.game_over:
            for item in game_state.falling_items:
                draw_trash_item(frame, item)
            draw_game_over(frame, game_state)
        
        cv2.imshow('Smart Waste Segregation', frame)
        
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord('q') or key == ord('Q'):
            print("\n👋 Thanks for playing!")
            break
        
        elif key == ord(' ') and game_state.show_start_screen:
            game_state.show_start_screen = False
            print("\n🎮 Game Started! Initializing camera...")
            
            # Initialize camera NOW
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                print("❌ ERROR: Could not open camera!")
                # Display error on screen and quit
                err_frame = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)
                cv2.putText(err_frame, "CAMERA ERROR!", (WIDTH//2 - 150, HEIGHT//2), cv2.FONT_HERSHEY_SIMPLEX, 1.5, RED, 3)
                cv2.imshow('Smart Waste Segregation', err_frame)
                cv2.waitKey(3000)
                break
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, WIDTH)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, HEIGHT)
            game_state.last_spawn_time = time.time() # Reset spawn timer
        
        elif key == ord('p') or key == ord('P'):
            if not game_state.show_start_screen and not game_state.game_over:
                game_state.paused = not game_state.paused
        
        elif key == ord('r') or key == ord('R'):
            if game_state.game_over or game_state.show_start_screen:
                game_state.reset()
                print("\n🔄 Game Restarted!")
    
    if cap:
        cap.release()
    cv2.destroyAllWindows()
    print(f"\n🏆 Final Score: {game_state.score}")
    
    # Save score to file
    score_file = os.path.join(os.path.dirname(__file__), 'waste_segregation_score.json')
    try:
        with open(score_file, 'w') as f:
            json.dump({'score': game_state.score}, f)
        print(f"Score saved: {game_state.score}")
    except Exception as e:
        print(f"Error saving score: {e}")
    
    return game_state.score


if __name__ == "__main__":
    try:
        run_game()
    except KeyboardInterrupt:
        print("\n\n⚠️ Game interrupted.")
    except Exception as e:
        print(f"\n❌ Error: {e}")
    finally:
        print("\n👋 Goodbye!")
